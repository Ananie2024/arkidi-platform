"""
Deanery Pydantic v2 Schemas
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DeaneryBase(BaseModel):
    name: str
    code: str
    vicar_forane_name: Optional[str] = None


class DeaneryCreate(DeaneryBase):
    archdiocese_id: uuid.UUID


class DeaneryUpdate(BaseModel):
    name: Optional[str] = None
    vicar_forane_name: Optional[str] = None


class DeaneryResponse(DeaneryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    archdiocese_id: uuid.UUID
    created_at: datetime
