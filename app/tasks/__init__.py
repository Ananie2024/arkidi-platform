"""
Arkidi Platform - Background Task Package
Celery tasks for long-running, asynchronous operations:
certificate generation, statistical reports, archive OCR indexing,
retention / disposition review, and backup / restore-drill automation.
"""

from app.tasks import (
    archive_ocr,
    archive_retention,
    backups,
    certificates,
    reports,
)

__all__ = [
    "certificates",
    "reports",
    "archive_ocr",
    "archive_retention",
    "backups",
]
