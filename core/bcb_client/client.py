from decimal import Decimal
from typing import Optional

import httpx
from pydantic import BaseSettings

from core.bcb_client.schemas import BCBRateResponse


class BCBClientSettings(BaseSettings):
    """
    Configuración del cliente HTTP hacia el simulador BCB.

    - BCB_BASE_URL: URL base del simulador (ej. http://bcb-simulator:8000)
    - BCB_TIMEOUT_SECONDS: timeout en segundos para la petición HTTP.
    """

    BCB_BASE_URL: str = "http://bcb-simulator:8000"
    BCB_TIMEOUT_SECONDS: int = 5

    class Config:
        env_prefix = ""


settings = BCBClientSettings()


async def fetch_current_rate(client: Optional[httpx.AsyncClient] = None) -> Decimal:
    """
    Consulta el tipo de cambio actual al simulador BCB.

    Devuelve un Decimal con 4 decimales listo para usar en la conversión
    USD→Bs. Lanza httpx.HTTPError si hay problemas de comunicación.
    """
    owns_client = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=settings.BCB_TIMEOUT_SECONDS)

    try:
        response = await client.get(f"{settings.BCB_BASE_URL}/rate")
        response.raise_for_status()

        # Con pydantic v1 usamos parse_obj en lugar de model_validate
        data = BCBRateResponse.parse_obj(response.json())
        # Aseguramos 4 decimales
        return data.rate.quantize(Decimal("0.0001"))
    finally:
        if owns_client:
            await client.aclose()

