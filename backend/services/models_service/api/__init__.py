"""
API package for Models Service
"""

from .routes import router
# from .emotion_routes import router as emotion_router
# from .translation_routes_ollama import router as ollama_translation_router

__all__ = ['router']  # 'emotion_router', 'ollama_translation_router']

