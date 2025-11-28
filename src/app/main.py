from fastapi import FastAPI
from .organizer.routers import (
    event_router,
    organizer_router,
    attendee_router,
    notification_router,
    ticket_router
)

app = FastAPI(title="Organizer API")

app.include_router(event_router.router)
app.include_router(organizer_router.router)
app.include_router(attendee_router.router)
app.include_router(notification_router.router)
app.include_router(ticket_router.router)
