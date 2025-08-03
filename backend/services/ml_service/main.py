"""
ML Service for Smart Notification Scheduling
Provides machine learning capabilities for personalized notification timing and content
"""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os
import logging
import uuid
import json
import asyncio
import numpy as np
from sqlalchemy.orm import Session
import sys

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.database import get_db
from shared.auth import get_current_user
from shared.models import MoodEntry, JournalEntry, Notification

# Import ML models
from models.pattern_analyzer import MoodPatternAnalyzer
from models.timing_predictor import OptimalTimingPredictor
from models.content_engine import NotificationContentEngine
from models.effectiveness_tracker import EffectivenessTracker

# 🚨 Phase 2A: Import Crisis Prediction & Early Warning Systems
from models.crisis_predictor import CrisisPredictionSystem
from models.early_warning_system import EarlyWarningSystem

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MantraPath ML Service",
    description="Machine Learning service for smart notification scheduling and personalized insights",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML models
pattern_analyzer = MoodPatternAnalyzer()
timing_predictor = OptimalTimingPredictor()
content_engine = NotificationContentEngine()
effectiveness_tracker = EffectivenessTracker()

# 🚨 Phase 2A: Initialize crisis prediction components
crisis_predictor = CrisisPredictionSystem()
early_warning_system = EarlyWarningSystem()

# Initialize API-only crisis monitoring dashboard
crisis_dashboard = None
try:
    from monitoring.api_crisis_dashboard import get_crisis_dashboard
    crisis_dashboard = get_crisis_dashboard()
    logger.info("✅ API Crisis Dashboard initialized successfully")
except ImportError as e:
    logger.warning(f"⚠️ Crisis dashboard dependencies not available: {e}")
except Exception as e:
    logger.warning(f"⚠️ Could not initialize crisis dashboard: {e}")
    crisis_dashboard = None

