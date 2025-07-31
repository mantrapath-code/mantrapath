"""
Mood Service - Handles mood tracking, journal entries, analytics, and insights
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import sys
import json

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

# Add parent directories to path
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

from shared.database import get_db, engine
from shared.models import MoodEntry, JournalEntry, User, Base
from shared.auth import get_current_user

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MantraPath Mood Service",
    description="Mood tracking, journaling, and analytics service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class MoodEntryCreate(BaseModel):
    mood_score: int
    energy_level: Optional[int] = None
    stress_level: Optional[int] = None
    sleep_quality: Optional[int] = None
    notes: Optional[str] = None
    context_tags: Optional[List[str]] = []

class MoodEntryResponse(BaseModel):
    id: str
    mood_score: int
    energy_level: Optional[int]
    stress_level: Optional[int]
    sleep_quality: Optional[int]
    notes: Optional[str]
    context_tags: List[str]
    created_at: datetime

class JournalEntryCreate(BaseModel):
    title: Optional[str] = None
    content: str
    mood_before: Optional[int] = None
    mood_after: Optional[int] = None
    is_private: bool = True

class JournalEntryResponse(BaseModel):
    id: str
    title: Optional[str]
    content: str
    mood_before: Optional[int]
    mood_after: Optional[int]
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]
    themes: List[str]
    is_private: bool
    created_at: datetime

class AnalyticsResponse(BaseModel):
    average_mood: float
    mood_trend: str
    total_entries: int
    streak: int
    weekly_pattern: dict
    monthly_summary: dict

# Mood tracking endpoints
@app.get("/api/v1/mood/", response_model=List[MoodEntryResponse])
async def get_mood_entries(
    limit: int = Query(50, le=1000),  # Allow up to 1000 entries for stats calculations
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's mood entries"""
    
    moods = db.query(MoodEntry).filter(
        MoodEntry.user_id == current_user["user_id"]
    ).order_by(desc(MoodEntry.created_at)).limit(limit).all()
    
    return [
        MoodEntryResponse(
            id=str(mood.id),
            mood_score=mood.mood_score,
            energy_level=mood.energy_level,
            stress_level=mood.stress_level,
            sleep_quality=mood.sleep_quality,
            notes=mood.notes,
            context_tags=mood.context_tags or [],
            created_at=mood.created_at
        )
        for mood in moods
    ]

@app.post("/api/v1/mood/", response_model=MoodEntryResponse)
async def create_mood_entry(
    mood_data: MoodEntryCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new mood entry"""
    
    mood_entry = MoodEntry(
        user_id=current_user["user_id"],
        mood_score=mood_data.mood_score,
        energy_level=mood_data.energy_level,
        stress_level=mood_data.stress_level,
        sleep_quality=mood_data.sleep_quality,
        notes=mood_data.notes,
        context_tags=mood_data.context_tags
    )
    
    db.add(mood_entry)
    db.commit()
    db.refresh(mood_entry)
    
    return MoodEntryResponse(
        id=str(mood_entry.id),
        mood_score=mood_entry.mood_score,
        energy_level=mood_entry.energy_level,
        stress_level=mood_entry.stress_level,
        sleep_quality=mood_entry.sleep_quality,
        notes=mood_entry.notes,
        context_tags=mood_entry.context_tags or [],
        created_at=mood_entry.created_at
    )

# Journal endpoints
@app.get("/api/v1/journal/", response_model=List[JournalEntryResponse])
async def get_journal_entries(
    limit: int = Query(20, le=50),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's journal entries"""
    
    entries = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user["user_id"]
    ).order_by(desc(JournalEntry.created_at)).limit(limit).all()
    
    return [
        JournalEntryResponse(
            id=str(entry.id),
            title=entry.title,
            content=entry.content,
            mood_before=entry.mood_before,
            mood_after=entry.mood_after,
            sentiment_score=entry.sentiment_score,
            sentiment_label=entry.sentiment_label,
            themes=entry.themes or [],
            is_private=entry.is_private,
            created_at=entry.created_at
        )
        for entry in entries
    ]

