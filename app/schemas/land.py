"""
Land Assets Module Pydantic v2 Schemas
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.parcel import LandUseType, TenureStatus


class LandParcelBase(BaseModel):
    upi: str
    parcel_name: str
    title_deed_number: str | None = None
    land_use: LandUseType = LandUseType.CHURCH_COMPOUND
    tenure_status: TenureStatus = TenureStatus.FREEHOLD
    area_sqm: float
    acquisition_date: date | None = None
    estimated_value_rwf: float | None = None
    province: str = "Kigali City"
    district: str | None = None
    sector: str | None = None
    cell: str | None = None
    village: str | None = None
    geojson_geometry: dict | None = None


class LandParcelCreate(LandParcelBase):
    parish_id: uuid.UUID
    deanery_id: uuid.UUID | None = None


class LandParcelUpdate(BaseModel):
    upi: str | None = None
    parcel_name: str | None = None
    title_deed_number: str | None = None
    land_use: LandUseType | None = None
    tenure_status: TenureStatus | None = None
    area_sqm: float | None = None
    acquisition_date: date | None = None
    estimated_value_rwf: float | None = None
    province: str | None = None
    district: str | None = None
    sector: str | None = None
    cell: str | None = None
    village: str | None = None
    parish_id: uuid.UUID | None = None
    deanery_id: uuid.UUID | None = None
    geojson_geometry: dict | None = None


class LandParcelResponse(LandParcelBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    deanery_id: uuid.UUID | None = None
    created_at: datetime


class LandDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parcel_id: uuid.UUID
    title: str
    document_type: str
    file_path: str
    created_at: datetime


class BuildingAssetCreate(BaseModel):
    parcel_id: uuid.UUID
    name: str
    building_type: str = "Church Building"
    construction_year: int | None = None
    floors_count: int = 1
    condition: str = "Good"


class BuildingAssetResponse(BuildingAssetCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
