"""
Statistics Module FastAPI Endpoints - Annual Reports & Annuario Pontificio
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import enforce_parish_scope, get_db, require_roles
from app.models.enums import UserRole
from app.schemas.common import (
    AnnualStatisticCreate,
    AnnualStatisticResponse,
    AnnuarioPontificioReport,
    ParishReportReconciliation,
)
from app.schemas.indicators import IndicatorConfigView, IndicatorResult
from app.services.indicators import AggregationService
from app.services.org.hierarchy_resolver import get_descendant_parish_ids
from app.services.statistics import StatisticsService
from app.utils.response import ApiResponse

router = APIRouter(prefix="/statistics", tags=["Statistics & Reports"])


@router.post("/parish-report", response_model=ApiResponse[AnnualStatisticResponse])
async def submit_parish_report(
    data: AnnualStatisticCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.PARISH_SECRETARY])),
):
    await enforce_parish_scope(user, db, data.parish_id)
    service = StatisticsService(db)
    user_id = uuid.UUID(user["sub"]) if user.get("sub") else None
    return ApiResponse.ok(
        data=await service.submit_parish_report(data, current_user_id=user_id),
        message="success.parish_statistic_submitted",
    )


@router.get("/parish-reports", response_model=ApiResponse[list[AnnualStatisticResponse]])
async def list_parish_reports(
    year: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    if user.get("parish_id"):
        parish_ids = [uuid.UUID(user["parish_id"])]
    elif user.get("deanery_id"):
        parish_ids = await get_descendant_parish_ids(
            db, deanery_id=uuid.UUID(user["deanery_id"])
        )
    else:
        await enforce_parish_scope(user, db, None)
        parish_ids = None
    service = StatisticsService(db)
    return ApiResponse.ok(data=await service.list_parish_reports(year=year, parish_ids=parish_ids))


@router.get("/annuario-pontificio", response_model=ApiResponse[AnnuarioPontificioReport])
async def annuario_pontificio(
    year: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    if user.get("parish_id") or user.get("deanery_id"):
        from app.core.exceptions import PermissionDeniedException

        raise PermissionDeniedException("The Annuario Pontificio is an archdiocesan report.")
    await enforce_parish_scope(user, db, None)
    service = StatisticsService(db)
    return ApiResponse.ok(data=await service.generate_annuario_pontificio(year))


@router.get(
    "/parish-reports/{parish_id}/{year}/reconciliation",
    response_model=ApiResponse[list[ParishReportReconciliation]],
)
async def reconcile_parish_report(
    parish_id: uuid.UUID,
    year: int = Query(ge=1900, le=2200),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    """Compare parish-reported sacrament totals with dated register entries."""
    await enforce_parish_scope(user, db, parish_id)
    service = StatisticsService(db)
    return ApiResponse.ok(data=await service.reconcile_parish_report(parish_id, year))


@router.get("/indicators", response_model=ApiResponse[list[IndicatorConfigView]])
async def list_indicators(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
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
    user: dict = Depends(require_roles([UserRole.READ_ONLY_AUDITOR])),
):
    if start_date and end_date and start_date > end_date:
        from app.core.exceptions import ValidationException

        raise ValidationException("start_date must be on or before end_date")
    if year is not None and not 1900 <= year <= 2200:
        from app.core.exceptions import ValidationException

        raise ValidationException("year must be between 1900 and 2200")
    """Compute one registered statistic indicator within an org scope.

    ``year`` is forwarded as a runtime ``report_year`` parameter filter so the
    annual-return indicators (e.g. ``annual_catholic_population_by_parish``)
    are pinned to a single reporting year through the same generic pipeline.
    """
    if user.get("parish_id"):
        from app.core.exceptions import PermissionDeniedException

        raise PermissionDeniedException("Parish-wide indicator output is outside this account scope.")
    if user.get("deanery_id"):
        assigned_deanery_id = uuid.UUID(user["deanery_id"])
        if deanery_id is not None and deanery_id != assigned_deanery_id:
            from app.core.exceptions import PermissionDeniedException

            raise PermissionDeniedException("Requested deanery is outside the assigned jurisdiction.")
        if archdiocese_id is not None:
            from app.core.exceptions import PermissionDeniedException

            raise PermissionDeniedException("Archdiocesan indicator output is outside this account scope.")
        deanery_id = assigned_deanery_id
    else:
        await enforce_parish_scope(user, db, None)
    aggregation = AggregationService(db)
    indicator = aggregation.get_indicator(key)
    if year is not None and indicator.period_field != "report_year":
        from app.core.exceptions import ValidationException

        raise ValidationException("A reporting year filter is supported only for annual return indicators.")
    param_filters: dict = {}
    if year is not None:
        param_filters["report_year"] = year

    result = await aggregation.compute(
        key,
        archdiocese_id=archdiocese_id,
        deanery_id=deanery_id,
        start_date=start_date,
        end_date=end_date,
        param_filters=param_filters,
    )
    return ApiResponse.ok(data=result)
