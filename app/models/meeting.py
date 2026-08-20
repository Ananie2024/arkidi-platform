"""
Meeting Model — council & commission meetings with agendas and decisions.
"""
import uuid
from datetime import date, time

from sqlalchemy import String, Date, Time, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class Meeting(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """A scheduled meeting of a council, commission or diocesan body."""

    __tablename__ = "meetings"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    meeting_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    venue: Mapped[str | None] = mapped_column(String(200), nullable=True)
    agenda: Mapped[str | None] = mapped_column(Text, nullable=True)
    decisions: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="SCHEDULED", nullable=False)

    council_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("councils.id"), nullable=True)
    commission_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("commissions.id"), nullable=True
    )
    archdiocese_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    deanery_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    parish_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    council: Mapped["Council | None"] = relationship("Council", back_populates="meetings")  # type: ignore[name-defined]
    minutes: Mapped[list["MeetingMinute"]] = relationship("MeetingMinute", back_populates="meeting")  # type: ignore[name-defined]
