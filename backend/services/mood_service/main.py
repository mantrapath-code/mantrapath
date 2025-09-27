"""
MantraPath Mood Service - AI-powered emotion detection and mood tracking

A modular, production-ready service for:
- Emotion detection using GoEmotions AI model
- Mood tracking and analytics
- Memory service integration for chatbot context
- Real-time mood pattern analysis
"""

import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from src.core.config import settings
from src.api import mood_router, health_router, actions_router
from shared.database import create_tables
from src.services import memory_integration_service

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info(f"Starting {settings.service_name} v{settings.version}")
    
    # Create database tables
    try:
        create_tables()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    # Startup complete
    logger.info(f"Mood Service started on {settings.host}:{settings.port}")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Mood Service")
    try:
        await memory_integration_service.cleanup()
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


# Create FastAPI application
app = FastAPI(
    title="MantraPath Mood Service",
    description=__doc__,
    version=settings.version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(mood_router)
app.include_router(health_router)
app.include_router(actions_router)  # Action Orchestrator integration


@app.get("/")
async def root():
    """Root endpoint redirects to documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_root():
    """Simple health check at root level for Docker and monitoring."""
    return {"status": "healthy", "service": "mood-service"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Handle favicon requests."""
    return {"message": "No favicon"}


# Legacy endpoints for backward compatibility
@app.post("/mood", include_in_schema=False)
async def create_mood_legacy():
    """Legacy endpoint - redirects to new API."""
    return RedirectResponse(url="/api/v1/mood/entries", status_code=301)


@app.get("/mood", include_in_schema=False)
async def get_mood_legacy():
    """Legacy endpoint - redirects to new API."""
    return RedirectResponse(url="/api/v1/mood/entries", status_code=301)


@app.post("/analyze", include_in_schema=False)
async def analyze_legacy():
    """Legacy endpoint - redirects to new API."""
    return RedirectResponse(url="/api/v1/mood/analyze", status_code=301)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )