"""
Content Service - Article management, affirmations, and personalized recommendations
"""

from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
from pydantic import BaseModel, UUID4, Field
import json
import redis
import random
import logging

# Import shared modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.database import get_db
from shared.auth import get_current_user, get_optional_user
from shared.models import Content, Affirmation, Like, User
# Enhanced Event Bus V3 Integration
from shared.events import get_enhanced_event_bus, V3EventChannels
from shared.feature_flags import get_flag_bool

app = FastAPI(
    title="MantraPath Content Service",
    description="Article management, affirmations, and personalized recommendations",
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
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"))

# Pydantic models
class ContentCreate(BaseModel):
    title: str
    content: str
    content_type: str = Field(..., pattern="^(article|video|audio|exercise)$")
    category: str
    author: Optional[str] = None
    source_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    difficulty_level: str = Field("beginner", pattern="^(beginner|intermediate|advanced)$")
    tags: Optional[List[str]] = []

class ContentResponse(BaseModel):
    id: UUID4
    title: str
    content: str
    content_type: str
    category: str
    author: Optional[str]
    source_url: Optional[str]
    duration_minutes: Optional[int]
    difficulty_level: str
    tags: List[str]
    view_count: int
    like_count: int
    bookmark_count: int
    is_published: bool
    created_at: datetime

class ContentSummary(BaseModel):
    id: UUID4
    title: str
    content_type: str
    category: str
    author: Optional[str]
    duration_minutes: Optional[int]
    difficulty_level: str
    view_count: int
    like_count: int
    created_at: datetime

class AffirmationCreate(BaseModel):
    text: str
    category: str
    mood_context: Optional[List[str]] = []

class AffirmationResponse(BaseModel):
    id: UUID4
    text: str
    category: str
    mood_context: List[str]
    view_count: int
    like_count: int
    created_at: datetime

class BookmarkResponse(BaseModel):
    content: ContentSummary
    bookmarked_at: datetime

# Content endpoints
@app.get("/content/feed")
async def get_personalized_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    category: Optional[str] = None,
    content_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get personalized content feed"""
    
    # Check cache for anonymous users
    if not current_user:
        cache_key = f"public_feed:{category}:{content_type}:{difficulty}:{skip}:{limit}"
        cached_feed = redis_client.get(cache_key)
        if cached_feed:
            return json.loads(cached_feed)
    
    query = db.query(Content).filter(Content.is_published == True)
    
    # Apply filters
    if category:
        query = query.filter(Content.category == category)
    if content_type:
        query = query.filter(Content.content_type == content_type)
    if difficulty:
        query = query.filter(Content.difficulty_level == difficulty)
    
    # For authenticated users, personalize based on their preferences
    bookmarked_categories = None
    if current_user:
        # Get user's bookmarked content categories for personalization
        bookmarked_categories = db.query(Content.category).join(Like).filter(
            and_(
                Like.user_id == current_user["user_id"],
                Like.content_type == "content"
            )
        ).distinct().all()
        
        if bookmarked_categories:
            categories = [cat[0] for cat in bookmarked_categories]
            # Boost content in preferred categories
            query = query.order_by(
                func.case(
                    [(Content.category.in_(categories), 1)],
                    else_=2
                ),
                desc(Content.view_count),
                desc(Content.created_at)
            )
        else:
            # Default sorting for new users
            query = query.order_by(desc(Content.view_count), desc(Content.created_at))
    else:
        # Public feed - sort by popularity
        query = query.order_by(desc(Content.view_count), desc(Content.created_at))
    
    content_items = query.offset(skip).limit(limit).all()
    
    result = [
        ContentSummary(
            id=item.id,
            title=item.title,
            content_type=item.content_type,
            category=item.category,
            author=item.author,
            duration_minutes=item.duration_minutes,
            difficulty_level=item.difficulty_level,
            view_count=item.view_count,
            like_count=item.like_count,
            created_at=item.created_at
        )
        for item in content_items
    ]
    
    # Cache public feeds for 10 minutes
    if not current_user:
        redis_client.setex(cache_key, 600, json.dumps([item.dict() for item in result], default=str))
    else:
        # 📤 E4: Publish content recommendation event for real-time pipeline
        if get_flag_bool('USE_EVENT_BUS'):
            try:
                bus = get_enhanced_event_bus()
                await bus.publish(
                    V3EventChannels.CONTENT_RECOMMENDATION_CREATED,
                    {
                        "user_id": current_user["user_id"],
                        "recommended_content_count": len(result),
                        "categories": list(set(item.category for item in result)),
                        "content_types": list(set(item.content_type for item in result)),
                        "personalization_applied": bool(bookmarked_categories),
                        "recommendation_context": {
                            "category_filter": category,
                            "content_type_filter": content_type,
                            "difficulty_filter": difficulty,
                            "skip": skip,
                            "limit": limit
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    user_id=current_user["user_id"]
                )
                logging.info(f"Published content recommendation event for user {current_user['user_id']}")
            except Exception as e:
                logging.error(f"Failed to publish content recommendation event: {e}")
    
    return result

@app.get("/content/wellness")
async def get_wellness_content(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    content_type: Optional[str] = Query(None, pattern="^(article|video|audio|exercise)$"),
    difficulty: Optional[str] = Query(None, pattern="^(beginner|intermediate|advanced)$"),
    db: Session = Depends(get_db)
):
    """Get wellness and mental health related content"""
    
    # Define wellness categories
    wellness_categories = ["wellness", "mental-health", "mindfulness", "meditation", "self-care", "stress-relief"]
    
    query = db.query(Content).filter(
        and_(
            Content.category.in_(wellness_categories),
            Content.is_published == True
        )
    )
    
    if content_type:
        query = query.filter(Content.content_type == content_type)
    
    if difficulty:
        query = query.filter(Content.difficulty_level == difficulty)
    
    content_items = query.order_by(desc(Content.view_count), desc(Content.created_at)).offset(skip).limit(limit).all()
    
    return [
        ContentSummary(
            id=item.id,
            title=item.title,
            content_type=item.content_type,
            category=item.category,
            author=item.author,
            duration_minutes=item.duration_minutes,
            difficulty_level=item.difficulty_level,
            view_count=item.view_count,
            like_count=item.like_count,
            created_at=item.created_at
        )
        for item in content_items
    ]

@app.get("/content/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: UUID4,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get specific content item"""
    
    content = db.query(Content).filter(
        and_(Content.id == content_id, Content.is_published == True)
    ).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Increment view count in background
    background_tasks.add_task(increment_view_count, content_id, db)
    
    return ContentResponse(
        id=content.id,
        title=content.title,
        content=content.content,
        content_type=content.content_type,
        category=content.category,
        author=content.author,
        source_url=content.source_url,
        duration_minutes=content.duration_minutes,
        difficulty_level=content.difficulty_level,
        tags=content.tags or [],
        view_count=content.view_count,
        like_count=content.like_count,
        bookmark_count=content.bookmark_count,
        is_published=content.is_published,
        created_at=content.created_at
    )

@app.get("/content/search")
async def search_content(
    q: str = Query(..., min_length=3),
    category: Optional[str] = None,
    content_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Search content"""
    
    query = db.query(Content).filter(
        and_(
            Content.is_published == True,
            or_(
                Content.title.ilike(f"%{q}%"),
                Content.content.ilike(f"%{q}%"),
                Content.tags.op("?&")(q.split())  # PostgreSQL JSON operator for tag search
            )
        )
    )
    
    if category:
        query = query.filter(Content.category == category)
    if content_type:
        query = query.filter(Content.content_type == content_type)
    
    content_items = query.order_by(
        desc(Content.view_count)
    ).offset(skip).limit(limit).all()
    
    return [
        ContentSummary(
            id=item.id,
            title=item.title,
            content_type=item.content_type,
            category=item.category,
            author=item.author,
            duration_minutes=item.duration_minutes,
            difficulty_level=item.difficulty_level,
            view_count=item.view_count,
            like_count=item.like_count,
            created_at=item.created_at
        )
        for item in content_items
    ]

@app.get("/content/category/{category}")
async def get_content_by_category(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get content by category"""
    
    content_items = db.query(Content).filter(
        and_(
            Content.category == category,
            Content.is_published == True
        )
    ).order_by(desc(Content.view_count), desc(Content.created_at)).offset(skip).limit(limit).all()
    
    return [
        ContentSummary(
            id=item.id,
            title=item.title,
            content_type=item.content_type,
            category=item.category,
            author=item.author,
            duration_minutes=item.duration_minutes,
            difficulty_level=item.difficulty_level,
            view_count=item.view_count,
            like_count=item.like_count,
            created_at=item.created_at
        )
        for item in content_items
    ]

# Affirmations endpoints
@app.get("/affirmations", response_model=List[AffirmationResponse])
async def get_affirmations(
    category: Optional[str] = None,
    mood_context: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get affirmations"""
    
    query = db.query(Affirmation)
    
    if category:
        query = query.filter(Affirmation.category == category)
    
    if mood_context:
        query = query.filter(Affirmation.mood_context.contains([mood_context]))
    
    affirmations = query.order_by(func.random()).limit(limit).all()
    
    return [
        AffirmationResponse(
            id=affirmation.id,
            text=affirmation.text,
            category=affirmation.category,
            mood_context=affirmation.mood_context or [],
            view_count=affirmation.view_count,
            like_count=affirmation.like_count,
            created_at=affirmation.created_at
        )
        for affirmation in affirmations
    ]

@app.get("/affirmations/random", response_model=AffirmationResponse)
async def get_random_affirmation(
    category: Optional[str] = None,
    mood_context: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get a random affirmation"""
    
    query = db.query(Affirmation)
    
    if category:
        query = query.filter(Affirmation.category == category)
    
    if mood_context:
        query = query.filter(Affirmation.mood_context.contains([mood_context]))
    
    affirmation = query.order_by(func.random()).first()
    
    if not affirmation:
        # Return a default affirmation if none found
        return AffirmationResponse(
            id=uuid.uuid4(),
            text="You are worthy of love, happiness, and all the good things life has to offer.",
            category="general",
            mood_context=[],
            view_count=0,
            like_count=0,
            created_at=datetime.utcnow()
        )
    
    # Increment view count
    db.query(Affirmation).filter(Affirmation.id == affirmation.id).update({
        "view_count": Affirmation.view_count + 1
    })
    db.commit()
    
    return AffirmationResponse(
        id=affirmation.id,
        text=affirmation.text,
        category=affirmation.category,
        mood_context=affirmation.mood_context or [],
        view_count=affirmation.view_count + 1,
        like_count=affirmation.like_count,
        created_at=affirmation.created_at
    )

# Bookmark system
@app.post("/bookmark/{content_id}")
async def bookmark_content(
    content_id: UUID4,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Bookmark content"""
    
    # Check if content exists
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Check if already bookmarked
    existing_bookmark = db.query(Like).filter(
        and_(
            Like.user_id == current_user["user_id"],
            Like.content_type == "content",
            Like.content_id == content_id
        )
    ).first()
    
    if existing_bookmark:
        raise HTTPException(status_code=400, detail="Content already bookmarked")
    
    # Create bookmark (using Like model with content_type="content")
    bookmark = Like(
        id=uuid.uuid4(),
        user_id=current_user["user_id"],
        content_type="content",
        content_id=content_id
    )
    
    db.add(bookmark)
    
    # Update bookmark count
    db.query(Content).filter(Content.id == content_id).update({
        "bookmark_count": Content.bookmark_count + 1
    })
    
    db.commit()
    
    return {"message": "Content bookmarked successfully"}

@app.delete("/bookmark/{content_id}")
async def remove_bookmark(
    content_id: UUID4,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Remove bookmark"""
    
    bookmark = db.query(Like).filter(
        and_(
            Like.user_id == current_user["user_id"],
            Like.content_type == "content",
            Like.content_id == content_id
        )
    ).first()
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    db.delete(bookmark)
    
    # Update bookmark count
    db.query(Content).filter(Content.id == content_id).update({
        "bookmark_count": Content.bookmark_count - 1
    })
    
    db.commit()
    
    return {"message": "Bookmark removed successfully"}

@app.get("/bookmarks", response_model=List[BookmarkResponse])
async def get_bookmarks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user's bookmarked content"""
    
    query = db.query(Like, Content).join(Content, Like.content_id == Content.id).filter(
        and_(
            Like.user_id == current_user["user_id"],
            Like.content_type == "content"
        )
    )
    
    if category:
        query = query.filter(Content.category == category)
    
    bookmarks = query.order_by(desc(Like.created_at)).offset(skip).limit(limit).all()
    
    return [
        BookmarkResponse(
            content=ContentSummary(
                id=content.id,
                title=content.title,
                content_type=content.content_type,
                category=content.category,
                author=content.author,
                duration_minutes=content.duration_minutes,
                difficulty_level=content.difficulty_level,
                view_count=content.view_count,
                like_count=content.like_count,
                created_at=content.created_at
            ),
            bookmarked_at=like.created_at
        )
        for like, content in bookmarks
    ]

# Helper functions
async def increment_view_count(content_id: UUID4, db: Session):
    """Background task to increment view count"""
    db.query(Content).filter(Content.id == content_id).update({
        "view_count": Content.view_count + 1
    })
    db.commit()

# Seed data endpoint (for development)
@app.post("/seed-data")
async def seed_content_data(db: Session = Depends(get_db)):
    """Seed initial content data (development only)"""
    
    # Sample articles
    articles = [
        {
            "title": "Understanding Anxiety: A Beginner's Guide",
            "content": """Anxiety is a natural response to stress, but when it becomes overwhelming, it can interfere with daily life. This guide will help you understand what anxiety is, how it affects your body and mind, and practical steps you can take to manage it.

**What is Anxiety?**
Anxiety is your body's natural alarm system. When you perceive a threat, your brain triggers a series of physical and emotional responses designed to keep you safe. However, sometimes this system becomes overactive.

**Common Symptoms:**
- Racing heart
- Sweating
- Difficulty concentrating
- Restlessness
- Worry that's hard to control

**Practical Coping Strategies:**
1. **Deep Breathing**: Try the 4-7-8 technique
2. **Grounding**: Use the 5-4-3-2-1 method
3. **Progressive Muscle Relaxation**
4. **Mindful Observation**

Remember, anxiety is treatable, and you don't have to face it alone.""",
            "content_type": "article",
            "category": "anxiety",
            "author": "Dr. Sarah Johnson",
            "difficulty_level": "beginner",
            "tags": ["anxiety", "coping", "mental-health", "beginner"]
        },
        {
            "title": "5-Minute Morning Mindfulness Routine",
            "content": """Start your day with intention and calm with this simple 5-minute mindfulness practice. Perfect for beginners and busy schedules.

**Your 5-Minute Routine:**

**Minute 1: Settling In**
- Find a comfortable seated position
- Close your eyes or soften your gaze
- Take three deep breaths

**Minutes 2-3: Body Awareness**
- Scan your body from head to toe
- Notice any tension or sensation
- Don't try to change anything, just observe

**Minutes 4-5: Intention Setting**
- Bring to mind one intention for the day
- It could be kindness, patience, or presence
- Feel this intention in your heart

**Closing:**
- Take three more deep breaths
- Open your eyes and carry this calm with you

This simple practice can transform your entire day. Start tomorrow morning!""",
            "content_type": "exercise",
            "category": "mindfulness",
            "author": "Mindfulness Center",
            "duration_minutes": 5,
            "difficulty_level": "beginner",
            "tags": ["mindfulness", "morning", "routine", "meditation"]
        }
    ]
    
    # Sample affirmations
    affirmations = [
        {
            "text": "I am capable of handling whatever comes my way today.",
            "category": "confidence",
            "mood_context": ["anxious", "stressed"]
        },
        {
            "text": "My feelings are valid, and it's okay to take time to process them.",
            "category": "self-compassion",
            "mood_context": ["sad", "overwhelmed"]
        },
        {
            "text": "I choose to focus on what I can control and let go of what I cannot.",
            "category": "acceptance",
            "mood_context": ["worried", "anxious"]
        },
        {
            "text": "I am growing stronger through every challenge I face.",
            "category": "resilience",
            "mood_context": ["difficult", "challenging"]
        },
        {
            "text": "I deserve love, kindness, and compassion, especially from myself.",
            "category": "self-love",
            "mood_context": ["low", "critical"]
        }
    ]
    
    # Add content
    for article_data in articles:
        existing = db.query(Content).filter(Content.title == article_data["title"]).first()
        if not existing:
            content = Content(
                id=uuid.uuid4(),
                title=article_data["title"],
                content=article_data["content"],
                content_type=article_data["content_type"],
                category=article_data["category"],
                author=article_data["author"],
                duration_minutes=article_data.get("duration_minutes"),
                difficulty_level=article_data["difficulty_level"],
                tags=article_data["tags"],
                is_published=True
            )
            db.add(content)
    
    # Add affirmations
    for affirmation_data in affirmations:
        existing = db.query(Affirmation).filter(Affirmation.text == affirmation_data["text"]).first()
        if not existing:
            affirmation = Affirmation(
                id=uuid.uuid4(),
                text=affirmation_data["text"],
                category=affirmation_data["category"],
                mood_context=affirmation_data["mood_context"]
            )
            db.add(affirmation)
    
    db.commit()
    
    return {"message": "Content data seeded successfully"}

# Health check
@app.get("/health")
async def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "service": "content_service",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)