# Playfair\n
def encrypt(text: str, key: str = "MONARCHY") -> str:
    matrix = "MONARCHYBCDEFGIKLPQRSTUVWXZ" # Matriz 5x5 simplificada
    text = text.upper().replace("J", "I").replace(" ", "")
    if len(text) % 2 != 0: text += "X"
    res = ""
    for i in range(0, len(text), 2):
        a, b = text[i], text[i+1]
        r1, c1 = divmod(matrix.find(a), 5)
        r2, c2 = divmod(matrix.find(b), 5)
        if r1 == r2: res += matrix[r1*5 + (c1+1)%5] + matrix[r2*5 + (c2+1)%5]
        elif c1 == c2: res += matrix[((r1+1)%5)*5 + c1] + matrix[((r2+1)%5)*5 + c2]
        else: res += matrix[r1*5 + c2] + matrix[r2*5 + c1]
    return res