"""
Arkidi Platform - Background Task Package
Celery tasks for long-running, asynchronous operations:
certificate generation, statistical reports, archive OCR indexing.
"""
from app.tasks import certificates, reports, archive_ocr  # noqa: F401

__all__ = ["certificates", "reports", "archive_ocr"]