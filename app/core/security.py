"""
Security & Cryptography Module
JWT token creation, validation, and Argon2 password hashing
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import uuid
import jwt
from passlib.context import CryptContext

from app.config import settings

# Password hashing context with Argon2 as primary scheme, bcrypt as fallback
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__memory_cost=65536,
    argon2__time_cost=3,
    argon2__parallelism=4,
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against an Argon2/bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a secure Argon2 hash from a plain password."""
    return pwd_context.hash(password)


def create_access_token(
    subject: str | Any,
    claims: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generate a signed JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": "access",
        # Unique token ID so the Redis-backed revocation blacklist can target it.
        "jti": str(uuid.uuid4()),
    }
    if claims:
        to_encode.update(claims)

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(
    subject: str | Any,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generate a signed JWT refresh token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": "refresh",
        # Unique token ID so the Redis-backed blacklist can revoke this token too.
        "jti": str(uuid.uuid4()),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_jwt_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token against the application SECRET_KEY."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.PyJWTError as e:
        raise ValueError(f"Invalid or expired JWT token: {str(e)}")
