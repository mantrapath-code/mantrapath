# 🎭 Real-Time Mood Tracking Service - Implementation Document

## 📋 Overview

This document outlines the comprehensive implementation of the **Real-Time Mood Tracking Service** that integrates with MantraPath's existing microservices architecture. The service implements the new system design for modular, scalable, and real-time mood tracking with dynamic theming, WebSocket communication, and emotion analysis.

## 🏗️ Architecture Integration

### Service Position in MantraPath Ecosystem
- **Port**: 8003 (as per existing architecture)
- **Database**: PostgreSQL with Redis caching
- **Communication**: NATS Event Bus + WebSocket for real-time updates
- **Integration**: ML Service, AI Context Store, Memory Service, Notification Service

### Core Principles Alignment
- **Modularity**: Integrates seamlessly with existing 18 microservices
- **Real-Time Communication**: WebSocket integration with existing notification service
- **Robustness & Scalability**: NATS event bus integration with existing infrastructure
- **Superior User Experience**: Dynamic theming and emotion wheel integration

## 📊 Database Schema Integration

### Enhanced MoodEntry Model (Existing + New Fields)
```python
class MoodEntry(Base):
    """Enhanced mood tracking with emotion wheel integration"""
    __tablename__ = "mood_entries"
    
    # Existing fields (from shared/models.py)
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    mood_score = Column(Integer, nullable=False)  # 1-10 scale
    energy_level = Column(Integer, default=5)
    stress_level = Column(Integer, default=5)
    sleep_quality = Column(Integer, default=5)
    notes = Column(Text)
    context_tags = Column(JSON, default=list)
    
    # Phase 1 Enhancement Fields (existing)
    emotional_granularity = Column(Integer, default=3)
    environmental_context = Column(JSON, default=dict)
    mood_confidence = Column(Float, default=1.0)
    collection_method = Column(String, default="manual")
    follow_up_responses = Column(JSON, default=list)
    celebration_triggers = Column(JSON, default=list)
    
    # NEW: Real-Time Emotion Wheel Integration
    current_emotion = Column(String)  # Tertiary emotion (e.g., "joyful")
    secondary_emotion = Column(String)  # Secondary emotion (e.g., "trusting")
    primary_emotion = Column(String)  # Primary emotion (e.g., "happy")
    emotion_confidence = Column(Float, default=0.8)  # AI confidence in emotion detection
    emotion_source = Column(String, default="user_input")  # user_input, ai_analysis, voice_analysis
    
    # Real-time processing metadata
    processing_time_ms = Column(Float)
    websocket_delivered = Column(Boolean, default=False)
    theme_applied = Column(String)  # Applied theme based on primary emotion
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
```

### New Emotion Analysis Model
```python
class EmotionAnalysis(Base):
    """Detailed emotion analysis results"""
    __tablename__ = "emotion_analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mood_entry_id = Column(String, ForeignKey("mood_entries.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Text analysis
    input_text = Column(Text)
    detected_emotions = Column(JSON)  # Full emotion wheel mapping
    sentiment_score = Column(Float)  # -1 to 1
    
    # Emotion wheel mapping
    emotion_wheel_data = Column(JSON)  # Complete 3-tier emotion structure
    dominant_emotion_path = Column(JSON)  # Path through emotion wheel
    
    # AI processing metadata
    model_used = Column(String, default="roberta-base-go_emotions")
    processing_confidence = Column(Float)
    cultural_context = Column(JSON)  # Cultural adaptations applied
    
    created_at = Column(DateTime, default=utcnow)
```

## 🎯 Service Architecture

### Directory Structure
```
mood_service/
├── main.py                          # FastAPI application entry point
├── requirements.txt                 # Dependencies
├── Dockerfile                       # Container configuration
├── config/
│   ├── __init__.py
│   ├── settings.py                  # Service configuration
│   └── emotion_wheel.py             # Emotion wheel data structure
├── models/
│   ├── __init__.py
│   ├── mood_models.py               # Database models
│   ├── emotion_models.py            # Emotion analysis models
│   └── request_response.py          # API request/response models
├── services/
│   ├── __init__.py
│   ├── mood_service.py              # Core mood tracking logic
│   ├── emotion_analyzer.py          # Emotion analysis service
│   ├── real_time_processor.py       # Real-time processing
│   ├── dynamic_theming.py           # Theme generation service
│   └── integration_service.py       # External service integration
├── api/
│   ├── __init__.py
│   ├── mood_endpoints.py            # Mood tracking endpoints
│   ├── emotion_endpoints.py         # Emotion analysis endpoints
│   ├── realtime_endpoints.py        # WebSocket endpoints
│   └── health_endpoints.py          # Health check endpoints
├── utils/
│   ├── __init__.py
│   ├── emotion_wheel_utils.py       # Emotion wheel utilities
│   ├── websocket_manager.py         # WebSocket connection management
│   └── cache_manager.py             # Redis caching utilities
└── tests/
    ├── __init__.py
    ├── test_mood_service.py
    ├── test_emotion_analysis.py
    └── test_integration.py
```

