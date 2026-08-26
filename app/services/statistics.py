"""
Statistics Module Business Logic Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.survey import StatisticsRepository
from app.schemas.common import (
    AnnualStatisticCreate,
    AnnualStatisticResponse,
    AnnuarioPontificioReport,
)


class StatisticsService:
    def __init__(self, db: AsyncSession):
        self.repo = StatisticsRepository(db)

    async def submit_parish_report(self, data: AnnualStatisticCreate) -> AnnualStatisticResponse:
        stat = await self.repo.save_statistic(data)
        return AnnualStatisticResponse.model_validate(stat)

    async def list_parish_reports(self, year: int | None = None) -> list[AnnualStatisticResponse]:
        stats = await self.repo.list_statistics(year=year)
        return [AnnualStatisticResponse.model_validate(stat) for stat in stats]

    async def generate_annuario_pontificio(self, year: int) -> AnnuarioPontificioReport:
        totals = await self.repo.get_archdiocesan_totals(year)
        return AnnuarioPontificioReport(
            year=year,
            total_parishes=await self.repo.count_parishes(),
            total_priests=await self.repo.count_active_priests(),
            total_catholics=totals["catholics"],
            total_baptisms=totals["baptisms"],
            total_confirmations=totals["confirmations"],
            total_marriages=totals["marriages"],
        )
