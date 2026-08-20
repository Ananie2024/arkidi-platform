"""
Mass Intention Pydantic v2 Schemas
"""
import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.intention import IntentionType


class MassIntentionBase(BaseModel):
    requested_by_name: str
    requested_by_phone: Optional[str] = None
    intention_type: IntentionType = IntentionType.THANKSGIVING
    intention_text: str
    stipend_amount: float = 2000.0
    scheduled_date: date
    is_paid: bool = True


class MassIntentionCreate(MassIntentionBase):
    parish_id: uuid.UUID
    mass_schedule_id: Optional[uuid.UUID] = None


class MassIntentionUpdate(BaseModel):
    mass_schedule_id: Optional[uuid.UUID] = None
    is_paid: Optional[bool] = None
    stipend_amount: Optional[float] = None


class MassIntentionResponse(MassIntentionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    mass_schedule_id: Optional[uuid.UUID] = None
    created_at: datetime