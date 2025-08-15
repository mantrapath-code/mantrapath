"""
Action Orchestrator Service - Main Application
Voice-driven cross-service workflow coordination
"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.api.endpoints import router
from src.services import create_orchestrator, shutdown_orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    
    # Startup
    logger.info("Starting Action Orchestrator Service...")
    
    try:
        # Initialize orchestrator
        await create_orchestrator()
        logger.info("Action Orchestrator initialized successfully")
        
        yield
        
    finally:
        # Shutdown
        logger.info("Shutting down Action Orchestrator Service...")
        await shutdown_orchestrator()
        logger.info("Action Orchestrator shutdown completed")


# Create FastAPI application
app = FastAPI(
    title="MantraPath Action Orchestrator",
    description="Voice-driven cross-service workflow coordination service",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "MantraPath Action Orchestrator",
        "version": "1.0.0",
        "status": "running",
        "description": "Voice-driven cross-service workflow coordination"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "action_orchestrator",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable, default to 8012
    port = int(os.getenv("ORCHESTRATOR_PORT", "8012"))
    host = os.getenv("ORCHESTRATOR_HOST", "0.0.0.0")
    
    print(f"🚀 Starting Action Orchestrator Service on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
