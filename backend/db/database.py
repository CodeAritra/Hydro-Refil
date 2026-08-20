"""
RTRWH Platform — Database Configuration
========================================
Asynchronous SQLAlchemy database engine and session management.
Defaults to SQLite with aiosqlite for zero-config portable deployment.
"""

import os
import urllib.parse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Default to local SQLite database file in the backend directory
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./rtrwh_platform.db")

connect_args = {}

if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}
else:
    # Convert standard postgresql:// to postgresql+asyncpg:// for SQLAlchemy async
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Parse and strip libpq-specific parameters (sslmode, channel_binding, etc.) that asyncpg doesn't accept
    parsed = urllib.parse.urlparse(DATABASE_URL)
    query_params = urllib.parse.parse_qs(parsed.query)

    has_ssl = False
    if "sslmode" in query_params:
        has_ssl = query_params["sslmode"][0] in ("require", "verify-ca", "verify-full", "prefer")
    elif "ssl" in query_params:
        has_ssl = query_params["ssl"][0] in ("require", "true", "True", "1")
    elif "neon.tech" in DATABASE_URL or "render.com" in DATABASE_URL:
        has_ssl = True

    # Rebuild clean URL without query string to avoid keyword conflicts with asyncpg
    DATABASE_URL = urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        "",
        "",
        "",
    ))

    if has_ssl:
        connect_args = {"ssl": "require"}

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("LOG_SQL", "False").lower() == "true",
    future=True,
    connect_args=connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db():
    """Dependency for obtaining an asynchronous database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create tables on application startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