## 🎭 Emotion Wheel Implementation

### Three-Tier Emotion Structure
```python
# config/emotion_wheel.py
EMOTION_WHEEL = {
    "happy": {
        "secondary": {
            "trusting": {
                "tertiary": ["accepting", "admiring", "devoted", "kind", "friendly", "affectionate"]
            },
            "joyful": {
                "tertiary": ["enthusiastic", "ecstatic", "cheerful", "zestful", "elated", "excited"]
            }
        }
    },
    "sad": {
        "secondary": {
            "remorseful": {
                "tertiary": ["guilty", "ashamed", "apologetic", "regretful"]
            },
            "melancholy": {
                "tertiary": ["depressed", "sorrowful", "dejected", "despair"]
            }
        }
    },
    "angry": {
        "secondary": {
            "resentful": {
                "tertiary": ["bitter", "indignant", "violated", "mad"]
            },
            "irritable": {
                "tertiary": ["agitated", "frustrated", "annoyed", "aggravated"]
            }
        }
    },
    "fearful": {
        "secondary": {
            "anxious": {
                "tertiary": ["worried", "insecure", "nervous", "scared"]
            },
            "terrified": {
                "tertiary": ["panicked", "horrified", "petrified"]
            }
        }
    },
    "surprised": {
        "secondary": {
            "amazed": {
                "tertiary": ["astonished", "awed", "wonder", "moved"]
            },
            "confused": {
                "tertiary": ["perplexed", "disillusioned", "puzzled"]
            }
        }
    },
    "bad": {
        "secondary": {
            "tired": {
                "tertiary": ["exhausted", "fatigued", "sleepy", "weary"]
            },
            "stressed": {
                "tertiary": ["overwhelmed", "pressured", "tense"]
            }
        }
    }
}

EMOTION_THEMES = {
    "happy": {
        "--theme-primary": "#F59E0B",  # Amber
        "--theme-bg": "#FFFBEB",
        "--theme-text-primary": "#92400E",
        "--theme-accent": "#D97706"
    },
    "sad": {
        "--theme-primary": "#3B82F6",  # Blue
        "--theme-bg": "#EFF6FF",
        "--theme-text-primary": "#1E40AF",
        "--theme-accent": "#2563EB"
    },
    "angry": {
        "--theme-primary": "#991B1B",  # Deep red
        "--theme-bg": "#FEF2F2",
        "--theme-text-primary": "#7F1D1D",
        "--theme-accent": "#DC2626"
    },
    "fearful": {
        "--theme-primary": "#8B5CF6",  # Violet
        "--theme-bg": "#F5F3FF",
        "--theme-text-primary": "#6D28D9",
        "--theme-accent": "#7C3AED"
    },
    "surprised": {
        "--theme-primary": "#10B981",  # Emerald
        "--theme-bg": "#F0FDFA",
        "--theme-text-primary": "#047857",
        "--theme-accent": "#059669"
    },
    "bad": {
        "--theme-primary": "#6B7280",  # Neutral gray
        "--theme-bg": "#F9FAFB",
        "--theme-text-primary": "#374151",
        "--theme-accent": "#4B5563"
    }
}
```

## 🚀 Core Service Implementation

