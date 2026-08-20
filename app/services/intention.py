"""
Mass Intention Module Business Logic Service
"""
import uuid
from datetime import date
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.intention import IntentionRepository
from app.schemas.intention import MassIntentionCreate, MassIntentionResponse
from app.core.exceptions import IntentionNotFoundException


class IntentionService:
    def __init__(self, db: AsyncSession):
        self.repo = IntentionRepository(db)

    async def get_intention(self, intention_id: uuid.UUID) -> MassIntentionResponse:
        intention = await self.repo.get_intention(intention_id)
        if not intention:
            raise IntentionNotFoundException(str(intention_id))
        return MassIntentionResponse.model_validate(intention)

    async def get_intentions(
        self, parish_id: uuid.UUID, target_date: Optional[date] = None
    ) -> List[MassIntentionResponse]:
        intentions = await self.repo.list_intentions(parish_id, target_date)
        return [MassIntentionResponse.model_validate(i) for i in intentions]

    async def register_intention(self, data: MassIntentionCreate) -> MassIntentionResponse:
        intention = await self.repo.create_intention(data)
        return MassIntentionResponse.model_validate(intention)