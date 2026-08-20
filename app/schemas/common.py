"""
Statistics Module Pydantic v2 Schemas
"""
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class AnnualStatisticBase(BaseModel):
    report_year: int
    total_catholic_population: int = 0
    total_catechumens: int = 0
    total_families: int = 0
    infant_baptisms: int = 0
    adult_baptisms: int = 0
    first_communions: int = 0
    confirmations: int = 0
    marriages_both_catholic: int = 0
    marriages_mixed_religion: int = 0
    christian_funerals: int = 0
    catholic_schools_count: int = 0
    students_count: int = 0
    health_centers_count: int = 0


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
