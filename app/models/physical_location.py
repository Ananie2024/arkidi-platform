"""
Physical Location Model — physical archival storage locations.
"""
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class PhysicalLocation(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """A physical archival location (room, shelf, box, cabinet)."""

    __tablename__ = "physical_locations"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    location_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    building: Mapped[str | None] = mapped_column(String(200), nullable=True)
    room: Mapped[str | None] = mapped_column(String(100), nullable=True)
    shelf: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(nullable=True)

    parish_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=True)

    storage_cabinets: Mapped[list["StorageCabinet"]] = relationship(  # type: ignore[name-defined]
        "StorageCabinet", back_populates="physical_location"
    )