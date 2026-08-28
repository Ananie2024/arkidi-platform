"""
SQLAlchemy Declarative Base and shared mixins.
All Arkidi ORM models inherit from :class:`Base` and the provided mixins.
"""
from datetime import datetime, timezone
import uuid

from sqlalchemy import DateTime, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _utcnow() -> datetime:
    """Timezone-aware UTC now used as a client-side default/onupdate value.

    Supplying a Python-side value for ``created_at``/``updated_at`` (in addition
    to the ``server_default``) means the ORM populates the columns on the client
    during INSERT/UPDATE. Without it, the columns are treated as pure server
    defaults, are expired after a flush, and a later synchronous read (e.g. when
    building a Pydantic response inside a service) triggers a lazy SELECT that
    raises ``sqlalchemy.exc.MissingGreenlet`` in async code.
    """
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy 2.0 models."""

    pass


class TimestampMixin:
    """Mixin for entity creation and modification timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
        server_default=func.now(),
        nullable=False,
    )


class UUIDPrimaryKeyMixin:
    """Mixin providing a UUID v4 primary key."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )


class SoftDeleteMixin:
    """Mixin providing soft-delete status for canonical records."""

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
