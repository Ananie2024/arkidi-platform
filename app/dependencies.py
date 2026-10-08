"""
FastAPI Route Dependencies (Database Session, Current User, Role Authorization)
"""

import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.exceptions import PermissionDeniedException
from app.core.redis import is_token_revoked
from app.core.security import decode_jwt_token
from app.models.enums import UserRole, has_role
from app.models.faithful import Faithful
from app.models.parish import Parish
from app.models.user import User

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


async def get_current_user_payload(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    request: Request = None,  # type: ignore[assignment]
) -> dict:
    """Extract and validate the active user claims from JWT bearer token."""
    try:
        payload = decode_jwt_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="errors.invalid_token_type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Access-token claims can outlive an account role change or deactivation.
    # Reload the account on each authenticated request so authorization and
    # parish/deanery scope always reflect the current database state.
    if isinstance(db, AsyncSession):
        try:
            user_id = uuid.UUID(str(payload.get("sub", "")))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="errors.invalid_token_subject",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = await db.scalar(
            select(User).where(
                User.id == user_id,
                User.is_active.is_(True),
                User.is_deleted.is_(False),
            )
        )
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="errors.invalid_token_subject",
                headers={"WWW-Authenticate": "Bearer"},
            )
        db.info["audit_user_id"] = user.id
        if request is not None and request.client is not None:
            db.info["audit_ip_address"] = request.client.host
        payload["role"] = user.role.value
        payload["parish_id"] = str(user.parish_id) if user.parish_id else None
        payload["deanery_id"] = str(user.deanery_id) if user.deanery_id else None

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


def require_roles(allowed_roles: list[UserRole]):
    """Enforce role-based access control dependency on endpoints."""

    async def role_checker(payload: dict = Depends(get_current_user_payload)) -> dict:
        user_role_raw = payload.get("role")
        user_role: UserRole | None = None
        if user_role_raw:
            try:
                user_role = UserRole(user_role_raw)
            except ValueError:
                user_role = None

        if not user_role or not has_role(user_role, allowed_roles):
            roles_str = ", ".join(r.value for r in allowed_roles)
            raise PermissionDeniedException(
                f"Access forbidden. Required roles: {roles_str}",
                message_key="errors.access_forbidden_roles",
                message_params={"roles": roles_str},
            )
        return payload

    return role_checker


async def enforce_parish_scope(
    payload: dict, db: AsyncSession, parish_id: uuid.UUID | None
) -> uuid.UUID | None:
    """Resolve or validate a requested parish against the signed user's jurisdiction.

    Parish-bound accounts are pinned to their parish; deanery-bound accounts may
    access only parishes inside that deanery. Unassigned diocesan roles may select
    a parish. The returned UUID is suitable for passing to a service query.
    """
    from app.core.exceptions import PermissionDeniedException

    requested_id = parish_id
    user_parish = uuid.UUID(payload["parish_id"]) if payload.get("parish_id") else None
    user_deanery = uuid.UUID(payload["deanery_id"]) if payload.get("deanery_id") else None

    if user_parish:
        if requested_id is not None and requested_id != user_parish:
            raise PermissionDeniedException("Access forbidden outside assigned parish.")
        return user_parish

    if user_deanery:
        if requested_id is None:
            raise PermissionDeniedException("A parish in the assigned deanery must be selected.")
        parish = await db.scalar(
            select(Parish.id).where(
                Parish.id == requested_id,
                Parish.deanery_id == user_deanery,
                Parish.is_deleted.is_(False),
            )
        )
        if parish is None:
            raise PermissionDeniedException("Access forbidden outside assigned deanery.")
        return requested_id

    role = payload.get("role")
    if role in {
        UserRole.PARISH_SECRETARY.value,
        UserRole.PARISH_PRIEST.value,
        UserRole.PARISH_VICAR.value,
        UserRole.MINISTRY_LEADER.value,
        UserRole.DEAN.value,
    }:
        raise PermissionDeniedException("The account has no assigned parish or deanery.")

    return requested_id


async def enforce_faithful_parish(
    db: AsyncSession, faithful_id: uuid.UUID, parish_id: uuid.UUID
) -> None:
    """Prevent a sacramental record from linking a person registered elsewhere."""
    from app.core.exceptions import PermissionDeniedException

    registered_parish = await db.scalar(
        select(Faithful.parish_id).where(
            Faithful.id == faithful_id,
            Faithful.is_deleted.is_(False),
        )
    )
    if registered_parish != parish_id:
        raise PermissionDeniedException(
            "The parishioner must be registered in the selected parish."
        )
