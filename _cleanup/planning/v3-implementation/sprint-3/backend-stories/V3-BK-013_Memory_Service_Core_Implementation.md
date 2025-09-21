# Story V3-BK-013: Memory Service Core Implementation
**Epic**: Memory Service Foundation  
**Priority**: P0 | **Points**: 8 | **Assignee**: Senior Dev 1

## Story Description
Create foundational Memory Service for comprehensive user interaction tracking that will serve as the data foundation for cross-platform mood intelligence and memory-aware chatbot capabilities.

## Current State Analysis
**Available Foundation**:
- ✅ PostgreSQL database (operational)
- ✅ Redis caching (operational) 
- ✅ NATS Event Bus (operational)
- ✅ Existing service patterns (18 operational services)
- ✅ Docker infrastructure (healthy)

**Missing Components**:
- ❌ Memory Service (Port 8017)
- ❌ User interaction tracking system
- ❌ Memory pattern analysis engine
- ❌ Cross-platform data aggregation

## Acceptance Criteria

### AC1: User Interaction Recording & Retrieval API
- [ ] **POST** `/api/v1/memory/interactions` - Record user interactions
- [ ] **GET** `/api/v1/memory/interactions/{user_id}` - Retrieve user interactions
- [ ] **GET** `/api/v1/memory/interactions/{user_id}/timeline` - Get interaction timeline
- [ ] **DELETE** `/api/v1/memory/interactions/{interaction_id}` - Delete specific interaction
- [ ] Support for mood, journal, chat, community, and challenge interactions
- [ ] Cultural context capture and storage
- [ ] Metadata tracking (timestamps, source services, user context)

### AC2: Mood Pattern Analysis & Storage Engine
- [ ] **GET** `/api/v1/memory/patterns/{user_id}` - Get mood patterns
- [ ] **POST** `/api/v1/memory/patterns/{user_id}/analyze` - Trigger pattern analysis
- [ ] **GET** `/api/v1/memory/patterns/{user_id}/trends` - Get mood trends
- [ ] Pattern detection algorithms for mood changes
- [ ] Confidence scoring for pattern reliability
- [ ] Time-based pattern analysis (daily, weekly, monthly)

### AC3: Behavioral Insights Generation System
- [ ] **GET** `/api/v1/memory/insights/{user_id}` - Get behavioral insights
- [ ] **POST** `/api/v1/memory/insights/{user_id}/generate` - Generate insights
- [ ] **GET** `/api/v1/memory/insights/{user_id}/recommendations` - Get recommendations
- [ ] Machine learning-based insight generation
- [ ] Accuracy scoring for insight reliability
- [ ] Actionable recommendations based on patterns

### AC4: Cross-Platform Interaction Aggregation
- [ ] **GET** `/api/v1/memory/aggregation/{user_id}` - Get aggregated data
- [ ] **GET** `/api/v1/memory/aggregation/{user_id}/summary` - Get interaction summary
- [ ] **GET** `/api/v1/memory/aggregation/{user_id}/sources` - Get source breakdown
- [ ] Data aggregation from multiple services
- [ ] Source attribution (mood service, chatbot, community, etc.)
- [ ] Unified view of user's platform engagement

### AC5: PostgreSQL Integration with Optimized Schemas
- [ ] Normalized database schema for user interactions
- [ ] Indexes optimized for common query patterns
- [ ] Foreign key relationships with existing user data
- [ ] Data migration scripts and version control
- [ ] Connection pooling and transaction management

### AC6: Redis Caching for Real-Time Access
- [ ] LRU cache for frequently accessed user interactions
- [ ] Pattern cache for computed mood patterns
- [ ] Insight cache for generated behavioral insights
- [ ] Cache invalidation strategies
- [ ] Performance optimization for sub-100ms response times

### AC7: Event Bus Integration for Real-Time Updates
- [ ] Event publishing for recorded interactions
- [ ] Event publishing for generated patterns and insights
- [ ] Event schema validation
- [ ] Error handling and retry mechanisms

## Detailed Implementation Plan

### Task 1: Service Architecture & Setup (2h)

#### 1.1: Directory Structure Creation
```bash
# Create Memory Service structure
mkdir -p backend/services/memory_service/{src,tests,config}
mkdir -p backend/services/memory_service/src/{api,core,models,integrations,utils}
```

