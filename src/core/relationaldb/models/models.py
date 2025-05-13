from datetime import datetime
from typing import TYPE_CHECKING

# from geoalchemy2 import Geometry
from geoalchemy2 import types as geo_types
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from shapely.geometry import Point  #noqa: F401


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(primary_key=True)
    opened_at: Mapped[datetime]
    closed_at: Mapped[datetime | None]
    name: Mapped[str]
    owner_id = Column(
        Integer,
        ForeignKey("eventparticipant.id", use_alter=True, name="fk_event_owner_id_eventparticipant"),
        nullable=False
    )

    locations: Mapped[list["EventLocation"]] = relationship(back_populates="event")
    participants: Mapped[list["EventParticipant"]] = relationship(back_populates="event")


class EventParticipant(Base):
    __tablename__ = "eventparticipant"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"))
    name: Mapped[str]
    email: Mapped[str]

    event: Mapped["Event"] = relationship(back_populates="participants")


class EventLocation(Base):
    __tablename__ = "eventlocation"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"))
    name: Mapped[str]
    location = Column(geo_types.Geometry(geometry_type='POINT', srid=4326))
    entered_at: Mapped[datetime | None]
    exited_at: Mapped[datetime | None]

    event: Mapped["Event"] = relationship(back_populates="locations")
