"""
Pytest Test Fixtures and Application Setup
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.fixture
async def client():
    """Async test HTTP client fixture."""
    async with AsyncClient(app=app, base_url="http://testserver") as c:
        yield c
