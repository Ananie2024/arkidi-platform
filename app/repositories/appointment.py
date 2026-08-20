"""
Clergy Module Database Repository
"""
import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.priest import Priest, ClergyAssignment
from app.schemas.appointment import PriestCreate, PriestUpdate, AssignmentCreate


class ClergyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, priest_id: uuid.UUID) -> Optional[Priest]:
        stmt = select(Priest).where(Priest.id == priest_id, Priest.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_priests(self, parish_id: Optional[uuid.UUID] = None) -> List[Priest]:
        stmt = select(Priest).where(Priest.is_deleted.is_(False))
        if parish_id:
            stmt = stmt.where(Priest.current_parish_id == parish_id)
        stmt = stmt.order_by(Priest.last_name, Priest.first_name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_priest(self, data: PriestCreate) -> Priest:
        priest = Priest(**data.model_dump())
        self.db.add(priest)
        await self.db.flush()
        return priest

    async def add_assignment(self, data: AssignmentCreate) -> ClergyAssignment:
        assignment = ClergyAssignment(**data.model_dump())
        self.db.add(assignment)
        await self.db.flush()
        return assignment

    async def list_assignments(self, priest_id: uuid.UUID) -> List[ClergyAssignment]:
        stmt = select(ClergyAssignment).where(ClergyAssignment.priest_id == priest_id).order_by(ClergyAssignment.start_date.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
