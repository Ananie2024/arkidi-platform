import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

import geoalchemy2  # noqa: F401  Ensures GeoAlchemy2 types are recognized

from app.config import settings
from app.core.database import Base

# Import all model modules so SQLAlchemy registers their tables in Base.metadata,
# enabling Alembic autogenerate to detect the full schema.
from app.models import (  # noqa: F401
    audit_log,
    base,
    commission,
    council,
    deanery,
    document,
    document_type,
    donation,
    enums,
    event,
    faithful,
    intention,
    land_use_category,
    lease_agreement,
    lease_payment_schedule,
    mass,
    meeting,
    meeting_minute,
    ministry,
    parcel,
    parcel_ownership_history,
    parish,
    physical_location,
    priest,
    qr_code_registry,
    sacrament,
    storage_cabinet,
    survey,
    tax_payment,
    tax_record,
    user,
)

# Alembic Config object
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = settings.ASYNC_DATABASE_URL

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()