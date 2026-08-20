"""
Finance Module SQLAlchemy Models
"""
import uuid
from datetime import date
from enum import Enum
from sqlalchemy import String, Date, Numeric, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class DonationType(str, Enum):
    TITHE = "TITHE"                    # Dîme / Ituro ry'umuryango
    OFFERTORY = "OFFERTORY"            # Amaturo asanzwe yo mu Misa
    CONSTRUCTION_FUND = "CONSTRUCTION_FUND" # Umusanzu wo kubaka kiliziya
    CARITAS_POOR = "CARITAS_POOR"      # Caritas / Abakene
    SPECIAL_COLLECTION = "SPECIAL_COLLECTION" # Ikoraniro ryihariye
    MASS_STIPEND = "MASS_STIPEND"      # Igitambo cya Misa


class PaymentMethod(str, Enum):
    CASH = "CASH"
    MOMO = "MOMO"                      # MTN Mobile Money / Airtel Money
    BANK_TRANSFER = "BANK_TRANSFER"
    CHECK = "CHECK"


class Donation(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Financial Contribution / Donation Record."""
    __tablename__ = "donations"

    parish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False)
    faithful_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("faithful.id"), nullable=True)
    family_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=True)

    donation_type: Mapped[DonationType] = mapped_column(
        SQLEnum(DonationType, name="donation_type_enum"),
        default=DonationType.TITHE,
        nullable=False,
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        SQLEnum(PaymentMethod, name="payment_method_enum"),
        default=PaymentMethod.CASH,
        nullable=False,
    )

    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="RWF", nullable=False)
    donation_date: Mapped[date] = mapped_column(Date, nullable=False)

    receipt_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    donor_name_override: Mapped[str | None] = mapped_column(String(200), nullable=True)
    reference_transaction_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
