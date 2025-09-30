import os
from typing import Annotated, AsyncGenerator

from fastapi import Depends
from pydantic import PostgresDsn
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class DatabaseConfig:
    """Central config for Postgres credentials (async)."""

    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "admin")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "appel")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "optimap")

    @property
    def uri(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


config = DatabaseConfig()

engine = create_async_engine(
    str(config.uri),
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


def get_db_engine() -> AsyncEngine:
    """
    Create a new async engine for the database.
    """
    return create_async_engine(
        str(config.uri),
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600,
    )


def get_db_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Create a new sessionmaker for the given engine.
    """
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an AsyncSession."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()


DbSessionDep = Annotated[AsyncSession, Depends(get_session)]
