# Twofish\n
from Crypto.Cipher import Blowfish
import base64

def encrypt(text: str, key: str = "key_for_twofish_sim") -> str:
    cipher = Blowfish.new(key.encode(), Blowfish.MODE_EAX)
    ct, tag = cipher.encrypt_and_digest(text.encode())
    return base64.b64encode(cipher.nonce + ct).decode()