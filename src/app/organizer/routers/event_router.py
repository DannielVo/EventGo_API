from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...db.session import SessionLocal
from ...organizer.schemas.event_schemas import EventCreate, EventUpdate, EventOut, EventStatisticsOut
from ...organizer.crud.event_crud import (
    create_event, get_events_by_organizer, update_event, get_event_statistics,
    get_event_by_id, delete_event
)

router = APIRouter(prefix="/events", tags=["Events"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def add_event(event: EventCreate, db: Session = Depends(get_db)):
    """
    Add new event
    """
    new_event = create_event(db, event)
    if not new_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organizer not found"
        )
    return new_event

@router.get("/organizer/{organizer_id}", response_model=List[EventOut])
def list_events(organizer_id: int, db: Session = Depends(get_db)):
    """
    Get all events for an organizer
    """
    events = get_events_by_organizer(db, organizer_id)
    if events is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organizer not found"
        )
    return events

@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """
    Get specific event by ID
    """
    event = get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event

@router.put("/{event_id}", response_model=EventOut)
def edit_event(event_id: int, data: EventUpdate, db: Session = Depends(get_db)):
    """
    Edit / update event
    """
    updated = update_event(db, event_id, data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return updated

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_event(event_id: int, db: Session = Depends(get_db)):
    """
    Delete an event
    """
    success = delete_event(db, event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    # No content response

@router.get("/{event_id}/statistics", response_model=EventStatisticsOut)
def event_status(event_id: int, db: Session = Depends(get_db)):
    """
    Get event statistics (tickets sold, revenue, etc.)
    """
    stats = get_event_statistics(db, event_id)
    if stats is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return stats