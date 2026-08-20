"""
Ministries Module SQLAlchemy Models
"""
import uuid
from enum import Enum
from sqlalchemy import String, Text, Enum as SQLEnum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class MinistryCategory(str, Enum):
    COMMISSION = "COMMISSION"        # E.g. Liturgie, Catéchèse, Caritas, Justice et Paix
    CHOIR = "CHOIR"                  # Korali
    ECCLESIAL_MOVEMENT = "ECCLESIAL_MOVEMENT" # Légion de Marie, Renouveau Charismatique, Xavéri
    COUNCIL = "COUNCIL"              # Conseil Pastoral Paroissial (CPP), Conseil pour les Affaires Économiques (CPAE)
    YOUTH_GUILD = "YOUTH_GUILD"      # Urubyiruko Gatolika


class Ministry(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Pastoral Ministry, Commission or Lay Movement."""
    __tablename__ = "ministries"

    parish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[MinistryCategory] = mapped_column(
        SQLEnum(MinistryCategory, name="ministry_category_enum"),
        default=MinistryCategory.COMMISSION,
        nullable=False,
    )
    patron_saint: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    leader_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    leader_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    meeting_schedule: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
