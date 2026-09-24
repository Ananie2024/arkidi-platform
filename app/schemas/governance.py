"""
Governance Module Pydantic v2 Schemas
Commissions, Councils, Meetings, and Meeting Minutes
"""

import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from app.models.commission import CommissionCategory
from app.models.council import CouncilType

# ---------------------------------------------------------------------------
# Commission Schemas
# ---------------------------------------------------------------------------


class CommissionBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: CommissionCategory = CommissionCategory.OTHER
    description: str | None = None
    patron_saint: str | None = None
    archdiocese_id: uuid.UUID | None = None
    deanery_id: uuid.UUID | None = None
    parish_id: uuid.UUID | None = None
    leader_name: str | None = None
    leader_phone: str | None = None
    meeting_schedule: str | None = None
    is_active: bool = True


class CommissionCreate(CommissionBase):
    pass


class CommissionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    category: CommissionCategory | None = None
    description: str | None = None
    patron_saint: str | None = None
    archdiocese_id: uuid.UUID | None = None
    deanery_id: uuid.UUID | None = None
    parish_id: uuid.UUID | None = None
    leader_name: str | None = None
    leader_phone: str | None = None
    meeting_schedule: str | None = None
    is_active: bool | None = None


class CommissionResponse(CommissionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Council Schemas
# ---------------------------------------------------------------------------


class CouncilBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    council_type: CouncilType = CouncilType.DIOCESAN_PASTORAL
    description: str | None = None
    archdiocese_id: uuid.UUID | None = None
    deanery_id: uuid.UUID | None = None
    parish_id: uuid.UUID | None = None
    president_name: str | None = None
    convener_user_id: uuid.UUID | None = None
    is_active: bool = True


class CouncilCreate(CouncilBase):
    pass


class CouncilUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    council_type: CouncilType | None = None
    description: str | None = None
    archdiocese_id: uuid.UUID | None = None
    deanery_id: uuid.UUID | None = None
    parish_id: uuid.UUID | None = None
    president_name: str | None = None
    convener_user_id: uuid.UUID | None = None
    is_active: bool | None = None


class CouncilResponse(CouncilBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Meeting Schemas
# ---------------------------------------------------------------------------


class MeetingBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    meeting_date: date
    start_time: time | None = None
    end_time: time | None = None
    venue: str | None = None
    agenda: str | None = None
    decisions: str | None = None
    status: str = Field(default="SCHEDULED", max_length=30)
    council_id: uuid.UUID | None = None
    commission_id: uuid.UUID | None = None
    archdiocese_id: uuid.UUID | None = None
    deanery_id: uuid.UUID | None = None
    parish_id: uuid.UUID | None = None


class MeetingCreate(MeetingBase):
    pass


class MeetingUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    meeting_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    venue: str | None = None
    agenda: str | None = None
    decisions: str | None = None
    status: str | None = None
    council_id: uuid.UUID | None = None
    commission_id: uuid.UUID | None = None
    archdiocese_id: uuid.UUID | None = None
    deanery_id: uuid.UUID | None = None
    parish_id: uuid.UUID | None = None


class MeetingResponse(MeetingBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Meeting Minute Schemas
# ---------------------------------------------------------------------------


class MeetingMinuteBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str | None = None
    document_path: str | None = None


class MeetingMinuteCreate(MeetingMinuteBase):
    meeting_id: uuid.UUID


class MeetingMinuteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = None
    document_path: str | None = None


class MeetingMinuteResponse(MeetingMinuteBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    meeting_id: uuid.UUID
    recorded_by_user_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
