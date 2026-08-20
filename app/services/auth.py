"""
Auth Module Business Logic Service
"""
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import AuthRepository
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.core.exceptions import InvalidCredentialsException, UserAlreadyExistsException, UserNotFoundException
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.redis import revoke_token
from app.config import settings


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = AuthRepository(db)

    async def authenticate(self, credentials: LoginRequest) -> TokenResponse:
        user = await self.repo.get_by_username_or_email(credentials.username_or_email)
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise InvalidCredentialsException()

        if not user.is_active:
            raise InvalidCredentialsException("User account is inactive.")

        claims = {
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role.value,
            "parish_id": str(user.parish_id) if user.parish_id else None,
            "deanery_id": str(user.deanery_id) if user.deanery_id else None,
        }

        access_token = create_access_token(subject=str(user.id), claims=claims)
        refresh_token = create_refresh_token(subject=str(user.id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def logout(self, payload: dict) -> None:
        """Revoke the current access token by adding its ``jti`` to the blacklist.

        The blacklist entry lives exactly as long as the token itself (the time
        remaining until ``exp``) so it is automatically cleaned up by Redis TTL
        once the token could not be valid anymore.
        """
        jti = payload.get("jti")
        if not jti:
            # Nothing to revoke — token without jti (e.g. pre-fix) is not blacklistable.
            return

        exp = payload.get("exp")
        now_ts = int(datetime.now(timezone.utc).timestamp())
        if exp is None or int(exp) <= now_ts:
            # Token already expired; nothing to blacklist.
            return

        expire_seconds = int(exp) - now_ts
        await revoke_token(str(jti), expire_seconds)

    async def register_user(self, data: UserCreate) -> UserResponse:
        existing = await self.repo.get_by_username_or_email(data.email)
        if existing:
            raise UserAlreadyExistsException("A user with this email or username already exists.")
        user = await self.repo.create_user(data)
        return UserResponse.model_validate(user)
