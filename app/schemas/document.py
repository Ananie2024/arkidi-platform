"""
Archive Module Pydantic v2 Schemas
"""
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.sacrament import SacramentType


class ArchiveLedgerBookBase(BaseModel):
    sacrament_type: SacramentType
    book_title: str
    start_year: int
    end_year: int
    volume_number: str
    shelf_location: Optional[str] = None


class ArchiveLedgerBookCreate(ArchiveLedgerBookBase):
    parish_id: uuid.UUID


class ArchiveLedgerBookResponse(ArchiveLedgerBookBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parish_id: uuid.UUID
    total_scanned_pages: int
    created_at: datetime


class ScannedPageCreate(BaseModel):
    ledger_book_id: uuid.UUID
    page_number: int
    image_file_path: str
    ocr_raw_text: Optional[str] = None


class ScannedPageResponse(ScannedPageCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
