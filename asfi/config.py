import os
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv


# Load local environment for ASFI service
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / "envs" / ".env")


# BCB Exchange simulator
BCB_URL: str = os.getenv("BCB_URL", "http://127.0.0.1:8001/rate")

# ASFI central MySQL connection (asfi_central)
ASFI_DB_USER: str = os.getenv("ASFI_DB_USER", "root")
ASFI_DB_PASSWORD: str = os.getenv("ASFI_DB_PASSWORD", "root123")
ASFI_DB_HOST: str = os.getenv("ASFI_DB_HOST", "localhost")
ASFI_DB_PORT: int = int(os.getenv("ASFI_DB_PORT", "3306"))
ASFI_DB_NAME: str = os.getenv("ASFI_DB_NAME", "asfi_central")


# Optional private keys for asymmetric decryption
RSA_PRIVATE_KEY: Optional[str] = os.getenv("RSA_PRIVATE_KEY")
ECC_PRIVATE_KEY: Optional[str] = os.getenv("ECC_PRIVATE_KEY")
ELGAMAL_PRIVATE_KEY: Optional[str] = os.getenv("ELGAMAL_PRIVATE_KEY")


# Bank API endpoints (same ports used by api/run_all.py)
# Each bank has a token as configured in the bank API's .env file.
BANKS: List[Dict[str, str]] = [
    {"id": 1, "name": "banco_union", "port": 8881, "token_env": "TOKEN_BANCO_UNION"},
    {"id": 4, "name": "bcp", "port": 8882, "token_env": "TOKEN_BCP"},
    {"id": 10, "name": "fortaleza", "port": 8883, "token_env": "TOKEN_FORTALEZA"},
    {"id": 2, "name": "mercantil", "port": 8884, "token_env": "TOKEN_MERCANTIL"},
    {"id": 5, "name": "bisa", "port": 8885, "token_env": "TOKEN_BISA"},
    {"id": 9, "name": "solidario", "port": 8886, "token_env": "TOKEN_SOLIDARIO"},
    {"id": 13, "name": "desarrollo_productivo", "port": 8887, "token_env": "TOKEN_DESARROLLO_PRODUCTIVO"},
    {"id": 3, "name": "bnb", "port": 8888, "token_env": "TOKEN_BNB"},
    {"id": 7, "name": "economico", "port": 8889, "token_env": "TOKEN_ECONOMICO"},
    {"id": 11, "name": "fie", "port": 8890, "token_env": "TOKEN_FIE"},
    {"id": 6, "name": "ganadero", "port": 8891, "token_env": "TOKEN_GANADERO"},
    {"id": 8, "name": "prodem", "port": 8892, "token_env": "TOKEN_PRODEM"},
    {"id": 12, "name": "pyme_comunidad", "port": 8893, "token_env": "TOKEN_PYME_COMUNIDAD"},
    {"id": 14, "name": "argentina", "port": 8894, "token_env": "TOKEN_ARGENTINA"},
]


def get_bank_token(bank_name: str) -> Optional[str]:
    cfg = next((b for b in BANKS if b["name"] == bank_name), None)
    if not cfg:
        return None
    return os.getenv(cfg["token_env"])


def get_bank_url(bank_name: str) -> Optional[str]:
    cfg = next((b for b in BANKS if b["name"] == bank_name), None)
    if not cfg:
        return None
    return f"http://127.0.0.1:{cfg['port']}"


def get_asfi_db_url() -> str:
    return (
        f"mysql+pymysql://{ASFI_DB_USER}:{ASFI_DB_PASSWORD}@"
        f"{ASFI_DB_HOST}:{ASFI_DB_PORT}/{ASFI_DB_NAME}"
    )
