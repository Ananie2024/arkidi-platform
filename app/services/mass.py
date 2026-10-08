"""
Mass Schedule Module Business Logic Service
"""

import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.mass import MassScheduleRepository
from app.schemas.mass import MassScheduleCreate, MassScheduleResponse
from app.utils.audit import record_audit_event


class MassService:
    def __init__(self, db: AsyncSession):
        self.repo = MassScheduleRepository(db)

    async def get_mass_schedules(
        self, parish_id: uuid.UUID, for_date: date | None = None
    ) -> list[MassScheduleResponse]:
        schedules = await self.repo.list_mass_schedules(parish_id, for_date)
        return [MassScheduleResponse.model_validate(s) for s in schedules]

    async def schedule_mass(self, data: MassScheduleCreate) -> MassScheduleResponse:
        schedule = await self.repo.create_mass_schedule(data)
        record_audit_event(
            self.repo.db,
            action="MASS_SCHEDULE_CREATED",
            entity_name="mass_schedule",
            entity_id=schedule.id,
            details={
                "parish_id": str(schedule.parish_id),
                "mass_date": schedule.mass_date.isoformat(),
            },
        )
        return MassScheduleResponse.model_validate(schedule)
