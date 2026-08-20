"""
Deanery Model — the Archdiocese root and its Deaneries (Doyennés).
"""
import uuid
from datetime import date

from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class Archdiocese(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """The Archdiocese of Kigali — single root of the hierarchical tree."""

    __tablename__ = "archdioceses"

    name: Mapped[str] = mapped_column(String(200), default="Archidiocèse de Kigali", nullable=False)
    canonical_erection_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    patron_saint: Mapped[str | None] = mapped_column(String(100), default="Saint Michel", nullable=True)
    see_city: Mapped[str] = mapped_column(String(100), default="Kigali", nullable=False)

    deaneries: Mapped[list["Deanery"]] = relationship("Deanery", back_populates="archdiocese")


class Deanery(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Deanery / Doyenné (e.g. Doyenné Saint Michel, Sainte Famille, Kicukiro, Nyamata)."""

    __tablename__ = "deaneries"

    archdiocese_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("archdioceses.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    vicar_forane_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    archdiocese: Mapped["Archdiocese"] = relationship("Archdiocese", back_populates="deaneries")
    parishes: Mapped[list["Parish"]] = relationship("Parish", back_populates="deanery")  # type: ignore[name-defined]
