from fastapi import FastAPI
from organizer.routers import event_router

app = FastAPI(title="Organizer API")
app.include_router(event_router.router)