#### 1.2: FastAPI Application Setup
```python
# File: backend/services/memory_service/main.py
from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager
import structlog
from src.core.memory_engine import MemoryEngine
from src.integrations.database import get_database
from src.integrations.cache import get_cache
from src.integrations.event_bus import get_event_bus

logger = structlog.get_logger(__name__)

# Global components
memory_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global memory_engine
    
    logger.info("Starting Memory Service")
    
    try:
        # Initialize core components
        memory_engine = MemoryEngine()
        await memory_engine.initialize()
        
        logger.info("Memory Service started successfully")
        yield
        
    except Exception as e:
        logger.error("Failed to start Memory Service", error=str(e))
        raise
    finally:
        if memory_engine:
            await memory_engine.cleanup()

app = FastAPI(
    title="Memory Service",
    description="Comprehensive user interaction tracking and memory intelligence",
    version="1.0.0",
    lifespan=lifespan
)

# Health check
@app.get("/health")
async def health_check():
    """Service health check"""
    if memory_engine is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    health_status = await memory_engine.get_health_status()
    return health_status

# Include API routes
from src.api import interactions, patterns, insights, aggregation
app.include_router(interactions.router, prefix="/api/v1/memory")
app.include_router(patterns.router, prefix="/api/v1/memory") 
app.include_router(insights.router, prefix="/api/v1/memory")
app.include_router(aggregation.router, prefix="/api/v1/memory")
```

#### 1.3: Docker Configuration
```dockerfile
# File: backend/services/memory_service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8017

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8017"]
```

#### 1.4: Dependencies Configuration
```python
# File: backend/services/memory_service/requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
asyncpg==0.29.0
redis==5.0.1
nats-py==2.6.0
sqlalchemy[asyncio]==2.0.23
alembic==1.12.1
pydantic==2.5.0
structlog==23.2.0
prometheus-client==0.19.0
```

### Task 2: Database Schema Design (2h)

#### 2.1: SQLAlchemy Models
```python
# File: backend/services/memory_service/src/models/interaction.py
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel

Base = declarative_base()

class UserInteraction(Base):
    __tablename__ = "user_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    interaction_type = Column(String(100), nullable=False, index=True)
    interaction_data = Column(JSON, nullable=False)
    cultural_context = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    metadata = Column(JSON)
    source_service = Column(String(100), index=True)

# Pydantic models for API
class InteractionCreate(BaseModel):
    user_id: str
    interaction_type: str
    interaction_data: Dict[str, Any]
    cultural_context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    source_service: str

class InteractionResponse(BaseModel):
    id: int
    user_id: str
    interaction_type: str
    interaction_data: Dict[str, Any]
    cultural_context: Optional[Dict[str, Any]]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]]
    source_service: str
```

```python
# File: backend/services/memory_service/src/models/pattern.py
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel

class MoodPattern(Base):
    __tablename__ = "mood_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    pattern_type = Column(String(100), nullable=False, index=True)
    pattern_data = Column(JSON, nullable=False)
    confidence_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSON)

class PatternResponse(BaseModel):
    id: int
    user_id: str
    pattern_type: str
    pattern_data: Dict[str, Any]
    confidence_score: float
    created_at: datetime
    metadata: Optional[Dict[str, Any]]
```

#### 2.2: Database Migration
```python
# File: backend/services/memory_service/alembic/versions/001_initial_schema.py
"""Initial memory service schema

Revision ID: 001
Revises: 
Create Date: 2025-08-25 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create user_interactions table
    op.create_table(
        'user_interactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('interaction_type', sa.String(length=100), nullable=False),
        sa.Column('interaction_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('cultural_context', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('source_service', sa.String(length=100)),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index('idx_user_interactions_user_id', 'user_interactions', ['user_id'])
    op.create_index('idx_user_interactions_type', 'user_interactions', ['interaction_type'])
    op.create_index('idx_user_interactions_timestamp', 'user_interactions', ['timestamp'])
    op.create_index('idx_user_interactions_source', 'user_interactions', ['source_service'])
    
    # Create mood_patterns table
    op.create_table(
        'mood_patterns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('pattern_type', sa.String(length=100), nullable=False),
        sa.Column('pattern_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('confidence_score', sa.Float()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text())),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('idx_mood_patterns_user_id', 'mood_patterns', ['user_id'])
    op.create_index('idx_mood_patterns_type', 'mood_patterns', ['pattern_type'])

def downgrade() -> None:
    op.drop_table('mood_patterns')
    op.drop_table('user_interactions')
```

