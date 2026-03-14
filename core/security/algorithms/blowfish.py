# Blowfish\n
from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import pad
import base64

def encrypt(text: str, key: str = "secretkey") -> str:
    cipher = Blowfish.new(key.encode(), Blowfish.MODE_CBC)
    ct = cipher.encrypt(pad(text.encode(), Blowfish.block_size))
    return base64.b64encode(cipher.iv + ct).decode()
