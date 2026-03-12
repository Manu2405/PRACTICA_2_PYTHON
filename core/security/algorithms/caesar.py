import string


def decrypt(ciphertext: str, key: str) -> str:
    offset = int(key) % 26 if key and key.isdigit() else 3
    alpha = string.ascii_lowercase
    return ''.join(alpha[(alpha.index(c)-offset)%26] if c in alpha else c for c in ciphertext.lower())
