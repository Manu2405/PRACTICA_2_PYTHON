from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64



def encode(b):
    return base64.b64encode(b).decode()

def decode(s):
    return base64.b64decode(s)


# RSA
def rsa_generate():
    key=RSA.generate(2048)
    return key.publickey().export_key(),key.export_key()

def rsa_encrypt(text, public_key=None):
    # If no public key is provided, generate a temporary key pair.
    if public_key is None:
        key_pair = RSA.generate(2048)
        public_key = key_pair.publickey().export_key()

    key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(key)
    return encode(cipher.encrypt(text.encode()))

def rsa_decrypt(data,private_key):
    key=RSA.import_key(private_key)
    cipher=PKCS1_OAEP.new(key)
    return cipher.decrypt(decode(data)).decode()


# ECC (simplificado)
def ecc_generate():

    key = ECC.generate(curve="P-256")

    return key.public_key().export_key(format="PEM"), key.export_key(format="PEM")


def ecc_encrypt(text, public_key=None):
    # If no public key is provided, generate an ephemeral key pair.
    if public_key is None:
        key = ECC.generate(curve="P-256")
        public_key = key.public_key().export_key(format="PEM")

    pub_key = ECC.import_key(public_key)

    # clave efímera
    eph_key = ECC.generate(curve="P-256")

    # In ECDH, the shared secret is the peer public point multiplied by our private scalar.
    shared_secret = pub_key.pointQ * eph_key.d

    key = SHA256.new(str(shared_secret.x).encode()).digest()

    cipher = AES.new(key, AES.MODE_EAX)

    ciphertext, tag = cipher.encrypt_and_digest(text.encode())

    data = {
        "ephemeral": eph_key.public_key().export_key(format="PEM"),
        "nonce": base64.b64encode(cipher.nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    }

    return base64.b64encode(str(data).encode()).decode()


def ecc_decrypt(data, private_key):

    priv_key = ECC.import_key(private_key)

    decoded = eval(base64.b64decode(data).decode())

    eph_key = ECC.import_key(decoded["ephemeral"])

    shared_secret = eph_key.pointQ * priv_key.d

    key = SHA256.new(str(shared_secret.x).encode()).digest()

    nonce = base64.b64decode(decoded["nonce"])

    ciphertext = base64.b64decode(decoded["ciphertext"])

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

    plaintext = cipher.decrypt(ciphertext)

    return plaintext.decode()
#ELGAMAL
from Crypto.PublicKey import ElGamal
from Crypto.Random import random
from Crypto.Util.number import bytes_to_long, long_to_bytes
import base64


def elgamal_generate():

    key = ElGamal.generate(2048, get_random_bytes)

    return key.publickey(), key


def elgamal_encrypt(text, public_key=None):
    # If a public key is not provided, generate a temporary keypair.
    if public_key is None:
        key = ElGamal.generate(2048, get_random_bytes)
        public_key = key.publickey()

    m = bytes_to_long(text.encode())

    p = int(public_key.p)
    k = random.StrongRandom().randint(1, p - 2)

    c1 = pow(int(public_key.g), k, p)
    c2 = (m * pow(int(public_key.y), k, p)) % p

    return base64.b64encode(f"{c1}:{c2}".encode()).decode()


def elgamal_decrypt(data,private_key):

    decoded=base64.b64decode(data).decode()

    c1,c2=map(int,decoded.split(":"))

    s=pow(c1,private_key.x,private_key.p)

    m=(c2*pow(s,-1,private_key.p))%private_key.p

    return long_to_bytes(m).decode()