"""
Governance Module Pydantic v2 Schemas
Commissions, Councils, Meetings, and Meeting Minutes
"""
import uuid
from datetime import date, time, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.models.commission import CommissionCategory
from app.models.council import CouncilType


# ---------------------------------------------------------------------------
# Commission Schemas
# ---------------------------------------------------------------------------

class CommissionBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: CommissionCategory = CommissionCategory.OTHER
    description: Optional[str] = None
    patron_saint: Optional[str] = None
    archdiocese_id: Optional[uuid.UUID] = None
    deanery_id: Optional[uuid.UUID] = None
    parish_id: Optional[uuid.UUID] = None
    leader_name: Optional[str] = None
    leader_phone: Optional[str] = None
    meeting_schedule: Optional[str] = None
    is_active: bool = True


class CommissionCreate(CommissionBase):
    pass


class CommissionUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    category: Optional[CommissionCategory] = None
    description: Optional[str] = None
    patron_saint: Optional[str] = None
    archdiocese_id: Optional[uuid.UUID] = None
    deanery_id: Optional[uuid.UUID] = None
    parish_id: Optional[uuid.UUID] = None
    leader_name: Optional[str] = None
    leader_phone: Optional[str] = None
    meeting_schedule: Optional[str] = None
    is_active: Optional[bool] = None


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
    description: Optional[str] = None
    archdiocese_id: Optional[uuid.UUID] = None
    deanery_id: Optional[uuid.UUID] = None
    parish_id: Optional[uuid.UUID] = None
    president_name: Optional[str] = None
    convener_user_id: Optional[uuid.UUID] = None
    is_active: bool = True


class CouncilCreate(CouncilBase):
    pass


class CouncilUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    council_type: Optional[CouncilType] = None
    description: Optional[str] = None
    archdiocese_id: Optional[uuid.UUID] = None
    deanery_id: Optional[uuid.UUID] = None
    parish_id: Optional[uuid.UUID] = None
    president_name: Optional[str] = None
    convener_user_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None


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
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    venue: Optional[str] = None
    agenda: Optional[str] = None
    decisions: Optional[str] = None
    status: str = Field(default="SCHEDULED", max_length=30)
    council_id: Optional[uuid.UUID] = None
    commission_id: Optional[uuid.UUID] = None
    archdiocese_id: Optional[uuid.UUID] = None
    deanery_id: Optional[uuid.UUID] = None
    parish_id: Optional[uuid.UUID] = None


class MeetingCreate(MeetingBase):
    pass


class MeetingUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    meeting_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    venue: Optional[str] = None
    agenda: Optional[str] = None
    decisions: Optional[str] = None
    status: Optional[str] = None
    council_id: Optional[uuid.UUID] = None
    commission_id: Optional[uuid.UUID] = None
    archdiocese_id: Optional[uuid.UUID] = None
    deanery_id: Optional[uuid.UUID] = None
    parish_id: Optional[uuid.UUID] = None


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
    content: Optional[str] = None
    document_path: Optional[str] = None


class MeetingMinuteCreate(MeetingMinuteBase):
    meeting_id: uuid.UUID


class MeetingMinuteUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    content: Optional[str] = None
    document_path: Optional[str] = None


class MeetingMinuteResponse(MeetingMinuteBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    meeting_id: uuid.UUID
    recorded_by_user_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
