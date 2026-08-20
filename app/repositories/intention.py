"""
Mass Intention Module Database Repository
"""
import uuid
from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.intention import MassIntention
from app.schemas.intention import MassIntentionCreate


class IntentionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_intention(self, intention_id: uuid.UUID) -> Optional[MassIntention]:
        stmt = select(MassIntention).where(
            MassIntention.id == intention_id,
            MassIntention.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_intentions(
        self, parish_id: uuid.UUID, target_date: Optional[date] = None
    ) -> List[MassIntention]:
        stmt = select(MassIntention).where(
            MassIntention.parish_id == parish_id,
            MassIntention.is_deleted.is_(False),
        )
        if target_date:
            stmt = stmt.where(MassIntention.scheduled_date == target_date)
        stmt = stmt.order_by(MassIntention.scheduled_date)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_intention(self, data: MassIntentionCreate) -> MassIntention:
        intention = MassIntention(**data.model_dump())
        self.db.add(intention)
        await self.db.flush()
        return intention