"""
FastAPI Route Dependencies (Database Session, Current User, Role Authorization)
"""
from typing import AsyncGenerator, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.exceptions import PermissionDeniedException
from app.core.security import decode_jwt_token
from app.core.redis import is_token_revoked
from app.models.enums import UserRole, has_role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user_payload(token: str = Depends(oauth2_scheme)) -> dict:
    """Extract and validate the active user claims from JWT bearer token."""
    try:
        payload = decode_jwt_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    jti = payload.get("jti")
    if jti and await is_token_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="errors.token_revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    fid = payload.get("fid")
    if fid and await is_token_revoked(f"family:{fid}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="errors.token_family_revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def require_roles(allowed_roles: List[UserRole]):
    """Enforce role-based access control dependency on endpoints."""
    async def role_checker(payload: dict = Depends(get_current_user_payload)) -> dict:
        user_role = payload.get("role")
        if not user_role or not has_role(UserRole(user_role), allowed_roles):
            roles_str = ", ".join(r.value for r in allowed_roles)
            raise PermissionDeniedException(
                f"Access forbidden. Required roles: {roles_str}",
                message_key="errors.access_forbidden_roles",
                message_params={"roles": roles_str},
            )
        return payload
    return role_checker
