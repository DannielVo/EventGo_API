from sqlalchemy.orm import Session
from ...organizer.models.models import Event, Organizer, Ticket  # Fixed import path
from ...organizer.schemas.event_schemas import EventCreate, EventUpdate  # Fixed import path

def create_event(db: Session, event: EventCreate):
    """
    Create a new event
    """
    # Verify organizer exists
    organizer = db.query(Organizer).filter(Organizer.organizer_id == event.organizer_id).first()
    if not organizer:
        return None
    
    new_event = Event(
        organizer_id=event.organizer_id,
        event_title=event.event_title,
        event_description=event.event_description,
        event_category=event.event_category,
        event_date=event.event_date,
        event_location=event.event_location,
        event_status=event.event_status
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

def get_events_by_organizer(db: Session, organizer_id: int):
    """
    Get all events for a specific organizer
    """
    # Verify organizer exists
    organizer = db.query(Organizer).filter(Organizer.organizer_id == organizer_id).first()
    if not organizer:
        return None
    
    return db.query(Event).filter(Event.organizer_id == organizer_id).all()

def get_event_by_id(db: Session, event_id: int):
    """
    Get specific event by ID
    """
    return db.query(Event).filter(Event.event_id == event_id).first()

def update_event(db: Session, event_id: int, data: EventUpdate):
    """
    Update event information
    """
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        return None
    
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)
    
    db.commit()
    db.refresh(event)
    return event

def delete_event(db: Session, event_id: int):
    """
    Delete an event
    """
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        return False
    
    db.delete(event)
    db.commit()
    return True

def get_event_statistics(db: Session, event_id: int):
    """
    Get statistics for an event
    """
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        return None
    
    tickets = db.query(Ticket).filter(Ticket.event_id == event_id).all()
    if not tickets:
        return {
            "event_id": event_id,
            "total_tickets": 0,
            "sold_tickets": 0,
            "remaining_tickets": 0,
            "total_revenue": 0.0
        }
    
    total = sum(t.ticket_total_quantity for t in tickets)
    remaining = sum(t.ticket_remaining_quantity for t in tickets)
    sold = total - remaining
    revenue = sum((t.ticket_total_quantity - t.ticket_remaining_quantity) * t.ticket_price for t in tickets)
    
    return {
        "event_id": event_id,
        "total_tickets": total,
        "sold_tickets": sold,
        "remaining_tickets": remaining,
        "total_revenue": revenue
    }