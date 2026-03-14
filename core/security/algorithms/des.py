# DES (pycryptodome)\n
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad
import base64

def encrypt(text: str, key: str = "8bytekey") -> str:
    cipher = DES.new(key.encode()[:8], DES.MODE_CBC)
    ct = cipher.encrypt(pad(text.encode(), DES.block_size))
    return base64.b64encode(cipher.iv + ct).decode()