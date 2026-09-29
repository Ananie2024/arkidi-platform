import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.main import app
from app.models.enums import UserRole
from app.models.user import User


@pytest.fixture
async def test_user() -> User:
    """Create an active test user for password reset tests."""
    user = User(
        id=uuid.uuid4(),
        username="resetuser",
        email="resetuser@archidiocesekigali.org",
        hashed_password=get_password_hash("OldPassword123!"),
        full_name="Reset User",
        role=UserRole.PARISH_SECRETARY,
        is_active=True,
    )
    async with AsyncSessionLocal() as db:
        await db.execute(
            delete(User).where(
                (User.email == "resetuser@archidiocesekigali.org") | (User.username == "resetuser")
            )
        )
        await db.commit()
        db.add(user)
        await db.commit()

    try:
        yield user
    finally:
        async with AsyncSessionLocal() as db:
            await db.execute(delete(User).where(User.id == user.id))
            await db.commit()


@pytest.mark.asyncio
async def test_forgot_password_returns_success_for_existing_user(test_user: User):
    """POST /auth/forgot-password should return success for an existing active user."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/forgot-password", json={"email": "resetuser@archidiocesekigali.org"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_forgot_password_returns_success_for_unknown_email():
    """POST /api/v1/auth/forgot-password should return success even for unknown emails (no user enumeration)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/forgot-password", json={"email": "nonexistent@archidiocesekigali.org"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_reset_password_with_valid_token(test_user: User):
    """POST /api/v1/auth/reset-password should update password when token is valid."""
    from app.core.redis import set_password_reset_token

    reset_token = "test-reset-token-12345"
    await set_password_reset_token(reset_token, str(test_user.id), 3600)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "NewSecurePass456!",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_reset_password_with_invalid_token():
    """POST /api/v1/auth/reset-password should reject an invalid token."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "invalid-token",
                "new_password": "NewSecurePass456!",
            },
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_reset_password_token_is_single_use(test_user: User):
    """A reset token should be consumed after one use and cannot be reused."""
    from app.core.redis import set_password_reset_token

    reset_token = "single-use-token-12345"
    await set_password_reset_token(reset_token, str(test_user.id), 3600)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First use should succeed
        response1 = await client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "NewSecurePass456!",
            },
        )
        assert response1.status_code == 200

        # Second use should fail (token consumed)
        response2 = await client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "AnotherPass789!",
            },
        )
        assert response2.status_code == 400
