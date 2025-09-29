# MantraPath Community Service

## Overview

The **MantraPath Community Service** is a sophisticated, psychology-aware community platform that provides mental health support through forums, challenges, events, and social interactions. This service implements calming design principles, mood-responsive theming, and evidence-based community features to foster therapeutic interactions and peer support.

### Key Features

- 🧠 **Psychology-Based Design** - Calming colors and therapeutic UI patterns
- 🌈 **Mood-Responsive Theming** - Dynamic color schemes based on user emotional state
- 🤝 **Unified Community Hub** - Forums, challenges, and events in one platform
- 📊 **Engagement Analytics** - Community participation scoring and progress tracking
- 🚨 **Crisis Detection** - Automatic identification of distress signals in content
- 🎯 **Personalized Feed** - AI-curated content based on psychological preferences
- 💬 **Supportive Communication** - Language analysis for therapeutic interactions
- 🏆 **Achievement System** - Challenge leaderboards and progress gamification

## Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Community Service (Port 8006)              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────────────────────┐   │
│  │   FastAPI App   │  │   Psychology Engine             │   │
│  │                 │  │  ┌─────────────────────────────┐ │   │
│  │  • Auth Layer   │  │  │  Mood-Responsive Themes     │ │   │
│  │  • CORS Config  │  │  │  • Calming Color System    │ │   │
│  │  • Endpoints    │  │  │  • Crisis Detection        │ │   │
│  │  • Event Pub    │  │  │  • Language Analysis       │ │   │
│  └─────────────────┘  │  └─────────────────────────────┘ │   │
│                       └─────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Community Components                     │   │
│  │  • Forums & Threads    • Challenges & Progress     │   │
│  │  • Events & Sessions   • Feed & Analytics          │   │
│  │  • Reactions & Likes   • Leaderboards & Stats      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Data Models & Database                   │   │
│  │  • Community Hubs      • Forum Threads            │   │
│  │  • Challenge Progress  • Event Participation      │   │
│  │  • User Analytics      • Psychology Profiles      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
community_service/
├── main.py                          # Primary FastAPI application (2040 lines)
├── enhanced_community_service.py    # Psychology-enhanced service features (477 lines)
├── feed_endpoints.py                # Unified feed system endpoints (295 lines)
├── psychology_models.py             # Psychology-based data models (287 lines)
├── requirements.txt                 # Service dependencies
├── Dockerfile                       # Container configuration (Port 8006)
├── models/                          # Data model definitions
│   ├── __init__.py                 # Model exports
│   ├── community_models.py         # Core community models (309 lines)
│   └── database_models.py          # Database relationship models
├── services/                        # Business logic services
│   └── community_service.py        # Core community service logic
├── utils/                          # Utility functions
│   └── psychology_utils.py         # Psychology-based utility functions (307 lines)
├── config/                         # Configuration files
│   └── psychology_config.py        # Psychology-based configuration (100 lines)
├── database/                       # Database initialization
│   └── init_community_tables.sql   # Community database schema (227 lines)
├── tests/                          # Test suite
│   └── test_event_integration.py   # Event integration tests (276 lines)
├── main_clean.py                   # Alternative clean implementation
└── main_simple.py                  # Simplified service version
```

## API Endpoints

### Core Community Endpoints

#### GET `/health`
**Service Health Check**
```json
Response:
{
  "status": "healthy",
  "service": "community",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### GET `/user/stats`
**User Community Statistics**
```json
Response:
{
  "challenges_joined": 5,
  "events_joined": 12,
  "active_challenges": 3,
  "completed_activities": 28,
  "community_engagement_score": 85
}
```

### Forum Management

#### GET `/forums`
**Get All Community Forums**
```json
Response: [
  {
    "id": "forum-uuid",
    "name": "Mindfulness & Meditation",
    "description": "Share your mindfulness journey and meditation experiences",
    "category": "mindfulness",
    "color_theme": "calm_blue",
    "psychological_focus": ["anxiety_support", "mindfulness"],
    "member_count": 156,
    "created_by": {
      "name": "MindfulModerator",
      "full_name": "Sarah Johnson"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "recent_posts": 8,
    "is_joined": true
  }
]
```

### Event Management

#### GET `/forums/events`
**Get Community Events**
- Returns list of upcoming and past events
- Includes participation status and attendee counts
- Filters by time range and event type

#### POST `/forums/events/{event_id}/join`
**Join Community Event**
```json
Request: {}
Response:
{
  "success": true,
  "message": "Successfully joined event",
  "participant_count": 24
}
```

#### DELETE `/forums/events/{event_id}/leave`
**Leave Community Event**
```json
Response:
{
  "success": true,
  "message": "Successfully left event",
  "participant_count": 23
}
```

#### POST `/forums/events`
**Create New Event**
```json
Request:
{
  "title": "Mindful Morning Session",
  "description": "Start your day with guided meditation",
  "start_time": "2024-02-01T07:00:00Z",
  "end_time": "2024-02-01T08:00:00Z",
  "max_participants": 50,
  "location": "Virtual Meeting Room",
  "is_virtual": true
}
```

### Challenge System

#### GET `/forums/challenges`
**Get Available Challenges**
```json
Response: [
  {
    "id": "challenge-uuid",
    "title": "30-Day Gratitude Practice",
    "description": "Daily gratitude journaling for improved mental wellness",
    "category": "mindfulness",
    "duration_days": 30,
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-31T23:59:59Z",
    "participant_count": 89,
    "comment_count": 156,
    "is_participating": true,
    "created_by": {
      "name": "WellnessCoach",
      "full_name": "Dr. Maria Rodriguez"
    }
  }
]
```

#### POST `/forums/challenges/{challenge_id}/join`
**Join Challenge**
- Auto-enrolls user in challenge
- Creates participant record
- Returns updated participant count

#### POST `/forums/challenges/{challenge_id}/progress`
**Update Challenge Progress**
```json
Request:
{
  "completed": true,
  "notes": "Today I felt grateful for family support",
  "reflection": "This practice is helping me focus on positive aspects",
  "mood_rating": 8,
  "difficulty_rating": 2
}

Response:
{
  "success": true,
  "message": "Progress updated successfully",
  "streak_count": 5
}
```

#### GET `/forums/challenges/{challenge_id}/progress`
**Get User's Challenge Progress**
```json
Response:
{
  "daily_completions": [
    {
      "id": "progress-uuid",
      "date": "2024-01-15",
      "completed": true,
      "notes": "Grateful for sunny weather today",
      "reflection": "Noticed improved mood after practice",
      "mood_rating": 7,
      "difficulty_rating": 3,
      "streak_count": 5,
      "created_at": "2024-01-15T20:30:00Z"
    }
  ],
  "total_days": 15,
  "completed_days": 12
}
```

#### GET `/forums/challenges/{challenge_id}/leaderboard`
**Challenge Leaderboard**
```json
Response: [
  {
    "user_id": "user-uuid",
    "name": "MindfulJenny",
    "username": "MindfulJenny",
    "avatar_url": null,
    "completion_percentage": 96.7,
    "completed_days": 29,
    "current_streak": 15,
    "joined_at": "2024-01-01T00:00:00Z"
  }
]
```

### Comment System

#### GET `/forums/challenges/{challenge_id}/comments`
**Get Challenge Comments**
- Returns threaded comments for challenge
- Includes author information and engagement metrics

#### POST `/forums/challenges/{challenge_id}/comments`
**Add Challenge Comment**
```json
Request:
{
  "content": "This challenge has been life-changing for my anxiety!",
  "parent_id": null
}

Response:
{
  "id": "comment-uuid",
  "content": "This challenge has been life-changing for my anxiety!",
  "author": {
    "id": "user-uuid",
    "name": "HopefulUser",
    "avatar_url": null,
    "badges": []
  },
  "created_at": "2024-01-15T15:30:00Z",
  "like_count": 0,
  "is_liked": false,
  "parent_id": null,
  "replies": []
}
```

### Feed & Analytics

#### GET `/feed`
**Unified Community Feed**
- Personalized content feed with psychological optimization
- Filters by content type (threads, challenges, events)
- Supports time range filtering and sorting

#### GET `/user/community-score`
**Community Engagement Score**
```json
Response:
{
  "score": 85,
  "level": "Active Contributor",
  "breakdown": {
    "challenges_completed": 30,
    "events_attended": 15,
    "helpful_comments": 25,
    "support_provided": 20
  }
}
```

#### GET `/user/activity`
**User Activity History**
```json
Response: [
  {
    "id": "activity-uuid",
    "type": "challenge_progress",
    "title": "Completed daily gratitude practice",
    "description": "30-Day Gratitude Practice - Day 15",
    "timestamp": "2024-01-15T20:30:00Z",
    "metadata": {
      "challenge_id": "challenge-uuid",
      "streak_count": 5
    }
  }
]
```

## Configuration

### Environment Variables

```bash
# Service Configuration
COMMUNITY_SERVICE_PORT=8006
COMMUNITY_SERVICE_HOST=0.0.0.0

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost/mantrapath
SQLALCHEMY_DATABASE_URL=postgresql://user:pass@localhost/mantrapath

# External Service URLs
AUTH_SERVICE_URL=http://auth-service:8001
MOOD_SERVICE_URL=http://mood-service:8003
PROFILE_SERVICE_URL=http://profile-service:8002

# Event Bus Configuration
USE_EVENT_BUS=true
NATS_SERVER_URL=nats://localhost:4222
EVENT_BUS_ENABLED=true

# Psychology Features
ENABLE_MOOD_THEMING=true
ENABLE_CRISIS_DETECTION=true
ENABLE_CALMING_FEATURES=true
PSYCHOLOGY_ANALYSIS_ENABLED=true

# JWT Configuration (from shared auth)
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Feature Flags
COMMUNITY_DEBUG=false
ENABLE_EVENT_PUBLISHING=true
ENABLE_ANALYTICS=true
ENABLE_GAMIFICATION=true
```

### Service Dependencies

- **Auth Service** (Port 8001) - User authentication and authorization
- **Mood Service** (Port 8003) - User mood data for responsive theming
- **Profile Service** (Port 8002) - User profile information and preferences
- **PostgreSQL** - Primary data storage for forums, challenges, and events
- **NATS** - Event streaming for real-time updates
- **Redis** (Optional) - Caching for performance optimization

## Psychology-Based Features

### Calming Color System
The service implements evidence-based color psychology for mental wellness:

```python
WELLNESS_COLORS = {
    "calm_blue": "#4A90E2",      # Trust, stability, peace
    "sage_green": "#87A96B",     # Growth, harmony, balance  
    "soft_purple": "#9B8CE8",    # Creativity, mindfulness
    "warm_beige": "#F5F1E8",     # Comfort, grounding
    "gentle_teal": "#5DADE2",    # Clarity, refreshing
    "lavender": "#BB8FCE",       # Relaxation, tranquility
}

MOOD_COLOR_MAPPING = {
    "anxious": ["calm_blue", "sage_green", "lavender"],
    "depressed": ["warm_beige", "sunset_orange", "gentle_teal"],
    "stressed": ["forest_green", "soft_purple", "calm_blue"],
    "happy": ["gentle_teal", "sage_green", "sunset_orange"]
}
```

### Crisis Detection System
Automatic identification of crisis indicators in user content:

```python
CRISIS_INDICATORS = {
    "high_urgency": ["suicide", "self-harm", "hurt myself", "end it all"],
    "medium_urgency": ["hopeless", "worthless", "no point", "give up"],
    "emotional_distress": ["overwhelmed", "breaking down", "can't cope"]
}
```

### Supportive Language Analysis
Analysis of communication patterns for therapeutic value:

```python
SUPPORTIVE_LANGUAGE = {
    "encouraged": ["I understand", "Thank you for sharing", "You're not alone"],
    "discouraged": ["You should", "Just think positive", "Get over it"]
}
```

### Calming Score Calculation
Content is scored for psychological calmness (0.0 to 1.0):
- **Calming Keywords**: peaceful, breathe, mindful, support, healing
- **Stress Keywords**: anxious, panic, crisis, overwhelming (negative impact)
- **Context Analysis**: Word frequency and emotional valence

## Data Models

### Community Hub
```python
class CommunityHub(Base):
    __tablename__ = 'community_hubs'
    
    id: str = Column(String, primary_key=True)
    name: str = Column(String, nullable=False)
    description: str = Column(Text)
    hub_type: str = Column(String)  # 'support', 'discussion', 'wellness'
    color_theme: str = Column(String, default='calm_blue')
    psychological_focus: List[str] = Column(JSON)  # ['anxiety', 'mindfulness']
    crisis_support_enabled: bool = Column(Boolean, default=False)
    calming_features: Dict = Column(JSON)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
```

### Community Conversation
```python
class CommunityConversation(Base):
    __tablename__ = 'community_conversations'
    
    id: str = Column(String, primary_key=True)
    title: str = Column(String, nullable=False)
    content: str = Column(Text, nullable=False)
    conversation_type: str = Column(String)  # 'discussion', 'support', 'question'
    mood_tags: List[str] = Column(JSON)  # ['anxious', 'hopeful']
    calming_score: float = Column(Float, default=5.0)  # 1-10 scale
    crisis_flagged: bool = Column(Boolean, default=False)
    author_id: str = Column(String, ForeignKey('users.id'))
```

### Challenge Progress
```python
class ChallengeProgress(Base):
    __tablename__ = 'challenge_progress'
    
    id: str = Column(String, primary_key=True)
    challenge_id: str = Column(String, ForeignKey('challenges.id'))
    user_id: str = Column(String, ForeignKey('users.id'))
    date: date = Column(Date, nullable=False)
    completed: bool = Column(Boolean, default=False)
    notes: str = Column(Text)
    reflection: str = Column(Text)
    mood_rating: int = Column(Integer)  # 1-10 scale
    difficulty_rating: int = Column(Integer)  # 1-10 scale
    streak_count: int = Column(Integer, default=0)
```

## Request Flow

```mermaid
sequenceDiagram
    participant User
    participant Community as Community Service
    participant Psychology as Psychology Engine
    participant EventBus as Event Bus
    participant DB as Database

    User->>Community: Submit challenge progress
    Community->>DB: Verify user participation
    Community->>Psychology: Analyze mood & content
    Psychology-->>Community: Calming score & theme
    Community->>DB: Update progress record
    Community->>EventBus: Publish progress event
    Community-->>User: Progress confirmation + streak
    
    Note over Psychology: Crisis detection analysis
    Note over EventBus: Real-time updates to other services
```

## Event Integration

The service publishes events for real-time system integration:

### Challenge Progress Events
```python
# Published to V3EventChannels.CHALLENGE_PROGRESS_UPDATED
{
    "challenge_id": "challenge-uuid",
    "user_id": "user-uuid", 
    "completed": true,
    "streak_count": 5,
    "date": "2024-01-15",
    "mood_rating": 8,
    "difficulty_rating": 3,
    "notes": "Feeling grateful today",
    "reflection": "This practice helps my anxiety"
}
```

### Community Post Events
```python
# Published to V3EventChannels.COMMUNITY_POST_CREATED
{
    "post_id": "post-uuid",
    "forum_id": "forum-uuid",
    "author_id": "user-uuid",
    "content_type": "thread",
    "title": "Sharing My Journey",
    "psychological_tone": "supportive",
    "calming_score": 0.85,
    "crisis_flagged": false
}
```

## Psychology Configuration

### Mood-Responsive Theming
```python
def get_mood_responsive_theme(current_mood: str, stress_level: float) -> Dict:
    """Generate therapeutic color scheme based on user state"""
    
    if stress_level > 0.7:
        # High stress - prioritize most calming colors
        return {
            "primary": WELLNESS_COLORS["calm_blue"],
            "secondary": WELLNESS_COLORS["lavender"], 
            "accent": WELLNESS_COLORS["sage_green"]
        }
    
    mood_colors = MOOD_COLOR_MAPPING.get(current_mood, ["calm_blue", "sage_green"])
    return generate_theme_from_colors(mood_colors)
```

### Content Analysis Pipeline
```python
def analyze_content_wellness(content: str) -> Dict:
    """Comprehensive psychological analysis of user content"""
    
    return {
        "calming_score": calculate_calming_score(content),
        "supportive_language": analyze_supportive_language(content),
        "crisis_indicators": detect_crisis_indicators(content),
        "emotional_tone": extract_emotional_tone(content),
        "therapeutic_value": calculate_therapeutic_value(content)
    }
```

## Development & Testing

### Running Locally

```bash
# Install dependencies
cd /home/sachin/mantrapath/backend/services/community_service
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost/mantrapath"
export USE_EVENT_BUS="true"
export ENABLE_MOOD_THEMING="true"

# Run the service
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8006 --reload
```

### Docker Deployment

```bash
# Build image
docker build -t mantrapath/community-service .

# Run container
docker run -d \
  --name community-service \
  -p 8006:8006 \
  -e DATABASE_URL="postgresql://user:pass@db:5432/mantrapath" \
  -e USE_EVENT_BUS="true" \
  mantrapath/community-service
```

### Testing

```bash
# Run all tests
python -m pytest tests/ -v --cov=. --cov-report=term-missing

# Test specific components
python -m pytest tests/test_event_integration.py -v
python -m pytest tests/test_psychology_features.py -v
python -m pytest tests/test_community_endpoints.py -v
```

### Test Coverage Areas
- **Event Integration**: Challenge progress and community post events
- **Psychology Features**: Mood theming, crisis detection, content analysis
- **API Endpoints**: All community management endpoints
- **Database Models**: Community hub, conversation, and progress models
- **Feed Algorithm**: Personalized content curation
- **Authentication**: JWT token validation and user context

## Monitoring & Health Checks

### Health Check Endpoint
**GET `/health`**
```json
{
  "status": "healthy",
  "service": "community", 
  "timestamp": "2024-01-15T10:30:00Z",
  "database": "connected",
  "event_bus": "active",
  "psychology_engine": "operational"
}
```

### Performance Metrics
- **Response Time Tracking**: API endpoint latency monitoring
- **Database Query Performance**: SQLAlchemy query optimization
- **Event Publishing Success**: NATS event delivery confirmation  
- **Psychology Analysis Speed**: Content analysis processing time
- **User Engagement Metrics**: Challenge completion rates, forum activity
- **Crisis Detection Accuracy**: False positive/negative rates

### Logging & Analytics
```python
# Comprehensive logging for community activities
logger.info(f"User {user_id} joined challenge {challenge_id}")
logger.warning(f"Crisis indicators detected in content: {content_id}")
logger.error(f"Failed to publish event for user {user_id}: {error}")
```

## Security & Privacy

### Data Protection
- **Content Anonymization**: Optional anonymous posting in sensitive forums
- **Crisis Intervention**: Automatic escalation for high-risk content
- **PII Handling**: Secure processing of personal reflections and notes
- **Therapeutic Confidentiality**: Protected sharing in support groups

### Access Control
- **Forum Permissions**: Role-based access to different community spaces
- **Content Moderation**: Automated and manual content review systems
- **Privacy Settings**: User control over visibility and participation
- **Crisis Protocol**: Immediate intervention procedures for safety

## Performance Considerations

### Optimization Strategies
- **Database Indexing**: Optimized queries for user activities and engagement
- **Event Streaming**: Async event publishing for real-time updates
- **Content Caching**: Forum and challenge data caching for performance
- **Psychology Analysis**: Efficient text processing for large volumes

### Scalability Features
- **Horizontal Scaling**: Stateless service design for multiple instances
- **Database Connection Pooling**: Efficient resource management
- **Event Bus Integration**: Distributed processing for real-time features
- **Feed Optimization**: Efficient personalized content algorithms

## Future Development Plans

### Phase 1 - Enhanced Psychology Features (Q2 2024)
- [ ] **Advanced Mood Detection**: Real-time emotional state analysis from text
- [ ] **Personalized Interventions**: Custom therapeutic responses based on user patterns
- [ ] **Group Therapy Sessions**: Professional-led virtual therapy groups
- [ ] **Crisis Prevention**: Predictive modeling for mental health crises

### Phase 2 - Community Intelligence (Q3 2024)
- [ ] **AI-Powered Matching**: Connect users with similar experiences and goals
- [ ] **Therapeutic Content Generation**: AI-assisted supportive responses
- [ ] **Progress Prediction**: Machine learning for challenge success rates
- [ ] **Community Health Metrics**: Population-level mental wellness tracking

### Phase 3 - Professional Integration (Q4 2024)
- [ ] **Licensed Therapist Network**: Direct access to professional support
- [ ] **Treatment Plan Integration**: Challenge alignment with therapeutic goals
- [ ] **Family/Caregiver Support**: Extended support network features
- [ ] **Research Platform**: Anonymous data contribution to mental health research

### Phase 4 - Advanced Features (2025)
- [ ] **VR/AR Support Groups**: Immersive therapeutic community experiences
- [ ] **Biometric Integration**: Wearable device data for context-aware support
- [ ] **Global Wellness Network**: Cross-platform community connections
- [ ] **Therapeutic Games**: Gamified mental health interventions

## Incomplete Implementations & TODOs

### Current Limitations
- **Thread Management**: Forum thread creation and reply system needs completion
- **Advanced Feed Algorithm**: Personalized feed curation requires ML integration  
- **Professional Moderation**: Human moderator tools and workflow
- **Mobile Optimization**: Mobile-specific community features
- **Notification System**: Real-time alerts for community activities

### Known TODOs
```python
# From main.py line 390
# TODO: Implement advanced feed algorithm with psychology weights
# TODO: Add professional moderator dashboard
# TODO: Integrate with external crisis intervention services
# TODO: Implement advanced threading system for forum discussions
# TODO: Add multimedia support for community posts
# TODO: Create analytics dashboard for community administrators
```

### Technical Debt
- **Model Imports**: Some models use conditional imports with fallback classes
- **Error Handling**: Enhanced error handling for external service failures
- **Test Coverage**: Expand test suite for psychology features and edge cases
- **Documentation**: API documentation generation and maintenance
- **Performance**: Query optimization for large community datasets

## API Documentation Standards

### Response Formats
All endpoints follow consistent JSON response patterns:
```python
# Success Response
{
    "success": true,
    "data": {...},
    "metadata": {
        "timestamp": "2024-01-15T10:30:00Z",
        "version": "2.0.0"
    }
}

# Error Response  
{
    "success": false,
    "error": {
        "code": "COMMUNITY_ERROR_001",
        "message": "User not authorized for this community",
        "details": {...}
    }
}
```

### Rate Limiting
- **Standard Endpoints**: 100 requests/minute per user
- **Progress Updates**: 50 requests/minute per user (higher write load)
- **Event Creation**: 10 requests/minute per user (prevent spam)
- **Crisis Detection**: No limits (safety priority)

## Contributing

### Development Guidelines
1. **Psychology-First Design**: All features must consider therapeutic impact
2. **Crisis Safety**: Any feature detecting distress must have intervention protocols
3. **Accessibility**: Comply with WCAG 2.1 AA standards for mental health accessibility
4. **Testing**: Maintain >90% test coverage for community and psychology features
5. **Documentation**: Update README and API docs for all changes

### Key Areas for Contribution
- **Psychology Research**: Evidence-based community intervention techniques
- **Crisis Prevention**: Advanced machine learning for early intervention
- **Therapeutic Gaming**: Gamification elements that support mental wellness
- **Professional Tools**: Features for licensed mental health professionals
- **Accessibility**: Enhanced accessibility for users with various mental health conditions

---

**Service Status**: ✅ Active Development  
**Port**: 8006  
**Version**: 2.0.0  
**Last Updated**: January 2024  
**Maintainer**: MantraPath Development Team  
**Psychology Consultant**: Licensed Clinical Psychology Team