### Task 3: Core API Implementation (3h)

#### 3.1: Interactions API
```python
# File: backend/services/memory_service/src/api/interactions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
import structlog

from ..models.interaction import InteractionCreate, InteractionResponse, UserInteraction
from ..integrations.database import get_session
from ..core.memory_engine import get_memory_engine

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.post("/interactions", response_model=InteractionResponse)
async def record_interaction(
    interaction: InteractionCreate,
    session: AsyncSession = Depends(get_session),
    memory_engine = Depends(get_memory_engine)
):
    """Record a new user interaction"""
    try:
        # Create interaction record
        db_interaction = UserInteraction(
            user_id=interaction.user_id,
            interaction_type=interaction.interaction_type,
            interaction_data=interaction.interaction_data,
            cultural_context=interaction.cultural_context,
            metadata=interaction.metadata,
            source_service=interaction.source_service
        )
        
        session.add(db_interaction)
        await session.commit()
        await session.refresh(db_interaction)
        
        # Publish interaction event
        await memory_engine.publish_interaction_event(db_interaction)
        
        logger.info("Interaction recorded", user_id=interaction.user_id, 
                   type=interaction.interaction_type)
        
        return InteractionResponse.from_orm(db_interaction)
        
    except Exception as e:
        logger.error("Failed to record interaction", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to record interaction")

@router.get("/interactions/{user_id}", response_model=List[InteractionResponse])
async def get_user_interactions(
    user_id: str,
    interaction_type: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    session: AsyncSession = Depends(get_session)
):
    """Get user interactions with optional filtering"""
    try:
        query = session.query(UserInteraction).filter(UserInteraction.user_id == user_id)
        
        if interaction_type:
            query = query.filter(UserInteraction.interaction_type == interaction_type)
        
        query = query.order_by(UserInteraction.timestamp.desc())
        query = query.offset(offset).limit(limit)
        
        interactions = await query.all()
        
        return [InteractionResponse.from_orm(interaction) for interaction in interactions]
        
    except Exception as e:
        logger.error("Failed to get interactions", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail="Failed to retrieve interactions")

@router.get("/interactions/{user_id}/timeline", response_model=List[InteractionResponse])
async def get_interaction_timeline(
    user_id: str,
    days: int = Query(30, le=365),
    session: AsyncSession = Depends(get_session)
):
    """Get user interaction timeline for specified days"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = session.query(UserInteraction).filter(
            UserInteraction.user_id == user_id,
            UserInteraction.timestamp >= start_date
        ).order_by(UserInteraction.timestamp.desc())
        
        interactions = await query.all()
        
        return [InteractionResponse.from_orm(interaction) for interaction in interactions]
        
    except Exception as e:
        logger.error("Failed to get timeline", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail="Failed to retrieve timeline")
```

#### 3.2: Patterns API
```python
# File: backend/services/memory_service/src/api/patterns.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import structlog

from ..models.pattern import PatternResponse
from ..integrations.database import get_session
from ..core.pattern_analyzer import get_pattern_analyzer

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.get("/patterns/{user_id}", response_model=List[PatternResponse])
async def get_mood_patterns(
    user_id: str,
    pattern_type: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session)
):
    """Get user mood patterns"""
    try:
        query = session.query(MoodPattern).filter(MoodPattern.user_id == user_id)
        
        if pattern_type:
            query = query.filter(MoodPattern.pattern_type == pattern_type)
        
        patterns = await query.all()
        
        return [PatternResponse.from_orm(pattern) for pattern in patterns]
        
    except Exception as e:
        logger.error("Failed to get patterns", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail="Failed to retrieve patterns")

@router.post("/patterns/{user_id}/analyze")
async def analyze_patterns(
    user_id: str,
    pattern_analyzer = Depends(get_pattern_analyzer),
    session: AsyncSession = Depends(get_session)
):
    """Trigger pattern analysis for user"""
    try:
        # Run pattern analysis
        patterns = await pattern_analyzer.analyze_user_patterns(user_id)
        
        # Store patterns in database
        for pattern_data in patterns:
            db_pattern = MoodPattern(
                user_id=user_id,
                pattern_type=pattern_data["type"],
                pattern_data=pattern_data["data"],
                confidence_score=pattern_data["confidence"]
            )
            session.add(db_pattern)
        
        await session.commit()
        
        logger.info("Pattern analysis completed", user_id=user_id, patterns_count=len(patterns))
        
        return {"status": "analysis_completed", "patterns_generated": len(patterns)}
        
    except Exception as e:
        logger.error("Pattern analysis failed", error=str(e), user_id=user_id)
        raise HTTPException(status_code=500, detail="Pattern analysis failed")
```

