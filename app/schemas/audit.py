"""Audit trail response schema."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID | None
    action: str
    entity_name: str
    entity_id: str | None
    details: dict[str, Any] | None
    ip_address: str | None
    created_at: datetime
