# ChaCha20\n
from Crypto.Cipher import ChaCha20
import base64

def encrypt(text: str, key: str = "12345678901234567890123456789012") -> str:
    cipher = ChaCha20.new(key=key.encode()[:32])
    return base64.b64encode(cipher.nonce + cipher.encrypt(text.encode())).decode()