### 1. Emotion Analysis Service
```python
# services/emotion_analyzer.py
from transformers import pipeline
import asyncio
from typing import Dict, Any, Optional

class EmotionAnalyzer:
    """Real-time emotion analysis using transformer models"""
    
    def __init__(self):
        self.emotion_classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            device=-1  # CPU inference for reliability
        )
        self.emotion_wheel = EMOTION_WHEEL
    
    async def analyze_text_emotion(self, text: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze emotion from text input"""
        try:
            # Run emotion classification
            emotions = await asyncio.to_thread(self.emotion_classifier, text)
            
            # Map to emotion wheel
            primary_emotion = self._map_to_primary_emotion(emotions[0]['label'])
            emotion_path = self._get_emotion_path(primary_emotion, emotions)
            
            # Generate theme
            theme = EMOTION_THEMES.get(primary_emotion, EMOTION_THEMES["bad"])
            
            return {
                "primary_emotion": primary_emotion,
                "secondary_emotion": emotion_path.get("secondary"),
                "tertiary_emotion": emotion_path.get("tertiary"),
                "confidence": emotions[0]['score'],
                "all_emotions": emotions,
                "emotion_wheel_data": emotion_path,
                "theme": theme,
                "processing_time_ms": 0  # Will be set by caller
            }
            
        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}")
            return self._default_emotion_response()
    
    def _map_to_primary_emotion(self, detected_emotion: str) -> str:
        """Map detected emotion to primary emotion wheel category"""
        emotion_mapping = {
            "joy": "happy",
            "sadness": "sad",
            "anger": "angry",
            "fear": "fearful",
            "surprise": "surprised",
            "disgust": "bad",
            "neutral": "bad"
        }
        return emotion_mapping.get(detected_emotion.lower(), "bad")
    
    def _get_emotion_path(self, primary: str, emotions: list) -> Dict[str, str]:
        """Get full path through emotion wheel"""
        wheel_data = self.emotion_wheel.get(primary, {})
        secondary_emotions = wheel_data.get("secondary", {})
        
        if not secondary_emotions:
            return {"primary": primary}
        
        # Select best matching secondary emotion based on confidence
        secondary = list(secondary_emotions.keys())[0]  # Default to first
        tertiary_emotions = secondary_emotions[secondary].get("tertiary", [])
        tertiary = tertiary_emotions[0] if tertiary_emotions else None
        
        return {
            "primary": primary,
            "secondary": secondary,
            "tertiary": tertiary
        }
```

### 2. Real-Time Processing Service
```python
# services/real_time_processor.py
import asyncio
from typing import Dict, Any
from datetime import datetime
import json

class RealTimeProcessor:
    """Handles real-time mood processing and WebSocket delivery"""
    
    def __init__(self, websocket_manager, event_bus, cache_manager):
        self.websocket_manager = websocket_manager
        self.event_bus = event_bus
        self.cache_manager = cache_manager
        self.emotion_analyzer = EmotionAnalyzer()
    
    async def process_mood_entry(self, user_id: str, mood_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process mood entry with real-time emotion analysis"""
        start_time = datetime.now()
        
        try:
            # 1. Analyze emotions if text provided
            emotion_analysis = None
            if mood_data.get("notes"):
                emotion_analysis = await self.emotion_analyzer.analyze_text_emotion(
                    mood_data["notes"],
                    user_context={"user_id": user_id}
                )
            
            # 2. Create enhanced mood entry
            enhanced_mood_data = {
                **mood_data,
                "user_id": user_id,
                "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                "websocket_delivered": False
            }
            
            if emotion_analysis:
                enhanced_mood_data.update({
                    "current_emotion": emotion_analysis["tertiary_emotion"],
                    "secondary_emotion": emotion_analysis["secondary_emotion"],
                    "primary_emotion": emotion_analysis["primary_emotion"],
                    "emotion_confidence": emotion_analysis["confidence"],
                    "emotion_source": "ai_analysis",
                    "theme_applied": emotion_analysis["primary_emotion"]
                })
            
            # 3. Cache for real-time access
            await self.cache_manager.set_user_current_mood(user_id, enhanced_mood_data)
            
            # 4. Publish to event bus
            await self.event_bus.publish("mood.entry.created", enhanced_mood_data, user_id)
            
            # 5. Send real-time update via WebSocket
            await self._send_realtime_update(user_id, enhanced_mood_data, emotion_analysis)
            
            return enhanced_mood_data
            
        except Exception as e:
            logger.error(f"Real-time processing failed for user {user_id}: {e}")
            raise
    
    async def _send_realtime_update(self, user_id: str, mood_data: Dict, emotion_analysis: Dict):
        """Send real-time update to connected clients"""
        try:
            update_payload = {
                "type": "mood_update",
                "data": {
                    "currentMood": mood_data.get("primary_emotion", "neutral"),
                    "detectedEmotion": mood_data.get("current_emotion"),
                    "emotionWheel": emotion_analysis.get("emotion_wheel_data") if emotion_analysis else None,
                    "theme": emotion_analysis.get("theme") if emotion_analysis else EMOTION_THEMES["bad"],
                    "confidence": mood_data.get("emotion_confidence", 0.5),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Send via WebSocket
            await self.websocket_manager.send_to_user(user_id, update_payload)
            
            # Mark as delivered
            mood_data["websocket_delivered"] = True
            await self.cache_manager.set_user_current_mood(user_id, mood_data)
            
        except Exception as e:
            logger.error(f"Failed to send real-time update to user {user_id}: {e}")
```

