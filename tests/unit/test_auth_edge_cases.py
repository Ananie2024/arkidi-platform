"""
Unit tests for Auth edge cases and RBAC dependencies:
- Token type enforcement (reject refresh tokens on protected routes)
- Role claims validation & malformed role handling (no unhandled ValueError)
- Registration duplicate username pre-check and IntegrityError handling
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import PermissionDeniedException, UserAlreadyExistsException
from app.core.security import create_access_token, create_refresh_token
from app.dependencies import get_current_user_payload, require_roles
from app.models.enums import UserRole
from app.schemas.user import UserCreate
from app.services.auth import AuthService


@pytest.mark.asyncio
async def test_get_current_user_payload_rejects_refresh_token():
    """Ensure refresh tokens cannot be used as bearer access tokens."""
    refresh_token = create_refresh_token(subject=str(uuid.uuid4()))
    with patch("app.dependencies.is_token_revoked", new_callable=AsyncMock, return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_payload(token=refresh_token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "errors.invalid_token_type"


@pytest.mark.asyncio
async def test_get_current_user_payload_accepts_valid_access_token():
    """Ensure valid access tokens are accepted and decoded."""
    user_id = str(uuid.uuid4())
    access_token = create_access_token(
        subject=user_id,
        claims={"role": UserRole.PARISH_SECRETARY.value, "username": "secr"},
    )
    with patch("app.dependencies.is_token_revoked", new_callable=AsyncMock, return_value=False):
        payload = await get_current_user_payload(token=access_token)

    assert payload["sub"] == user_id
    assert payload["type"] == "access"
    assert payload["role"] == UserRole.PARISH_SECRETARY.value


@pytest.mark.asyncio
async def test_require_roles_rejects_malformed_role_without_500():
    """Ensure malformed/unknown role strings fail cleanly with PermissionDeniedException (403), not ValueError (500)."""
    checker = require_roles([UserRole.CHANCELLOR, UserRole.SUPER_ADMIN])
    malformed_payload = {"sub": str(uuid.uuid4()), "role": "NOT_A_REAL_ROLE"}

    with pytest.raises(PermissionDeniedException) as exc_info:
        await checker(payload=malformed_payload)

    assert exc_info.value.status_code == 403
    assert exc_info.value.message_key == "errors.access_forbidden_roles"


@pytest.mark.asyncio
async def test_require_roles_rejects_missing_role():
    """Ensure None or empty role claim is rejected cleanly with PermissionDeniedException."""
    checker = require_roles([UserRole.CHANCELLOR])
    payload = {"sub": str(uuid.uuid4())}

    with pytest.raises(PermissionDeniedException) as exc_info:
        await checker(payload=payload)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_require_roles_allows_matching_role():
    """Ensure valid and sufficient role is allowed through."""
    checker = require_roles([UserRole.CHANCELLOR])
    payload = {"sub": str(uuid.uuid4()), "role": UserRole.CHANCELLOR.value}

    result = await checker(payload=payload)
    assert result == payload


@pytest.mark.asyncio
async def test_auth_service_register_checks_duplicate_username():
    """Ensure registration rejects a duplicate username even if the email is new."""
    mock_db = MagicMock()
    mock_db.rollback = AsyncMock()
    service = AuthService(mock_db)

    user_data = UserCreate(
        email="new_email@archidiocesekigali.org",
        username="existing_username",
        password="SecurePassword123!",
        full_name="Duplicate User",
        role=UserRole.PARISH_SECRETARY,
    )

    # Email lookup returns None, but username lookup returns an existing user
    async def mock_get_by_username_or_email(identifier: str):
        if identifier == user_data.username:
            return MagicMock(id=uuid.uuid4(), username="existing_username")
        return None

    service.repo.get_by_username_or_email = mock_get_by_username_or_email
    service.repo.create_user = AsyncMock()

    with pytest.raises(UserAlreadyExistsException):
        await service.register_user(user_data)

    service.repo.create_user.assert_not_called()


@pytest.mark.asyncio
async def test_auth_service_register_catches_integrity_error():
    """Ensure unexpected IntegrityError during insert triggers rollback and UserAlreadyExistsException."""
    mock_db = MagicMock()
    mock_db.rollback = AsyncMock()
    service = AuthService(mock_db)

    user_data = UserCreate(
        email="unique@archidiocesekigali.org",
        username="unique_user",
        password="SecurePassword123!",
        full_name="Integrity User",
        role=UserRole.PARISH_SECRETARY,
    )

    service.repo.get_by_username_or_email = AsyncMock(return_value=None)
    service.repo.create_user = AsyncMock(
        side_effect=IntegrityError("duplicate key", params=None, orig=Exception())
    )

    with pytest.raises(UserAlreadyExistsException):
        await service.register_user(user_data)

    mock_db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_rate_limiter_blocks_excessive_requests():
    """Ensure slowapi limits requests and returns HTTP 429 with standard JSON response."""
    from fastapi import FastAPI, Request
    from httpx import ASGITransport, AsyncClient
    from slowapi import Limiter
    from slowapi.middleware import SlowAPIMiddleware
    from slowapi.util import get_remote_address

    from app.core.exceptions import setup_exception_handlers

    test_limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")
    test_app = FastAPI()
    test_app.state.limiter = test_limiter
    test_app.add_middleware(SlowAPIMiddleware)
    setup_exception_handlers(test_app)

    @test_app.post("/test-limit")
    @test_limiter.limit("2/minute")
    async def rate_limited_endpoint(request: Request):
        return {"success": True}

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r1 = await ac.post("/test-limit")
        assert r1.status_code == 200
        r2 = await ac.post("/test-limit")
        assert r2.status_code == 200
        r3 = await ac.post("/test-limit")
        assert r3.status_code == 429
        body = r3.json()
        assert body["success"] is False
        assert body["error"]["type"] == "RateLimitExceeded"
        assert "Too many requests" in body["error"]["message"]
