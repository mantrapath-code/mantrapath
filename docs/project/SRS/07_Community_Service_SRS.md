# Software Requirements Specification (SRS)
## Community Service

**Version:** 2.0.0  
**Date:** December 2024  
**Project:** MantraPath - Mental Health and Wellness Platform

---

## 1. Introduction

### 1.1 Purpose
This document specifies the requirements for the Community Service, a comprehensive social platform component that facilitates mental health peer support through forums, challenges, events, and unified community feeds. The service implements psychology-based design principles to create calming, supportive environments that promote user engagement and mental wellness through community connection.

### 1.2 Scope
The Community Service encompasses:
- Psychology-based community forum management with calming color themes
- Mental health challenge system with progress tracking and leaderboards
- Community event management with virtual and in-person support
- Unified activity feed aggregating all community interactions
- User engagement scoring and community analytics
- Real-time event publishing for cross-service integration

### 1.3 Definitions and Acronyms
- **Community Forum**: Themed discussion spaces focused on specific mental health topics
- **Challenge System**: Structured wellness activities with progress tracking and peer support
- **Event Management**: Community-organized virtual and in-person mental health events
- **Engagement Scoring**: Algorithm-based measurement of user community participation
- **Psychology-Based Design**: Color and interaction patterns designed for mental wellness
- **Unified Feed**: Aggregated view of all community activities across forums, challenges, and events

### 1.4 References
- MantraPath Community Psychology Guidelines
- Mental Health Peer Support Best Practices
- Community Engagement and Gamification Standards
- Color Psychology in Mental Health Applications

### 1.5 Document Overview
This SRS details functional requirements, non-functional requirements, system interfaces, and implementation constraints for the Community Service within the MantraPath ecosystem.

---

## 2. Overall Description

### 2.1 Product Perspective
The Community Service operates as the social hub in MantraPath's microservices architecture. It:
- Provides peer support infrastructure for mental health community building
- Integrates with all platform services for comprehensive user context
- Implements psychology-based design for therapeutic community environments
- Publishes real-time events for cross-service community analytics
- Supports frontend applications with rich social interaction capabilities

### 2.2 Product Functions
**Core Functions:**
- **Forum Management**: Psychology-themed discussion spaces with calming color schemes and moderation tools
- **Challenge System**: Structured wellness challenges with progress tracking, leaderboards, and peer encouragement
- **Event Coordination**: Virtual and in-person community events with RSVP management and discussion features
- **Unified Activity Feed**: Personalized community activity aggregation with intelligent filtering
- **Engagement Analytics**: Community participation scoring and user engagement measurement
- **Real-time Integration**: Event-driven updates to AI Context Store and Event Processor

**Psychology-Based Features:**
- **Calming Color System**: 10 psychology-researched colors mapped to emotional states (calm_blue, sage_green, lavender, etc.)
- **Mood-Adaptive Interfaces**: Dynamic color schemes based on user emotional state
- **Supportive Interaction Patterns**: Comment systems designed to encourage positive peer support
- **Achievement Recognition**: Non-competitive progress celebration and milestone acknowledgment
- **Safe Space Design**: Moderation tools and community guidelines enforcement

**Advanced Community Features:**
- **Smart Feed Curation**: AI-powered content relevance and mood-appropriate filtering
- **Peer Matching**: Algorithm-based connection of users with similar challenges and interests
- **Crisis Support Integration**: Automatic escalation of concerning posts to professional support
- **Cultural Sensitivity**: Multi-cultural community norms and communication style adaptation

### 2.3 User Classes and Characteristics
**Primary Users:**
- Community Members: Users seeking peer support and social connection for mental health
- Challenge Participants: Users engaging in structured wellness activities with community support
- Event Organizers: Community leaders creating and managing mental health events
- Forum Moderators: Trusted community members maintaining safe and supportive environments

**User Characteristics:**
- Diverse mental health needs requiring varied levels of community support
- Different comfort levels with social interaction and vulnerability sharing
- Varying cultural backgrounds requiring sensitive community management
- Range of technical proficiency levels needing intuitive community interfaces

### 2.4 Operating Environment
**Deployment Environment:**
- Containerized deployment using Docker
- Kubernetes orchestration for high availability
- Port 8002 for HTTP API access
- PostgreSQL database for community data persistence
- Redis for community activity caching and real-time features

**Dependencies:**
- Python 3.11+ runtime environment
- FastAPI web framework with async support
- SQLAlchemy ORM for complex community data relationships
- Enhanced Event Bus V3 for real-time cross-service integration

