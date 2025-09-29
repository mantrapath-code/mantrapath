# MantraPath Content Service

## Overview

The **MantraPath Content Service** is a comprehensive content management and delivery system that provides articles, affirmations, and personalized recommendations for mental health and wellness. This service acts as the central content repository for the MantraPath platform, delivering curated wellness content, daily affirmations, and intelligent content recommendations based on user preferences and behavior.

### Key Features

- 📚 **Content Management** - Articles, videos, audio content, and exercises
- 💫 **Affirmations System** - Mood-contextual daily affirmations and positive messages
- 🎯 **Personalized Recommendations** - AI-driven content curation based on user preferences
- 🔖 **Bookmark System** - Save and organize favorite content for later access
- 🔍 **Advanced Search** - Full-text search with filtering and categorization
- 📊 **Analytics Tracking** - View counts, engagement metrics, and popularity scoring
- ⚡ **Redis Caching** - High-performance content delivery with intelligent caching
- 🔄 **Event Integration** - Real-time content recommendation events for analytics

## Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Content Service (Port 8005)               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────────────────────┐   │
│  │   FastAPI App   │  │    Content Management           │   │
│  │                 │  │  ┌─────────────────────────────┐ │   │
│  │  • Auth Layer   │  │  │  Articles & Resources       │ │   │
│  │  • CORS Config  │  │  │  • Wellness Content        │ │   │
│  │  • Rate Limits  │  │  │  • Categories & Tags       │ │   │
│  │  • Endpoints    │  │  │  • Difficulty Levels       │ │   │
│  └─────────────────┘  │  └─────────────────────────────┘ │   │
│                       └─────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Personalization Engine                   │   │
│  │  • User Preference Analysis  • Mood-Based Curation │   │
│  │  • Engagement Tracking      • Category Optimization│   │
│  │  • Recommendation Algorithm • Content Scoring      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Data & Caching Layer                      │   │
│  │  • Redis Cache              • PostgreSQL Database  │   │
│  │  • Content Models           • Affirmation Models   │   │
│  │  • Bookmark System          • Analytics Storage    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
content_service/
├── main.py                 # FastAPI application entry point (724 lines)
├── requirements.txt        # Service dependencies (minimal, optimized)
└── Dockerfile             # Container configuration (Port 8005)
```

**Note**: This is a streamlined, single-file microservice designed for high performance and maintainability. All core functionality is consolidated in `main.py` with clear separation of concerns through well-organized endpoint groups and helper functions.

## API Endpoints

### Content Feed & Discovery

#### GET `/content/feed`
**Personalized Content Feed**
```json
Query Parameters:
- skip: int = 0 (pagination offset)
- limit: int = 20 (max 50, items per page)
- category: Optional[str] (filter by category)
- content_type: Optional[str] (article|video|audio|exercise)
- difficulty: Optional[str] (beginner|intermediate|advanced)

Response: ContentSummary[]
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Understanding Anxiety: A Beginner's Guide",
    "content_type": "article",
    "category": "anxiety",
    "author": "Dr. Sarah Johnson",
    "duration_minutes": null,
    "difficulty_level": "beginner",
    "view_count": 1547,
    "like_count": 89,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

**Personalization Logic:**
- **Authenticated Users**: Content prioritized by bookmarked categories and engagement history
- **Anonymous Users**: Popular content with Redis caching (10-minute TTL)
- **Event Publishing**: Publishes `CONTENT_RECOMMENDATION_CREATED` events for analytics

#### GET `/content/wellness`
**Wellness-Specific Content**
```json
Query Parameters:
- skip: int = 0
- limit: int = 20 (max 50)
- content_type: Optional[str]
- difficulty: Optional[str]

Categories Included:
- wellness, mental-health, mindfulness
- meditation, self-care, stress-relief

Response: ContentSummary[] (same format as feed)
```

### Content Access & Details

