from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    user_image = Column(String, nullable=True)
    role = Column(String, nullable=False)  # attendee / organizer

    bookings = relationship("Booking", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    user_tickets = relationship("UserTicket", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    user_discounts = relationship("UserDiscount", back_populates="user")
    attendees = relationship("Attendee", back_populates="user")
    organizer_profile = relationship("Organizer", back_populates="user")
    
class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True) # nullable nếu broadcast
    event_id = Column(Integer, ForeignKey("events.event_id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
    event = relationship("Event", back_populates="notifications")