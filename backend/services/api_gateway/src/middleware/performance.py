"""
Performance Middleware for MantraPath API Gateway V3
Provides performance monitoring and metrics collection
"""

import time
from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring"""
    
    def __init__(self, app, performance_monitor=None):
        super().__init__(app)
        self.performance_monitor = performance_monitor
    
    async def dispatch(self, request: Request, call_next):
        """Process request with performance monitoring"""
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            # Record metrics if monitor is available
            if self.performance_monitor:
                await self.performance_monitor.record_request(
                    path=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    processing_time=processing_time
                )
            
            # Add performance headers
            response.headers["X-Processing-Time"] = str(round(processing_time, 2))
            
            return response
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            
            # Record error metrics
            if self.performance_monitor:
                await self.performance_monitor.record_error(
                    path=request.url.path,
                    method=request.method,
                    error=str(e),
                    processing_time=processing_time
                )
            
            raise e