# ECC\n
from Crypto.PublicKey import ECC
import base64

def encrypt(text: str) -> str:
    # Simulación de salida de curva elíptica
    return base64.b64encode(f"ECC-P256-{text}".encode()).decode()