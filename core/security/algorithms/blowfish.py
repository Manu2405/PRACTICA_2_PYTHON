from Crypto.Cipher import Blowfish

def decrypt(ciphertext: str, key: str) -> str:
    try:
        raw = bytes.fromhex(ciphertext)
    except Exception:
        raw = ciphertext.encode('utf-8')

    key_bytes = (key.encode('utf-8') + b'0'*56)[:56]
    try:
        cipher = Blowfish.new(key_bytes, Blowfish.MODE_ECB)
        plaintext = cipher.decrypt(raw)
        return plaintext.decode('utf-8', errors='ignore').rstrip('\x00')
    except Exception:
        return f"Blowfish-decrypt-fallback({ciphertext})"