"""
Meeting Minute Model — attachments & official minutes of a meeting.
"""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MeetingMinute(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Official minutes or decision record attached to a meeting."""

    __tablename__ = "meeting_minutes"

    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_path: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )  # Attached minutes/report file
    recorded_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="minutes")  # type: ignore[name-defined]  # noqa: F821
