def decrypt(ciphertext: str, key: str) -> str:
    normalized = ''.join(ciphertext.upper().split())
    pairs = [normalized[i:i+2] for i in range(0, len(normalized), 2)]
    return ''.join(p[::-1] for p in pairs)