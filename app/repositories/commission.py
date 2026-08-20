"""
Ministries Module Database Repository
"""
import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ministry import Ministry
from app.schemas.commission import MinistryCreate


class MinistriesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_ministries(self, parish_id: uuid.UUID) -> List[Ministry]:
        stmt = select(Ministry).where(
            Ministry.parish_id == parish_id,
            Ministry.is_deleted.is_(False),
        ).order_by(Ministry.name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_ministry(self, data: MinistryCreate) -> Ministry:
        ministry = Ministry(**data.model_dump())
        self.db.add(ministry)
        await self.db.flush()
        return ministry
