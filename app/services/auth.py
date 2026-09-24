"""
Auth Module Business Logic Service
"""

import secrets
import uuid
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import (
    GoogleAccountNotLinkedException,
    GoogleAuthException,
    InvalidCredentialsException,
    InvalidResetTokenException,
    UserAlreadyExistsException,
)
from app.core.redis import (
    consume_password_reset_token,
    is_token_revoked,
    revoke_token,
    set_password_reset_token,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_jwt_token,
    get_password_hash,
    verify_password,
)
from app.models.enums import UserRole
from app.repositories.user import AuthRepository
from app.schemas.user import (
    GoogleAuthRequest,
    GoogleAuthUrlResponse,
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from app.services.google_auth import GoogleAuthService
from app.utils.alerts import send_email_message


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

    async def get_google_authorization_url(
        self, redirect_uri: str | None = None
    ) -> GoogleAuthUrlResponse:
        """Get the Google OAuth 2.0 authorization URL for the frontend to redirect to."""
        google_service = GoogleAuthService()
        return google_service.get_authorization_url(redirect_uri)

    async def google_authenticate(self, data: GoogleAuthRequest) -> TokenResponse:
        """Authenticate (or optionally self-register) a user via Google OAuth.

        Supports two flows:
        1. Authorization code flow (code + redirect_uri) — from server-side OAuth redirect.
        2. ID token flow (credential) — from Google One-Tap / GIS button on the frontend.
        """
        google_service = GoogleAuthService()

        # Verify the Google token and extract the user profile
        if data.code:
            profile = await google_service.exchange_code(data.code, data.redirect_uri)
        elif data.credential:
            profile = await google_service.verify_id_token(data.credential)
        else:
            raise GoogleAuthException(
                "Either 'code' or 'credential' must be provided.",
                message_key="errors.google_auth_failed",
            )

        email = profile.get("email", "").lower().strip()
        if not email:
            raise GoogleAuthException(
                "Google account did not return an email address.",
                message_key="errors.google_auth_failed",
            )

        # Look up the user by email
        user = await self.repo.get_by_email(email)

        if not user:
            if settings.GOOGLE_ALLOW_SELF_REGISTRATION:
                # Self-register a new user with info from Google profile
                from app.schemas.user import UserCreate

                full_name = profile.get("name") or email.split("@")[0]
                username = email.split("@")[0]

                # Ensure username uniqueness by appending a suffix if needed
                base_username = username
                counter = 1
                while await self.repo.get_by_username_or_email(username):
                    username = f"{base_username}{counter}"
                    counter += 1

                user_create = UserCreate(
                    email=email,
                    username=username,
                    full_name=full_name,
                    password=secrets.token_urlsafe(32),  # Random password — user logs in via Google
                    role=UserRole.PARISH_SECRETARY,  # Default role for self-registered users
                )
                try:
                    user = await self.repo.create_user(user_create)
                except IntegrityError:
                    await self.repo.db.rollback()
                    raise GoogleAuthException(
                        "Failed to create account from Google profile.",
                        message_key="errors.google_auth_failed",
                    )
            else:
                raise GoogleAccountNotLinkedException(email=email)

        if not user.is_active:
            raise InvalidCredentialsException("errors.user_account_inactive")

        # Update last login timestamp
        await self.repo.update_last_login(user.id)

        # Issue JWT tokens
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
            now_ts = int(datetime.now(UTC).timestamp())
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
        now_ts = int(datetime.now(UTC).timestamp())
        expire_seconds = max(int(exp) - now_ts, 1) if (exp and int(exp) > now_ts) else 3600

        if jti:
            await revoke_token(str(jti), expire_seconds)

        fid = payload.get("fid")
        if fid:
            await revoke_token(f"family:{fid}", expire_seconds)

    async def register_user(self, data: UserCreate) -> UserResponse:
        existing_email = await self.repo.get_by_username_or_email(data.email)
        if existing_email:
            raise UserAlreadyExistsException()
        existing_username = await self.repo.get_by_username_or_email(data.username)
        if existing_username:
            raise UserAlreadyExistsException()
        try:
            user = await self.repo.create_user(data)
            return UserResponse.model_validate(user)
        except IntegrityError:
            await self.repo.db.rollback()
            raise UserAlreadyExistsException()

    async def request_password_reset(self, email: str) -> None:
        """Generate a one-time password-reset token and e-mail it to the user.

        The same success response is returned whether or not an active user
        exists for the given e-mail, to prevent user-enumeration attacks.
        """
        user = await self.repo.get_by_email(email)
        if user and user.is_active:
            reset_token = secrets.token_urlsafe(32)
            ttl_seconds = settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES * 60
            await set_password_reset_token(reset_token, str(user.id), ttl_seconds)

            reset_url = f"{settings.PUBLIC_FRONTEND_URL}/reset-password?token={reset_token}"
            send_email_message(
                to=user.email,
                subject="Arkidi Platform — Password Reset Request",
                body=(
                    "You requested a password reset for your Arkidi Platform account.\n\n"
                    f"Click the link below to reset your password (valid for "
                    f"{settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes):\n\n"
                    f"{reset_url}\n\n"
                    "If you did not request this, please ignore this e-mail."
                ),
            )

    async def reset_password(self, token: str, new_password: str) -> None:
        """Consume a one-time reset token and update the user's password.

        Raises ``InvalidResetTokenException`` when the token is unknown, expired,
        already consumed, or the target user no longer exists/is inactive.
        """
        user_id_str = await consume_password_reset_token(token)
        if not user_id_str:
            raise InvalidResetTokenException()

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise InvalidResetTokenException()

        user = await self.repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise InvalidResetTokenException()

        await self.repo.update_password(user_id, get_password_hash(new_password))