@app.post("/api/v1/journal/", response_model=JournalEntryResponse)
async def create_journal_entry(
    journal_data: JournalEntryCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new journal entry with sentiment analysis"""
    
    # Perform sentiment analysis
    blob = TextBlob(journal_data.content)
    sentiment_score = blob.sentiment.polarity
    
    if sentiment_score > 0.1:
        sentiment_label = "positive"
    elif sentiment_score < -0.1:
        sentiment_label = "negative"
    else:
        sentiment_label = "neutral"
    
    # Extract themes (simple keyword extraction)
    themes = []
    words = journal_data.content.lower().split()
    emotion_keywords = {
        "stress": ["stress", "stressed", "anxious", "worry", "tension"],
        "happiness": ["happy", "joy", "excited", "grateful", "blessed"],
        "sadness": ["sad", "depressed", "down", "lonely", "empty"],
        "energy": ["tired", "exhausted", "energetic", "sleepy", "alert"],
        "relationships": ["friend", "family", "partner", "relationship", "social"]
    }
    
    for theme, keywords in emotion_keywords.items():
        if any(keyword in words for keyword in keywords):
            themes.append(theme)
    
    journal_entry = JournalEntry(
        user_id=current_user["user_id"],
        title=journal_data.title,
        content=journal_data.content,
        mood_before=journal_data.mood_before,
        mood_after=journal_data.mood_after,
        sentiment_score=sentiment_score,
        sentiment_label=sentiment_label,
        themes=themes,
        is_private=journal_data.is_private
    )
    
    db.add(journal_entry)
    db.commit()
    db.refresh(journal_entry)
    
    return JournalEntryResponse(
        id=str(journal_entry.id),
        title=journal_entry.title,
        content=journal_entry.content,
        mood_before=journal_entry.mood_before,
        mood_after=journal_entry.mood_after,
        sentiment_score=journal_entry.sentiment_score,
        sentiment_label=journal_entry.sentiment_label,
        themes=journal_entry.themes or [],
        is_private=journal_entry.is_private,
        created_at=journal_entry.created_at
    )

# Analytics endpoints
@app.get("/api/v1/analytics/overview", response_model=AnalyticsResponse)
async def get_analytics_overview(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics overview"""
    
    # Get mood data for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    mood_entries = db.query(MoodEntry).filter(
        and_(
            MoodEntry.user_id == current_user["user_id"],
            MoodEntry.created_at >= thirty_days_ago
        )
    ).all()
    
    if not mood_entries:
        return AnalyticsResponse(
            average_mood=0,
            mood_trend="neutral",
            total_entries=0,
            streak=0,
            weekly_pattern={},
            monthly_summary={}
        )
    
    # Calculate average mood
    average_mood = sum(mood.mood_score for mood in mood_entries) / len(mood_entries)
    
    # Calculate trend (comparing first half vs second half of period)
    half_point = len(mood_entries) // 2
    if half_point > 0:
        first_half_avg = sum(mood.mood_score for mood in mood_entries[:half_point]) / half_point
        second_half_avg = sum(mood.mood_score for mood in mood_entries[half_point:]) / (len(mood_entries) - half_point)
        
        if second_half_avg > first_half_avg + 0.5:
            mood_trend = "improving"
        elif second_half_avg < first_half_avg - 0.5:
            mood_trend = "declining"
        else:
            mood_trend = "stable"
    else:
        mood_trend = "neutral"
    
    # Calculate current streak
    today = datetime.utcnow().date()
    streak = 0
    for i in range(30):
        check_date = today - timedelta(days=i)
        has_entry = any(mood.created_at.date() == check_date for mood in mood_entries)
        if has_entry:
            streak += 1
        else:
            break
    
    # Weekly pattern (average by day of week)
    weekly_pattern = {}
    for day in range(7):  # 0 = Monday, 6 = Sunday
        day_moods = [mood.mood_score for mood in mood_entries if mood.created_at.weekday() == day]
        if day_moods:
            weekly_pattern[str(day)] = sum(day_moods) / len(day_moods)
        else:
            weekly_pattern[str(day)] = 0
    
    # Monthly summary
    monthly_summary = {
        "highest_mood": max(mood.mood_score for mood in mood_entries),
        "lowest_mood": min(mood.mood_score for mood in mood_entries),
        "total_days_tracked": len(set(mood.created_at.date() for mood in mood_entries)),
        "most_common_stress_level": 5  # Default placeholder
    }
    
    return AnalyticsResponse(
        average_mood=round(average_mood, 2),
        mood_trend=mood_trend,
        total_entries=len(mood_entries),
        streak=streak,
        weekly_pattern=weekly_pattern,
        monthly_summary=monthly_summary
    )

