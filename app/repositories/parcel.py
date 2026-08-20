"""
Land Assets Module Database Repository
"""
import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.parcel import LandParcel, LandDocument, BuildingAsset
from app.schemas.land import LandParcelCreate, BuildingAssetCreate


class LandAssetsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, parcel_id: uuid.UUID) -> Optional[LandParcel]:
        stmt = select(LandParcel).where(LandParcel.id == parcel_id, LandParcel.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_upi(self, upi: str) -> Optional[LandParcel]:
        stmt = select(LandParcel).where(LandParcel.upi == upi, LandParcel.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_parcels(self, parish_id: Optional[uuid.UUID] = None) -> List[LandParcel]:
        stmt = select(LandParcel).where(LandParcel.is_deleted.is_(False))
        if parish_id:
            stmt = stmt.where(LandParcel.parish_id == parish_id)
        stmt = stmt.order_by(LandParcel.parcel_name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_parcel(self, data: LandParcelCreate) -> LandParcel:
        data_dict = data.model_dump(exclude={"geojson_geometry"})
        parcel = LandParcel(**data_dict)
        self.db.add(parcel)
        await self.db.flush()
        return parcel

    async def create_building(self, data: BuildingAssetCreate) -> BuildingAsset:
        building = BuildingAsset(**data.model_dump())
        self.db.add(building)
        await self.db.flush()
        return building
