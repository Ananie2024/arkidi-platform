"""
Finance Module FastAPI Endpoints — Donations & Financial Summaries
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import enforce_parish_scope, get_db, require_roles
from app.models.enums import UserRole
from app.schemas.donation import DonationCreate, DonationResponse, FinancialSummaryResponse
from app.services.donation import FinanceService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/finance", tags=["Finance & Offerings"])


@router.post(
    "/donations",
    response_model=ApiResponse[DonationResponse],
    status_code=status.HTTP_201_CREATED,
)
async def record_donation(
    data: DonationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.PARISH_SECRETARY])),
):
    await enforce_parish_scope(current_user, db, data.parish_id)
    service = FinanceService(db)
    user_id = uuid.UUID(current_user["sub"]) if current_user.get("sub") else None
    return ApiResponse.ok(
        data=await service.record_donation(data, current_user_id=user_id),
        message="success.donation_recorded",
    )


@router.get("/donations", response_model=ApiResponse[list[DonationResponse]])
async def list_donations(
    parish_id: uuid.UUID,
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    await enforce_parish_scope(current_user, db, parish_id)
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be on or before end_date")
    service = FinanceService(db)
    return ApiResponse.ok(data=await service.list_donations(parish_id, start_date, end_date))


@router.get("/donations/{donation_id}", response_model=ApiResponse[DonationResponse])
async def get_donation(
    donation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = FinanceService(db)
    item = await service.get_donation(donation_id)
    await enforce_parish_scope(current_user, db, item.parish_id)
    return ApiResponse.ok(data=item)


@router.get("/summary", response_model=ApiResponse[FinancialSummaryResponse])
async def financial_summary(
    parish_id: uuid.UUID,
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    await enforce_parish_scope(current_user, db, parish_id)
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be on or before end_date")
    service = FinanceService(db)
    return ApiResponse.ok(data=await service.get_financial_summary(parish_id, start_date, end_date))


@router.get("/reconciliation", response_model=ApiResponse[list[dict]])
async def financial_reconciliation(
    parish_id: uuid.UUID,
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """Summarize recorded receipts by tender type for a closed date range."""
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be on or before end_date")
    await enforce_parish_scope(current_user, db, parish_id)
    service = FinanceService(db)
    return ApiResponse.ok(data=await service.get_reconciliation(parish_id, start_date, end_date))
