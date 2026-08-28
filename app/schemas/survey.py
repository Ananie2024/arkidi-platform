"""
Survey Module Pydantic v2 Schemas
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SurveyStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class QuestionType(str, Enum):
    TEXT = "TEXT"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    SINGLE_CHOICE = "SINGLE_CHOICE"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    RATING = "RATING"
    DATE = "DATE"


class SurveyQuestion(BaseModel):
    id: str = Field(description="Unique question identifier within the survey (e.g. 'q1')")
    question_text: str = Field(min_length=1, max_length=500)
    question_type: QuestionType = QuestionType.TEXT
    options: Optional[List[str]] = Field(default=None, description="Available choices for choice questions")
    required: bool = True
    help_text: Optional[str] = None


class SurveyBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    status: SurveyStatus = SurveyStatus.DRAFT
    questions: List[SurveyQuestion] = Field(default_factory=list)
    archdiocese_id: Optional[uuid.UUID] = None
    deanery_id: Optional[uuid.UUID] = None
    parish_id: Optional[uuid.UUID] = None


class SurveyCreate(SurveyBase):
    pass


class SurveyUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[SurveyStatus] = None
    questions: Optional[List[SurveyQuestion]] = None
    archdiocese_id: Optional[uuid.UUID] = None
    deanery_id: Optional[uuid.UUID] = None
    parish_id: Optional[uuid.UUID] = None


class SurveyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: Optional[str] = None
    status: str
    questions: List[SurveyQuestion] = Field(default_factory=list)
    archdiocese_id: Optional[uuid.UUID] = None
    deanery_id: Optional[uuid.UUID] = None
    parish_id: Optional[uuid.UUID] = None
    response_count: int = 0
    created_at: datetime
    updated_at: datetime


class SurveyAnswerSubmit(BaseModel):
    respondent_name: Optional[str] = None
    respondent_parish_id: Optional[uuid.UUID] = None
    answers: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value mapping of question ID to submitted answer",
    )


class SurveyResponseRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    survey_id: uuid.UUID
    respondent_name: Optional[str] = None
    respondent_parish_id: Optional[uuid.UUID] = None
    submitted_by_user_id: Optional[uuid.UUID] = None
    answers: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class SurveySummaryResponse(BaseModel):
    survey_id: uuid.UUID
    title: str
    total_responses: int
    question_summaries: Dict[str, Any]
