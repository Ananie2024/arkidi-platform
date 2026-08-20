"""
Deanery Module Database Repository
"""
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deanery import Archdiocese, Deanery
from app.schemas.deanery import DeaneryCreate


class DeaneryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_archdiocese(self) -> Optional[Archdiocese]:
        stmt = select(Archdiocese)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_deaneries(self) -> List[Deanery]:
        stmt = select(Deanery).where(Deanery.is_deleted.is_(False)).order_by(Deanery.name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_deanery(self, deanery_id: uuid.UUID) -> Optional[Deanery]:
        stmt = select(Deanery).where(Deanery.id == deanery_id, Deanery.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_deanery(self, data: DeaneryCreate) -> Deanery:
        deanery = Deanery(**data.model_dump())
        self.db.add(deanery)
        await self.db.flush()
        return deanery
