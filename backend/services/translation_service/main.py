"""
MantraPath Translation Service
High-performance, scalable translation service with cultural adaptation
"""
import asyncio
import logging
import sys
import os
import time
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import redis.asyncio as redis

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from config.settings import TranslationSettings
from engines.enhanced_multi_translator import EnhancedMultiTranslator
from models.request_models import (
    TranslationRequest, TranslationResponse, VoiceTranslationRequest, 
    VoiceTranslationResponse, BatchTranslationRequest, BatchTranslationResponse,
    LanguageDetectionRequest, LanguageDetectionResponse, TranslationFeedbackRequest,
    CustomGlossaryRequest, SupportedLanguagesResponse, TranslationStatsResponse,
    HealthCheckResponse, ErrorResponse, LanguageInfo
)
from shared.auth import get_current_user
from shared.database import get_db, create_tables
from shared.events import get_event_bus, EventChannels
from shared.redis_client import redis_client as shared_redis_client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
translation_requests = Counter(
    'translation_requests_total',
    'Total translation requests',
    ['source_language', 'target_language', 'engine', 'status']
)

translation_duration = Histogram(
    'translation_duration_seconds',
    'Translation processing time',
    ['source_language', 'target_language', 'engine']
)

cache_hits = Counter(
    'translation_cache_hits_total',
    'Translation cache hits',
    ['source_language', 'target_language']
)

# Global instances
translation_engine = EnhancedMultiTranslator()
async_redis_client = None
event_bus = None
settings = TranslationSettings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global async_redis_client, event_bus
    
    logger.info("Starting Translation Service...")
    
    try:
        # Initialize Redis (async version for this service)
        async_redis_client = redis.from_url(settings.redis_url)
        await async_redis_client.ping()
        logger.info("Redis connection established")
        
        # Initialize event bus
        event_bus = get_event_bus()
        logger.info("Event bus initialized")
        
        # Initialize translation engine
        if await translation_engine.initialize():
            logger.info("Translation engine initialized successfully")
        else:
            logger.error("Failed to initialize translation engine")
            raise RuntimeError("Translation engine initialization failed")
        
        # Create database tables
        create_tables()
        logger.info("Database tables created/verified")
        
        logger.info("Translation Service started successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start Translation Service: {e}")
        raise
    finally:
        logger.info("Shutting down Translation Service...")
        if async_redis_client:
            await async_redis_client.close()
        logger.info("Translation Service shutdown complete")

app = FastAPI(
    title="MantraPath Translation Service",
    description="High-performance translation service with cultural adaptation and meditation-specific terminology",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="internal_server_error",
            message="An unexpected error occurred"
        ).dict()
    )

# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Service health check"""
    try:
        # Check translation engine
        engine_health = await translation_engine.health_check()
        
        # Check Redis
        redis_status = "healthy"
        try:
            if async_redis_client:
                await async_redis_client.ping()
            else:
                redis_status = "unhealthy"
        except Exception:
            redis_status = "unhealthy"
        
        # Check database
        db_status = "healthy"  # Simple check for now
        
        return HealthCheckResponse(
            status="healthy" if engine_health["status"] == "healthy" and redis_status == "healthy" else "degraded",
            timestamp=datetime.now(),
            version=settings.service_version,
            engines_status={"local": engine_health["status"]},
            cache_status=redis_status,
            database_status=db_status,
            uptime_seconds=int(time.time())  # Simplified uptime
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )

