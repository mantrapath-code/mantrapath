import asyncio
import os
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import structlog

from core.ai_processor import AIEventProcessor
from core.emotion_analyzer import EmotionAnalyzer
from core.cultural_intelligence import CulturalIntelligenceProcessor
from core.predictive_engine import PredictiveInterventionEngine
from models.ai_models import (
    EmotionAnalysisRequest,
    EmotionAnalysisResponse,
    ContextUpdateRequest,
    PredictiveAnalysisResponse,
    PredictiveAnalysisResult
)

logger = structlog.get_logger(__name__)

# Global services
ai_processor: Optional[AIEventProcessor] = None
emotion_analyzer: Optional[EmotionAnalyzer] = None
cultural_processor: Optional[CulturalIntelligenceProcessor] = None
predictive_engine: Optional[PredictiveInterventionEngine] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global ai_processor, emotion_analyzer, cultural_processor, predictive_engine
    
    logger.info("Starting AI Event Processor Service initialization")
    
    try:
        # Initialize core services
        ai_processor = AIEventProcessor()
        emotion_analyzer = EmotionAnalyzer()
        cultural_processor = CulturalIntelligenceProcessor()
        predictive_engine = PredictiveInterventionEngine()
        
        # Start the services
        await ai_processor.start()
        await emotion_analyzer.start()
        await cultural_processor.start()
        await predictive_engine.start()
        
        logger.info("AI Event Processor Service started successfully")
        yield
        
    except Exception as e:
        logger.error("Failed to start AI Event Processor Service", error=str(e))
        raise
    finally:
        # Cleanup
        if ai_processor:
            await ai_processor.stop()
        if emotion_analyzer:
            await emotion_analyzer.stop()
        if cultural_processor:
            await cultural_processor.stop()
        if predictive_engine:
            await predictive_engine.stop()
        
        logger.info("AI Event Processor Service stopped")

async def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="AI Event Processor Service",
        description="Real-time AI processing pipeline for MantraPath V3",
        version="3.0.0",
        lifespan=lifespan
    )
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        try:
            status = {
                "status": "healthy",
                "service": "ai-event-processor",
                "version": "3.0.0",
                "components": {
                    "ai_processor": ai_processor.health_check() if ai_processor else False,
                    "emotion_analyzer": emotion_analyzer.health_check() if emotion_analyzer else False,
                    "cultural_processor": cultural_processor.health_check() if cultural_processor else False,
                    "predictive_engine": predictive_engine.health_check() if predictive_engine else False,
                }
            }
            return status
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            raise HTTPException(status_code=503, detail="Service unhealthy")
    
    @app.get("/health/live")
    async def liveness_check():
        """Kubernetes liveness probe"""
        return {"status": "alive"}
    
    @app.get("/health/ready")
    async def readiness_check():
        """Kubernetes readiness probe"""
        if not ai_processor or not ai_processor.is_ready():
            raise HTTPException(status_code=503, detail="Service not ready")
        return {"status": "ready"}
    
    @app.post("/api/v1/analyze/emotion", response_model=EmotionAnalysisResponse)
    async def analyze_emotion(request: EmotionAnalysisRequest):
        """Analyze emotion from text or voice data"""
        try:
            if not emotion_analyzer:
                raise HTTPException(status_code=503, detail="Emotion analyzer not available")
            
            result = await emotion_analyzer.analyze(
                text=request.text,
                language=request.language,
                user_id=request.user_id,
                context=request.context
            )
            
            # Create EmotionAnalysisResponse with proper field mapping
            return EmotionAnalysisResponse(
                user_id=request.user_id,
                result=result,
                processing_time_ms=result.processing_time_ms or 0.0,
                timestamp=datetime.now(timezone.utc),
                language=result.language or request.language,
                cultural_adaptation={
                    "adapted_culture": result.language if result.language != "en" else None,
                    "adaptation_applied": result.has_cultural_adaptation,
                    "cultural_context": result.cultural_context
                } if result.has_cultural_adaptation else None
            )
            
        except Exception as e:
            logger.error("Emotion analysis failed", error=str(e), user_id=request.user_id)
            raise HTTPException(status_code=500, detail="Emotion analysis failed")
    
    @app.post("/api/v1/context/update")
    async def update_context(request: ContextUpdateRequest, background_tasks: BackgroundTasks):
        """Update AI context with new data"""
        try:
            if not ai_processor:
                raise HTTPException(status_code=503, detail="AI processor not available")
            
            # Process context update asynchronously
            background_tasks.add_task(
                ai_processor.update_context,
                user_id=request.user_id,
                context_data=request.context_data,
                source=request.source
            )
            
            return {"status": "accepted", "message": "Context update queued"}
            
        except Exception as e:
            logger.error("Context update failed", error=str(e), user_id=request.user_id)
            raise HTTPException(status_code=500, detail="Context update failed")
    
    @app.get("/api/v1/predict/intervention/{user_id}", response_model=PredictiveAnalysisResponse)
    async def predict_intervention(user_id: str):
        """Get predictive intervention analysis for user"""
        try:
            if not predictive_engine:
                raise HTTPException(status_code=503, detail="Predictive engine not available")
            
            analysis = await predictive_engine.analyze_intervention_needs(user_id)
            
            # Create proper response structure
            result = PredictiveAnalysisResult(
                intervention_needed=analysis["intervention_needed"],
                confidence=analysis["confidence"],
                intervention_type=analysis.get("intervention_type"),
                urgency_level=analysis["urgency_level"],
                recommended_actions=analysis["recommended_actions"],
                cultural_considerations=analysis.get("cultural_considerations")
            )
            
            # Extract factor names from risk_factors dictionary
            risk_factors_dict = analysis.get("risk_factors", {})
            factors_analyzed = list(risk_factors_dict.keys()) if isinstance(risk_factors_dict, dict) else []
            
            return PredictiveAnalysisResponse(
                user_id=user_id,
                result=result,
                processing_time_ms=analysis["processing_time_ms"],
                factors_analyzed=factors_analyzed
            )
            
        except Exception as e:
            logger.error("Predictive analysis failed", error=str(e), user_id=user_id)
            raise HTTPException(status_code=500, detail="Predictive analysis failed")
    
    @app.get("/api/v1/metrics")
    async def get_metrics():
        """Get service metrics"""
        try:
            metrics = {}
            
            if ai_processor:
                metrics["ai_processor"] = await ai_processor.get_metrics()
            if emotion_analyzer:
                metrics["emotion_analyzer"] = await emotion_analyzer.get_metrics()
            if cultural_processor:
                metrics["cultural_processor"] = await cultural_processor.get_metrics()
            if predictive_engine:
                metrics["predictive_engine"] = await predictive_engine.get_metrics()
            
            return metrics
            
        except Exception as e:
            logger.error("Failed to get metrics", error=str(e))
            raise HTTPException(status_code=500, detail="Failed to get metrics")
    
    return app
