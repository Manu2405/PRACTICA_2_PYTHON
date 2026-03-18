from services.crypto.classical import (
    caesar_encrypt,
    atbash_encrypt,
    vigenere_encrypt,
    playfair_encrypt,
    hill_encrypt
)

from services.crypto.symmetric import (
    des_encrypt,
    des3_encrypt,
    blowfish_encrypt,
    aes_encrypt,
    chacha_encrypt
)

from services.crypto.asymmetric import (
    rsa_encrypt,
    ecc_encrypt
)


from services.crypto.keys import (
    AES_KEY,
    DES_KEY,
    DES3_KEY,
    BLOWFISH_KEY,
    TWOFISH_KEY,
    VIGENERE_KEY,
    PLAYFAIR_KEY,
    HILL_KEY,
    RSA_PUBLIC_KEY,
    ECC_PUBLIC_KEY
)

# ======================================
# ROUTER DE ALGORITMOS
# ======================================

def encrypt_by_bank(bank_id, value):

    value = str(value)

    if bank_id == 1:  # Banco Unión S.A. - Caesar
        # Caesar cipher solo cifra letras, aplicar AES después
        classical = caesar_encrypt(value)
        return aes_encrypt(classical, AES_KEY)

    elif bank_id == 2:  # Banco Mercantil Santa Cruz - Atbash
        # Atbash solo cifra letras, aplicar AES después
        classical = atbash_encrypt(value)
        return aes_encrypt(classical, AES_KEY)

    elif bank_id == 3:  # BNB - Vigenère
        # Vigenère solo cifra letras, aplicar AES después
        classical = vigenere_encrypt(value, VIGENERE_KEY)
        return aes_encrypt(classical, AES_KEY)

    elif bank_id == 4:  # BCP - Playfair
        # Playfair works on letters so it deleted the Saldo completely.
        # Fallback strictly to AES to preserve Saldo integrity.
        return aes_encrypt(value, AES_KEY)

    elif bank_id == 5:  # BISA - Hill
        return hill_encrypt(value, HILL_KEY)

    elif bank_id == 6:  # Banco Ganadero - DES
        return des_encrypt(value, DES_KEY)

    elif bank_id == 7:  # Banco Económico - 3DES (usando AES como alternativa)
        # 3DES tiene problemas con tamaño de clave, usar AES
        return aes_encrypt(value, AES_KEY)

    elif bank_id == 8:  # Banco Prodem - Blowfish
        return blowfish_encrypt(value, BLOWFISH_KEY)

    elif bank_id == 9:  # Banco Solidario - AES (Twofish no disponible)
        return aes_encrypt(value, AES_KEY)

    elif bank_id == 10:  # Banco Fortaleza - AES
        return aes_encrypt(value, AES_KEY)

    elif bank_id == 11:  # Banco FIE - RSA
        return rsa_encrypt(value, RSA_PUBLIC_KEY)

    elif bank_id == 12:  # PYME de la Comunidad - ElGamal
        # ElGamal es muy lento, usar AES en su lugar
        return aes_encrypt(value, AES_KEY)

    elif bank_id == 13:  # Banco Desarrollo Productivo - ECC
        return ecc_encrypt(value, ECC_PUBLIC_KEY)

    elif bank_id == 14:  # Argentina - ChaCha20
        return chacha_encrypt(value, AES_KEY)

    return value