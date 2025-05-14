from datetime import datetime

# from geoalchemy2 import types as geo_types
# from shapely.geometry import Point
from sqlalchemy import Boolean, DateTime, ForeignKey, PrimaryKeyConstraint, String, Text, UniqueConstraint

# from sqlalchemy import Index, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Participant(Base):
    __tablename__ = "participant"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    event_links: Mapped[list["EventParticipantAssociation"]] = relationship(back_populates="participant")
    owned_events: Mapped[list["Event"]] = relationship(
        secondary="eventowner",
        back_populates="owners"
    )


class Event(Base):
    __tablename__ = "event"
    __table_args__ = (
        PrimaryKeyConstraint("id", "opened_at"),
        UniqueConstraint("id"),
    )

    id: Mapped[int] = mapped_column()
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    name: Mapped[str] = mapped_column(Text)

    locations: Mapped[list["EventLocation"]] = relationship(back_populates="event")

    participant_links: Mapped[list["EventParticipantAssociation"]] = relationship(back_populates="event")

    owners: Mapped[list["Participant"]] = relationship(
        secondary="eventowner",
        back_populates="owned_events"
    )

    @property
    def participants(self) -> list["Participant"]:
        return [link.participant for link in self.participant_links if link.accepted]

    def assign_owner(self, participant: Participant, session: Session) -> None:
        is_accepted = session.query(EventParticipantAssociation).filter_by(
            event_id=self.id,
            participant_id=participant.id,
            accepted=True
        ).first()

        if not is_accepted:
            raise ValueError("Participant must accept the invitation before becoming an owner.")

        if participant not in self.owners:
            self.owners.append(participant)


class EventOwner(Base):
    __tablename__ = "eventowner"

    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"), primary_key=True)
    participant_id: Mapped[int] = mapped_column(ForeignKey("participant.id"), primary_key=True)

    event: Mapped["Event"] = relationship()
    participant: Mapped["Participant"] = relationship()

    def validate_participation(self, session: Session) -> bool:
        return session.query(EventParticipantAssociation).filter_by(
            event_id=self.event_id,
            participant_id=self.participant_id,
            accepted=True
        ).first() is not None


class EventParticipantAssociation(Base):
    __tablename__ = "eventparticipantassociation"
    __table_args__ = (
        PrimaryKeyConstraint("event_id", "participant_id"),
    )

    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"))
    participant_id: Mapped[int] = mapped_column(ForeignKey("participant.id"))

    accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    settled: Mapped[bool] = mapped_column(Boolean, default=False)
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    event: Mapped["Event"] = relationship(back_populates="participant_links")
    participant: Mapped["Participant"] = relationship(back_populates="event_links")


class EventLocation(Base):
    __tablename__ = "eventlocation"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # location: Mapped[Point] = mapped_column(geo_types.Geometry(geometry_type='POINT', srid=4326))

    entered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    exited_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"), nullable=False)
    event: Mapped["Event"] = relationship(back_populates="locations")

    # __table_args__ = (
    #     Index('idx_eventlocation_location', 'location', postgresql_using='gist', postgresql_where=text('TRUE')),
    # )


class EventTransaction(Base):
    __tablename__ = "eventtransaction"
    __table_args__ = (
        PrimaryKeyConstraint("id", "timestamp"),
    )

    id: Mapped[int] = mapped_column()
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"), nullable=False)
    participant_id: Mapped[int] = mapped_column(ForeignKey("participant.id"), nullable=False)

    amount: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    event: Mapped["Event"] = relationship()
    participant: Mapped["Participant"] = relationship()

    def validate_participation(self, session: Session) -> bool:
        return session.query(EventParticipantAssociation).filter_by(
            event_id=self.event_id,
            participant_id=self.participant_id,
            accepted=True
        ).first() is not None
