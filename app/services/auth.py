"""
Auth Module Business Logic Service
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import AuthRepository
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.core.exceptions import InvalidCredentialsException, UserAlreadyExistsException, UserNotFoundException
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_jwt_token
from app.core.redis import revoke_token, is_token_revoked
from app.config import settings


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = AuthRepository(db)

    async def authenticate(self, credentials: LoginRequest) -> TokenResponse:
        user = await self.repo.get_by_username_or_email(credentials.username_or_email)
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise InvalidCredentialsException()

        if not user.is_active:
            raise InvalidCredentialsException("errors.user_account_inactive")

        claims = {
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role.value,
            "parish_id": str(user.parish_id) if user.parish_id else None,
            "deanery_id": str(user.deanery_id) if user.deanery_id else None,
        }

        fid = str(uuid.uuid4())
        access_token = create_access_token(subject=str(user.id), claims=claims, family_id=fid)
        refresh_token = create_refresh_token(subject=str(user.id), family_id=fid)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh(self, refresh_token_str: str) -> TokenResponse:
        """Rotate refresh token and issue a fresh access/refresh token pair."""
        try:
            payload = decode_jwt_token(refresh_token_str)
        except ValueError:
            raise InvalidCredentialsException("errors.invalid_refresh_token")

        if payload.get("type") != "refresh":
            raise InvalidCredentialsException("errors.invalid_token_type")

        jti = payload.get("jti")
        if jti and await is_token_revoked(str(jti)):
            raise InvalidCredentialsException("errors.refresh_token_revoked")

        fid = payload.get("fid")
        if fid and await is_token_revoked(f"family:{fid}"):
            raise InvalidCredentialsException("errors.token_family_revoked")

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise InvalidCredentialsException("errors.invalid_token_subject")

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise InvalidCredentialsException("errors.invalid_user_id_format")

        user = await self.repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise InvalidCredentialsException("errors.user_not_found_or_inactive")

        # Revoke the old refresh token jti so it cannot be reused
        if jti:
            exp = payload.get("exp")
            now_ts = int(datetime.now(timezone.utc).timestamp())
            expire_seconds = max(int(exp) - now_ts, 1) if exp else 3600
            await revoke_token(str(jti), expire_seconds)

        claims = {
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role.value,
            "parish_id": str(user.parish_id) if user.parish_id else None,
            "deanery_id": str(user.deanery_id) if user.deanery_id else None,
        }

        new_access_token = create_access_token(subject=str(user.id), claims=claims, family_id=fid)
        new_refresh_token = create_refresh_token(subject=str(user.id), family_id=fid)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def logout(self, payload: dict) -> None:
        """Revoke the current access token and its token family."""
        jti = payload.get("jti")
        exp = payload.get("exp")
        now_ts = int(datetime.now(timezone.utc).timestamp())
        expire_seconds = max(int(exp) - now_ts, 1) if (exp and int(exp) > now_ts) else 3600

        if jti:
            await revoke_token(str(jti), expire_seconds)

        fid = payload.get("fid")
        if fid:
            await revoke_token(f"family:{fid}", expire_seconds)

    async def register_user(self, data: UserCreate) -> UserResponse:
        existing = await self.repo.get_by_username_or_email(data.email)
        if existing:
            raise UserAlreadyExistsException()
        user = await self.repo.create_user(data)
        return UserResponse.model_validate(user)
