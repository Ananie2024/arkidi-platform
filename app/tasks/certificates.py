"""
Certificate Generation Background Tasks
Renders sacramental certificate PDFs and stores verification QR codes asynchronously.
"""
import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger("arkidi.tasks.certificates")


@celery_app.task(name="certificates.generate_batch")
def generate_certificate_batch(certificate_ids: list[str]) -> dict:
    """
    Placeholder task: batch-generate sacramental certificate PDFs for the given IDs.

    Args:
        certificate_ids: list of CertificateIssue UUIDs to render.
    """
    logger.info("generate_certificate_batch received %d certificate(s)", len(certificate_ids))
    return {"generated": 0, "certificate_ids": certificate_ids}