"""
Archive OCR Indexing Background Tasks
Extracts and indexes OCR text from scanned historical ledger pages asynchronously.
"""
import asyncio
import logging

from app.core.database import AsyncSessionLocal
from app.models.document import ScannedPage
from app.tasks.celery_app import celery_app

logger = logging.getLogger("arkidi.tasks.archive_ocr")


@celery_app.task(name="archive.process_ocr_page")
def process_ocr_page(scanned_page_id: str) -> dict:
    """Index OCR text already attached to a scanned canonical ledger page."""
    logger.info("process_ocr_page for scanned page %s", scanned_page_id)

    async def _run() -> dict:
        async with AsyncSessionLocal() as db:
            page = await db.get(ScannedPage, scanned_page_id)
            if page is None:
                return {"scanned_page_id": scanned_page_id, "status": "not_found"}

            text = page.ocr_raw_text or ""
            word_count = len(text.split())
            page.ocr_metadata = {
                **(page.ocr_metadata or {}),
                "indexed": True,
                "text_length": len(text),
                "word_count": word_count,
            }
            await db.commit()
            return {
                "scanned_page_id": scanned_page_id,
                "status": "indexed",
                "text_length": len(text),
                "word_count": word_count,
            }

    return asyncio.run(_run())
