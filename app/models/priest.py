"""
Priest / Clergy Model — canonical profile & assignment history.
"""
import uuid
from datetime import date
from enum import Enum

from sqlalchemy import String, Date, Text, Enum as SQLEnum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class ClergyType(str, Enum):
    BISHOP = "BISHOP"
    DIOCESAN_PRIEST = "DIOCESAN_PRIEST"
    RELIGIOUS_PRIEST = "RELIGIOUS_PRIEST"
    PERMANENT_DEACON = "PERMANENT_DEACON"
    TRANSITIONAL_DEACON = "TRANSITIONAL_DEACON"
    RELIGIOUS_BROTHER = "RELIGIOUS_BROTHER"
    RELIGIOUS_SISTER = "RELIGIOUS_SISTER"
    SEMINARIAN = "SEMINARIAN"


class ClergyStatus(str, Enum):
    ACTIVE_DUTY = "ACTIVE_DUTY"
    RETIRED = "RETIRED"
    STUDIES = "STUDIES"
    ON_LEAVE = "ON_LEAVE"
    MISSION_OUTSIDE = "MISSION_OUTSIDE"
    DECEASED = "DECEASED"


class Priest(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Clergy / Priest profile."""

    __tablename__ = "priests"

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(50), default="Padiri", nullable=False)  # Monseigneur, Padiri, Diakoni...
    clergy_type: Mapped[ClergyType] = mapped_column(
        SQLEnum(ClergyType, name="clergy_type_enum"),
        default=ClergyType.DIOCESAN_PRIEST,
        nullable=False,
    )
    status: Mapped[ClergyStatus] = mapped_column(
        SQLEnum(ClergyStatus, name="clergy_status_enum"),
        default=ClergyStatus.ACTIVE_DUTY,
        nullable=False,
    )

    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    ordination_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    ordaining_bishop: Mapped[str | None] = mapped_column(String(200), nullable=True)
    congregation: Mapped[str | None] = mapped_column(String(200), nullable=True)  # E.g. Salesians, White Fathers

    phone_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    biography: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Current assignment
    current_parish_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=True)
    current_role: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Curé, Vicaire, Aumônier, etc.

    assignments: Mapped[list["ClergyAssignment"]] = relationship("ClergyAssignment", back_populates="priest")
    appointments: Mapped[list["Appointment"]] = relationship(  # type: ignore[name-defined]
        "Appointment", back_populates="priest"
    )


class ClergyAssignment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Historical and active diocesan assignments/decrees."""

    __tablename__ = "clergy_assignments"

    priest_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("priests.id"), nullable=False)
    parish_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=True)
    role_title: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    decree_reference_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    priest: Mapped["Priest"] = relationship("Priest", back_populates="assignments")
