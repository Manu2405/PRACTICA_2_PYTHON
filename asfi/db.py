import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, Any

from sqlalchemy import create_engine, text

from .config import get_asfi_db_url

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(
            get_asfi_db_url(), 
            pool_size=20, 
            max_overflow=20, 
            pool_pre_ping=True
        )
    return _engine


def normalize_account_dict(row: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize account dictionary keys to CamelCase regardless of source format.
    
    Handles both CamelCase (from MySQL) and lowercase (from Postgres, MongoDB, API responses).
    """
    
    # Create a lowercase version for lookup
    lower_row = {k.lower(): v for k, v in row.items()}
    
    return {
        "Nro": lower_row.get("nro"),
        "Identificacion": lower_row.get("identificacion"),
        "Nombres": lower_row.get("nombres"),
        "Apellidos": lower_row.get("apellidos"),
        "NroCuenta": lower_row.get("nrocuenta"),
        "IdBanco": lower_row.get("idbanco") or lower_row.get("bancoid"),
        "Saldo": lower_row.get("saldo"),
        "SaldoUSD": lower_row.get("saldousd"),
        "SaldoBs": lower_row.get("saldobs"),
    }


def get_bank_algorithm(bank_id: int) -> str | None:
    """Query the Bancos table to discover the encryption algorithm for a bank."""

    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT AlgoritmoEncriptacion FROM Bancos WHERE BancoId = :id"),
            {"id": bank_id},
        )
        row = result.fetchone()
        return row[0] if row else None


def upsert_account(
    nro: int,
    identificacion: str,
    nombres: str,
    apellidos: str,
    nro_cuenta: str,
    banco_id: int,
    saldo_bs: Decimal,
    saldo_usd: Decimal,
    codigo_verificacion: str | None = None,
    created_by: str = "asfi_service",
) -> None:
    """Insert or update a record in the ASFI central Cuentas table."""

    engine = get_engine()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    with engine.begin() as conn:
        conn.execute(
            text(
                """INSERT INTO Cuentas
                (Nro, Identificacion, Nombres, Apellidos, NroCuenta, BancoId,
                 SaldoBs, SaldoUSD, CodigoVerificacion, CreatedAt, CreatedBy)
                VALUES
                (:nro, :identificacion, :nombres, :apellidos, :nro_cuenta, :banco_id,
                 :saldo_bs, :saldo_usd, :codigo_verificacion, :created_at, :created_by)
                ON DUPLICATE KEY UPDATE
                  Identificacion = VALUES(Identificacion),
                  Nombres = VALUES(Nombres),
                  Apellidos = VALUES(Apellidos),
                  NroCuenta = VALUES(NroCuenta),
                  BancoId = VALUES(BancoId),
                  SaldoBs = VALUES(SaldoBs),
                  SaldoUSD = VALUES(SaldoUSD),
                  CodigoVerificacion = VALUES(CodigoVerificacion),
                  CreatedAt = VALUES(CreatedAt),
                  CreatedBy = VALUES(CreatedBy)
                """
            ),
            {
                "nro": nro,
                "identificacion": identificacion,
                "nombres": nombres,
                "apellidos": apellidos,
                "nro_cuenta": nro_cuenta,
                "banco_id": banco_id,
                "saldo_bs": str(saldo_bs),
                "saldo_usd": str(saldo_usd),
                "codigo_verificacion": codigo_verificacion,
                "created_at": now,
                "created_by": created_by,
            },
        )


def upsert_accounts_batch(
    accounts: list[dict],
    created_by: str = "asfi_service",
) -> None:
    """Insert or update a batch of records in the ASFI central Cuentas table."""

    if not accounts:
        return

    engine = get_engine()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    for acc in accounts:
        acc["created_at"] = now
        acc["created_by"] = created_by
        acc["saldo_bs"] = str(acc["saldo_bs"])
        acc["saldo_usd"] = str(acc["saldo_usd"])

    with engine.begin() as conn:
        conn.execute(
            text(
                """INSERT INTO Cuentas
                (Nro, Identificacion, Nombres, Apellidos, NroCuenta, BancoId,
                 SaldoBs, SaldoUSD, CodigoVerificacion, CreatedAt, CreatedBy)
                VALUES
                (:nro, :identificacion, :nombres, :apellidos, :nro_cuenta, :banco_id,
                 :saldo_bs, :saldo_usd, :codigo_verificacion, :created_at, :created_by)
                ON DUPLICATE KEY UPDATE
                  Identificacion = VALUES(Identificacion),
                  Nombres = VALUES(Nombres),
                  Apellidos = VALUES(Apellidos),
                  NroCuenta = VALUES(NroCuenta),
                  BancoId = VALUES(BancoId),
                  SaldoBs = VALUES(SaldoBs),
                  SaldoUSD = VALUES(SaldoUSD),
                  CodigoVerificacion = VALUES(CodigoVerificacion),
                  CreatedAt = VALUES(CreatedAt),
                  CreatedBy = VALUES(CreatedBy)
                """
            ),
            accounts,
        )


def safe_decimal(value) -> Decimal:
    try:
        if value is None:
            return Decimal(0)
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        logging.warning("Could not parse value %r as Decimal", value)
        return Decimal(0)
