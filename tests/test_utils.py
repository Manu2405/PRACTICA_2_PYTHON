from core.utils import generate_verification_hex, log_rate
import os

def test_generate_verification_hex_length():
    code = generate_verification_hex()
    assert len(code) == 8


def test_log_rate_writes_file(tmp_path):
    log_file = tmp_path / 'auditoria.log'
    log_rate(1.05, 'ID45', 'Banco Test', path=str(log_file))
    assert log_file.exists()
    content = log_file.read_text(encoding='utf-8')
    assert 'ID45' in content and 'Banco Test' in content


def test_log_rate_writes_prueba_log(tmp_path):
    test_file = tmp_path / 'prueba.log'
    log_rate(2.00, 'ID_PRUEBA', 'Banco Prueba', path=str(test_file))
    assert test_file.exists()
    assert 'Banco Prueba' in test_file.read_text(encoding='utf-8')
