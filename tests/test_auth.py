"""
Auth Endpoint Tests
"""
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import delete

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.enums import UserRole
from app.models.user import User


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "nonexistent@archidiocesekigali.org", "password": "wrongpassword123"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_access_token(client: AsyncClient):
    """A token used after logout is rejected; it keeps working before logout."""
    password = "test-logout-password-123"
    username = f"logout_{uuid.uuid4().hex[:8]}"

    created_user_id = None
    try:
        # Create a throwaway active user so login succeeds.
        async with AsyncSessionLocal() as db:
            user = User(
                email=f"{username}@arkidi.test",
                username=username,
                hashed_password=get_password_hash(password),
                full_name="Logout Test User",
                role=UserRole.PARISH_SECRETARY,
                is_active=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            created_user_id = user.id

        # 1. Log in and capture the access token.
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username_or_email": username, "password": password},
        )
        assert login_resp.status_code == 200, login_resp.text
        access_token = login_resp.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # 2. The token works normally before logout.
        me_before = await client.get("/api/v1/auth/me", headers=headers)
        assert me_before.status_code == 200

        # 3. Logout revokes the current token.
        logout_resp = await client.post("/api/v1/auth/logout", headers=headers)
        assert logout_resp.status_code == 200, logout_resp.text

        # 4. The same token must now be rejected.
        me_after = await client.get("/api/v1/auth/me", headers=headers)
        assert me_after.status_code == 401
    finally:
        if created_user_id is not None:
            async with AsyncSessionLocal() as db:
                await db.execute(delete(User).where(User.id == created_user_id))
                await db.commit()
