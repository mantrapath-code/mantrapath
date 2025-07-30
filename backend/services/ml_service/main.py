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
            "effectiveness_tracker": effectiveness_tracker.is_ready()
        }
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