### 2.5 Design and Implementation Constraints
**Technical Constraints:**
- Community feed generation time <500ms for 95% of requests
- Support for 1,000+ concurrent community interactions
- Forum thread loading <200ms with full context and replies
- Challenge progress updates with real-time leaderboard synchronization

**Psychological Constraints:**
- All community interfaces must implement calming color psychology
- Content moderation must prioritize mental health safety
- Interaction patterns must encourage positive peer support
- Crisis detection and escalation protocols must be fail-safe

### 2.6 Assumptions and Dependencies
**Assumptions:**
- Users engage with community features voluntarily for peer support
- Community moderation maintains safe and supportive environments
- Psychology-based design principles improve user mental wellness
- Real-time event integration enhances cross-service user context

**Dependencies:**
- PostgreSQL database for complex community data relationships
- AI Event Processor for community activity analysis and insights
- AI Context Store for comprehensive user community behavior tracking
- Authentication Service for secure community participation

---

## 3. System Features

### 3.1 Psychology-Based Forum Management
**Description:** Comprehensive forum system implementing psychology-based design principles for therapeutic community environments.

**Functional Requirements:**
- FR-3.1.1: System shall provide themed forums for specific mental health topics (mindfulness, challenges, general, mental-health)
- FR-3.1.2: System shall implement 10 psychology-researched calming colors with mood-specific mappings
- FR-3.1.3: System shall support dynamic color scheme adaptation based on user emotional state
- FR-3.1.4: System shall provide thread creation, reply management, and nested discussion support
- FR-3.1.5: System shall implement community-driven like/unlike systems for positive reinforcement

**Psychology-Based Color System:**
```yaml
calming_colors:
  calm_blue: "#4A90E2"      # Trust, stability, peace
  sage_green: "#87A96B"     # Growth, harmony, balance
  soft_purple: "#9B8CE8"    # Creativity, mindfulness
  warm_beige: "#F5F1E8"     # Comfort, grounding
  gentle_teal: "#5DADE2"    # Clarity, refreshing
  lavender: "#BB8FCE"       # Relaxation, tranquility

mood_mappings:
  anxious: ["calm_blue", "sage_green", "lavender"]
  depressed: ["warm_beige", "sunset_orange", "gentle_teal"]
  stressed: ["forest_green", "soft_purple", "calm_blue"]
```

**Forum Management Features:**
- **Automatic Forum Creation**: Default mental health-focused forums with psychology-based themes
- **Membership Management**: Join/leave functionality with engagement tracking
- **Thread Discussion**: Full conversation threading with reply support and context preservation
- **Content Moderation**: Community-driven reporting and moderation tools for safety
- **Activity Tracking**: Real-time forum engagement analytics and user participation metrics

### 3.2 Mental Health Challenge System
**Description:** Structured wellness challenge platform with progress tracking, peer support, and community leaderboards.

**Functional Requirements:**
- FR-3.2.1: System shall support challenge creation with customizable duration, categories, and difficulty levels
- FR-3.2.2: System shall provide daily progress tracking with mood ratings and reflection notes
- FR-3.2.3: System shall calculate streak counts and achievement milestones for motivation
- FR-3.2.4: System shall generate non-competitive leaderboards focusing on participation and consistency
- FR-3.2.5: System shall publish real-time progress events for AI-powered insights and intervention

**Challenge Management Pipeline:**
1. **Challenge Creation**: User-generated or system-created wellness challenges with clear goals
2. **Participation Management**: Join/leave functionality with automatic progress tracking setup
3. **Daily Progress Logging**: Completion status, mood ratings, difficulty assessments, and personal reflections
4. **Streak Calculation**: Consecutive day tracking with motivational milestone recognition
5. **Community Support**: Peer commenting, encouragement, and shared experience discussions

**Progress Tracking Features:**
- **Daily Completion Logging**: Boolean completion with optional mood and difficulty ratings
- **Reflection Journaling**: Personal notes and insights for each day's progress
- **Streak Management**: Automatic calculation of consecutive completion streaks
- **Leaderboard Generation**: Non-competitive rankings emphasizing participation over competition
- **Achievement Recognition**: Milestone celebrations and progress acknowledgment

### 3.3 Community Event Management
**Description:** Comprehensive event coordination system supporting virtual and in-person mental health community events.

**Functional Requirements:**
- FR-3.3.1: System shall support event creation with title, description, timing, and capacity management
- FR-3.3.2: System shall provide RSVP functionality with participant limit enforcement
- FR-3.3.3: System shall support both virtual events (with meeting links) and in-person events (with location details)
- FR-3.3.4: System shall enable event discussion through commenting and community interaction
- FR-3.3.5: System shall track event participation for community engagement analytics

