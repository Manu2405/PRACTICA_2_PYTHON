# 3DES\n
from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad
import base64

def encrypt(text: str, key: str = "123456789012345678901234") -> str:
    cipher = DES3.new(key.encode()[:24], DES3.MODE_CBC)
    ct = cipher.encrypt(pad(text.encode(), DES3.block_size))
    return base64.b64encode(cipher.iv + ct).decode()