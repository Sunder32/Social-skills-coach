"""
Main API Router
Aggregates all endpoint routers
"""
from fastapi import APIRouter
from app.api import users, chats, analysis, library, exercises

api_router = APIRouter()

# Include all routers
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(chats.router, prefix="/chats", tags=["Chats"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
api_router.include_router(library.router, prefix="/library", tags=["Library"])
api_router.include_router(exercises.router, prefix="/exercises", tags=["Exercises"])
