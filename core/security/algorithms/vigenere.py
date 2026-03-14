# Vigen�re\n
def encrypt(text: str, key: str = "ASFI") -> str:
    res = ""
    key = key.upper()
    text = text.upper()
    for i, char in enumerate(text):
        if char.isalpha():
            shift = ord(key[i % len(key)]) - ord('A')
            res += chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
        else:
            res += char
    return res