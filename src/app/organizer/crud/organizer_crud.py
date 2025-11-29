from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from ...organizer.models.models import Organizer, Event, Attendee, Ticket
from ...organizer.schemas.organizer_schemas import OrganizerCreate, OrganizerUpdate

def create_organizer(db: Session, data: OrganizerCreate):
    """
    Create a new organizer
    """
    # Check if organizer already exists for this user
    existing_organizer = db.query(Organizer).filter(Organizer.user_id == data.user_id).first()
    if existing_organizer:
        return None  # Or raise an exception
    
    db_org = Organizer(**data.dict())
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

def get_organizer_by_id(db: Session, organizer_id: int):
    """
    Get organizer by ID
    """
    return db.query(Organizer).filter(Organizer.organizer_id == organizer_id).first()

def get_organizer_by_user_id(db: Session, user_id: int):
    """
    Get organizer by user ID
    """
    return db.query(Organizer).filter(Organizer.user_id == user_id).first()

def update_organizer(db: Session, organizer_id: int, data: OrganizerUpdate):
    """
    Update organizer information
    """
    org = db.query(Organizer).filter(Organizer.organizer_id == organizer_id).first()
    if not org:
        return None
    
    # Update updated_at timestamp
    data_dict = data.dict(exclude_unset=True)
    data_dict['updated_at'] = datetime.now()
    
    for key, value in data_dict.items():
        setattr(org, key, value)
    
    db.commit()
    db.refresh(org)
    return org

def get_all_organizers(db: Session, skip: int = 0, limit: int = 100):
    """
    Get all organizers with pagination
    """
    return db.query(Organizer).offset(skip).limit(limit).all()

def delete_organizer(db: Session, organizer_id: int):
    """
    Delete organizer (soft delete or hard delete based on requirements)
    """
    org = db.query(Organizer).filter(Organizer.organizer_id == organizer_id).first()
    if not org:
        return False
    
    db.delete(org)
    db.commit()
    return True

def get_organizer_statistics(db: Session, organizer_id: int):
    """
    Get comprehensive statistics for an organizer
    """
    organizer = db.query(Organizer).filter(Organizer.organizer_id == organizer_id).first()
    if not organizer:
        return None
    
    # Get events count
    total_events = db.query(Event).filter(Event.organizer_id == organizer_id).count()
    
    # Get active events (events in the future)
    active_events = db.query(Event).filter(
        Event.organizer_id == organizer_id,
        Event.event_date >= datetime.now()
    ).count()
    
    # Get total attendees across all events
    total_attendees = db.query(Attendee).join(Event).filter(
        Event.organizer_id == organizer_id
    ).count()
    
    # Calculate total revenue
    revenue_result = db.query(
        func.sum((Ticket.ticket_total_quantity - Ticket.ticket_remaining_quantity) * Ticket.ticket_price)
    ).join(Event).filter(
        Event.organizer_id == organizer_id
    ).scalar()
    
    total_revenue = revenue_result if revenue_result else 0.0
    
    return {
        "organizer_id": organizer_id,
        "company_name": organizer.company_name,
        "total_events": total_events,
        "active_events": active_events,
        "total_attendees": total_attendees,
        "total_revenue": total_revenue
    }