"""
Auth Module FastAPI Endpoints
"""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.limiter import limiter
from app.dependencies import get_current_user_payload, get_db, require_roles
from app.models.enums import UserRole
from app.schemas.user import (
    ForgotPasswordRequest,
    GoogleAuthRequest,
    GoogleAuthUrlResponse,
    LoginRequest,
    RefreshRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from app.services.auth import AuthService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=ApiResponse[TokenResponse])
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def login(
    request: Request,
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and issue access + refresh JWT tokens."""
    service = AuthService(db)
    tokens = await service.authenticate(credentials)
    return ApiResponse.ok(data=tokens, message="success.login_successful")


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
@limiter.limit(settings.RATE_LIMIT_REFRESH)
async def refresh_token(
    request: Request,
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Rotate refresh token and issue a fresh token pair."""
    service = AuthService(db)
    tokens = await service.refresh(body.refresh_token)
    return ApiResponse.ok(data=tokens, message="success.token_refreshed")


@router.post(
    "/register",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR])),
):
    """Register a new system user (admin only)."""
    service = AuthService(db)
    created = await service.register_user(data)
    return ApiResponse.ok(data=created, message="success.user_registered")


@router.get(
    "/me",
    response_model=ApiResponse[dict],
)
async def read_current_user(
    payload: dict = Depends(get_current_user_payload),
):
    """Return the decoded JWT payload of the currently authenticated user."""
    return ApiResponse.ok(data=payload)


@router.post(
    "/logout",
    response_model=ApiResponse[dict],
)
async def logout(
    db: AsyncSession = Depends(get_db),
    payload: dict = Depends(get_current_user_payload),
):
    """Revoke the current access token so it can no longer authenticate."""
    await AuthService(db).logout(payload)
    return ApiResponse.ok(message="success.logout_successful", data={"detail": "token revoked"})


@router.post("/forgot-password", response_model=ApiResponse[dict])
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request a one-time password-reset link.

    Always returns the same success message regardless of whether an active
    account exists for the given e-mail, to prevent user enumeration.
    """
    await AuthService(db).request_password_reset(data.email)
    return ApiResponse.ok(
        message="success.password_reset_requested",
        data={
            "detail": "If an account exists for this email, a password reset link has been sent."
        },
    )


@router.post("/reset-password", response_model=ApiResponse[dict])
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Consume a one-time reset token and update the user's password."""
    await AuthService(db).reset_password(data.token, data.new_password)
    return ApiResponse.ok(
        message="success.password_reset_completed", data={"detail": "Password reset successfully"}
    )


# ==========================================================================
# Google OAuth 2.0 Endpoints
# ==========================================================================


@router.get("/google/url", response_model=ApiResponse[GoogleAuthUrlResponse])
@limiter.limit(settings.RATE_LIMIT_GOOGLE_AUTH)
async def get_google_auth_url(
    request: Request,
    redirect_uri: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Return the Google OAuth 2.0 authorization URL for the frontend to redirect to.

    The frontend should redirect the user to the returned URL. After the user
    consents, Google will redirect back to the backend with an authorization code.
    """
    service = AuthService(db)
    result = await service.get_google_authorization_url(redirect_uri)
    return ApiResponse.ok(data=result, message="success.google_auth_url_generated")


@router.post("/google/login", response_model=ApiResponse[TokenResponse])
@limiter.limit(settings.RATE_LIMIT_GOOGLE_AUTH)
async def google_login(
    request: Request,
    data: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate a user via Google OAuth.

    Supports two flows:
    1. Authorization code flow — pass `code` (and optionally `redirect_uri`)
    2. ID token flow — pass `credential` (from Google One-Tap / GIS button)

    Returns the same JWT token pair as the standard login endpoint.
    """
    service = AuthService(db)
    tokens = await service.google_authenticate(data)
    return ApiResponse.ok(data=tokens, message="success.login_successful")
