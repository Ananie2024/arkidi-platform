"""
Finance Module FastAPI Endpoints — Donations & Financial Summaries
"""
import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_roles
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
    _: dict = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.PARISH_SECRETARY])),
):
    service = FinanceService(db)
    return ApiResponse.ok(data=await service.record_donation(data), message="Donation recorded")


@router.get("/donations", response_model=ApiResponse[List[DonationResponse]])
async def list_donations(parish_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = FinanceService(db)
    return ApiResponse.ok(data=await service.list_donations(parish_id))


@router.get("/summary", response_model=ApiResponse[FinancialSummaryResponse])
async def financial_summary(parish_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = FinanceService(db)
    return ApiResponse.ok(data=await service.get_financial_summary(parish_id))