"""
Survey Module Pydantic v2 Schemas
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

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
    options: list[str] | None = Field(
        default=None, description="Available choices for choice questions"
    )
    required: bool = True
    help_text: str | None = None


class SurveyBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: SurveyStatus = SurveyStatus.DRAFT
    questions: list[SurveyQuestion] = Field(default_factory=list)
    archdiocese_id: uuid.UUID | None = None
    deanery_id: uuid.UUID | None = None
    parish_id: uuid.UUID | None = None


class SurveyCreate(SurveyBase):
    pass


class SurveyUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: SurveyStatus | None = None
    questions: list[SurveyQuestion] | None = None
    archdiocese_id: uuid.UUID | None = None
    deanery_id: uuid.UUID | None = None
    parish_id: uuid.UUID | None = None


class SurveyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None = None
    status: str
    questions: list[SurveyQuestion] = Field(default_factory=list)
    archdiocese_id: uuid.UUID | None = None
    deanery_id: uuid.UUID | None = None
    parish_id: uuid.UUID | None = None
    response_count: int = 0
    created_at: datetime
    updated_at: datetime


class SurveyAnswerSubmit(BaseModel):
    respondent_name: str | None = None
    respondent_parish_id: uuid.UUID | None = None
    answers: dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value mapping of question ID to submitted answer",
    )


class SurveyResponseRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    survey_id: uuid.UUID
    respondent_name: str | None = None
    respondent_parish_id: uuid.UUID | None = None
    submitted_by_user_id: uuid.UUID | None = None
    answers: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class SurveySummaryResponse(BaseModel):
    survey_id: uuid.UUID
    title: str
    total_responses: int
    question_summaries: dict[str, Any]
