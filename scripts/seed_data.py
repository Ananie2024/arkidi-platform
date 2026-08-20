"""
Database Initial Seeding Script
Populates initial Archdiocese, Deaneries, and Super Admin user
"""
import asyncio
import os
from datetime import date

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.deanery import Archdiocese, Deanery
from app.models.parish import Parish
from app.models.enums import UserRole
from app.core.security import get_password_hash

# Dev-only fallback for the seed admin account. This is NOT a real credential —
# anything that hashes this placeholder is only usable in a local dev database.
# Set ADMIN_SEED_PASSWORD to a real value when seeding any non-local environment.
ADMIN_SEED_PASSWORD = os.environ.get("ADMIN_SEED_PASSWORD", "dev-only-insecure-admin-change-me")


async def seed():
    async with AsyncSessionLocal() as session:
        print("\U0001F331 Seeding initial Archdiocese of Kigali data...")

        # Check existing Archdiocese
        res = await session.execute(select(Archdiocese))
        archdiocese = res.scalar_one_or_none()

        if not archdiocese:
            archdiocese = Archdiocese(
                name="Archidiocèse de Kigali",
                canonical_erection_date=date(1976, 5, 3),
                patron_saint="Saint Michel Archange",
                see_city="Kigali",
            )
            session.add(archdiocese)
            await session.flush()
            print("\u2713 Created Archdiocese of Kigali")

            # Deaneries in Kigali
            deaneries_data = [
                {"name": "Doyenné Saint Michel", "code": "DOY-STM", "vicar": "Mgr. Vicaire Épiscopal"},
                {"name": "Doyenné Sainte Famille", "code": "DOY-STF", "vicar": "Abbé Curé Doyen"},
                {"name": "Doyenné Kicukiro", "code": "DOY-KCK", "vicar": "Abbé Curé Doyen"},
                {"name": "Doyenné Nyamata", "code": "DOY-NYM", "vicar": "Abbé Curé Doyen"},
            ]

            for d in deaneries_data:
                deanery = Deanery(
                    archdiocese_id=archdiocese.id,
                    name=d["name"],
                    code=d["code"],
                    vicar_forane_name=d["vicar"],
                )
                session.add(deanery)
            await session.flush()
            print("\u2713 Seeded 4 Deaneries")

        # Check existing Super Admin
        admin_res = await session.execute(select(User).where(User.username == "admin"))
        if not admin_res.scalar_one_or_none():
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
        else:
            await session.commit()

        print("\u2727 Seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed())