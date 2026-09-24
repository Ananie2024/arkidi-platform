"""
Ministries Module Pydantic v2 Schemas
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.ministry import MinistryCategory


class MinistryBase(BaseModel):
    name: str
    category: MinistryCategory = MinistryCategory.COMMISSION
    patron_saint: str | None = None
    description: str | None = None
    leader_name: str | None = None
    leader_phone: str | None = None
    meeting_schedule: str | None = None
    is_active: bool = True


class MinistryCreate(MinistryBase):
    parish_id: uuid.UUID


class MinistryResponse(MinistryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    created_at: datetime
