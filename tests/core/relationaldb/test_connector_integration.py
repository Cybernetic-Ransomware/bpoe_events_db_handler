import pytest
import asyncpg


@pytest.mark.integration
async def test_asyncpg_connection_opens_and_closes(postgres_url: str, applied_schema) -> None:
    """Verify that a raw asyncpg connection can be established and closed cleanly."""
    raw_url = postgres_url.replace("postgresql+asyncpg://", "postgresql://")
    conn: asyncpg.Connection = await asyncpg.connect(raw_url)
    try:
        result = await conn.fetchval("SELECT 1")
        assert result == 1
    finally:
        await conn.close()


@pytest.mark.integration
async def test_asyncpg_pool_acquire_and_release(postgres_url: str, applied_schema) -> None:
    """Verify that an asyncpg pool can acquire and release connections."""
    raw_url = postgres_url.replace("postgresql+asyncpg://", "postgresql://")
    pool: asyncpg.Pool = await asyncpg.create_pool(raw_url, min_size=1, max_size=3)
    try:
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 42")
            assert result == 42
    finally:
        await pool.close()


@pytest.mark.integration
async def test_schema_tables_exist(pg_connection: asyncpg.Connection) -> None:
    """Verify that all expected tables were created by the schema setup."""
    expected_tables = {
        "participant",
        "event",
        "eventowner",
        "eventparticipantassociation",
        "eventlocation",
        "eventtransaction",
    }
    rows = await pg_connection.fetch(
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
    )
    existing = {row["tablename"] for row in rows}
    assert expected_tables.issubset(existing), f"Missing tables: {expected_tables - existing}"
