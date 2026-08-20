"""
Parish Pydantic v2 Schemas — Parish, Centrale & Small Christian Communities.
"""
import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ParishBase(BaseModel):
    name: str
    code: str
    patron_saint: Optional[str] = None
    establishment_date: Optional[date] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    sector: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ParishCreate(ParishBase):
    deanery_id: uuid.UUID


class ParishUpdate(BaseModel):
    name: Optional[str] = None
    patron_saint: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    sector: Optional[str] = None
    deanery_id: Optional[uuid.UUID] = None


class ParishResponse(ParishBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    deanery_id: uuid.UUID
    created_at: datetime


class CentraleBase(BaseModel):
    name: str
    code: Optional[str] = None
    patron_saint: Optional[str] = None


class CentraleCreate(CentraleBase):
    parish_id: uuid.UUID


class CentraleResponse(CentraleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    created_at: datetime


class SCCBase(BaseModel):
    name: str
    patron_saint: Optional[str] = None
    leader_name: Optional[str] = None
    leader_phone: Optional[str] = None


class SCCCreate(SCCBase):
    centrale_id: uuid.UUID


class SCCResponse(SCCBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    centrale_id: uuid.UUID
    created_at: datetime