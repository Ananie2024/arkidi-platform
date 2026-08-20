"""
Commission Model — pastoral commissions & apostolate bodies:
Family, Education, Youth, Liturgy, Caritas/Social, Vocations, Communications...
"""
import uuid
from enum import Enum

from sqlalchemy import String, Text, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class CommissionCategory(str, Enum):
    FAMILY = "FAMILY"                # Commission de la Famille
    EDUCATION = "EDUCATION"          # Commission de l'Éducation
    YOUTH = "YOUTH"                  # Commission des Jeunes
    LITURGY = "LITURGY"              # Commission de la Liturgie
    CARITAS_SOCIAL = "CARITAS_SOCIAL"  # Caritas / Pastorale sociale
    VOCATIONS = "VOCATIONS"          # Pastorale des vocations
    COMMUNICATIONS = "COMMUNICATIONS"  # Communication sociale
    JUSTICE_PEACE = "JUSTICE_PEACE"  # Justice et Paix
    HEALTH = "HEALTH"                # Pastorale de la santé
    OTHER = "OTHER"


class Commission(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """A diocesan or parish pastoral commission."""

    __tablename__ = "commissions"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[CommissionCategory] = mapped_column(
        SQLEnum(CommissionCategory, name="commission_category_enum"),
        default=CommissionCategory.OTHER,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    patron_saint: Mapped[str | None] = mapped_column(String(100), nullable=True)

    archdiocese_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    deanery_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    parish_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=True)

    leader_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    leader_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    meeting_schedule: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
