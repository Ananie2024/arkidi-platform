"""
Archive OCR Indexing Background Tasks

Real Tesseract OCR extraction for scanned historical canonical ledger pages.
Each scanned page image is processed asynchronously by a Celery worker so the
digital archive becomes full-text searchable beyond its metadata (the raw
text lands in ``ScannedPage.ocr_raw_text`` and the extraction diagnostics in
``ScannedPage.ocr_metadata``).

The heavy pytesseract calls are blocking system calls, so the task runs them
in a worker thread (``asyncio.to_thread``) instead of the event loop.
"""

import asyncio
import logging
import os
import time

from app.config import settings
from app.core.database import AsyncSessionLocal
from app.models.document import ScannedPage
from app.tasks.celery_app import celery_app
from app.utils.audit import record_audit_event
from app.utils.file_storage import storage_service

logger = logging.getLogger("arkidi.tasks.archive_ocr")


class OcrEngineUnavailableError(RuntimeError):
    """Tesseract binary / python bindings are missing on this worker."""


def extract_ocr_text(image_path: str) -> tuple[str, dict]:
    """Run the Tesseract engine over a page image.

    Returns a ``(raw_text, engine_metadata)`` tuple. The metadata carries the
    engine name, language pack(s), mean word confidence and run duration so
    it can be persisted straight into ``ScannedPage.ocr_metadata``.

    Raises:
        FileNotFoundError: the image file does not exist on disk.
        OcrEngineUnavailableError: pytesseract/Pillow missing or the
            tesseract binary is not installed on the worker.
        pytesseract.TesseractError: the engine failed on this image.
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise OcrEngineUnavailableError(
            "pytesseract/Pillow are not installed on this worker; "
            "install them (requirements.txt) to enable OCR extraction."
        ) from exc

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Scanned page image not found: {image_path}")

    started = time.monotonic()
    try:
        with Image.open(image_path) as image:
            text = pytesseract.image_to_string(
                image,
                lang=settings.OCR_LANGUAGE,
                config=f"--dpi {settings.OCR_DPI}",
                timeout=settings.OCR_TIMEOUT_SECONDS,
            )
            # image_to_data gives per-word confidences; derive the page mean
            # for archivist quality triage. It is best-effort: a failure here
            # must not lose the raw text we already extracted.
            mean_confidence: float | None = None
            try:
                data = pytesseract.image_to_data(
                    image,
                    lang=settings.OCR_LANGUAGE,
                    config=f"--dpi {settings.OCR_DPI}",
                    timeout=settings.OCR_TIMEOUT_SECONDS,
                    output_type=pytesseract.Output.DICT,
                )
                confidences = [int(c) for c in data.get("conf", []) if c not in ("-1", -1)]
                if confidences:
                    mean_confidence = round(sum(confidences) / len(confidences), 2)
            except Exception:  # noqa: BLE001 - diagnostics are optional
                logger.debug("OCR confidence extraction failed", exc_info=True)
    except pytesseract.TesseractNotFoundError as exc:
        raise OcrEngineUnavailableError(
            "The tesseract binary is not installed on this worker. Install "
            "tesseract-ocr (and the tesseract-ocr-<lang> packs matching "
            f"OCR_LANGUAGE='{settings.OCR_LANGUAGE}'."
        ) from exc

    duration_ms = int((time.monotonic() - started) * 1000)
    return text.strip(), {
        "engine": "tesseract",
        "language": settings.OCR_LANGUAGE,
        "image_dpi": settings.OCR_DPI,
        "mean_confidence": mean_confidence,
        "duration_ms": duration_ms,
    }


@celery_app.task(name="archive.process_ocr_page", bind=True, max_retries=5)
def process_ocr_page(task, scanned_page_id: str) -> dict:
    """Extract real OCR text from a scanned canonical ledger page and index it.

    Task statuses (returned to the Celery result backend):

    * ``not_found``           -- the scanned page row no longer exists.
    * ``indexed``             -- Tesseract extracted text; stored + indexed.
    * ``indexed_without_ocr`` -- OCR disabled; only pre-attached text indexed.
    * ``ocr_unavailable``     -- the Tesseract engine is missing on the worker.
    * ``image_not_found``     -- the page image file is missing from storage.
    * ``ocr_failed``          -- the engine errored while reading the image.
    """
    logger.info("process_ocr_page (Tesseract) for scanned page %s", scanned_page_id)

    async def _run() -> dict:
        async with AsyncSessionLocal() as db:
            page = await db.get(ScannedPage, scanned_page_id)
            if page is None:
                return {"scanned_page_id": scanned_page_id, "status": "not_found"}

            # ----------------------------------------------------------------
            # Degraded mode: OCR disabled on this deployment. Fall back to the
            # legacy behaviour -- index whatever text was pre-attached so the
            # existing indexing step stays functional.
            # ----------------------------------------------------------------
            if not settings.OCR_ENABLED:
                text = page.ocr_raw_text or ""
                page.ocr_metadata = {
                    **(page.ocr_metadata or {}),
                    "indexed": True,
                    "status": "indexed_without_ocr",
                    "ocr_engine": "disabled",
                    "text_length": len(text),
                    "word_count": len(text.split()),
                }
                record_audit_event(
                    db,
                    action="ARCHIVE_PAGE_OCR_INDEXED",
                    entity_name="scanned_page",
                    entity_id=page.id,
                    details={"status": "indexed_without_ocr", "text_length": len(text)},
                )
                await db.commit()
                return {
                    "scanned_page_id": scanned_page_id,
                    "status": "indexed_without_ocr",
                    "text_length": len(text),
                    "word_count": len(text.split()),
                }

            image_path = storage_service.get_full_path(page.image_file_path)

            # ----------------------------------------------------------------
            # Run the blocking Tesseract engine in a worker thread so the
            # task's event loop stays responsive.
            # ----------------------------------------------------------------
            try:
                text, engine_meta = await asyncio.to_thread(extract_ocr_text, image_path)
            except OcrEngineUnavailableError as exc:
                logger.error("OCR engine unavailable for page %s: %s", scanned_page_id, exc)
                page.ocr_metadata = {
                    **(page.ocr_metadata or {}),
                    "indexed": False,
                    "status": "ocr_unavailable",
                    "error": "OCR_ENGINE_UNAVAILABLE",
                }
                record_audit_event(
                    db, action="ARCHIVE_PAGE_OCR_FAILED", entity_name="scanned_page",
                    entity_id=page.id, details={"status": "ocr_unavailable"},
                )
                await db.commit()
                return {
                    "scanned_page_id": scanned_page_id,
                    "status": "ocr_unavailable",
                    "error": "OCR_ENGINE_UNAVAILABLE",
                }
            except FileNotFoundError as exc:
                logger.error("OCR image missing for page %s: %s", scanned_page_id, exc)
                page.ocr_metadata = {
                    **(page.ocr_metadata or {}),
                    "indexed": False,
                    "status": "image_not_found",
                    "error": "IMAGE_NOT_FOUND",
                }
                record_audit_event(
                    db, action="ARCHIVE_PAGE_OCR_FAILED", entity_name="scanned_page",
                    entity_id=page.id, details={"status": "image_not_found"},
                )
                await db.commit()
                return {
                    "scanned_page_id": scanned_page_id,
                    "status": "image_not_found",
                    "error": "IMAGE_NOT_FOUND",
                }
            except Exception:  # noqa: BLE001 - pytesseract.TesseractError etc.
                logger.exception("OCR extraction failed for page %s", scanned_page_id)
                page.ocr_metadata = {
                    **(page.ocr_metadata or {}),
                    "indexed": False,
                    "status": "ocr_failed",
                    "error": "OCR_PROCESSING_FAILED",
                }
                record_audit_event(
                    db, action="ARCHIVE_PAGE_OCR_FAILED", entity_name="scanned_page",
                    entity_id=page.id, details={"status": "ocr_failed"},
                )
                await db.commit()
                return {
                    "scanned_page_id": scanned_page_id,
                    "status": "ocr_failed",
                    "error": "OCR_PROCESSING_FAILED",
                }

            # ----------------------------------------------------------------
            # Success: persist the extracted text and merge the extraction
            # diagnostics into the page metadata (the existing indexing step).
            # ----------------------------------------------------------------
            page.ocr_raw_text = text
            page.ocr_metadata = {
                **(page.ocr_metadata or {}),
                "indexed": True,
                "status": "ok",
                "text_length": len(text),
                "word_count": len(text.split()),
                **engine_meta,
            }
            record_audit_event(
                db,
                action="ARCHIVE_PAGE_OCR_INDEXED",
                entity_name="scanned_page",
                entity_id=page.id,
                details={
                    "status": "indexed",
                    "text_length": len(text),
                    "word_count": len(text.split()),
                    "mean_confidence": engine_meta.get("mean_confidence"),
                },
            )
            await db.commit()
            return {
                "scanned_page_id": scanned_page_id,
                "status": "indexed",
                "text_length": len(text),
                "word_count": len(text.split()),
                "mean_confidence": engine_meta.get("mean_confidence"),
            }

    result = asyncio.run(_run())
    # Upload transactions enqueue before the HTTP dependency commits. A worker
    # can win that race, so retry a short-lived missing row instead of dropping
    # the indexing job permanently.
    if result.get("status") == "not_found":
        raise task.retry(countdown=2)
    return result
