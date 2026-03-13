from decimal import Decimal, getcontext
from pydantic import BaseSettings


class BCBSettings(BaseSettings):
    """
    Configuración del simulador de tipo de cambio del BCB.

    - BASE_RATE: tipo de cambio base publicado (p. ej. 6.96)
    - MAX_DELTA: oscilación máxima permitida alrededor de la base (±0.9999)
    - REFRESH_SECONDS: intervalo de actualización "oficial" del tipo de cambio
      en segundos (por defecto, 3 minutos = 180s).
    - SEED: semilla opcional para obtener secuencias reproducibles en pruebas.
    """

    BASE_RATE: Decimal = Decimal("6.96")
    MAX_DELTA: Decimal = Decimal("0.9999")
    REFRESH_SECONDS: int = 180
    SEED: int | None = None

    class Config:
        env_prefix = "BCB_"
        # Permite que Pydantic lea Decimals desde strings en .env
        json_encoders = {Decimal: str}


# Configuramos la precisión global de Decimal para garantizar al menos 4 dígitos
getcontext().prec = 10

settings = BCBSettings()


def clamp_rate(rate: Decimal, base: Decimal | None = None, max_delta: Decimal | None = None) -> Decimal:
    """
    Asegura que el tipo de cambio se mantenga dentro del rango permitido:
    [BASE_RATE - MAX_DELTA, BASE_RATE + MAX_DELTA], con 4 decimales.
    """
    base = base or settings.BASE_RATE
    max_delta = max_delta or settings.MAX_DELTA

    min_rate = base - max_delta
    max_rate = base + max_delta

    if rate < min_rate:
        rate = min_rate
    elif rate > max_rate:
        rate = max_rate

    # Cuatro decimales fijos
    return rate.quantize(Decimal("0.0001"))

