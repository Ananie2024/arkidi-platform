"""
Liturgy Module FastAPI Endpoints — Mass Schedules & Intentions
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_roles
from app.models.enums import UserRole
from app.schemas.intention import MassIntentionCreate, MassIntentionResponse
from app.schemas.mass import MassScheduleCreate, MassScheduleResponse
from app.services.intention import IntentionService
from app.services.mass import MassService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/liturgy", tags=["Liturgy & Sacred Music"])


@router.get("/mass-schedules", response_model=ApiResponse[list[MassScheduleResponse]])
async def list_mass_schedules(
    parish_id: uuid.UUID,
    for_date: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
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
    _: dict = Depends(require_roles([UserRole.PARISH_PRIEST, UserRole.PARISH_VICAR])),
):
    service = MassService(db)
    return ApiResponse.ok(data=await service.schedule_mass(data), message="success.mass_created")


@router.get("/intentions", response_model=ApiResponse[list[MassIntentionResponse]])
async def list_intentions(
    parish_id: uuid.UUID,
    target_date: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = IntentionService(db)
    return ApiResponse.ok(data=await service.get_intentions(parish_id, target_date))


@router.get("/intentions/{intention_id}", response_model=ApiResponse[MassIntentionResponse])
async def get_intention(
    intention_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
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
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    service = IntentionService(db)
    return ApiResponse.ok(
        data=await service.register_intention(data), message="success.intention_registered"
    )
