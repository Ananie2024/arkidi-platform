"""
Deanery Pydantic v2 Schemas
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DeaneryBase(BaseModel):
    name: str
    code: str
    vicar_forane_name: str | None = None


class DeaneryCreate(DeaneryBase):
    archdiocese_id: uuid.UUID


class DeaneryUpdate(BaseModel):
    name: str | None = None
    vicar_forane_name: str | None = None


class DeaneryResponse(DeaneryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    archdiocese_id: uuid.UUID
    created_at: datetime
