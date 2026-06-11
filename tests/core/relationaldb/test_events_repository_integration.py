import uuid

import asyncpg
import pytest

from core.relationaldb.exceptions import NoRecordFoundError
from core.relationaldb.psycopg2_con.repositories.events import (
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
