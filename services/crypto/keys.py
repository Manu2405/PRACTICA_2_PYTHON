import os
from dotenv import load_dotenv

load_dotenv()

AES_KEY = os.getenv("AES_KEY").encode()
DES_KEY = os.getenv("DES_KEY").encode()
DES3_KEY = os.getenv("DES3_KEY", os.getenv("DES_KEY") * 2).encode()  # Fallback to DES_KEY doubled
BLOWFISH_KEY = os.getenv("BLOWFISH_KEY").encode()
TWOFISH_KEY = os.getenv("TWOFISH_KEY").encode()

VIGENERE_KEY = os.getenv("VIGENERE_KEY")
PLAYFAIR_KEY = os.getenv("PLAYFAIR_KEY")

HILL_KEY = [
    [3, 3],
    [2, 5]
]

# Fixed public keys for asymmetric encryption
RSA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuCIZvsmJOE9HSEIl66ue
PiDZzQwqEiFhRnZx7UJT+1uKH6h+adyCPNvKwbDod1C03VZruLu8X1ZWXe6w3Z+x
/vZyMB8moQ0DL9TGytODvipf1XAOnzv/tHhc9eJSHtjVtn3rDlFbBBLaXEr9rhJa
7p98Q3FKHtjReHY/iq2xXbXFLcEDmesgIAkqYPOI9aLjYEA+h3s3E4/JJY+LSuoV
dAyw5aWNxBHJY6a8Q+x+wAWQ/VBFq15765HkPASBzsWQbcUTacrXBr3xJrLywkcq
4JNHDc4mQ0yKvfdftCJRAOwRZNEAtJZzq+yrq2Od0SXj6ViepWf7amQkufCtZGUL
3wIDAQAB
-----END PUBLIC KEY-----"""

ECC_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE/sZyNwvghso3I+a8nfxwhAoQdNNV
6DxN2MHPOIJSbhKtLHG4GJS9z1IniTmxfFYjMcTUFdlMgdeUlt5ZXfBZuw==
-----END PUBLIC KEY-----"""