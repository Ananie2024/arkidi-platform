"""
Certificate Generation Background Tasks
Renders sacramental certificate PDFs (with verification QR) and persists them
to the file store for batch/offline workflows.

The synchronous Celery task wraps an async coroutine (mirroring the reports
task pattern) because the app's SQLAlchemy engine is asynchronous.
"""

import asyncio
import logging
import os
import uuid

from app.config import settings
from app.core.database import AsyncSessionLocal
from app.repositories.sacrament import SacramentsRepository
from app.services.sacrament import SACRAMENT_DISPLAY_NAMES
from app.tasks.celery_app import celery_app
from app.utils.pdf import generate_certificate_pdf
from app.utils.qr import generate_qr_code_bytes

logger = logging.getLogger("arkidi.tasks.certificates")


async def render_certificate_batch(certificate_ids: list[str]) -> dict:
    """Asynchronous core: render and persist certificate PDFs for *certificate_ids*.

    PDFs are written to ``<FILE_STORAGE_PATH>/certificates/<cert_number>.pdf``.
    Returns ``{"generated": N, "failed": [...], "certificate_ids": [...],
    "output_directory": ...}``.
    """
    logger.info("render_certificate_batch received %d certificate(s)", len(certificate_ids))
    cert_dir = os.path.join(settings.FILE_STORAGE_PATH, "certificates")
    os.makedirs(cert_dir, exist_ok=True)

    generated, failed = 0, []
    async with AsyncSessionLocal() as db:
        repo = SacramentsRepository(db)
        for cert_id in certificate_ids:
            try:
                issue = await repo.get_certificate_by_id(uuid.UUID(cert_id))
                if not issue:
                    failed.append(cert_id)
                    continue

                faithful = await repo.get_faithful_by_id(issue.faithful_id)
                parish = await repo.get_parish_by_id(issue.parish_id)

                if faithful:
                    recipient = (
                        f"{faithful.first_name} {faithful.last_name} ({faithful.christian_name})"
                    )
                else:
                    recipient = "Registered Faithful"

                title = SACRAMENT_DISPLAY_NAMES.get(issue.sacrament_type, "Sacramental Certificate")
                details = {
                    "Sacrament": issue.sacrament_type.value.replace("_", " ").title(),
                    "Parish": parish.name if parish else "",
                }
                pdf = generate_certificate_pdf(
                    title=title,
                    recipient=recipient,
                    details=details,
                    issued_at=issue.created_at,
                    certificate_number=issue.certificate_number,
                    qr_image_bytes=generate_qr_code_bytes(issue.qr_code_payload),
                    verification_url=issue.qr_code_payload,
                )
                out_path = os.path.join(cert_dir, f"{issue.certificate_number}.pdf")
                with open(out_path, "wb") as handle:
                    handle.write(pdf)
                generated += 1
            except Exception as exc:  # noqa: BLE001 - report and continue
                logger.warning("Failed to render certificate %s: %s", cert_id, exc)
                failed.append(cert_id)

    logger.info("render_certificate_batch: generated=%d failed=%d", generated, len(failed))
    return {
        "generated": generated,
        "failed": failed,
        "certificate_ids": certificate_ids,
        "output_directory": cert_dir,
    }


@celery_app.task(name="certificates.generate_batch")
def generate_certificate_batch(certificate_ids: list[str]) -> dict:
    """Celery entry point for batch certificate PDF rendering.

    The wrapper uses ``asyncio.run`` because Celery workers run this task on a
    plain synchronous thread; callers already inside an event loop (e.g.
    pytest-asyncio integration tests) should await
    ``render_certificate_batch`` directly.
    """
    return asyncio.run(render_certificate_batch(certificate_ids))
