"""
Clergy Module Business Logic Service
"""

import uuid
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PriestNotFoundException
from app.repositories.appointment import ClergyRepository
from app.schemas.appointment import (
    AssignmentCreate,
    AssignmentResponse,
    PriestCreate,
    PriestResponse,
)
from app.utils.audit import record_audit_event


class ClergyService:
    def __init__(self, db: AsyncSession):
        self.repo = ClergyRepository(db)

    async def list_priests(self, parish_id: uuid.UUID | None = None) -> list[PriestResponse]:
        priests = await self.repo.list_priests(parish_id)
        return [PriestResponse.model_validate(p) for p in priests]

    async def get_priest(self, priest_id: uuid.UUID) -> PriestResponse:
        priest = await self.repo.get_by_id(priest_id)
        if not priest:
            raise PriestNotFoundException(str(priest_id))
        return PriestResponse.model_validate(priest)

    async def create_priest(self, data: PriestCreate) -> PriestResponse:
        priest = await self.repo.create_priest(data)
        record_audit_event(
            self.repo.db,
            action="CLERGY_PROFILE_CREATED",
            entity_name="priest",
            entity_id=priest.id,
            details={
                "current_parish_id": (
                    str(priest.current_parish_id) if priest.current_parish_id else None
                ),
                "clergy_type": priest.clergy_type.value,
            },
        )
        return PriestResponse.model_validate(priest)

    async def record_assignment(self, data: AssignmentCreate) -> AssignmentResponse:
        if data.is_current:
            previous_assignments = await self.repo.list_assignments(data.priest_id)
            for previous in previous_assignments:
                if previous.is_current:
                    previous.is_current = False
                    if previous.end_date is None and previous.start_date < data.start_date:
                        previous.end_date = data.start_date - timedelta(days=1)
            priest = await self.repo.get_by_id(data.priest_id)
            if priest is not None:
                priest.current_parish_id = data.parish_id
                priest.current_role = data.role_title
            await self.repo.db.flush()
        assignment = await self.repo.add_assignment(data)
        record_audit_event(
            self.repo.db,
            action="CLERGY_ASSIGNMENT_RECORDED",
            entity_name="clergy_assignment",
            entity_id=assignment.id,
            details={
                "priest_id": str(assignment.priest_id),
                "parish_id": str(assignment.parish_id) if assignment.parish_id else None,
                "start_date": assignment.start_date.isoformat(),
            },
        )
        return AssignmentResponse.model_validate(assignment)

    async def list_assignments(self, priest_id: uuid.UUID) -> list[AssignmentResponse]:
        if not await self.repo.get_by_id(priest_id):
            raise PriestNotFoundException(str(priest_id))
        assignments = await self.repo.list_assignments(priest_id)
        return [AssignmentResponse.model_validate(item) for item in assignments]