#### GET `/content/{content_id}`
**Get Specific Content Item**
```json
Response: ContentResponse
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Understanding Anxiety: A Beginner's Guide", 
  "content": "Anxiety is a natural response to stress, but when it becomes overwhelming...",
  "content_type": "article",
  "category": "anxiety",
  "author": "Dr. Sarah Johnson",
  "source_url": null,
  "duration_minutes": null,
  "difficulty_level": "beginner",
  "tags": ["anxiety", "coping", "mental-health", "beginner"],
  "view_count": 1548,
  "like_count": 89,
  "bookmark_count": 23,
  "is_published": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Features:**
- Automatic view count increment (background task)
- Full content body with formatting
- Complete metadata and engagement metrics

#### GET `/content/search`
**Advanced Content Search**
```json
Query Parameters:
- q: str (min 3 characters, search query)
- category: Optional[str]
- content_type: Optional[str]
- skip: int = 0
- limit: int = 20 (max 50)

Search Scope:
- Title matching (case-insensitive)
- Content body matching (full-text)
- Tag matching (PostgreSQL JSON operators)

Response: ContentSummary[] (ranked by view count)
```

#### GET `/content/category/{category}`
**Content by Category**
```json
Path Parameters:
- category: str (wellness category name)

Query Parameters:
- skip: int = 0
- limit: int = 20 (max 50)

Response: ContentSummary[] (sorted by popularity and recency)
```

### Affirmations System

#### GET `/affirmations`
**Get Curated Affirmations**
```json
Query Parameters:
- category: Optional[str] (confidence|self-compassion|acceptance|resilience|self-love)
- mood_context: Optional[str] (anxious|stressed|sad|overwhelmed|low|critical)
- limit: int = 10 (max 50)

Response: AffirmationResponse[]
[
  {
    "id": "affirmation-uuid",
    "text": "I am capable of handling whatever comes my way today.",
    "category": "confidence",
    "mood_context": ["anxious", "stressed"],
    "view_count": 234,
    "like_count": 45,
    "created_at": "2024-01-10T00:00:00Z"
  }
]
```

#### GET `/affirmations/random`
**Get Random Affirmation**
```json
Query Parameters:
- category: Optional[str]
- mood_context: Optional[str]