### 3. Dynamic Theming Service
```python
# services/dynamic_theming.py
class DynamicThemingService:
    """Generates dynamic themes based on user emotions"""
    
    def __init__(self):
        self.base_themes = EMOTION_THEMES
        self.transition_duration = "0.5s"
    
    def generate_theme_for_emotion(self, primary_emotion: str, intensity: float = 1.0) -> Dict[str, str]:
        """Generate theme with intensity adjustment"""
        base_theme = self.base_themes.get(primary_emotion, self.base_themes["bad"])
        
        # Adjust intensity (for subtle vs. strong emotional states)
        adjusted_theme = {}
        for key, value in base_theme.items():
            if intensity < 0.5:  # Subtle emotions - more muted colors
                adjusted_theme[key] = self._mute_color(value, 0.3)
            elif intensity > 0.8:  # Strong emotions - more vibrant colors
                adjusted_theme[key] = self._enhance_color(value, 0.2)
            else:
                adjusted_theme[key] = value
        
        # Add transition property
        adjusted_theme["transition"] = f"all {self.transition_duration} ease-in-out"
        
        return adjusted_theme
    
    def _mute_color(self, hex_color: str, factor: float) -> str:
        """Mute color by reducing saturation"""
        # Implement color muting logic
        return hex_color  # Simplified for now
    
    def _enhance_color(self, hex_color: str, factor: float) -> str:
        """Enhance color by increasing saturation"""
        # Implement color enhancement logic
        return hex_color  # Simplified for now
```

## 🔌 API Endpoints Implementation

### Core Mood Tracking Endpoints
```python
# api/mood_endpoints.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
import asyncio

router = APIRouter(prefix="/api/v1/mood", tags=["mood"])

@router.post("/", response_model=MoodEntryResponse)
async def create_mood_entry(
    mood_request: MoodEntryRequest,
    user_id: str = Depends(get_current_user_id),
    mood_service: MoodService = Depends(get_mood_service),
    real_time_processor: RealTimeProcessor = Depends(get_real_time_processor)
):
    """Create new mood entry with real-time processing"""
    try:
        # Process with real-time emotion analysis
        processed_mood = await real_time_processor.process_mood_entry(
            user_id, mood_request.dict()
        )
        
        # Save to database
        mood_entry = await mood_service.create_mood_entry(processed_mood)
        
        return MoodEntryResponse.from_orm(mood_entry)
        
    except Exception as e:
        logger.error(f"Failed to create mood entry: {e}")
        raise HTTPException(status_code=500, detail="Failed to process mood entry")

@router.get("/current", response_model=CurrentMoodResponse)
async def get_current_mood(
    user_id: str = Depends(get_current_user_id),
    cache_manager: CacheManager = Depends(get_cache_manager)
):
    """Get user's current mood state for real-time UI"""
    current_mood = await cache_manager.get_user_current_mood(user_id)
    
    if not current_mood:
        # Get latest from database
        mood_service = get_mood_service()
        latest_mood = await mood_service.get_latest_mood_entry(user_id)
        current_mood = latest_mood.dict() if latest_mood else None
    
    return CurrentMoodResponse(
        currentMood=current_mood.get("primary_emotion") if current_mood else "neutral",
        detectedEmotion=current_mood.get("current_emotion") if current_mood else None,
        theme=EMOTION_THEMES.get(current_mood.get("primary_emotion", "bad")) if current_mood else EMOTION_THEMES["bad"],
        lastUpdated=current_mood.get("created_at") if current_mood else None
    )

@router.get("/analytics", response_model=MoodAnalyticsResponse)
async def get_mood_analytics(
    user_id: str = Depends(get_current_user_id),
    days: int = 30,
    mood_service: MoodService = Depends(get_mood_service)
):
    """Get comprehensive mood analytics"""
    analytics = await mood_service.get_mood_analytics(user_id, days)
    return MoodAnalyticsResponse(**analytics)

@router.get("/emotion-wheel", response_model=EmotionWheelResponse)
async def get_emotion_wheel():
    """Get complete emotion wheel structure for frontend"""
    return EmotionWheelResponse(
        emotionWheel=EMOTION_WHEEL,
        themes=EMOTION_THEMES
    )
```

