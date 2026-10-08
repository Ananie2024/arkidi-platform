"""
Statistics Module Business Logic Service

The Annuario Pontificio report is composed from configuration-driven
indicator computations (ADR 002) — no hand-written aggregation SQL.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.survey import StatisticsRepository
from app.schemas.common import (
    AnnualStatisticCreate,
    AnnualStatisticResponse,
    AnnuarioPontificioReport,
    ParishReportReconciliation,
)
from app.services.indicators import AggregationService
from app.utils.audit import record_audit_event

# Annuario Pontificio figure -> indicator key. Each indicator is summed over
# every archdiocese with param_filters={"report_year": year}, which reproduces
# the former global totals without bespoke SQL.
_ANNUARIO_SOURCES: list[tuple[str, str]] = [
    ("total_catholics", "annual_catholic_population_by_parish"),
    ("infant_baptisms", "annual_infant_baptisms_by_parish"),
    ("adult_baptisms", "annual_adult_baptisms_by_parish"),
    ("confirmations", "annual_confirmations_by_parish"),
    ("marriages_both_catholic", "annual_marriages_both_catholic_by_parish"),
    ("marriages_mixed_religion", "annual_marriages_mixed_religion_by_parish"),
]


class StatisticsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = StatisticsRepository(db)

    async def submit_parish_report(
        self, data: AnnualStatisticCreate, current_user_id: uuid.UUID | None = None
    ) -> AnnualStatisticResponse:
        await self.repo.lock_parish_reporting_scope(data.parish_id)
        existing = await self.repo.get_by_parish_and_year(data.parish_id, data.report_year)
        previous = (
            {
                field: getattr(existing, field)
                for field in data.model_dump()
                if field not in {"parish_id", "report_year"}
            }
            if existing is not None
            else None
        )
        stat = await self.repo.save_statistic(data)
        current = data.model_dump(exclude={"parish_id", "report_year"})
        changes = {
            key: {"old": previous[key], "new": value}
            for key, value in current.items()
            if previous is not None and previous[key] != value
        }
        record_audit_event(
            self.db,
            user_id=current_user_id,
            action=(
                "PARISH_STATISTIC_CORRECTED"
                if previous is not None
                else "PARISH_STATISTIC_SUBMITTED"
            ),
            entity_name="annual_parish_statistic",
            entity_id=stat.id,
            details={
                "parish_id": str(stat.parish_id),
                "report_year": stat.report_year,
                "is_correction": previous is not None,
                "field_changes": changes,
            },
        )
        return AnnualStatisticResponse.model_validate(stat)

    async def list_parish_reports(
        self, year: int | None = None, parish_ids: list | None = None
    ) -> list[AnnualStatisticResponse]:
        stats = await self.repo.list_statistics(year=year, parish_ids=parish_ids)
        return [AnnualStatisticResponse.model_validate(stat) for stat in stats]

    async def reconcile_parish_report(
        self, parish_id: uuid.UUID, year: int
    ) -> list[ParishReportReconciliation]:
        report = await self.repo.get_by_parish_and_year(parish_id, year)
        register_totals = await self.repo.get_register_totals(parish_id, year)
        submitted = {
            "baptisms": (report.infant_baptisms + report.adult_baptisms) if report else None,
            "confirmations": report.confirmations if report else None,
            "first_communions": report.first_communions if report else None,
            "marriages": (
                (report.marriages_both_catholic + report.marriages_mixed_religion)
                if report
                else None
            ),
            "christian_funerals": report.christian_funerals if report else None,
        }
        reconciliations = []
        for field, register_total in register_totals.items():
            submitted_count = submitted[field]
            difference = (submitted_count - register_total) if submitted_count is not None else None
            status = (
                "NO_RETURN"
                if report is None
                else "MATCH" if submitted_count == register_total else "MISMATCH"
            )
            reconciliations.append(
                ParishReportReconciliation(
                    parish_id=parish_id,
                    report_year=year,
                    field=field,
                    submitted_count=submitted_count,
                    register_count=register_total,
                    difference=difference,
                    status=status,
                )
            )
        return reconciliations

    async def generate_annuario_pontificio(self, year: int) -> AnnuarioPontificioReport:
        """Compose the annual report from configuration-driven indicators.

        ``total_parishes`` / ``total_priests`` remain simple repository
        counts: neither ``Parish`` nor ``Priest`` is itself an indicator
        source (Parish has no ``parish_id``; Priest assignment is tracked via
        ``current_parish_id``/assignments, not a scoped metric column).
        """
        aggregation = AggregationService(self.db)
        archdioceses = await self.repo.list_archdioceses()

        parts: dict[str, float] = {name: 0.0 for name, _key in _ANNUARIO_SOURCES}
        for archdiocese in archdioceses:
            for name, key in _ANNUARIO_SOURCES:
                result = await aggregation.compute(
                    key,
                    archdiocese_id=archdiocese.id,
                    param_filters={"report_year": year},
                )
                parts[name] += sum(float(row.value) for row in result.rows)

        return AnnuarioPontificioReport(
            year=year,
            total_parishes=await self.repo.count_parishes(),
            total_priests=await self.repo.count_active_priests(),
            total_catholics=int(parts["total_catholics"]),
            total_baptisms=int(parts["infant_baptisms"] + parts["adult_baptisms"]),
            total_confirmations=int(parts["confirmations"]),
            total_marriages=int(
                parts["marriages_both_catholic"] + parts["marriages_mixed_religion"]
            ),
        )
