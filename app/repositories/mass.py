"""
Mass Schedule Module Database Repository
"""
import uuid
from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mass import MassSchedule
from app.schemas.mass import MassScheduleCreate


class MassScheduleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_mass_schedules(self, parish_id: uuid.UUID, for_date: Optional[date] = None) -> List[MassSchedule]:
        stmt = select(MassSchedule).where(
            MassSchedule.parish_id == parish_id,
            MassSchedule.is_deleted.is_(False),
        )
        if for_date:
            stmt = stmt.where(MassSchedule.mass_date == for_date)
        stmt = stmt.order_by(MassSchedule.mass_date, MassSchedule.start_time)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_mass_schedule(self, data: MassScheduleCreate) -> MassSchedule:
        schedule = MassSchedule(**data.model_dump())
        self.db.add(schedule)
        await self.db.flush()
        return schedule