Response: AffirmationResponse (single affirmation)
{
  "id": "affirmation-uuid",
  "text": "You are worthy of love, happiness, and all the good things life has to offer.",
  "category": "general",
  "mood_context": [],
  "view_count": 1,
  "like_count": 0,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Features:**
- Automatic view count tracking
- Fallback to default affirmation if none found
- Mood-contextual filtering for therapeutic relevance

### Bookmark Management

#### POST `/bookmark/{content_id}`
**Bookmark Content**
```json
Path Parameters:
- content_id: UUID4

Response:
{
  "message": "Content bookmarked successfully"
}

Error Responses:
- 404: Content not found
- 400: Content already bookmarked
```

#### DELETE `/bookmark/{content_id}`
**Remove Bookmark**
```json
Path Parameters:
- content_id: UUID4

Response:
{
  "message": "Bookmark removed successfully"
}

Error Responses:
- 404: Bookmark not found
```

#### GET `/bookmarks`
**Get User's Bookmarks**
```json
Query Parameters:
- skip: int = 0
- limit: int = 20 (max 50)
- category: Optional[str]

Response: BookmarkResponse[]
[
  {
    "content": {
      "id": "content-uuid",
      "title": "5-Minute Morning Mindfulness Routine",
      "content_type": "exercise",
      "category": "mindfulness",
      "author": "Mindfulness Center",
      "duration_minutes": 5,
      "difficulty_level": "beginner",
      "view_count": 892,
      "like_count": 67,
      "created_at": "2024-01-10T00:00:00Z"
    },
    "bookmarked_at": "2024-01-15T14:30:00Z"
  }
]
```

### Utility Endpoints

#### GET `/health`
**Service Health Check**
```json
Response:
{
  "status": "healthy",
  "service": "content_service",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### POST `/seed-data` 
**Development Data Seeding**
```json
Response:
{
  "message": "Content data seeded successfully"
}
```

**Seeds:**
- Sample wellness articles with full content
- Categorized affirmations with mood contexts
- Realistic view counts and engagement metrics

## Configuration

### Environment Variables

```bash
# Service Configuration
CONTENT_SERVICE_PORT=8005
CONTENT_SERVICE_HOST=0.0.0.0

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost/mantrapath
SQLALCHEMY_DATABASE_URL=postgresql://user:pass@localhost/mantrapath

# Redis Configuration (Required)
REDIS_URL=redis://redis:6379
REDIS_CACHE_TTL=600  # 10 minutes default

# Authentication (from shared auth)
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Event Bus Configuration
USE_EVENT_BUS=true
NATS_SERVER_URL=nats://localhost:4222
EVENT_BUS_ENABLED=true

# Content Configuration
DEFAULT_CONTENT_LIMIT=20
MAX_CONTENT_LIMIT=50
CACHE_ANONYMOUS_FEEDS=true
ENABLE_VIEW_TRACKING=true

# Feature Flags
CONTENT_DEBUG=false
ENABLE_PERSONALIZATION=true
ENABLE_ANALYTICS_EVENTS=true
ENABLE_SEARCH_CACHING=true
```

### Service Dependencies

- **PostgreSQL** - Primary data storage for content and affirmations
- **Redis** - High-performance caching for content feeds and search results
- **Auth Service** (Port 8001) - User authentication and context
- **NATS** - Event streaming for recommendation analytics
- **Shared Models** - Database models for Content, Affirmation, Like, and User entities

## Data Models

### Content Model
```python
class Content(Base):
    __tablename__ = "content"
    
    id: str = Column(String, primary_key=True, default=uuid.uuid4)
    title: str = Column(String, nullable=False)
    content: str = Column(Text, nullable=False)  # Full content body
    excerpt: str = Column(Text)  # Short summary
    author_id: str = Column(String, ForeignKey("users.id"))
    content_type: str = Column(String, default="article")  # article|video|audio|exercise
    category: str = Column(String)  # wellness|anxiety|mindfulness|meditation
    tags: List[str] = Column(JSON)  # Searchable tags array
    is_published: bool = Column(Boolean, default=False)
    featured: bool = Column(Boolean, default=False)
    read_time: int = Column(Integer)  # Estimated read time in minutes
    view_count: int = Column(Integer, default=0)
    like_count: int = Column(Integer, default=0)
    
    created_at: datetime = Column(DateTime, default=utcnow)
    updated_at: datetime = Column(DateTime, onupdate=utcnow)
    published_at: datetime = Column(DateTime)
```

### Affirmation Model  
```python
class Affirmation(Base):
    __tablename__ = "affirmations"
    
    id: str = Column(String, primary_key=True, default=uuid.uuid4)
    text: str = Column(Text, nullable=False)  # Affirmation text
    category: str = Column(String)  # confidence|self-compassion|acceptance
    author: str = Column(String)  # Author attribution
    is_daily: bool = Column(Boolean, default=False)  # Featured daily affirmation
    popularity_score: float = Column(Float, default=0.0)  # Algorithm ranking
    
    created_at: datetime = Column(DateTime, default=utcnow)
```

### Content Service Extensions
The service extends the base models with additional fields for enhanced functionality:

```python
# Service-specific model extensions (handled via Pydantic)
source_url: Optional[str]           # External content URLs
duration_minutes: Optional[int]     # Audio/video duration
difficulty_level: str               # beginner|intermediate|advanced  
bookmark_count: int                 # User bookmark tracking
mood_context: List[str]             # Affirmation mood targeting
```

## Request Flow

```mermaid
sequenceDiagram
    participant User
    participant Content as Content Service
    participant Redis as Redis Cache
    participant DB as PostgreSQL
    participant EventBus as Event Bus

    User->>Content: Request personalized feed
    Content->>Redis: Check cache (if anonymous)
    
    alt Cache Hit
        Redis-->>Content: Cached feed data
    else Cache Miss or Authenticated
        Content->>DB: Query with personalization
        DB-->>Content: Content results
        Content->>Redis: Cache results (if anonymous)
    end
    
    Content->>EventBus: Publish recommendation event
    Content-->>User: Personalized feed response
    
    Note over Content: Background view count tracking
    Note over EventBus: Analytics pipeline integration
```

## Personalization Algorithm

### User Preference Analysis
```python
# Personalization logic for authenticated users
bookmarked_categories = get_user_bookmark_categories(user_id)

if bookmarked_categories:
    # Boost content in preferred categories using SQL CASE
    query = query.order_by(
        func.case(
            [(Content.category.in_(categories), 1)],  # Priority 1
            else_=2                                   # Priority 2
        ),
        desc(Content.view_count),     # Secondary: popularity
        desc(Content.created_at)      # Tertiary: recency
    )
```

### Content Scoring Factors
1. **User Preference Match** - Boost content in bookmarked categories
2. **Popularity Score** - View count and engagement metrics
3. **Recency Factor** - Recently published content gets visibility
4. **Difficulty Appropriateness** - Match user skill level preferences
5. **Category Distribution** - Ensure diverse content representation

### Caching Strategy
- **Anonymous Users**: 10-minute Redis cache for popular feeds
- **Authenticated Users**: No caching to ensure fresh personalization
- **Search Results**: Cached by query parameters for performance
- **Static Content**: Long-term caching for published articles

## Event Integration

### Content Recommendation Events
Published to `V3EventChannels.CONTENT_RECOMMENDATION_CREATED`:

```json
{
  "user_id": "user-uuid",
  "recommended_content_count": 15,
  "categories": ["wellness", "mindfulness", "anxiety"],
  "content_types": ["article", "exercise"],
  "personalization_applied": true,
  "recommendation_context": {
    "category_filter": null,
    "content_type_filter": null,
    "difficulty_filter": "beginner",
    "skip": 0,
    "limit": 20
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Analytics Pipeline Integration
- **Real-time Tracking**: User content consumption patterns
- **Recommendation Effectiveness**: Click-through and engagement rates
- **Content Performance**: View patterns and popularity trends
- **Personalization Success**: User satisfaction and retention metrics

## Content Categories

### Wellness Categories
- **wellness** - General wellness and health content
- **mental-health** - Clinical mental health resources
- **mindfulness** - Mindfulness practices and techniques
- **meditation** - Guided meditations and instruction
- **self-care** - Self-care practices and routines
- **stress-relief** - Stress management and coping strategies
- **anxiety** - Anxiety-specific resources and techniques
- **depression** - Depression support and management
- **sleep** - Sleep hygiene and improvement techniques
- **nutrition** - Mental health nutrition and diet

### Content Types
- **article** - Written articles and guides
- **video** - Video content and tutorials
- **audio** - Audio content, meditations, and podcasts
- **exercise** - Interactive exercises and activities

### Difficulty Levels
- **beginner** - Introductory content for new users
- **intermediate** - Moderate difficulty for developing users
- **advanced** - Complex content for experienced practitioners

## Development & Testing

### Running Locally

```bash
# Install dependencies
cd /home/sachin/mantrapath/backend/services/content_service
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost/mantrapath"
export REDIS_URL="redis://localhost:6379"
export USE_EVENT_BUS="true"

# Run the service
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8005 --reload
```

### Docker Deployment

```bash
# Build image
docker build -t mantrapath/content-service .

# Run container
docker run -d \
  --name content-service \
  -p 8005:8005 \
  -e DATABASE_URL="postgresql://user:pass@db:5432/mantrapath" \
  -e REDIS_URL="redis://redis:6379" \
  -e USE_EVENT_BUS="true" \
  mantrapath/content-service
```

### Testing Strategy

```bash
# Unit Testing Framework (to be implemented)
python -m pytest tests/ -v --cov=. --cov-report=term-missing

# Test Categories
python -m pytest tests/test_content_endpoints.py -v
python -m pytest tests/test_affirmations.py -v
python -m pytest tests/test_personalization.py -v
python -m pytest tests/test_bookmarks.py -v
python -m pytest tests/test_search.py -v
python -m pytest tests/test_caching.py -v
```

### Performance Testing
- **Load Testing**: Concurrent user feed requests
- **Cache Performance**: Redis hit/miss ratios and response times
- **Database Optimization**: Query performance for personalized feeds
- **Search Performance**: Full-text search with filtering
- **Event Publishing**: NATS event delivery confirmation

## Monitoring & Analytics

### Health Monitoring
```json
# Enhanced health check (to be implemented)
{
  "status": "healthy",
  "service": "content_service",
  "timestamp": "2024-01-15T10:30:00Z",
  "components": {
    "database": "connected",
    "redis": "connected", 
    "event_bus": "active"
  },
  "metrics": {
    "cache_hit_ratio": 0.85,
    "avg_response_time_ms": 45,
    "content_items_cached": 1234
  }
}
```

### Performance Metrics
- **Response Times**: Endpoint latency tracking
- **Cache Performance**: Hit ratios and memory usage
- **Database Queries**: Slow query identification
- **Personalization Effectiveness**: Recommendation click-through rates
- **User Engagement**: Content consumption patterns

### Logging Strategy
```python
# Structured logging for analytics
logging.info(f"Published content recommendation event for user {user_id}")
logging.warning(f"Cache miss for anonymous feed: {cache_key}")
logging.error(f"Failed to publish content recommendation event: {e}")
```

## Security & Privacy

### Data Protection
- **Content Access Control**: Published content only for public endpoints
- **User Data Privacy**: Bookmark and preference data protection
- **Search Query Logging**: Anonymized search analytics
- **Personal Recommendations**: User-specific data isolation

### Authentication & Authorization
- **JWT Integration**: Shared authentication system integration
- **Optional Authentication**: Public access to general content
- **User Context**: Authenticated user preference tracking
- **Rate Limiting**: Endpoint throttling for API protection

## Performance Optimization

### Caching Strategy
```python
# Multi-level caching approach
class ContentCache:
    # Level 1: Redis for anonymous content feeds
    anonymous_feed_cache = 600 seconds  # 10 minutes
    
    # Level 2: Query result caching for search
    search_result_cache = 300 seconds   # 5 minutes
    
    # Level 3: Static content caching
    published_content_cache = 3600 seconds  # 1 hour
```

### Database Optimization
- **Indexed Queries**: Optimized for category, content_type, and published status
- **Pagination**: Efficient LIMIT/OFFSET for large datasets
- **JSON Operators**: PostgreSQL JSON search for tags
- **Connection Pooling**: SQLAlchemy connection management

### Background Processing
```python
# Asynchronous view count updates
@app.get("/content/{content_id}")
async def get_content(..., background_tasks: BackgroundTasks):
    # Return content immediately
    content = get_content_from_db()
    
    # Update view count in background
    background_tasks.add_task(increment_view_count, content_id, db)
    
    return content
```

## Future Development Plans

### Phase 1 - Enhanced Personalization (Q2 2024)
- [ ] **Machine Learning Recommendations** - Advanced collaborative filtering
- [ ] **User Behavior Analysis** - Reading time and engagement tracking  
- [ ] **Content Similarity Matching** - Related content suggestions
- [ ] **A/B Testing Framework** - Recommendation algorithm optimization

### Phase 2 - Content Intelligence (Q3 2024)
- [ ] **AI Content Generation** - Automated affirmation creation
- [ ] **Mood-Adaptive Content** - Real-time mood-based recommendations
- [ ] **Content Quality Scoring** - Automated therapeutic value assessment
- [ ] **Multi-language Support** - Internationalization and localization

### Phase 3 - Advanced Features (Q4 2024)
- [ ] **Interactive Content** - Embedded exercises and assessments
- [ ] **Content Creation Workflows** - Professional content management system
- [ ] **Social Content Features** - User-generated content and reviews
- [ ] **Progressive Web App** - Offline content access and synchronization

### Phase 4 - Professional Integration (2025)
- [ ] **Clinical Content Library** - Evidence-based therapeutic resources
- [ ] **Professional Content Tools** - Therapist-created content management
- [ ] **Treatment Plan Integration** - Content alignment with therapy goals
- [ ] **Outcome Tracking** - Content effectiveness measurement

## Incomplete Implementations & TODOs

### Current Limitations
- **Content Creation API**: No endpoints for creating/updating content (admin-only via database)
- **Advanced Search**: No semantic search or content similarity matching
- **User Ratings**: Like system exists but no rating/review system
- **Content Moderation**: No automated content quality or safety checks
- **Mobile Optimization**: No mobile-specific content formatting

### Known TODOs
```python
# From main.py analysis
# TODO: Implement content creation/editing endpoints for admin users
# TODO: Add content rating and review system
# TODO: Implement semantic search with vector embeddings
# TODO: Add content recommendation ML pipeline
# TODO: Create content analytics dashboard for content managers
# TODO: Add content approval workflow for user-generated content
# TODO: Implement content versioning and revision history
# TODO: Add multimedia content support (image galleries, video streaming)
# TODO: Create content scheduling system for timed releases
# TODO: Add content localization and multi-language support
```

### Technical Debt
- **Single File Architecture**: Consider modularization as service grows
- **Error Handling**: Enhanced error responses with detailed error codes
- **Test Coverage**: Comprehensive test suite implementation needed
- **API Documentation**: OpenAPI/Swagger documentation generation
- **Performance Monitoring**: Advanced metrics collection and alerting

### Missing Features
- **Content Versioning**: Track content changes and revision history  
- **Editorial Workflow**: Content approval and publishing pipeline
- **Content Analytics**: Detailed performance metrics and user engagement
- **Social Features**: Content sharing, comments, and community interaction
- **Advanced Filtering**: Multi-dimensional content filtering and sorting

## API Documentation Standards

### Response Format Consistency
All endpoints follow standardized response patterns:

```python
# Success Response Pattern
{
    "data": [...],           # Actual content
    "meta": {               # Optional metadata
        "total": 150,
        "page": 1,
        "per_page": 20
    }
}

# Error Response Pattern
{
    "error": {
        "code": "CONTENT_NOT_FOUND",
        "message": "The requested content item was not found",
        "details": {
            "content_id": "invalid-uuid",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    }
}
```

### Rate Limiting
- **Content Feed**: 60 requests/minute per user
- **Search Endpoints**: 30 requests/minute per user  
- **Bookmark Operations**: 100 requests/minute per user
- **Health Check**: No limits (monitoring priority)

### Pagination Standards
- **Default Limit**: 20 items per page
- **Maximum Limit**: 50 items per page
- **Offset-based**: Using `skip` and `limit` parameters
- **Cursor-based**: Future implementation for large datasets

## Contributing

### Development Guidelines
1. **Single Responsibility**: Each endpoint should have one clear purpose
2. **Performance First**: Consider caching and database optimization for all changes
3. **User Experience**: Prioritize fast response times and relevant content
4. **Security**: Validate all inputs and protect user data
5. **Testing**: Write tests for all new functionality

### Key Areas for Contribution
- **Personalization Algorithms**: Advanced recommendation engine development
- **Content Intelligence**: NLP and ML for content analysis and generation
- **Performance Optimization**: Caching strategies and database optimization
- **Mobile Experience**: Mobile-specific content formatting and delivery
- **Accessibility**: Content accessibility features for users with disabilities

---

**Service Status**: ✅ Active Development  
**Port**: 8005  
**Version**: 1.0.0  
**Last Updated**: January 2024  
**Maintainer**: MantraPath Development Team  
**Content Strategy**: Evidence-Based Mental Health Content Curation