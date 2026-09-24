"""
Backup & Restore-Drill Celery Background Tasks
=============================================

Two periodic tasks, scheduled by ``celery_app.beat_schedule``:

1. ``backup.run_nightly_backup`` (daily, via Celery beat)
   Runs ``scripts/backup.sh`` — local ``pg_dump`` + file-storage tarball —
   and then uploads the artefacts to GCS/B2 via ``scripts/cloud_upload.py``
   for real offsite redundancy.

2. ``backup.run_weekly_restore_drill`` (weekly, via Celery beat)
   Runs ``scripts/restore_drill.sh`` end-to-end and verifies the round-trip.
   Proves the backups are actually restorable – the single most important
   DR control.

Both tasks emit an e-mail alert (via ``app.utils.alerts``) on failure so
recovery-readiness is never silently broken.
"""

import logging
import os
import subprocess

from app.config import settings
from app.tasks.celery_app import celery_app
from app.utils.alerts import send_alert

logger = logging.getLogger("arkidi.tasks.backup")

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scripts")
BACKUP_SH = os.path.join(SCRIPTS_DIR, "backup.sh")
RESTORE_DRILL_SH = os.path.join(SCRIPTS_DIR, "restore_drill.sh")


def _build_env() -> dict:
    """Build a subprocess environment with DB credentials and backup settings.

    The Celery worker container injects DATABASE_* via its own environment,
    but we also need DB_ADMIN_* for the restore drill's PostGIS provisioning.
    backup.sh / restore_drill.sh accept either DB_* or DATABASE_* names;
    we normalise the DATABASE_* settings into DB_* aliases so the legacy
    bash variable names keep working.
    """
    env = os.environ.copy()
    env.setdefault("DB_HOST", settings.DATABASE_HOST)
    env.setdefault("DB_PORT", str(settings.DATABASE_PORT))
    env.setdefault("DB_NAME", settings.DATABASE_NAME)
    env.setdefault("DB_USER", settings.DATABASE_USER)
    env.setdefault("DB_PASSWORD", settings.DATABASE_PASSWORD)
    env.setdefault("DB_ADMIN_USER", settings.effective_admin_user)
    env.setdefault("DB_ADMIN_PASSWORD", settings.effective_admin_password)
    env.setdefault("BACKUP_DIR", settings.BACKUP_BASE_PATH)
    env.setdefault("FILE_STORAGE_PATH", settings.FILE_STORAGE_PATH)
    # Make the app root importable so scripts/cloud_upload.py can import app.config.
    app_root = os.path.dirname(SCRIPTS_DIR)
    python_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{app_root}:{python_path}" if python_path else app_root
    return env


def _run_script(script_path: str, env: dict, label: str) -> dict:
    """Run *script_path* as a subprocess and return a result dict."""
    if not os.path.isfile(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")

    logger.info("[%s] starting: %s", label, script_path)
    result = subprocess.run(
        ["bash", script_path],
        env=env,
        capture_output=True,
        text=True,
        timeout=3600,  # 1 hour hard cap
    )
    stdout_tail = result.stdout[-2000:] if result.stdout else ""
    stderr_tail = result.stderr[-2000:] if result.stderr else ""
    output = {
        "returncode": result.returncode,
        "stdout_tail": stdout_tail,
        "stderr_tail": stderr_tail,
        "script": script_path,
        "label": label,
    }
    if result.returncode != 0:
        logger.error(
            "[%s] FAILED (rc=%d)\nstdout:\n%s\nstderr:\n%s",
            label,
            result.returncode,
            stdout_tail,
            stderr_tail,
        )
    else:
        logger.info("[%s] completed successfully", label)
    return output


@celery_app.task(name="backup.run_nightly_backup", bind=True)
def run_nightly_backup(self) -> dict:
    """Nightly backup: local pg_dump + file-storage tarball + cloud upload.

    Delegates to ``scripts/backup.sh`` (which internally calls
    ``scripts/cloud_upload.py`` for offsite upload).  On failure, an
    alert e-mail is dispatched so operators know the backup chain is broken.
    """
    env = _build_env()
    try:
        result = _run_script(BACKUP_SH, env, "nightly_backup")
        if result["returncode"] != 0:
            _send_failure_alert(
                "Nightly Backup FAILED",
                result,
                task_id=self.request.id if self else None,
            )
        return result
    except Exception as exc:
        logger.exception("[nightly_backup] unhandled exception")
        _send_failure_alert(
            "Nightly Backup FAILED (exception)",
            {"error": str(exc), "script": BACKUP_SH},
            task_id=self.request.id if self else None,
        )
        raise


@celery_app.task(name="backup.run_weekly_restore_drill", bind=True)
def run_weekly_restore_drill(self) -> dict:
    """Weekly end-to-end restore drill.

    Runs ``scripts/restore_drill.sh`` which backs up, creates a scratch DB,
    restores into it, and verifies the round-trip.  On failure an alert is
    sent so recovery-readiness is never silently broken.
    """
    env = _build_env()
    try:
        result = _run_script(RESTORE_DRILL_SH, env, "weekly_restore_drill")
        if result["returncode"] != 0:
            _send_failure_alert(
                "Weekly Restore Drill FAILED",
                result,
                task_id=self.request.id if self else None,
            )
        return result
    except Exception as exc:
        logger.exception("[weekly_restore_drill] unhandled exception")
        _send_failure_alert(
            "Weekly Restore Drill FAILED (exception)",
            {"error": str(exc), "script": RESTORE_DRILL_SH},
            task_id=self.request.id if self else None,
        )
        raise


def _send_failure_alert(subject: str, result: dict, task_id: str | None = None) -> None:
    """Compose and send an e-mail alert for a failed scheduled job."""
    hostname = os.environ.get("HOSTNAME", "unknown")
    body_lines = [
        f"Task: {subject}",
        f"Host: {hostname}",
        f"Task ID: {task_id or 'N/A'}",
        f"Script: {result.get('script', 'N/A')}",
        f"Return code: {result.get('returncode', 'N/A')}",
        "",
        "--- stdout (tail) ---",
        result.get("stdout_tail", "") or "(empty)",
        "",
        "--- stderr (tail) ---",
        result.get("stderr_tail", "") or "(empty)",
        "",
        f"Full error: {result.get('error', 'see stderr above')}",
    ]
    body = "\n".join(body_lines)

    html_body = (
        f"<html><body><h2>{subject}</h2>"
        f"<p><strong>Host:</strong> {hostname}<br>"
        f"<strong>Task ID:</strong> {task_id or 'N/A'}</p>"
        f"<pre>{result.get('stdout_tail', '')}</pre>"
        f"<pre style='color:red'>{result.get('stderr_tail', '')}</pre>"
        f"<pre>{result.get('error', '')}</pre>"
        f"</body></html>"
    )

    sent = send_alert(subject=subject, body=body, html_body=html_body)
    if not sent:
        logger.warning(
            "Alert for '%s' was logged but not sent (SMTP not configured).",
            subject,
        )
