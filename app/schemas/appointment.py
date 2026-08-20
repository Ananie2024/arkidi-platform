"""
Clergy Module Pydantic v2 Schemas
"""
import uuid
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.priest import ClergyType, ClergyStatus


class PriestBase(BaseModel):
    first_name: str
    last_name: str
    title: str = "Padiri"
    clergy_type: ClergyType = ClergyType.DIOCESAN_PRIEST
    status: ClergyStatus = ClergyStatus.ACTIVE_DUTY
    date_of_birth: Optional[date] = None
    ordination_date: Optional[date] = None
    ordaining_bishop: Optional[str] = None
    congregation: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    biography: Optional[str] = None
    current_parish_id: Optional[uuid.UUID] = None
    current_role: Optional[str] = None


class PriestCreate(PriestBase):
    pass


class PriestUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[ClergyStatus] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    biography: Optional[str] = None
    current_parish_id: Optional[uuid.UUID] = None
    current_role: Optional[str] = None


class PriestResponse(PriestBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class AssignmentBase(BaseModel):
    role_title: str
    start_date: date
    end_date: Optional[date] = None
    decree_reference_number: Optional[str] = None
    is_current: bool = True


class AssignmentCreate(AssignmentBase):
    priest_id: uuid.UUID
    parish_id: Optional[uuid.UUID] = None


class AssignmentResponse(AssignmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    priest_id: uuid.UUID
    parish_id: Optional[uuid.UUID] = None
    created_at: datetime
