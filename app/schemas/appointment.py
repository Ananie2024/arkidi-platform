"""
Clergy Module Pydantic v2 Schemas
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.priest import ClergyStatus, ClergyType


class PriestBase(BaseModel):
    first_name: str
    last_name: str
    title: str = "Padiri"
    clergy_type: ClergyType = ClergyType.DIOCESAN_PRIEST
    status: ClergyStatus = ClergyStatus.ACTIVE_DUTY
    date_of_birth: date | None = None
    ordination_date: date | None = None
    ordaining_bishop: str | None = None
    congregation: str | None = None
    phone_number: str | None = None
    email: str | None = None
    biography: str | None = None
    current_parish_id: uuid.UUID | None = None
    current_role: str | None = None


class PriestCreate(PriestBase):
    pass


class PriestUpdate(BaseModel):
    title: str | None = None
    status: ClergyStatus | None = None
    phone_number: str | None = None
    email: str | None = None
    biography: str | None = None
    current_parish_id: uuid.UUID | None = None
    current_role: str | None = None


class PriestResponse(PriestBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class AssignmentBase(BaseModel):
    role_title: str = Field(min_length=1, max_length=100)
    start_date: date
    end_date: date | None = None
    decree_reference_number: str | None = None
    is_current: bool = True

    @model_validator(mode="after")
    def valid_assignment_period(self):
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("Assignment end date must be on or after its start date")
        return self


class AssignmentCreate(AssignmentBase):
    priest_id: uuid.UUID
    parish_id: uuid.UUID | None = None


class AssignmentResponse(AssignmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    priest_id: uuid.UUID
    parish_id: uuid.UUID | None = None
    created_at: datetime
