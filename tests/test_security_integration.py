"""Integration tests for the hardened auth/token lifecycle (requires a live
Postgres + Redis, mirroring development/production wiring).

Covers:
- login → access token works on /auth/me
- refresh rotation issues a fresh pair and revokes the old refresh token
- logout revokes the whole token family (access + refresh)
- reusing a rotated/revoked refresh token is rejected
- /health exposes database + redis probes
"""
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import delete

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.enums import UserRole
from app.models.user import User


async def _create_user() -> tuple[str, str, uuid.UUID | None]:
    """Create a throwaway active user and return (username, password, id)."""
    password = f"test-sec-{uuid.uuid4().hex[:10]}"
    username = f"sec_{uuid.uuid4().hex[:8]}"
    user_id = None
    async with AsyncSessionLocal() as db:
        user = User(
            email=f"{username}@arkidi.test",
            username=username,
            hashed_password=get_password_hash(password),
            full_name="Security Test User",
            role=UserRole.PARISH_SECRETARY,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        user_id = user.id
    return username, password, user_id


async def _cleanup(user_id: uuid.UUID | None) -> None:
    if user_id is None:
        return
    async with AsyncSessionLocal() as db:
        await db.execute(delete(User).where(User.id == user_id))
        await db.commit()


async def _login(client: AsyncClient, username: str, password: str) -> dict:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username_or_email": username, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


@pytest.mark.asyncio
async def test_refresh_rotates_and_revokes_old_refresh_token(client: AsyncClient):
    username, password, uid = await _create_user()
    try:
        tokens = await _login(client, username, password)
        old_access, old_refresh = tokens["access_token"], tokens["refresh_token"]

        # Access token works before refresh.
        me = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {old_access}"}
        )
        assert me.status_code == 200

        # Refresh rotates into a fresh pair.
        refreshed = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": old_refresh}
        )
        assert refreshed.status_code == 200, refreshed.text
        new_tokens = refreshed.json()["data"]
        assert new_tokens["access_token"] != old_access
        assert new_tokens["refresh_token"] != old_refresh

        # Old access token is unaffected (still valid) but the old *refresh*
        # token is now consumed -> rejected.
        reused = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": old_refresh}
        )
        assert reused.status_code == 401

        # New access token works.
        me_new = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {new_tokens['access_token']}"},
        )
        assert me_new.status_code == 200
    finally:
        await _cleanup(uid)


@pytest.mark.asyncio
async def test_logout_revokes_access_and_refresh_family(client: AsyncClient):
    username, password, uid = await _create_user()
    try:
        tokens = await _login(client, username, password)
        access, refresh = tokens["access_token"], tokens["refresh_token"]
        headers = {"Authorization": f"Bearer {access}"}

        assert (await client.get("/api/v1/auth/me", headers=headers)).status_code == 200

        logout = await client.post("/api/v1/auth/logout", headers=headers)
        assert logout.status_code == 200, logout.text

        # Access token is now rejected.
        assert (await client.get("/api/v1/auth/me", headers=headers)).status_code == 401

        # The linked refresh family is revoked too (token family revocation).
        refres = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
        assert refres.status_code == 401
    finally:
        await _cleanup(uid)


@pytest.mark.asyncio
async def test_health_exposes_dependency_probes(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["checks"]["database"] in {"up", "down"}
    assert data["checks"]["redis"] in {"up", "down"}
    assert data["status"] in {"healthy", "degraded"}