# Core translation endpoints
@app.post("/translate", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    current_user = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Translate text with cultural adaptation and custom terminology"""
    start_time = time.time()
    
    try:
        # Perform translation
        context = {
            "user_id": current_user.id if current_user else None,
            "engine": request.engine.value,
            "domain": request.domain,
            "use_cache": request.use_cache,
            "cultural_adaptation": request.cultural_adaptation,
            "use_custom_glossary": request.use_custom_glossary
        }
        
        result = await translation_engine.translate(
            text=request.text,
            target_language=request.target_language,
            source_language=request.source_language or "auto",
            context=context
        )
        
        # Record metrics
        processing_time = time.time() - start_time
        translation_duration.labels(
            source_language=result.get("source_language", request.source_language or "unknown"),
            target_language=result.get("target_language", request.target_language),
            engine=result.get("engine", request.engine.value)
        ).observe(processing_time)
        
        translation_requests.labels(
            source_language=result.get("source_language", request.source_language or "unknown"),
            target_language=result.get("target_language", request.target_language),
            engine=result.get("engine", request.engine.value),
            status="success"
        ).inc()
        
        if result.get("cache_hit"):
            cache_hits.labels(
                source_language=result.get("source_language", request.source_language or "unknown"),
                target_language=result.get("target_language", request.target_language)
            ).inc()
        
        # Publish event
        background_tasks.add_task(
            publish_translation_event,
            result,
            current_user.id if current_user else None
        )
        
        return TranslationResponse(
            translated_text=result.get("translated_text", ""),
            source_language=result.get("source_language", request.source_language or "unknown"),
            target_language=result.get("target_language", request.target_language),
            confidence_score=result.get("confidence_score", 0.0),
            quality_score=result.get("quality_score", 0.0),
            engine_used=result.get("engine", request.engine.value),
            processing_time_ms=result.get("processing_time_ms", int(processing_time * 1000)),
            cache_hit=result.get("cache_hit", False),
            cultural_adaptations_applied=result.get("cultural_notes", []),
            custom_terms_used=result.get("custom_terms_used", []),
            request_id=result.get("request_id", ""),
            status="completed"
        )
        
    except Exception as e:
        # Record failure metrics
        translation_requests.labels(
            source_language=request.source_language or "unknown",
            target_language=request.target_language,
            engine=request.engine.value,
            status="error"
        ).inc()
        
        logger.error(f"Translation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )

@app.post("/translate/batch", response_model=BatchTranslationResponse)
async def translate_batch(
    request: BatchTranslationRequest,
    current_user = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Translate multiple texts efficiently"""
    start_time = time.time()
    
    try:
        # Prepare batch requests
        batch_requests = []
        for text in request.texts:
            batch_requests.append({
                'text': text,
                'target_language': request.target_language,
                'source_language': request.source_language or "auto",
                'context': {
                    "user_id": current_user.id if current_user else None,
                    "engine": request.engine.value,
                    "domain": request.domain,
                    "use_cache": True,
                    "cultural_adaptation": request.cultural_adaptation,
                    "use_custom_glossary": request.use_custom_glossary
                }
            })
        
        results = await translation_engine.translate_batch(batch_requests)
        
        # Convert to response format
        translations = []
        success_count = 0
        failure_count = 0
        
        for i, result in enumerate(results):
            if result.get('status') == 'success':
                translations.append(TranslationResponse(
                    translated_text=result.get('translated_text', ''),
                    source_language=result.get('source_language', request.source_language or 'unknown'),
                    target_language=result.get('target_language', request.target_language),
                    confidence_score=result.get('confidence_score', 0.0),
                    quality_score=result.get('quality_score', 0.0),
                    engine_used=result.get('engine', 'multi'),
                    processing_time_ms=result.get('processing_time_ms', 0),
                    cache_hit=result.get('cache_hit', False),
                    cultural_adaptations_applied=result.get('cultural_adaptations_applied', []),
                    custom_terms_used=result.get('custom_terms_used', []),
                    request_id=f"batch_{i}",
                    status="completed"
                ))
                success_count += 1
            else:
                failure_count += 1
        
        total_processing_time = int((time.time() - start_time) * 1000)
        
        return BatchTranslationResponse(
            translations=translations,
            total_processing_time_ms=total_processing_time,
            success_count=success_count,
            failure_count=failure_count,
            batch_id=f"batch_{int(time.time())}"
        )
        
    except Exception as e:
        logger.error(f"Batch translation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch translation failed: {str(e)}"
        )

@app.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(request: LanguageDetectionRequest):
    """Detect the language of input text"""
    start_time = time.time()
    
    try:
        result = await translation_engine.detect_language(text=request.text)
        
        # Extract language and confidence from result
        if isinstance(result, dict):
            detected_language = result.get("language", "unknown")
            confidence = result.get("confidence", 0.0)
        else:
            detected_language = "unknown"
            confidence = 0.0
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return LanguageDetectionResponse(
            detected_language=detected_language,
            confidence_score=confidence,
            alternative_languages=[],  # TODO: Implement alternatives
            processing_time_ms=processing_time,
            engine_used="google"  # TODO: Track actual engine used
        )
        
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Language detection failed: {str(e)}"
        )

@app.get("/languages", response_model=SupportedLanguagesResponse)
async def get_supported_languages():
    """Get list of supported languages with capabilities"""
    try:
        from config.settings import SUPPORTED_LANGUAGES, TIER_CONFIGURATIONS
        
        languages = []
        for code, info in SUPPORTED_LANGUAGES.items():
            tier = info.get("tier", 3)
            tier_config = TIER_CONFIGURATIONS.get(tier, {})
            
            languages.append(LanguageInfo(
                code=code,
                name=info["name"],
                native_name=info["native"],
                rtl=info.get("rtl", False),
                tier=tier,
                features=tier_config.get("features", [])
            ))
        
        return SupportedLanguagesResponse(
            languages=languages,
            total_count=len(languages),
            tiers=TIER_CONFIGURATIONS
        )
        
    except Exception as e:
        logger.error(f"Failed to get supported languages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get supported languages"
        )

# Utility functions
async def publish_translation_event(result, user_id: Optional[str]):
    """Publish translation event to event bus"""
    try:
        if event_bus:
            await event_bus.publish(
                EventChannels.TRANSLATION_COMPLETED,
                {
                    "user_id": user_id,
                    "source_language": result.source_language,
                    "target_language": result.target_language,
                    "engine_used": result.engine_name,
                    "processing_time_ms": result.processing_time_ms,
                    "confidence_score": result.confidence_score,
                    "quality_score": result.metadata.get("quality_score", 0.0),
                    "cache_hit": result.metadata.get("cache_hit", False)
                }
            )
    except Exception as e:
        logger.warning(f"Failed to publish translation event: {e}")

# Test endpoint without authentication for debugging
@app.post("/test/translate")
async def test_translate_text(request: TranslationRequest):
    """Test translation without authentication - for debugging only"""
    start_time = time.time()
    
    try:
        # Perform translation
        context = {
            "domain": request.domain,
            "cultural_adaptation": request.cultural_adaptation
        }
        
        result = await translation_engine.translate(
            text=request.text,
            target_language=request.target_language,
            source_language=request.source_language or "auto",
            context=context
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "translated_text": result.get("translated_text", ""),
            "source_language": result.get("source_language", request.source_language),
            "target_language": result.get("target_language", request.target_language),
            "confidence_score": result.get("confidence", 0.0),
            "processing_time_ms": round(processing_time, 2),
            "engine_used": result.get("engine", "local"),
            "cached": result.get("cached", False)
        }
        
    except Exception as e:
        logger.error(f"Test translation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_level="info",
        reload=settings.debug
    )