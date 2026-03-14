# RSA\n
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

key = RSA.generate(2048)
cipher = PKCS1_OAEP.new(key.publickey())

def encrypt(text: str) -> str:
    return base64.b64encode(cipher.encrypt(text.encode())).decode()