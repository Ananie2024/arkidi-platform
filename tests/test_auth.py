"""
Auth Endpoint Tests
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "nonexistent@archidiocesekigali.org", "password": "wrongpassword123"},
    )
    assert response.status_code == 401
