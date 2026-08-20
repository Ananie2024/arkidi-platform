"""
Mass Schedule Pydantic v2 Schemas
"""
import uuid
from datetime import date, time, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MassScheduleBase(BaseModel):
    mass_date: date
    start_time: time
    language: str = "rw"
    celebrant_name: Optional[str] = None
    liturgical_feast: Optional[str] = None


class MassScheduleCreate(MassScheduleBase):
    parish_id: uuid.UUID
    centrale_id: Optional[uuid.UUID] = None


class MassScheduleUpdate(BaseModel):
    mass_date: Optional[date] = None
    start_time: Optional[time] = None
    celebrant_name: Optional[str] = None
    liturgical_feast: Optional[str] = None


class MassScheduleResponse(MassScheduleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    centrale_id: Optional[uuid.UUID] = None
    created_at: datetime
