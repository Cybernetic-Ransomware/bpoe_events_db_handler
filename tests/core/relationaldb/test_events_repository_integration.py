import uuid

import asyncpg
import pytest

from src.core.relationaldb.exceptions import NoRecordFoundError
from src.core.relationaldb.psycopg2_con.repositories.events import (
    create_event_with_owner,
    get_event_by_id,
)


@pytest.mark.integration
async def test_create_event_with_new_owner(pg_connection: asyncpg.Connection) -> None:
    """Creating an event with a brand-new owner inserts all required rows."""
    email = "owner@example.com"
    event_id = await create_event_with_owner(pg_connection, "Integration Test Event", email)

    assert isinstance(event_id, uuid.UUID)

    row = await pg_connection.fetchrow("SELECT name FROM event WHERE id = $1", str(event_id))
    assert row is not None
    assert row["name"] == "Integration Test Event"

    participant_row = await pg_connection.fetchrow(
        "SELECT id FROM participant WHERE email = $1", email
    )
    assert participant_row is not None


@pytest.mark.integration
async def test_create_event_with_existing_owner(pg_connection: asyncpg.Connection) -> None:
    """Creating two events with the same owner email reuses the existing participant row."""
    email = "repeat@example.com"

    event_id_1 = await create_event_with_owner(pg_connection, "First Event", email)
    event_id_2 = await create_event_with_owner(pg_connection, "Second Event", email)

    assert event_id_1 != event_id_2

    count = await pg_connection.fetchval(
        "SELECT COUNT(*) FROM participant WHERE email = $1", email
    )
    assert count == 1


@pytest.mark.integration
async def test_get_event_by_id_returns_correct_data(pg_connection: asyncpg.Connection) -> None:
    """get_event_by_id returns an EventRead model with the expected fields."""
    email = "getter@example.com"
    event_id = await create_event_with_owner(pg_connection, "Fetchable Event", email)

    event = await get_event_by_id(pg_connection, event_id)

    assert event.id == event_id
    assert event.name == "Fetchable Event"
    assert event.closed_at is None
    assert len(event.participants) >= 1
    participant_emails = [p.email for p in event.participants]
    assert email in participant_emails


@pytest.mark.integration
async def test_get_event_by_id_raises_for_missing_event(pg_connection: asyncpg.Connection) -> None:
    """get_event_by_id raises NoRecordFoundError when the event does not exist."""
    with pytest.raises(NoRecordFoundError):
        await get_event_by_id(pg_connection, uuid.uuid4())


class _FailOnFirstExecute:
    """Proxy that delegates all asyncpg methods to the real connection but raises on the first execute()."""

    def __init__(self, conn: asyncpg.Connection) -> None:
        self._conn = conn
        self._executed = False

    async def fetchrow(self, sql: str, *args):
        return await self._conn.fetchrow(sql, *args)

    async def fetch(self, sql: str, *args):
        return await self._conn.fetch(sql, *args)

    async def fetchval(self, sql: str, *args):
        return await self._conn.fetchval(sql, *args)

    async def execute(self, sql: str, *args):
        if not self._executed:
            self._executed = True
            raise RuntimeError("simulated failure on first execute()")
        return await self._conn.execute(sql, *args)

    def transaction(self):
        return self._conn.transaction()


@pytest.mark.integration
async def test_create_event_is_atomic(pg_connection: asyncpg.Connection) -> None:
    """Failure on INSERT_PARTICIPANT_ASSOCIATION rolls back the participant and event rows too."""
    participant_count_before = await pg_connection.fetchval("SELECT COUNT(*) FROM participant")
    event_count_before = await pg_connection.fetchval("SELECT COUNT(*) FROM event")

    proxy = _FailOnFirstExecute(pg_connection)

    with pytest.raises(RuntimeError, match="simulated failure"):
        await create_event_with_owner(proxy, "Should Roll Back", "rollback@example.com")  # type: ignore[arg-type]

    participant_count_after = await pg_connection.fetchval("SELECT COUNT(*) FROM participant")
    event_count_after = await pg_connection.fetchval("SELECT COUNT(*) FROM event")

    assert participant_count_after == participant_count_before, "participant row should be rolled back on failure"
    assert event_count_after == event_count_before, "event row should be rolled back on failure"
