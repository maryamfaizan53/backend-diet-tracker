# py
from fastapi import APIRouter
from app.api.routes import ai, health, users

api_router = APIRouter()
api_router.include_router(ai.router, prefix="", tags=["ai"])
api_router.include_router(health.router, prefix="", tags=["health"])
api_router.include_router(users.router, prefix="", tags=["users"])
