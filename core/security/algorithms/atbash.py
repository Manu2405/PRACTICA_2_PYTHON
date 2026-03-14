# Atbash\n
def encrypt(text: str) -> str:
    abc = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
    rev = abc[::-1]
    text = text.upper()
    return "".join([rev[abc.index(c)] if c in abc else c for c in text])