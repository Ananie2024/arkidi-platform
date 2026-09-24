"""
Lease Payment Schedule Model — planned & received lease rent installments.
"""

import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class LeasePaymentSchedule(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """A scheduled lease installment with payment status."""

    __tablename__ = "lease_payment_schedule"

    lease_agreement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lease_agreements.id"), nullable=False
    )
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount_rwf: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    paid_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    receipt_number: Mapped[str | None] = mapped_column(String(50), nullable=True)

    lease_agreement: Mapped["LeaseAgreement"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "LeaseAgreement", back_populates="payments"
    )
