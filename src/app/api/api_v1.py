from fastapi import APIRouter
from app.general import router as general_router

api_router = APIRouter()

api_router.include_router(general_router.router)
