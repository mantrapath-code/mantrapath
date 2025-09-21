"""
MantraPath Mood Service
Real-time mood tracking and emotion analysis service
"""
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from datetime import datetime
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="MantraPath Mood Service",
    description="Real-time mood tracking and emotion analysis",
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

# Models
class MoodEntry(BaseModel):
    mood_level: int
    energy_level: int
    stress_level: int
    sleep_quality: int
    notes: Optional[str] = None
    timestamp: Optional[datetime] = None

class MoodResponse(BaseModel):
    id: str
    mood_level: int
    energy_level: int
    stress_level: int
    sleep_quality: int
    notes: Optional[str]
    timestamp: datetime
    emotion_analysis: Optional[Dict[str, Any]] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mood-service"}

# Mood endpoints
@app.post("/mood", response_model=MoodResponse)
async def create_mood_entry(mood_entry: MoodEntry):
    """Create a new mood entry"""
    # For now, just return a mock response
    # In real implementation, this would save to database
    mood_id = f"mood_{datetime.now().timestamp()}"
    
    return MoodResponse(
        id=mood_id,
        mood_level=mood_entry.mood_level,
        energy_level=mood_entry.energy_level,
        stress_level=mood_entry.stress_level,
        sleep_quality=mood_entry.sleep_quality,
        notes=mood_entry.notes,
        timestamp=mood_entry.timestamp or datetime.now(),
        emotion_analysis={"primary_emotion": "neutral", "confidence": 0.7}
    )

@app.get("/mood/{mood_id}", response_model=MoodResponse)
async def get_mood_entry(mood_id: str):
    """Get a specific mood entry"""
    # Mock response for now
    return MoodResponse(
        id=mood_id,
        mood_level=7,
        energy_level=6,
        stress_level=4,
        sleep_quality=8,
        notes="Feeling good today",
        timestamp=datetime.now(),
        emotion_analysis={"primary_emotion": "happy", "confidence": 0.8}
    )

@app.get("/mood", response_model=List[MoodResponse])
async def get_mood_history(limit: int = 10):
    """Get mood history"""
    # Mock response for now
    return [
        MoodResponse(
            id=f"mood_{i}",
            mood_level=7,
            energy_level=6,
            stress_level=4,
            sleep_quality=8,
            notes=f"Mock entry {i}",
            timestamp=datetime.now(),
            emotion_analysis={"primary_emotion": "neutral", "confidence": 0.7}
        ) for i in range(limit)
    ]

if __name__ == "__main__":
    port = int(os.getenv("MOOD_SERVICE_PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=port)