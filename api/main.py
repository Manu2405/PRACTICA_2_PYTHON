import argparse
import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from .schemas import CuentaPayload, VerificationPayload
from .utils import compute_verification_code, validate_bearer_token
from .db import fetch_accounts, list_verifications, store_verification


def create_app(bank_id: str, token: str) -> FastAPI:
    app = FastAPI(title=f"Banco {bank_id} API")

    @app.get("/accounts")
    async def get_accounts(
        limit: int = 100,
        offset: int = 0,
        parallel: bool = False,
        workers: int = 4,
        authorization: str | None = Header(default=None),
    ):
        """Return account data from this bank's database.

        The response includes a `verification_code` per account. ASFI should use
        this code to confirm receipt.
        """

        if not validate_bearer_token(authorization, token):
            raise HTTPException(status_code=401, detail="Invalid or missing authorization token")

        accounts = fetch_accounts(bank_id, limit=limit, offset=offset, parallel=parallel, workers=workers)

        return {"accounts": accounts}

    @app.post("/verify")
    async def verify(
        payload: VerificationPayload,
        authorization: str | None = Header(default=None),
    ):
        """Accept verification codes from ASFI for previously delivered accounts."""

        if not validate_bearer_token(authorization, token):
            raise HTTPException(status_code=401, detail="Invalid or missing authorization token")

        accepted = 0
        rejected = 0

        for item in payload.items:
            # Store the code for audit / tracking.
            store_verification(bank_id, item.NroCuenta, item.verification_code)
            accepted += 1

        return {"accepted": accepted, "rejected": rejected}

    @app.get("/verifications")
    async def verifications(authorization: str | None = Header(default=None)):
        if not validate_bearer_token(authorization, token):
            raise HTTPException(status_code=401, detail="Invalid or missing authorization token")

        return list_verifications(bank_id)

    @app.get("/health")
    async def health():
        return {"status": "ok", "bank_id": bank_id}

    return app


def main():
    parser = argparse.ArgumentParser(description="Run a bank API simulator")
    parser.add_argument("--bank-id", required=True, help="Bank identifier")
    parser.add_argument("--port", required=True, type=int, help="Port to serve on")
    parser.add_argument(
        "--env-file",
        default=None,
        help="Path to a .env file containing TOKEN and BANK_ID (optional)",
    )

    args = parser.parse_args()

    if args.env_file:
        load_dotenv(args.env_file)

    bank_id = args.bank_id
    token = os.getenv("TOKEN")
    env_bank_id = os.getenv("BANK_ID")

    if env_bank_id and env_bank_id != bank_id:
        raise SystemExit("BANK_ID in env file does not match --bank-id")

    if not token:
        raise SystemExit("TOKEN must be set via env or .env file")

    app = create_app(bank_id, token)

    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
