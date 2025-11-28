from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List, Dict
from ...organizer.models.models import Event, Attendee  # Fixed import path
from ...general.models import Notification, User
from ...organizer.schemas.organizer_schemas import NotificationCreate, BroadcastCreate, NotificationType  # Fixed import path

def create_notification(db: Session, data: NotificationCreate):
    """
    Create a single notification for a specific user or as a broadcast
    """
    # Verify event exists
    event = db.query(Event).filter(Event.event_id == data.event_id).first()
    if not event:
        return None
    
    # Verify user exists if user_id is provided
    if data.user_id:
        user = db.query(User).filter(User.user_id == data.user_id).first()
        if not user:
            return None
    
    db_notif = Notification(
        title=data.title,
        message=data.message,
        type=data.type,
        event_id=data.event_id,
        user_id=data.user_id,  # NULL for broadcasts
        created_at=datetime.utcnow()
        # REMOVED: is_broadcast
    )
    db.add(db_notif)
    db.commit()
    db.refresh(db_notif)
    return db_notif

def get_notifications_by_event(db: Session, event_id: int, skip: int = 0, limit: int = 100):
    """
    Get all notifications for a specific event with pagination
    """
    # Verify event exists
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        return None
    
    return db.query(Notification).filter(
        Notification.event_id == event_id
    ).order_by(
        Notification.created_at.desc()
    ).offset(skip).limit(limit).all()

def get_notification_by_id(db: Session, notification_id: int):
    """
    Get specific notification by ID
    """
    return db.query(Notification).filter(Notification.notification_id == notification_id).first()

def send_broadcast_notification(db: Session, event_id: int, broadcast_data: BroadcastCreate, organizer_id: int):
    """
    Send broadcast notification to all attendees of an event
    """
    # Verify event exists and belongs to organizer
    event = db.query(Event).filter(
        Event.event_id == event_id,
        Event.organizer_id == organizer_id
    ).first()
    
    if not event:
        return None
    
    # Get recipients based on broadcast settings
    recipients = []
    
    if broadcast_data.send_to_attendees:
        # Get all attendees for the event
        attendees = db.query(Attendee).filter(Attendee.event_id == event_id).all()
        recipients.extend([attendee.user_id for attendee in attendees])
    
    # Note: Removed ticket_holders logic since your schema doesn't have direct user-ticket relationship
    # You might need to query through bookings table if you want ticket holders
    
    # Remove duplicates
    recipients = list(set(recipients))
    
    if not recipients and not broadcast_data.send_to_attendees:
        # If no specific recipients and not sending to attendees, create a single broadcast notification
        broadcast_notif = Notification(
            title=broadcast_data.title,
            message=broadcast_data.message,
            type=broadcast_data.type,
            event_id=event_id,
            user_id=None,  # NULL indicates broadcast
            created_at=datetime.utcnow()
        )
        db.add(broadcast_notif)
        db.commit()
        db.refresh(broadcast_notif)
        
        return {
            "success": True,
            "sent_count": 0,
            "failed_count": 0,
            "total_recipients": 0,
            "notification_ids": [broadcast_notif.notification_id]
        }
    
    # Create individual notifications for each recipient
    notification_ids = []
    sent_count = 0
    failed_count = 0
    
    for user_id in recipients:
        try:
            # Verify user exists
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                failed_count += 1
                continue
                
            notification = Notification(
                title=broadcast_data.title,
                message=broadcast_data.message,
                type=broadcast_data.type,
                event_id=event_id,
                user_id=user_id,
                created_at=datetime.utcnow()
            )
            db.add(notification)
            notification_ids.append(notification.notification_id)
            sent_count += 1
        except Exception as e:
            failed_count += 1
            continue
    
    db.commit()
    
    return {
        "success": True,
        "sent_count": sent_count,
        "failed_count": failed_count,
        "total_recipients": len(recipients),
        "notification_ids": notification_ids
    }

def get_notification_statistics(db: Session, event_id: int):
    """
    Get statistics for notifications of an event
    """
    # Verify event exists
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        return None
    
    # Total notifications
    total_notifications = db.query(Notification).filter(
        Notification.event_id == event_id
    ).count()
    
    # Broadcast vs individual (broadcast = user_id is NULL)
    broadcast_count = db.query(Notification).filter(
        Notification.event_id == event_id,
        Notification.user_id == None  # Broadcast notifications
    ).count()
    
    individual_count = db.query(Notification).filter(
        Notification.event_id == event_id,
        Notification.user_id != None  # Individual notifications
    ).count()
    
    # Count by type
    type_counts = db.query(
        Notification.type,
        func.count(Notification.notification_id)
    ).filter(
        Notification.event_id == event_id
    ).group_by(Notification.type).all()
    
    by_type = {ntype: count for ntype, count in type_counts}
    
    return {
        "event_id": event_id,
        "total_notifications": total_notifications,
        "broadcast_count": broadcast_count,
        "individual_count": individual_count,
        "by_type": by_type
    }

def delete_notification(db: Session, notification_id: int):
    """
    Delete a notification
    """
    notification = db.query(Notification).filter(Notification.notification_id == notification_id).first()
    if not notification:
        return False
    
    db.delete(notification)
    db.commit()
    return True

def get_user_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 50):
    """
    Get all notifications for a specific user
    """
    # Verify user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return None
    
    return db.query(Notification).filter(
        (Notification.user_id == user_id) | 
        (Notification.user_id == None)  # Include broadcast notifications
    ).order_by(
        Notification.created_at.desc()
    ).offset(skip).limit(limit).all()