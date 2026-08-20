"""
Event Model — parish and archdiocesan calendar events.
"""
import uuid
from datetime import date, time
from enum import Enum

from sqlalchemy import String, Date, Time, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class EventType(str, Enum):
    LITURGICAL = "LITURGICAL"            # Fêtes, processions
    PASTORAL = "PASTORAL"                # Catéchèse, retraites
    ADMINISTRATIVE = "ADMINISTRATIVE"    # Réunions, sessions
    SOCIAL = "SOCIAL"                    # Caritas, jeunes, sport
    TRAINING = "TRAINING"                # Formations


class Event(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """A scheduled event at archdiocesan, deanery or parish level."""

    __tablename__ = "events"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    event_type: Mapped[EventType] = mapped_column(
        SQLEnum(EventType, name="event_type_enum"),
        default=EventType.PASTORAL,
        nullable=False,
    )
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    venue: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    organizer_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    archdiocese_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    deanery_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    parish_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=True)