"""
Tax Record Model — property tax assessments for church land parcels.
"""
import uuid
from datetime import date

from sqlalchemy import String, Date, Numeric, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class TaxRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Annual property tax assessment record for a parcel."""

    __tablename__ = "tax_records"

    parcel_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("land_parcels.id"), nullable=False)
    tax_year: Mapped[int] = mapped_column(nullable=False)
    assessed_value_rwf: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0, nullable=False)
    tax_amount_rwf: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ASSESSED", nullable=False)
    assessment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)