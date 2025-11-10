from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Organizer(Base):
    __tablename__ = "organizers"

    organizer_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    company_name = Column(String, nullable=False)

    events = relationship("Event", back_populates="organizer")
    user = relationship("User", back_populates="organizer_profile")

class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True)
    organizer_id = Column(Integer, ForeignKey("organizers.organizer_id"))
    event_title = Column(String, nullable=False)
    event_description = Column(String, nullable=True)
    event_category = Column(String, nullable=True)
    event_date = Column(DateTime, nullable=False)
    event_location = Column(String, nullable=False)
    event_status = Column(String, default="draft")  # draft, published, cancelled, completed

    organizer = relationship("Organizer", back_populates="events")
    tickets = relationship("Ticket", back_populates="event")
    seat_maps = relationship("SeatMap", back_populates="event")
    reviews = relationship("Review", back_populates="event")
    bookings = relationship("Booking", back_populates="event")
    notifications = relationship("Notification", back_populates="event")
    discounts = relationship("Discount", back_populates="event")
    attendees = relationship("Attendee", back_populates="event")
    event_media = relationship("EventMedia", back_populates="event")
    event_artists = relationship("EventArtist", back_populates="event")
    event_categories = relationship("EventCategory", back_populates="event")


class EventMedia(Base):
    __tablename__ = "event_media"

    media_id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.event_id"))
    media_url = Column(String, nullable=False)
    media_type = Column(String, nullable=False)

    event = relationship("Event", back_populates="event_media")


class Artist(Base):
    __tablename__ = "artists"

    artist_id = Column(Integer, primary_key=True)
    artist_name = Column(String, nullable=False)

    event_artists = relationship("EventArtist", back_populates="artist")


class EventArtist(Base):
    __tablename__ = "event_artist"

    event_id = Column(Integer, ForeignKey("events.event_id"), primary_key=True)
    artist_id = Column(Integer, ForeignKey("artists.artist_id"), primary_key=True)

    event = relationship("Event", back_populates="event_artists")
    artist = relationship("Artist", back_populates="event_artists")


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True)
    category_name = Column(String, nullable=False)
    category_desc = Column(String)

    event_categories = relationship("EventCategory", back_populates="category")


class EventCategory(Base):
    __tablename__ = "event_category"

    event_id = Column(Integer, ForeignKey("events.event_id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), primary_key=True)

    event = relationship("Event", back_populates="event_categories")
    category = relationship("Category", back_populates="event_categories")


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True)
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.ticket_type_id"))
    event_id = Column(Integer, ForeignKey("events.event_id"))
    ticket_price = Column(Float, nullable=False)
    ticket_total_quantity = Column(Integer, nullable=False)
    ticket_remaining_quantity = Column(Integer, nullable=False)

    ticket_type = relationship("TicketType", back_populates="tickets")
    event = relationship("Event", back_populates="tickets")
    booking_details = relationship("BookingDetail", back_populates="ticket")
    user_tickets = relationship("UserTicket", back_populates="ticket")


class TicketType(Base):
    __tablename__ = "ticket_types"

    ticket_type_id = Column(Integer, primary_key=True)
    ticket_type_name = Column(String, nullable=False)
    ticket_type_desc = Column(String)

    tickets = relationship("Ticket", back_populates="ticket_type")


class Discount(Base):
    __tablename__ = "discounts"

    discount_id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.event_id"))
    discount_code = Column(String, nullable=False)
    discount_value = Column(Float, nullable=False)
    max_usage = Column(Integer, nullable=False)
    used_count = Column(Integer, default=0)
    discount_status = Column(String, default="active")  # active, inactive

    event = relationship("Event", back_populates="discounts")
    user_discounts = relationship("UserDiscount", back_populates="discount")


class Attendee(Base):
    __tablename__ = "attendees"

    attendee_id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.event_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    check_in_status = Column(String, default="pending")  # checked_in, pending
    check_in_time = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="attendees")
    event = relationship("Event", back_populates="attendees")
