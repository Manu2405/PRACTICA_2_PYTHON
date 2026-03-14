# AES\n
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

def encrypt(text: str, key: str = "1234567890123456") -> str:
    cipher = AES.new(key.encode()[:16], AES.MODE_CBC)
    ct = cipher.encrypt(pad(text.encode(), AES.block_size))
    return base64.b64encode(cipher.iv + ct).decode()