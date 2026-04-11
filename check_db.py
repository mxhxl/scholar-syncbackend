"""Verify the backend can actually connect to the database.

Reads the same .env / config the backend uses, and connects with the
same async driver. If this script succeeds, the backend will too. If it
fails, the backend will fail the same way.

Usage:
    python check_db.py
"""

import asyncio
import sys
from sqlalchemy import text
from app.core.database import engine
from app.config import settings


async def main() -> int:
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
    print("Connecting...")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT current_database(), current_user, version();"))
            db, user, version = result.one()
            print("  OK")
            print(f"  database: {db}")
            print(f"  user:     {user}")
            print(f"  server:   {version.splitlines()[0]}")

            result = await conn.execute(
                text("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
            )
            table_count = result.scalar()
            print(f"  tables:   {table_count} in public schema")
        return 0
    except Exception as e:
        print(f"  FAILED: {type(e).__name__}: {e}")
        return 1
    finally:
        await engine.dispose()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
