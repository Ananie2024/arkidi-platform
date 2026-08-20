"""
Ministries Module Pydantic v2 Schemas
"""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.ministry import MinistryCategory


class MinistryBase(BaseModel):
    name: str
    category: MinistryCategory = MinistryCategory.COMMISSION
    patron_saint: Optional[str] = None
    description: Optional[str] = None
    leader_name: Optional[str] = None
    leader_phone: Optional[str] = None
    meeting_schedule: Optional[str] = None
    is_active: bool = True


class MinistryCreate(MinistryBase):
    parish_id: uuid.UUID


class MinistryResponse(MinistryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    created_at: datetime