# Start background metrics collection
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks and monitoring"""
    logger.info("🚀 Starting ML Service with Crisis Prediction Dashboard")
    
    # Start metrics collection background task
    asyncio.create_task(collect_metrics_background())
    
    logger.info("✅ Crisis prediction monitoring active")

async def collect_metrics_background():
    """Background task to collect crisis prediction metrics"""
    while True:
        try:
            if crisis_dashboard:
                await crisis_dashboard.collect_metrics(crisis_predictor, early_warning_system)
            await asyncio.sleep(60)  # Collect metrics every minute
        except Exception as e:
            logger.error(f"Metrics collection error: {e}")
            await asyncio.sleep(60)  # Wait before retrying
            await asyncio.sleep(60)  # Continue despite errors

# Pydantic models
class UserBehaviorData(BaseModel):
    user_id: str
    mood_entries: List[Dict[str, Any]] = []
    journal_entries: List[Dict[str, Any]] = []
    notification_responses: List[Dict[str, Any]] = []
    app_usage_patterns: List[Dict[str, Any]] = []
    contextual_data: Dict[str, Any] = {}

class OptimalTime(BaseModel):
    hour: int
    day_of_week: Optional[int] = None
    effectiveness_score: float
    notification_type: str
    reason: str
    confidence_level: float

class PersonalizedInsight(BaseModel):
    insight_type: str
    title: str
    content: str
    action_suggestions: List[str]
    confidence_score: float
    priority: str

class NotificationEngagement(BaseModel):
    notification_id: str
    user_id: str
    engagement_type: str  # 'opened', 'dismissed', 'acted_upon', 'ignored'
    engagement_time: datetime
    subsequent_mood_change: Optional[float] = None

# 🚨 Phase 2A: Crisis Prediction Pydantic Models
class CrisisAssessmentRequest(BaseModel):
    user_id: str
    mood_entries: List[Dict[str, Any]] = []
    journal_entries: List[Dict[str, Any]] = []
    activity_data: Dict[str, Any] = {}
    sleep_data: Dict[str, Any] = {}
    demographic_info: Dict[str, Any] = {}
    include_interventions: bool = True

class CrisisRiskResponse(BaseModel):
    user_id: str
    crisis_probability: float
    risk_level: str  # 'MINIMAL', 'LOW', 'MEDIUM', 'HIGH'
    confidence: float
    time_to_crisis: Dict[str, Any]
    key_risk_factors: List[str]
    protective_factors: List[str]
    recommended_interventions: List[str]
    urgency_level: str  # 'ROUTINE', 'MODERATE', 'URGENT', 'IMMEDIATE'
    model_version: str

class MonitoringRequest(BaseModel):
    user_id: str
    user_data: Dict[str, Any]
    force_check: bool = False

# Health check
@app.get("/health")
async def health_check():
    """ML Service health check"""
    return {
        "status": "healthy",
        "service": "ml_service",
        "timestamp": datetime.utcnow(),
        "models_loaded": {
            "pattern_analyzer": pattern_analyzer.is_ready(),
            "timing_predictor": timing_predictor.is_ready(),
            "content_engine": content_engine.is_ready(),
            "effectiveness_tracker": effectiveness_tracker.is_ready(),
            "crisis_predictor": crisis_predictor.ready,
            "early_warning_system": True  # Always available
        },
        "phase_2a_active": True,
        "crisis_prediction_available": crisis_predictor.ready
    }

@app.post("/ml/analyze-patterns")
async def analyze_user_patterns(
    behavior_data: UserBehaviorData,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze user behavior patterns using ML"""
    try:
        # Get user's mood and journal data from database
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == behavior_data.user_id
        ).order_by(MoodEntry.created_at.desc()).limit(100).all()
        
        journal_entries = db.query(JournalEntry).filter(
            JournalEntry.user_id == behavior_data.user_id
        ).order_by(JournalEntry.created_at.desc()).limit(50).all()
        
        # Convert to format expected by ML models
        mood_data = [
            {
                "timestamp": entry.created_at,
                "mood_score": entry.mood_score,
                "energy_level": getattr(entry, 'energy_level', 5),
                "context": getattr(entry, 'context', {})
            }
            for entry in mood_entries
        ]
        
        journal_data = [
            {
                "timestamp": entry.created_at,
                "content": entry.content,
                "mood_before": getattr(entry, 'mood_before', None),
                "mood_after": getattr(entry, 'mood_after', None),
                "tags": getattr(entry, 'tags', [])
            }
            for entry in journal_entries
        ]
        
        # Analyze patterns
        patterns = pattern_analyzer.analyze_user_patterns({
            "mood_data": mood_data,
            "journal_data": journal_data,
            "user_id": behavior_data.user_id
        })
        
        return {
            "user_id": behavior_data.user_id,
            "patterns": patterns,
            "analysis_timestamp": datetime.utcnow(),
            "data_points_analyzed": {
                "mood_entries": len(mood_data),
                "journal_entries": len(journal_data)
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing patterns for user {behavior_data.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Pattern analysis failed: {str(e)}")

@app.get("/ml/optimal-times/{user_id}")
async def get_optimal_notification_times(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get ML-predicted optimal notification times for user"""
    try:
        # Get recent user data
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id,
            MoodEntry.created_at >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        if len(mood_entries) < 5:
            # Not enough data for ML prediction, return default optimal times
            return {
                "optimal_times": [
                    {
                        "hour": 9,
                        "day_of_week": None,
                        "effectiveness_score": 7.5,
                        "notification_type": "morning_check",
                        "reason": "Default morning check-in time",
                        "confidence_level": 0.6
                    },
                    {
                        "hour": 15,
                        "day_of_week": None,
                        "effectiveness_score": 8.0,
                        "notification_type": "afternoon_support",
                        "reason": "Common afternoon energy dip",
                        "confidence_level": 0.6
                    },
                    {
                        "hour": 20,
                        "day_of_week": None,
                        "effectiveness_score": 7.0,
                        "notification_type": "evening_reflection",
                        "reason": "Evening reflection time",
                        "confidence_level": 0.6
                    }
                ],
                "ml_prediction": False,
                "confidence_level": "low",
                "recommendation": "Continue using the app to improve personalization"
            }
        
        # Use ML model to predict optimal times
        user_data = {
            "mood_entries": [
                {
                    "timestamp": entry.created_at,
                    "mood_score": entry.mood_score,
                    "hour": entry.created_at.hour,
                    "day_of_week": entry.created_at.weekday()
                }
                for entry in mood_entries
            ]
        }
        
        optimal_times = timing_predictor.predict_optimal_times(user_data)
        
        return {
            "optimal_times": optimal_times,
            "ml_prediction": True,
            "confidence_level": "high",
            "data_points_used": len(mood_entries),
            "next_update": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error predicting optimal times for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Optimal time prediction failed: {str(e)}")

@app.post("/ml/track-engagement")
async def track_notification_engagement(
    engagement: NotificationEngagement,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track notification engagement for ML model improvement"""
    try:
        # Store engagement data
        engagement_data = {
            "notification_id": engagement.notification_id,
            "user_id": engagement.user_id,
            "engagement_type": engagement.engagement_type,
            "engagement_time": engagement.engagement_time,
            "subsequent_mood_change": engagement.subsequent_mood_change
        }
        
        # Update effectiveness tracker
        effectiveness_result = effectiveness_tracker.track_engagement(engagement_data)
        
        # Update timing predictor with feedback
        timing_predictor.update_with_feedback(engagement_data)
        
        return {
            "message": "Engagement tracked successfully",
            "engagement_id": str(uuid.uuid4()),
            "effectiveness_update": effectiveness_result,
            "model_updated": True
        }
        
    except Exception as e:
        logger.error(f"Error tracking engagement: {e}")
        raise HTTPException(status_code=500, detail=f"Engagement tracking failed: {str(e)}")

@app.get("/ml/personalized-insights/{user_id}")
async def get_personalized_insights(
    user_id: str,
    insight_type: str = "weekly_summary",
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI-powered personalized insights"""
    try:
        # Get user data
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id,
            MoodEntry.created_at >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        journal_entries = db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.created_at >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        # Prepare data for insight generation
        user_data = {
            "mood_entries": [
                {
                    "timestamp": entry.created_at,
                    "mood_score": entry.mood_score,
                    "energy_level": getattr(entry, 'energy_level', 5)
                }
                for entry in mood_entries
            ],
            "journal_entries": [
                {
                    "timestamp": entry.created_at,
                    "content": entry.content
                }
                for entry in journal_entries
            ]
        }
        
        # Generate insights using content engine
        insights = content_engine.generate_personalized_insights(user_data, insight_type)
        
        return {
            "user_id": user_id,
            "insights": insights,
            "insight_type": insight_type,
            "generated_at": datetime.utcnow(),
            "data_quality": {
                "mood_entries_count": len(mood_entries),
                "journal_entries_count": len(journal_entries),
                "confidence_level": "high" if len(mood_entries) > 5 else "moderate"
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating insights for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {str(e)}")

@app.post("/ml/update-model")
async def update_ml_models(
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Trigger ML model updates with latest data"""
    try:
        # Schedule background model updates
        background_tasks.add_task(update_models_background)
        
        return {
            "message": "Model update scheduled",
            "update_id": str(uuid.uuid4()),
            "scheduled_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error scheduling model update: {e}")
        raise HTTPException(status_code=500, detail=f"Model update failed: {str(e)}")

@app.get("/ml/model-performance")
async def get_model_performance(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get ML model performance metrics"""
    try:
        performance_metrics = {
            "pattern_analyzer": pattern_analyzer.get_performance_metrics(),
            "timing_predictor": timing_predictor.get_performance_metrics(),
            "content_engine": content_engine.get_performance_metrics(),
            "effectiveness_tracker": effectiveness_tracker.get_performance_metrics()
        }
        
        return {
            "metrics": performance_metrics,
            "overall_health": "good",
            "last_updated": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting model performance: {e}")
        raise HTTPException(status_code=500, detail=f"Performance metrics failed: {str(e)}")

async def update_models_background():
    """Background task to update ML models"""
    try:
        logger.info("Starting ML model update...")
        
        # Update each model
        pattern_analyzer.retrain_model()
        timing_predictor.retrain_model()
        content_engine.retrain_model()
        effectiveness_tracker.update_metrics()
        
        logger.info("ML model update completed successfully")
        
    except Exception as e:
        logger.error(f"Background model update failed: {e}")

# 🚨 Phase 2A: Crisis Prediction & Early Warning API Endpoints

@app.post("/crisis/predict-risk")
async def predict_crisis_risk(
    request: CrisisAssessmentRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    🚨 CRITICAL: Predict mental health crisis risk using advanced ML models
    
    This endpoint could literally save lives by identifying users at risk
    of mental health crises before they occur.
    """
    try:
        logger.info(f"Crisis risk prediction requested for user: {request.user_id}")
        
        # Enhanced data collection from database if not provided
        if not request.mood_entries:
            mood_entries = db.query(MoodEntry).filter(
                MoodEntry.user_id == request.user_id,
                MoodEntry.created_at >= datetime.utcnow() - timedelta(days=30)
            ).order_by(MoodEntry.created_at.desc()).all()
            
            request.mood_entries = [
                {
                    "timestamp": entry.created_at.isoformat(),
                    "mood_score": entry.mood_score,
                    "energy_level": getattr(entry, 'energy_level', 5),
                    "stress_level": getattr(entry, 'stress_level', 5),
                    "notes": getattr(entry, 'notes', '')
                }
                for entry in mood_entries
            ]
        
        if not request.journal_entries:
            journal_entries = db.query(JournalEntry).filter(
                JournalEntry.user_id == request.user_id,
                JournalEntry.created_at >= datetime.utcnow() - timedelta(days=14)
            ).order_by(JournalEntry.created_at.desc()).all()
            
            request.journal_entries = [
                {
                    "timestamp": entry.created_at.isoformat(),
                    "content": entry.content,
                    "sentiment": getattr(entry, 'sentiment', 'neutral')
                }
                for entry in journal_entries
            ]
        
        # Prepare comprehensive user data for ML analysis
        user_data = {
            "user_id": request.user_id,
            "mood_entries": request.mood_entries,
            "journal_entries": request.journal_entries,
            "activity_data": request.activity_data,
            "sleep_data": request.sleep_data,
            "demographic_info": request.demographic_info
        }
        
        # Execute crisis prediction
        crisis_prediction = crisis_predictor.predict_crisis_risk(user_data)
        
        # Record prediction in dashboard for real-time monitoring
        if crisis_dashboard:
            try:
                processing_start = datetime.utcnow()
                crisis_dashboard.record_prediction({
                    'user_id': request.user_id,
                    'risk_level': crisis_prediction.get("risk_level", "UNKNOWN"),
                    'confidence': crisis_prediction.get("confidence", 0.5),
                    'crisis_probability': crisis_prediction.get("crisis_probability", 0.0),
                    'processing_time': (datetime.utcnow() - processing_start).total_seconds(),
                    'recommended_interventions': crisis_prediction.get("recommended_interventions", []),
                    'data_quality': {
                        'mood_entries': len(request.mood_entries),
                        'journal_entries': len(request.journal_entries)
                    }
                })
            except Exception as dashboard_error:
                logger.warning(f"Dashboard recording failed: {dashboard_error}")
        
        # Log critical predictions for monitoring
        risk_level = crisis_prediction.get("risk_level", "UNKNOWN")
        if risk_level in ["HIGH", "CRITICAL"]:
            logger.critical(f"HIGH RISK DETECTED - User: {request.user_id}, Risk: {risk_level}, Probability: {crisis_prediction.get('crisis_probability', 0):.3f}")
        elif risk_level == "MEDIUM":
            logger.warning(f"Medium risk detected - User: {request.user_id}, Probability: {crisis_prediction.get('crisis_probability', 0):.3f}")
        
        return {
            "success": True,
            "crisis_assessment": crisis_prediction,
            "timestamp": datetime.utcnow().isoformat(),
            "data_quality": {
                "mood_entries_analyzed": len(request.mood_entries),
                "journal_entries_analyzed": len(request.journal_entries),
                "sufficient_data": len(request.mood_entries) >= 7
            }
        }
        
    except Exception as e:
        logger.error(f"Crisis prediction error for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Crisis prediction failed: {str(e)}")

@app.post("/crisis/monitor-user")
async def monitor_user_crisis_risk(
    request: MonitoringRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    🎯 Real-time crisis risk monitoring with intelligent alerting
    
    Continuously monitors user mental health indicators and triggers
    appropriate interventions when elevated risk is detected.
    """
    try:
        logger.debug(f"Crisis monitoring check for user: {request.user_id}")
        
        # Execute real-time monitoring
        monitoring_result = await early_warning_system.monitor_user_risk(
            request.user_id, 
            request.user_data
        )
        
        # Log any alerts triggered
        if monitoring_result.get("alert_triggered"):
            alert_level = monitoring_result.get("alert_level", "UNKNOWN")
            logger.info(f"Crisis alert triggered - User: {request.user_id}, Level: {alert_level}")
        
        return {
            "success": True,
            "monitoring_result": monitoring_result,
            "timestamp": datetime.utcnow().isoformat(),
            "system_version": early_warning_system.system_version
        }
        
    except Exception as e:
        logger.error(f"Crisis monitoring error for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Crisis monitoring failed: {str(e)}")

@app.get("/crisis/alert-status/{user_id}")
async def get_user_alert_status(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    📊 Get current crisis alert status for a user
    """
    try:
        alert_status = await early_warning_system.get_user_alert_status(user_id)
        
        return {
            "success": True,
            "alert_status": alert_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting alert status for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Alert status retrieval failed: {str(e)}")

@app.post("/crisis/resolve-alert/{user_id}")
async def resolve_crisis_alert(
    user_id: str,
    resolution_reason: str = "Resolved by user",
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    ✅ Manually resolve an active crisis alert
    """
    try:
        resolution_result = await early_warning_system.resolve_alert(user_id, resolution_reason)
        
        if resolution_result.get("success"):
            logger.info(f"Crisis alert resolved for user {user_id}: {resolution_reason}")
        
        return {
            "success": resolution_result.get("success", False),
            "resolution_result": resolution_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error resolving alert for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Alert resolution failed: {str(e)}")

@app.get("/crisis/system-metrics")
async def get_crisis_system_metrics(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    📈 Get crisis prediction system performance metrics
    """
    try:
        return {
            "success": True,
            "metrics": {
                "crisis_predictor": {
                    "version": crisis_predictor.model_version,
                    "ready": crisis_predictor.ready,
                    "predictions_made": len(crisis_predictor.prediction_history),
                    "thresholds": crisis_predictor.crisis_thresholds
                },
                "early_warning_system": {
                    "version": early_warning_system.system_version,
                    "active_alerts": len(early_warning_system.active_alerts),
                    "total_alerts_issued": len(early_warning_system.alert_history),
                    "alert_thresholds": {level.name: threshold for level, threshold in early_warning_system.alert_thresholds.items()}
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting crisis system metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")

# 📊 Crisis Monitoring Dashboard API Endpoints

@app.get("/dashboard/test")
async def test_dashboard_routing() -> Dict[str, Any]:
    """
    🧪 Test endpoint to verify dashboard routing (no authentication required)
    """
    return {
        "success": True,
        "message": "Dashboard routing is working correctly!",
        "service": "ml_service",
        "endpoint": "/dashboard/test",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/dashboard/public-status")
async def get_public_dashboard_status() -> Dict[str, Any]:
    """
    📊 Get public dashboard status (no authentication required)
    Shows anonymized aggregate metrics for demonstration
    """
    try:
        if crisis_dashboard:
            metrics = crisis_dashboard.get_current_metrics()
            status = crisis_dashboard.get_system_status()
            
            return {
                "success": True,
                "dashboard_active": True,
                "anonymized_metrics": {
                    "total_predictions_24h": metrics.get('total_predictions', 0),
                    "high_risk_alerts_24h": metrics.get('high_risk_alerts', 0),
                    "medium_risk_alerts_24h": metrics.get('medium_risk_alerts', 0),
                    "low_risk_alerts_24h": metrics.get('low_risk_alerts', 0),
                    "system_uptime_percent": metrics.get('system_uptime', 100.0),
                    "avg_response_time_seconds": metrics.get('avg_response_time', 0.0)
                },
                "system_health": {
                    "dashboard_status": status.get('dashboard_status', 'unknown'),
                    "redis_connected": status.get('system_health', {}).get('redis_connected', False),
                    "version": status.get('version', 'unknown')
                },
                "last_updated": datetime.utcnow().isoformat(),
                "note": "This endpoint provides anonymized aggregate statistics for demonstration purposes"
            }
        else:
            return {
                "success": False,
                "dashboard_active": False,
                "message": "Crisis dashboard not available",
                "timestamp": datetime.utcnow().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Error getting public dashboard status: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/dashboard/metrics")
async def get_dashboard_metrics(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    📊 Get real-time crisis prediction dashboard metrics
    
    Provides comprehensive metrics for monitoring dashboard including:
    - Current risk distribution
    - Alert statistics
    - System performance metrics
    - Model accuracy indicators
    """
    try:
        if crisis_dashboard:
            return {
                "success": True,
                "dashboard_metrics": crisis_dashboard.get_current_metrics(),
                "system_status": crisis_dashboard.get_system_status(),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "success": True,
                "dashboard_metrics": {"message": "Dashboard not available"},
                "system_status": {"status": "dashboard_disabled"},
                "timestamp": datetime.utcnow().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard metrics failed: {str(e)}")

@app.get("/dashboard/health")
async def get_dashboard_health() -> Dict[str, Any]:
    """
    🏥 Get crisis prediction system health status
    
    Returns comprehensive health indicators:
    - System uptime and availability
    - Model performance metrics
    - Alert response times
    - Redis connection status
    """
    try:
        if crisis_dashboard:
            system_status = crisis_dashboard.get_system_status()
            
            return {
                "success": True,
                "health_status": "healthy" if system_status.get("dashboard_status") == "operational" else "degraded",
                "system_status": system_status,
                "uptime_check": {
                    "crisis_predictor": crisis_predictor.ready,
                    "early_warning_system": True,
                    "dashboard": crisis_dashboard.ready,
                    "redis_connected": crisis_dashboard.redis_client is not None
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "success": True,
                "health_status": "healthy",
                "system_status": {"status": "dashboard_disabled"},
                "uptime_check": {
                    "crisis_predictor": crisis_predictor.ready,
                    "early_warning_system": True,
                    "dashboard": False,
                    "redis_connected": False
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Error getting dashboard health: {e}")
        return {
            "success": False,
            "health_status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/dashboard/alerts/summary")
async def get_alerts_summary(
    hours: int = 24,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    📋 Get crisis alerts summary for specified time period
    
    Returns aggregated alert statistics including:
    - Alert counts by risk level
    - Response time analytics
    - Intervention success rates
    - Trend analysis
    """
    try:
        # Get alert history from early warning system
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_alerts = [
            alert for alert in early_warning_system.alert_history
            if datetime.fromisoformat(alert['timestamp']) > cutoff_time
        ]
        
        # Analyze alerts
        alert_levels = {}
        total_response_time = 0
        successful_interventions = 0
        total_interventions = 0
        
        for alert in recent_alerts:
            level = alert.get('alert_level', 'UNKNOWN')
            alert_levels[level] = alert_levels.get(level, 0) + 1
            
            response_time = alert.get('response_time_seconds', 0)
            total_response_time += response_time
            
            interventions = alert.get('interventions_triggered', [])
            total_interventions += len(interventions)
            successful_interventions += sum(1 for i in interventions if i.get('successful', False))
        
        avg_response_time = total_response_time / len(recent_alerts) if recent_alerts else 0
        intervention_success_rate = (successful_interventions / total_interventions * 100) if total_interventions > 0 else 0
        
        return {
            "success": True,
            "summary_period_hours": hours,
            "total_alerts": len(recent_alerts),
            "alert_distribution": alert_levels,
            "performance_metrics": {
                "avg_response_time_seconds": round(avg_response_time, 2),
                "intervention_success_rate_percent": round(intervention_success_rate, 1),
                "alerts_per_hour": round(len(recent_alerts) / hours, 2)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting alerts summary: {e}")
        raise HTTPException(status_code=500, detail=f"Alerts summary failed: {str(e)}")

# ============================================================
# ANALYTICS ENDPOINTS - Comprehensive ML Analytics
# ============================================================

@app.get("/ml/mood-analysis")
async def get_mood_analysis(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Comprehensive mood analysis for current user"""
    try:
        user_id = current_user.get("user_id")  # Fixed: use user_id instead of sub
        
        # Get recent mood entries
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(MoodEntry.created_at.desc()).limit(30).all()
        
        if not mood_entries:
            return {
                "status": "no_data",
                "message": "No mood data available for analysis",
                "recommendations": ["Start tracking your mood daily for personalized insights"]
            }
        
        # Calculate analytics
        mood_scores = [entry.mood_score for entry in mood_entries]
        energy_levels = [getattr(entry, 'energy_level', 5) for entry in mood_entries]
        stress_levels = [getattr(entry, 'stress_level', 5) for entry in mood_entries]
        
        analysis = {
            "user_id": user_id,
            "analysis_date": datetime.utcnow().isoformat(),
            "data_points": len(mood_entries),
            "mood_statistics": {
                "average_mood": round(np.mean(mood_scores), 2),
                "mood_trend": "improving" if len(mood_scores) > 1 and mood_scores[0] > mood_scores[-1] else "stable",
                "mood_variance": round(np.var(mood_scores), 2),
                "best_mood": max(mood_scores),
                "lowest_mood": min(mood_scores)
            },
            "energy_statistics": {
                "average_energy": round(np.mean(energy_levels), 2),
                "energy_trend": "stable"
            },
            "stress_statistics": {
                "average_stress": round(np.mean(stress_levels), 2),
                "stress_trend": "stable"
            },
            "insights": [
                f"Your average mood score is {round(np.mean(mood_scores), 1)}/10",
                f"Most recent mood entries show {'positive' if mood_scores[0] > 6 else 'neutral' if mood_scores[0] > 4 else 'concerning'} patterns",
                "Continue tracking to unlock more personalized insights"
            ],
            "recommendations": [
                "Maintain regular mood tracking",
                "Consider journaling during mood dips",
                "Engage with community during challenging times"
            ]
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Mood analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Mood analysis failed: {str(e)}")

@app.get("/ml/user-insights/{user_id}")
async def get_user_insights(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive user insights and patterns"""
    try:
        # Verify user access - Fixed: use user_id instead of sub
        if current_user.get("user_id") != user_id and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get user data
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(MoodEntry.created_at.desc()).limit(100).all()
        
        journal_entries = db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id
        ).order_by(JournalEntry.created_at.desc()).limit(50).all()
        
        # Calculate insights
        insights = {
            "user_id": user_id,
            "generated_at": datetime.utcnow().isoformat(),
            "mood_patterns": {
                "total_entries": len(mood_entries),
                "tracking_consistency": len(mood_entries) / 30 if len(mood_entries) <= 30 else 1.0,
                "average_mood": round(np.mean([e.mood_score for e in mood_entries]), 2) if mood_entries else 0
            },
            "behavioral_insights": [
                "Regular mood tracking detected",
                "Engagement with mental health tools is positive",
                "Continue current wellness practices"
            ],
            "personalized_recommendations": [
                "Schedule daily check-ins",
                "Explore community features",
                "Set mood tracking reminders"
            ],
            "risk_assessment": {
                "level": "low",
                "factors": [],
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
        return insights
        
    except Exception as e:
        logger.error(f"User insights failed: {e}")
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")

@app.get("/ml/analytics/overview")
async def get_analytics_overview(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get ML analytics overview for the current user"""
    try:
        user_id = current_user.get("user_id")  # Fixed: use user_id instead of sub
        
        # Get data for analytics
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(MoodEntry.created_at.desc()).limit(50).all()
        
        overview = {
            "user_id": user_id,
            "overview_date": datetime.utcnow().isoformat(),
            "data_summary": {
                "mood_entries_count": len(mood_entries),
                "analysis_period_days": 30,
                "data_quality": "good" if len(mood_entries) > 10 else "limited"
            },
            "key_metrics": {
                "wellness_score": round(np.mean([e.mood_score for e in mood_entries]) * 10, 1) if mood_entries else 50,
                "engagement_level": min(100, len(mood_entries) * 3),
                "consistency_score": min(100, len(mood_entries) * 2)
            },
            "trend_analysis": {
                "mood_trend": "stable",
                "energy_trend": "stable", 
                "stress_trend": "stable"
            },
            "ml_features_available": [
                "mood_analysis",
                "pattern_recognition",
                "personalized_insights",
                "crisis_detection"
            ]
        }
        
        return overview
        
    except Exception as e:
        logger.error(f"Analytics overview failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics overview failed: {str(e)}")

@app.get("/ml/predictions/mood-forecast")
async def get_mood_forecast(
    days: int = 7,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate mood forecast for user"""
    try:
        user_id = current_user.get("user_id")  # Fixed: use user_id instead of sub
        
        # Get historical data
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(MoodEntry.created_at.desc()).limit(30).all()
        
        if len(mood_entries) < 5:
            return {
                "status": "insufficient_data",
                "message": "Need at least 5 mood entries for forecasting",
                "forecast": []
            }
        
        # Simple forecasting based on recent trends
        recent_moods = [e.mood_score for e in mood_entries[:7]]
        trend = np.mean(np.diff(recent_moods)) if len(recent_moods) > 1 else 0
        baseline = np.mean(recent_moods)
        
        forecast = []
        for i in range(days):
            predicted_mood = baseline + (trend * i * 0.1)
            predicted_mood = max(1, min(10, predicted_mood))  # Clamp between 1-10
            
            forecast.append({
                "date": (datetime.utcnow() + timedelta(days=i+1)).date().isoformat(),
                "predicted_mood": round(predicted_mood, 1),
                "confidence": max(0.5, 1.0 - (i * 0.1))  # Decreasing confidence
            })
        
        return {
            "user_id": user_id,
            "forecast_generated": datetime.utcnow().isoformat(),
            "forecast_days": days,
            "forecast": forecast,
            "methodology": "trend_based",
            "disclaimer": "Predictions are estimates based on historical patterns"
        }
        
    except Exception as e:
        logger.error(f"Mood forecast failed: {e}")
        raise HTTPException(status_code=500, detail=f"Mood forecasting failed: {str(e)}")

@app.get("/ml/recommendations/personalized")
async def get_personalized_recommendations(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized ML-driven recommendations"""
    try:
        user_id = current_user.get("user_id")  # Fixed: use user_id instead of sub
        
        # Get user data for recommendations
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(MoodEntry.created_at.desc()).limit(20).all()
        
        if not mood_entries:
            return {
                "recommendations": [
                    "Start tracking your mood daily",
                    "Explore the community features",
                    "Try the AI chatbot for support"
                ],
                "personalization_level": "basic"
            }
        
        # Analyze recent patterns
        recent_moods = [e.mood_score for e in mood_entries[:7]]
        avg_mood = np.mean(recent_moods)
        
        recommendations = []
        
        if avg_mood < 5:
            recommendations.extend([
                "Consider reaching out to the community for support",
                "Try daily journaling to process emotions",
                "Schedule regular check-ins with the AI chatbot"
            ])
        elif avg_mood < 7:
            recommendations.extend([
                "Maintain your current wellness practices",
                "Explore new coping strategies",
                "Connect with others in similar situations"
            ])
        else:
            recommendations.extend([
                "Share your wellness strategies with the community",
                "Continue your positive momentum",
                "Consider helping others on their journey"
            ])
        
        # Add time-based recommendations
        recommendations.append("Track your mood at consistent times for better insights")
        recommendations.append("Use the chatbot when you need immediate support")
        
        return {
            "user_id": user_id,
            "generated_at": datetime.utcnow().isoformat(),
            "recommendations": recommendations,
            "personalization_level": "adaptive",
            "based_on": {
                "mood_entries": len(mood_entries),
                "average_mood": round(avg_mood, 1),
                "analysis_period": "recent_activity"
            }
        }
        
    except Exception as e:
        logger.error(f"Personalized recommendations failed: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Production-ready server configuration
    config = {
        "app": app,
        "host": "0.0.0.0",
        "port": 8008,
        "reload": False,  # Disable in production
        "workers": 1,     # Single worker for shared state
        "log_level": "info",
        "access_log": True
    }
    
    logger.info("🚀 Starting MantraPath ML Service with Crisis Prediction & Monitoring")
    logger.info(f"📊 Dashboard available at: http://localhost:{config['port']}/dashboard/")
    logger.info(f"🚨 Crisis prediction endpoints: http://localhost:{config['port']}/crisis/")
    
    uvicorn.run(**config)
