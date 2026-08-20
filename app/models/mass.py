"""
Mass Schedule Model — scheduled Masses in parishes and centrales.
"""
import uuid
from datetime import date, time

from sqlalchemy import String, Date, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class MassSchedule(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Scheduled Mass in a Parish or Centrale."""

    __tablename__ = "mass_schedules"

    parish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False)
    centrale_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("centrales.id"), nullable=True)

    mass_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    language: Mapped[str] = mapped_column(String(20), default="rw", nullable=False)  # rw, fr, en
    celebrant_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    liturgical_feast: Mapped[str | None] = mapped_column(String(150), nullable=True)

    intentions: Mapped[list["MassIntention"]] = relationship(  # type: ignore[name-defined]
        "MassIntention", back_populates="mass_schedule"
    )
