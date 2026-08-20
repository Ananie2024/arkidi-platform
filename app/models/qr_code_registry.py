"""
QR Code Registry Model — certificate & document verification codes.
"""
import uuid
from enum import Enum

from sqlalchemy import String, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class QrCodePurpose(str, Enum):
    CERTIFICATE = "CERTIFICATE"
    DOCUMENT = "DOCUMENT"
    LAND_PARCEL = "LAND_PARCEL"


class QrCodeRegistry(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Registered QR code used for official document / certificate verification."""

    __tablename__ = "qr_code_registry"

    token: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    purpose: Mapped[QrCodePurpose] = mapped_column(
        SQLEnum(QrCodePurpose, name="qr_code_purpose_enum"),
        nullable=False,
    )
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    document_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    certificate_issue_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    parcel_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("land_parcels.id"), nullable=True)
    scanned_count: Mapped[int] = mapped_column(default=0, nullable=False)
    last_scanned_at: Mapped[uuid.UUID | None] = mapped_column(nullable=True)