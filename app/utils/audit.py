"""Shared, transaction-bound audit event creation."""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


def record_audit_event(
    db: AsyncSession,
    *,
    action: str,
    entity_name: str,
    entity_id: uuid.UUID | str | None,
    details: dict[str, Any] | None = None,
    user_id: uuid.UUID | None = None,
) -> AuditLog:
    """Add an audit row to the active transaction using its authenticated actor."""
    if not action or len(action) > 100:
        raise ValueError("Audit action must contain 1 to 100 characters")
    if not entity_name or len(entity_name) > 100:
        raise ValueError("Audit entity_name must contain 1 to 100 characters")

    actor_id = user_id or db.info.get("audit_user_id")
    event = AuditLog(
        user_id=actor_id,
        action=action,
        entity_name=entity_name,
        entity_id=str(entity_id) if entity_id is not None else None,
        details=details or {},
        ip_address=db.info.get("audit_ip_address"),
    )
    db.add(event)
    return event
