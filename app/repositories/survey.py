"""
Statistics Module Database Repository
"""
import uuid
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.survey import AnnualParishStatistic
from app.schemas.common import AnnualStatisticCreate


class StatisticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_parish_and_year(self, parish_id: uuid.UUID, year: int) -> Optional[AnnualParishStatistic]:
        stmt = select(AnnualParishStatistic).where(
            AnnualParishStatistic.parish_id == parish_id,
            AnnualParishStatistic.report_year == year,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def save_statistic(self, data: AnnualStatisticCreate) -> AnnualParishStatistic:
        stat = AnnualParishStatistic(**data.model_dump())
        self.db.add(stat)
        await self.db.flush()
        return stat

    async def get_archdiocesan_totals(self, year: int) -> dict:
        stmt = select(
            func.sum(AnnualParishStatistic.total_catholic_population).label("catholics"),
            func.sum(AnnualParishStatistic.infant_baptisms + AnnualParishStatistic.adult_baptisms).label("baptisms"),
            func.sum(AnnualParishStatistic.confirmations).label("confirmations"),
            func.sum(AnnualParishStatistic.marriages_both_catholic + AnnualParishStatistic.marriages_mixed_religion).label("marriages"),
        ).where(AnnualParishStatistic.report_year == year)

        result = await self.db.execute(stmt)
        row = result.first()
        if row:
            return {
                "catholics": int(row[0] or 0),
                "baptisms": int(row[1] or 0),
                "confirmations": int(row[2] or 0),
                "marriages": int(row[3] or 0),
            }
        return {"catholics": 0, "baptisms": 0, "confirmations": 0, "marriages": 0}
