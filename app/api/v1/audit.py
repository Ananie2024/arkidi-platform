"""Restricted, filterable read access to immutable audit events."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PermissionDeniedException
from app.dependencies import get_db, require_roles
from app.models.audit_log import AuditLog
from app.models.enums import UserRole
from app.schemas.audit import AuditLogResponse
from app.utils.response import ApiResponse

router = APIRouter(prefix="/audit-logs", tags=["Audit Trail"])


@router.get("", response_model=ApiResponse[list[AuditLogResponse]])
async def list_audit_logs(
    action: str | None = Query(default=None, max_length=100),
    entity_name: str | None = Query(default=None, max_length=100),
    entity_id: str | None = Query(default=None, max_length=100),
    actor_user_id: uuid.UUID | None = Query(default=None),
    created_after: datetime | None = Query(default=None),
    created_before: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(
        require_roles(
            [UserRole.SUPER_ADMIN, UserRole.ARCHBISHOP, UserRole.VICAR_GENERAL, UserRole.CHANCELLOR]
        )
    ),
):
    if user.get("parish_id") or user.get("deanery_id"):
        raise PermissionDeniedException("Audit-log access requires an archdiocesan assignment.")
    if created_after and created_before and created_after > created_before:
        raise HTTPException(status_code=422, detail="created_after must be before created_before")

    stmt = select(AuditLog)
    if action is not None:
        stmt = stmt.where(AuditLog.action == action)
    if entity_name is not None:
        stmt = stmt.where(AuditLog.entity_name == entity_name)
    if entity_id is not None:
        stmt = stmt.where(AuditLog.entity_id == entity_id)
    if actor_user_id is not None:
        stmt = stmt.where(AuditLog.user_id == actor_user_id)
    if created_after is not None:
        stmt = stmt.where(AuditLog.created_at >= created_after)
    if created_before is not None:
        stmt = stmt.where(AuditLog.created_at <= created_before)

    stmt = stmt.order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    rows = (await db.scalars(stmt)).all()
    return ApiResponse.ok(data=[AuditLogResponse.model_validate(row) for row in rows])
