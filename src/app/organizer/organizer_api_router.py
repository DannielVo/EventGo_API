from fastapi import APIRouter
from ..organizer.routers import (
    event_router,
    organizer_router,
    attendee_router,
    notification_router,
    ticket_router
)

router = APIRouter()

router.include_router(event_router.router)
router.include_router(organizer_router.router)
router.include_router(attendee_router.router)
router.include_router(notification_router.router)
router.include_router(ticket_router.router)