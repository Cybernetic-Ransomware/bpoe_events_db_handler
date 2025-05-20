import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class EventLocationRead(BaseModel):
    id: uuid.UUID
    name: str
    entered_at: datetime | None
    exited_at: datetime | None

# ---------- PARTICIPANT ----------

class EventParticipantRead(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr

# ---------- EVENT ----------

class EventCreateIn(BaseModel):
    name: str
    owner_email: EmailStr

class EventRead(BaseModel):
    id: uuid.UUID
    name: str
    opened_at: datetime
    closed_at: datetime | None = None
    owner_id: uuid.UUID
    participants: list[EventParticipantRead] = Field(default_factory=list)
    locations: list[EventLocationRead] = Field(default_factory=list)
