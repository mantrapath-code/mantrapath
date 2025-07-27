"""
Mood Service - Comprehensive mood tracking, analytics, and insights
"""

from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_, extract
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
import uuid
from pydantic import BaseModel, UUID4, Field
import json
import redis
import numpy as np
from textblob import TextBlob
import asyncio

# Import shared modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.database import get_db
from shared.auth import get_current_user
from shared.models import (
    MoodEntry, JournalEntry, Habit, HabitEvent, User
)

app = FastAPI(
    title="MantraPath Mood Service",
    description="Comprehensive mood tracking, analytics, and insights",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis for caching
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Pydantic models
class MoodCreate(BaseModel):
    mood_score: int = Field(..., ge=1, le=10)
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    anxiety_level: Optional[int] = Field(None, ge=1, le=10)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    context_tags: Optional[List[str]] = []
    notes: Optional[str] = None
    location: Optional[str] = None
    weather: Optional[str] = None

class MoodResponse(BaseModel):
    id: UUID4
    mood_score: int
    energy_level: Optional[int]
    anxiety_level: Optional[int]
    stress_level: Optional[int]
    context_tags: List[str]
    notes: Optional[str]
    sentiment_score: Optional[float]
    detected_emotions: Optional[Dict[str, Any]]
    created_at: datetime

class JournalCreate(BaseModel):
    title: Optional[str] = None
    content: str
    mood_before: Optional[int] = Field(None, ge=1, le=10)
    mood_after: Optional[int] = Field(None, ge=1, le=10)
    is_private: bool = True
    tags: Optional[List[str]] = []

class JournalResponse(BaseModel):
    id: UUID4
    title: Optional[str]
    content: str
    mood_before: Optional[int]
    mood_after: Optional[int]
    sentiment_score: Optional[float]
    key_themes: Optional[List[str]]
    word_count: int
    is_private: bool
    tags: List[str]
    created_at: datetime

class HabitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    target_frequency: str = "daily"

class HabitResponse(BaseModel):
    id: UUID4
    name: str
    description: Optional[str]
    category: str
    target_frequency: str
    is_active: bool
    current_streak: int
    longest_streak: int
    total_completions: int
    created_at: datetime

class HabitEventCreate(BaseModel):
    notes: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    duration_minutes: Optional[int] = None

# Utility functions
def analyze_sentiment(text: str) -> float:
    """Analyze sentiment of text (-1 to 1)"""
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity
    except:
        return 0.0

def extract_emotions(text: str) -> Dict[str, float]:
    """Extract emotions from text using keyword matching"""
    emotion_keywords = {
        "joy": ["happy", "joyful", "excited", "cheerful", "glad", "delighted"],
        "sadness": ["sad", "depressed", "down", "melancholy", "blue", "gloomy"],
        "anger": ["angry", "mad", "furious", "irritated", "annoyed", "rage"],
        "fear": ["afraid", "scared", "anxious", "worried", "terrified", "nervous"],
        "surprise": ["surprised", "amazed", "shocked", "astonished", "stunned"],
        "disgust": ["disgusted", "revolted", "repulsed", "sick", "nauseated"]
    }
    
    text_lower = text.lower()
    emotions = {}
    
    for emotion, keywords in emotion_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        emotions[emotion] = min(1.0, score / len(keywords))
    
    return emotions

def extract_themes(text: str) -> List[str]:
    """Extract key themes from journal text"""
    # Simple keyword-based theme extraction
    theme_keywords = {
        "work": ["job", "work", "career", "office", "boss", "colleague", "meeting"],
        "relationships": ["friend", "family", "partner", "love", "relationship", "social"],
        "health": ["health", "exercise", "diet", "sleep", "medical", "doctor"],
        "stress": ["stress", "pressure", "overwhelmed", "busy", "deadline"],
        "growth": ["learn", "growth", "improve", "achieve", "goal", "progress"],
        "gratitude": ["grateful", "thankful", "blessed", "appreciate", "lucky"]
    }
    
    text_lower = text.lower()
    themes = []
    
    for theme, keywords in theme_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            themes.append(theme)
    
    return themes

def calculate_health_score(mood_entries: List[MoodEntry], habits: List[Habit]) -> float:
    """Calculate overall health score (0-100)"""
    if not mood_entries:
        return 50.0  # Default neutral score
    
    # Average mood score (1-10 scale)
    avg_mood = sum(entry.mood_score for entry in mood_entries) / len(mood_entries)
    mood_component = (avg_mood / 10) * 40  # 40% weight
    
    # Energy and stress levels
    energy_scores = [entry.energy_level for entry in mood_entries if entry.energy_level]
    stress_scores = [entry.stress_level for entry in mood_entries if entry.stress_level]
    
    avg_energy = sum(energy_scores) / len(energy_scores) if energy_scores else 5
    avg_stress = sum(stress_scores) / len(stress_scores) if stress_scores else 5
    
    energy_component = (avg_energy / 10) * 20  # 20% weight
    stress_component = ((10 - avg_stress) / 10) * 20  # 20% weight (inverted)
    
    # Habit consistency
    active_habits = [h for h in habits if h.is_active]
    if active_habits:
        avg_streak = sum(h.current_streak for h in active_habits) / len(active_habits)
        habit_component = min(20, avg_streak * 2)  # 20% weight, max 20
    else:
        habit_component = 10  # Default if no habits
    
    total_score = mood_component + energy_component + stress_component + habit_component
    return min(100, max(0, total_score))

# Mood tracking endpoints
@app.post("/api/v1/mood/", response_model=MoodResponse)
async def create_mood_entry(
    mood_data: MoodCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new mood entry"""
    
    # Analyze sentiment from notes
    sentiment_score = None
    detected_emotions = None
    
    if mood_data.notes:
        sentiment_score = analyze_sentiment(mood_data.notes)
        detected_emotions = extract_emotions(mood_data.notes)
    
    mood_entry = MoodEntry(
        id=uuid.uuid4(),
        user_id=current_user["user_id"],
        mood_score=mood_data.mood_score,
        energy_level=mood_data.energy_level,
        anxiety_level=mood_data.anxiety_level,
        stress_level=mood_data.stress_level,
        context_tags=mood_data.context_tags,
        notes=mood_data.notes,
        location=mood_data.location,
        weather=mood_data.weather,
        sentiment_score=sentiment_score,
        detected_emotions=detected_emotions
    )
    
    db.add(mood_entry)
    db.commit()
    db.refresh(mood_entry)
    
    # Clear user's mood cache
    redis_client.delete(f"mood_analytics:{current_user['user_id']}")
    
    # Schedule analytics update in background
    background_tasks.add_task(update_user_insights, current_user["user_id"], db)
    
    return MoodResponse(
        id=mood_entry.id,
        mood_score=mood_entry.mood_score,
        energy_level=mood_entry.energy_level,
        anxiety_level=mood_entry.anxiety_level,
        stress_level=mood_entry.stress_level,
        context_tags=mood_entry.context_tags or [],
        notes=mood_entry.notes,
        sentiment_score=mood_entry.sentiment_score,
        detected_emotions=mood_entry.detected_emotions,
        created_at=mood_entry.created_at
    )

@app.get("/api/v1/mood/", response_model=List[MoodResponse])
async def get_mood_entries(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get mood entries for user"""
    
    query = db.query(MoodEntry).filter(MoodEntry.user_id == current_user["user_id"])
    
    # Apply date filters
    if start_date:
        query = query.filter(MoodEntry.created_at >= start_date)
    if end_date:
        query = query.filter(MoodEntry.created_at <= end_date + timedelta(days=1))
    
    mood_entries = query.order_by(desc(MoodEntry.created_at)).offset(skip).limit(limit).all()
    
    return [
        MoodResponse(
            id=entry.id,
            mood_score=entry.mood_score,
            energy_level=entry.energy_level,
            anxiety_level=entry.anxiety_level,
            stress_level=entry.stress_level,
            context_tags=entry.context_tags or [],
            notes=entry.notes,
            sentiment_score=entry.sentiment_score,
            detected_emotions=entry.detected_emotions,
            created_at=entry.created_at
        )
        for entry in mood_entries
    ]

# Journal endpoints
@app.post("/api/v1/journal/", response_model=JournalResponse)
async def create_journal_entry(
    journal_data: JournalCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new journal entry"""
    
    # Analyze the content
    sentiment_score = analyze_sentiment(journal_data.content)
    key_themes = extract_themes(journal_data.content)
    word_count = len(journal_data.content.split())
    
    journal_entry = JournalEntry(
        id=uuid.uuid4(),
        user_id=current_user["user_id"],
        title=journal_data.title,
        content=journal_data.content,
        mood_before=journal_data.mood_before,
        mood_after=journal_data.mood_after,
        sentiment_score=sentiment_score,
        key_themes=key_themes,
        word_count=word_count,
        is_private=journal_data.is_private,
        tags=journal_data.tags or []
    )
    
    db.add(journal_entry)
    db.commit()
    db.refresh(journal_entry)
    
    # If mood before/after provided, create mood entries
    if journal_data.mood_before or journal_data.mood_after:
        if journal_data.mood_after:
            mood_entry = MoodEntry(
                id=uuid.uuid4(),
                user_id=current_user["user_id"],
                mood_score=journal_data.mood_after,
                context_tags=["journaling"],
                notes=f"After journaling: {journal_data.title or 'Untitled'}",
                sentiment_score=sentiment_score
            )
            db.add(mood_entry)
            db.commit()
    
    # Schedule insights update
    background_tasks.add_task(update_user_insights, current_user["user_id"], db)
    
    return JournalResponse(
        id=journal_entry.id,
        title=journal_entry.title,
        content=journal_entry.content,
        mood_before=journal_entry.mood_before,
        mood_after=journal_entry.mood_after,
        sentiment_score=journal_entry.sentiment_score,
        key_themes=journal_entry.key_themes or [],
        word_count=journal_entry.word_count,
        is_private=journal_entry.is_private,
        tags=journal_entry.tags or [],
        created_at=journal_entry.created_at
    )

@app.get("/api/v1/journal/", response_model=List[JournalResponse])
async def get_journal_entries(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get journal entries for user"""
    
    query = db.query(JournalEntry).filter(JournalEntry.user_id == current_user["user_id"])
    
    # Apply search filter
    if search:
        query = query.filter(
            or_(
                JournalEntry.title.ilike(f"%{search}%"),
                JournalEntry.content.ilike(f"%{search}%")
            )
        )
    
    # Apply tag filter
    if tag:
        query = query.filter(JournalEntry.tags.contains([tag]))
    
    entries = query.order_by(desc(JournalEntry.created_at)).offset(skip).limit(limit).all()
    
    return [
        JournalResponse(
            id=entry.id,
            title=entry.title,
            content=entry.content,
            mood_before=entry.mood_before,
            mood_after=entry.mood_after,
            sentiment_score=entry.sentiment_score,
            key_themes=entry.key_themes or [],
            word_count=entry.word_count,
            is_private=entry.is_private,
            tags=entry.tags or [],
            created_at=entry.created_at
        )
        for entry in entries
    ]

# Habit tracking endpoints
@app.post("/api/v1/habits/", response_model=HabitResponse)
async def create_habit(
    habit_data: HabitCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new habit"""
    
    habit = Habit(
        id=uuid.uuid4(),
        user_id=current_user["user_id"],
        name=habit_data.name,
        description=habit_data.description,
        category=habit_data.category,
        target_frequency=habit_data.target_frequency,
        is_active=True
    )
    
    db.add(habit)
    db.commit()
    db.refresh(habit)
    
    return HabitResponse(
        id=habit.id,
        name=habit.name,
        description=habit.description,
        category=habit.category,
        target_frequency=habit.target_frequency,
        is_active=habit.is_active,
        current_streak=habit.current_streak,
        longest_streak=habit.longest_streak,
        total_completions=habit.total_completions,
        created_at=habit.created_at
    )

@app.get("/api/v1/habits/", response_model=List[HabitResponse])
async def get_habits(
    active_only: bool = Query(True),
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user's habits"""
    
    query = db.query(Habit).filter(Habit.user_id == current_user["user_id"])
    
    if active_only:
        query = query.filter(Habit.is_active == True)
    
    if category:
        query = query.filter(Habit.category == category)
    
    habits = query.order_by(Habit.name).all()
    
    return [
        HabitResponse(
            id=habit.id,
            name=habit.name,
            description=habit.description,
            category=habit.category,
            target_frequency=habit.target_frequency,
            is_active=habit.is_active,
            current_streak=habit.current_streak,
            longest_streak=habit.longest_streak,
            total_completions=habit.total_completions,
            created_at=habit.created_at
        )
        for habit in habits
    ]

@app.post("/api/v1/habits/{habit_id}/events")
async def complete_habit(
    habit_id: UUID4,
    event_data: HabitEventCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Mark habit as completed"""
    
    # Verify habit belongs to user
    habit = db.query(Habit).filter(
        and_(Habit.id == habit_id, Habit.user_id == current_user["user_id"])
    ).first()
    
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    # Check if already completed today
    today = date.today()
    existing_event = db.query(HabitEvent).filter(
        and_(
            HabitEvent.habit_id == habit_id,
            HabitEvent.user_id == current_user["user_id"],
            func.date(HabitEvent.completed_at) == today
        )
    ).first()
    
    if existing_event:
        raise HTTPException(status_code=400, detail="Habit already completed today")
    
    # Create habit event
    event = HabitEvent(
        id=uuid.uuid4(),
        habit_id=habit_id,
        user_id=current_user["user_id"],
        notes=event_data.notes,
        rating=event_data.rating,
        duration_minutes=event_data.duration_minutes
    )
    
    db.add(event)
    
    # Update habit statistics
    habit.total_completions += 1
    
    # Calculate streak
    yesterday = today - timedelta(days=1)
    yesterday_event = db.query(HabitEvent).filter(
        and_(
            HabitEvent.habit_id == habit_id,
            HabitEvent.user_id == current_user["user_id"],
            func.date(HabitEvent.completed_at) == yesterday
        )
    ).first()
    
    if yesterday_event:
        habit.current_streak += 1
    else:
        habit.current_streak = 1
    
    if habit.current_streak > habit.longest_streak:
        habit.longest_streak = habit.current_streak
    
    db.commit()
    
    # Schedule insights update
    background_tasks.add_task(update_user_insights, current_user["user_id"], db)
    
    return {
        "message": "Habit completed successfully",
        "current_streak": habit.current_streak,
        "total_completions": habit.total_completions
    }

# Analytics endpoints
@app.get("/api/v1/analytics/overview")
async def get_analytics_overview(
    period: str = Query("week", regex="^(week|month|quarter|year)$"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get comprehensive analytics overview"""
    
    # Check cache first
    cache_key = f"mood_analytics:{current_user['user_id']}:{period}"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    
    # Calculate date range
    end_date = datetime.utcnow()
    if period == "week":
        start_date = end_date - timedelta(days=7)
    elif period == "month":
        start_date = end_date - timedelta(days=30)
    elif period == "quarter":
        start_date = end_date - timedelta(days=90)
    else:  # year
        start_date = end_date - timedelta(days=365)
    
    user_id = current_user["user_id"]
    
    # Get mood entries
    mood_entries = db.query(MoodEntry).filter(
        and_(
            MoodEntry.user_id == user_id,
            MoodEntry.created_at >= start_date
        )
    ).all()
    
    # Get journal entries
    journal_entries = db.query(JournalEntry).filter(
        and_(
            JournalEntry.user_id == user_id,
            JournalEntry.created_at >= start_date
        )
    ).count()
    
    # Get habits
    habits = db.query(Habit).filter(
        and_(Habit.user_id == user_id, Habit.is_active == True)
    ).all()
    
    # Calculate metrics
    if mood_entries:
        avg_mood = sum(entry.mood_score for entry in mood_entries) / len(mood_entries)
        avg_energy = sum(entry.energy_level for entry in mood_entries if entry.energy_level) / max(1, len([e for e in mood_entries if e.energy_level]))
        avg_stress = sum(entry.stress_level for entry in mood_entries if entry.stress_level) / max(1, len([e for e in mood_entries if e.stress_level]))
        
        # Mood trend
        if len(mood_entries) >= 2:
            recent_half = mood_entries[:len(mood_entries)//2]
            older_half = mood_entries[len(mood_entries)//2:]
            recent_avg = sum(entry.mood_score for entry in recent_half) / len(recent_half)
            older_avg = sum(entry.mood_score for entry in older_half) / len(older_half)
            mood_trend = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
        else:
            mood_trend = "stable"
    else:
        avg_mood = avg_energy = avg_stress = 0
        mood_trend = "no_data"
    
    # Calculate health score
    health_score = calculate_health_score(mood_entries, habits)
    
    # Habit completion rate
    if habits:
        total_possible_completions = len(habits) * 7  # Assuming daily habits for week
        actual_completions = sum(habit.current_streak for habit in habits)
        habit_completion_rate = min(100, (actual_completions / total_possible_completions) * 100)
    else:
        habit_completion_rate = 0
    
    analytics_data = {
        "period": period,
        "health_score": round(health_score, 1),
        "mood_average": round(avg_mood, 1),
        "energy_average": round(avg_energy, 1),
        "stress_average": round(avg_stress, 1),
        "mood_trend": mood_trend,
        "mood_entries_count": len(mood_entries),
        "journal_entries_count": journal_entries,
        "active_habits_count": len(habits),
        "habit_completion_rate": round(habit_completion_rate, 1),
        "insights": generate_insights(mood_entries, habits, period)
    }
    
    # Cache for 1 hour
    redis_client.setex(cache_key, 3600, json.dumps(analytics_data))
    
    return analytics_data

def generate_insights(mood_entries: List[MoodEntry], habits: List[Habit], period: str) -> List[str]:
    """Generate personalized insights"""
    insights = []
    
    if not mood_entries:
        insights.append("Start logging your mood daily to get personalized insights!")
        return insights
    
    avg_mood = sum(entry.mood_score for entry in mood_entries) / len(mood_entries)
    
    if avg_mood >= 7:
        insights.append("You've been maintaining a positive mood! Keep up the great work.")
    elif avg_mood <= 4:
        insights.append("Your mood has been lower lately. Consider talking to someone or trying stress-reduction techniques.")
    else:
        insights.append("Your mood is in a neutral range. Small positive changes could make a big difference.")
    
    # Context tag analysis
    all_tags = []
    for entry in mood_entries:
        if entry.context_tags:
            all_tags.extend(entry.context_tags)
    
    if all_tags:
        from collections import Counter
        common_tags = Counter(all_tags).most_common(3)
        insights.append(f"Your most common mood contexts: {', '.join([tag for tag, _ in common_tags])}")
    
    # Habit insights
    if habits:
        total_streak = sum(habit.current_streak for habit in habits)
        avg_streak = total_streak / len(habits)
        if avg_streak >= 7:
            insights.append("Excellent habit consistency! Your routines are really paying off.")
        elif avg_streak >= 3:
            insights.append("Good habit progress. Try to maintain consistency for even better results.")
        else:
            insights.append("Focus on building consistent habits. Start small and gradually increase.")
    
    return insights

async def update_user_insights(user_id: str, db: Session):
    """Background task to update user insights"""
    # This would contain logic to generate new insights
    # For now, just clear the cache to force regeneration
    redis_client.delete(f"mood_analytics:{user_id}:*")

# Weekly patterns
@app.get("/api/v1/analytics/patterns/weekly")
async def get_weekly_patterns(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get weekly mood patterns"""
    
    # Get mood entries from last 4 weeks
    four_weeks_ago = datetime.utcnow() - timedelta(days=28)
    mood_entries = db.query(MoodEntry).filter(
        and_(
            MoodEntry.user_id == current_user["user_id"],
            MoodEntry.created_at >= four_weeks_ago
        )
    ).all()
    
    # Group by day of week
    day_patterns = {i: [] for i in range(7)}  # 0=Monday, 6=Sunday
    
    for entry in mood_entries:
        day_of_week = entry.created_at.weekday()
        day_patterns[day_of_week].append(entry.mood_score)
    
    # Calculate averages
    weekly_pattern = {}
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for day_num, scores in day_patterns.items():
        if scores:
            weekly_pattern[days[day_num]] = {
                "average_mood": round(sum(scores) / len(scores), 1),
                "entry_count": len(scores)
            }
        else:
            weekly_pattern[days[day_num]] = {
                "average_mood": None,
                "entry_count": 0
            }
    
    return {
        "weekly_pattern": weekly_pattern,
        "analysis_period": "4_weeks",
        "total_entries": len(mood_entries)
    }

# Health check
@app.get("/health")
async def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "service": "mood_service",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)