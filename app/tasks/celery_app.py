"""
Celery Distributed Task Queue Configuration
"""
from celery import Celery
from app.config import settings

celery_app = Celery(
    "arkidi_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Kigali",
    enable_utc=True,
    task_track_started=True,
    # Auto-discover registered background tasks
    imports=(
        "app.tasks.certificates",
        "app.tasks.reports",
        "app.tasks.archive_ocr",
    ),
)
