"""
Mood Tracking Service for MantraPath
Handles mood entries, analytics, and insights
"""
from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import sys
import os

# Add shared modules to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
shared_dir = os.path.join(backend_dir, "shared")
sys.path.insert(0, shared_dir)

from database import get_db, create_tables
from auth import verify_token
from models import User, MoodEntry

app = FastAPI(
    title="MantraPath Mood Service",
    description="Mood tracking and analytics service",
    version="1.0.0"
)

security = HTTPBearer()

# Pydantic models
class MoodEntryCreate(BaseModel):
    mood_score: int  # 1-5 scale
    energy_level: Optional[int] = 3
    stress_level: Optional[int] = 3
    sleep_quality: Optional[int] = 3
    notes: Optional[str] = ""
    context_tags: Optional[List[str]] = []

class MoodEntryResponse(BaseModel):
    id: str
    mood_score: int
    energy_level: int
    stress_level: int
    sleep_quality: int
    notes: str
    context_tags: List[str]
    created_at: datetime

class MoodAnalyticsResponse(BaseModel):
    average_mood: float
    mood_trend: str
    total_entries: int
    streak: int
    weekly_pattern: Dict[str, float]
    monthly_summary: Dict[str, Any]

class WeeklyPatternsResponse(BaseModel):
    weekly_averages: Dict[str, float]
    patterns: List[Dict[str, str]]
    total_weeks: int

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user

@app.on_event("startup")
async def startup_event():
    """Initialize database tables"""
    create_tables()

