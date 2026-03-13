from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Configuración de la API central de ASFI.

    - ASFI_DB_DSN: cadena de conexión a PostgreSQL (db_asfi)
    - BCB_BASE_URL: URL base del simulador BCB
    - PRECISION_DECIMALES: número de decimales para conversiones
    """

    ASFI_DB_DSN: str = "postgresql://postgres:admin123@localhost:5432/db_asfi"
    BCB_BASE_URL: str = "http://localhost:8000"
    PRECISION_DECIMALES: int = 4

    class Config:
        env_file = ".env"


settings = Settings()

