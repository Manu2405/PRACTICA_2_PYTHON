from datetime import datetime, timezone
from decimal import Decimal
import random

from fastapi import FastAPI

from config import settings, clamp_rate

app = FastAPI(
    title="BCB Simulator",
    version="1.0.0",
    description=(
        "Simulador del tipo de cambio oficial/referencial del Banco Central de Bolivia "
        "con oscilación controlada ±0.9999 sobre una tasa base."
    ),
)


if settings.SEED is not None:
    random.seed(settings.SEED)


def generate_rate(previous_rate: Decimal | None = None) -> Decimal:
    """
    Genera un nuevo tipo de cambio a partir de la tasa base o de una tasa previa.

    La variación es pseudoaleatoria pero siempre se mantiene dentro de:
    [BASE_RATE - MAX_DELTA, BASE_RATE + MAX_DELTA]
    y con precisión de 4 decimales usando Decimal.
    """
    base = settings.BASE_RATE

    # Si tenemos una tasa previa, hacemos una pequeña variación alrededor de ella.
    ref = previous_rate or base

    # Variación en el rango [-MAX_DELTA, +MAX_DELTA]
    delta_float = random.uniform(float(-settings.MAX_DELTA), float(settings.MAX_DELTA))
    raw_rate = ref + Decimal(str(delta_float))

    return clamp_rate(raw_rate, base=base, max_delta=settings.MAX_DELTA)


_current_rate: Decimal | None = None
_last_update: datetime | None = None


def _maybe_refresh_rate() -> None:
    """
    Actualiza la tasa si ha pasado más del intervalo de refresco.
    """
    global _current_rate, _last_update

    now = datetime.now(timezone.utc)

    if _current_rate is None or _last_update is None:
        _current_rate = generate_rate()
        _last_update = now
        return

    elapsed = (now - _last_update).total_seconds()
    if elapsed >= settings.REFRESH_SECONDS:
        _current_rate = generate_rate(previous_rate=_current_rate)
        _last_update = now


@app.get("/rate")
def get_rate():
    """
    Endpoint principal del simulador BCB.

    Devuelve:
    - rate: tipo de cambio actual (Decimal serializado como string)
    - base_rate: tasa base configurada
    - max_delta: oscilación máxima configurada
    - refreshed_at: timestamp UTC de la última actualización
    - refresh_seconds: intervalo de refresco configurado
    """
    _maybe_refresh_rate()

    assert _current_rate is not None
    assert _last_update is not None

    return {
        "rate": str(_current_rate),
        "base_rate": str(settings.BASE_RATE),
        "max_delta": str(settings.MAX_DELTA),
        "refreshed_at": _last_update.isoformat(),
        "refresh_seconds": settings.REFRESH_SECONDS,
    }

