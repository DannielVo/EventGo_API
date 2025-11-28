from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import List

# ---------------- Ticket Schemas ----------------
class TicketBase(BaseModel):
    ticket_type_id: Optional[int] = None
    ticket_price: float
    ticket_total_quantity: int
    # REMOVED: ticket_name, ticket_type, ticket_description, sales_start, sales_end
    # These don't exist in your tickets table

class TicketCreate(TicketBase):
    event_id: int

class TicketUpdate(BaseModel):
    ticket_type_id: Optional[int] = None
    ticket_price: Optional[float] = None
    ticket_total_quantity: Optional[int] = None
    ticket_remaining_quantity: Optional[int] = None

class TicketOut(TicketBase):
    ticket_id: int
    event_id: int
    ticket_remaining_quantity: int

    class Config:
        from_attributes = True

# ---------------- Ticket Status Schemas ----------------
class TicketStatusOut(BaseModel):
    ticket_id: int
    ticket_price: float
    total_quantity: int
    remaining_quantity: int
    sold_quantity: int
    sales_percentage: float
    revenue_generated: float
    is_on_sale: bool

    class Config:
        from_attributes = True

class EventTicketsStatusOut(BaseModel):
    event_id: int
    total_tickets: int
    total_sold: int
    total_remaining: int
    total_revenue: float
    overall_sales_percentage: float
    ticket_statuses: List[TicketStatusOut]

    class Config:
        from_attributes = True