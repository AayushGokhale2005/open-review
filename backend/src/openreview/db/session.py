"""Database engine and session management."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from openreview.core.config import Settings


class Base(DeclarativeBase):
    pass


engine = None
SessionLocal: async_sessionmaker[AsyncSession] | None = None


def init_db(settings: Settings) -> None:
    global engine, SessionLocal
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        connect_args={"check_same_thread": False},
    )
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def create_tables() -> None:
    if engine is None:
        raise RuntimeError("Database not initialized")
    # Import models so metadata is populated
    import openreview.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if SessionLocal is None:
        raise RuntimeError("Database not initialized")
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
