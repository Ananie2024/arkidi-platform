"""
Ministries Module FastAPI Endpoints — Commissions & Church Groups
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_roles
from app.models.enums import UserRole
from app.schemas.commission import MinistryCreate, MinistryResponse
from app.services.commission import MinistriesService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/ministries", tags=["Ministries & Commissions"])


@router.get("/", response_model=ApiResponse[list[MinistryResponse]])
async def list_ministries(
    parish_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    service = MinistriesService(db)
    return ApiResponse.ok(data=await service.list_ministries(parish_id=parish_id))


@router.post(
    "/",
    response_model=ApiResponse[MinistryResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_ministry(
    data: MinistryCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR])),
):
    service = MinistriesService(db)
    return ApiResponse.ok(data=await service.create_ministry(data), message="Ministry created successfully")