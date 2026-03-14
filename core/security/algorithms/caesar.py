# Cifrado C�sar\n
def encrypt(text: str, shift: int = 3) -> str:
    res = ""
    for char in text:
        if char.isalpha():
            start = ord('A') if char.isupper() else ord('a')
            res += chr((ord(char) - start + shift) % 26 + start)
        else:
            res += char
    return res