**Event Management Features:**
- **Event Creation**: Comprehensive event setup with metadata, timing, and capacity constraints
- **RSVP Management**: Join/leave functionality with participant count tracking and capacity limits
- **Event Types**: Support for workshops, support groups, mindfulness sessions, and community gatherings
- **Discussion Integration**: Event-specific commenting and community conversation facilitation
- **Participation Tracking**: Analytics on event engagement and community building effectiveness

### 3.4 Unified Community Activity Feed
**Description:** Intelligent activity aggregation system providing personalized community content across all platform interactions.

**Functional Requirements:**
- FR-3.4.1: System shall aggregate activities from forums, challenges, and events into unified feeds
- FR-3.4.2: System shall provide intelligent filtering by content type, time range, and relevance
- FR-3.4.3: System shall support multiple sorting algorithms (recent, popular, trending, personalized)
- FR-3.4.4: System shall implement user-specific feed personalization based on interests and engagement history
- FR-3.4.5: System shall provide feed caching and real-time updates for optimal performance

**Feed Aggregation Pipeline:**
1. **Content Collection**: Real-time gathering of forum threads, challenge updates, and event activities
2. **Relevance Scoring**: Algorithm-based ranking considering user interests, engagement history, and community trends
3. **Personalization**: User-specific content curation based on forum memberships, challenge participation, and interaction patterns
4. **Real-time Updates**: Live feed updates as new community activities occur
5. **Performance Optimization**: Intelligent caching and lazy loading for responsive user experience

**Feed Intelligence Features:**
- **Multi-Source Aggregation**: Seamless integration of forum, challenge, and event activities
- **Smart Filtering**: Advanced filtering by content type, time range, and user preferences
- **Personalized Ranking**: AI-powered content relevance scoring based on user behavior
- **Real-time Synchronization**: Live updates and notifications for community engagement
- **Performance Caching**: Redis-based caching for sub-500ms feed generation

### 3.5 Community Engagement Analytics
**Description:** Comprehensive user engagement measurement and community health analytics system.

**Functional Requirements:**
- FR-3.5.1: System shall calculate user community engagement scores based on participation patterns
- FR-3.5.2: System shall track community health metrics including participation rates and interaction quality
- FR-3.5.3: System shall provide user activity history with detailed engagement breakdowns
- FR-3.5.4: System shall generate community insights for platform optimization and user support
- FR-3.5.5: System shall integrate with AI Event Processor for behavioral analysis and intervention recommendations

**Engagement Scoring Algorithm:**
```python
engagement_score = min(100, 
    (challenges_joined * 10) + 
    (events_joined * 5) + 
    (completed_activities * 2) + 
    (forum_posts * 3) + 
    (helpful_comments * 4)
)
```

**Analytics Components:**
- **Participation Metrics**: Challenge completion rates, event attendance, forum engagement
- **Quality Indicators**: Comment helpfulness, positive interaction ratios, community support provision
- **Engagement Trends**: User activity patterns, peak engagement times, content preferences
- **Community Health**: Overall platform engagement, user retention, support network strength
- **Intervention Signals**: Early warning indicators for users needing additional support

---

## 4. External Interface Requirements

### 4.1 User Interfaces
**Community Interfaces:**
- Psychology-based forum interface with calming color schemes
- Challenge progress tracking interface with motivational design
- Event management interface with RSVP and discussion features
- Unified activity feed with personalized content curation

### 4.2 API Interfaces

**Forum Management Endpoints:**
```
GET /forums
- Output: List of available forums with membership status and activity metrics

POST /forums/{forum_id}/join
- Input: Forum ID and user authentication
- Output: Membership confirmation and forum access

POST /forums/thread
- Input: Thread creation data (title, content, forum_id)
- Output: Created thread with forum context and community metadata

GET /forums/{forum_id}/threads
- Output: Forum-specific threads with reply counts and engagement metrics
```

**Challenge System Endpoints:**
```
GET /forums/challenges
- Output: Available challenges with participation counts and progress metrics

POST /forums/challenges/{challenge_id}/join
- Input: Challenge ID and user authentication
- Output: Participation confirmation and progress tracking setup

POST /forums/challenges/{challenge_id}/progress
- Input: Daily progress data (completed, notes, mood_rating, difficulty_rating)
- Output: Updated progress with streak count and achievement status

GET /forums/challenges/{challenge_id}/leaderboard
- Output: Non-competitive leaderboard emphasizing participation and consistency
```

