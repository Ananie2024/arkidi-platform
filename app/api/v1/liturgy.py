"""
Liturgy Module FastAPI Endpoints — Mass Schedules & Intentions
"""
import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_roles
from app.models.enums import UserRole
from app.schemas.mass import MassScheduleCreate, MassScheduleResponse
from app.schemas.intention import MassIntentionCreate, MassIntentionResponse
from app.services.mass import MassService
from app.services.intention import IntentionService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/liturgy", tags=["Liturgy & Sacred Music"])


@router.get("/mass-schedules", response_model=ApiResponse[List[MassScheduleResponse]])
async def list_mass_schedules(
    parish_id: uuid.UUID,
    for_date: Optional[date] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    service = MassService(db)
    return ApiResponse.ok(data=await service.get_mass_schedules(parish_id, for_date))


@router.post(
    "/mass-schedules",
    response_model=ApiResponse[MassScheduleResponse],
    status_code=status.HTTP_201_CREATED,
)
async def schedule_mass(
    data: MassScheduleCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.ARCHBISHOP])),
):
    service = MassService(db)
    return ApiResponse.ok(data=await service.schedule_mass(data), message="Mass schedule created")


@router.get("/intentions", response_model=ApiResponse[List[MassIntentionResponse]])
async def list_intentions(
    parish_id: uuid.UUID,
    target_date: Optional[date] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    service = IntentionService(db)
    return ApiResponse.ok(data=await service.get_intentions(parish_id, target_date))


@router.get("/intentions/{intention_id}", response_model=ApiResponse[MassIntentionResponse])
async def get_intention(intention_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = IntentionService(db)
    return ApiResponse.ok(data=await service.get_intention(intention_id))


@router.post(
    "/intentions",
    response_model=ApiResponse[MassIntentionResponse],
    status_code=status.HTTP_201_CREATED,
)
async def register_intention(
    data: MassIntentionCreate,
    db: AsyncSession = Depends(get_db),
):
    service = IntentionService(db)
    return ApiResponse.ok(data=await service.register_intention(data), message="Intention registered")