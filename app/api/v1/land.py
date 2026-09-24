"""
Land Assets Module FastAPI Endpoints
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_roles
from app.models.enums import UserRole
from app.schemas.land import (
    BuildingAssetCreate,
    BuildingAssetResponse,
    LandParcelCreate,
    LandParcelResponse,
    LandParcelUpdate,
)
from app.services.land import LandAssetsService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/land-assets", tags=["Land Assets & Parcels"])


@router.get("/parcels", response_model=ApiResponse[list[LandParcelResponse]])
async def list_parcels(
    parish_id: uuid.UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = LandAssetsService(db)
    return ApiResponse.ok(data=await service.list_parcels(parish_id=parish_id))


@router.get("/parcels/{parcel_id}", response_model=ApiResponse[LandParcelResponse])
async def get_parcel(
    parcel_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = LandAssetsService(db)
    return ApiResponse.ok(data=await service.get_parcel(parcel_id))


@router.put("/parcels/{parcel_id}", response_model=ApiResponse[LandParcelResponse])
async def update_parcel(
    parcel_id: uuid.UUID,
    data: LandParcelUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.CHANCELLOR])),
):
    service = LandAssetsService(db)
    return ApiResponse.ok(
        data=await service.update_parcel(parcel_id, data), message="success.parcel_updated"
    )


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
    return ApiResponse.ok(
        data=await service.create_parcel(data), message="success.parcel_registered"
    )


@router.get(
    "/parcels/{parcel_id}/buildings", response_model=ApiResponse[list[BuildingAssetResponse]]
)
async def list_parcel_buildings(
    parcel_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = LandAssetsService(db)
    return ApiResponse.ok(data=await service.list_buildings(parcel_id))


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
    return ApiResponse.ok(
        data=await service.create_building_asset(data), message="success.building_registered"
    )
