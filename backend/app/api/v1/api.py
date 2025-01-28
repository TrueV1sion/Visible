from fastapi import APIRouter
from .endpoints import battlecards, users, auth, ai

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    battlecards.router, prefix="/battlecards", tags=["battlecards"]
)
api_router.include_router(ai.router, prefix="/ai", tags=["ai"]) 