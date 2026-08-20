"""
Mass Intention Model — parishioner-requested Mass intentions (Ibitambo bya Misa).
"""
import uuid
from datetime import date
from enum import Enum

from sqlalchemy import String, Date, Numeric, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class IntentionType(str, Enum):
    REQUIEM = "REQUIEM"                  # Gusabira abitabye Imana / Repos de l'âme
    THANKSGIVING = "THANKSGIVING"        # Gushimira Imana / Action de grâce
    SPECIAL_PETITION = "SPECIAL_PETITION"  # Gusabira uburwayi / Intention particulière


class MassIntention(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Parishioner requested Mass intention with canonical stipend."""

    __tablename__ = "mass_intentions"

    mass_schedule_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mass_schedules.id"), nullable=True
    )
    parish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False)

    requested_by_name: Mapped[str] = mapped_column(String(200), nullable=False)
    requested_by_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    intention_type: Mapped[IntentionType] = mapped_column(
        SQLEnum(IntentionType, name="intention_type_enum"),
        default=IntentionType.THANKSGIVING,
        nullable=False,
    )
    intention_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Canonical Mass stipend offering (Igitambo / Stipendium)
    stipend_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    is_paid: Mapped[bool] = mapped_column(default=True, nullable=False)
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)

    mass_schedule: Mapped["MassSchedule"] = relationship("MassSchedule", back_populates="intentions")  # type: ignore[name-defined]