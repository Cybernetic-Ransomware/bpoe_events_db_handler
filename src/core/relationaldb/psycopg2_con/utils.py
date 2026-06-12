from abc import ABC, abstractmethod
from contextlib import asynccontextmanager, contextmanager

import asyncpg
import psycopg
from psycopg.rows import dict_row

from src.config.config import POSTGRES_DB, POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_POOL_SIZE, POSTGRES_USER
from src.core.relationaldb.exceptions import (
    ConnectionNotEstablishedError,
    InvalidConnectorModeError,
    PoolNotInitializedError,
)


class BasePGConnector(ABC):
    def __init__(self):
        self.host = POSTGRES_HOST
        self.port = 5432
        self.database = POSTGRES_DB
        self.user = POSTGRES_USER
        self.password = POSTGRES_PASSWORD
        self.pool_size: tuple[int, int] = POSTGRES_POOL_SIZE

    @abstractmethod
    def connect(self):
        pass


class SyncPGConnector(BasePGConnector):
    def __init__(self):
        super().__init__()
        self._dsn: str | None = None

    def connect(self):
        if not self._dsn:
            self._dsn = (
                f"host={self.host} port={self.port} dbname={self.database} user={self.user} password={self.password}"
            )

    def get_pool(self):
        if not self._dsn:
            raise ConnectionNotEstablishedError("Sync connector not connected.")
        return self._dsn

    @contextmanager
    def get_connection(self):
        if self._dsn is None:
            raise PoolNotInitializedError("Sync connection not initialized.")
        with psycopg.connect(self._dsn) as conn:
            yield conn

    @contextmanager
    def get_cursor(self):
        with self.get_connection() as conn, conn.cursor(row_factory=dict_row) as cursor:
            yield cursor


class AsyncPGConnector(BasePGConnector):
    def __init__(self):
        super().__init__()
        self._pool: asyncpg.Pool | None = None

    async def connect(self):
        if not self._pool:
            self._pool = await asyncpg.create_pool(
                min_size=self.pool_size[0],
                max_size=self.pool_size[1],
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                command_timeout=60,
            )

    def get_pool(self):
        if not self._pool:
            raise ConnectionNotEstablishedError("Async connector not connected.")
        return self._pool

    @asynccontextmanager
    async def get_connection(self):
        if self._pool is None:
            raise PoolNotInitializedError("Async connection pool is not initialized.")
        async with self._pool.acquire() as conn:
            yield conn

    async def close_postgres(self) -> None:
        if self._pool is not None:
            await self._pool.close()


def get_pg_connector(mode: str = "sync") -> SyncPGConnector | AsyncPGConnector:
    if mode == "sync":
        return SyncPGConnector()
    elif mode == "async":
        return AsyncPGConnector()
    else:
        raise InvalidConnectorModeError(mode)
