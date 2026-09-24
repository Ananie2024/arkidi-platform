"""
Document Model — the Archdiocesan digital document & archive registry.

Documents may be attached to any organisational entity:
Parish, Deanery, Commission, Council, Meeting, Clergy person, Land parcel, etc.
Also hosts the historical sacramental ledger books and scanned page archive.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.sacrament import SacramentType


class Document(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """A single archived document with owner polymorphism across the structure."""

    __tablename__ = "documents"

    __table_args__ = (
        # Every document must be scoped to at least one organisational entity.
        # We deliberately do NOT offer a classification-based escape hatch here:
        # Document.classification is a free-form String (default "OFFICIAL") with
        # no taxonomy defined yet, so any allow-list would silently reject the
        # default. Until a real classification enum exists, this constraint just
        # guarantees the scoping FK columns are populated.
        CheckConstraint(
            "archdiocese_id IS NOT NULL OR deanery_id IS NOT NULL OR "
            "parish_id IS NOT NULL OR commission_id IS NOT NULL OR "
            "council_id IS NOT NULL OR meeting_id IS NOT NULL OR "
            "priest_id IS NOT NULL OR parcel_id IS NOT NULL",
            name="ck_documents_scoping_required",
        ),
        # disposition_status is constrained to a known set of states tracked
        # by the retention / archivist-review scheduler (see
        # app.tasks.archive_retention).
        CheckConstraint(
            "disposition_status IS NULL OR disposition_status IN "
            "('ACTIVE', 'DUE_FOR_REVIEW', 'DISPOSED', 'PRESERVE_INDEFINITELY')",
            name="ck_documents_disposition_status",
        ),
        # Archive integrity: the same byte content may only ever be registered
        # once. Soft-deleted rows are excluded so re-archiving after a deletion
        # stays possible (the unique key applies to the active document set).
        Index(
            "uq_documents_checksum_active",
            "checksum_sha256",
            unique=True,
            postgresql_where=text("checksum_sha256 IS NOT NULL AND is_deleted = false"),
        ),
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    document_type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("document_types.id"), nullable=True
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Soft hierarchy scoping — one (or several) of these may be set
    archdiocese_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("archdioceses.id"), nullable=True
    )
    deanery_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deaneries.id"), nullable=True
    )
    parish_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=True
    )
    commission_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("commissions.id"), nullable=True
    )
    council_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("councils.id"), nullable=True
    )
    meeting_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=True
    )
    priest_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("priests.id"), nullable=True
    )
    parcel_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("land_parcels.id"), nullable=True
    )

    uploaded_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    classification: Mapped[str] = mapped_column(String(50), default="OFFICIAL", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ------------------------------------------------------------------
    # Retention & Disposition Scheduling
    # ------------------------------------------------------------------
    # retention_flagged_at is set by app.tasks.archive_retention when the
    # document's DocumentType.retention_years deadline has passed, signalling
    # an archivist that the document is due for manual disposition review.
    retention_flagged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # disposition_status tracks where a document sits in its retention lifecycle.
    # Valid values are constrained by ck_documents_disposition_status above.
    disposition_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        default="ACTIVE",
        comment="ACTIVE|DUE_FOR_REVIEW|DISPOSED|PRESERVE_INDEFINITELY",
    )


class ArchiveLedgerBook(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Physical Historical Registry Book."""

    __tablename__ = "archive_ledger_books"

    __table_args__ = (
        # A physical canonical ledger book is uniquely identified by its parish,
        # sacrament type and volume number. Soft-deleted rows are excluded so
        # a book can be re-registered after an archival cleanup.
        Index(
            "uq_ledger_book_parish_volume",
            "parish_id",
            "sacrament_type",
            "volume_number",
            unique=True,
            postgresql_where=text("is_deleted = false"),
        ),
    )

    parish_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False
    )
    sacrament_type: Mapped[SacramentType] = mapped_column(
        SQLEnum(SacramentType, name="sacrament_type_archive_enum"),
        nullable=False,
    )
    book_title: Mapped[str] = mapped_column(String(200), nullable=False)
    start_year: Mapped[int] = mapped_column(nullable=False)
    end_year: Mapped[int] = mapped_column(nullable=False)
    volume_number: Mapped[str] = mapped_column(String(20), nullable=False)
    shelf_location: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # Archival room / Shelf / Box
    total_scanned_pages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class ScannedPage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Individual Digitized Scan of a Canonical Ledger Page."""

    __tablename__ = "archive_scanned_pages"

    __table_args__ = (
        # Each page of a given ledger book may be scanned exactly once.
        UniqueConstraint("ledger_book_id", "page_number", name="uq_scanned_page_book_page"),
    )

    ledger_book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("archive_ledger_books.id"), nullable=False
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    image_file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    ocr_raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
