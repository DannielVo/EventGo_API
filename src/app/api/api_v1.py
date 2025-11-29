from fastapi import APIRouter
from ..general import router as general_router
from ..organizer import organizer_api_router as organizer_router


api_router = APIRouter()

api_router.include_router(general_router.router)
api_router.include_router(organizer_router.router)
