from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def decrypt(ciphertext: str, key: str) -> str:
    try:
        raw = bytes.fromhex(ciphertext)
    except Exception:
        raw = ciphertext.encode('utf-8')

    key_bytes = (key.encode('utf-8') + b'0'*32)[:32]
    iv = key_bytes[:16]

    try:
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv=iv)
        decrypted = unpad(cipher.decrypt(raw), AES.block_size)
        return decrypted.decode('utf-8', errors='ignore')
    except Exception:
        return f"AES-decrypt-fallback({ciphertext})"

