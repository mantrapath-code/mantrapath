"""
Mood Service for MantraPath
Handles mood tracking, journal entries, habits, insights, and analytics
"""

from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Integer, Text, DECIMAL, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
import uuid
import os
import redis.asyncio as redis
import json
import logging
from pydantic import BaseModel, Field
import asyncio
from collections import defaultdict
import statistics
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://mantrapath_user:mantrapath_password@postgres:5432/mantrapath")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/3")

# InfluxDB setup for time-series analytics
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "your_influxdb_token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "mantrapath")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "mood_analytics")

app = FastAPI(
    title="MantraPath Mood Service",
    description="Mood tracking, journaling, habits, and wellness analytics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Models
class MoodEntry(Base):
    __tablename__ = "mood_entries"
    __table_args__ = {'schema': 'mood'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    mood_value = Column(Integer, nullable=False)  # 1-10 scale
    energy_level = Column(Integer)  # 1-10 scale
    stress_level = Column(Integer)  # 1-10 scale
    anxiety_level = Column(Integer)  # 1-10 scale
    sleep_quality = Column(Integer)  # 1-10 scale
    notes = Column(Text)
    context_tags = Column(ARRAY(String))
    weather = Column(String(50))
    location = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    __table_args__ = {'schema': 'mood'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    title = Column(String(200))
    content = Column(Text, nullable=False)
    sentiment_score = Column(DECIMAL(3,2))  # -1.0 to 1.0
    sentiment_label = Column(String(20))  # positive, negative, neutral
    mood_id = Column(UUID(as_uuid=True))
    tags = Column(ARRAY(String))
    is_private = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Habit(Base):
    __tablename__ = "habits"
    __table_args__ = {'schema': 'mood'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    target_frequency = Column(Integer, default=1)
    frequency_unit = Column(String(10), default="daily")  # daily, weekly, monthly
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HabitEvent(Base):
    __tablename__ = "habit_events"
    __table_args__ = {'schema': 'mood'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    habit_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    mood_impact = Column(Integer)  # -5 to 5 scale

class Insight(Base):
    __tablename__ = "insights"
    __table_args__ = {'schema': 'mood'}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    confidence_score = Column(DECIMAL(3,2))
    data_points = Column(JSONB)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

# Pydantic Models
class MoodEntryCreate(BaseModel):
    mood_value: int = Field(..., ge=1, le=10)
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    anxiety_level: Optional[int] = Field(None, ge=1, le=10)
    sleep_quality: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    context_tags: Optional[List[str]] = []
    weather: Optional[str] = None
    location: Optional[str] = None

class MoodEntryResponse(BaseModel):
    id: str
    user_id: str
    mood_value: int
    energy_level: Optional[int]
    stress_level: Optional[int]
    anxiety_level: Optional[int]
    sleep_quality: Optional[int]
    notes: Optional[str]
    context_tags: Optional[List[str]]
    weather: Optional[str]
    location: Optional[str]
    created_at: datetime
    updated_at: datetime

class JournalEntryCreate(BaseModel):
    title: Optional[str] = None
    content: str
    mood_id: Optional[str] = None
    tags: Optional[List[str]] = []
    is_private: bool = True

class JournalEntryResponse(BaseModel):
    id: str
    user_id: str
    title: Optional[str]
    content: str
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]
    mood_id: Optional[str]
    tags: Optional[List[str]]
    is_private: bool
    created_at: datetime
    updated_at: datetime

class HabitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    target_frequency: int = 1
    frequency_unit: str = "daily"

class HabitResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    category: Optional[str]
    target_frequency: int
    frequency_unit: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class HabitEventCreate(BaseModel):
    habit_id: str
    notes: Optional[str] = None
    mood_impact: Optional[int] = Field(None, ge=-5, le=5)

class HabitEventResponse(BaseModel):
    id: str
    habit_id: str
    user_id: str
    completed_at: datetime
    notes: Optional[str]
    mood_impact: Optional[int]

class InsightResponse(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    content: str
    confidence_score: Optional[float]
    data_points: Optional[Dict[str, Any]]
    is_read: bool
    created_at: datetime
    expires_at: Optional[datetime]

class WeeklyAnalytics(BaseModel):
    average_mood: float
    mood_trend: str  # improving, declining, stable
    total_journal_entries: int
    habits_completed: int
    stress_levels: List[int]
    energy_levels: List[int]
    insights_count: int

# Utility functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_redis():
    return redis.from_url(REDIS_URL, decode_responses=True)

def get_user_id_from_header(x_user_id: str = Header(...)) -> str:
    """Extract user ID from header set by API Gateway"""
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in request headers"
        )
    return x_user_id

async def analyze_sentiment(text: str) -> tuple[float, str]:
    """Simple sentiment analysis - replace with ML model in production"""
    positive_words = ['happy', 'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'joy', 'excited']
    negative_words = ['sad', 'bad', 'terrible', 'awful', 'horrible', 'hate', 'angry', 'depressed', 'anxious', 'worried']
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    total_words = len(text_lower.split())
    if total_words == 0:
        return 0.0, "neutral"
    
    sentiment_score = (positive_count - negative_count) / max(total_words, 1)
    sentiment_score = max(-1.0, min(1.0, sentiment_score))  # Clamp to [-1, 1]
    
    if sentiment_score > 0.1:
        sentiment_label = "positive"
    elif sentiment_score < -0.1:
        sentiment_label = "negative"
    else:
        sentiment_label = "neutral"
    
    return sentiment_score, sentiment_label

async def write_to_influxdb(user_id: str, mood_data: dict):
    """Write mood data to InfluxDB for analytics"""
    try:
        client = influxdb_client.InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )
        write_api = client.write_api(write_options=SYNCHRONOUS)
        
        point = influxdb_client.Point("mood_entry") \
            .tag("user_id", user_id) \
            .field("mood_value", mood_data["mood_value"]) \
            .field("energy_level", mood_data.get("energy_level", 0)) \
            .field("stress_level", mood_data.get("stress_level", 0)) \
            .field("anxiety_level", mood_data.get("anxiety_level", 0)) \
            .field("sleep_quality", mood_data.get("sleep_quality", 0)) \
            .time(datetime.utcnow())
        
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        client.close()
    except Exception as e:
        logger.error(f"Failed to write to InfluxDB: {e}")

# Routes
@app.get("/")
async def root():
    return {"message": "MantraPath Mood Service", "version": "1.0.0"}

# Mood Tracking Endpoints
@app.post("/api/v1/mood/", response_model=MoodEntryResponse)
async def create_mood_entry(
    mood_data: MoodEntryCreate,
    user_id: str = Depends(get_user_id_from_header),
    db: Session = Depends(get_db)
):
    db_mood = MoodEntry(
        user_id=uuid.UUID(user_id),
        **mood_data.dict()
    )
    
    db.add(db_mood)
    db.commit()
    db.refresh(db_mood)
    
    # Write to InfluxDB for analytics
    await write_to_influxdb(user_id, mood_data.dict())
    
    logger.info(f"Mood entry created for user {user_id}")
    
    return MoodEntryResponse(
        id=str(db_mood.id),
        user_id=str(db_mood.user_id),
        mood_value=db_mood.mood_value,
        energy_level=db_mood.energy_level,
        stress_level=db_mood.stress_level,
        anxiety_level=db_mood.anxiety_level,
        sleep_quality=db_mood.sleep_quality,
        notes=db_mood.notes,
        context_tags=db_mood.context_tags or [],
        weather=db_mood.weather,
        location=db_mood.location,
        created_at=db_mood.created_at,
        updated_at=db_mood.updated_at
    )

@app.get("/api/v1/mood/", response_model=List[MoodEntryResponse])
async def get_mood_entries(
    user_id: str = Depends(get_user_id_from_header),
    limit: int = 50,
    skip: int = 0,
    db: Session = Depends(get_db)
):
    entries = db.query(MoodEntry).filter(
        MoodEntry.user_id == uuid.UUID(user_id)
    ).order_by(MoodEntry.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        MoodEntryResponse(
            id=str(entry.id),
            user_id=str(entry.user_id),
            mood_value=entry.mood_value,
            energy_level=entry.energy_level,
            stress_level=entry.stress_level,
            anxiety_level=entry.anxiety_level,
            sleep_quality=entry.sleep_quality,
            notes=entry.notes,
            context_tags=entry.context_tags or [],
            weather=entry.weather,
            location=entry.location,
            created_at=entry.created_at,
            updated_at=entry.updated_at
        )
        for entry in entries
    ]

# Journal Endpoints
@app.post("/api/v1/journal/", response_model=JournalEntryResponse)
async def create_journal_entry(
    journal_data: JournalEntryCreate,
    user_id: str = Depends(get_user_id_from_header),
    db: Session = Depends(get_db)
):
    # Analyze sentiment
    sentiment_score, sentiment_label = await analyze_sentiment(journal_data.content)
    
    db_journal = JournalEntry(
        user_id=uuid.UUID(user_id),
        title=journal_data.title,
        content=journal_data.content,
        sentiment_score=sentiment_score,
        sentiment_label=sentiment_label,
        mood_id=uuid.UUID(journal_data.mood_id) if journal_data.mood_id else None,
        tags=journal_data.tags,
        is_private=journal_data.is_private
    )
    
    db.add(db_journal)
    db.commit()
    db.refresh(db_journal)
    
    logger.info(f"Journal entry created for user {user_id}")
    
    return JournalEntryResponse(
        id=str(db_journal.id),
        user_id=str(db_journal.user_id),
        title=db_journal.title,
        content=db_journal.content,
        sentiment_score=float(db_journal.sentiment_score) if db_journal.sentiment_score else None,
        sentiment_label=db_journal.sentiment_label,
        mood_id=str(db_journal.mood_id) if db_journal.mood_id else None,
        tags=db_journal.tags or [],
        is_private=db_journal.is_private,
        created_at=db_journal.created_at,
        updated_at=db_journal.updated_at
    )

@app.get("/api/v1/journal/", response_model=List[JournalEntryResponse])
async def get_journal_entries(
    user_id: str = Depends(get_user_id_from_header),
    limit: int = 50,
    skip: int = 0,
    db: Session = Depends(get_db)
):
    entries = db.query(JournalEntry).filter(
        JournalEntry.user_id == uuid.UUID(user_id)
    ).order_by(JournalEntry.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        JournalEntryResponse(
            id=str(entry.id),
            user_id=str(entry.user_id),
            title=entry.title,
            content=entry.content,
            sentiment_score=float(entry.sentiment_score) if entry.sentiment_score else None,
            sentiment_label=entry.sentiment_label,
            mood_id=str(entry.mood_id) if entry.mood_id else None,
            tags=entry.tags or [],
            is_private=entry.is_private,
            created_at=entry.created_at,
            updated_at=entry.updated_at
        )
        for entry in entries
    ]

# Habits Endpoints
@app.post("/api/v1/habits/", response_model=HabitResponse)
async def create_habit(
    habit_data: HabitCreate,
    user_id: str = Depends(get_user_id_from_header),
    db: Session = Depends(get_db)
):
    db_habit = Habit(
        user_id=uuid.UUID(user_id),
        **habit_data.dict()
    )
    
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    
    return HabitResponse(
        id=str(db_habit.id),
        user_id=str(db_habit.user_id),
        name=db_habit.name,
        description=db_habit.description,
        category=db_habit.category,
        target_frequency=db_habit.target_frequency,
        frequency_unit=db_habit.frequency_unit,
        is_active=db_habit.is_active,
        created_at=db_habit.created_at,
        updated_at=db_habit.updated_at
    )

@app.get("/api/v1/habits/", response_model=List[HabitResponse])
async def get_habits(
    user_id: str = Depends(get_user_id_from_header),
    db: Session = Depends(get_db)
):
    habits = db.query(Habit).filter(
        Habit.user_id == uuid.UUID(user_id),
        Habit.is_active == True
    ).all()
    
    return [
        HabitResponse(
            id=str(habit.id),
            user_id=str(habit.user_id),
            name=habit.name,
            description=habit.description,
            category=habit.category,
            target_frequency=habit.target_frequency,
            frequency_unit=habit.frequency_unit,
            is_active=habit.is_active,
            created_at=habit.created_at,
            updated_at=habit.updated_at
        )
        for habit in habits
    ]

@app.post("/api/v1/habits/{habit_id}/events", response_model=HabitEventResponse)
async def create_habit_event(
    habit_id: str,
    event_data: HabitEventCreate,
    user_id: str = Depends(get_user_id_from_header),
    db: Session = Depends(get_db)
):
    # Verify habit belongs to user
    habit = db.query(Habit).filter(
        Habit.id == uuid.UUID(habit_id),
        Habit.user_id == uuid.UUID(user_id)
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    db_event = HabitEvent(
        habit_id=uuid.UUID(habit_id),
        user_id=uuid.UUID(user_id),
        notes=event_data.notes,
        mood_impact=event_data.mood_impact
    )
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    return HabitEventResponse(
        id=str(db_event.id),
        habit_id=str(db_event.habit_id),
        user_id=str(db_event.user_id),
        completed_at=db_event.completed_at,
        notes=db_event.notes,
        mood_impact=db_event.mood_impact
    )

# Analytics Endpoints
@app.get("/api/v1/analytics/overview", response_model=WeeklyAnalytics)
async def get_weekly_analytics(
    user_id: str = Depends(get_user_id_from_header),
    db: Session = Depends(get_db)
):
    # Get data from last 7 days
    start_date = datetime.utcnow() - timedelta(days=7)
    
    # Mood entries
    mood_entries = db.query(MoodEntry).filter(
        MoodEntry.user_id == uuid.UUID(user_id),
        MoodEntry.created_at >= start_date
    ).all()
    
    # Journal entries
    journal_count = db.query(JournalEntry).filter(
        JournalEntry.user_id == uuid.UUID(user_id),
        JournalEntry.created_at >= start_date
    ).count()
    
    # Habit events
    habit_events_count = db.query(HabitEvent).filter(
        HabitEvent.user_id == uuid.UUID(user_id),
        HabitEvent.completed_at >= start_date
    ).count()
    
    # Insights
    insights_count = db.query(Insight).filter(
        Insight.user_id == uuid.UUID(user_id),
        Insight.created_at >= start_date
    ).count()
    
    # Calculate analytics
    if mood_entries:
        mood_values = [entry.mood_value for entry in mood_entries]
        average_mood = statistics.mean(mood_values)
        
        # Determine trend (simple comparison with previous week)
        prev_start = start_date - timedelta(days=7)
        prev_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == uuid.UUID(user_id),
            MoodEntry.created_at >= prev_start,
            MoodEntry.created_at < start_date
        ).all()
        
        if prev_entries:
            prev_average = statistics.mean([entry.mood_value for entry in prev_entries])
            if average_mood > prev_average + 0.5:
                trend = "improving"
            elif average_mood < prev_average - 0.5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        stress_levels = [entry.stress_level for entry in mood_entries if entry.stress_level]
        energy_levels = [entry.energy_level for entry in mood_entries if entry.energy_level]
    else:
        average_mood = 5.0
        trend = "stable"
        stress_levels = []
        energy_levels = []
    
    return WeeklyAnalytics(
        average_mood=round(average_mood, 1),
        mood_trend=trend,
        total_journal_entries=journal_count,
        habits_completed=habit_events_count,
        stress_levels=stress_levels,
        energy_levels=energy_levels,
        insights_count=insights_count
    )

@app.get("/api/v1/analytics/patterns/weekly")
async def get_weekly_patterns(
    user_id: str = Depends(get_user_id_from_header),
    weeks: int = 4,
    db: Session = Depends(get_db)
):
    patterns = []
    
    for week in range(weeks):
        start_date = datetime.utcnow() - timedelta(days=(week + 1) * 7)
        end_date = datetime.utcnow() - timedelta(days=week * 7)
        
        mood_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == uuid.UUID(user_id),
            MoodEntry.created_at >= start_date,
            MoodEntry.created_at < end_date
        ).all()
        
        if mood_entries:
            avg_mood = statistics.mean([entry.mood_value for entry in mood_entries])
            avg_energy = statistics.mean([entry.energy_level for entry in mood_entries if entry.energy_level])
            avg_stress = statistics.mean([entry.stress_level for entry in mood_entries if entry.stress_level])
        else:
            avg_mood = avg_energy = avg_stress = 0
        
        patterns.append({
            "week": week + 1,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "average_mood": round(avg_mood, 1),
            "average_energy": round(avg_energy, 1) if avg_energy else 0,
            "average_stress": round(avg_stress, 1) if avg_stress else 0,
            "entry_count": len(mood_entries)
        })
    
    return {"patterns": patterns}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "mood_service",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)