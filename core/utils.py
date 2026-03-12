import datetime
import logging
import secrets


def generate_verification_hex() -> str:
    """Genera un código de 8 caracteres en hexadecimal."""
    return secrets.token_hex(4)  # 8 hex chars


def log_rate(tasa: float, id_usuario: str, banco: str, path: str = 'logs/auditoria.log') -> None:
    """Escribe un log en texto plano con formato: [Timestamp] | [Tasa] | [ID] | [Banco]."""
    timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
    row = f"[{timestamp}] | [{tasa}] | [{id_usuario}] | [{banco}]\n"

    # Garantizar directorio existente
    from pathlib import Path
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'a', encoding='utf-8') as f:
        f.write(row)

    logging.info(row.strip())
