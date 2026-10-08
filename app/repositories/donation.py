"""
Finance Module Database Repository
"""

import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.donation import Donation
from app.schemas.donation import DonationCreate


class FinanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, donation_id: uuid.UUID) -> Donation | None:
        stmt = select(Donation).where(Donation.id == donation_id, Donation.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_donation(self, data: DonationCreate, receipt_number: str) -> Donation:
        donation = Donation(
            receipt_number=receipt_number,
            **data.model_dump(),
        )
        self.db.add(donation)
        await self.db.flush()
        return donation

    async def list_donations(
        self,
        parish_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Donation]:
        stmt = (
            select(Donation)
            .where(
                Donation.parish_id == parish_id,
                Donation.is_deleted.is_(False),
            )
            .order_by(Donation.donation_date.desc())
            .offset(skip)
            .limit(limit)
        )
        if start_date is not None:
            stmt = stmt.where(Donation.donation_date >= start_date)
        if end_date is not None:
            stmt = stmt.where(Donation.donation_date <= end_date)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_summary(
        self, parish_id: uuid.UUID, start_date: date | None = None, end_date: date | None = None
    ) -> dict:
        stmt = (
            select(
                Donation.donation_type,
                func.sum(Donation.amount).label("total"),
            )
            .where(
                Donation.parish_id == parish_id,
                Donation.is_deleted.is_(False),
            )
            .group_by(Donation.donation_type)
        )
        if start_date is not None:
            stmt = stmt.where(Donation.donation_date >= start_date)
        if end_date is not None:
            stmt = stmt.where(Donation.donation_date <= end_date)

        result = await self.db.execute(stmt)
        summary_by_type = {row[0]: float(row[1] or 0.0) for row in result.all()}
        return summary_by_type

    async def get_reconciliation(
        self, parish_id: uuid.UUID, start_date: date, end_date: date
    ) -> list[dict]:
        stmt = (
            select(
                Donation.payment_method,
                func.count(Donation.id).label("transaction_count"),
                func.sum(Donation.amount).label("total_amount"),
            )
            .where(
                Donation.parish_id == parish_id,
                Donation.is_deleted.is_(False),
                Donation.donation_date >= start_date,
                Donation.donation_date <= end_date,
            )
            .group_by(Donation.payment_method)
            .order_by(Donation.payment_method)
        )
        result = await self.db.execute(stmt)
        return [
            {
                "payment_method": row.payment_method.value,
                "transaction_count": row.transaction_count,
                "total_amount": float(row.total_amount or 0),
            }
            for row in result
        ]
