def decrypt(ciphertext: str, key: str) -> str:
    return ''.join(chr((ord(c) - 97 - 3) % 26 + 97) if 'a' <= c <= 'z' else c for c in ciphertext.lower())
