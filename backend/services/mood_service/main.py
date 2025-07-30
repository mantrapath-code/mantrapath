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
    limit: int = Query(50, le=100),
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