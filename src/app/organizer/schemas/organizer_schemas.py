from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ---------------- Organizer ----------------
class OrganizerBase(BaseModel):
    user_id: int
    company_name: str


class OrganizerCreate(OrganizerBase):
    pass

class OrganizerUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    website: Optional[str] = None
    bio: Optional[str] = None
    address: Optional[str] = None

class OrganizerOut(OrganizerBase):
    organizer_id: int
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class OrganizerStatsOut(BaseModel):
    organizer_id: int
    company_name: str
    total_events: int
    active_events: int
    total_attendees: int
    total_revenue: float

    class Config:
        orm_mode = True
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
        orm_mode = True

class EventStatisticsOut(BaseModel):
    event_id: int
    total_tickets: int
    sold_tickets: int
    remaining_tickets: int
    total_revenue: float

    class Config:
        orm_mode = True
# ---------------- Ticket ----------------
class TicketBase(BaseModel):
    ticket_type_id: int
    ticket_price: float
    ticket_total_quantity: int

class TicketCreate(TicketBase):
    event_id: int

class TicketOut(TicketBase):
    ticket_id: int
    ticket_remaining_quantity: int
    event_id: int

    class Config:
        orm_mode = True
# ---------------- Attendee ----------------
class CheckInStatus(str, Enum):
    PENDING = "pending"
    CHECKED_IN = "checked_in"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class AttendeeBase(BaseModel):
    user_id: int
    event_id: int
    check_in_status: Optional[CheckInStatus] = CheckInStatus.PENDING
    check_in_time: Optional[datetime] = None
    # REMOVED: notes, created_at (not in your database)

class AttendeeCreate(AttendeeBase):
    pass

class AttendeeUpdate(BaseModel):
    check_in_status: Optional[CheckInStatus] = None
    check_in_time: Optional[datetime] = None
    # REMOVED: notes

class AttendeeOut(AttendeeBase):
    attendee_id: int
    # REMOVED: created_at

    class Config:
        from_attributes = True

class AttendeeImportRow(BaseModel):
    user_id: int
    # REMOVED: notes

class AttendeeBulkImport(BaseModel):
    attendees: List[AttendeeImportRow]

class AttendeeImportResponse(BaseModel):
    imported_count: int
    failed_rows: List[int]
    total_rows: int

class CheckInUpdate(BaseModel):
    check_in_status: CheckInStatus
    # REMOVED: notes
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

# ---------------- Notification ----------------
class NotificationType(str, Enum):
    EVENT_UPDATE = "event_update"
    REMINDER = "reminder"
    ANNOUNCEMENT = "announcement"
    CHECKIN_REMINDER = "checkin_reminder"
    SYSTEM = "system"

class NotificationBase(BaseModel):
    title: str
    message: str
    type: Optional[NotificationType] = NotificationType.ANNOUNCEMENT

class NotificationCreate(NotificationBase):
    user_id: Optional[int] = None  # If null, it's considered a broadcast
    event_id: int

class BroadcastCreate(BaseModel):
    title: str
    message: str
    type: Optional[NotificationType] = NotificationType.ANNOUNCEMENT
    send_to_attendees: bool = True
    send_to_ticket_holders: bool = False

class NotificationOut(NotificationBase):
    notification_id: int
    user_id: Optional[int] = None
    event_id: int
    # REMOVED: is_broadcast (not in database)
    created_at: datetime

    class Config:
        from_attributes = True

class BroadcastResponse(BaseModel):
    success: bool
    sent_count: int
    failed_count: int
    total_recipients: int
    notification_ids: List[int]

class NotificationStats(BaseModel):
    event_id: int
    total_notifications: int
    broadcast_count: int  # Count of notifications with user_id = NULL
    individual_count: int  # Count of notifications with user_id != NULL
    by_type: Dict[str, int]

# ---------------- Ticket Schemas ----------------
class TicketBase(BaseModel):
    ticket_name: str
    ticket_type: str  # VIP, Standard, etc.
    ticket_price: float
    ticket_total_quantity: int
    ticket_description: Optional[str] = None
    sales_start: Optional[datetime] = None
    sales_end: Optional[datetime] = None

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    ticket_name: Optional[str] = None
    ticket_type: Optional[str] = None
    ticket_price: Optional[float] = None
    ticket_total_quantity: Optional[int] = None
    ticket_description: Optional[str] = None
    sales_start: Optional[datetime] = None
    sales_end: Optional[datetime] = None

class TicketOut(TicketBase):
    ticket_id: int
    event_id: int
    ticket_remaining_quantity: int

    class Config:
        orm_mode = True

# ---------------- Ticket Status Schemas ----------------
class TicketStatusOut(BaseModel):
    ticket_id: int
    ticket_name: str
    ticket_type: str
    ticket_price: float
    total_quantity: int
    remaining_quantity: int
    sold_quantity: int
    sales_percentage: float
    revenue_generated: float
    sales_start: Optional[datetime] = None
    sales_end: Optional[datetime] = None
    is_on_sale: bool

    class Config:
        orm_mode = True

class EventTicketsStatusOut(BaseModel):
    event_id: int
    total_tickets: int
    total_sold: int
    total_remaining: int
    total_revenue: float
    overall_sales_percentage: float
    ticket_statuses: list[TicketStatusOut]

    class Config:
        orm_mode = True