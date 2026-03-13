
import asyncio
from decimal import Decimal

import httpx

from core.bcb_client.client import fetch_current_rate, settings as client_settings


async def _mock_server_rate():
    async def handler(request):
        return httpx.Response(
            200,
            json={
                "rate": "7.1234",
                "base_rate": "6.9600",
                "max_delta": "0.9999",
                "refreshed_at": "2026-03-12T00:00:00Z",
                "refresh_seconds": 180,
            },
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="http://mock-bcb") as client:
        # Parche temporal de la URL base del cliente
        original_url = client_settings.BCB_BASE_URL
        client_settings.BCB_BASE_URL = "http://mock-bcb"
        try:
            rate = await fetch_current_rate(client=client)
            assert isinstance(rate, Decimal)
            assert rate == Decimal("7.1234")
        finally:
            client_settings.BCB_BASE_URL = original_url


def test_fetch_current_rate_with_mock():
    asyncio.run(_mock_server_rate())
