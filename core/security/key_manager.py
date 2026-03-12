from typing import Optional

# Llave maestra de cada banco (puede derivarse de KDF en ambiente real)
MASTER_KEYS = {
    "bank_a": "00112233445566778899aabbccddeeff",
    "bank_b": "112233445566778899aabbccddeeff00",
    "bank_c": "2233445566778899aabbccddeeff0011",
    "bank_d": "33445566778899aabbccddeeff001122",
    "bank_e": "445566778899aabbccddeeff00112233",
    "bank_f": "5566778899aabbccddeeff0011223344",
    "bank_g": "66778899aabbccddeeff001122334455",
    "bank_h": "778899aabbccddeeff00112233445566",
    "bank_i": "8899aabbccddeeff0011223344556677",
    "bank_j": "99aabbccddeeff001122334455667788",
    "bank_k": "aabbccddeeff00112233445566778899",
    "bank_l": "bbccddeeff00112233445566778899aa",
    "bank_m": "ccddeeff00112233445566778899aabb",
    "bank_n": "ddeeff00112233445566778899aabbcc",
}

DEFAULT_MASTER_KEY = "ffeeddccbbaa99887766554433221100"


def get_master_key(bank_id: str) -> str:
    """Devuelve la llave maestra basada en el banco."""
    return MASTER_KEYS.get(bank_id, DEFAULT_MASTER_KEY)


def derive_bank_key(bank_id: str, purpose: str = "decryption") -> str:
    """Deriva una llave de banco (placeholder) según el propósito."""
    master = get_master_key(bank_id)
    return f"{master[:16]}:{purpose}" if bank_id else DEFAULT_MASTER_KEY


def register_master_key(bank_id: str, key_hex: str) -> None:
    """Registra o actualiza la llave maestra de un banco."""
    MASTER_KEYS[bank_id] = key_hex
