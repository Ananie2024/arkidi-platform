"""
Deanery Module Business Logic Service
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DeaneryNotFoundException
from app.repositories.deanery import DeaneryRepository
from app.schemas.deanery import DeaneryCreate, DeaneryResponse
from app.utils.audit import record_audit_event


class DeaneryService:
    def __init__(self, db: AsyncSession):
        self.repo = DeaneryRepository(db)

    async def get_all_deaneries(self) -> list[DeaneryResponse]:
        deaneries = await self.repo.list_deaneries()
        return [DeaneryResponse.model_validate(d) for d in deaneries]

    async def get_deanery_by_id(self, deanery_id: uuid.UUID) -> DeaneryResponse:
        deanery = await self.repo.get_deanery(deanery_id)
        if not deanery:
            raise DeaneryNotFoundException(str(deanery_id))
        return DeaneryResponse.model_validate(deanery)

    async def create_deanery(self, data: DeaneryCreate) -> DeaneryResponse:
        """Create a deanery and record the administrative action."""
        deanery = await self.repo.create_deanery(data)
        record_audit_event(
            self.repo.db,
            action="DEANERY_CREATED",
            entity_name="deanery",
            entity_id=deanery.id,
            details={"archdiocese_id": str(deanery.archdiocese_id), "code": deanery.code},
        )
        return DeaneryResponse.model_validate(deanery)
