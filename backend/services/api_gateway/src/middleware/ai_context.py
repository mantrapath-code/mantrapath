"""
AI Context Middleware for MantraPath API Gateway V3
Provides AI-powered context injection and request enhancement
"""

from typing import Optional, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger(__name__)


class AIContextMiddleware(BaseHTTPMiddleware):
    """Middleware for AI context injection"""
    
    def __init__(self, app, ai_context_manager=None):
        super().__init__(app)
        self.ai_context_manager = ai_context_manager
    
    async def dispatch(self, request: Request, call_next):
        """Process request with AI context enhancement"""
        try:
            # Skip AI context for health checks and static files
            if request.url.path.startswith(("/health", "/docs", "/redoc", "/openapi.json")):
                return await call_next(request)
            
            # Add AI context to request if manager is available
            if self.ai_context_manager:
                ai_context = await self.ai_context_manager.get_context_from_request(request)
                if ai_context:
                    request.state.ai_context = ai_context
            
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.warning("AI context middleware error", error=str(e))
            return await call_next(request)