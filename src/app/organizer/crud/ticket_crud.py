from sqlalchemy.orm import Session
from datetime import datetime
from ...organizer.models.models import Event, Ticket, TicketType  # Fixed import path
from ...organizer.schemas.ticket_schemas import TicketCreate, TicketUpdate  # Fixed import path

# ---------------- Ticket CRUD ----------------
def create_ticket(db: Session, event_id: int, ticket: TicketCreate):
    """
    Create a new ticket for a specific event
    """
    # Verify event exists
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        return None
    
    # Verify ticket_type exists if provided
    if ticket.ticket_type_id:
        ticket_type = db.query(TicketType).filter(TicketType.ticket_type_id == ticket.ticket_type_id).first()
        if not ticket_type:
            return None
    
    new_ticket = Ticket(
        event_id=event_id,
        ticket_type_id=ticket.ticket_type_id,
        ticket_price=ticket.ticket_price,
        ticket_total_quantity=ticket.ticket_total_quantity,
        ticket_remaining_quantity=ticket.ticket_total_quantity  # Start with all tickets available
        # REMOVED: ticket_name, ticket_type, ticket_description, sales_start, sales_end
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

def get_tickets_by_event(db: Session, event_id: int):
    """
    Get all tickets for a specific event
    """
    # Verify event exists
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        return None
    
    return db.query(Ticket).filter(Ticket.event_id == event_id).all()

def get_ticket_by_id(db: Session, ticket_id: int):
    return db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()

def get_ticket_by_event_and_id(db: Session, event_id: int, ticket_id: int):
    """
    Get a specific ticket that belongs to a specific event
    """
    return db.query(Ticket).filter(
        Ticket.ticket_id == ticket_id,
        Ticket.event_id == event_id
    ).first()

def update_ticket(db: Session, ticket_id: int, data: TicketUpdate):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        return None
    
    # Calculate the difference in total quantity to update remaining quantity
    if data.ticket_total_quantity is not None and data.ticket_total_quantity != ticket.ticket_total_quantity:
        quantity_diff = data.ticket_total_quantity - ticket.ticket_total_quantity
        ticket.ticket_remaining_quantity += quantity_diff
    
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ticket, key, value)
    
    db.commit()
    db.refresh(ticket)
    return ticket

def delete_ticket(db: Session, ticket_id: int):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        return False
    
    db.delete(ticket)
    db.commit()
    return True

# ---------------- Ticket Status CRUD ----------------
def get_ticket_status(db: Session, ticket_id: int):
    """
    Get detailed status and statistics for a specific ticket
    """
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        return None
    
    sold_quantity = ticket.ticket_total_quantity - ticket.ticket_remaining_quantity
    sales_percentage = (sold_quantity / ticket.ticket_total_quantity * 100) if ticket.ticket_total_quantity > 0 else 0
    revenue_generated = sold_quantity * ticket.ticket_price
    
    # Check if ticket is currently on sale
    # REMOVED: sales_start and sales_end logic since these fields don't exist
    is_on_sale = ticket.ticket_remaining_quantity > 0  # Simple check based on availability
    
    return {
        "ticket_id": ticket.ticket_id,
        "ticket_price": ticket.ticket_price,
        "total_quantity": ticket.ticket_total_quantity,
        "remaining_quantity": ticket.ticket_remaining_quantity,
        "sold_quantity": sold_quantity,
        "sales_percentage": round(sales_percentage, 2),
        "revenue_generated": revenue_generated,
        "is_on_sale": is_on_sale
    }

def get_event_tickets_status(db: Session, event_id: int):
    """
    Get comprehensive status for all tickets in an event
    """
    # Verify event exists
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        return None
    
    tickets = db.query(Ticket).filter(Ticket.event_id == event_id).all()
    if not tickets:
        return None
    
    ticket_statuses = []
    total_tickets = 0
    total_sold = 0
    total_revenue = 0
    
    for ticket in tickets:
        status = get_ticket_status(db, ticket.ticket_id)
        if status:
            ticket_statuses.append(status)
            total_tickets += ticket.ticket_total_quantity
            total_sold += status["sold_quantity"]
            total_revenue += status["revenue_generated"]
    
    total_remaining = total_tickets - total_sold
    overall_sales_percentage = (total_sold / total_tickets * 100) if total_tickets > 0 else 0
    
    return {
        "event_id": event_id,
        "total_tickets": total_tickets,
        "total_sold": total_sold,
        "total_remaining": total_remaining,
        "total_revenue": total_revenue,
        "overall_sales_percentage": round(overall_sales_percentage, 2),
        "ticket_statuses": ticket_statuses
    }