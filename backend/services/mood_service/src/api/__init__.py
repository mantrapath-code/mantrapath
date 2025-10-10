"""API package initialization."""

from .journal_routes import router as journal_router
from .analytics_routes import router as analytics_router
from fastapi import APIRouter

# Create placeholder routers
mood_router = APIRouter(prefix="/api/v1/mood", tags=["mood"])
health_router = APIRouter(prefix="/health", tags=["health"])
actions_router = APIRouter(prefix="/api/v1/actions", tags=["actions"])

# Add basic health endpoint
@health_router.get("/")
async def health_check():
    return {"status": "healthy", "service": "mood-service"}

# Add basic mood endpoints placeholders
@mood_router.get("/entries")
async def get_mood_entries():
    return []

@mood_router.post("/entries")
async def create_mood_entry():
    return {"message": "Mood entry created"}

# Add basic actions endpoint
@actions_router.post("/")
async def handle_actions():
    return {"message": "Action handled"}

__all__ = ["mood_router", "health_router", "actions_router", "journal_router", "analytics_router"]