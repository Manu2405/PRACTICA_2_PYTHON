import hashlib
import hmac
from typing import Optional


def compute_verification_code(payload: dict, secret: str) -> str:
    """Compute a deterministic code for a payload using an HMAC-SHA256.

    This serves as the "verification code" that the API returns to confirm it
    received the data.
    """

    # Use a stable serialization order
    items = sorted(payload.items())
    message = "|".join(f"{k}={v}" for k, v in items)

    digest = hmac.new(secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256)
    return digest.hexdigest()


def validate_bearer_token(auth_header: Optional[str], expected_token: str) -> bool:
    if not auth_header:
        return False
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return False
    return hmac.compare_digest(parts[1], expected_token)
