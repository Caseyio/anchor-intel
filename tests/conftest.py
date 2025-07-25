# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture(scope="module")
def client():
    """
    Provides a TestClient with FastAPI app using lifespan events.
    """
    with TestClient(app) as c:
        yield c
