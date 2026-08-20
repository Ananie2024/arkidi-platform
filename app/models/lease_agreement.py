"""
Lease Agreement Model — rental/emphyteutic lease contracts on church land.
"""
import uuid
from datetime import date

from sqlalchemy import String, Date, Numeric, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class LeaseAgreement(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """A signed lease contract for church property or land."""

    __tablename__ = "lease_agreements"

    lease_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    parcel_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("land_parcels.id"), nullable=False)
    lessee_name: Mapped[str] = mapped_column(String(200), nullable=False)
    lessee_contact: Mapped[str | None] = mapped_column(String(200), nullable=True)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    monthly_rent_rwf: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)
    contract_document_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    payments: Mapped[list["LeasePaymentSchedule"]] = relationship(  # type: ignore[name-defined]
        "LeasePaymentSchedule", back_populates="lease_agreement"
    )