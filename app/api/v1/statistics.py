"""
Statistics Module FastAPI Endpoints — Annual Reports & Annuario Pontificio
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.common import AnnualStatisticCreate, AnnualStatisticResponse, AnnuarioPontificioReport
from app.services.statistics import StatisticsService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/statistics", tags=["Statistics & Reports"])


@router.post("/parish-report", response_model=ApiResponse[AnnualStatisticResponse])
async def submit_parish_report(data: AnnualStatisticCreate, db: AsyncSession = Depends(get_db)):
    service = StatisticsService(db)
    return ApiResponse.ok(data=await service.submit_parish_report(data), message="Parish statistic submitted")


@router.get("/annuario-pontificio", response_model=ApiResponse[AnnuarioPontificioReport])
async def annuario_pontificio(year: int, db: AsyncSession = Depends(get_db)):
    service = StatisticsService(db)
    return ApiResponse.ok(data=await service.generate_annuario_pontificio(year))