from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...db.session import SessionLocal
from ...organizer.schemas.ticket_schemas import TicketCreate, TicketUpdate, TicketOut, TicketStatusOut, EventTicketsStatusOut
from ...organizer.crud.ticket_crud import (
    create_ticket, 
    get_tickets_by_event, 
    get_ticket_by_id, 
    update_ticket, 
    delete_ticket,
    get_ticket_by_event_and_id,
    get_ticket_status,
    get_event_tickets_status
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------- Create Ticket Type for Specific Event --------
@router.post("/event/{event_id}", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket_type(event_id: int, ticket: TicketCreate, db: Session = Depends(get_db)):
    """
    Add ticket categories (VIP, Standard…) for a specific event
    """
    new_ticket = create_ticket(db, event_id, ticket)
    if not new_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found or ticket type does not exist"
        )
    return new_ticket

# -------- List Ticket Types for an Event --------
@router.get("/event/{event_id}", response_model=List[TicketOut])
def list_ticket_types(event_id: int, db: Session = Depends(get_db)):
    """
    Show all ticket types for a specific event
    """
    tickets = get_tickets_by_event(db, event_id)
    if tickets is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return tickets

# -------- Get Specific Ticket Type --------
@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket_type(ticket_id: int, db: Session = Depends(get_db)):
    """
    Get specific ticket type by ID
    """
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return ticket

# -------- Get Specific Ticket for Specific Event --------
@router.get("/event/{event_id}/{ticket_id}", response_model=TicketOut)
def get_event_ticket_type(event_id: int, ticket_id: int, db: Session = Depends(get_db)):
    """
    Get a specific ticket type that belongs to a specific event
    """
    ticket = get_ticket_by_event_and_id(db, event_id, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found for this event"
        )
    return ticket

# -------- Update Ticket Type --------
@router.put("/{ticket_id}", response_model=TicketOut)
def update_ticket_type(ticket_id: int, ticket_data: TicketUpdate, db: Session = Depends(get_db)):
    """
    Modify ticket information
    """
    updated_ticket = update_ticket(db, ticket_id, ticket_data)
    if not updated_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return updated_ticket

# -------- Delete Ticket Type --------
@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket_type(ticket_id: int, db: Session = Depends(get_db)):
    """
    Remove ticket type
    """
    success = delete_ticket(db, ticket_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    # No content response

# -------- Ticket Status Endpoints --------
@router.get("/{ticket_id}/status", response_model=TicketStatusOut)
def get_ticket_status_endpoint(ticket_id: int, db: Session = Depends(get_db)):
    """
    Get detailed status and statistics for a specific ticket
    """
    status = get_ticket_status(db, ticket_id)
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return status

@router.get("/event/{event_id}/status", response_model=EventTicketsStatusOut)
def get_event_tickets_status_endpoint(event_id: int, db: Session = Depends(get_db)):
    """
    Get comprehensive status for all tickets in an event
    """
    status = get_event_tickets_status(db, event_id)
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found or no tickets available"
        )
    return status