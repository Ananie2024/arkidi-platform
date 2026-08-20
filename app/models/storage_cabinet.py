"""
Storage Cabinet Model — physical drawer/cabinet units in the archives.
"""
import uuid

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class StorageCabinet(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """A physical storage cabinet inside an archival location."""

    __tablename__ = "storage_cabinets"

    cabinet_number: Mapped[str] = mapped_column(String(50), nullable=False)
    drawer_count: Mapped[int] = mapped_column(default=1, nullable=False)
    current_capacity_pct: Mapped[int] = mapped_column(default=0, nullable=False)
    physical_location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("physical_locations.id"), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    physical_location: Mapped["PhysicalLocation"] = relationship(  # type: ignore[name-defined]
        "PhysicalLocation", back_populates="storage_cabinets"
    )