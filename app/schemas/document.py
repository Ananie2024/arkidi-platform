"""
Document & Archive Module Pydantic v2 Schemas
Covers generic Document/DocumentType registry as well as historical ledger books.
"""
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.sacrament import SacramentType


# ---------------------------------------------------------------------------
# Document Type Schemas
# ---------------------------------------------------------------------------

class DocumentTypeBase(BaseModel):
    code: str = Field(min_length=1, max_length=50, description="Unique alphanumeric code (e.g. 'DECREE_OFFICIAL')")
    name_en: str = Field(min_length=1, max_length=200)
    name_fr: str = Field(min_length=1, max_length=200)
    name_rw: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    category: str = Field(default="GENERAL", max_length=50)
    is_active: bool = True


class DocumentTypeCreate(DocumentTypeBase):
    pass


class DocumentTypeUpdate(BaseModel):
    name_en: Optional[str] = Field(default=None, min_length=1, max_length=200)
    name_fr: Optional[str] = Field(default=None, min_length=1, max_length=200)
    name_rw: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class DocumentTypeResponse(DocumentTypeBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Generic Document Schemas
# ---------------------------------------------------------------------------

class DocumentBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    document_type_id: Optional[uuid.UUID] = None
    classification: str = Field(default="OFFICIAL", max_length=50)
    notes: Optional[str] = None

    # Organisational hierarchy scoping
    archdiocese_id: Optional[uuid.UUID] = None
    deanery_id: Optional[uuid.UUID] = None
    parish_id: Optional[uuid.UUID] = None
    commission_id: Optional[uuid.UUID] = None
    council_id: Optional[uuid.UUID] = None
    meeting_id: Optional[uuid.UUID] = None
    priest_id: Optional[uuid.UUID] = None
    parcel_id: Optional[uuid.UUID] = None


class DocumentCreate(DocumentBase):
    file_path: str = Field(min_length=1, max_length=500)
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    checksum_sha256: Optional[str] = None

    @model_validator(mode="after")
    def check_at_least_one_scope(self) -> "DocumentCreate":
        scopes = [
            self.archdiocese_id,
            self.deanery_id,
            self.parish_id,
            self.commission_id,
            self.council_id,
            self.meeting_id,
            self.priest_id,
            self.parcel_id,
        ]
        if not any(scopes):
            raise ValueError(
                "At least one organisational scoping identifier must be provided "
                "(archdiocese_id, deanery_id, parish_id, commission_id, council_id, meeting_id, priest_id, or parcel_id)."
            )
        return self


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    document_type_id: Optional[uuid.UUID] = None
    classification: Optional[str] = None
    notes: Optional[str] = None
    archdiocese_id: Optional[uuid.UUID] = None
    deanery_id: Optional[uuid.UUID] = None
    parish_id: Optional[uuid.UUID] = None
    commission_id: Optional[uuid.UUID] = None
    council_id: Optional[uuid.UUID] = None
    meeting_id: Optional[uuid.UUID] = None
    priest_id: Optional[uuid.UUID] = None
    parcel_id: Optional[uuid.UUID] = None


class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    file_path: str
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    checksum_sha256: Optional[str] = None
    uploaded_by_user_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Historical Canonical Ledger Book Archive Schemas
# ---------------------------------------------------------------------------

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
