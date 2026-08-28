"""
Celery Distributed Task Queue Configuration
"""
from celery import Celery
from celery.schedules import crontab
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
    task_acks_late=True,
    task_default_queue="default",
    task_default_exchange="arkidi",
    task_default_routing_key="default",
    # Auto-discover registered background tasks
    imports=(
        "app.tasks.certificates",
        "app.tasks.reports",
        "app.tasks.archive_ocr",
        "app.tasks.archive_retention",
        "app.tasks.backups",
    ),
)

# ------------------------------------------------------------------
# Periodic task schedule (Celery Beat)
# ------------------------------------------------------------------
# All scheduled jobs live here so that a single celery-beat process is the
# source of truth for cron-like automation.  The celery-beat container runs
# this schedule with no additional cron infrastructure needed.
#
# Timezone is Africa/Kigali (UTC+2).  All times below are local to that zone.
celery_app.conf.beat_schedule = {
    # -- Retention & Disposition Review --------------------------------
    # Runs weekdays at 02:00.  Flags documents whose DocumentType
    # retention_years deadline has elapsed and sets disposition_status =
    # DUE_FOR_REVIEW so archivists know which records need manual
    # disposition action.
    "archive_retention.flag_documents_due_for_review": {
        "task": "archive_retention.flag_documents_due_for_review",
        "schedule": crontab(hour=2, minute=0, day_of_week="mon-fri"),
        "options": {"queue": "archive"},
    },
    # -- Nightly Backup (local + cloud) --------------------------------
    # Runs daily at 01:30.  backup.sh produces a pg_dump + file-storage
    # tarball and then uploads to GCS/B2 via scripts/cloud_upload.py.
    "backup.run_nightly_backup": {
        "task": "backup.run_nightly_backup",
        "schedule": crontab(hour=1, minute=30),
        "options": {"queue": "archive"},
    },
    # -- Weekly Restore Drill ------------------------------------------
    # Runs every Sunday at 03:30.  Proves the backup chain is actually
    # restorable by round-tripping a backup into a scratch database.
    # On failure, an e-mail alert is dispatched (see app/utils/alerts.py).
    "backup.run_weekly_restore_drill": {
        "task": "backup.run_weekly_restore_drill",
        "schedule": crontab(hour=3, minute=30, day_of_week="sun"),
        "options": {"queue": "archive"},
    },
}


