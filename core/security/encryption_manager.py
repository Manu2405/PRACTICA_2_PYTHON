from typing import Optional
from .key_manager import derive_bank_key
from .algorithms import ALGOS

BANK_ALGORITHM = {
    'bank_union': 'caesar',
    'bank_mercantil': 'atbash',
    'bank_bnb': 'vigenere',
    'bank_bcp': 'playfair',
    'bank_bisa': 'hill',
    'bank_ganadero': 'des',
    'bank_economico': 'triple_des',
    'bank_prodem': 'blowfish',
    'bank_solidario': 'twofish',
    'bank_fortaleza': 'aes',
    'bank_fie': 'rsa',
    'bank_pyme': 'elgamal',
    'bank_desarrollo': 'ecc',
    'bank_argentina': 'chacha20',
}


def decrypt(bank_id: str, ciphertext: str, key: Optional[str] = None) -> str:
    algorithm_key = BANK_ALGORITHM.get(bank_id, 'atbash')
    if algorithm_key not in ALGOS:
        algorithm_key = 'atbash'

    algo_module = ALGOS[algorithm_key]
    bank_key = key or derive_bank_key(bank_id)
    try:
        return algo_module.decrypt(ciphertext, bank_key)
    except Exception as e:
        return f"error({algorithm_key}): {e}"
                                        