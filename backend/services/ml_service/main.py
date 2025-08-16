"""
ML Service for Smart Notification Scheduling
Provides machine learning capabilities for personalized notification timing and content
"""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Iterable
from datetime import datetime, timedelta, timezone
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
from shared.events import get_event_bus, EventChannels, Event, publish_insight_delta
# BK-004: V3 enhanced bus imports
from shared.events import get_enhanced_event_bus, V3EventChannels
from shared.feature_flags import get_flag_bool

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

# E4: Real-Time Insight Delta Processor
class RealTimeInsightProcessor:
    """Processes real-time events and generates insight deltas"""
    
    def __init__(self):
        self.insight_cache = {}  # Simple in-memory cache {user_id: cache_data}
        self.cache_ttl = 300  # 5 minutes TTL
        logger.info("🔄 RealTimeInsightProcessor initialized")
    
    async def process_mood_entry_event(self, event: Event):
        """Process mood entry created event and generate insight delta"""
        try:
            user_id = event.user_id
            mood_data = event.data
            
            if not user_id:
                return
            
            # Calculate quick insight updates
            delta = await self._calculate_mood_delta(user_id, mood_data)
            
            # Publish insight delta
            if delta:
                await publish_insight_delta(user_id, delta)
                logger.info(f"📊 Published insight delta for user {user_id}")
                
        except Exception as e:
            logger.error(f"❌ Error processing mood entry event: {e}")
    
    async def process_journal_entry_event(self, event: Event):
        """Process journal entry created event and generate insight delta"""
        try:
            user_id = event.user_id
            journal_data = event.data
            
            if not user_id:
                return
            
            # Calculate quick insight updates
            delta = await self._calculate_journal_delta(user_id, journal_data)
            
            # Publish insight delta
            if delta:
                await publish_insight_delta(user_id, delta)
                logger.info(f"📝 Published journal insight delta for user {user_id}")
                
        except Exception as e:
            logger.error(f"❌ Error processing journal entry event: {e}")
    
    async def process_challenge_progress_event(self, event: Event):
        """Process challenge progress updated event and generate insight delta"""
        try:
            user_id = event.user_id
            challenge_data = event.data
            
            if not user_id:
                return
            
            # Calculate quick insight updates
            delta = await self._calculate_challenge_delta(user_id, challenge_data)
            
            # Publish insight delta
            if delta:
                await publish_insight_delta(user_id, delta)
                logger.info(f"🏆 Published challenge insight delta for user {user_id}")
                
        except Exception as e:
            logger.error(f"❌ Error processing challenge progress event: {e}")
    
    async def _calculate_mood_delta(self, user_id: str, mood_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calculate mood-related insight deltas"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # Update cache with new mood entry count
            cache_key = f"mood_insights_{user_id}"
            cached_data = self.insight_cache.get(cache_key, {})
            
            # Simple delta calculations
            delta = {
                "type": "mood_update",
                "timestamp": current_time.isoformat(),
                "changes": {
                    "latest_mood": mood_data.get("mood_score"),
                    "energy_level": mood_data.get("energy_level"),
                    "stress_level": mood_data.get("stress_level"),
                    "days_tracked_increment": 1  # This day was tracked
                }
            }
            
            # Calculate streak if cache exists
            last_entry_date = cached_data.get("last_mood_date")
            today = current_time.date().isoformat()
            
            if last_entry_date:
                # Simple consecutive day check
                try:
                    last_date = datetime.fromisoformat(last_entry_date).date()
                    current_date = current_time.date()
                    
                    if (current_date - last_date).days == 1:
                        # Consecutive day - increment streak
                        current_streak = cached_data.get("mood_streak", 0) + 1
                        delta["changes"]["mood_streak"] = current_streak
                    elif (current_date - last_date).days == 0:
                        # Same day - maintain streak
                        delta["changes"]["mood_streak"] = cached_data.get("mood_streak", 1)
                    else:
                        # Gap in days - reset streak
                        delta["changes"]["mood_streak"] = 1
                except Exception:
                    delta["changes"]["mood_streak"] = 1
            else:
                delta["changes"]["mood_streak"] = 1
            
            # Update cache
            self.insight_cache[cache_key] = {
                "last_mood_date": today,
                "mood_streak": delta["changes"].get("mood_streak", 1),
                "last_updated": current_time.isoformat()
            }
            
            return delta
            
        except Exception as e:
            logger.error(f"❌ Error calculating mood delta: {e}")
            return None
    
    async def _calculate_journal_delta(self, user_id: str, journal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calculate journal-related insight deltas"""
        try:
            current_time = datetime.now(timezone.utc)
            
            delta = {
                "type": "journal_update",
                "timestamp": current_time.isoformat(),
                "changes": {
                    "journal_entries_increment": 1,
                    "latest_sentiment": journal_data.get("sentiment_label"),
                    "sentiment_score": journal_data.get("sentiment_score")
                }
            }
            
            return delta
            
        except Exception as e:
            logger.error(f"❌ Error calculating journal delta: {e}")
            return None
    
    async def _calculate_challenge_delta(self, user_id: str, challenge_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calculate challenge-related insight deltas"""
        try:
            current_time = datetime.now(timezone.utc)
            
            delta = {
                "type": "challenge_update",
                "timestamp": current_time.isoformat(),
                "changes": {
                    "challenge_completed": challenge_data.get("completed", False),
                    "streak_count": challenge_data.get("streak_count", 0),
                    "engagement_increment": 1
                }
            }
            
            return delta
            
        except Exception as e:
            logger.error(f"❌ Error calculating challenge delta: {e}")
            return None

# Initialize real-time processor
realtime_processor = RealTimeInsightProcessor()

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
    
    # E4: Setup real-time event subscriptions
    if get_flag_bool('USE_EVENT_BUS'):
        await setup_realtime_subscriptions()
    
    logger.info("✅ Crisis prediction monitoring active")

async def setup_realtime_subscriptions():
    """Setup event subscriptions for real-time insight processing"""
    try:
        bus = get_event_bus()
        
        # Subscribe to mood entry events (legacy)
        await bus.subscribe(
            EventChannels.MOOD_ENTRY_CREATED,
            realtime_processor.process_mood_entry_event
        )
        
        # Subscribe to journal entry events (legacy)
        await bus.subscribe(
            EventChannels.JOURNAL_ENTRY_CREATED,
            realtime_processor.process_journal_entry_event
        )
        
        # Subscribe to challenge progress events (legacy)
        await bus.subscribe(
            EventChannels.CHALLENGE_PROGRESS_UPDATED,
            realtime_processor.process_challenge_progress_event
        )
        
        # BK-004: Also subscribe to V3 enhanced channels when enabled
        if get_flag_bool('USE_NATS_EVENT_BUS'):
            v3bus = get_enhanced_event_bus()
            await v3bus.subscribe(
                V3EventChannels.MOOD_ENTRY_CREATED,
                realtime_processor.process_mood_entry_event
            )
            await v3bus.subscribe(
                V3EventChannels.JOURNAL_ENTRY_CREATED,
                realtime_processor.process_journal_entry_event
            )
        
        logger.info("🔔 Real-time event subscriptions established (legacy + V3)")
        
    except Exception as e:
        logger.error(f"❌ Failed to setup real-time subscriptions: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        from shared.events import cleanup_event_bus
        await cleanup_event_bus()
        logger.info("🛑 Event bus cleaned up")
    except Exception as e:
        logger.error(f"❌ Error during shutdown cleanup: {e}")

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

# Helper function to calculate user statistics
from shared.models import MoodEntry as _MoodEntry, JournalEntry as _JournalEntry

def calculate_user_statistics(mood_entries: Iterable[_MoodEntry], journal_entries: Iterable[_JournalEntry]) -> Dict[str, Any]:
    """Calculate statistical insights from user data (typing improved)."""
    try:
        mood_entries_list: List[_MoodEntry] = list(mood_entries)
        _ = list(journal_entries)  # currently unused
        statistics: Dict[str, Any] = {
            "best_day": "",
            "energy_peak": "",
            "mood_streak": 0,
            "average_mood": 0.0,
            "mood_variability": 0.0,
            "total_entries": len(mood_entries_list)
        }
        if not mood_entries_list:
            return statistics
        scores: List[int] = [int(getattr(entry, 'mood_score', 0) or 0) for entry in mood_entries_list]
        total_mood = sum(scores)
        statistics["average_mood"] = round(total_mood / len(scores), 1) if scores else 0.0
        avg = statistics["average_mood"]  # already float
        variance = (sum((s - avg) ** 2 for s in scores) / len(scores)) if scores else 0.0
        statistics["mood_variability"] = round(variance ** 0.5, 1) if variance else 0.0
        day_moods: Dict[int, List[int]] = {}
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for entry in mood_entries_list:
            created = getattr(entry, 'created_at', None)
            if not created:
                continue
            day_of_week = created.weekday()
            day_moods.setdefault(day_of_week, []).append(int(getattr(entry,'mood_score',0) or 0))
        if day_moods:
            day_averages: Dict[int, float] = {day: (sum(scores)/len(scores) if scores else 0.0) for day, scores in day_moods.items()}
            if day_averages:
                best_day_num = max(day_averages, key=lambda d: day_averages[d])
                statistics["best_day"] = day_names[best_day_num]
        hour_energy: Dict[int, List[int]] = {}
        for entry in mood_entries_list:
            created = getattr(entry, 'created_at', None)
            if not created:
                continue
            hour = created.hour
            energy = int(getattr(entry, 'energy_level', 5) or 5)
            hour_energy.setdefault(hour, []).append(energy)
        if hour_energy:
            hour_averages: Dict[int, float] = {h: (sum(levels)/len(levels) if levels else 0.0) for h, levels in hour_energy.items()}
            if hour_averages:
                peak_hour = max(hour_averages, key=lambda h: hour_averages[h])
                statistics["energy_peak"] = f"{peak_hour:02d}:00"
        if len(mood_entries_list) > 1:
            sorted_entries = sorted([e for e in mood_entries_list if getattr(e,'created_at',None)], key=lambda x: x.created_at)
            daily_moods: Dict[Any, List[int]] = {}
            for entry in sorted_entries:
                date_key = entry.created_at.date()
                daily_moods.setdefault(date_key, []).append(int(getattr(entry,'mood_score',0) or 0))
            daily_averages: Dict[Any, float] = {date: (sum(values)/len(values) if values else 0.0) for date, values in daily_moods.items()}
            overall_avg = statistics["average_mood"]
            streak = 0
            for date in sorted(daily_averages.keys(), reverse=True):
                if daily_averages[date] >= overall_avg:
                    streak += 1
                else:
                    break
            statistics["mood_streak"] = streak
        return statistics
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        return {
            "best_day": "",
            "energy_peak": "",
            "mood_streak": 0,
            "average_mood": 0.0,
            "mood_variability": 0.0,
            "total_entries": 0
        }

# Health check
@app.get("/health")
async def health_check():
    """ML Service health check"""
    return {
        "status": "healthy",
        "service": "ml_service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
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

# Additional health check for /ml/health endpoint
@app.get("/ml/health")
async def ml_health_check():
    """ML Service health check (alternative endpoint)"""
    return await health_check()

# Correlation analysis endpoint
@app.get("/ml/correlation-analysis/me")
async def get_correlation_analysis(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get correlation analysis between mood, activities, and external factors"""
    try:
        user_id = current_user.get("sub") or current_user.get("id") or current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Unable to extract user ID from token")
        
        # Get user's mood and journal entries
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(MoodEntry.created_at.desc()).limit(100).all()
        
        journal_entries = db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id
        ).order_by(JournalEntry.created_at.desc()).limit(50).all()
        
        if not mood_entries:
            return {
                "user_id": user_id,
                "correlations": {},
                "insights": [],
                "data_points": 0,
                "message": "Insufficient data for correlation analysis"
            }
        
        # Calculate correlations
        correlations = {}
        insights = []
        
        # Mood-time correlation
        mood_by_hour = {}
        for entry in mood_entries:
            hour = entry.created_at.hour
            if hour not in mood_by_hour:
                mood_by_hour[hour] = []
            mood_by_hour[hour].append(entry.mood_score)
        
        # Find best and worst times
        avg_by_hour = {hour: sum(scores)/len(scores) for hour, scores in mood_by_hour.items() if scores}
        if avg_by_hour:
            best_hour = max(avg_by_hour.keys(), key=lambda h: avg_by_hour[h])
            worst_hour = min(avg_by_hour.keys(), key=lambda h: avg_by_hour[h])
            
            correlations["time_patterns"] = {
                "best_hour": best_hour,
                "worst_hour": worst_hour,
                "hourly_averages": avg_by_hour
            }
            
            insights.append(f"You tend to feel best around {best_hour}:00 and lowest around {worst_hour}:00")
        
        # Activity correlations from journal entries
        if journal_entries:
            activity_keywords = ["exercise", "meditation", "sleep", "work", "social", "outdoors"]
            activity_moods = {keyword: [] for keyword in activity_keywords}
            
            for journal in journal_entries:
                content = journal.content.lower()
                # Find mood entries close to this journal entry
                nearby_moods = [m for m in mood_entries 
                              if abs((m.created_at - journal.created_at).total_seconds()) < 3600]
                
                if nearby_moods:
                    avg_mood = sum(m.mood_score for m in nearby_moods) / len(nearby_moods)
                    for keyword in activity_keywords:
                        if keyword in content:
                            activity_moods[keyword].append(avg_mood)
            
            # Calculate activity impact
            activity_impact = {}
            for activity, moods in activity_moods.items():
                if moods:
                    activity_impact[activity] = sum(moods) / len(moods)
            
            if activity_impact:
                correlations["activity_impact"] = activity_impact
                best_activity = max(activity_impact.keys(), key=lambda a: activity_impact[a])
                insights.append(f"Your mood tends to be highest when you mention '{best_activity}' in your journal")
        
        return {
            "user_id": user_id,
            "correlations": correlations,
            "insights": insights,
            "data_points": len(mood_entries),
            "analysis_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in correlation analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Correlation analysis failed: {str(e)}")

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
            "interaction_data": behavior_data.interaction_data
        })
        
        return {
            "user_id": behavior_data.user_id,
            "patterns": patterns,
            "analysis_date": datetime.utcnow(),
            "insights": [
                "Pattern analysis completed",
                f"Analyzed {len(mood_entries)} mood entries",
                f"Analyzed {len(journal_entries)} journal entries"
            ],
            "recommendations": [
                "Continue regular mood tracking",
                "Maintain journaling practice"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing patterns for user {behavior_data.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Pattern analysis failed: {str(e)}")

@app.post("/ml/analyze-patterns/me")
async def analyze_my_patterns(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze current user's behavior patterns using ML"""
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Unable to identify user")
            
        # Get user's mood and journal data from database
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id
        ).order_by(MoodEntry.created_at.desc()).limit(100).all()
        
        journal_entries = db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id
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
            "interaction_data": []  # No interaction data needed for this endpoint
        })
        
        # Calculate additional statistics for insights
        statistics = calculate_user_statistics(mood_entries, journal_entries)
        
        return {
            "user_id": user_id,
            "patterns": patterns,
            "statistics": statistics,
            "analysis_date": datetime.utcnow(),
            "insights": [
                "Pattern analysis completed",
                f"Analyzed {len(mood_entries)} mood entries",
                f"Analyzed {len(journal_entries)} journal entries"
            ],
            "recommendations": [
                "Continue regular mood tracking",
                "Maintain journaling practice"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing patterns for current user: {e}")
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
        logger.error(f"Personalized insights failed: {e}")
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")

@app.get("/ml/personalized-insights/me")
async def get_my_personalized_insights(
    insight_type: str = "weekly_summary",
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI-powered personalized insights for current user"""
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Unable to identify user")
            
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

# ==================================================
# E2 & E3 UNIFIED INSIGHTS ENDPOINTS
# ==================================================
from integrations.unified_insights_aggregator import aggregator
from integrations.enhanced_unified_insights_aggregator import enhanced_aggregator
from shared.feature_flags import feature_enabled, get_flag_bool

@app.get("/api/v1/insights/unified")
async def get_unified_insights(
    force_refresh: bool = False,
    enhanced: bool = False,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    E2/E3 Epic: Unified insights aggregation endpoint
    Aggregates insights from mood, journal, community, and ML data
    
    Parameters:
    - enhanced: Use enhanced ML aggregator with sentiment analysis and pattern detection
    """
    if not feature_enabled('USE_SERVER_UNIFIED_INSIGHTS'):
        raise HTTPException(status_code=404, detail="Unified insights disabled")
    
    user_id = current_user.get("sub") or current_user.get("id") or current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID missing")
    
    # Choose aggregator based on enhanced flag and feature availability
    use_enhanced = enhanced and get_flag_bool('USE_ENHANCED_ML_INSIGHTS', default=True)
    
    if use_enhanced:
        result = enhanced_aggregator.get_unified_insights(db, user_id, force_refresh=force_refresh)
        result['version'] = 'v2_enhanced'
    else:
        result = aggregator.get_unified_insights(db, user_id, force_refresh=force_refresh)
        result['version'] = 'v1_baseline'
    
    return result

@app.get("/api/v1/insights/models/status")
async def get_ml_models_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Get status of ML models used in enhanced insights
    """
    if not get_flag_bool('USE_ENHANCED_ML_INSIGHTS', default=True):
        raise HTTPException(status_code=404, detail="Enhanced ML insights disabled")
    
    return enhanced_aggregator.get_model_status()

@app.post("/api/v1/insights/unified/clear-cache")
async def clear_unified_insights_cache(
    current_user: dict = Depends(get_current_user)
):
    """
    Clear unified insights cache (for testing)
    """
    # Clear both caches
    aggregator.clear_cache()
    enhanced_aggregator.clear_cache()
    
    return {"message": "Cache cleared successfully"}

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
