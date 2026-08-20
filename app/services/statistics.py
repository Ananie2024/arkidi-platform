"""
Statistics Module Business Logic Service
"""
import uuid
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

    async def generate_annuario_pontificio(self, year: int) -> AnnuarioPontificioReport:
        totals = await self.repo.get_archdiocesan_totals(year)
        return AnnuarioPontificioReport(
            year=year,
            total_parishes=34, # Current parishes count in Archdiocese of Kigali
            total_priests=178,
            total_catholics=totals["catholics"],
            total_baptisms=totals["baptisms"],
            total_confirmations=totals["confirmations"],
            total_marriages=totals["marriages"],
        )
