"""
Statistical Report Generation Background Tasks
Builds annual diocesan statistical returns (Annuario Pontificio extracts) asynchronously.
"""
import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger("arkidi.tasks.reports")


@celery_app.task(name="reports.generate_annuario_pontificio")
def generate_annuario_pontificio(year: int) -> dict:
    """
    Placeholder task: assemble the annual statistical report for the Holy See.

    Args:
        year: reporting year.
    """
    logger.info("generate_annuario_pontificio for year %s", year)
    return {"year": year, "status": "pending"}