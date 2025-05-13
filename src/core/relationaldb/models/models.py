from datetime import datetime
from typing import Optional, TYPE_CHECKING

# from geoalchemy2 import Geometry
from geoalchemy2 import types as geo_types
from shapely.geometry import Point
from sqlalchemy import DateTime, ForeignKey, Index, String, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class EventOwner(Base):
    __tablename__ = "eventowner"

    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"), primary_key=True)
    participant_id: Mapped[int] = mapped_column(ForeignKey("eventparticipant.id"), primary_key=True)

    event: Mapped["Event"] = relationship(back_populates="owner_association")
    participant: Mapped["EventParticipant"] = relationship(back_populates="owner_associations")


class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(primary_key=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    name: Mapped[str]
    locations: Mapped[list["EventLocation"]] = relationship(back_populates="event")
    participants: Mapped[list["EventParticipant"]] = relationship(back_populates="event")

    owner_association: Mapped[list["EventOwner"]] = relationship()

    @property
    def owner(self) -> Optional["EventParticipant"]:
        if not hasattr(self, '_owner'):
            if not self.owner_association:
                return None

            owner_id = self.owner_association[0].participant_id
            session = Session.object_session(self)

            if session:
                self._owner = session.query(EventParticipant).filter_by(id=owner_id).first()
            else:
                self._owner = None

        return self._owner

    def set_owner(self, participant: "EventParticipant") -> None:
        session = Session.object_session(self)
        if not session:
            raise ValueError("Event must be in a session to set owner")

        session.query(EventOwner).filter_by(event_id=self.id).delete()

        owner_assoc = EventOwner(event_id=self.id, participant_id=participant.id)
        session.add(owner_assoc)

        self._owner = participant


class EventParticipant(Base):
    __tablename__ = "eventparticipant"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)

    event: Mapped["Event"] = relationship(back_populates="participants")
    owner_associations: Mapped[list["EventOwner"]] = relationship(back_populates="participant",
                                                                  cascade="all, delete-orphan")

    @property
    def owned_events(self) -> list["Event"]:
        """Get events owned by this participant."""
        return [assoc.event for assoc in self.owner_associations]

    @property
    def is_owner_of_current_event(self) -> bool:
        """Check if this participant is the owner of their associated event."""
        if not self.event:
            return False

        owner = self.event.owner
        return owner is not None and owner.id == self.id


class EventLocation(Base):
    __tablename__ = "eventlocation"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[Point] = mapped_column(geo_types.Geometry(geometry_type='POINT', srid=4326))
    entered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    exited_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    event: Mapped["Event"] = relationship(back_populates="locations")

    __table_args__ = (
        Index('idx_eventlocation_location', 'location', postgresql_using='gist', postgresql_where=text('TRUE')),
    )
