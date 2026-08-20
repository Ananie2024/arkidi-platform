"""
Land Use Category Model — canonical land usage classification catalog.
"""
from sqlalchemy import String, Boolean

from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class LandUseCategory(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Catalog of land use categories (church compound, education, agriculture...)."""

    __tablename__ = "land_use_categories"

    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    name_fr: Mapped[str] = mapped_column(String(200), nullable=False)
    name_rw: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)