"""
Statistics Module Pydantic v2 Schemas
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnnualStatisticBase(BaseModel):
    report_year: int = Field(ge=1900, le=2200)
    total_catholic_population: int = Field(default=0, ge=0)
    total_catechumens: int = Field(default=0, ge=0)
    total_families: int = Field(default=0, ge=0)
    infant_baptisms: int = Field(default=0, ge=0)
    adult_baptisms: int = Field(default=0, ge=0)
    first_communions: int = Field(default=0, ge=0)
    confirmations: int = Field(default=0, ge=0)
    marriages_both_catholic: int = Field(default=0, ge=0)
    marriages_mixed_religion: int = Field(default=0, ge=0)
    christian_funerals: int = Field(default=0, ge=0)
    catholic_schools_count: int = Field(default=0, ge=0)
    students_count: int = Field(default=0, ge=0)
    health_centers_count: int = Field(default=0, ge=0)


class AnnualStatisticCreate(AnnualStatisticBase):
    parish_id: uuid.UUID


class AnnualStatisticResponse(AnnualStatisticBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    created_at: datetime


class AnnuarioPontificioReport(BaseModel):
    year: int
    total_parishes: int
    total_priests: int
    total_catholics: int
    total_baptisms: int
    total_confirmations: int
    total_marriages: int


class ParishReportReconciliation(BaseModel):
    parish_id: uuid.UUID
    report_year: int
    field: str
    submitted_count: int | None
    register_count: int
    difference: int | None
    status: str
