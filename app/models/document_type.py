"""
Document Type Model — canonical & administrative document categories.
"""

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class DocumentType(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """Catalog of document categories (decree, deed, letter, certificate, minutes).

    Retention / disposition scheduling
    -----------------------------------
    ``retention_years`` is the number of years a document of this type is kept
    from its creation date before an archivist must review it.  A null value
    means "retain indefinitely".

    ``disposition_action`` describes what the archivist should do once the
    retention period has elapsed — one of: ``DESTROY``, ``TRANSFER``,
    ``MANUAL_REVIEW``, or ``PRESERVE_INDEFINITELY``.
    """

    __tablename__ = "document_types"

    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    name_fr: Mapped[str] = mapped_column(String(200), nullable=False)
    name_rw: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="GENERAL", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ------------------------------------------------------------------
    # Retention & Disposition Scheduling
    # ------------------------------------------------------------------
    retention_years: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Years to retain documents of this type from creation date. NULL = indefinite.",
    )
    disposition_action: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Action to take when retention expires: DESTROY|TRANSFER|MANUAL_REVIEW|PRESERVE_INDEFINITELY.",
    )
