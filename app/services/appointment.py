"""
Clergy Module Business Logic Service
"""
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.appointment import ClergyRepository
from app.schemas.appointment import (
    PriestCreate,
    PriestResponse,
    AssignmentCreate,
    AssignmentResponse,
)
from app.core.exceptions import PriestNotFoundException


class ClergyService:
    def __init__(self, db: AsyncSession):
        self.repo = ClergyRepository(db)

    async def list_priests(self, parish_id: Optional[uuid.UUID] = None) -> List[PriestResponse]:
        priests = await self.repo.list_priests(parish_id)
        return [PriestResponse.model_validate(p) for p in priests]

    async def get_priest(self, priest_id: uuid.UUID) -> PriestResponse:
        priest = await self.repo.get_by_id(priest_id)
        if not priest:
            raise PriestNotFoundException(str(priest_id))
        return PriestResponse.model_validate(priest)

    async def create_priest(self, data: PriestCreate) -> PriestResponse:
        priest = await self.repo.create_priest(data)
        return PriestResponse.model_validate(priest)

    async def record_assignment(self, data: AssignmentCreate) -> AssignmentResponse:
        assignment = await self.repo.add_assignment(data)
        return AssignmentResponse.model_validate(assignment)
