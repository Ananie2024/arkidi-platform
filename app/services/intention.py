"""
Mass Intention Module Business Logic Service
"""

import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import IntentionNotFoundException
from app.repositories.intention import IntentionRepository
from app.schemas.intention import MassIntentionCreate, MassIntentionResponse
from app.utils.audit import record_audit_event


class IntentionService:
    def __init__(self, db: AsyncSession):
        self.repo = IntentionRepository(db)

    async def get_intention(self, intention_id: uuid.UUID) -> MassIntentionResponse:
        intention = await self.repo.get_intention(intention_id)
        if not intention:
            raise IntentionNotFoundException(str(intention_id))
        return MassIntentionResponse.model_validate(intention)

    async def get_intentions(
        self, parish_id: uuid.UUID, target_date: date | None = None
    ) -> list[MassIntentionResponse]:
        intentions = await self.repo.list_intentions(parish_id, target_date)
        return [MassIntentionResponse.model_validate(i) for i in intentions]

    async def register_intention(self, data: MassIntentionCreate) -> MassIntentionResponse:
        intention = await self.repo.create_intention(data)
        record_audit_event(
            self.repo.db,
            action="MASS_INTENTION_REGISTERED",
            entity_name="mass_intention",
            entity_id=intention.id,
            details={
                "parish_id": str(intention.parish_id),
                "scheduled_date": intention.scheduled_date.isoformat(),
                "intention_type": intention.intention_type.value,
            },
        )
        return MassIntentionResponse.model_validate(intention)
