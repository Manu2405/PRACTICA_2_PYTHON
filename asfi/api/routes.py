from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import secrets

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from asfi.config import settings
from asfi.database import get_pool
from core.bcb_client.client import fetch_current_rate, settings as bcb_client_settings


# Sincronizamos la URL base del cliente BCB con la config de ASFI
bcb_client_settings.BCB_BASE_URL = settings.BCB_BASE_URL


router = APIRouter()


class CuentaEntrada(BaseModel):
    banco_id: int = Field(..., description="Identificador del banco origen (1,3,10,11).")
    cuenta_id_externa: int = Field(..., description="ID de la cuenta en el banco origen.")
    identificacion: str = Field(..., description="Identificación del cliente ya descifrada.")
    nro_cuenta: str = Field(..., description="Número de cuenta origen.")
    saldo_usd: Decimal = Field(..., description="Saldo original en USD.")


class ConversionResponse(BaseModel):
    banco_id: int
    cuenta_id_externa: int
    saldo_usd: Decimal
    tipo_cambio: Decimal
    saldo_bs: Decimal
    codigo_verificacion: str
    timestamp: datetime


def _quantize(value: Decimal) -> Decimal:
    """
    Aplica la precisión configurada para los decimales.
    """
    fmt = "0." + "0" * settings.PRECISION_DECIMALES
    return value.quantize(Decimal(fmt), rounding=ROUND_HALF_UP)


def _generate_verification_code() -> str:
    """
    Genera un código de verificación hexadecimal de 8 caracteres.
    """
    return secrets.token_hex(4).upper()


@router.post("/conversion", response_model=ConversionResponse)
async def registrar_conversion(entrada: CuentaEntrada) -> ConversionResponse:
    """
    Registra en la base de ASFI una conversión USD→Bs para una cuenta de un banco.

    Flujo:
    - Consulta el tipo de cambio actual al simulador BCB.
    - Calcula saldo_bs con precisión definida.
    - Inserta en cuentas_origen, conversiones y auditoria.
    - Devuelve los datos de la conversión y el código de verificación.
    """
    # Tipo de cambio dinámico desde el simulador BCB
    tipo_cambio = await fetch_current_rate()
    tipo_cambio = _quantize(tipo_cambio)

    saldo_usd_q = _quantize(entrada.saldo_usd)
    saldo_bs = _quantize(saldo_usd_q * tipo_cambio)

    codigo_verificacion = _generate_verification_code()
    # Usamos datetime sin zona horaria porque en PostgreSQL la columna es TIMESTAMP (sin time zone)
    ahora = datetime.utcnow()

    pool = get_pool()
    async with pool.acquire() as conn:
        tx = conn.transaction()
        await tx.start()
        try:
            # 1) Registrar en cuentas_origen
            origen_id = await conn.fetchval(
                """
                INSERT INTO cuentas_origen (
                    banco_id,
                    cuenta_id_externa,
                    identificacion_descifrada,
                    nro_cuenta,
                    saldo_usd,
                    fecha_recepcion
                )
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING origen_id;
                """,
                entrada.banco_id,
                entrada.cuenta_id_externa,
                entrada.identificacion,
                entrada.nro_cuenta,
                saldo_usd_q,
                ahora,
            )

            # 2) Registrar conversión
            conversion_id = await conn.fetchval(
                """
                INSERT INTO conversiones (
                    origen_id,
                    tipo_cambio,
                    saldo_bs,
                    fecha_conversion,
                    codigo_verificacion
                )
                VALUES ($1, $2, $3, $4, $5)
                RETURNING conversion_id;
                """,
                origen_id,
                tipo_cambio,
                saldo_bs,
                ahora,
                codigo_verificacion,
            )

            # 3) Auditoría básica
            hash_integridad = None  # Se puede calcular más adelante
            await conn.execute(
                """
                INSERT INTO auditoria (
                    banco_id,
                    cuenta_id_externa,
                    tipo_cambio_aplicado,
                    hash_integridad,
                    resultado
                )
                VALUES ($1, $2, $3, $4, $5);
                """,
                entrada.banco_id,
                entrada.cuenta_id_externa,
                tipo_cambio,
                hash_integridad,
                f"CONVERSION_OK:{conversion_id}",
            )

            await tx.commit()
        except Exception as exc:  # pragma: no cover - logging pendiente
            await tx.rollback()
            raise HTTPException(status_code=500, detail=f"Error registrando conversión en ASFI: {exc}") from exc

    return ConversionResponse(
        banco_id=entrada.banco_id,
        cuenta_id_externa=entrada.cuenta_id_externa,
        saldo_usd=saldo_usd_q,
        tipo_cambio=tipo_cambio,
        saldo_bs=saldo_bs,
        codigo_verificacion=codigo_verificacion,
        timestamp=ahora,
    )

