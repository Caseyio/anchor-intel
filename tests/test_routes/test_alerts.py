# tests/test_routes/test_alerts.py

import pytest
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from httpx import ASGITransport
from main import app


@pytest.mark.asyncio
async def test_low_stock_alerts_empty():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            response = await ac.get("/alerts/low-stock?threshold=10")
            assert response.status_code == 200
            assert response.json() == []
