"""
Parish Pydantic v2 Schemas — Parish, Centrale & Small Christian Communities.
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ParishBase(BaseModel):
    name: str
    code: str
    patron_saint: str | None = None
    establishment_date: date | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    district: str | None = None
    sector: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class ParishCreate(ParishBase):
    deanery_id: uuid.UUID


class ParishUpdate(BaseModel):
    name: str | None = None
    patron_saint: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    district: str | None = None
    sector: str | None = None
    deanery_id: uuid.UUID | None = None


class ParishResponse(ParishBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    deanery_id: uuid.UUID
    created_at: datetime


class CentraleBase(BaseModel):
    name: str
    code: str | None = None
    patron_saint: str | None = None


class CentraleCreate(CentraleBase):
    parish_id: uuid.UUID


class CentraleResponse(CentraleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    created_at: datetime


class SCCBase(BaseModel):
    name: str
    patron_saint: str | None = None
    leader_name: str | None = None
    leader_phone: str | None = None


class SCCCreate(SCCBase):
    centrale_id: uuid.UUID


class SCCResponse(SCCBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    centrale_id: uuid.UUID
    created_at: datetime
