"""
Sacraments Module Database Repository
"""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.faithful import Faithful
from app.models.parish import Parish
from app.models.sacrament import (
    AmendmentStatus,
    AnointingOfTheSickRecord,
    BaptismRecord,
    CertificateIssue,
    ChristianFuneralRecord,
    ConfirmationRecord,
    FirstCommunionRecord,
    HolyOrdersRecord,
    MatrimonyRecord,
    ReligiousProfessionRecord,
    SacramentalAmendment,
    SacramentType,
)
from app.schemas.sacrament import (
    AmendmentRequestCreate,
    AnointingOfTheSickCreate,
    BaptismCreate,
    ChristianFuneralCreate,
    ConfirmationCreate,
    FirstCommunionCreate,
    HolyOrdersCreate,
    MatrimonyCreate,
    ReligiousProfessionCreate,
)


class SacramentsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_baptism_by_id(self, record_id: uuid.UUID) -> BaptismRecord | None:
        stmt = select(BaptismRecord).where(
            BaptismRecord.id == record_id, BaptismRecord.is_deleted.is_(False)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_baptism_by_faithful(self, faithful_id: uuid.UUID) -> BaptismRecord | None:
        stmt = select(BaptismRecord).where(
            BaptismRecord.faithful_id == faithful_id, BaptismRecord.is_deleted.is_(False)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_baptisms(self, parish_id: uuid.UUID | None = None) -> list[BaptismRecord]:
        stmt = select(BaptismRecord).where(BaptismRecord.is_deleted.is_(False))
        if parish_id:
            stmt = stmt.where(BaptismRecord.parish_id == parish_id)
        stmt = stmt.order_by(BaptismRecord.celebration_date.desc(), BaptismRecord.act_number.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_confirmations(
        self, parish_id: uuid.UUID | None = None
    ) -> list[ConfirmationRecord]:
        stmt = select(ConfirmationRecord).where(ConfirmationRecord.is_deleted.is_(False))
        if parish_id:
            stmt = stmt.where(ConfirmationRecord.parish_id == parish_id)
        stmt = stmt.order_by(
            ConfirmationRecord.celebration_date.desc(), ConfirmationRecord.act_number.desc()
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_matrimonies(self, parish_id: uuid.UUID | None = None) -> list[MatrimonyRecord]:
        stmt = select(MatrimonyRecord).where(MatrimonyRecord.is_deleted.is_(False))
        if parish_id:
            stmt = stmt.where(MatrimonyRecord.parish_id == parish_id)
        stmt = stmt.order_by(
            MatrimonyRecord.celebration_date.desc(), MatrimonyRecord.act_number.desc()
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

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

    async def create_religious_profession(
        self, data: ReligiousProfessionCreate
    ) -> ReligiousProfessionRecord:
        record = ReligiousProfessionRecord(**data.model_dump())
        self.db.add(record)
        await self.db.flush()
        return record

    async def create_anointing_of_the_sick(
        self, data: AnointingOfTheSickCreate
    ) -> AnointingOfTheSickRecord:
        record = AnointingOfTheSickRecord(**data.model_dump())
        self.db.add(record)
        await self.db.flush()
        return record

    async def create_christian_funeral(
        self, data: ChristianFuneralCreate
    ) -> ChristianFuneralRecord:
        record = ChristianFuneralRecord(**data.model_dump())
        self.db.add(record)
        await self.db.flush()
        return record

    async def create_certificate_issue(self, issue: CertificateIssue) -> CertificateIssue:
        self.db.add(issue)
        await self.db.flush()
        return issue

    async def get_certificate_by_token(self, token: str) -> CertificateIssue | None:
        stmt = select(CertificateIssue).where(CertificateIssue.verification_token == token)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_certificate_by_id(self, certificate_id: uuid.UUID) -> CertificateIssue | None:
        stmt = select(CertificateIssue).where(CertificateIssue.id == certificate_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_faithful_by_id(self, faithful_id: uuid.UUID) -> Faithful | None:
        stmt = select(Faithful).where(Faithful.id == faithful_id, Faithful.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_parish_by_id(self, parish_id: uuid.UUID) -> Parish | None:
        stmt = select(Parish).where(Parish.id == parish_id, Parish.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # -----------------------------------------------------------------------
    # Sacramental Amendment Workflow Methods
    # -----------------------------------------------------------------------

    def get_model_for_sacrament(self, sacrament_type: SacramentType):
        mapping = {
            SacramentType.BAPTISM: BaptismRecord,
            SacramentType.CONFIRMATION: ConfirmationRecord,
            SacramentType.MATRIMONY: MatrimonyRecord,
            SacramentType.FIRST_COMMUNION: FirstCommunionRecord,
            SacramentType.HOLY_ORDERS: HolyOrdersRecord,
            SacramentType.RELIGIOUS_PROFESSION: ReligiousProfessionRecord,
            SacramentType.ANOINTING_OF_THE_SICK: AnointingOfTheSickRecord,
            SacramentType.CHRISTIAN_FUNERAL: ChristianFuneralRecord,
        }
        return mapping.get(sacrament_type)

    async def get_record_by_type_and_id(
        self,
        sacrament_type: SacramentType,
        record_id: uuid.UUID,
    ) -> Any | None:
        model_cls = self.get_model_for_sacrament(sacrament_type)
        if not model_cls:
            return None
        stmt = select(model_cls).where(model_cls.id == record_id, model_cls.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_amendment(
        self,
        data: AmendmentRequestCreate,
        requested_by_user_id: uuid.UUID | None = None,
    ) -> SacramentalAmendment:
        amendment = SacramentalAmendment(
            sacrament_type=data.sacrament_type,
            record_id=data.record_id,
            amendment_type=data.amendment_type,
            reason=data.reason,
            field_changes=data.field_changes,
            supporting_document_id=data.supporting_document_id,
            status=AmendmentStatus.PENDING,
            requested_by_user_id=requested_by_user_id,
        )
        self.db.add(amendment)
        await self.db.flush()
        return amendment

    async def get_amendment_by_id(self, amendment_id: uuid.UUID) -> SacramentalAmendment | None:
        stmt = select(SacramentalAmendment).where(
            SacramentalAmendment.id == amendment_id,
            SacramentalAmendment.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_amendments(
        self,
        sacrament_type: SacramentType | None = None,
        record_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> list[SacramentalAmendment]:
        stmt = select(SacramentalAmendment).where(SacramentalAmendment.is_deleted.is_(False))
        if sacrament_type is not None:
            stmt = stmt.where(SacramentalAmendment.sacrament_type == sacrament_type)
        if record_id is not None:
            stmt = stmt.where(SacramentalAmendment.record_id == record_id)
        if status is not None:
            stmt = stmt.where(SacramentalAmendment.status == status)

        stmt = stmt.order_by(SacramentalAmendment.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
