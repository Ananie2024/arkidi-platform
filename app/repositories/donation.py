"""
Finance Module Database Repository
"""
import uuid
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.donation import Donation, DonationType
from app.schemas.donation import DonationCreate


class FinanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_donation(self, data: DonationCreate, receipt_number: str) -> Donation:
        donation = Donation(
            receipt_number=receipt_number,
            **data.model_dump(),
        )
        self.db.add(donation)
        await self.db.flush()
        return donation

    async def list_donations(self, parish_id: uuid.UUID, skip: int = 0, limit: int = 50) -> List[Donation]:
        stmt = select(Donation).where(
            Donation.parish_id == parish_id,
            Donation.is_deleted.is_(False),
        ).order_by(Donation.donation_date.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_summary(self, parish_id: uuid.UUID) -> dict:
        stmt = select(
            Donation.donation_type,
            func.sum(Donation.amount).label("total"),
        ).where(
            Donation.parish_id == parish_id,
            Donation.is_deleted.is_(False),
        ).group_by(Donation.donation_type)

        result = await self.db.execute(stmt)
        summary_by_type = {row[0]: float(row[1] or 0.0) for row in result.all()}
        return summary_by_type
