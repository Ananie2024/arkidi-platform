"""
Clergy Module FastAPI Endpoints — Priests & Clergy Assignments
"""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import enforce_parish_scope, get_db, require_roles
from app.models.enums import UserRole
from app.schemas.appointment import (
    AssignmentCreate,
    AssignmentResponse,
    PriestCreate,
    PriestResponse,
)
from app.services.appointment import ClergyService
from app.services.org.hierarchy_resolver import get_descendant_parish_ids
from app.utils.response import ApiResponse

router = APIRouter(prefix="/clergy", tags=["Clergy & Appointments"])


@router.get("/priests", response_model=ApiResponse[list[PriestResponse]])
async def list_priests(
    parish_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    parish_id = await enforce_parish_scope(current_user, db, parish_id)
    """List priests, optionally filtered by current parish."""
    service = ClergyService(db)
    return ApiResponse.ok(data=await service.list_priests(parish_id=parish_id))


@router.get("/priests/{priest_id}", response_model=ApiResponse[PriestResponse])
async def get_priest(
    priest_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = ClergyService(db)
    priest = await service.get_priest(priest_id)
    if priest.current_parish_id is not None:
        await enforce_parish_scope(current_user, db, priest.current_parish_id)
    elif current_user.get("parish_id") or current_user.get("deanery_id"):
        from app.core.exceptions import PermissionDeniedException

        raise PermissionDeniedException("Access forbidden outside assigned parish.")
    return ApiResponse.ok(data=priest)


@router.post(
    "/priests",
    response_model=ApiResponse[PriestResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_priest(
    data: PriestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR])),
):
    if data.current_parish_id is not None:
        await enforce_parish_scope(current_user, db, data.current_parish_id)
    service = ClergyService(db)
    return ApiResponse.ok(
        data=await service.create_priest(data), message="success.priest_registered"
    )


@router.post(
    "/assignments",
    response_model=ApiResponse[AssignmentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_assignment(
    data: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR])),
):
    """Record a new clergy assignment."""
    service = ClergyService(db)
    priest = await service.get_priest(data.priest_id)
    if priest.current_parish_id is not None:
        await enforce_parish_scope(current_user, db, priest.current_parish_id)
    if data.parish_id is not None:
        await enforce_parish_scope(current_user, db, data.parish_id)
    return ApiResponse.ok(
        data=await service.record_assignment(data), message="success.assignment_recorded"
    )


@router.get(
    "/priests/{priest_id}/assignments",
    response_model=ApiResponse[list[AssignmentResponse]],
)
async def list_priest_assignments(
    priest_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = ClergyService(db)
    priest = await service.get_priest(priest_id)
    parish_id = current_user.get("parish_id")
    deanery_id = current_user.get("deanery_id")
    if priest.current_parish_id is not None:
        await enforce_parish_scope(current_user, db, priest.current_parish_id)
    elif parish_id or deanery_id:
        from app.core.exceptions import PermissionDeniedException

        raise PermissionDeniedException("Access forbidden outside assigned parish.")
    assignments = await service.list_assignments(priest_id)
    if parish_id:
        allowed_parish_ids = {uuid.UUID(parish_id)}
    elif deanery_id:
        allowed_parish_ids = set(
            await get_descendant_parish_ids(db, deanery_id=uuid.UUID(deanery_id))
        )
    else:
        return ApiResponse.ok(data=assignments)
    return ApiResponse.ok(
        data=[item for item in assignments if item.parish_id in allowed_parish_ids]
    )
