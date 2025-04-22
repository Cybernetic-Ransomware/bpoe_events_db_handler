from sqlmodel import SQLModel, Field, Relationship
from geoalchemy2 import Geometry
import pendulum


class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    opened_at: pendulum.DateTime
    closed_at: pendulum.DateTime | None = None
    name: str
    owner_id: int = Field(foreign_key="eventparticipant.id")

    locations: list["EventLocation"] = Relationship(back_populates="event")
    participants: list["EventParticipant"] = Relationship(back_populates="event")


class EventParticipant(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id")
    name: str
    email: str

    event: Event = Relationship(back_populates="participants")


class EventLocation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id")
    name: str
    location: Geometry = Field(sa_column=Field(Geometry("POINT", srid=4326)))
    entered_at: pendulum.DateTime | None = None
    exited_at: pendulum.DateTime | None = None

    event: Event = Relationship(back_populates="locations")
