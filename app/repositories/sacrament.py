"""
Sacraments Module Database Repository
"""
import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sacrament import (
    BaptismRecord,
    ConfirmationRecord,
    MatrimonyRecord,
    FirstCommunionRecord,
    HolyOrdersRecord,
    ReligiousProfessionRecord,
    AnointingOfTheSickRecord,
    ChristianFuneralRecord,
    CertificateIssue,
)
from app.schemas.sacrament import (
    BaptismCreate,
    ConfirmationCreate,
    MatrimonyCreate,
    FirstCommunionCreate,
    HolyOrdersCreate,
    ReligiousProfessionCreate,
    AnointingOfTheSickCreate,
    ChristianFuneralCreate,
)


class SacramentsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_baptism_by_id(self, record_id: uuid.UUID) -> Optional[BaptismRecord]:
        stmt = select(BaptismRecord).where(BaptismRecord.id == record_id, BaptismRecord.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_baptism_by_faithful(self, faithful_id: uuid.UUID) -> Optional[BaptismRecord]:
        stmt = select(BaptismRecord).where(BaptismRecord.faithful_id == faithful_id, BaptismRecord.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_baptism(self, data: BaptismCreate) -> BaptismRecord:
        record = BaptismRecord(**data.model_dump())
        self.db.add(record)
        await self.db.flush()
        return record

    async def create_confirmation(self, data: ConfirmationCreate) -> ConfirmationRecord:
        record = ConfirmationRecord(**data.model_dump())
        self.db.add(record)
        await self.db.flush()
        return record

    async def create_matrimony(self, data: MatrimonyCreate) -> MatrimonyRecord:
        record = MatrimonyRecord(**data.model_dump())
        self.db.add(record)
        await self.db.flush()
        return record

    async def create_first_communion(self, data: FirstCommunionCreate) -> FirstCommunionRecord:
        record = FirstCommunionRecord(**data.model_dump())
        self.db.add(record)
        await self.db.flush()
        return record

    async def create_holy_orders(self, data: HolyOrdersCreate) -> HolyOrdersRecord:
        record = HolyOrdersRecord(**data.model_dump())
        self.db.add(record)
        await self.db.flush()
        return record

    async def create_religious_profession(self, data: ReligiousProfessionCreate) -> ReligiousProfessionRecord:
        record = ReligiousProfessionRecord(**data.model_dump())
        self.db.add(record)
        await self.db.flush()
        return record

    async def create_anointing_of_the_sick(self, data: AnointingOfTheSickCreate) -> AnointingOfTheSickRecord:
        record = AnointingOfTheSickRecord(**data.model_dump())
        self.db.add(record)
        await self.db.flush()
        return record

    async def create_christian_funeral(self, data: ChristianFuneralCreate) -> ChristianFuneralRecord:
        record = ChristianFuneralRecord(**data.model_dump())
        self.db.add(record)
        await self.db.flush()
        return record

    async def create_certificate_issue(self, issue: CertificateIssue) -> CertificateIssue:
        self.db.add(issue)
        await self.db.flush()
        return issue

    async def get_certificate_by_token(self, token: str) -> Optional[CertificateIssue]:
        stmt = select(CertificateIssue).where(CertificateIssue.verification_token == token)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
