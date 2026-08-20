"""
Curia & Leadership Appointment Model.
Tracks canonical appointments and terms for the Archbishop, Vicar Generals,
Episcopal Vicars, Chancellor, Économe, Deans, Parish Priests and Secretaries.
"""
import uuid
from datetime import date
from enum import Enum

from sqlalchemy import String, Date, Text, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class AppointmentRole(str, Enum):
    """Official diocesan leadership roles."""

    ARCHBISHOP = "ARCHBISHOP"                # Archevêque
    AUXILIARY_BISHOP = "AUXILIARY_BISHOP"    # Évêque auxiliaire
    VICAR_GENERAL = "VICAR_GENERAL"          # Vicaire général
    EPISCOPAL_VICAR = "EPISCOPAL_VICAR"      # Vicaire épiscopal
    CHANCELLOR = "CHANCELLOR"                # Chancelier de la Curie
    VICE_CHANCELLOR = "VICE_CHANCELLOR"      # Vice-chancelier
    ECONOMO = "ECONOMO"                      # Économe diocésain
    DEAN = "DEAN"                            # Curé de doyenné / Vicaire forain
    PARISH_PRIEST = "PARISH_PRIEST"          # Curé de paroisse
    PARISH_VICAR = "PARISH_VICAR"            # Vicaire paroissial
    PARISH_SECRETARY = "PARISH_SECRETARY"    # Secrétaire paroissial


class AppointmentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"
    SUSPENDED = "SUSPENDED"


class Appointment(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """A curia / parish leadership appointment with defined term dates."""

    __tablename__ = "appointments"

    person_first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    person_last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Monseigneur, Abbé, Padiri...
    photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)

    role: Mapped[AppointmentRole] = mapped_column(
        SQLEnum(AppointmentRole, name="appointment_role_enum"),
        nullable=False,
    )
    status: Mapped[AppointmentStatus] = mapped_column(
        SQLEnum(AppointmentStatus, name="appointment_status_enum"),
        default=AppointmentStatus.ACTIVE,
        nullable=False,
    )

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    decree_reference_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Optional scoping to the ecclesiastical structure
    archdiocese_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    deanery_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    parish_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Linked user account (for role-based access)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)

    # Optional canonical register of the linked Priest profile
    priest_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("priests.id"), nullable=True)

    priest: Mapped["Priest | None"] = relationship("Priest", back_populates="appointments")  # type: ignore[name-defined]
