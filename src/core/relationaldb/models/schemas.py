from datetime import datetime

from geoalchemy2.shape import to_shape
from pydantic import BaseModel, Field

from core.relationaldb.models.models import EventLocation


class LocationPoint(BaseModel):
    lat: float
    lon: float


class EventLocationRead(BaseModel):
    id: int
    name: str
    location: LocationPoint
    entered_at: datetime | None = None
    exited_at: datetime | None = None

    @staticmethod
    def from_orm_with_geo(location: EventLocation) -> "EventLocationRead":
        shape = to_shape(location.location)
        return EventLocationRead(
            id=location.id,
            name=location.name,
            location=LocationPoint(lat=shape.y, lon=shape.x),
            entered_at=location.entered_at,
            exited_at=location.exited_at,
        )


class EventParticipantRead(BaseModel):
    id: int
    name: str
    email: str


class EventRead(BaseModel):
    id: int
    name: str
    opened_at: datetime
    closed_at: datetime | None = None
    owner_id: int
    participants: list[EventParticipantRead] = Field(default_factory=list)
    locations: list[EventLocationRead] = Field(default_factory=list)
