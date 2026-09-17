"""
Document & Archive Module Pydantic v2 Schemas
Covers generic Document/DocumentType registry as well as historical ledger books.
"""
import uuid
from datetime import datetime

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
    description: str | None = Field(default=None, max_length=500)
    category: str = Field(default="GENERAL", max_length=50)
    is_active: bool = True
    retention_years: int | None = Field(
        default=None, ge=0,
        description="Years to retain documents of this type from creation date. Null = indefinite.",
    )
    disposition_action: str | None = Field(
        default=None, max_length=50,
        description="Action when retention expires: DESTROY|TRANSFER|MANUAL_REVIEW|PRESERVE_INDEFINITELY.",
    )

class DocumentTypeCreate(DocumentTypeBase):
    pass

class DocumentTypeUpdate(BaseModel):
    name_en: str | None = Field(default=None, min_length=1, max_length=200)
    name_fr: str | None = Field(default=None, min_length=1, max_length=200)
    name_rw: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    category: str | None = None
    is_active: bool | None = None
    retention_years: int | None = Field(default=None, ge=0)
    disposition_action: str | None = Field(default=None, max_length=50)

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
    document_type_id: uuid.UUID | None = None
    classification: str = Field(default="OFFICIAL", max_length=50)
    notes: str | None = None
    disposition_status: str | None = Field(
        default=None, max_length=50,
        description="ACTIVE|DUE_FOR_REVIEW|DISPOSED|PRESERVE_INDEFINITELY",
    )

    # Organisational hierarchy scoping
    archdiocese_id: uuid.UUID | None = None
    deanery_id: uuid.UUID | None = None
    parish_id: uuid.UUID | None = None
    commission_id: uuid.UUID | None = None
    council_id: uuid.UUID | None = None
    meeting_id: uuid.UUID | None = None
    priest_id: uuid.UUID | None = None
    parcel_id: uuid.UUID | None = None

class DocumentCreate(DocumentBase):
    file_path: str = Field(min_length=1, max_length=500)
    file_size_bytes: int | None = None
    mime_type: str | None = None
    checksum_sha256: str | None = None

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
    title: str | None = Field(default=None, min_length=1, max_length=200)
    document_type_id: uuid.UUID | None = None
    classification: str | None = None
    notes: str | None = None
    disposition_status: str | None = Field(default=None, max_length=50)
    archdiocese_id: uuid.UUID | None = None
    deanery_id: uuid.UUID | None = None
    parish_id: uuid.UUID | None = None
    commission_id: uuid.UUID | None = None
    council_id: uuid.UUID | None = None
    meeting_id: uuid.UUID | None = None
    priest_id: uuid.UUID | None = None
    parcel_id: uuid.UUID | None = None

class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    file_path: str
    file_size_bytes: int | None = None
    mime_type: str | None = None
    checksum_sha256: str | None = None
    uploaded_by_user_id: uuid.UUID | None = None
    retention_flagged_at: datetime | None = None
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
    shelf_location: str | None = None

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
    ocr_raw_text: str | None = None

class ScannedPageResponse(ScannedPageCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
