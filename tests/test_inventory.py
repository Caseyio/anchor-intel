import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_inventory_events_requires_auth():
    response = client.get("/inventory/inventory-events")
    assert response.status_code == 403 or response.status_code == 401
