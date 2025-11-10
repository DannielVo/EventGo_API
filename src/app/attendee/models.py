from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    event_id = Column(Integer, ForeignKey("events.event_id"))
    booking_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False)
    payment_status = Column(String, default="pending")  # pending, paid, failed
    qr_code = Column(String, unique=True, nullable=False)

    user = relationship("User", back_populates="bookings")
    booking_details = relationship("BookingDetail", back_populates="booking")
    user_discounts = relationship("UserDiscount", back_populates="booking")
    event = relationship("Event", back_populates="bookings")


class BookingDetail(Base):
    __tablename__ = "booking_details"

    booking_detail_id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.booking_id"))
    ticket_id = Column(Integer, ForeignKey("tickets.ticket_id"))
    seat_map_id = Column(Integer, ForeignKey("seat_maps.seat_map_id"))
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    booking = relationship("Booking", back_populates="booking_details")
    ticket = relationship("Ticket", back_populates="booking_details")
    seat_map = relationship("SeatMap", back_populates="booking_details")


class UserTicket(Base):
    __tablename__ = "user_tickets"

    user_ticket_id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.ticket_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    qr_code = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)  # valid / expired
    purchase_date = Column(DateTime, default=datetime.utcnow)
    used_date = Column(DateTime, nullable=True)
    expire_date = Column(DateTime)

    user = relationship("User", back_populates="user_tickets")
    ticket = relationship("Ticket", back_populates="user_tickets")


class SeatMap(Base):
    __tablename__ = "seat_maps"

    seat_map_id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.event_id"))
    row = Column(String, nullable=False)
    seat_number = Column(String, nullable=False)
    status = Column(String, nullable=False)  # available, booked, pending

    event = relationship("Event", back_populates="seat_maps")
    booking_details = relationship("BookingDetail", back_populates="seat_map")


class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.event_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    review_content = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reviews")
    event = relationship("Event", back_populates="reviews")


class UserDiscount(Base):
    __tablename__ = "user_discount"

    user_discount_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    discount_id = Column(Integer, ForeignKey("discounts.discount_id"))
    booking_id = Column(Integer, ForeignKey("bookings.booking_id"), nullable=True)
    used_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="user_discounts")
    discount = relationship("Discount", back_populates="user_discounts")
    booking = relationship("Booking", back_populates="user_discounts")

    __table_args__ = (
        UniqueConstraint('user_id', 'discount_id', name='uq_user_discount'),
    )