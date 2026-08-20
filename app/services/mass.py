"""
Mass Schedule Module Business Logic Service
"""
import uuid
from datetime import date
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.mass import MassScheduleRepository
from app.schemas.mass import MassScheduleCreate, MassScheduleResponse


class MassService:
    def __init__(self, db: AsyncSession):
        self.repo = MassScheduleRepository(db)

    async def get_mass_schedules(
        self, parish_id: uuid.UUID, for_date: Optional[date] = None
    ) -> List[MassScheduleResponse]:
        schedules = await self.repo.list_mass_schedules(parish_id, for_date)
        return [MassScheduleResponse.model_validate(s) for s in schedules]

    async def schedule_mass(self, data: MassScheduleCreate) -> MassScheduleResponse:
        schedule = await self.repo.create_mass_schedule(data)
        return MassScheduleResponse.model_validate(schedule)