### Task 4: Testing & Documentation (1h)

#### 4.1: Unit Tests
```python
# File: backend/services/memory_service/tests/test_interactions_api.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from main import app
from src.models.interaction import InteractionCreate

@pytest.fixture
async def async_session():
    """Create test database session"""
    engine = create_async_engine("sqlite+aiosqlite:///./test.db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session

@pytest.mark.asyncio
async def test_record_interaction(async_session):
    """Test interaction recording"""
    client = TestClient(app)
    
    interaction_data = {
        "user_id": "test_user",
        "interaction_type": "mood",
        "interaction_data": {"mood": "happy", "intensity": 8},
        "source_service": "mood_service"
    }
    
    response = client.post("/api/v1/memory/interactions", json=interaction_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test_user"
    assert data["interaction_type"] == "mood"

@pytest.mark.asyncio
async def test_get_user_interactions(async_session):
    """Test getting user interactions"""
    client = TestClient(app)
    
    response = client.get("/api/v1/memory/interactions/test_user")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
```

#### 4.2: API Documentation
```python
# File: backend/services/memory_service/src/api/docs.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/docs/examples")
async def get_api_examples():
    """API usage examples"""
    return {
        "record_interaction": {
            "url": "POST /api/v1/memory/interactions",
            "example": {
                "user_id": "user123",
                "interaction_type": "mood",
                "interaction_data": {
                    "mood": "happy",
                    "intensity": 8,
                    "context": "completed challenge"
                },
                "cultural_context": {
                    "culture": "individualist",
                    "region": "north_america"
                },
                "source_service": "mood_service"
            }
        },
        "get_patterns": {
            "url": "GET /api/v1/memory/patterns/{user_id}",
            "description": "Get mood patterns for user"
        }
    }
```

## Integration Points

### Service Dependencies
1. **PostgreSQL Database**: User interaction storage and querying
2. **Redis Cache**: Fast access to frequently used data
3. **NATS Event Bus**: Real-time event publishing and subscription
4. **Existing Services**: Integration with all 18 operational services

### API Integration
- **Mood Service**: Subscribe to mood entry events
- **Chatbot Service**: Subscribe to chat message events
- **Community Service**: Subscribe to post and interaction events
- **Journal Service**: Subscribe to journal entry events

### Event Integration
```python
# Events to Subscribe To:
- mood.entry_created
- journal.entry_created  
- chat.message_sent
- community.post_created
- challenge.progress_updated

# Events to Publish:
- memory.interaction_recorded
- memory.pattern_updated
- memory.insight_generated
```

## Performance Requirements
- **API Response Time**: <100ms for simple operations
- **Pattern Analysis**: <500ms for user pattern generation
- **Database Queries**: Optimized with proper indexing
- **Cache Hit Rate**: >80% for frequently accessed data
- **Event Processing**: <50ms event propagation delay

## Monitoring and Observability
- **Health Checks**: Database, Redis, and Event Bus connectivity
- **Metrics**: API response times, database performance, cache hit rates
- **Logging**: Structured logging with user context and correlation IDs
- **Alerts**: Service availability, performance degradation, error rates

## Security Considerations
- **Data Privacy**: User interaction data encryption at rest
- **Access Control**: API authentication and authorization
- **Data Retention**: Configurable data retention policies
- **Audit Logging**: Track data access and modifications

## Risk Mitigation
1. **Database Performance**: Connection pooling, query optimization, caching
2. **Event Processing**: Retry mechanisms, error handling, dead letter queues
3. **Data Consistency**: Transaction management, data validation
4. **Scalability**: Horizontal scaling preparation, load testing

## Definition of Done
- [ ] Memory Service operational on Port 8017
- [ ] All API endpoints implemented and tested
- [ ] Database schema created and migrated
- [ ] Redis caching implemented and tested
- [ ] Event integration working with all services
- [ ] Unit tests achieving >90% coverage
- [ ] Integration tests passing
- [ ] Performance requirements met
- [ ] Documentation complete
- [ ] Health checks and monitoring implemented
