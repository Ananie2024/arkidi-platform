"""
Land Assets Module Database Repository
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parcel import BuildingAsset, LandParcel
from app.schemas.land import BuildingAssetCreate, LandParcelCreate, LandParcelUpdate


class LandAssetsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, parcel_id: uuid.UUID) -> LandParcel | None:
        stmt = select(LandParcel).where(
            LandParcel.id == parcel_id, LandParcel.is_deleted.is_(False)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_upi(self, upi: str) -> LandParcel | None:
        stmt = select(LandParcel).where(LandParcel.upi == upi, LandParcel.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_parcels(self, parish_id: uuid.UUID | None = None) -> list[LandParcel]:
        stmt = select(LandParcel).where(LandParcel.is_deleted.is_(False))
        if parish_id:
            stmt = stmt.where(LandParcel.parish_id == parish_id)
        stmt = stmt.order_by(LandParcel.parcel_name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_parcel(self, data: LandParcelCreate) -> LandParcel:
        data_dict = data.model_dump(exclude={"geojson_geometry"})
        parcel = LandParcel(**data_dict)
        if data.geojson_geometry:
            try:
                from geoalchemy2.shape import from_shape
                from shapely.geometry import shape

                parcel.boundary = from_shape(shape(data.geojson_geometry), srid=4326)
            except Exception:
                pass
        self.db.add(parcel)
        await self.db.flush()
        return parcel

    async def update_parcel(
        self, parcel_id: uuid.UUID, data: LandParcelUpdate
    ) -> LandParcel | None:
        parcel = await self.get_by_id(parcel_id)
        if not parcel:
            return None
        data_dict = data.model_dump(exclude_unset=True, exclude={"geojson_geometry"})
        for key, value in data_dict.items():
            setattr(parcel, key, value)
        if data.geojson_geometry is not None:
            try:
                from geoalchemy2.shape import from_shape
                from shapely.geometry import shape

                parcel.boundary = from_shape(shape(data.geojson_geometry), srid=4326)
            except Exception:
                pass
        await self.db.flush()
        return parcel

    async def list_buildings(self, parcel_id: uuid.UUID) -> list[BuildingAsset]:
        stmt = (
            select(BuildingAsset)
            .where(BuildingAsset.parcel_id == parcel_id, BuildingAsset.is_deleted.is_(False))
            .order_by(BuildingAsset.name)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_building(self, data: BuildingAssetCreate) -> BuildingAsset:
        building = BuildingAsset(**data.model_dump())
        self.db.add(building)
        await self.db.flush()
        return building
