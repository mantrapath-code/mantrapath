# Content Service - Documentation

## Overview
The Content Service manages articles, affirmations, and personalized wellness content recommendations for the MantraPath platform.

## Recent Updates ✅

### New Wellness Content Endpoint
- **Endpoint**: `GET /content/wellness`
- **Purpose**: Dedicated endpoint for mental health and wellness content
- **Status**: ✅ Implemented and tested (August 4, 2025)

## API Endpoints

### Content Endpoints

#### `GET /content/wellness`
Get wellness and mental health related content.

**Query Parameters:**
- `skip` (int, default: 0): Number of items to skip
- `limit` (int, default: 20, max: 50): Maximum items to return
- `content_type` (optional): Filter by content type (article|video|audio|exercise)
- `difficulty` (optional): Filter by difficulty (beginner|intermediate|advanced)

**Response:**
```json
[
  {
    "id": "uuid",
    "title": "Managing Stress in Tech Careers",
    "content_type": "article",
    "category": "stress-relief",
    "author": "Dr. Mental Health",
    "duration_minutes": 5,
    "difficulty_level": "beginner",
    "view_count": 150,
    "like_count": 23,
    "created_at": "2025-08-04T00:00:00"
  }
]
```

**Wellness Categories Supported:**
- `wellness`
- `mental-health`
- `mindfulness`
- `meditation`
- `self-care`
- `stress-relief`

#### `GET /content/feed`
Get personalized content feed for authenticated users.

#### `GET /content/search`
Search content by title and description.

#### `GET /content/category/{category}`
Get content by specific category.

#### `GET /content/{content_id}`
Get detailed content by ID.

### Affirmations Endpoints

#### `GET /affirmations`
Get affirmations with optional filtering.

#### `GET /affirmations/random`
Get a random affirmation.

## Authentication
Most endpoints require JWT authentication via `Authorization: Bearer <token>` header.

## Testing

### Test Wellness Endpoint
```bash
# With authentication
curl -X GET "http://localhost:8000/content/wellness" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# With filters
curl -X GET "http://localhost:8000/content/wellness?content_type=article&difficulty=beginner" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Expected Responses
- **200 OK**: Successfully retrieved content (may be empty array if no content exists)
- **401 Unauthorized**: Missing or invalid JWT token
- **422 Unprocessable Entity**: Invalid query parameters

## Content Management

### Adding Wellness Content
Content can be added through admin endpoints or database seeding scripts.

**Example Content Structure:**
```python
Content(
    title="5-Minute Meditation for Busy Professionals",
    content="Step-by-step meditation guide...",
    content_type="exercise",
    category="mindfulness",
    difficulty_level="beginner",
    duration_minutes=5,
    is_published=True
)
```

## Target User Alignment

### Tech-savvy, Privacy-conscious
- **RESTful API**: Standard HTTP methods and status codes
- **Filtered Access**: Granular content discovery options
- **Secure Authentication**: JWT-based access control

### High Stress, Career Pressure
- **Quick Access**: Optimized endpoints for fast content retrieval
- **Categorized Content**: Stress-relief and mental health focused
- **Duration Filtering**: Time-appropriate content for busy schedules

### Limited Time for Traditional Therapy
- **Instant Content**: No appointment scheduling required
- **Micro-Content**: Short-duration wellness exercises and articles
- **Self-Guided**: Autonomous access to mental health resources

### Open to Digital Health Solutions
- **Modern API**: Contemporary web service architecture
- **Scalable Design**: Microservice-based content delivery
- **Integration Ready**: Compatible with mobile apps and web interfaces

## Service Health
- **Port**: 8005
- **Health Check**: `GET /health`
- **Documentation**: `GET /docs` (Swagger UI)

## Dependencies
- **Database**: PostgreSQL for content storage
- **Cache**: Redis for performance optimization
- **Authentication**: Shared JWT authentication service

## Recent Changes

### August 4, 2025 - Critical Fixes
1. **Route Ordering Fix**: Moved wellness endpoint before `{content_id}` to prevent UUID parsing conflicts
2. **Endpoint Implementation**: Added comprehensive wellness content filtering
3. **Container Updates**: Deployed via Docker rebuild for route changes
4. **Testing Validation**: Confirmed 200 OK responses with proper filtering

### Issues Resolved
- ✅ **422 Validation Errors**: Fixed route conflicts
- ✅ **Missing Endpoints**: Added wellness-specific content access
- ✅ **API Gateway Integration**: Proper routing through `/content/wellness`

## Support
For technical issues or feature requests, refer to the main project documentation or create an issue in the project repository.
