"""
MantraPath Models Service
Centralized model management, training, and inference service
Serves STT, TTS, and NLP models to other services via REST API
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
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
# Temporarily disable NLPEngine due to import issues
# from models.nlp_engine import NLPEngine
from models.model_manager import ModelManager
from api.routes import router as api_router
from api.translation_routes import router as translation_router, set_models_service
# from api.emotion_routes import router as emotion_router
# from api.translation_routes_ollama import router as ollama_translation_router
from api.text_generation_routes import router as text_generation_router
from config.settings import get_settings
from utils.logger import setup_logger

# Setup
settings = get_settings()
logger = setup_logger(__name__)

# Global components
stt_engine: Optional[STTEngine] = None
tts_engine: Optional[TTSEngine] = None
nlp_engine: Optional[Any]  # NLPEngine temporarily disabled = None
model_manager: Optional[ModelManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global stt_engine, tts_engine, nlp_engine, model_manager
    
    # Startup
    logger.info("🚀 Starting MantraPath Models Service...")
    
    # Check if we're in minimal mode
    minimal_mode = os.environ.get("MODELS_SERVICE_MODE") == "minimal"
    if minimal_mode:
        logger.info("🔧 Running in MINIMAL MODE - models will load on-demand")
    
    try:
        # Initialize model manager
        model_manager = ModelManager(settings.MODELS_DIR)
        await model_manager.initialize()
        
        # Initialize engines
        stt_engine = STTEngine(model_manager)
        tts_engine = TTSEngine(model_manager)
        # nlp_engine = NLPEngine(model_manager)  # Temporarily disabled
        
        # Optional preload list (comma separated)
        preload_list_env = os.getenv("MODELS_PRELOAD_LIST", "").strip()
        background_preload = os.getenv("MODELS_PRELOAD_BACKGROUND", "true").lower() == "true"

        if minimal_mode:
            logger.info("✅ Models Service initialized in minimal mode (skipping default model loading)")
        else:
            # Load defaults unless user explicitly wants to skip (when providing custom preload list and setting skip flag)
            skip_defaults = os.getenv("MODELS_SERVICE_SKIP_DEFAULTS", "false").lower() == "true"
            if skip_defaults and preload_list_env:
                logger.info("⚙️  Skipping default model loads due to MODELS_SERVICE_SKIP_DEFAULTS=true")
            else:
                await stt_engine.load_default_models()
                await tts_engine.load_default_models()
                await nlp_engine.load_default_models()

        # Handle custom preload list (works in both minimal and normal modes)
        if preload_list_env:
            models_to_preload = [m.strip() for m in preload_list_env.split(',') if m.strip()]
            if models_to_preload:
                logger.info(f"📥 Requested preload of models: {models_to_preload} (background={background_preload})")

                async def _preload_models():
                    for model_name in models_to_preload:
                        try:
                            if model_manager.is_model_available(model_name):
                                logger.info(f"✅ Model already available: {model_name}")
                                continue
                            await model_manager.download_model(model_name)
                        except Exception as e:
                            logger.error(f"❌ Failed to preload {model_name}: {e}")
                    logger.info("🎯 Preload sequence complete")

                if background_preload:
                    # Launch without blocking startup
                    asyncio.create_task(_preload_models())
                else:
                    await _preload_models()
        
        # Set models service reference for translation routes
        set_models_service(nlp_engine)
        
        logger.info("✅ Models Service initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Models Service: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Models Service...")
    
    if model_manager:
        await model_manager.cleanup()
    
    logger.info("✅ Models Service shutdown complete")

# FastAPI app
app = FastAPI(
    title="MantraPath Models Service",
    description="Centralized AI Models Service for STT, TTS, NLP, and Training",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Global components
stt_engine: Optional[STTEngine] = None
tts_engine: Optional[TTSEngine] = None
nlp_engine: Optional[Any]  # NLPEngine temporarily disabled = None
model_manager: Optional[ModelManager] = None

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            "stt_loaded": len(stt_engine.loaded_models) if stt_engine and hasattr(stt_engine, 'loaded_models') else 0,
            "tts_loaded": len(tts_engine.loaded_models) if tts_engine and hasattr(tts_engine, 'loaded_models') else 0,
            "nlp_loaded": len(nlp_engine.loaded_models) if nlp_engine and hasattr(nlp_engine, 'loaded_models') else 0
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
app.include_router(translation_router, prefix="/api/v1/translation", tags=["translation"])

# Include new Ollama-based routes for centralized model service (temporarily commented out)
# app.include_router(emotion_router, tags=["emotion"])  # Includes /api/v1/emotion/*
# app.include_router(ollama_translation_router, prefix="/api/v1/translation/ollama", tags=["ollama-translation"])
app.include_router(text_generation_router, tags=["text-generation"])  # Includes /api/v1/nlp/*

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