@app.get("/api/v1/analytics/patterns/weekly")
async def get_weekly_patterns(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weekly mood patterns for trend analysis"""
    
    # Get last 8 weeks of data
    eight_weeks_ago = datetime.utcnow() - timedelta(weeks=8)
    
    mood_entries = db.query(MoodEntry).filter(
        and_(
            MoodEntry.user_id == current_user["user_id"],
            MoodEntry.created_at >= eight_weeks_ago
        )
    ).all()
    
    # Group by week
    weekly_data = {}
    for mood in mood_entries:
        # Calculate week number
        week_start = mood.created_at - timedelta(days=mood.created_at.weekday())
        week_key = week_start.strftime("%Y-%W")
        
        if week_key not in weekly_data:
            weekly_data[week_key] = []
        weekly_data[week_key].append(mood.mood_score)
    
    # Calculate weekly averages
    weekly_averages = {}
    for week, scores in weekly_data.items():
        weekly_averages[week] = sum(scores) / len(scores)
    
    # Detect patterns
    patterns = []
    if len(weekly_averages) >= 4:
        # Check for declining pattern
        recent_weeks = list(weekly_averages.values())[-4:]
        if all(recent_weeks[i] > recent_weeks[i+1] for i in range(len(recent_weeks)-1)):
            patterns.append({
                "type": "declining_mood",
                "severity": "moderate",
                "message": "Your mood has been declining over the past few weeks. Consider reaching out for support.",
                "recommendation": "breathing_exercises"
            })
    
    return {
        "weekly_averages": weekly_averages,
        "patterns": patterns,
        "total_weeks": len(weekly_averages)
    }

@app.get("/api/v1/analytics/personalized-insights")
async def get_personalized_insights(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate personalized weekly mood insights with actionable recommendations"""
    
    user_id = current_user["user_id"]
    
    # Get mood data for the past 4 weeks for comprehensive analysis
    four_weeks_ago = datetime.utcnow() - timedelta(weeks=4)
    mood_entries = db.query(MoodEntry).filter(
        and_(
            MoodEntry.user_id == user_id,
            MoodEntry.created_at >= four_weeks_ago
        )
    ).order_by(desc(MoodEntry.created_at)).all()
    
    # Get journal entries for context
    journal_entries = db.query(JournalEntry).filter(
        and_(
            JournalEntry.user_id == user_id,
            JournalEntry.created_at >= four_weeks_ago
        )
    ).order_by(desc(JournalEntry.created_at)).all()
    
    insights = []
    
    if not mood_entries:
        return {
            "insights": [],
            "recommendations": [],
            "optimal_times": [],
            "weekly_summary": {
                "current_week_score": 0,
                "trend": "stable",
                "improvement_areas": []
            }
        }
    
    # Analyze current week vs previous weeks
    now = datetime.utcnow()
    current_week_start = now - timedelta(days=now.weekday())
    
    current_week_moods = [m for m in mood_entries if m.created_at >= current_week_start]
    previous_weeks_moods = [m for m in mood_entries if m.created_at < current_week_start]
    
    current_week_avg = sum(m.mood_score for m in current_week_moods) / len(current_week_moods) if current_week_moods else 0
    previous_avg = sum(m.mood_score for m in previous_weeks_moods) / len(previous_weeks_moods) if previous_weeks_moods else 0
    
    # Generate trend insights
    trend = "stable"
    if current_week_avg > previous_avg + 0.5:
        trend = "improving"
        insights.append({
            "id": "trend_positive",
            "type": "achievement",
            "title": "Positive Progress! 🌟",
            "description": f"Your mood has improved by {((current_week_avg - previous_avg) * 10):.0f}% this week",
            "actionable": "Keep doing what's working! Consider documenting your successful strategies.",
            "priority": "medium",
            "category": "mood"
        })
    elif current_week_avg < previous_avg - 0.5:
        trend = "declining"
        insights.append({
            "id": "trend_concern",
            "type": "support",
            "title": "Gentle Check-in 💙",
            "description": "Your mood has dipped slightly this week. This is completely normal.",
            "actionable": "Consider reaching out to a friend, practicing self-care, or reviewing recent stressors.",
            "priority": "high",
            "category": "wellness"
        })
    
    # Analyze time-of-day patterns for optimal intervention timing
    time_patterns = {}
    for mood in mood_entries:
        hour = mood.created_at.hour
        time_slot = "morning" if 6 <= hour < 12 else "afternoon" if 12 <= hour < 18 else "evening" if 18 <= hour < 22 else "night"
        
        if time_slot not in time_patterns:
            time_patterns[time_slot] = []
        time_patterns[time_slot].append(mood.mood_score)
    
    # Find optimal intervention times (when mood typically dips)
    optimal_times = []
    for time_slot, scores in time_patterns.items():
        if len(scores) >= 3:
            avg_score = sum(scores) / len(scores)
            if avg_score < 6:  # Below neutral mood
                optimal_times.append({
                    "time_of_day": time_slot,
                    "average_mood": avg_score,
                    "recommendation": f"Consider scheduling wellness activities during {time_slot} when your mood typically dips",
                    "effectiveness_score": 8.5 - avg_score  # Higher score for lower mood times
                })
    
    # Analyze day-of-week patterns
    day_patterns = {}
    for mood in mood_entries:
        day_name = mood.created_at.strftime("%A")
        if day_name not in day_patterns:
            day_patterns[day_name] = []
        day_patterns[day_name].append(mood.mood_score)
    
    # Identify challenging days
    challenging_days = []
    for day, scores in day_patterns.items():
        if len(scores) >= 2:
            avg_score = sum(scores) / len(scores)
            if avg_score < 6:
                challenging_days.append(day)
                insights.append({
                    "id": f"day_pattern_{day.lower()}",
                    "type": "pattern",
                    "title": f"{day} Pattern Noticed",
                    "description": f"Your mood tends to be lower on {day}s (avg: {avg_score:.1f}/10)",
                    "actionable": f"Plan lighter activities and extra self-care on {day}s",
                    "priority": "medium",
                    "category": "pattern"
                })
    
    # Generate personalized recommendations based on patterns
    recommendations = []
    
    if current_week_avg < 6:
        recommendations.append({
            "id": "mood_boost",
            "title": "Mood Enhancement Activities",
            "description": "Activities proven to boost mood based on your patterns",
            "actions": [
                "Take a 10-minute walk in nature",
                "Practice 5 minutes of deep breathing",
                "Connect with a supportive friend",
                "Listen to uplifting music"
            ],
            "estimated_time": "10-20 minutes",
            "expected_benefit": "Immediate mood lift, sustained energy"
        })
    
    if len(challenging_days) > 0:
        recommendations.append({
            "id": "challenging_day_prep",
            "title": f"Prepare for {challenging_days[0]}s",
            "description": "Proactive strategies for your typically challenging days",
            "actions": [
                f"Schedule something enjoyable for {challenging_days[0]} evening",
                "Prepare comfort items the night before",
                "Set a gentle morning routine",
                "Plan check-ins with supportive people"
            ],
            "estimated_time": "5-15 minutes of preparation",
            "expected_benefit": "Smoother difficult days, reduced stress"
        })
    
    if len(optimal_times) > 0:
        best_intervention_time = min(optimal_times, key=lambda x: x["average_mood"])
        recommendations.append({
            "id": "optimal_timing",
            "title": f"Strategic {best_intervention_time['time_of_day'].title()} Support",
            "description": f"Your mood typically dips during {best_intervention_time['time_of_day']} - perfect for proactive care",
            "actions": [
                f"Set a gentle reminder for {best_intervention_time['time_of_day']} wellness check-ins",
                "Practice mindfulness during this time",
                "Use this time for gentle movement or stretching",
                "Connect with community support"
            ],
            "estimated_time": "5-10 minutes",
            "expected_benefit": "Prevents mood dips, builds resilience"
        })
    
    return {
        "insights": insights,
        "recommendations": recommendations,
        "optimal_times": sorted(optimal_times, key=lambda x: x["effectiveness_score"], reverse=True),
        "weekly_summary": {
            "current_week_score": round(current_week_avg, 1),
            "previous_weeks_score": round(previous_avg, 1),
            "trend": trend,
            "improvement_areas": challenging_days,
            "total_entries": len(mood_entries),
            "days_tracked_this_week": len(current_week_moods)
        }
    }

@app.get("/api/v1/analytics/optimal-notification-times")
async def get_optimal_notification_times(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate optimal times for notifications based on user's mood patterns"""
    
    user_id = current_user["user_id"]
    
    # Get mood data for the past 6 weeks for pattern analysis
    six_weeks_ago = datetime.utcnow() - timedelta(weeks=6)
    mood_entries = db.query(MoodEntry).filter(
        and_(
            MoodEntry.user_id == user_id,
            MoodEntry.created_at >= six_weeks_ago
        )
    ).order_by(desc(MoodEntry.created_at)).all()
    
    if len(mood_entries) < 10:
        # Default notification schedule for new users
        return {
            "optimal_times": [
                {
                    "hour": 9,
                    "day_of_week": None,  # Any day
                    "effectiveness_score": 7.5,
                    "notification_type": "check_in",
                    "reason": "Morning check-ins help set a positive tone for the day"
                },
                {
                    "hour": 15,
                    "day_of_week": None,
                    "effectiveness_score": 8.0,
                    "notification_type": "mood_boost",
                    "reason": "Afternoon energy dips are common - perfect for gentle reminders"
                },
                {
                    "hour": 20,
                    "day_of_week": None,
                    "effectiveness_score": 7.0,
                    "notification_type": "reflection",
                    "reason": "Evening reflection helps process the day and prepare for rest"
                }
            ],
            "user_preferences": {
                "quiet_hours": {"start": 22, "end": 7},
                "frequency": "moderate",
                "types": ["check_in", "mood_boost", "reflection"]
            }
        }
    
    # Analyze hourly patterns to find low mood periods (intervention opportunities)
    hourly_patterns = {}
    daily_patterns = {}
    
    for mood in mood_entries:
        hour = mood.created_at.hour
        day_of_week = mood.created_at.weekday()  # 0 = Monday
        
        if hour not in hourly_patterns:
            hourly_patterns[hour] = []
        hourly_patterns[hour].append(mood.mood_score)
        
        if day_of_week not in daily_patterns:
            daily_patterns[day_of_week] = []
        daily_patterns[day_of_week].append(mood.mood_score)
    
    # Find optimal intervention hours (lower mood = higher intervention value)
    optimal_times = []
    
    for hour, scores in hourly_patterns.items():
        if len(scores) >= 3:  # Need enough data points
            avg_score = sum(scores) / len(scores)
            if 7 <= hour <= 21:  # Only suggest during waking hours
                effectiveness = 10 - avg_score  # Lower mood = higher effectiveness
                
                # Determine notification type based on time of day
                if 6 <= hour <= 10:
                    notification_type = "morning_boost"
                    reason = f"Morning support when your energy is typically {avg_score:.1f}/10"
                elif 11 <= hour <= 14:
                    notification_type = "midday_check"
                    reason = f"Midday wellness check when mood averages {avg_score:.1f}/10"
                elif 15 <= hour <= 18:
                    notification_type = "afternoon_support"
                    reason = f"Afternoon boost when you typically experience {avg_score:.1f}/10 mood"
                else:
                    notification_type = "evening_reflection"
                    reason = f"Evening mindfulness when mood is typically {avg_score:.1f}/10"
                
                optimal_times.append({
                    "hour": hour,
                    "day_of_week": None,
                    "effectiveness_score": round(effectiveness, 1),
                    "notification_type": notification_type,
                    "reason": reason,
                    "average_mood_at_time": round(avg_score, 1),
                    "sample_size": len(scores)
                })
    
    # Find challenging days for day-specific notifications
    challenging_days = []
    for day, scores in daily_patterns.items():
        if len(scores) >= 3:
            avg_score = sum(scores) / len(scores)
            if avg_score < 6:  # Below neutral
                day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                challenging_days.append({
                    "day_of_week": day,
                    "day_name": day_names[day],
                    "average_mood": round(avg_score, 1),
                    "recommended_hour": 8,  # Morning preparation
                    "notification_type": "day_preparation",
                    "reason": f"Prepare for {day_names[day]}s when your mood typically dips to {avg_score:.1f}/10"
                })
    
    # Sort by effectiveness and select top 3-4 times
    optimal_times.sort(key=lambda x: x["effectiveness_score"], reverse=True)
    selected_times = optimal_times[:3]
    
    # Add challenging day notifications
    selected_times.extend(challenging_days)
    
    return {
        "optimal_times": selected_times,
        "user_preferences": {
            "quiet_hours": {"start": 22, "end": 7},
            "frequency": "adaptive",  # Based on mood patterns
            "types": ["check_in", "mood_boost", "reflection", "preventive"]
        },
        "analysis_summary": {
            "data_points": len(mood_entries),
            "analysis_period_weeks": 6,
            "pattern_confidence": min(100, (len(mood_entries) / 42) * 100),  # 42 = ideal 1 entry per day for 6 weeks
            "next_update": (datetime.utcnow() + timedelta(weeks=1)).isoformat()
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mood-service"}

# User Data Management Endpoints
@app.delete("/api/v1/user/{user_id}/delete")
async def delete_user_data(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete all user data from mood service"""
    # Verify user authorization
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized to delete this user's data")
    
    try:
        # Delete mood entries
        mood_entries_deleted = db.query(MoodEntry).filter(MoodEntry.user_id == user_id).delete()
        
        # Delete journal entries
        journal_entries_deleted = db.query(JournalEntry).filter(JournalEntry.user_id == user_id).delete()
        
        db.commit()
        
        return {
            "message": "User data deleted successfully",
            "user_id": user_id,
            "deleted_items": {
                "mood_entries": mood_entries_deleted,
                "journal_entries": journal_entries_deleted
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete user data: {str(e)}")

@app.get("/api/v1/user/{user_id}/export")
async def export_user_data(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all user data from mood service"""
    # Verify user authorization
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized to export this user's data")
    
    try:
        # Get mood entries
        mood_entries = db.query(MoodEntry).filter(MoodEntry.user_id == user_id).all()
        mood_data = []
        for entry in mood_entries:
            mood_data.append({
                "id": entry.id,
                "mood_score": entry.mood_score,
                "energy_level": entry.energy_level,
                "stress_level": entry.stress_level,
                "sleep_quality": entry.sleep_quality,
                "notes": entry.notes,
                "context_tags": json.loads(entry.context_tags) if entry.context_tags else [],
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            })
        
        # Get journal entries
        journal_entries = db.query(JournalEntry).filter(JournalEntry.user_id == user_id).all()
        journal_data = []
        for entry in journal_entries:
            journal_data.append({
                "id": entry.id,
                "title": entry.title,
                "content": entry.content,
                "mood_before": entry.mood_before,
                "mood_after": entry.mood_after,
                "tags": json.loads(entry.tags) if entry.tags else [],
                "sentiment_score": entry.sentiment_score,
                "created_at": entry.created_at.isoformat() if entry.created_at else None
            })
        
        return {
            "user_id": user_id,
            "export_timestamp": datetime.utcnow().isoformat(),
            "data": {
                "mood_entries": mood_data,
                "journal_entries": journal_data,
                "summary": {
                    "total_mood_entries": len(mood_data),
                    "total_journal_entries": len(journal_data),
                    "date_range": {
                        "earliest_mood": mood_data[0]["created_at"] if mood_data else None,
                        "latest_mood": mood_data[-1]["created_at"] if mood_data else None,
                        "earliest_journal": journal_data[0]["created_at"] if journal_data else None,
                        "latest_journal": journal_data[-1]["created_at"] if journal_data else None
                    }
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export user data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)