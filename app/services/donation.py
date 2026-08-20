"""
Finance Module Business Logic Service
"""
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.donation import FinanceRepository
from app.schemas.donation import (
    DonationCreate,
    DonationResponse,
    FinancialSummaryResponse,
)
from app.models.donation import DonationType


class FinanceService:
    def __init__(self, db: AsyncSession):
        self.repo = FinanceRepository(db)

    async def record_donation(self, data: DonationCreate) -> DonationResponse:
        receipt_no = f"REC-{data.donation_date.strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
        donation = await self.repo.create_donation(data, receipt_no)
        return DonationResponse.model_validate(donation)

    async def list_donations(self, parish_id: uuid.UUID) -> List[DonationResponse]:
        items = await self.repo.list_donations(parish_id)
        return [DonationResponse.model_validate(d) for d in items]

    async def get_financial_summary(self, parish_id: uuid.UUID) -> FinancialSummaryResponse:
        summary = await self.repo.get_summary(parish_id)
        tithes = summary.get(DonationType.TITHE, 0.0)
        offertory = summary.get(DonationType.OFFERTORY, 0.0)
        construction = summary.get(DonationType.CONSTRUCTION_FUND, 0.0)
        grand = sum(summary.values())

        return FinancialSummaryResponse(
            total_tithes=tithes,
            total_offertory=offertory,
            total_construction=construction,
            grand_total=grand,
        )
