"""
Finance Module Business Logic Service
"""

import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundException
from app.models.audit_log import AuditLog
from app.models.donation import DonationType
from app.repositories.donation import FinanceRepository
from app.schemas.donation import (
    DonationCreate,
    DonationResponse,
    FinancialSummaryResponse,
)


class FinanceService:
    def __init__(self, db: AsyncSession):
        self.repo = FinanceRepository(db)

    async def get_donation(self, donation_id: uuid.UUID) -> DonationResponse:
        donation = await self.repo.get_by_id(donation_id)
        if not donation:
            raise EntityNotFoundException("errors.donation_not_found")
        return DonationResponse.model_validate(donation)

    async def record_donation(
        self, data: DonationCreate, current_user_id: uuid.UUID | None = None
    ) -> DonationResponse:
        receipt_no = f"REC-{data.donation_date.strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
        donation = await self.repo.create_donation(data, receipt_no)
        audit = AuditLog(
            user_id=current_user_id,
            action="DONATION_RECORDED",
            entity_name="donation",
            entity_id=str(donation.id),
            details={
                "parish_id": str(donation.parish_id),
                "amount": float(donation.amount),
                "donation_type": (
                    donation.donation_type.value
                    if hasattr(donation.donation_type, "value")
                    else str(donation.donation_type)
                ),
                "receipt_number": donation.receipt_number,
            },
        )
        self.repo.db.add(audit)
        return DonationResponse.model_validate(donation)

    async def list_donations(
        self, parish_id: uuid.UUID, start_date: date | None = None, end_date: date | None = None
    ) -> list[DonationResponse]:
        items = await self.repo.list_donations(parish_id, start_date=start_date, end_date=end_date)
        return [DonationResponse.model_validate(d) for d in items]

    async def get_financial_summary(
        self, parish_id: uuid.UUID, start_date: date | None = None, end_date: date | None = None
    ) -> FinancialSummaryResponse:
        summary = await self.repo.get_summary(parish_id, start_date, end_date)
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

    async def get_reconciliation(
        self, parish_id: uuid.UUID, start_date: date, end_date: date
    ) -> list[dict]:
        return await self.repo.get_reconciliation(parish_id, start_date, end_date)
