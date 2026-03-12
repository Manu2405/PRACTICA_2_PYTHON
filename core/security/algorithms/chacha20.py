from Crypto.Cipher import ChaCha20


def decrypt(ciphertext: str, key: str) -> str:
    try:
        raw = bytes.fromhex(ciphertext)
    except Exception:
        raw = ciphertext.encode('utf-8')

    key_bytes = (key.encode('utf-8') + b'0'*32)[:32]
    nonce = key_bytes[:8]

    try:
        cipher = ChaCha20.new(key=key_bytes, nonce=nonce)
        return cipher.decrypt(raw).decode('utf-8', errors='ignore')
    except Exception:
        return f"ChaCha20-decrypt-fallback({ciphertext})"