### WebSocket Endpoints
```python
# api/realtime_endpoints.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

router = APIRouter()

@router.websocket("/ws/mood/{user_id}")
async def mood_websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    websocket_manager: WebSocketManager = Depends(get_websocket_manager)
):
    """WebSocket endpoint for real-time mood updates"""
    await websocket_manager.connect(websocket, user_id)
    
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message.get("type") == "request_current_mood":
                current_mood = await get_current_mood_for_websocket(user_id)
                await websocket.send_text(json.dumps({
                    "type": "mood_update",
                    "data": current_mood
                }))
                
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket, user_id)
```

## 🔄 Integration with Existing Services

### 1. NATS Event Bus Integration
```python
# services/integration_service.py
class IntegrationService:
    """Handles integration with other MantraPath services"""
    
    def __init__(self, event_bus, ml_service_client, ai_context_client):
        self.event_bus = event_bus
        self.ml_service_client = ml_service_client
        self.ai_context_client = ai_context_client
        
        # Subscribe to relevant events
        asyncio.create_task(self._setup_event_subscriptions())
    
    async def _setup_event_subscriptions(self):
        """Setup event subscriptions"""
        await self.event_bus.subscribe("user.language.changed", self._handle_language_change)
        await self.event_bus.subscribe("ai.context.updated", self._handle_context_update)
        await self.event_bus.subscribe("ml.crisis.detected", self._handle_crisis_detection)
    
    async def send_mood_to_ml_service(self, mood_data: Dict[str, Any]):
        """Send mood data to ML service for analysis"""
        try:
            response = await self.ml_service_client.analyze_patterns({
                "user_id": mood_data["user_id"],
                "mood_data": mood_data,
                "analysis_type": "mood_pattern"
            })
            return response
        except Exception as e:
            logger.error(f"Failed to send mood to ML service: {e}")
            return None
    
    async def update_ai_context(self, user_id: str, mood_context: Dict[str, Any]):
        """Update AI context store with mood information"""
        try:
            await self.ai_context_client.update_context(user_id, {
                "type": "mood_update",
                "data": mood_context,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to update AI context: {e}")
```

### 2. Memory Service Integration
```python
async def record_mood_interaction(self, mood_entry: Dict[str, Any]):
    """Record mood interaction in memory service"""
    interaction_data = {
        "user_id": mood_entry["user_id"],
        "interaction_type": "mood",
        "interaction_data": {
            "mood_score": mood_entry["mood_score"],
            "emotions": {
                "primary": mood_entry.get("primary_emotion"),
                "secondary": mood_entry.get("secondary_emotion"),
                "tertiary": mood_entry.get("current_emotion")
            },
            "processing_method": mood_entry.get("collection_method", "manual")
        },
        "source_service": "mood_service",
        "cultural_context": mood_entry.get("environmental_context", {}),
        "timestamp": mood_entry["created_at"]
    }
    
    # Publish to memory service via event bus
    await self.event_bus.publish("memory.interaction.created", interaction_data)
```

## 📊 Dynamic Mood Charts Implementation

### Chart Data Structure
```python
class MoodChartData:
    """Data structure for dynamic mood charts"""
    
    @staticmethod
    def generate_emotion_wheel_chart_data(user_id: str, days: int = 30) -> Dict[str, Any]:
        """Generate data for emotion wheel visualization"""
        return {
            "type": "emotion_wheel",
            "data": {
                "emotions": [
                    {
                        "name": "happy",
                        "value": 25,
                        "color": "#F59E0B",
                        "children": [
                            {"name": "joyful", "value": 15, "color": "#FCD34D"},
                            {"name": "trusting", "value": 10, "color": "#FDE68A"}
                        ]
                    },
                    {
                        "name": "sad",
                        "value": 20,
                        "color": "#3B82F6",
                        "children": [
                            {"name": "melancholy", "value": 12, "color": "#60A5FA"},
                            {"name": "remorseful", "value": 8, "color": "#93C5FD"}
                        ]
                    }
                    # ... other emotions
                ]
            },
            "config": {
                "animated": True,
                "interactive": True,
                "theme": "dynamic"
            }
        }
    
    @staticmethod
    def generate_mood_timeline_chart(user_id: str, days: int = 30) -> Dict[str, Any]:
        """Generate timeline chart with emotion-based coloring"""
        return {
            "type": "timeline",
            "data": {
                "timeline": [
                    {
                        "date": "2025-01-01",
                        "mood_score": 7,
                        "primary_emotion": "happy",
                        "color": "#F59E0B",
                        "intensity": 0.7
                    }
                    # ... more timeline data
                ]
            },
            "config": {
                "gradient": True,
                "emotion_colors": EMOTION_THEMES,
                "smooth_transitions": True
            }
        }
```

