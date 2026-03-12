import string

def decrypt(ciphertext: str, key: str) -> str:
    alphabet = string.ascii_uppercase
    rev = alphabet[::-1]
    return ''.join(rev[alphabet.index(c)] if c in alphabet else c for c in ciphertext.upper())