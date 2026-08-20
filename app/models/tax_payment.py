"""
Tax Payment Model — payment installments against a tax record.
"""
import uuid
from datetime import date

from sqlalchemy import String, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class TaxPayment(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """A payment made against an assessed tax record."""

    __tablename__ = "tax_payments"

    tax_record_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tax_records.id"), nullable=False)
    amount_paid_rwf: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(30), default="CASH", nullable=False)
    receipt_number: Mapped[str | None] = mapped_column(String(50), nullable=True)