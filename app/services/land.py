"""
Land Assets Module Business Logic Service
"""
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.parcel import LandAssetsRepository
from app.models.parcel import LandParcel
from app.schemas.land import (
    LandParcelCreate,
    LandParcelUpdate,
    LandParcelResponse,
    BuildingAssetCreate,
    BuildingAssetResponse,
)
from app.core.exceptions import ParcelNotFoundException, DuplicateUPIException


def _to_response(parcel: LandParcel) -> LandParcelResponse:
    res = LandParcelResponse.model_validate(parcel)
    if getattr(parcel, "boundary", None) is not None:
        try:
            from geoalchemy2.shape import to_shape
            from shapely.geometry import mapping
            res.geojson_geometry = mapping(to_shape(parcel.boundary))
        except Exception:
            pass
    return res


class LandAssetsService:
    def __init__(self, db: AsyncSession):
        self.repo = LandAssetsRepository(db)

    async def list_parcels(self, parish_id: Optional[uuid.UUID] = None) -> List[LandParcelResponse]:
        items = await self.repo.list_parcels(parish_id)
        return [_to_response(p) for p in items]

    async def get_parcel(self, parcel_id: uuid.UUID) -> LandParcelResponse:
        parcel = await self.repo.get_by_id(parcel_id)
        if not parcel:
            raise ParcelNotFoundException(str(parcel_id))
        return _to_response(parcel)

    async def create_parcel(self, data: LandParcelCreate) -> LandParcelResponse:
        existing = await self.repo.get_by_upi(data.upi)
        if existing:
            raise DuplicateUPIException(data.upi)
        parcel = await self.repo.create_parcel(data)
        return _to_response(parcel)

    async def update_parcel(self, parcel_id: uuid.UUID, data: LandParcelUpdate) -> LandParcelResponse:
        parcel = await self.repo.update_parcel(parcel_id, data)
        if not parcel:
            raise ParcelNotFoundException(str(parcel_id))
        return _to_response(parcel)

    async def list_buildings(self, parcel_id: uuid.UUID) -> List[BuildingAssetResponse]:
        items = await self.repo.list_buildings(parcel_id)
        return [BuildingAssetResponse.model_validate(b) for b in items]

    async def create_building_asset(self, data: BuildingAssetCreate) -> BuildingAssetResponse:
        building = await self.repo.create_building(data)
        return BuildingAssetResponse.model_validate(building)

