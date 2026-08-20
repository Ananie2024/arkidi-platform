"""
Land Assets Module Pydantic v2 Schemas
"""
import uuid
from datetime import date, datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict
from app.models.parcel import LandUseType, TenureStatus


class LandParcelBase(BaseModel):
    upi: str
    parcel_name: str
    title_deed_number: Optional[str] = None
    land_use: LandUseType = LandUseType.CHURCH_COMPOUND
    tenure_status: TenureStatus = TenureStatus.FREEHOLD
    area_sqm: float
    acquisition_date: Optional[date] = None
    estimated_value_rwf: Optional[float] = None
    province: str = "Kigali City"
    district: Optional[str] = None
    sector: Optional[str] = None
    cell: Optional[str] = None
    village: Optional[str] = None
    geojson_geometry: Optional[dict] = None


class LandParcelCreate(LandParcelBase):
    parish_id: uuid.UUID
    deanery_id: Optional[uuid.UUID] = None


class LandParcelResponse(LandParcelBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    deanery_id: Optional[uuid.UUID] = None
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
    construction_year: Optional[int] = None
    floors_count: int = 1
    condition: str = "Good"


class BuildingAssetResponse(BuildingAssetCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