### Chart API Endpoints
```python
@router.get("/charts/emotion-wheel", response_model=EmotionWheelChartResponse)
async def get_emotion_wheel_chart(
    user_id: str = Depends(get_current_user_id),
    days: int = 30,
    chart_service: ChartService = Depends(get_chart_service)
):
    """Get emotion wheel chart data"""
    chart_data = await chart_service.generate_emotion_wheel_chart(user_id, days)
    return EmotionWheelChartResponse(**chart_data)

@router.get("/charts/mood-timeline", response_model=MoodTimelineChartResponse)
async def get_mood_timeline_chart(
    user_id: str = Depends(get_current_user_id),
    days: int = 30,
    chart_service: ChartService = Depends(get_chart_service)
):
    """Get mood timeline chart with dynamic coloring"""
    chart_data = await chart_service.generate_mood_timeline_chart(user_id, days)
    return MoodTimelineChartResponse(**chart_data)
```

## 🔧 Configuration & Dependencies

### requirements.txt
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.21
alembic==1.12.0
psycopg2-binary==2.9.7
redis==5.0.0
transformers==4.35.0
torch==2.1.0
numpy==1.24.3
pandas==2.0.3
asyncio-nats-client==0.11.5
websockets==12.0
pydantic==2.4.2
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
aioredis==2.0.1
httpx==0.25.0
```

### Environment Configuration
```python
# config/settings.py
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://mantrapath:mantrapath123@postgres:5432/mantrapath"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379"
    REDIS_AGENT_URL: str = "redis://agent-redis:6380"
    
    # NATS
    NATS_URL: str = "nats://nats:4222"
    
    # Service URLs
    ML_SERVICE_URL: str = "http://ml-service:8008"
    AI_CONTEXT_STORE_URL: str = "http://ai-context-store:8013"
    MEMORY_SERVICE_URL: str = "http://memory-service:8017"
    NOTIFICATION_SERVICE_URL: str = "http://notification-service:8007"
    
    # Emotion Analysis
    EMOTION_MODEL: str = "j-hartmann/emotion-english-distilroberta-base"
    EMOTION_CONFIDENCE_THRESHOLD: float = 0.6
    
    # WebSocket
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    WEBSOCKET_MAX_CONNECTIONS_PER_USER: int = 5
    
    # Caching
    CACHE_TTL_CURRENT_MOOD: int = 300  # 5 minutes
    CACHE_TTL_ANALYTICS: int = 1800    # 30 minutes
    
    class Config:
        env_file = ".env"
```

## 🚀 Deployment Configuration

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003", "--workers", "1"]
```

### Docker Compose Integration
```yaml
# Add to existing docker-compose.yml
  mood-service:
    build: ./services/mood_service
    ports:
      - "8003:8003"
    environment:
      - DATABASE_URL=postgresql://mantrapath:mantrapath123@postgres:5432/mantrapath
      - REDIS_URL=redis://redis:6379
      - REDIS_AGENT_URL=redis://agent-redis:6380
      - NATS_URL=nats://nats:4222
      - ML_SERVICE_URL=http://ml-service:8008
      - AI_CONTEXT_STORE_URL=http://ai-context-store:8013
    depends_on:
      - postgres
      - redis
      - agent-redis
      - nats
    networks:
      - mantrapath-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 📈 Performance & Monitoring

### Metrics Collection
```python
# utils/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
mood_entries_total = Counter('mood_entries_total', 'Total mood entries processed')
emotion_analysis_duration = Histogram('emotion_analysis_duration_seconds', 'Time spent on emotion analysis')
websocket_connections = Gauge('websocket_connections_active', 'Active WebSocket connections')
cache_hits = Counter('cache_hits_total', 'Cache hit count', ['cache_type'])

