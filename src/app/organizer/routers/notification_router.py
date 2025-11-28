from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from ...db.session import SessionLocal
from ...organizer.schemas.organizer_schemas import (  # Fixed import path
    NotificationCreate, 
    NotificationOut, 
    BroadcastCreate,
    BroadcastResponse,
    NotificationStats
)
from ...organizer.crud.notification_crud import (  # Fixed import path
    create_notification, 
    get_notifications_by_event,
    get_notification_by_id,
    send_broadcast_notification,
    get_notification_statistics,
    delete_notification,
    get_user_notifications
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------- Send Individual Notification --------
@router.post("/", response_model=NotificationOut, status_code=status.HTTP_201_CREATED)
def send_notification(data: NotificationCreate, db: Session = Depends(get_db)):
    """
    Send a notification to a specific user or as a broadcast
    """
    notification = create_notification(db, data)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error sending notification: Event not found or user does not exist"
        )
    return notification

# -------- Send Broadcast Notification --------
@router.post("/event/{event_id}/broadcast", response_model=BroadcastResponse)
def send_broadcast_notification_endpoint(
    event_id: int,
    broadcast_data: BroadcastCreate,
    organizer_id: int = Query(..., description="Organizer ID for authorization"),
    db: Session = Depends(get_db)
):
    """
    Send broadcast message to all attendees of the event that the organizer owns
    """
    result = send_broadcast_notification(db, event_id, broadcast_data, organizer_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found or you don't have permission to send notifications for this event"
        )
    return result

# -------- List Notifications by Event --------
@router.get("/event/{event_id}", response_model=List[NotificationOut])
def list_notifications(
    event_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """
    View history of sent notifications for an event
    """
    notifications = get_notifications_by_event(db, event_id, skip=skip, limit=limit)
    if notifications is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    if not notifications:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No notifications found for this event"
        )
    return notifications

# -------- Get User Notifications --------
@router.get("/user/{user_id}", response_model=List[NotificationOut])
def get_user_notifications_endpoint(
    user_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get all notifications for a specific user (including broadcasts)
    """
    notifications = get_user_notifications(db, user_id, skip=skip, limit=limit)
    if notifications is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return notifications

# -------- Get Notification by ID --------
@router.get("/{notification_id}", response_model=NotificationOut)
def get_notification(notification_id: int, db: Session = Depends(get_db)):
    """
    Get specific notification by ID
    """
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return notification

# -------- Get Notification Statistics --------
@router.get("/event/{event_id}/statistics", response_model=NotificationStats)
def get_notification_statistics_endpoint(event_id: int, db: Session = Depends(get_db)):
    """
    Get statistics for notifications of an event
    """
    stats = get_notification_statistics(db, event_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return stats

# -------- Delete Notification --------
@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification_endpoint(notification_id: int, db: Session = Depends(get_db)):
    """
    Delete a notification
    """
    success = delete_notification(db, notification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    # No content response