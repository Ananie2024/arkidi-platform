"""
Statistics Module Business Logic Service

The Annuario Pontificio report is composed from configuration-driven
indicator computations (ADR 002) — no hand-written aggregation SQL.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.survey import StatisticsRepository
from app.schemas.common import (
    AnnualStatisticCreate,
    AnnualStatisticResponse,
    AnnuarioPontificioReport,
)
from app.services.indicators import AggregationService

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

    async def submit_parish_report(self, data: AnnualStatisticCreate) -> AnnualStatisticResponse:
        stat = await self.repo.save_statistic(data)
        return AnnualStatisticResponse.model_validate(stat)

    async def list_parish_reports(self, year: int | None = None) -> list[AnnualStatisticResponse]:
        stats = await self.repo.list_statistics(year=year)
        return [AnnualStatisticResponse.model_validate(stat) for stat in stats]

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
