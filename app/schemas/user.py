"""
Auth Module Pydantic v2 Schemas
"""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from app.models.enums import UserRole


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    """Request body for the public refresh-token rotation endpoint."""
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Request body for requesting a password-reset link (public endpoint)."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request body for consuming a one-time password-reset token."""
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def _password_min_length(cls, value: str) -> str:
        if len(value) < 10:
            raise ValueError("New password must be at least 10 characters long.")
        return value


class GoogleAuthRequest(BaseModel):
    """Request body for Google OAuth authentication (code exchange or ID token verification)."""
    code: Optional[str] = None
    credential: Optional[str] = None
    redirect_uri: Optional[str] = None
    state: Optional[str] = None


class GoogleAuthUrlResponse(BaseModel):
    """Response containing the Google OAuth authorization URL."""
    url: str
    state: str


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    phone_number: Optional[str] = None
    role: UserRole = UserRole.PARISH_SECRETARY
    parish_id: Optional[uuid.UUID] = None
    deanery_id: Optional[uuid.UUID] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    parish_id: Optional[uuid.UUID] = None
    deanery_id: Optional[uuid.UUID] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None