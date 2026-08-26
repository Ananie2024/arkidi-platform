"""One-off status check: list tables, alembic version, entity counts."""
import asyncio

from sqlalchemy import text

from app.core.database import AsyncSessionLocal


async def main() -> None:
    async with AsyncSessionLocal() as db:
        r = await db.execute(
            text(
                "SELECT tablename FROM pg_tables "
                "WHERE schemaname='public' ORDER BY tablename"
            )
        )
        tables = [t[0] for t in r.all()]
        print(f"TABLES ({len(tables)}): {', '.join(tables)}")

        if "alembic_version" in tables:
            rv = await db.execute(text("SELECT version_num FROM alembic_version"))
            print("ALEMBIC VERSION:", rv.scalar())

        counts = {}
        for table in ("users", "parishes", "deaneries", "priests", "faithful"):
            if table in tables:
                rc = await db.execute(text(f'SELECT count(*) FROM "{table}"'))
                counts[table] = rc.scalar()
        print("COUNTS:", counts)


asyncio.run(main())