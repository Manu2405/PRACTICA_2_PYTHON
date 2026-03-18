import string
import numpy as np

alphabet = string.ascii_uppercase


# CAESAR
def caesar_encrypt(text, shift=3):
    result = ""
    for c in text.upper():
        if c in alphabet:
            result += alphabet[(alphabet.index(c)+shift)%26]
        else:
            result += c
    return result

def caesar_decrypt(text, shift=3):
    return caesar_encrypt(text,-shift)


# ATBASH
def atbash_encrypt(text):
    result=""
    for c in text.upper():
        if c in alphabet:
            result+=alphabet[25-alphabet.index(c)]
        else:
            result+=c
    return result

def atbash_decrypt(text):
    return atbash_encrypt(text)


# VIGENERE
def vigenere_encrypt(text,key):
    result=""
    key=key.upper()
    k=0

    for c in text.upper():
        if c in alphabet:
            shift=alphabet.index(key[k%len(key)])
            result+=alphabet[(alphabet.index(c)+shift)%26]
            k+=1
        else:
            result+=c
    return result

def vigenere_decrypt(text,key):
    result=""
    key=key.upper()
    k=0

    for c in text.upper():
        if c in alphabet:
            shift=alphabet.index(key[k%len(key)])
            result+=alphabet[(alphabet.index(c)-shift)%26]
            k+=1
        else:
            result+=c
    return result
##Playfair
def playfair_matrix(key):
    key = key.upper().replace("J","I")
    matrix = []
    used = set()

    for c in key:
        if c not in used and c.isalpha():
            matrix.append(c)
            used.add(c)

    for c in "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if c not in used:
            matrix.append(c)

    return [matrix[i:i+5] for i in range(0,25,5)]


def playfair_find(matrix,char):
    for i in range(5):
        for j in range(5):
            if matrix[i][j]==char:
                return i,j


def playfair_prepare(text):
    text=text.upper().replace("J","I")
    text="".join([c for c in text if c.isalpha()])
    result=""
    i=0

    while i<len(text):
        a=text[i]
        b="X"

        if i+1<len(text):
            b=text[i+1]

        if a==b:
            result+=a+"X"
            i+=1
        else:
            result+=a+b
            i+=2

    if len(result)%2!=0:
        result+="X"

    return result


def playfair_encrypt(text,key):

    matrix=playfair_matrix(key)
    text=playfair_prepare(text)

    result=""

    for i in range(0,len(text),2):

        a=text[i]
        b=text[i+1]

        r1,c1=playfair_find(matrix,a)
        r2,c2=playfair_find(matrix,b)

        if r1==r2:
            result+=matrix[r1][(c1+1)%5]
            result+=matrix[r2][(c2+1)%5]

        elif c1==c2:
            result+=matrix[(r1+1)%5][c1]
            result+=matrix[(r2+1)%5][c2]

        else:
            result+=matrix[r1][c2]
            result+=matrix[r2][c1]

    return result


def playfair_decrypt(text,key):

    matrix=playfair_matrix(key)
    result=""

    for i in range(0,len(text),2):

        a=text[i]
        b=text[i+1]

        r1,c1=playfair_find(matrix,a)
        r2,c2=playfair_find(matrix,b)

        if r1==r2:
            result+=matrix[r1][(c1-1)%5]
            result+=matrix[r2][(c2-1)%5]

        elif c1==c2:
            result+=matrix[(r1-1)%5][c1]
            result+=matrix[(r2-1)%5][c2]

        else:
            result+=matrix[r1][c2]
            result+=matrix[r2][c1]

    return result
## Hill (supports arbitrary input by encoding to a restricted alphabet)
import numpy as np
import binascii

# We use a 16-character alphabet (A-P) to safely map any byte sequence
# into a format compatible with the classical Hill cipher implementation.
HILL_ALPHABET = "ABCDEFGHIJKLMNOP"


def _encode_for_hill(text: str) -> str:
    """Encode arbitrary text into the restricted alphabet used by Hill cipher."""

    hexstr = binascii.hexlify(text.encode("utf-8")).decode("ascii")
    return "".join(HILL_ALPHABET[int(ch, 16)] for ch in hexstr)


def _decode_from_hill(encoded: str) -> str:
    """Decode text that was encoded with `_encode_for_hill`."""

    hexstr = "".join(format(HILL_ALPHABET.index(c), "x") for c in encoded)
    return binascii.unhexlify(hexstr).decode("utf-8", errors="ignore")


def hill_encrypt(text, key_matrix):

    encoded = _encode_for_hill(text)
    n = len(key_matrix)
    mod = len(HILL_ALPHABET)

    while len(encoded) % n != 0:
        encoded += HILL_ALPHABET[-1]

    result = ""

    for i in range(0, len(encoded), n):
        block = encoded[i : i + n]
        vector = [HILL_ALPHABET.index(c) for c in block]

        encrypted = np.dot(key_matrix, vector) % mod
        result += "".join(HILL_ALPHABET[int(x)] for x in encrypted)

    return result


def hill_decrypt(text, key_matrix):

    mod = len(HILL_ALPHABET)
    det = int(round(np.linalg.det(key_matrix)))
    det_inv = pow(det, -1, mod)

    matrix_mod_inv = (det_inv * np.round(det * np.linalg.inv(key_matrix)).astype(int)) % mod

    n = len(key_matrix)
    result = ""

    for i in range(0, len(text), n):
        block = text[i : i + n]
        vector = [HILL_ALPHABET.index(c) for c in block]

        decrypted = np.dot(matrix_mod_inv, vector) % mod
        result += "".join(HILL_ALPHABET[int(x)] for x in decrypted)

    return _decode_from_hill(result)
