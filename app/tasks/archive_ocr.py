"""
Archive OCR Indexing Background Tasks
Extracts and indexes OCR text from scanned historical ledger pages asynchronously.
"""
import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger("arkidi.tasks.archive_ocr")


@celery_app.task(name="archive.process_ocr_page")
def process_ocr_page(scanned_page_id: str) -> dict:
    """
    Placeholder task: run OCR extraction on a scanned canonical ledger page.

    Args:
        scanned_page_id: UUID of the ScannedPage record to process.
    """
    logger.info("process_ocr_page for scanned page %s", scanned_page_id)
    return {"scanned_page_id": scanned_page_id, "status": "pending"}