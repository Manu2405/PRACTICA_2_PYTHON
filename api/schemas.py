from typing import List, Optional, Union

from pydantic import BaseModel


class CuentaPayload(BaseModel):
    Nro: str
    Identificacion: str
    Nombres: str
    Apellidos: str
    NroCuenta: str
    IdBanco: str
    SaldoBs: Optional[str] = None
    SaldoUSD: Optional[str] = None


class VerificationItem(BaseModel):
    NroCuenta: Union[str, int]
    verification_code: str


class VerificationPayload(BaseModel):
    items: List[VerificationItem]
