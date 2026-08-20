"""
Clergy Module FastAPI Endpoints — Priests & Clergy Assignments
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_roles
from app.models.enums import UserRole
from app.schemas.appointment import PriestCreate, PriestResponse, AssignmentCreate, AssignmentResponse
from app.services.appointment import ClergyService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/clergy", tags=["Clergy & Appointments"])


@router.get("/priests", response_model=ApiResponse[List[PriestResponse]])
async def list_priests(
    parish_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
):
    """List priests, optionally filtered by current parish."""
    service = ClergyService(db)
    return ApiResponse.ok(data=await service.list_priests(parish_id=parish_id))


@router.get("/priests/{priest_id}", response_model=ApiResponse[PriestResponse])
async def get_priest(priest_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = ClergyService(db)
    return ApiResponse.ok(data=await service.get_priest(priest_id))


@router.post(
    "/priests",
    response_model=ApiResponse[PriestResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_priest(
    data: PriestCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR])),
):
    service = ClergyService(db)
    return ApiResponse.ok(data=await service.create_priest(data), message="Priest registered successfully")


@router.post(
    "/assignments",
    response_model=ApiResponse[AssignmentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_assignment(
    data: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR])),
):
    """Record a new clergy assignment."""
    service = ClergyService(db)
    return ApiResponse.ok(data=await service.record_assignment(data), message="Assignment recorded")