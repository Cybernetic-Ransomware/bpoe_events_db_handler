from abc import ABC, abstractmethod
from contextlib import asynccontextmanager, contextmanager

import asyncpg
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

from src.config.config import POOL_SIZE, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_USER


class BasePGConnector(ABC):
    def __init__(self):
        self.host = POSTGRES_HOST
        self.port = 5432
        self.database = POSTGRES_DB
        self.user = POSTGRES_USER
        self.password = POSTGRES_PASSWORD
        self.pool_size = POOL_SIZE

    @abstractmethod
    def connect(self):
        pass


class SyncPGConnector(BasePGConnector):
    def __init__(self):
        super().__init__()
        self._connection_pool = None

    def connect(self):
        if not self._connection_pool:
            self._connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=self.pool_size,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )

    def get_pool(self):
        if not self._connection_pool:
            raise Exception("Call connect() first.")
        return self._connection_pool

    @contextmanager
    def get_connection(self):
        conn = self._connection_pool.getconn()
        try:
            yield conn
        finally:
            self._connection_pool.putconn(conn)

    @contextmanager
    def get_cursor(self):
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                yield cursor
            finally:
                cursor.close()


class AsyncPGConnector(BasePGConnector):
    def __init__(self):
        super().__init__()
        self._pool = None

    async def connect(self):
        if not self._pool:
            self._pool = await asyncpg.create_pool(
                min_size=1,
                max_size=self.pool_size,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                command_timeout=60
            )

    def get_pool(self):
        if not self._pool:
            raise Exception("Call connect() first.")
        return self._pool

    @asynccontextmanager
    async def get_connection(self):
        async with self._pool.acquire() as conn:
            yield conn


def get_pg_connector(mode: str = "sync") -> BasePGConnector:
    if mode == "sync":
        return SyncPGConnector()
    elif mode == "async":
        return AsyncPGConnector()
    else:
        raise ValueError("Unknown connector mode. Use 'sync' or 'async'.")