@app.get("/api/v1/mood/", response_model=List[MoodEntryResponse])
async def get_mood_entries(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's mood entries"""
    entries = db.query(MoodEntry)\
        .filter(MoodEntry.user_id == current_user.id)\
        .order_by(desc(MoodEntry.created_at))\
        .offset(offset)\
        .limit(limit)\
        .all()
    
    return [
        MoodEntryResponse(
            id=entry.id,
            mood_score=entry.mood_score,
            energy_level=entry.energy_level or 3,
            stress_level=entry.stress_level or 3,
            sleep_quality=entry.sleep_quality or 3,
            notes=entry.notes or "",
            context_tags=entry.context_tags or [],
            created_at=entry.created_at
        )
        for entry in entries
    ]

@app.post("/api/v1/mood/", response_model=MoodEntryResponse)
async def create_mood_entry(
    mood_data: MoodEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new mood entry"""
    
    # Validate mood score
    if not 1 <= mood_data.mood_score <= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mood score must be between 1 and 5"
        )
    
    new_entry = MoodEntry(
        user_id=current_user.id,
        mood_score=mood_data.mood_score,
        energy_level=mood_data.energy_level,
        stress_level=mood_data.stress_level,
        sleep_quality=mood_data.sleep_quality,
        notes=mood_data.notes,
        context_tags=mood_data.context_tags
    )
    
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    
    return MoodEntryResponse(
        id=new_entry.id,
        mood_score=new_entry.mood_score,
        energy_level=new_entry.energy_level or 3,
        stress_level=new_entry.stress_level or 3,
        sleep_quality=new_entry.sleep_quality or 3,
        notes=new_entry.notes or "",
        context_tags=new_entry.context_tags or [],
        created_at=new_entry.created_at
    )

@app.get("/api/v1/analytics/overview", response_model=MoodAnalyticsResponse)
async def get_analytics_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get mood analytics overview"""
    
    # Get all user's mood entries
    entries = db.query(MoodEntry)\
        .filter(MoodEntry.user_id == current_user.id)\
        .order_by(desc(MoodEntry.created_at))\
        .all()
    
    if not entries:
        return MoodAnalyticsResponse(
            average_mood=3.0,
            mood_trend="stable",
            total_entries=0,
            streak=0,
            weekly_pattern={},
            monthly_summary={}
        )
    
    # Calculate average mood
    average_mood = sum(entry.mood_score for entry in entries) / len(entries)
    
    # Determine mood trend (last 7 vs previous 7 entries)
    recent_entries = entries[:7]
    previous_entries = entries[7:14] if len(entries) > 7 else []
    
    recent_avg = sum(e.mood_score for e in recent_entries) / len(recent_entries) if recent_entries else 3
    previous_avg = sum(e.mood_score for e in previous_entries) / len(previous_entries) if previous_entries else recent_avg
    
    if recent_avg > previous_avg + 0.3:
        mood_trend = "improving"
    elif recent_avg < previous_avg - 0.3:
        mood_trend = "declining"
    else:
        mood_trend = "stable"
    
    # Calculate streak (consecutive days with entries)
    streak = calculate_mood_streak(entries)
    
    # Weekly pattern (average by day of week)
    weekly_pattern = calculate_weekly_pattern(entries)
    
    # Monthly summary
    monthly_summary = {
        "highest_mood": max(entry.mood_score for entry in entries),
        "lowest_mood": min(entry.mood_score for entry in entries),
        "total_days_tracked": len(set(entry.created_at.date() for entry in entries)),
        "most_common_stress_level": 3  # Default for now
    }
    
    return MoodAnalyticsResponse(
        average_mood=round(average_mood, 2),
        mood_trend=mood_trend,
        total_entries=len(entries),
        streak=streak,
        weekly_pattern=weekly_pattern,
        monthly_summary=monthly_summary
    )

@app.get("/api/v1/analytics/patterns/weekly", response_model=WeeklyPatternsResponse)
async def get_weekly_patterns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weekly mood patterns and insights"""
    
    # Get recent entries for pattern analysis
    cutoff_date = datetime.utcnow() - timedelta(weeks=4)
    entries = db.query(MoodEntry)\
        .filter(
            and_(
                MoodEntry.user_id == current_user.id,
                MoodEntry.created_at >= cutoff_date
            )
        )\
        .order_by(desc(MoodEntry.created_at))\
        .all()
    
    weekly_averages = calculate_weekly_pattern(entries)
    
    # Generate patterns based on analysis
    patterns = []
    
    # Check for concerning patterns
    recent_moods = [entry.mood_score for entry in entries[:7]]
    if recent_moods and sum(recent_moods) / len(recent_moods) < 2.5:
        patterns.append({
            "type": "concerning",
            "severity": "medium",
            "message": "Your mood has been lower than usual this week",
            "recommendation": "Consider talking to someone or trying relaxation techniques"
        })
    
    # Check for positive patterns
    if recent_moods and sum(recent_moods) / len(recent_moods) > 4:
        patterns.append({
            "type": "positive",
            "severity": "low",
            "message": "You've been maintaining great mood levels!",
            "recommendation": "Keep up the great work with your current routine"
        })
    
    return WeeklyPatternsResponse(
        weekly_averages=weekly_averages,
        patterns=patterns,
        total_weeks=4
    )

def calculate_mood_streak(entries: List[MoodEntry]) -> int:
    """Calculate consecutive days with mood entries"""
    if not entries:
        return 0
    
    dates = sorted(set(entry.created_at.date() for entry in entries), reverse=True)
    
    streak = 0
    current_date = datetime.utcnow().date()
    
    for date in dates:
        if date == current_date - timedelta(days=streak):
            streak += 1
        else:
            break
    
    return streak

def calculate_weekly_pattern(entries: List[MoodEntry]) -> Dict[str, float]:
    """Calculate average mood by day of week"""
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    daily_moods = {day: [] for day in day_names}
    
    for entry in entries:
        day_name = day_names[entry.created_at.weekday()]
        daily_moods[day_name].append(entry.mood_score)
    
    return {
        day: round(sum(moods) / len(moods), 2) if moods else 3.0
        for day, moods in daily_moods.items()
    }

@app.get("/health")
async def health_check():
    """Service health check"""
    return {"status": "healthy", "service": "mood"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)