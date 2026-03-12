from Crypto.Cipher import DES


def decrypt(ciphertext: str, key: str) -> str:
    try:
        raw = bytes.fromhex(ciphertext)
    except Exception:
        raw = ciphertext.encode('utf-8')

    key_bytes = (key.encode('utf-8') + b'0'*8)[:8]
    iv = key_bytes

    try:
        cipher = DES.new(key_bytes, DES.MODE_CBC, iv=iv)
        plaintext = cipher.decrypt(raw)
        return plaintext.decode('utf-8', errors='ignore').rstrip('\x00')
    except Exception:
        return f"DES-decrypt-fallback({ciphertext})"
 #(pycryptodome)
