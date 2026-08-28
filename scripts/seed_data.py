"""
Database Initial Seeding Script

Only seed *accounts* (i.e. login credentials) are created here, so that an
operator can sign into a freshly-migrated environment. No demo or reference
business data — Archdeocese, Deaneries, Parishes, Faithful, etc. — is inserted
by this script; all of that must be created through the application APIs and
stored in the database (the UI reads everything back from the database).
"""
import asyncio
import os

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.enums import UserRole
from app.core.security import get_password_hash

# Dev-only fallback for the seed admin account. This is NOT a real credential —
# anything that hashes this placeholder is only usable in a local dev database.
# Set ADMIN_SEED_PASSWORD to a real value when seeding any non-local environment.
ADMIN_SEED_PASSWORD = os.environ.get("ADMIN_SEED_PASSWORD", "dev-only-insecure-admin-change-me")


async def seed():
    async with AsyncSessionLocal() as session:
        print("\U0001F331 Seeding seed accounts only...")

        # Check existing Super Admin
        admin_res = await session.execute(select(User).where(User.username == "admin"))
        existing = admin_res.scalar_one_or_none()
        if existing is not None:
            print("\u2713 Super Admin account already exists; skipping.")
            await session.commit()
            print("\u2727 Seeding completed (no changes).")
            return

        admin = User(
            email="chancellor@archidiocesekigali.org",
            username="admin",
            hashed_password=get_password_hash(ADMIN_SEED_PASSWORD),
            full_name="Archdiocese Chancellor & Admin",
            role=UserRole.SUPER_ADMIN,
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        print(f"\u2713 Created Super Admin user (admin / {ADMIN_SEED_PASSWORD})")
        print("\u2727 Seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed())