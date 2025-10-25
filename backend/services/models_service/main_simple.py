"""
MantraPath Models Service - Simplified Version
Only includes text generation with Qwen2.5-1.5B-Instruct
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
import os
from typing import Dict, List, Optional, Any

# Import routes
from api.text_generation_routes import router as text_generation_router
from api.simple_stt_routes import router as stt_router
from api.simple_tts_routes import router as tts_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting MantraPath Models Service (Simplified)")
    logger.info("   - Text Generation: Qwen2.5-1.5B-Instruct")
    logger.info("   - Speech-to-Text: IndicWav2Vec + Whisper")
    logger.info("   - Text-to-Speech: Indic-TTS + MMS")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down MantraPath Models Service")

# Create FastAPI app
app = FastAPI(
    title="MantraPath Models Service (Simplified)",
    description="Text generation service with Qwen2.5-1.5B-Instruct",
    version="1.0.0-simple",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes
app.include_router(text_generation_router)
app.include_router(stt_router)
app.include_router(tts_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "models-service-simple",
        "version": "1.0.0-simple",
        "features": ["text-generation", "speech-to-text", "text-to-speech"],
        "model": "Qwen2.5-1.5B-Instruct"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "MantraPath Models Service (Simplified)",
        "version": "1.0.0-simple",
        "description": "Text generation with Qwen2.5-1.5B-Instruct",
        "endpoints": {
            "text_generation": "/api/v1/nlp/generate",
            "speech_to_text": "/api/v1/stt/transcribe",
            "text_to_speech": "/api/v1/tts/synthesize",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    )
