from .security.encryption_manager import decrypt as decrypt_payload
from .security.key_manager import derive_bank_key


def decrypt_bank_payload(bank_id: str, payload: str, key: str = None) -> str:
    """Desencripta el payload de un banco usando su algoritmo asignado y llave maestra."""
    bank_key = key or derive_bank_key(bank_id)
    return decrypt_payload(bank_id, payload, bank_key)


def get_algorithm_for_bank(bank_id: str) -> str:
    from .security.encryption_manager import BANK_ALGORITHM
    return BANK_ALGORITHM.get(bank_id, 'atbash')
