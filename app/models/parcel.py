"""
Land Assets Module SQLAlchemy Models
Geospatial PostGIS Land Parcels, Real Estate Assets and Deeds
"""
import uuid
from datetime import date
from enum import Enum
from sqlalchemy import String, Date, Numeric, Text, Enum as SQLEnum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class LandUseType(str, Enum):
    CHURCH_COMPOUND = "CHURCH_COMPOUND"      # Kiriziya n'ibiro bya padiri
    CENTRALE_CHAPEL = "CENTRALE_CHAPEL"      # Isakramentu / Centrale
    HEALTH_FACILITY = "HEALTH_FACILITY"      # Ibitaro / Ikigo nderabuzima
    EDUCATIONAL = "EDUCATIONAL"              # Amashuri (Primary, Secondary, TVET)
    AGRICULTURAL = "AGRICULTURAL"            # Isambu y'ubuhinzi / Ubworozi
    COMMERCIAL_RENTAL = "COMMERCIAL_RENTAL"  # Inzu zikodeshwa / Ubucuruzi
    CONVENT_MONASTERY = "CONVENT_MONASTERY"  # Umuryango w'abihayimana
    CEMETERY = "CEMETERY"                    # Irimbi rya kiliziya
    VACANT_RESERVE = "VACANT_RESERVE"        # Ubutaka budakoreshwa


class TenureStatus(str, Enum):
    FREEHOLD = "FREEHOLD"                    # Icyemezo cy'ubutaka burambye
    EMPHYTEUTIC_LEASE = "EMPHYTEUTIC_LEASE"  # Ubukode bw'igihe kirekire
    DISPUTED = "DISPUTED"                    # Harimo amakimbirane
    IN_REGISTRATION = "IN_REGISTRATION"      # Buri mu kwandikishwa


class LandParcel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Geospatial Land Parcel (PostGIS Polygon SRID 4326)."""
    __tablename__ = "land_parcels"

    upi: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False) # Unique Parcel Identifier
    title_deed_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    parcel_name: Mapped[str] = mapped_column(String(200), nullable=False)

    parish_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parishes.id"), nullable=False)
    deanery_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("deaneries.id"), nullable=True)

    land_use: Mapped[LandUseType] = mapped_column(
        SQLEnum(LandUseType, name="land_use_enum"),
        default=LandUseType.CHURCH_COMPOUND,
        nullable=False,
    )
    tenure_status: Mapped[TenureStatus] = mapped_column(
        SQLEnum(TenureStatus, name="tenure_status_enum"),
        default=TenureStatus.FREEHOLD,
        nullable=False,
    )

    area_sqm: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    acquisition_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    estimated_value_rwf: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)

    # PostGIS Boundary Geometry (Polygon / MultiPolygon)
    boundary = mapped_column(Geometry(geometry_type="GEOMETRY", srid=4326), nullable=True)

    # Location references
    province: Mapped[str] = mapped_column(String(50), default="Kigali City", nullable=False)
    district: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sector: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cell: Mapped[str | None] = mapped_column(String(50), nullable=True)
    village: Mapped[str | None] = mapped_column(String(50), nullable=True)

    documents: Mapped[list["LandDocument"]] = relationship("LandDocument", back_populates="parcel")
    buildings: Mapped[list["BuildingAsset"]] = relationship("BuildingAsset", back_populates="parcel")


class LandDocument(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Deed Scan, Cadastral Map, Lease Contract or Certificate."""
    __tablename__ = "land_documents"

    parcel_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("land_parcels.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), default="TITLE_DEED", nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(nullable=True)

    parcel: Mapped["LandParcel"] = relationship("LandParcel", back_populates="documents")


class BuildingAsset(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Physical Building Asset constructed on Land Parcel."""
    __tablename__ = "building_assets"

    parcel_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("land_parcels.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    building_type: Mapped[str] = mapped_column(String(100), default="Church Building", nullable=False)
    construction_year: Mapped[int | None] = mapped_column(nullable=True)
    floors_count: Mapped[int] = mapped_column(default=1, nullable=False)
    condition: Mapped[str] = mapped_column(String(50), default="Good", nullable=False)

    parcel: Mapped["LandParcel"] = relationship("LandParcel", back_populates="buildings")
