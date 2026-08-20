"""
Parcel Ownership History Model — auditable record of land title changes.
"""
import uuid
from datetime import date

from sqlalchemy import String, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class ParcelOwnershipHistory(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Historical ownership transfer record for a land parcel."""

    __tablename__ = "parcel_ownership_history"

    parcel_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("land_parcels.id"), nullable=False)
    owner_name: Mapped[str] = mapped_column(String(200), nullable=False)
    owner_type: Mapped[str] = mapped_column(String(50), default="CHURCH", nullable=False)
    ownership_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    ownership_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    transfer_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)