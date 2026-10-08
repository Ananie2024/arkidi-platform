"""
Faithful Module Database Repository
"""

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.faithful import Faithful, Family
from app.schemas.faithful import FaithfulCreate, FaithfulUpdate, FamilyCreate, FamilyUpdate


class FaithfulRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, faithful_id: uuid.UUID) -> Faithful | None:
        stmt = select(Faithful).where(Faithful.id == faithful_id, Faithful.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_registration_number(self, reg_num: str) -> Faithful | None:
        stmt = select(Faithful).where(
            Faithful.registration_number == reg_num, Faithful.is_deleted.is_(False)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_family_by_id(self, family_id: uuid.UUID) -> Family | None:
        stmt = select(Family).where(Family.id == family_id, Family.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_families(
        self, parish_id: uuid.UUID | None = None, search: str | None = None
    ) -> list[Family]:
        stmt = select(Family).where(Family.is_deleted.is_(False))
        if parish_id:
            stmt = stmt.where(Family.parish_id == parish_id)
        if search:
            stmt = stmt.where(
                or_(
                    Family.family_code.ilike(f"%{search}%"), Family.family_name.ilike(f"%{search}%")
                )
            )
        return list((await self.db.scalars(stmt.order_by(Family.family_name))).all())

    async def list_family_members(self, family_id: uuid.UUID) -> list[Faithful]:
        stmt = (
            select(Faithful)
            .where(Faithful.family_id == family_id, Faithful.is_deleted.is_(False))
            .order_by(Faithful.last_name, Faithful.first_name)
        )
        return list((await self.db.scalars(stmt)).all())

    async def list_faithful(
        self,
        parish_id: uuid.UUID | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Faithful], int]:
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

    async def update_faithful(self, faithful: Faithful, data: FaithfulUpdate) -> Faithful:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(faithful, key, value)
        await self.db.flush()
        return faithful

    async def create_family(self, data: FamilyCreate) -> Family:
        family = Family(**data.model_dump())
        self.db.add(family)
        await self.db.flush()
        return family

    async def update_family(self, family: Family, data: FamilyUpdate) -> Family:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(family, key, value)
        await self.db.flush()
        return family
