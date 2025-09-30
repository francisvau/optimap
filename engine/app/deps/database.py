import os
from contextlib import asynccontextmanager
from typing import Annotated, Any, AsyncGenerator

from fastapi import Depends, FastAPI
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import MongoDsn

from app.exceptions import InvalidConfiguration
from app.logger import logger


class MongoConfig:
    """Central MongoDB configuration class"""

    MONGO_USER: str = os.getenv("MONGO_INITDB_ROOT_USERNAME", "optimap")
    MONGO_PASSWORD: str = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "appel")
    MONGO_HOST: str = os.getenv("MONGO_HOST", "mongodb")
    MONGO_PORT: int = int(os.getenv("MONGO_PORT", "27017"))
    MONGO_DB: str = os.getenv("MONGO_INITDB_DATABASE", "optimap")
    MONGO_AUTH_SOURCE: str = os.getenv("MONGO_AUTH_SOURCE", "admin")

    def __init__(self, path: str | None = None):
        if not all(
            [
                self.MONGO_USER,
                self.MONGO_PASSWORD,
                self.MONGO_HOST,
                self.MONGO_PORT,
                self.MONGO_DB,
            ]
        ):
            raise InvalidConfiguration("MongoDB configuration is incomplete.")

        self.path = path or self.MONGO_DB

    @property
    def MONGO_URI(self) -> MongoDsn:
        dsn = MongoDsn.build(
            scheme="mongodb",
            username=self.MONGO_USER,
            password=self.MONGO_PASSWORD,
            host=self.MONGO_HOST,
            port=self.MONGO_PORT,
            path=self.MONGO_DB,
            query=f"authSource={self.MONGO_AUTH_SOURCE}",
        )
        return dsn


config = MongoConfig()

# Global client instance with connection pool
_client: AsyncIOMotorClient[Any] = AsyncIOMotorClient(
    str(config.MONGO_URI),
    maxPoolSize=100,  # Maximum connections in pool
    minPoolSize=10,  # Minimum idle connections
    maxIdleTimeMS=30000,  # Max time a connection can be idle
    socketTimeoutMS=5000,  # Network operation timeout
    serverSelectionTimeoutMS=5000,
)

_db: AsyncIOMotorDatabase[Any] = _client.get_database()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Manage connection pool lifecycle"""
    global _client, _db

    try:
        await _client.admin.command("ping")
        logger.info(f"MongoDB connection pool initialized: {str(config.MONGO_URI)}")
    except Exception as e:
        logger.error("Could not connect to MongoDB")
        raise InvalidConfiguration("Could not connect to MongoDB") from e

    yield  # Application runs here

    # Close all connections in pool
    _client.close()
    logger.info("MongoDB connection pool closed")


async def get_client() -> AsyncGenerator[AsyncIOMotorClient[Any], None]:
    """
    Get a database session from the connection pool
    (Note: Motor handles pooling automatically, this is mainly for DI)
    """
    yield _client


async def get_db() -> AsyncIOMotorDatabase[Any]:
    """Get database instance with connection from the pool"""
    return _db


# Dependency types
MongoClientDep = Annotated[AsyncIOMotorClient[Any], Depends(get_client)]
MongoDbDep = Annotated[AsyncIOMotorDatabase[dict[str, Any]], Depends(get_db)]
