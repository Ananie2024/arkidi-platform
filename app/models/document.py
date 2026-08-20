"""
Document Model — the Archdiocesan digital document & archive registry.

Documents may be attached to any organisational entity:
Parish, Deanery, Commission, Council, Meeting, Clergy person, Land parcel, etc.
Also hosts the historical sacramental ledger books and scanned page archive.
"""
import uuid

from sqlalchemy import String, Integer, Text, Enum as SQLEnum, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin
from app.models.sacrament import SacramentType


class Document(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """A single archived document with owner polymorphism across the structure."""

    __tablename__ = "documents"

    __table_args__ = (
        # At least one organisational scoping column must be set, unless the
        # `classification` explicitly allows an unscoped / general document.
        CheckConstraint(
            "archdiocese_id IS NOT NULL OR deanery_id IS NOT NULL OR "
            "parish_id IS NOT NULL OR commission_id IS NOT NULL OR "
            "council_id IS NOT NULL OR meeting_id IS NOT NULL OR "
            "priest_id IS NOT NULL OR parcel_id IS NOT NULL OR "
            "classification IN ('GENERAL', 'DICOESAN', 'CURIA')",
            name="ck_documents_scoping_required",
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
    archdiocese_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("archdioceses.id"), nullable=True)
    deanery_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("deaneries.id"), nullable=True)
    parish_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=True)
    commission_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("commissions.id"), nullable=True)
    council_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("councils.id"), nullable=True)
    meeting_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=True)
    priest_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("priests.id"), nullable=True)
    parcel_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("land_parcels.id"), nullable=True)

    uploaded_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    classification: Mapped[str] = mapped_column(String(50), default="OFFICIAL", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class ArchiveLedgerBook(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Physical Historical Registry Book."""
    __tablename__ = "archive_ledger_books"

    parish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False)
    sacrament_type: Mapped[SacramentType] = mapped_column(
        SQLEnum(SacramentType, name="sacrament_type_archive_enum"),
        nullable=False,
    )
    book_title: Mapped[str] = mapped_column(String(200), nullable=False)
    start_year: Mapped[int] = mapped_column(nullable=False)
    end_year: Mapped[int] = mapped_column(nullable=False)
    volume_number: Mapped[str] = mapped_column(String(20), nullable=False)
    shelf_location: Mapped[str | None] = mapped_column(String(100), nullable=True) # Archival room / Shelf / Box
    total_scanned_pages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class ScannedPage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Individual Digitized Scan of a Canonical Ledger Page."""
    __tablename__ = "archive_scanned_pages"

    ledger_book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("archive_ledger_books.id"), nullable=False
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    image_file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    ocr_raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
