import asyncio
import logging
from typing import Any, Dict, Optional, List

import httpx

from .config import BCB_URL, get_bank_token, get_bank_url


async def fetch_bank_accounts_paginated(bank_name: str, batch_size: int = 1000, timeout: int = 120):
    """Fetch accounts from a bank API using pagination.

    Yields individual account dicts.
    """

    base_url = get_bank_url(bank_name)
    if not base_url:
        logging.warning("No URL configured for bank %s", bank_name)
        return

    token = get_bank_token(bank_name)
    if not token:
        logging.warning("No token found for bank %s", bank_name)
        return

    headers = {"Authorization": f"Bearer {token}"}
    offset = 0

    async with httpx.AsyncClient(timeout=timeout) as client:
        while True:
            url = f"{base_url}/accounts?limit={batch_size}&offset={offset}"
            try:
                resp = await client.get(url, headers=headers)
            except Exception as e:
                logging.error("Error requesting %s: %s", url, e)
                break

            if resp.status_code != 200:
                logging.error("Bank %s returned %s: %s", bank_name, resp.status_code, resp.text)
                break

            data = resp.json()
            accounts = data.get("accounts") or []
            
            for acc in accounts:
                yield acc
                
            if len(accounts) < batch_size:
                break
                
            offset += batch_size


async def fetch_bank_accounts_batches(bank_name: str, batch_size: int = 500, timeout: int = 300):
    """Fetch accounts from a bank API using pagination.
    Yields list of account dicts at a time.
    """
    base_url = get_bank_url(bank_name)
    if not base_url:
        logging.warning("No URL configured for bank %s", bank_name)
        return

    token = get_bank_token(bank_name)
    if not token:
        logging.warning("No token found for bank %s", bank_name)
        return

    headers = {"Authorization": f"Bearer {token}"}
    offset = 0
    max_retries = 5
    total_fetched = 0

    async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as client:
        while True:
            url = f"{base_url}/accounts?limit={batch_size}&offset={offset}"
            success = False
            resp = None
            for attempt in range(max_retries):
                try:
                    resp = await client.get(url, headers=headers)
                    if resp.status_code == 200:
                        success = True
                        break
                    logging.error(
                        "Bank %s returned %s at offset %s (attempt %d): %s",
                        bank_name, resp.status_code, offset, attempt + 1, resp.text[:200]
                    )
                except Exception as e:
                    logging.error(
                        "Error requesting %s (attempt %d): %s", url, attempt + 1, e
                    )
                await asyncio.sleep(min(2 ** attempt, 30))

            if not success:
                logging.error(
                    "Max retries reached for bank %s at offset %s. Stopping pagination.",
                    bank_name, offset
                )
                break

            try:
                data = resp.json()
            except Exception:
                logging.error("Invalid JSON for bank %s at offset %s", bank_name, offset)
                break

            accounts = data.get("accounts") or []
            count = len(accounts)

            if accounts:
                total_fetched += count
                logging.info(
                    "Bank %s: fetched %d accounts at offset %s (total so far: %d)",
                    bank_name, count, offset, total_fetched
                )
                yield accounts

            if count < batch_size:
                logging.info(
                    "Bank %s: pagination complete — %d total records fetched.",
                    bank_name, total_fetched
                )
                break

            offset += batch_size


async def send_verification_code(bank_name: str, nro_cuenta: str, code: str, timeout: int = 30) -> bool:
    """Send a verification code to a bank API.

    Returns True if successful, False otherwise.
    """

    base_url = get_bank_url(bank_name)
    if not base_url:
        logging.warning("No URL configured for bank %s", bank_name)
        return False

    token = get_bank_token(bank_name)
    if not token:
        logging.warning("No token found for bank %s", bank_name)
        return False

    url = f"{base_url}/verify"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"items": [{"NroCuenta": nro_cuenta, "verification_code": code}]}

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.post(url, headers=headers, json=payload)
        except Exception as e:
            logging.error("Error sending verification to %s: %s", bank_name, e)
            return False

        if resp.status_code != 200:
            logging.error("Bank %s verify returned %s: %s", bank_name, resp.status_code, resp.text)
            return False

        return True


async def send_verification_codes_batch(bank_name: str, items: List[Dict[str, str]], timeout: int = 120) -> bool:
    """Send a batch of verification codes to a bank API."""
    if not items:
        return True

    base_url = get_bank_url(bank_name)
    if not base_url:
        logging.warning("No URL configured for bank %s", bank_name)
        return False

    token = get_bank_token(bank_name)
    if not token:
        logging.warning("No token found for bank %s", bank_name)
        return False

    url = f"{base_url}/verify"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"items": items}

    max_retries = 3
    retries = 0
    async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as client:
        while retries < max_retries:
            try:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    return True
                logging.error("Bank %s verify batch returned %s: %s", bank_name, resp.status_code, resp.text)
            except Exception as e:
                logging.error("Error sending verification batch to %s: %s", bank_name, e)
            retries += 1
            await asyncio.sleep(2)
        return False


async def get_bcb_rate(timeout: int = 10) -> Optional[float]:
    """Fetch the current USD/BOB rate from the BCB simulator."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.get(BCB_URL)
        except Exception as e:
            logging.error("Error requesting BCB rate: %s", e)
            return None

        if resp.status_code != 200:
            logging.error("BCB rate endpoint returned %s: %s", resp.status_code, resp.text)
            return None

        payload = resp.json()
        rate = payload.get("rate")
        try:
            return float(rate)
        except Exception as e:
            logging.error("Invalid rate value from BCB: %r (%s)", rate, e)
            return None


# Removed fetch_all_banks_accounts to prevent OOM when loading 120,000 accs