**Event Management Endpoints:**
```
GET /forums/events
- Output: Upcoming community events with participation status

POST /forums/events/{event_id}/join
- Input: Event ID and user authentication
- Output: RSVP confirmation and event access details

POST /forums/events
- Input: Event creation data (title, description, timing, capacity, location)
- Output: Created event with community visibility
```

**Community Analytics Endpoints:**
```
GET /user/stats
- Output: User community engagement statistics and participation metrics

GET /feed
- Input: Filter parameters (types, time_range, sort_by, limit)
- Output: Personalized unified community activity feed

GET /user/community-score
- Output: Detailed engagement scoring with breakdown and improvement suggestions
```

### 4.3 Hardware Interfaces
**Compute Resources:**
- CPU: Multi-core processor for concurrent community interactions and feed generation
- Memory: Minimum 1GB RAM for community data caching and real-time processing
- Storage: SSD storage for community content, user interactions, and analytics data

### 4.4 Software Interfaces

**Database Interfaces:**
- PostgreSQL: Complex community data relationships with proper foreign key constraints
- Community tables: Forums, threads, replies, challenges, events, participation tracking
- Analytics tables: Engagement metrics, user activity history, community health indicators

**Event System Interfaces:**
- Enhanced Event Bus V3: Real-time community activity publishing
- AI Event Processor: Community behavior analysis and intervention recommendations
- AI Context Store: User community engagement context for personalized experiences

**Caching Interfaces:**
- Redis: Community activity caching, feed generation optimization, real-time features
- Performance optimization: Sub-500ms feed generation with intelligent cache invalidation

### 4.5 Communication Protocols
- HTTP/HTTPS for REST API communication
- JSON for data serialization and API responses
- WebSocket for real-time community updates (future enhancement)
- Event-driven messaging for cross-service community analytics

---

## 5. Non-Functional Requirements

### 5.1 Performance
- **Community Feed Generation:** 95% of personalized feeds generated within 500ms
- **Forum Thread Loading:** <200ms for thread display with full reply context
- **Challenge Progress Updates:** Real-time leaderboard synchronization within 100ms
- **Concurrent Users:** Support 1,000+ simultaneous community interactions

### 5.2 Reliability
- **Availability:** 99.9% uptime for community services
- **Data Consistency:** ACID compliance for community interactions and progress tracking
- **Error Recovery:** Graceful handling of database failures with community data preservation
- **Event Delivery:** 100% reliability for community activity event publishing

### 5.3 Psychology and Safety
- **Color Psychology Compliance:** 100% adherence to calming color system across all interfaces
- **Content Moderation:** Automated detection and human review of concerning community content
- **Crisis Intervention:** Immediate escalation protocols for mental health emergencies
- **Safe Space Maintenance:** Community guidelines enforcement with therapeutic focus

### 5.4 Scalability
- **Horizontal Scaling:** Auto-scaling based on community activity load
- **Database Optimization:** Efficient querying for complex community data relationships
- **Feed Generation:** Scalable algorithms for personalized content curation
- **Real-time Processing:** Event-driven architecture supporting high community engagement

### 5.5 Usability
- **Intuitive Navigation:** Psychology-informed interface design for mental wellness
- **Accessibility:** Full compliance with accessibility standards for diverse user needs
- **Mobile Optimization:** Responsive design for community engagement across devices
- **Therapeutic UX:** User experience patterns promoting positive mental health outcomes

---

## 6. Glossary and Appendix

### 6.1 Glossary
- **Challenge Progress Tracking**: Daily completion logging with mood and reflection data
- **Community Engagement Score**: Algorithm-based measurement of user participation quality
- **Psychology-Based Design**: Color and interaction patterns researched for mental wellness
- **Unified Activity Feed**: Aggregated community content from forums, challenges, and events
- **Therapeutic Community Environment**: Safe, supportive digital spaces for mental health peer support

