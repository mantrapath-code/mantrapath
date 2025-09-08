"""
API Routes Package
Contains all API route definitions for the voice service
"""

from .voice_routes import router as voice_router
from .conversation_routes import router as conversation_router
from .session_routes import router as session_router
from .health_routes import router as health_router

__all__ = ["voice_router", "conversation_router", "session_router", "health_router"]
