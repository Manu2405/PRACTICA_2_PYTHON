from decimal import Decimal
from pydantic import BaseModel, Field


class BCBRateResponse(BaseModel):
    """
    Esquema de la respuesta del simulador BCB.
    """

    rate: Decimal = Field(..., description="Tipo de cambio actual USD→Bs con 4 decimales.")
    base_rate: Decimal = Field(..., description="Tasa base configurada en el simulador.")
    max_delta: Decimal = Field(..., description="Oscilación máxima permitida alrededor de la base.")
    refreshed_at: str = Field(..., description="Timestamp ISO8601 de la última actualización.")
    refresh_seconds: int = Field(..., description="Intervalo de refresco en segundos.")

