"""
Failure-Alert Delivery Utility

Sends e-mail alerts when Celery-managed scheduled jobs (nightly backup,
weekly restore-drill, retention review) fail.  Uses the stdlib ``smtplib``
so no additional dependencies are required.

Configuration comes from ``app.config.settings`` (see ``.env.example``):

* ``SMTP_SERVER`` / ``SMTP_PORT`` / ``SMTP_USER`` / ``SMTP_PASSWORD``
* ``SMTP_USE_TLS``
* ``EMAIL_SENDER``  (return path)
* ``ALERT_RECIPIENTS`` (comma-separated list, defaults to ``EMAIL_SENDER``)

When SMTP is not configured (no ``SMTP_SERVER``), alerts are logged as a
warning instead of being sent, so the tasks never crash purely because
e-mail is unconfigured in a dev environment.
"""

import logging
import os
import smtplib
import ssl
from email.message import EmailMessage

from app.config import settings

logger = logging.getLogger("arkidi.utils.alerts")

_ALERT_RECIPIENTS_ENV = "ALERT_RECIPIENTS"


def _recipients() -> list[str]:
    raw = os.environ.get(_ALERT_RECIPIENTS_ENV, "").strip()
    if not raw:
        # Fall back to SMTP_USER (the authenticated account) or EMAIL_SENDER.
        fallback = settings.SMTP_USER or settings.EMAIL_SENDER
        return [fallback] if fallback else []
    return [addr.strip() for addr in raw.split(",") if addr.strip()]


def _smtp_configured() -> bool:
    return bool(settings.SMTP_SERVER)


def _smtp_server() -> str:
    """Return the configured SMTP host as a non-optional ``str``.

    Callers reach this only after ``_smtp_configured()`` returned true, so the
    assertion never fires in practice — it exists purely to narrow the
    ``str | None`` from settings for the type checker.
    """
    server = settings.SMTP_SERVER
    assert server is not None, "SMTP_SERVER must be configured before sending"
    return server


def send_alert(
    subject: str,
    body: str,
    recipients: list[str] | None = None,
    html_body: str | None = None,
) -> bool:
    """Send an alert e-mail.

    Returns ``True`` if the e-mail was sent successfully, ``False`` if
    SMTP is not configured (the alert was logged instead).
    """
    if not _smtp_configured():
        logger.warning(
            "SMTP not configured (no SMTP_SERVER). Alert would have been sent:\n"
            "  Subject: %s\n  Body: %s",
            subject,
            body,
        )
        return False

    if recipients is None:
        recipients = _recipients()
    if not recipients:
        logger.warning(
            "No alert recipients configured. Alert would have been sent:\n"
            "  Subject: %s\n  Body: %s",
            subject,
            body,
        )
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_SENDER or (settings.SMTP_USER or "arkidi-alerts@localhost")
    msg["To"] = ", ".join(recipients)
    msg.set_content(body, subtype="plain")
    if html_body:
        msg.add_alternative(html_body, subtype="html")

    try:
        ctx = ssl.create_default_context() if settings.SMTP_USE_TLS else None
        if settings.SMTP_PORT in (465, 587) or settings.SMTP_USE_TLS:
            server = smtplib.SMTP(_smtp_server(), settings.SMTP_PORT, timeout=30)
            if settings.SMTP_USE_TLS:
                server.starttls(context=ctx)
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
        else:
            server = smtplib.SMTP(_smtp_server(), settings.SMTP_PORT, timeout=30)
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
        logger.info("Alert e-mail sent: %s -> %s", subject, recipients)
        return True
    except Exception as exc:  # noqa: BLE001 — alerts must never crash the task
        logger.error("Failed to send alert e-mail '%s': %s", subject, exc)
        return False


def send_email_message(
    to: str,
    subject: str,
    body: str,
    html_body: str | None = None,
) -> bool:
    """Send a transactional e-mail to a single recipient (e.g. password reset).

    Mirrors the alert-sending machinery (``smtplib`` + TLS + optional login)
    but targets the explicit ``to`` address instead of the configured alert list,
    so user-facing e-mails (password resets) can be delivered directly ath.
    Returns ``True`` when the e-mail was sent, ``False`` when SMTP was not
    configured or sending failed (the attempt is logged accordingly).
    """
    if not _smtp_configured():
        logger.warning(
            "SMTP not configured (no SMTP_SERVER). E-mail would have been sent:\n"
            "  To: %s\n  Subject: %s\n  Body: %s",
            to,
            subject,
            body,
        )
        return False
    if not to:
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_SENDER or (settings.SMTP_USER or "noreply@archidiocesekigali.org")
    msg["To"] = to
    msg.set_content(body, subtype="plain")
    if html_body:
        msg.add_alternative(html_body, subtype="html")

    try:
        server = smtplib.SMTP(_smtp_server(), settings.SMTP_PORT, timeout=30)
        if settings.SMTP_USE_TLS:
            ctx = ssl.create_default_context()
            server.starttls(context=ctx)
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info("E-mail sent: %s -> %s", subject, to)
        return True
    except Exception as exc:  # noqa: BLE001 — e-mail must never crash the request
        logger.error("Failed to send e-mail '%s' to %s: %s", subject, to, exc)
        return False