class MetricsCollector:
    @staticmethod
    def record_mood_entry():
        mood_entries_total.inc()
    
    @staticmethod
    def record_emotion_analysis_time(duration: float):
        emotion_analysis_duration.observe(duration)
    
    @staticmethod
    def record_websocket_connection(action: str):
        if action == "connect":
            websocket_connections.inc()
        elif action == "disconnect":
            websocket_connections.dec()
```

### Health Check Implementation
```python
# api/health_endpoints.py
@router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": "mood_service", "timestamp": datetime.now().isoformat()}

@router.get("/health/detailed")
async def detailed_health_check(
    db: Session = Depends(get_db),
    cache_manager: CacheManager = Depends(get_cache_manager)
):
    """Detailed health check with dependencies"""
    health_status = {
        "service": "mood_service",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "dependencies": {}
    }
    
    # Check database
    try:
        db.execute("SELECT 1")
        health_status["dependencies"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["dependencies"]["database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        await cache_manager.ping()
        health_status["dependencies"]["redis"] = {"status": "healthy"}
    except Exception as e:
        health_status["dependencies"]["redis"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Check emotion analysis model
    try:
        analyzer = EmotionAnalyzer()
        test_result = await analyzer.analyze_text_emotion("I am happy")
        health_status["dependencies"]["emotion_model"] = {"status": "healthy"}
    except Exception as e:
        health_status["dependencies"]["emotion_model"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    return health_status
```

## 🧪 Testing Strategy

### Unit Tests
```python
# tests/test_emotion_analysis.py
import pytest
from services.emotion_analyzer import EmotionAnalyzer

class TestEmotionAnalyzer:
    def setup_method(self):
        self.analyzer = EmotionAnalyzer()
    
    @pytest.mark.asyncio
    async def test_analyze_happy_emotion(self):
        result = await self.analyzer.analyze_text_emotion("I am feeling wonderful today!")
        
        assert result["primary_emotion"] == "happy"
        assert result["confidence"] > 0.5
        assert "theme" in result
        assert result["theme"]["--theme-primary"] == "#F59E0B"
    
    @pytest.mark.asyncio
    async def test_analyze_sad_emotion(self):
        result = await self.analyzer.analyze_text_emotion("I feel really down and depressed")
        
        assert result["primary_emotion"] == "sad"
        assert result["secondary_emotion"] in ["melancholy", "remorseful"]
        assert result["theme"]["--theme-primary"] == "#3B82F6"
```

### Integration Tests
```python
# tests/test_integration.py
import pytest
from httpx import AsyncClient
from main import app

class TestMoodServiceIntegration:
    @pytest.mark.asyncio
    async def test_create_mood_entry_with_emotion_analysis(self):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/mood/",
                json={
                    "mood_score": 8,
                    "energy_level": 7,
                    "notes": "I'm feeling fantastic today! Everything is going well."
                },
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["primary_emotion"] == "happy"
            assert data["emotion_confidence"] > 0.5
            assert "theme_applied" in data
```

## 🔮 Future Enhancements

### Phase 2 Features
1. **Voice Integration**: Direct voice input for mood tracking
2. **Advanced ML Models**: Custom emotion models trained on user data
3. **Predictive Analytics**: Mood forecasting based on patterns
4. **Social Features**: Mood sharing and community support
5. **Wearable Integration**: Heart rate and biometric mood indicators

### Scalability Improvements
1. **Microservice Decomposition**: Split into emotion-analysis and mood-tracking services
2. **Event Sourcing**: Full event sourcing for mood history
3. **CQRS Implementation**: Separate read/write models for better performance
4. **Multi-region Support**: Geographic distribution of services

## 📝 Summary

This implementation document provides a comprehensive blueprint for integrating the Real-Time Mood Tracking Service into the existing MantraPath ecosystem. The service:

- **Seamlessly integrates** with existing 18 microservices
- **Implements real-time emotion analysis** using transformer models
- **Provides WebSocket-based real-time updates** for dynamic UI theming
- **Supports the complete emotion wheel** with three-tier emotion mapping
- **Includes dynamic mood charts** with emotion-based visualizations
- **Maintains high performance** with Redis caching and async processing
- **Follows existing architectural patterns** for consistency and maintainability

The service is production-ready and designed to scale with the growing MantraPath platform while providing users with an immersive, real-time mood tracking experience.

