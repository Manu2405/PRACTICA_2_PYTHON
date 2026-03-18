"""ASFI central service.

This service pulls account data from the 14 bank APIs, decrypts it using the
appropriate algorithm, converts balances using the BCB exchange rate, and
stores the results into the central `asfi_central` database.

Usage:
    python -m asfi.main --once
    python -m asfi.main --interval 30

"""

import argparse
import asyncio
import logging
import random
import string
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from .clients import get_bcb_rate, send_verification_codes_batch, fetch_bank_accounts_batches
from .config import BANKS
from .crypto_router import decrypt_account_fields
from .db import get_bank_algorithm, safe_decimal, upsert_accounts_batch


def configure_logging(log_file: Optional[str] = None):
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
    )


def generate_verification_code(length: int = 8) -> str:
    """Generate a random alphanumeric verification code."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def calculate_balances(raw: Dict[str, any], rate: float) -> (Decimal, Decimal):
    """Return (saldo_usd, saldo_bs)."""

    # The bank APIs store the balance in different keys depending on the engine.
    # Our ETL pushes into a `SaldoUSD` column, so prefer it.
    raw_value = raw.get("SaldoUSD") or raw.get("Saldo") or raw.get("SaldoBs")

    saldo_usd = safe_decimal(raw_value)
    saldo_bs = (saldo_usd * Decimal(str(rate))).quantize(Decimal("0.0001"))
    return saldo_usd, saldo_bs


async def _get_bcb_rate_with_fallback(last_rate: Optional[float]) -> float:
    """Get BCB rate with retry logic and fallback."""
    rate = await get_bcb_rate()
    if rate:
        return rate
    if last_rate is not None:
        return last_rate
    for _ in range(5):
        logging.warning("Failed to get BCB rate, retrying in 2 seconds...")
        await asyncio.sleep(2)
        rate = await get_bcb_rate()
        if rate:
            return rate
    logging.warning("BCB rate unavailable, using fallback 6.96")
    return 6.96


async def process_bank(bank_cfg: dict, verify_queue: asyncio.Queue):
    """Fetch all accounts from a bank and enqueue verification batches.
    
    Verification is handled separately by a background worker so that
    it does NOT block pagination — this is the key fix for the 21k limit.
    """
    bank_name = bank_cfg["name"]
    bank_id = bank_cfg["id"]

    algorithm = await asyncio.to_thread(get_bank_algorithm, bank_id)
    if not algorithm:
        algorithm = ""

    logging.info("Starting ingestion for bank %s (id=%s)", bank_name, bank_id)

    # Fetch BCB rate once before we start paging — avoid hammering BCB per batch.
    rate = await _get_bcb_rate_with_fallback(None)
    last_rate = rate
    total_inserted = 0
    batch_count = 0

    async for batch in fetch_bank_accounts_batches(bank_name, batch_size=500):
        if not batch:
            continue

        batch_count += 1

        # Refresh rate every 10 batches (every ~5000 records) rather than per batch.
        if batch_count % 10 == 0:
            rate = await _get_bcb_rate_with_fallback(last_rate)
            last_rate = rate

        db_batch = []
        verify_batch = []
        log_lines = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for account in batch:
            decrypted = decrypt_account_fields(account, algorithm)
            saldo_usd, saldo_bs = calculate_balances(decrypted, rate)
            verification_code = generate_verification_code()
            nro_cuenta = decrypted.get("NroCuenta", "")

            db_batch.append({
                "nro": int(decrypted.get("Nro", 0)),
                "identificacion": decrypted.get("Identificacion", ""),
                "nombres": decrypted.get("Nombres", ""),
                "apellidos": decrypted.get("Apellidos", ""),
                "nro_cuenta": nro_cuenta,
                "banco_id": bank_id,
                "saldo_bs": saldo_bs,
                "saldo_usd": saldo_usd,
                "codigo_verificacion": verification_code,
            })

            verify_batch.append({
                "NroCuenta": nro_cuenta,
                "verification_code": verification_code
            })

            log_lines.append(f"{now_str} | Tipo Cambio: {rate} | NroCuenta: {nro_cuenta} | ID Banco: {bank_id}\n")

        # Insert to DB — this is fast and must be done synchronously.
        await asyncio.to_thread(upsert_accounts_batch, db_batch)
        total_inserted += len(db_batch)

        # Enqueue verification — handled by background worker, never blocks pagination.
        await verify_queue.put((bank_name, verify_batch))

        logging.info(
            "Bank %s: batch %d done, total so far: %d",
            bank_name, batch_count, total_inserted
        )

        # Write log lines in background, don't block pagination.
        try:
            with open("asfi_extraction.log", "a") as logf:
                logf.writelines(log_lines)
        except Exception as e:
            logging.error("Failed to write to asfi_extraction.log: %s", e)

    logging.info(
        "Completed ingestion for bank %s — %d records in %d batches",
        bank_name, total_inserted, batch_count
    )


async def verification_worker(verify_queue: asyncio.Queue):
    """Background worker that sends verification codes without blocking paginators."""
    while True:
        item = await verify_queue.get()
        if item is None:
            # Sentinel: time to stop.
            verify_queue.task_done()
            break
        bank_name, verify_batch = item
        try:
            await send_verification_codes_batch(bank_name, verify_batch)
        except Exception as e:
            logging.error("Error sending verifications for %s: %s", bank_name, e)
        finally:
            verify_queue.task_done()


async def ingest_once():
    logging.info("Starting concurrent bulk ingestion for all banks...")

    verify_queue: asyncio.Queue = asyncio.Queue()

    # Start background verification worker.
    worker_task = asyncio.create_task(verification_worker(verify_queue))

    # Run all bank ingestions concurrently.
    bank_tasks = [process_bank(bank_cfg, verify_queue) for bank_cfg in BANKS]
    await asyncio.gather(*bank_tasks)

    # Signal worker to stop and wait for it to drain the queue.
    await verify_queue.put(None)
    await worker_task

    logging.info("Ingestion complete.")


async def run_loop(interval: int):
    while True:
        await ingest_once()
        await asyncio.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="ASFI central ingestion service")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single ingestion pass and exit",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=0,
        help="If set, run ingestion in a loop every N seconds",
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help="Optional log file path",
    )

    args = parser.parse_args()

    configure_logging(log_file=args.log_file)

    if args.once or args.interval <= 0:
        asyncio.run(ingest_once())
    else:
        asyncio.run(run_loop(args.interval))


if __name__ == "__main__":
    main()
