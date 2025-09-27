"""API package initialization."""

from .mood_routes import router as mood_router
from .health_routes import router as health_router
from .actions_routes import router as actions_router

__all__ = ["mood_router", "health_router", "actions_router"]