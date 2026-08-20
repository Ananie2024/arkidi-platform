"""
Parish Module Database Repository — Parish, Centrale & Small Christian Communities.
"""
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parish import Parish, Centrale, SmallChristianCommunity
from app.schemas.parish import ParishCreate, CentraleCreate, SCCCreate


class ParishRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_parishes(self, deanery_id: Optional[uuid.UUID] = None) -> List[Parish]:
        stmt = select(Parish).where(Parish.is_deleted.is_(False))
        if deanery_id:
            stmt = stmt.where(Parish.deanery_id == deanery_id)
        stmt = stmt.order_by(Parish.name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_parish(self, parish_id: uuid.UUID) -> Optional[Parish]:
        stmt = select(Parish).where(Parish.id == parish_id, Parish.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_parish(self, data: ParishCreate) -> Parish:
        parish = Parish(**data.model_dump())
        self.db.add(parish)
        await self.db.flush()
        return parish

    async def list_centrales(self, parish_id: uuid.UUID) -> List[Centrale]:
        stmt = select(Centrale).where(Centrale.parish_id == parish_id, Centrale.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_centrale(self, data: CentraleCreate) -> Centrale:
        centrale = Centrale(**data.model_dump())
        self.db.add(centrale)
        await self.db.flush()
        return centrale

    async def list_scc(self, centrale_id: uuid.UUID) -> List[SmallChristianCommunity]:
        stmt = select(SmallChristianCommunity).where(
            SmallChristianCommunity.centrale_id == centrale_id,
            SmallChristianCommunity.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_scc(self, data: SCCCreate) -> SmallChristianCommunity:
        scc = SmallChristianCommunity(**data.model_dump())
        self.db.add(scc)
        await self.db.flush()
        return scc