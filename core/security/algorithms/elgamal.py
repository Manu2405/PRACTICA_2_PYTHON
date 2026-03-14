# ElGamal\n
import random

def encrypt(text: str) -> str:
    p, g, y = 7919, 2, 500 # Valores simulados
    res = []
    for c in text:
        k = random.randint(1, p-2)
        res.append(f"{pow(g, k, p)}-{(ord(c) * pow(y, k, p)) % p}")
    return "|".join(res)