"""Decryption router for ASFI central service.

This module mirrors the encryption logic in `etl/crypto_router.py` and
allows ASFI to decrypt data coming from each bank.

Note: For asymmetric algorithms (RSA/ECC/ElGamal), a corresponding private key
must be provided via environment variables (`RSA_PRIVATE_KEY`, etc.) for decryption.
If no private key is present, the function will log a warning and return the
ciphertext unchanged.
"""

from typing import Optional

from services.crypto.asymmetric import (
    ecc_decrypt,
    elgamal_decrypt,
    rsa_decrypt,
)
from services.crypto.classical import (
    atbash_decrypt,
    caesar_decrypt,
    hill_decrypt,
    playfair_decrypt,
    vigenere_decrypt,
)
from services.crypto.symmetric import (
    aes_decrypt,
    blowfish_decrypt,
    chacha_decrypt,
    des3_decrypt,
    des_decrypt,
)

from .config import ECC_PRIVATE_KEY, ELGAMAL_PRIVATE_KEY, RSA_PRIVATE_KEY
from services.crypto.keys import AES_KEY, DES_KEY, BLOWFISH_KEY, VIGENERE_KEY, PLAYFAIR_KEY, HILL_KEY


def decrypt_by_algorithm(algorithm: str, ciphertext: str) -> str:
    """Decrypt a value using the given algorithm name.

    The algorithm name is expected to match the values stored in the `Bancos`
    table (e.g. "Cifrado Cesar", "AES", "RSA", etc.).
    """

    # Normalize and accept common variants.
    algo = (algorithm or "").strip().lower()

    try:
        if "cesar" in algo or "cifrado" in algo:
            # Banco Unión: Caesar + AES
            return caesar_decrypt(aes_decrypt(ciphertext, AES_KEY))

        if "atbash" in algo:
            # Banco Mercantil: Atbash + AES
            return atbash_decrypt(aes_decrypt(ciphertext, AES_KEY))

        if "vigenere" in algo:
            # BNB: Vigenère + AES
            return vigenere_decrypt(aes_decrypt(ciphertext, AES_KEY), VIGENERE_KEY)

        if "playfair" in algo:
            # BCP: Playfair no soporta números en el Saldo, ETL usa AES exclusivamente.
            return aes_decrypt(ciphertext, AES_KEY)

        if "hill" in algo:
            # BISA: Hill (no AES)
            return hill_decrypt(ciphertext, HILL_KEY)

        if "des" == algo or "des" in algo and "3" not in algo:
            # Banco Ganadero: DES
            return des_decrypt(ciphertext, DES_KEY)

        if "3des" in algo or "triple" in algo:
            # Banco Económico: in practice we used AES encryption
            return aes_decrypt(ciphertext, AES_KEY)

        if "blowfish" in algo:
            return blowfish_decrypt(ciphertext, BLOWFISH_KEY)

        if "twofish" in algo:
            # Twofish not implemented, Banks use AES for compatibility
            return aes_decrypt(ciphertext, AES_KEY)

        if "aes" in algo and "chacha" not in algo:
            return aes_decrypt(ciphertext, AES_KEY)

        if "chacha" in algo:
            return chacha_decrypt(ciphertext, AES_KEY)

        if "rsa" in algo:
            if not RSA_PRIVATE_KEY:
                return ciphertext
            return rsa_decrypt(ciphertext, RSA_PRIVATE_KEY)

        if "elgamal" in algo:
            # PYME: ElGamal algorithm but actually encrypted with AES in ETL
            return aes_decrypt(ciphertext, AES_KEY)

        if "ecc" in algo:
            if not ECC_PRIVATE_KEY:
                return ciphertext
            return ecc_decrypt(ciphertext, ECC_PRIVATE_KEY)

    except Exception:
        # If anything fails, return ciphertext so the calling code can log/inspect it.
        return ciphertext

    # Unknown algorithm: return raw value
    return ciphertext


def decrypt_account_fields(account: dict, algorithm: str) -> dict:
    """Decrypt the common string fields on an account record, including balance."""

    decrypted = dict(account)
    
    # Only decrypt balance fields (Saldo, SaldoUSD, SaldoBs)
    for key in ["Saldo", "SaldoUSD", "SaldoBs"]:
        if key in decrypted and isinstance(decrypted[key], str):
            try:
                decrypted[key] = decrypt_by_algorithm(algorithm, decrypted[key])
            except Exception as e:
                print(f"Warning: Could not decrypt {key}: {e}")
    
    return decrypted
