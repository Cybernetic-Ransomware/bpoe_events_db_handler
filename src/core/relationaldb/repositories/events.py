import uuid
from datetime import datetime
from uuid import uuid4

from asyncpg import Connection
from pydantic import EmailStr

from src.api.schemas import EventLocationRead, EventParticipantRead, EventRead


async def create_event_with_owner(conn: Connection, name: str, owner_email: EmailStr) -> uuid.UUID:
    GET_PARTICIPANT_SQL = "SELECT id FROM participant WHERE email = $1"
    INSERT_PARTICIPANT_SQL = """
        INSERT INTO participant (id, email, name)
        VALUES ($1, $2, $3)
        RETURNING id
    """
    INSERT_EVENT_SQL = """
        INSERT INTO event (id, name, opened_at)
        VALUES ($1, $2, $3)
        RETURNING id, opened_at
    """
    INSERT_PARTICIPANT_ASSOCIATION_SQL = """
        INSERT INTO eventparticipantassociation (event_id, participant_id, accepted)
        VALUES ($1, $2, true)
    """
    INSERT_OWNER_SQL = """
        INSERT INTO eventowner (event_id, participant_id)
        VALUES ($1, $2)
    """

    event_id = uuid4()
    participant_record = await conn.fetchrow(GET_PARTICIPANT_SQL, owner_email)

    if participant_record:
        participant_id = participant_record["id"]
    else:
        participant_id = uuid4()
        await conn.fetchrow(
            INSERT_PARTICIPANT_SQL,
            participant_id,
            owner_email,
            owner_email.split('@')[0]
        )

    insert_event = await conn.fetchrow(
        INSERT_EVENT_SQL,
        event_id,
        name,
        datetime.now()
    )
    event_id = insert_event["id"]

    await conn.execute(INSERT_PARTICIPANT_ASSOCIATION_SQL, event_id, participant_id)
    await conn.execute(INSERT_OWNER_SQL, event_id, participant_id)

    return event_id



async def get_event_by_id(conn: Connection, event_id: uuid.UUID) -> EventRead:
    query = """
        SELECT e.id, e.name, e.opened_at, e.closed_at, eo.participant_id AS owner_id
        FROM event e
        JOIN eventowner eo ON eo.event_id = e.id
        WHERE e.id = $1
        LIMIT 1
    """
    event_row = await conn.fetchrow(query, str(event_id))

    if not event_row:
        raise ValueError(f"Event with id {event_id} not found")

    participants_query = """
        SELECT p.id, p.name, p.email
        FROM participant p
        JOIN eventparticipantassociation ep ON ep.participant_id = p.id
        WHERE ep.event_id = $1 AND ep.accepted = true
    """
    participant_rows = await conn.fetch(participants_query, str(event_id))

    locations_query = """
        SELECT el.id, el.name, el.entered_at, el.exited_at
        FROM eventlocation el
        WHERE el.event_id = $1
    """
    location_rows = await conn.fetch(locations_query, str(event_id))

    return EventRead(
        id=event_row["id"],  # asyncpg już zwraca UUID
        name=event_row["name"],
        opened_at=event_row["opened_at"],
        closed_at=event_row["closed_at"],
        owner_id=event_row["owner_id"],
        participants=[
            EventParticipantRead(**dict(row)) for row in participant_rows
        ],
        locations=[
            EventLocationRead(
                id=row["id"],  # też UUID już jest
                name=row["name"],
                entered_at=row["entered_at"],
                exited_at=row["exited_at"]
            )
            for row in location_rows
        ]
    )