### 6.2 Appendix A: Psychology-Based Color System
```yaml
# Complete Color Psychology Implementation
wellness_colors:
  primary_calm:
    calm_blue: "#4A90E2"      # Trust, stability, peace
    sage_green: "#87A96B"     # Growth, harmony, balance
    soft_purple: "#9B8CE8"    # Creativity, mindfulness
    warm_beige: "#F5F1E8"     # Comfort, grounding
    gentle_teal: "#5DADE2"    # Clarity, refreshing
  
  accent_colors:
    sunset_orange: "#F39C12"  # Warmth, optimism (used sparingly)
    forest_green: "#27AE60"   # Nature, healing
    lavender: "#BB8FCE"       # Relaxation, tranquility
    soft_pink: "#F8BBD9"      # Nurturing, compassion
    warm_yellow: "#F7DC6F"    # Hope, gentle energy

mood_color_mappings:
  anxious: ["calm_blue", "sage_green", "lavender"]
  depressed: ["warm_beige", "sunset_orange", "gentle_teal"]
  stressed: ["forest_green", "soft_purple", "calm_blue"]
  overwhelmed: ["lavender", "warm_beige", "sage_green"]
  lonely: ["soft_pink", "warm_yellow", "gentle_teal"]
  happy: ["gentle_teal", "sage_green", "sunset_orange"]
  peaceful: ["sage_green", "lavender", "calm_blue"]
  hopeful: ["warm_yellow", "forest_green", "gentle_teal"]
  neutral: ["calm_blue", "sage_green", "warm_beige"]
```

### 6.3 Appendix B: Community Database Schema
**Core Community Tables:**
```sql
-- Community Forums
CREATE TABLE community_forums (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Forum Threads
CREATE TABLE forum_threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    forum_id UUID REFERENCES community_forums(id),
    title VARCHAR(500) NOT NULL,
    content TEXT,
    author_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Challenges
CREATE TABLE challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    duration_days INTEGER DEFAULT 30,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Challenge Progress
CREATE TABLE challenge_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    challenge_participant_id UUID REFERENCES challenge_participants(id),
    challenge_id UUID REFERENCES challenges(id),
    user_id UUID REFERENCES users(id),
    date DATE NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    reflection TEXT,
    mood_rating INTEGER CHECK (mood_rating BETWEEN 1 AND 10),
    difficulty_rating INTEGER CHECK (difficulty_rating BETWEEN 1 AND 5),
    streak_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6.4 Appendix C: Engagement Scoring Algorithm
**Community Engagement Calculation:**
```python
def calculate_community_engagement_score(user_activities):
    """
    Calculate user community engagement score based on participation patterns
    
    Scoring Components:
    - Challenge participation: High value for consistent engagement
    - Event attendance: Medium value for community building
    - Forum contributions: Medium value for peer support
    - Helpful interactions: High value for community health
    """
    
    base_scores = {
        'challenges_joined': 10,      # Long-term commitment value
        'events_joined': 5,           # Community building value
        'completed_activities': 2,    # Consistency value
        'forum_posts': 3,            # Peer support value
        'helpful_comments': 4,       # Community health value
        'thread_replies': 2,         # Engagement value
        'likes_given': 1,            # Positive interaction value
    }
    
    # Calculate weighted score with cap at 100
    total_score = 0
    for activity, count in user_activities.items():
        if activity in base_scores:
            total_score += count * base_scores[activity]
    
    # Apply engagement quality multipliers
    consistency_bonus = calculate_consistency_bonus(user_activities)
    helpfulness_bonus = calculate_helpfulness_ratio(user_activities)
    
    final_score = min(100, total_score * consistency_bonus * helpfulness_bonus)
    
    return {
        'total_score': final_score,
        'breakdown': calculate_score_breakdown(user_activities, base_scores),
        'level': determine_engagement_level(final_score),
        'next_level_threshold': get_next_level_threshold(final_score)
    }
```

### 6.5 Appendix D: Event Publishing Schema
**Community Activity Events:**
```yaml
# Community Post Created Event
community_post_created:
  channel: "community.post.created"
  payload:
    id: "thread-uuid"
    forum_id: "forum-uuid"
    title: "Thread title"
    content: "Thread content"
    post_type: "thread" | "reply" | "comment"
    author_id: "user-uuid"
    created_at: "ISO timestamp"

# Challenge Progress Updated Event
challenge_progress_updated:
  channel: "community.challenge.progress"
  payload:
    challenge_id: "challenge-uuid"
    user_id: "user-uuid"
    completed: boolean
    streak_count: integer
    date: "ISO date"
    mood_rating: integer (1-10)
    difficulty_rating: integer (1-5)
    notes: "Progress notes"
    reflection: "User reflection"
```

### 6.6 Appendix E: Safety and Moderation Guidelines
**Community Safety Protocols:**
- **Crisis Detection**: Automated keyword monitoring with immediate escalation
- **Content Moderation**: Community reporting with rapid human review
- **Peer Support Training**: Guidelines for healthy community interaction
- **Professional Escalation**: Clear protocols for connecting users with mental health professionals
- **Privacy Protection**: Strict data handling for sensitive community discussions



