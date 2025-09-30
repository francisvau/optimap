from fastapi import FastAPI

from app.deps.database import lifespan
from app.router import api_router

app = FastAPI(lifespan=lifespan)

app.include_router(api_router)
