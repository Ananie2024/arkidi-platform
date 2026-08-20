"""
Land Assets Module Business Logic Service
"""
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.parcel import LandAssetsRepository
from app.schemas.land import (
    LandParcelCreate,
    LandParcelResponse,
    BuildingAssetCreate,
    BuildingAssetResponse,
)
from app.core.exceptions import ParcelNotFoundException, DuplicateUPIException


class LandAssetsService:
    def __init__(self, db: AsyncSession):
        self.repo = LandAssetsRepository(db)

    async def list_parcels(self, parish_id: Optional[uuid.UUID] = None) -> List[LandParcelResponse]:
        items = await self.repo.list_parcels(parish_id)
        return [LandParcelResponse.model_validate(p) for p in items]

    async def get_parcel(self, parcel_id: uuid.UUID) -> LandParcelResponse:
        parcel = await self.repo.get_by_id(parcel_id)
        if not parcel:
            raise ParcelNotFoundException(str(parcel_id))
        return LandParcelResponse.model_validate(parcel)

    async def create_parcel(self, data: LandParcelCreate) -> LandParcelResponse:
        existing = await self.repo.get_by_upi(data.upi)
        if existing:
            raise DuplicateUPIException(data.upi)
        parcel = await self.repo.create_parcel(data)
        return LandParcelResponse.model_validate(parcel)

    async def create_building_asset(self, data: BuildingAssetCreate) -> BuildingAssetResponse:
        building = await self.repo.create_building(data)
        return BuildingAssetResponse.model_validate(building)
