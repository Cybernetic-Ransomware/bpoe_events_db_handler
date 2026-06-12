import os
import sys
from pathlib import Path
from typing import AsyncGenerator

import pytest

# Make both `from src.X` and `from core.X` style imports work.
# Some modules use `src.` prefix, others omit it (treating src/ as root).
_root = Path(__file__).parent.parent
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_root / "src"))

# Load test env vars before any src module is imported so that
# python-decouple (which checks os.environ first) picks them up.
_env_file = Path(__file__).parent / ".env.test"
for _line in _env_file.read_text().splitlines():
    _line = _line.strip()
    if not _line or _line.startswith("#"):
        continue
    if "=" in _line:
        _key, _, _value = _line.partition("=")
        os.environ.setdefault(_key.strip(), _value.strip().strip('"').strip("'"))


@pytest.fixture(scope="session")
def app():
    from src.main import app as fastapi_app

    return fastapi_app


# ---------------------------------------------------------------------------
# Postgres fixtures (integration only — require Docker)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def postgres_container():
    try:
        import docker

        docker.from_env().ping()
    except Exception:
        pytest.skip("Docker not available — skipping Postgres integration tests")

    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:17") as container:
        yield container


@pytest.fixture(scope="session")
def postgres_url(postgres_container) -> str:
    """asyncpg-style URL for both schema setup and async tests."""
    return postgres_container.get_connection_url().replace("psycopg2", "asyncpg")


@pytest.fixture(scope="session")
def applied_schema(postgres_url: str) -> None:
    """Create all ORM tables once per session via asyncpg + SQLAlchemy async engine."""
    import asyncio

    from sqlalchemy.ext.asyncio import create_async_engine

    from src.core.relationaldb.models.models import Base

    async def _create() -> None:
        engine = create_async_engine(postgres_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()

    asyncio.run(_create())


@pytest.fixture
async def pg_connection(postgres_url: str, applied_schema) -> AsyncGenerator:
    """Provide a fresh asyncpg connection for each test, rolled back on teardown."""
    import asyncpg

    raw_url = postgres_url.replace("postgresql+asyncpg://", "postgresql://")
    conn: asyncpg.Connection = await asyncpg.connect(raw_url)
    tr = conn.transaction()
    await tr.start()
    yield conn
    await tr.rollback()
    await conn.close()


# ---------------------------------------------------------------------------
# MongoDB fixtures (integration only — require Docker)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def mongo_container():
    try:
        import docker

        docker.from_env().ping()
    except Exception:
        pytest.skip("Docker not available — skipping MongoDB integration tests")

    from testcontainers.mongodb import MongoDbContainer

    with MongoDbContainer("mongo:8.0") as container:
        yield container


@pytest.fixture(scope="session")
def mongo_url(mongo_container) -> str:
    return mongo_container.get_connection_url()
