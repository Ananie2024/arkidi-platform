"""
Mass Schedule Pydantic v2 Schemas
"""

import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict


class MassScheduleBase(BaseModel):
    mass_date: date
    start_time: time
    language: str = "rw"
    celebrant_name: str | None = None
    liturgical_feast: str | None = None


class MassScheduleCreate(MassScheduleBase):
    parish_id: uuid.UUID
    centrale_id: uuid.UUID | None = None


class MassScheduleUpdate(BaseModel):
    mass_date: date | None = None
    start_time: time | None = None
    celebrant_name: str | None = None
    liturgical_feast: str | None = None


class MassScheduleResponse(MassScheduleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    centrale_id: uuid.UUID | None = None
    created_at: datetime
