"""
Statistics Module FastAPI Endpoints - Annual Reports & Annuario Pontificio
"""
import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_roles
from app.models.enums import UserRole
from app.schemas.common import (
    AnnualStatisticCreate,
    AnnualStatisticResponse,
    AnnuarioPontificioReport,
)
from app.schemas.indicators import IndicatorConfigView, IndicatorResult
from app.services.indicators import AggregationService
from app.services.statistics import StatisticsService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/statistics", tags=["Statistics & Reports"])


@router.post("/parish-report", response_model=ApiResponse[AnnualStatisticResponse])
async def submit_parish_report(
    data: AnnualStatisticCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    service = StatisticsService(db)
    return ApiResponse.ok(data=await service.submit_parish_report(data), message="success.parish_statistic_submitted")


@router.get("/parish-reports", response_model=ApiResponse[list[AnnualStatisticResponse]])
async def list_parish_reports(
    year: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = StatisticsService(db)
    return ApiResponse.ok(data=await service.list_parish_reports(year=year))


@router.get("/annuario-pontificio", response_model=ApiResponse[AnnuarioPontificioReport])
async def annuario_pontificio(
    year: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    service = StatisticsService(db)
    return ApiResponse.ok(data=await service.generate_annuario_pontificio(year))


@router.get("/indicators", response_model=ApiResponse[list[IndicatorConfigView]])
async def list_indicators(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """List the configuration-driven statistic indicators.

    Every indicator is declarative config (``app/services/indicators.py::
    INDICATORS``); adding a new statistics family is a config entry, not a
    hand-written method.
    """
    return ApiResponse.ok(data=AggregationService(db).list_indicators())


@router.get("/indicators/{key}", response_model=ApiResponse[IndicatorResult])
async def compute_indicator(
    key: str,
    archdiocese_id: uuid.UUID | None = Query(default=None),
    deanery_id: uuid.UUID | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    year: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """Compute one registered statistic indicator within an org scope.

    ``year`` is forwarded as a runtime ``report_year`` parameter filter so the
    annual-return indicators (e.g. ``annual_catholic_population_by_parish``)
    are pinned to a single reporting year through the same generic pipeline.
    """
    param_filters: dict = {}
    if year is not None:
        param_filters["report_year"] = year

    result = await AggregationService(db).compute(
        key,
        archdiocese_id=archdiocese_id,
        deanery_id=deanery_id,
        start_date=start_date,
        end_date=end_date,
        param_filters=param_filters,
    )
    return ApiResponse.ok(data=result)
