"""
Sacraments Module SQLAlchemy Models
Official Catholic Sacramental Registers and Canonical Records
"""
import uuid
from datetime import date
from enum import Enum
from sqlalchemy import String, Date, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class SacramentType(str, Enum):
    BAPTISM = "BAPTISM"
    FIRST_COMMUNION = "FIRST_COMMUNION"
    CONFIRMATION = "CONFIRMATION"
    MATRIMONY = "MATRIMONY"
    HOLY_ORDERS = "HOLY_ORDERS"
    RELIGIOUS_PROFESSION = "RELIGIOUS_PROFESSION"
    ANOINTING_OF_THE_SICK = "ANOINTING_OF_THE_SICK"
    CHRISTIAN_FUNERAL = "CHRISTIAN_FUNERAL"


class BaptismRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Canonical Baptism Register (Registre des Baptêmes)."""
    __tablename__ = "baptism_records"

    parish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False)
    faithful_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("faithful.id"), nullable=False)

    # Canonical registry reference
    registry_year: Mapped[int] = mapped_column(nullable=False)
    volume_number: Mapped[str] = mapped_column(String(20), nullable=False)
    page_number: Mapped[str] = mapped_column(String(20), nullable=False)
    act_number: Mapped[str] = mapped_column(String(50), nullable=False)

    celebration_date: Mapped[date] = mapped_column(Date, nullable=False)
    minister_name: Mapped[str] = mapped_column(String(200), nullable=False)

    godfather_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    godmother_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Canonical marginal notes (Adnotatio marginalis for confirmation, marriage, Holy Orders)
    marginal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class ConfirmationRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Canonical Confirmation Register (Registre des Confirmations)."""
    __tablename__ = "confirmation_records"

    parish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False)
    faithful_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("faithful.id"), nullable=False)

    registry_year: Mapped[int] = mapped_column(nullable=False)
    volume_number: Mapped[str] = mapped_column(String(20), nullable=False)
    page_number: Mapped[str] = mapped_column(String(20), nullable=False)
    act_number: Mapped[str] = mapped_column(String(50), nullable=False)

    celebration_date: Mapped[date] = mapped_column(Date, nullable=False)
    administering_bishop_or_vicar: Mapped[str] = mapped_column(String(200), nullable=False)
    sponsor_name: Mapped[str | None] = mapped_column(String(200), nullable=True)


class MatrimonyRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Canonical Marriage Register (Registre des Mariages)."""
    __tablename__ = "matrimony_records"

    parish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False)
    groom_faithful_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("faithful.id"), nullable=False)
    bride_faithful_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("faithful.id"), nullable=False)

    registry_year: Mapped[int] = mapped_column(nullable=False)
    volume_number: Mapped[str] = mapped_column(String(20), nullable=False)
    page_number: Mapped[str] = mapped_column(String(20), nullable=False)
    act_number: Mapped[str] = mapped_column(String(50), nullable=False)

    celebration_date: Mapped[date] = mapped_column(Date, nullable=False)
    priest_celebrant: Mapped[str] = mapped_column(String(200), nullable=False)

    witness_1_name: Mapped[str] = mapped_column(String(200), nullable=False)
    witness_2_name: Mapped[str] = mapped_column(String(200), nullable=False)

    dispensations_or_canonical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class FirstCommunionRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Canonical First Communion Register (Registre des Premières Communions)."""
    __tablename__ = "first_communion_records"

    parish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False)
    faithful_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("faithful.id"), nullable=False)

    registry_year: Mapped[int] = mapped_column(nullable=False)
    volume_number: Mapped[str] = mapped_column(String(20), nullable=False)
    page_number: Mapped[str] = mapped_column(String(20), nullable=False)
    act_number: Mapped[str] = mapped_column(String(50), nullable=False)

    celebration_date: Mapped[date] = mapped_column(Date, nullable=False)
    celebrant_name: Mapped[str] = mapped_column(String(200), nullable=False)
    catechetical_program_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    sponsor_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    marginal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class HolyOrdersOrderType(str, Enum):
    DIACONATE = "DIACONATE"
    PRIESTHOOD = "PRIESTHOOD"
    EPISCOPATE = "EPISCOPATE"


class HolyOrdersRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Canonical Holy Orders Register (Registre des Ordinations)."""
    __tablename__ = "holy_orders_records"

    parish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False)
    ordained_faithful_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("faithful.id"), nullable=False)

    register_book: Mapped[str] = mapped_column(String(20), default="Ordinations", nullable=False)
    page_number: Mapped[str] = mapped_column(String(20), nullable=False)
    act_number: Mapped[str] = mapped_column(String(50), nullable=False)

    ordination_date: Mapped[date] = mapped_column(Date, nullable=False)
    order_type: Mapped[HolyOrdersOrderType] = mapped_column(
        SQLEnum(HolyOrdersOrderType, name="holy_orders_order_type_enum"),
        nullable=False,
    )
    ordaining_prelate: Mapped[str] = mapped_column(String(200), nullable=False)
    diocese_of_incardination: Mapped[str | None] = mapped_column(String(200), nullable=True)
    permanent: Mapped[bool] = mapped_column(default=True, nullable=False)
    marginal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class ReligiousProfessionType(str, Enum):
    TEMPORARY_VOWS = "TEMPORARY_VOWS"
    PERPETUAL_VOWS = "PERPETUAL_VOWS"


class ReligiousProfessionRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Canonical Religious Profession Register (Registre des Professions Religieuses)."""
    __tablename__ = "religious_profession_records"

    parish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False)
    professed_faithful_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("faithful.id"), nullable=False)

    register_book: Mapped[str] = mapped_column(String(20), default="Religious Professions", nullable=False)
    page_number: Mapped[str] = mapped_column(String(20), nullable=False)
    act_number: Mapped[str] = mapped_column(String(50), nullable=False)

    profession_date: Mapped[date] = mapped_column(Date, nullable=False)
    profession_type: Mapped[ReligiousProfessionType] = mapped_column(
        SQLEnum(ReligiousProfessionType, name="religious_profession_type_enum"),
        nullable=False,
    )
    congregation_or_institute: Mapped[str] = mapped_column(String(200), nullable=False)
    superior_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    marginal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class AnointingOfTheSickRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Pastoral Register for the Anointing of the Sick (Registre des Onctions)."""
    __tablename__ = "anointing_of_the_sick_records"

    parish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False)
    faithful_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("faithful.id"), nullable=False)

    anointing_date: Mapped[date] = mapped_column(Date, nullable=False)
    minister_name: Mapped[str] = mapped_column(String(200), nullable=False)
    place_of_anointing: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class ChristianFuneralRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Canonical Register of Christian Funerals & Burials (Registre des Sépultures)."""
    __tablename__ = "christian_funeral_records"

    parish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False)
    deceased_faithful_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("faithful.id"), nullable=False)

    date_of_death: Mapped[date] = mapped_column(Date, nullable=False)
    funeral_date: Mapped[date] = mapped_column(Date, nullable=False)
    burial_site: Mapped[str | None] = mapped_column(String(200), nullable=True)
    officiating_priest: Mapped[str] = mapped_column(String(200), nullable=False)
    last_sacraments_received: Mapped[bool] = mapped_column(default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class CertificateIssue(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Issued Sacramental Certificates with QR verification codes."""
    __tablename__ = "certificate_issues"

    certificate_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    sacrament_type: Mapped[SacramentType] = mapped_column(
        SQLEnum(SacramentType, name="sacrament_type_enum"),
        nullable=False,
    )
    faithful_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("faithful.id"), nullable=False)
    parish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False)
    issued_by_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    verification_token: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    qr_code_payload: Mapped[str] = mapped_column(Text, nullable=False)
