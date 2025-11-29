from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from ...db.session import SessionLocal
from ...organizer.schemas.organizer_schemas import (
    OrganizerCreate, 
    OrganizerUpdate, 
    OrganizerOut,
    OrganizerStatsOut
)
from ...organizer.crud.organizer_crud import (
    create_organizer, 
    get_organizer_by_id, 
    update_organizer,
    get_all_organizers,
    get_organizer_by_user_id,
    delete_organizer,
    get_organizer_statistics
)

router = APIRouter(prefix="/organizers", tags=["Organizers"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------- Create Organizer --------
@router.post("/", response_model=OrganizerOut, status_code=status.HTTP_201_CREATED)
def add_organizer(data: OrganizerCreate, db: Session = Depends(get_db)):
    """
    Add a new organizer
    """
    organizer = create_organizer(db, data)
    if not organizer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organizer already exists for this user"
        )
    return organizer

# -------- Get All Organizers --------
@router.get("/", response_model=List[OrganizerOut])
def get_organizers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get all organizers with pagination
    """
    return get_all_organizers(db, skip=skip, limit=limit)

# -------- Get Organizer by ID --------
@router.get("/{organizer_id}", response_model=OrganizerOut)
def get_organizer(organizer_id: int, db: Session = Depends(get_db)):
    """
    Fetch organizer information by ID
    """
    organizer = get_organizer_by_id(db, organizer_id)
    if not organizer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organizer not found"
        )
    return organizer

# -------- Get Organizer by User ID --------
@router.get("/user/{user_id}", response_model=OrganizerOut)
def get_organizer_by_user(user_id: int, db: Session = Depends(get_db)):
    """
    Fetch organizer information by user ID
    """
    organizer = get_organizer_by_user_id(db, user_id)
    if not organizer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organizer not found for this user"
        )
    return organizer

# -------- Update Organizer Profile --------
@router.put("/{organizer_id}", response_model=OrganizerOut)
def edit_organizer(organizer_id: int, data: OrganizerUpdate, db: Session = Depends(get_db)):
    """
    Modify organizer account details
    """
    updated_organizer = update_organizer(db, organizer_id, data)
    if not updated_organizer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organizer not found"
        )
    return updated_organizer

# -------- Delete Organizer --------
@router.delete("/{organizer_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_organizer(organizer_id: int, db: Session = Depends(get_db)):
    """
    Delete organizer account
    Note: This is a hard delete. Consider soft delete for production.
    """
    success = delete_organizer(db, organizer_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organizer not found"
        )
    return {"message": "Organizer deleted successfully"}

# -------- Get Organizer Statistics --------
@router.get("/{organizer_id}/statistics", response_model=OrganizerStatsOut)
def get_organizer_stats(organizer_id: int, db: Session = Depends(get_db)):
    """
    Get comprehensive statistics for an organizer
    """
    stats = get_organizer_statistics(db, organizer_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organizer not found"
        )
    return stats