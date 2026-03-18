import base64


def encode(data: bytes) -> str:
    return base64.b64encode(data).decode()


def decode(data: str) -> bytes:
    return base64.b64decode(data.encode())