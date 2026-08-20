"""
Council Model — official diocesan consultative & governing bodies:
Diocesan Pastoral Council, Presbyterium, College of Consulters,
Economic Affairs Council.
"""
import uuid
from enum import Enum

from sqlalchemy import String, Text, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class CouncilType(str, Enum):
    DIOCESAN_PASTORAL = "DIOCESAN_PASTORAL"    # Conseil Pastoral Diocésain
    PRESBYTERIUM = "PRESBYTERIUM"              # Presbyterium / Conseil presbytéral
    COLLEGE_OF_CONSULTERS = "COLLEGE_OF_CONSULTERS"  # Collège des consulteurs
    ECONOMIC_AFFAIRS = "ECONOMIC_AFFAIRS"      # Conseil pour les affaires économiques
    PARISH_PASTORAL = "PARISH_PASTORAL"        # Conseil Pastoral Paroissial (CPP)
    PARISH_ECONOMIC = "PARISH_ECONOMIC"        # Conseil pour les affaires économiques paroissial


class Council(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """A diocesan or parish council body."""

    __tablename__ = "councils"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    council_type: Mapped[CouncilType] = mapped_column(
        SQLEnum(CouncilType, name="council_type_enum"),
        default=CouncilType.DIOCESAN_PASTORAL,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    archdiocese_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    deanery_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    parish_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=True)

    president_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    convener_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    meetings: Mapped[list["Meeting"]] = relationship("Meeting", back_populates="council")  # type: ignore[name-defined]
