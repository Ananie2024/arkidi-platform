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

# Intentionally empty for now: the periodic statistics/report schedules belong to
# the aggregation work that is out of scope for this remediation pass. Keeping the
# key defined (even empty) lets the celery-beat service start cleanly and signals
# where new schedulers should be registered.
celery_app.conf.beat_schedule = {}
