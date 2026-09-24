"""
Faithful Module Pydantic v2 Schemas
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.faithful import CanonicalStatus, FamilyRole, Gender


class FaithfulBase(BaseModel):
    registration_number: str
    first_name: str
    last_name: str
    christian_name: str
    gender: Gender
    date_of_birth: date | None = None
    place_of_birth: str | None = None
    father_name: str | None = None
    mother_name: str | None = None
    national_id: str | None = None
    phone_number: str | None = None
    email: str | None = None
    occupation: str | None = None
    canonical_status: CanonicalStatus = CanonicalStatus.BAPTIZED
    family_role: FamilyRole = FamilyRole.HEAD


class FaithfulCreate(FaithfulBase):
    parish_id: uuid.UUID
    family_id: uuid.UUID | None = None
    scc_id: uuid.UUID | None = None


class FaithfulUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    christian_name: str | None = None
    phone_number: str | None = None
    email: str | None = None
    occupation: str | None = None
    canonical_status: CanonicalStatus | None = None
    family_id: uuid.UUID | None = None
    family_role: FamilyRole | None = None
    scc_id: uuid.UUID | None = None


class FaithfulResponse(FaithfulBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    family_id: uuid.UUID | None = None
    scc_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class FamilyBase(BaseModel):
    family_code: str
    family_name: str
    residence_address: str | None = None
    phone: str | None = None


class FamilyCreate(FamilyBase):
    parish_id: uuid.UUID
    centrale_id: uuid.UUID | None = None
    scc_id: uuid.UUID | None = None


class FamilyResponse(FamilyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    centrale_id: uuid.UUID | None = None
    scc_id: uuid.UUID | None = None
    created_at: datetime
