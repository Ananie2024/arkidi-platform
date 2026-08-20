"""
Faithful Module Pydantic v2 Schemas
"""
import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.faithful import Gender, CanonicalStatus, FamilyRole


class FaithfulBase(BaseModel):
    registration_number: str
    first_name: str
    last_name: str
    christian_name: str
    gender: Gender
    date_of_birth: Optional[date] = None
    place_of_birth: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    national_id: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    occupation: Optional[str] = None
    canonical_status: CanonicalStatus = CanonicalStatus.BAPTIZED
    family_role: FamilyRole = FamilyRole.HEAD


class FaithfulCreate(FaithfulBase):
    parish_id: uuid.UUID
    family_id: Optional[uuid.UUID] = None
    scc_id: Optional[uuid.UUID] = None


class FaithfulUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    christian_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    occupation: Optional[str] = None
    canonical_status: Optional[CanonicalStatus] = None
    family_id: Optional[uuid.UUID] = None
    family_role: Optional[FamilyRole] = None
    scc_id: Optional[uuid.UUID] = None


class FaithfulResponse(FaithfulBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    family_id: Optional[uuid.UUID] = None
    scc_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime


class FamilyBase(BaseModel):
    family_code: str
    family_name: str
    residence_address: Optional[str] = None
    phone: Optional[str] = None


class FamilyCreate(FamilyBase):
    parish_id: uuid.UUID
    centrale_id: Optional[uuid.UUID] = None
    scc_id: Optional[uuid.UUID] = None


class FamilyResponse(FamilyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    centrale_id: Optional[uuid.UUID] = None
    scc_id: Optional[uuid.UUID] = None
    created_at: datetime
