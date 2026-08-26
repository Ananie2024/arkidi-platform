"""
Statistical Report Generation Background Tasks
Builds annual diocesan statistical returns (Annuario Pontificio extracts) asynchronously.
"""
import asyncio
import logging

from app.core.database import AsyncSessionLocal
from app.services.statistics import StatisticsService
from app.tasks.celery_app import celery_app

logger = logging.getLogger("arkidi.tasks.reports")


@celery_app.task(name="reports.generate_annuario_pontificio")
def generate_annuario_pontificio(year: int) -> dict:
    """Assemble the annual statistical report for the Holy See."""
    logger.info("generate_annuario_pontificio for year %s", year)

    async def _run() -> dict:
        async with AsyncSessionLocal() as db:
            report = await StatisticsService(db).generate_annuario_pontificio(year)
            return report.model_dump()

    return asyncio.run(_run())
