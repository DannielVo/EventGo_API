from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
import csv
import io
import logging
from typing import List
from ...db.session import SessionLocal
from ...organizer.schemas.organizer_schemas import (  # Fixed import path
    AttendeeCreate, 
    AttendeeOut, 
    AttendeeUpdate,
    AttendeeImportResponse,
    CheckInUpdate,
    CheckInStatus
)
from ...organizer.crud.attendee_crud import (  # Fixed import path
    create_attendee, 
    get_attendees_by_event, 
    bulk_import_attendees,
    update_attendee_checkin,
    get_attendee_by_id,
    get_attendee_statistics
)

router = APIRouter(prefix="/attendees", tags=["Attendees"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

logger = logging.getLogger(__name__)

# -------- Add Attendee Manually --------
@router.post("/", response_model=AttendeeOut, status_code=status.HTTP_201_CREATED)
def add_attendee(data: AttendeeCreate, db: Session = Depends(get_db)):
    """
    Add attendee manually to an event
    """
    attendee = create_attendee(db, data)
    if not attendee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found or user does not exist"
        )
    return attendee

# -------- List Attendees for Event --------
@router.get("/event/{event_id}", response_model=List[AttendeeOut])
def list_attendees(event_id: int, db: Session = Depends(get_db)):
    """
    Show all attendees for a specific event
    """
    attendees = get_attendees_by_event(db, event_id)
    if attendees is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return attendees

# -------- Get Specific Attendee --------
@router.get("/{attendee_id}", response_model=AttendeeOut)
def get_attendee(attendee_id: int, db: Session = Depends(get_db)):
    """
    Get specific attendee by ID
    """
    attendee = get_attendee_by_id(db, attendee_id)
    if not attendee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendee not found"
        )
    return attendee

# -------- Update Attendee Check-In Status --------
@router.put("/{attendee_id}", response_model=AttendeeOut)
def update_attendee_checkin_status(
    attendee_id: int, 
    data: AttendeeUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update attendee check-in status and information
    """
    updated_attendee = update_attendee_checkin(db, attendee_id, data)
    if not updated_attendee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendee not found"
        )
    return updated_attendee

# -------- Quick Check-In Endpoint --------
@router.put("/{attendee_id}/checkin", response_model=AttendeeOut)
def quick_checkin(
    attendee_id: int, 
    data: CheckInUpdate, 
    db: Session = Depends(get_db)
):
    """
    Quick check-in endpoint specifically for updating check-in status
    """
    update_data = AttendeeUpdate(
        check_in_status=data.check_in_status
        # REMOVED: notes
    )
    
    if data.check_in_status == CheckInStatus.CHECKED_IN:
        from datetime import datetime
        update_data.check_in_time = datetime.now()
    
    updated_attendee = update_attendee_checkin(db, attendee_id, update_data)
    if not updated_attendee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendee not found"
        )
    return updated_attendee

# -------- Import Attendee List (CSV) --------
@router.post("/import/{event_id}", response_model=AttendeeImportResponse)
async def import_attendees(
    event_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """
    Upload CSV list of attendees for an event
    Expected CSV format: user_id
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    try:
        content = await file.read()
        csv_data = io.StringIO(content.decode("utf-8"))
        reader = csv.DictReader(csv_data)
        
        # Validate CSV has required columns
        if 'user_id' not in reader.fieldnames:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV must contain 'user_id' column"
            )
        
        attendees_data = list(reader)
        result = bulk_import_attendees(db, event_id, attendees_data)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        return AttendeeImportResponse(
            imported_count=result["imported_count"],
            failed_rows=result["failed_rows"],
            total_rows=result["total_rows"]
        )
        
    except Exception as e:
        logger.error(f"Error importing CSV: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing CSV file: {str(e)}"
        )

# -------- Get Attendee Statistics --------
@router.get("/event/{event_id}/statistics")
def get_event_attendee_statistics(event_id: int, db: Session = Depends(get_db)):
    """
    Get statistics for attendees of an event
    """
    stats = get_attendee_statistics(db, event_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found or no attendees"
        )
    return stats