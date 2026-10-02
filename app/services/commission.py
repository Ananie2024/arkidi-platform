"""
Ministries Module Business Logic Service
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.commission import MinistriesRepository
from app.schemas.commission import MinistryCreate, MinistryResponse
from app.utils.audit import record_audit_event


class MinistriesService:
    def __init__(self, db: AsyncSession):
        self.repo = MinistriesRepository(db)

    async def list_ministries(self, parish_id: uuid.UUID | None = None) -> list[MinistryResponse]:
        items = await self.repo.list_ministries(parish_id)
        return [MinistryResponse.model_validate(m) for m in items]

    async def create_ministry(self, data: MinistryCreate) -> MinistryResponse:
        created = await self.repo.create_ministry(data)
        record_audit_event(
            self.repo.db, action="MINISTRY_CREATED", entity_name="ministry", entity_id=created.id,
            details={"parish_id": str(created.parish_id) if created.parish_id else None},
        )
        return MinistryResponse.model_validate(created)
