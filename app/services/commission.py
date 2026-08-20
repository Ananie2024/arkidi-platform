"""
Ministries Module Business Logic Service
"""
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.commission import MinistriesRepository
from app.schemas.commission import MinistryCreate, MinistryResponse


class MinistriesService:
    def __init__(self, db: AsyncSession):
        self.repo = MinistriesRepository(db)

    async def list_ministries(self, parish_id: uuid.UUID) -> List[MinistryResponse]:
        items = await self.repo.list_ministries(parish_id)
        return [MinistryResponse.model_validate(m) for m in items]

    async def create_ministry(self, data: MinistryCreate) -> MinistryResponse:
        created = await self.repo.create_ministry(data)
        return MinistryResponse.model_validate(created)
