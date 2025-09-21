"""
Cultural Context Middleware for MantraPath API Gateway V3
Provides cultural adaptation and localization support
"""

from typing import Optional, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger(__name__)


class CulturalContextMiddleware(BaseHTTPMiddleware):
    """Middleware for cultural context adaptation"""
    
    def __init__(self, app, cultural_manager=None):
        super().__init__(app)
        self.cultural_manager = cultural_manager
    
    async def dispatch(self, request: Request, call_next):
        """Process request with cultural context adaptation"""
        try:
            # Skip cultural context for health checks and static files
            if request.url.path.startswith(("/health", "/docs", "/redoc", "/openapi.json")):
                return await call_next(request)
            
            # Add cultural context to request if manager is available
            if self.cultural_manager:
                cultural_context = await self.cultural_manager.get_context_from_request(request)
                if cultural_context:
                    request.state.cultural_context = cultural_context
            
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.warning("Cultural context middleware error", error=str(e))
            return await call_next(request)