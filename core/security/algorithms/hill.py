# Hill\n
def encrypt(text: str) -> str:
    text = text.upper().replace(" ", "")
    if len(text) % 2 != 0: text += "X"
    res = ""
    # Matriz clave [[3, 3], [2, 5]]
    for i in range(0, len(text), 2):
        p = [ord(text[i]) - 65, ord(text[i+1]) - 65]
        res += chr(((3*p[0] + 3*p[1]) % 26) + 65)
        res += chr(((2*p[0] + 5*p[1]) % 26) + 65)
    return res