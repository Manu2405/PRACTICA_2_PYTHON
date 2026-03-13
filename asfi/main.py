from fastapi import FastAPI

from asfi.config import settings
from asfi.database import init_db, close_db
from asfi.api.routes import router as asfi_router


app = FastAPI(
    title="ASFI Central API",
    version="1.0.0",
    description="API central de ASFI para registro de conversiones USD→Bs.",
)


@app.on_event("startup")
async def startup() -> None:
    await init_db(settings.ASFI_DB_DSN)


@app.on_event("shutdown")
async def shutdown() -> None:
    await close_db()


@app.get("/health", tags=["ASFI"])
async def health_check():
    return {"status": "ok"}


app.include_router(asfi_router, prefix="/asfi", tags=["ASFI"])

