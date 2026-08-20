"""
Deanery Module Business Logic Service
"""
import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.deanery import DeaneryRepository
from app.schemas.deanery import DeaneryResponse
from app.core.exceptions import DeaneryNotFoundException


class DeaneryService:
    def __init__(self, db: AsyncSession):
        self.repo = DeaneryRepository(db)

    async def get_all_deaneries(self) -> List[DeaneryResponse]:
        deaneries = await self.repo.list_deaneries()
        return [DeaneryResponse.model_validate(d) for d in deaneries]

    async def get_deanery_by_id(self, deanery_id: uuid.UUID) -> DeaneryResponse:
        deanery = await self.repo.get_deanery(deanery_id)
        if not deanery:
            raise DeaneryNotFoundException(str(deanery_id))
        return DeaneryResponse.model_validate(deanery)
