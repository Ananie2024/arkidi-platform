"""
Faithful Module Database Repository
"""
import uuid
from typing import List, Optional, Tuple
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.faithful import Faithful, Family
from app.schemas.faithful import FaithfulCreate, FaithfulUpdate, FamilyCreate


class FaithfulRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, faithful_id: uuid.UUID) -> Optional[Faithful]:
        stmt = select(Faithful).where(Faithful.id == faithful_id, Faithful.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_registration_number(self, reg_num: str) -> Optional[Faithful]:
        stmt = select(Faithful).where(Faithful.registration_number == reg_num, Faithful.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_faithful(
        self,
        parish_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Faithful], int]:
        stmt = select(Faithful).where(Faithful.is_deleted.is_(False))
        count_stmt = select(func.count(Faithful.id)).where(Faithful.is_deleted.is_(False))

        if parish_id:
            stmt = stmt.where(Faithful.parish_id == parish_id)
            count_stmt = count_stmt.where(Faithful.parish_id == parish_id)

        if search:
            search_filter = or_(
                Faithful.first_name.ilike(f"%{search}%"),
                Faithful.last_name.ilike(f"%{search}%"),
                Faithful.christian_name.ilike(f"%{search}%"),
                Faithful.registration_number.ilike(f"%{search}%"),
                Faithful.national_id.ilike(f"%{search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total_res = await self.db.execute(count_stmt)
        total = total_res.scalar() or 0

        stmt = stmt.order_by(Faithful.last_name, Faithful.first_name).offset(skip).limit(limit)
        items_res = await self.db.execute(stmt)
        return list(items_res.scalars().all()), total

    async def create_faithful(self, data: FaithfulCreate) -> Faithful:
        faithful = Faithful(**data.model_dump())
        self.db.add(faithful)
        await self.db.flush()
        return faithful

    async def create_family(self, data: FamilyCreate) -> Family:
        family = Family(**data.model_dump())
        self.db.add(family)
        await self.db.flush()
        return family
