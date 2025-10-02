"""
API package for Models Service
"""

from .routes import router
from .emotion_routes import router as emotion_router
__all__ = ['router', 'emotion_router']

