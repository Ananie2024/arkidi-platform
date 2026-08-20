"""
Land Assets Module FastAPI Endpoints
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_roles
from app.models.enums import UserRole
from app.schemas.land import LandParcelCreate, LandParcelResponse, BuildingAssetCreate, BuildingAssetResponse
from app.services.land import LandAssetsService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/land-assets", tags=["Land Assets & Parcels"])


@router.get("/parcels", response_model=ApiResponse[list[LandParcelResponse]])
async def list_parcels(
    parish_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    service = LandAssetsService(db)
    return ApiResponse.ok(data=await service.list_parcels(parish_id=parish_id))


@router.get("/parcels/{parcel_id}", response_model=ApiResponse[LandParcelResponse])
async def get_parcel(parcel_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = LandAssetsService(db)
    return ApiResponse.ok(data=await service.get_parcel(parcel_id))


@router.post(
    "/parcels",
    response_model=ApiResponse[LandParcelResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_parcel(
    data: LandParcelCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR])),
):
    service = LandAssetsService(db)
    return ApiResponse.ok(data=await service.create_parcel(data), message="Land parcel registered")


@router.post(
    "/buildings",
    response_model=ApiResponse[BuildingAssetResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_building_asset(
    data: BuildingAssetCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR])),
):
    service = LandAssetsService(db)
    return ApiResponse.ok(data=await service.create_building_asset(data), message="Building asset registered")