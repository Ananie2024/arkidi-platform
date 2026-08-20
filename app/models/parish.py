"""
Parish Structure Models — Parish, Centrale (sub-parish) and
Small Christian Communities (CEB / Imiryango-remezo).
"""
import uuid
from datetime import date

from sqlalchemy import String, Date, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class Parish(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Parish / Paroisse."""

    __tablename__ = "parishes"

    deanery_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deaneries.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    patron_saint: Mapped[str | None] = mapped_column(String(150), nullable=True)
    establishment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Civil administrative location in Rwanda
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # GIS Location Point (SRID 4326)
    location = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)

    deanery: Mapped["Deanery"] = relationship("Deanery", back_populates="parishes")  # type: ignore[name-defined]
    centrales: Mapped[list["Centrale"]] = relationship("Centrale", back_populates="parish")


class Centrale(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Sub-parish / Succursale / Centrale."""

    __tablename__ = "centrales"

    parish_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[str | None] = mapped_column(String(30), nullable=True)
    patron_saint: Mapped[str | None] = mapped_column(String(150), nullable=True)

    location = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)

    parish: Mapped["Parish"] = relationship("Parish", back_populates="centrales")
    communities: Mapped[list["SmallChristianCommunity"]] = relationship(
        "SmallChristianCommunity", back_populates="centrale"
    )


class SmallChristianCommunity(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Small Christian Community / CEB / Umuryango-remezo."""

    __tablename__ = "small_christian_communities"

    centrale_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("centrales.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    patron_saint: Mapped[str | None] = mapped_column(String(150), nullable=True)
    leader_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    leader_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    centrale: Mapped["Centrale"] = relationship("Centrale", back_populates="communities")