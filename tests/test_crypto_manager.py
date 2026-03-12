from core.crypto_manager import decrypt_bank_payload


def test_decrypt_bank_payload_default():
    text = decrypt_bank_payload('bank_a', 'abc123', key='0102030405060708')
    assert isinstance(text, str)


def test_decrypt_bank_payload_atbash():
    text = decrypt_bank_payload('bank_h', 'ABC', key='dummy')
    assert text == 'ZYX'


def test_decrypt_bank_payload_caesar():
    text = decrypt_bank_payload('bank_union', 'khoor', key='3')
    assert text == 'hello'


def test_decrypt_bank_payload_vigenere():
    text = decrypt_bank_payload('bank_bnb', 'Rijvs', key='key')
    assert text == 'hello'


def test_decrypt_bank_payload_playfair_stub():
    text = decrypt_bank_payload('bank_bcp', 'ABCD', key='unused')
    assert text == 'BADC'


def test_decrypt_bank_payload_hill_stub():
    text = decrypt_bank_payload('bank_bisa', 'def', key='unused')
    assert text == 'abc'


def test_decrypt_bank_payload_des_roundtrip():
    from Crypto.Cipher import DES
    key = b'12345678'
    cipher = DES.new(key, DES.MODE_CBC, iv=key)
    msg = b'test1234test1234'
    ct = cipher.encrypt(msg)
    cthex = ct.hex()
    decrypted = decrypt_bank_payload('bank_ganadero', cthex, key.decode('utf-8'))
    assert 'test1234' in decrypted


def test_decrypt_bank_payload_aes_roundtrip():
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    key = b'0123456789abcdef0123456789abcdef'
    cipher = AES.new(key, AES.MODE_CBC, iv=key[:16])
    msg = pad(b'test of aes', AES.block_size)
    ct = cipher.encrypt(msg)
    decrypted = decrypt_bank_payload('bank_fortaleza', ct.hex(), key.decode('utf-8'))
    assert 'test of aes' in decrypted

