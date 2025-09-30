from fastapi import APIRouter

from app.router.mapping import router as mappings_router
from app.router.model import router as models_router

api_router = APIRouter()
api_router.include_router(mappings_router)
api_router.include_router(models_router)
