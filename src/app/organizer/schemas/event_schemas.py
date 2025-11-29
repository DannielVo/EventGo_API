from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ---------------- Event ----------------
class EventBase(BaseModel):
    event_title: str
    event_description: Optional[str] = None
    event_category: Optional[str] = None
    event_date: datetime
    event_location: str
    event_status: Optional[str] = "draft"

class EventCreate(EventBase):
    organizer_id: int

class EventUpdate(BaseModel):
    event_title: Optional[str] = None
    event_description: Optional[str] = None
    event_category: Optional[str] = None
    event_date: Optional[datetime] = None
    event_location: Optional[str] = None
    event_status: Optional[str] = None

class EventOut(EventBase):
    event_id: int
    organizer_id: int

    class Config:
        from_attributes = True

class EventStatisticsOut(BaseModel):
    event_id: int
    total_tickets: int
    sold_tickets: int
    remaining_tickets: int
    total_revenue: float

    class Config:
        from_attributes = True