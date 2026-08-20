"""
Faithful Module SQLAlchemy Models
"""
import uuid
from datetime import date
from enum import Enum
from sqlalchemy import String, Date, Boolean, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class CanonicalStatus(str, Enum):
    CATECHUMEN = "CATECHUMEN"                  # Umwigishwa
    BAPTIZED = "BAPTIZED"                      # Umubatizwa
    CONFIRMED = "CONFIRMED"                    # Uwakomejwe
    CANONICAL_MARRIAGE = "CANONICAL_MARRIAGE"  # Usezeranye muri Kiliziya
    CIVIL_ONLY = "CIVIL_ONLY"                  # Usezeranye mu mategeko gusa
    CLERGY_OR_RELIGIOUS = "CLERGY_OR_RELIGIOUS"# Umusaserodoti / Umwihaye Imana
    DECEASED = "DECEASED"                      # Yitabye Imana


class FamilyRole(str, Enum):
    HEAD = "HEAD"
    SPOUSE = "SPOUSE"
    CHILD = "CHILD"
    DEPENDENT = "DEPENDENT"
    OTHER = "OTHER"


class Family(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Household / Umuryango."""
    __tablename__ = "families"

    family_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    family_name: Mapped[str] = mapped_column(String(200), nullable=False)
    parish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False)
    centrale_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("centrales.id"), nullable=True)
    scc_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("small_christian_communities.id"), nullable=True)

    residence_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    members: Mapped[list["Faithful"]] = relationship("Faithful", back_populates="family")


class Faithful(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Individual Parishioner / Faithful (Umukristu)."""
    __tablename__ = "faithful"

    registration_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    christian_name: Mapped[str] = mapped_column(String(100), nullable=False)  # Izina rya batisimu
    gender: Mapped[Gender] = mapped_column(SQLEnum(Gender, name="gender_enum"), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    place_of_birth: Mapped[str | None] = mapped_column(String(150), nullable=True)

    father_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    mother_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    national_id: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(100), nullable=True)

    canonical_status: Mapped[CanonicalStatus] = mapped_column(
        SQLEnum(CanonicalStatus, name="canonical_status_enum"),
        default=CanonicalStatus.BAPTIZED,
        nullable=False,
    )

    # Ecclesiastical assignments
    parish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False)
    family_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=True)
    family_role: Mapped[FamilyRole] = mapped_column(
        SQLEnum(FamilyRole, name="family_role_enum"),
        default=FamilyRole.HEAD,
        nullable=False,
    )
    scc_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("small_christian_communities.id"), nullable=True)

    family: Mapped["Family"] = relationship("Family", back_populates="members")
