from sqlalchemy.orm import Session
from datetime import datetime
from ...organizer.models.models import Attendee, Event
from ...general.models import User
from ...organizer.schemas.organizer_schemas import AttendeeCreate, AttendeeUpdate, CheckInStatus
import logging

logger = logging.getLogger(__name__)

def create_attendee(db: Session, data: AttendeeCreate):
    """
    Create a new attendee manually
    """
    # Verify event exists
    event = db.query(Event).filter(Event.event_id == data.event_id).first()
    if not event:
        return None
    
    # Verify user exists
    user = db.query(User).filter(User.user_id == data.user_id).first()
    if not user:
        return None
    
    db_attendee = Attendee(
        event_id=data.event_id,
        user_id=data.user_id,
        check_in_status=data.check_in_status,
        check_in_time=data.check_in_time
    )
    db.add(db_attendee)
    db.commit()
    db.refresh(db_attendee)
    return db_attendee

def get_attendees_by_event(db: Session, event_id: int):
    """
    Get all attendees for a specific event
    """
    # Verify event exists
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        return None
    
    return db.query(Attendee).filter(Attendee.event_id == event_id).all()

def get_attendee_by_id(db: Session, attendee_id: int):
    """
    Get specific attendee by ID
    """
    return db.query(Attendee).filter(Attendee.attendee_id == attendee_id).first()

def update_attendee_checkin(db: Session, attendee_id: int, data: AttendeeUpdate):
    """
    Update attendee check-in status
    """
    attendee = db.query(Attendee).filter(Attendee.attendee_id == attendee_id).first()
    if not attendee:
        return None
    
    # If checking in and no check-in time provided, set it to now
    if data.check_in_status == CheckInStatus.CHECKED_IN and not data.check_in_time:
        data.check_in_time = datetime.now()
    
    # If status is changing from checked_in to something else, clear check-in time
    if (data.check_in_status and 
        data.check_in_status != CheckInStatus.CHECKED_IN and 
        attendee.check_in_status == CheckInStatus.CHECKED_IN):
        data.check_in_time = None
    
    # Update only provided fields
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(attendee, key, value)
    
    db.commit()
    db.refresh(attendee)
    return attendee

def bulk_import_attendees(db: Session, event_id: int, attendees: list[dict]):
    """
    Bulk import attendees from CSV data
    """
    # Verify event exists
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        return None
    
    objs = []
    failed_rows = []
    
    for i, row in enumerate(attendees):
        try:
            # Validate required fields
            if 'user_id' not in row or not row['user_id']:
                failed_rows.append(i + 1)
                continue
            
            # Convert user_id to integer if it's a string
            if isinstance(row['user_id'], str):
                try:
                    row['user_id'] = int(row['user_id'])
                except ValueError:
                    failed_rows.append(i + 1)
                    continue
            
            # Verify user exists
            user = db.query(User).filter(User.user_id == row['user_id']).first()
            if not user:
                failed_rows.append(i + 1)
                continue
            
            # Create attendee object
            attendee_data = {
                'event_id': event_id,
                'user_id': row['user_id'],
                'check_in_status': CheckInStatus.PENDING,
                'check_in_time': None
            }
            
            obj = Attendee(**attendee_data)
            db.add(obj)
            objs.append(obj)
            
        except Exception as e:
            logger.error(f"Error processing row {i + 1}: {e}")
            failed_rows.append(i + 1)
            continue
    
    try:
        db.commit()
        # Refresh all objects to get their IDs
        for obj in objs:
            db.refresh(obj)
    except Exception as e:
        db.rollback()
        logger.error(f"Database error during bulk import: {e}")
        return None
    
    return {
        "imported_count": len(objs),
        "failed_rows": failed_rows,
        "total_rows": len(attendees),
        "attendees": objs
    }

def get_attendee_statistics(db: Session, event_id: int):
    """
    Get statistics for attendees of an event
    """
    attendees = db.query(Attendee).filter(Attendee.event_id == event_id).all()
    if not attendees:
        return None
    
    total_attendees = len(attendees)
    checked_in = len([a for a in attendees if a.check_in_status == CheckInStatus.CHECKED_IN])
    pending = len([a for a in attendees if a.check_in_status == CheckInStatus.PENDING])
    cancelled = len([a for a in attendees if a.check_in_status == CheckInStatus.CANCELLED])
    no_show = len([a for a in attendees if a.check_in_status == CheckInStatus.NO_SHOW])
    
    check_in_rate = (checked_in / total_attendees * 100) if total_attendees > 0 else 0
    
    return {
        "event_id": event_id,
        "total_attendees": total_attendees,
        "checked_in": checked_in,
        "pending": pending,
        "cancelled": cancelled,
        "no_show": no_show,
        "check_in_rate": round(check_in_rate, 2)
    }