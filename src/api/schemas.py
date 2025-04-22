from pydantic import BaseModel, EmailStr, Field, field_validator
import pendulum


# ---------- LOCATION ----------
class EventLocationBase(BaseModel):
    name: str
    entered_at: pendulum.DateTime | None = None
    exited_at: pendulum.DateTime | None = None


class EventLocationCreate(EventLocationBase):
    location: dict = Field(description="GeoJSON Point: {\"type\": \"Point\", \"coordinates\": [lon, lat]}")

    @field_validator("location")
    def validate_geojson(cls, v):
        if v.get("type") != "Point" or "coordinates" not in v:
            raise ValueError("Invalid GeoJSON Point format")
        return v


class EventLocationResponse(EventLocationBase):
    id: int
    event_id: int
    location: dict

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            pendulum.DateTime: lambda dt: dt.isoformat(),
        }
    }


# ---------- PARTICIPANT ----------
class EventParticipantBase(BaseModel):
    name: str
    email: EmailStr


class EventParticipantCreate(EventParticipantBase):
    pass


class EventParticipantResponse(EventParticipantBase):
    id: int
    event_id: int

    class Config:
        from_attributes = True


# ---------- EVENT ----------
class EventBase(BaseModel):
    name: str
    opened_at: pendulum.DateTime
    closed_at: pendulum.DateTime | None = None


class EventCreate(EventBase):
    owner_id: int
    participants: list[EventParticipantCreate] = []
    locations: list[EventLocationCreate] = []


class EventResponse(EventBase):
    id: int
    owner_id: int
    participants: list[EventParticipantResponse] = []
    locations: list[EventLocationResponse] = []

    class Config:
        from_attributes = True
        json_encoders = {
            pendulum.DateTime: lambda dt: dt.isoformat(),
        }
