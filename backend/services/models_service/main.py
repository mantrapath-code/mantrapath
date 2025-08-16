"""
MantraPath Models Service
Centralized model management, training, and inference service
Serves STT, TTS, and NLP models to other services via REST API
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import asyncio
import logging
from pathlib import Path
import json
from datetime import datetime
import os
from typing import Dict, List, Optional, Any
import torch
import psutil

from models.stt_engine import STTEngine
from models.tts_engine import TTSEngine  
from models.nlp_engine import NLPEngine
from models.model_manager import ModelManager
from api.routes import router as api_router
from config.settings import get_settings
from utils.logger import setup_logger

# Setup
settings = get_settings()
logger = setup_logger(__name__)

# FastAPI app
app = FastAPI(
    title="MantraPath Models Service",
    description="Centralized AI Models Service for STT, TTS, NLP, and Training",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global components
stt_engine: Optional[STTEngine] = None
tts_engine: Optional[TTSEngine] = None
nlp_engine: Optional[NLPEngine] = None
model_manager: Optional[ModelManager] = None

@app.on_event("startup")
async def startup_event():
    """Initialize models and services on startup"""
    global stt_engine, tts_engine, nlp_engine, model_manager
    
    logger.info("🚀 Starting MantraPath Models Service...")
    
    try:
        # Initialize model manager
        model_manager = ModelManager(settings.MODELS_DIR)
        await model_manager.initialize()
        
        # Initialize engines
        stt_engine = STTEngine(model_manager)
        tts_engine = TTSEngine(model_manager)
        nlp_engine = NLPEngine(model_manager)
        
        # Load default models
        await stt_engine.load_default_models()
        await tts_engine.load_default_models()
        await nlp_engine.load_default_models()
        
        logger.info("✅ Models Service initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Models Service: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Models Service...")
    
    if model_manager:
        await model_manager.cleanup()
    
    logger.info("✅ Models Service shutdown complete")

# Health and Status endpoints
@app.get("/health")
async def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "models_service",
        "version": "1.0.0"
    }

@app.get("/status")
async def get_status():
    """Detailed service status"""
    gpu_available = torch.cuda.is_available()
    gpu_count = torch.cuda.device_count() if gpu_available else 0
    
    status = {
        "service": "models_service",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "running",
        "hardware": {
            "cpu_count": psutil.cpu_count(),
            "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "gpu_available": gpu_available,
            "gpu_count": gpu_count,
            "gpu_memory_gb": []
        },
        "models": {
            "stt_loaded": len(stt_engine.loaded_models) if stt_engine else 0,
            "tts_loaded": len(tts_engine.loaded_models) if tts_engine else 0,
            "nlp_loaded": len(nlp_engine.loaded_models) if nlp_engine else 0
        },
        "supported_languages": {
            "stt": list(stt_engine.supported_languages.keys()) if stt_engine else [],
            "tts": list(tts_engine.supported_languages.keys()) if tts_engine else []
        }
    }
    
    # Get GPU memory info
    if gpu_available:
        for i in range(gpu_count):
            props = torch.cuda.get_device_properties(i)
            status["hardware"]["gpu_memory_gb"].append(
                round(props.total_memory / (1024**3), 2)
            )
    
    return status

@app.get("/models/available")
async def get_available_models():
    """Get list of all available models"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not initialized")
    
    return await model_manager.get_available_models()

@app.get("/models/loaded")
async def get_loaded_models():
    """Get list of currently loaded models"""
    loaded = {
        "stt": list(stt_engine.loaded_models.keys()) if stt_engine else [],
        "tts": list(tts_engine.loaded_models.keys()) if tts_engine else [],
        "nlp": list(nlp_engine.loaded_models.keys()) if nlp_engine else []
    }
    return loaded

# Include API routes
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("MODELS_SERVICE_PORT", 8080))
    
    logger.info(f"Starting MantraPath Models Service on port {port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=port,
        reload=False,
        workers=1,  # Single worker for model sharing
        log_level="info",
        access_log=True
    )
