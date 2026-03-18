from Crypto.Cipher import AES, DES3, DES, Blowfish, ChaCha20
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
import base64


def encode(b):
    return base64.b64encode(b).decode()

def decode(s):
    return base64.b64decode(s)


# AES
def aes_encrypt(text,key):
    cipher=AES.new(key,AES.MODE_EAX)
    ciphertext,tag=cipher.encrypt_and_digest(text.encode())
    return encode(cipher.nonce+ciphertext)

def aes_decrypt(data,key):
    raw=decode(data)
    nonce=raw[:16]
    ciphertext=raw[16:]
    cipher=AES.new(key,AES.MODE_EAX,nonce=nonce)
    return cipher.decrypt(ciphertext).decode()


# DES
def des_encrypt(text,key):
    cipher=DES.new(key,DES.MODE_EAX)
    ciphertext,tag=cipher.encrypt_and_digest(text.encode())
    return encode(cipher.nonce+ciphertext)

def des_decrypt(data,key):
    raw=decode(data)
    nonce=raw[:16]
    ciphertext=raw[16:]
    cipher=DES.new(key,DES.MODE_EAX,nonce=nonce)
    return cipher.decrypt(ciphertext).decode()


# 3DES
def des3_encrypt(text,key):
    cipher=DES3.new(key,DES3.MODE_EAX)
    ciphertext,tag=cipher.encrypt_and_digest(text.encode())
    return encode(cipher.nonce+ciphertext)

def des3_decrypt(data,key):
    raw=decode(data)
    nonce=raw[:16]
    ciphertext=raw[16:]
    cipher=DES3.new(key,DES3.MODE_EAX,nonce=nonce)
    return cipher.decrypt(ciphertext).decode()


# BLOWFISH
def blowfish_encrypt(text,key):
    cipher=Blowfish.new(key,Blowfish.MODE_EAX)
    ciphertext,tag=cipher.encrypt_and_digest(text.encode())
    return encode(cipher.nonce+ciphertext)

def blowfish_decrypt(data,key):
    raw=decode(data)
    nonce=raw[:16]
    ciphertext=raw[16:]
    cipher=Blowfish.new(key,Blowfish.MODE_EAX,nonce=nonce)
    return cipher.decrypt(ciphertext).decode()


# CHACHA20
def chacha_encrypt(text, key):
    # ChaCha20 requires a 32-byte key. If the provided key is shorter/longer,
    # derive a 32-byte key using SHA-256 for deterministic reproducibility.
    if len(key) != 32:
        key = SHA256.new(key).digest()

    cipher = ChaCha20.new(key=key)
    ciphertext = cipher.encrypt(text.encode())
    return encode(cipher.nonce + ciphertext)

def chacha_decrypt(data,key):
    if len(key) != 32:
        key = SHA256.new(key).digest()
    raw=decode(data)
    nonce=raw[:8]
    ciphertext=raw[8:]
    cipher=ChaCha20.new(key=key,nonce=nonce)
    return cipher.decrypt(ciphertext).decode()