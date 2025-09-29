# Software Requirements Specification (SRS)
## Content Service

**Version:** 1.0.0  
**Date:** December 2024  
**Project:** MantraPath - Mental Health and Wellness Platform

---

## 1. Introduction

### 1.1 Purpose
This document specifies the requirements for the Content Service, a comprehensive content management and recommendation system that provides personalized mental health resources including articles, affirmations, exercises, and multimedia content. The service implements intelligent content curation, mood-based recommendations, and user engagement tracking to deliver therapeutic value through evidence-based wellness content.

### 1.2 Scope
The Content Service encompasses:
- Comprehensive content management for articles, videos, audio, and interactive exercises
- Intelligent personalized content recommendation system based on user behavior and preferences
- Mood-contextual affirmation system with therapeutic messaging
- Advanced bookmark and favorite system for content curation
- Content analytics and engagement tracking for optimization
- Real-time event publishing for AI-powered content insights

### 1.3 Definitions and Acronyms
- **Content Curation**: AI-powered selection and organization of therapeutic content
- **Mood-Contextual Affirmations**: Positive messaging adapted to user emotional state
- **Personalized Recommendations**: Algorithm-based content suggestions using user behavior analysis
- **Content Analytics**: Comprehensive tracking of content engagement and therapeutic effectiveness
- **Wellness Content**: Evidence-based mental health resources including articles, exercises, and multimedia
- **Therapeutic Value Scoring**: Algorithm measuring content effectiveness for mental wellness

### 1.4 References
- MantraPath Content Psychology Guidelines
- Evidence-Based Mental Health Content Standards
- Personalization and Recommendation System Architecture
- Content Accessibility and Therapeutic Design Principles

### 1.5 Document Overview
This SRS details functional requirements, non-functional requirements, system interfaces, and implementation constraints for the Content Service within the MantraPath ecosystem.

---

## 2. Overall Description

### 2.1 Product Perspective
The Content Service operates as the therapeutic content hub in MantraPath's microservices architecture. It:
- Provides evidence-based mental health resources through multiple content formats
- Implements intelligent personalization for therapeutic content recommendations
- Integrates with AI services for mood-based content curation and user behavior analysis
- Publishes content engagement events for cross-service analytics and insights
- Supports frontend applications with rich content discovery and consumption experiences

### 2.2 Product Functions
**Core Functions:**
- **Content Management**: Multi-format content storage and organization (articles, videos, audio, exercises)
- **Intelligent Recommendations**: AI-powered personalized content feed based on user behavior and preferences
- **Affirmation System**: Mood-contextual positive messaging with therapeutic value
- **Bookmark Management**: Advanced content curation and personal library functionality
- **Search and Discovery**: Full-text search with category, type, and difficulty filtering
- **Engagement Analytics**: Comprehensive content interaction tracking and effectiveness measurement

**Content Types Supported:**
- **Articles**: Long-form mental health education and guidance content
- **Videos**: Therapeutic video content including guided meditations and educational material
- **Audio**: Mindfulness recordings, sleep stories, and therapeutic audio content
- **Exercises**: Interactive wellness activities and therapeutic interventions

**Personalization Features:**
- **Behavioral Learning**: Content recommendation adaptation based on user interaction patterns
- **Mood Integration**: Content curation based on current emotional state from Mood Service
- **Difficulty Progression**: Adaptive content difficulty based on user engagement and progress
- **Category Preferences**: Learning and reinforcement of user content category preferences
- **Engagement Optimization**: Real-time adjustment of recommendations based on content effectiveness

**Advanced Content Features:**
- **Therapeutic Tagging**: Evidence-based content categorization for specific mental health needs
- **Duration-Based Filtering**: Content selection based on available time and attention capacity
- **Cultural Sensitivity**: Content adaptation for diverse cultural backgrounds and sensitivities
- **Accessibility Compliance**: Full accessibility support for users with diverse needs

### 2.3 User Classes and Characteristics
**Primary Users:**
- Content Consumers: Users seeking mental health resources and therapeutic content
- Content Curators: Users creating personal libraries and bookmark collections
- Wellness Seekers: Users looking for specific therapeutic interventions and exercises
- Content Contributors: Mental health professionals and approved content creators

**User Characteristics:**
- Diverse mental health needs requiring varied therapeutic content approaches
- Different learning preferences (visual, auditory, interactive, textual)
- Varying attention spans and cognitive capacity requiring flexible content duration
- Cultural and linguistic diversity requiring sensitive content curation

### 2.4 Operating Environment
**Deployment Environment:**
- Containerized deployment using Docker
- Kubernetes orchestration for high availability
- Port 8005 for HTTP API access
- PostgreSQL database for content metadata and user interaction storage
- Redis for content caching and recommendation optimization

**Dependencies:**
- Python 3.11+ runtime environment
- FastAPI web framework with async support
- SQLAlchemy ORM for content and user data management
- Redis for high-performance content caching and recommendation serving

### 2.5 Design and Implementation Constraints
**Technical Constraints:**
- Content feed generation time <300ms for 95% of personalized requests
- Support for 500+ concurrent content requests with sub-second response times
- Search functionality with <200ms response time for complex queries
- Recommendation accuracy >80% based on user engagement metrics

**Content Constraints:**
- All content must meet evidence-based mental health standards
- Content accessibility compliance with WCAG 2.1 AA standards
- Therapeutic value validation through user engagement and outcome metrics
- Cultural sensitivity review for diverse user base support

### 2.6 Assumptions and Dependencies
**Assumptions:**
- Users engage with content recommendations based on personalized relevance
- Content effectiveness can be measured through engagement and user feedback
- Mood integration enhances therapeutic value of content recommendations
- Caching strategies significantly improve content delivery performance

**Dependencies:**
- PostgreSQL database for content metadata and user interaction storage
- Redis for content caching and recommendation performance optimization
- AI Context Store for user behavior analysis and recommendation enhancement
- Authentication Service for secure content access and personalization

---

## 3. System Features

### 3.1 Intelligent Content Management and Delivery
**Description:** Comprehensive content management system with multi-format support and intelligent delivery optimization.

**Functional Requirements:**
- FR-3.1.1: System shall support four primary content types (article, video, audio, exercise) with extensible architecture
- FR-3.1.2: System shall provide comprehensive content metadata including category, difficulty, duration, and therapeutic tags
- FR-3.1.3: System shall implement content versioning and publication workflow for quality control
- FR-3.1.4: System shall support content view tracking with background processing for performance optimization
- FR-3.1.5: System shall provide content categorization with wellness-focused taxonomy (mindfulness, anxiety, depression, self-care)

**Content Management Pipeline:**
1. **Content Ingestion**: Multi-format content upload with metadata extraction and validation
2. **Quality Assurance**: Therapeutic value assessment and evidence-based content validation
3. **Categorization**: Automatic and manual content categorization with therapeutic taxonomy
4. **Publication**: Content approval workflow with version control and rollback capabilities
5. **Optimization**: Performance optimization through caching and delivery network integration

**Content Metadata Schema:**
```yaml
content_structure:
  core_fields:
    - id: UUID4
    - title: string (required)
    - content: text (required)
    - content_type: enum [article, video, audio, exercise]
    - category: string (wellness taxonomy)
    - difficulty_level: enum [beginner, intermediate, advanced]
  
  extended_metadata:
    - author: string (optional)
    - source_url: string (optional)
    - duration_minutes: integer (optional)
    - tags: array[string] (therapeutic tags)
    - therapeutic_focus: array[string] (specific mental health areas)
  
  analytics_fields:
    - view_count: integer (engagement tracking)
    - like_count: integer (user preference)
    - bookmark_count: integer (curation tracking)
    - effectiveness_score: float (therapeutic value)
```

### 3.2 Personalized Content Recommendation System
**Description:** Advanced AI-powered recommendation engine providing personalized content based on user behavior, preferences, and emotional state.

**Functional Requirements:**
- FR-3.2.1: System shall generate personalized content feeds based on user interaction history and preferences
- FR-3.2.2: System shall integrate with user mood data for emotionally-appropriate content recommendations
- FR-3.2.3: System shall implement collaborative filtering for discovering content based on similar user preferences
- FR-3.2.4: System shall provide real-time recommendation adaptation based on current session behavior
- FR-3.2.5: System shall publish content recommendation events for AI-powered analytics and optimization

**Recommendation Algorithm Pipeline:**
1. **User Profiling**: Analysis of content interaction patterns, bookmark categories, and engagement duration
2. **Mood Integration**: Real-time emotional state consideration from Mood Service for contextually appropriate content
3. **Collaborative Filtering**: Identification of users with similar preferences for content discovery
4. **Content Scoring**: Multi-factor scoring including relevance, therapeutic value, and engagement prediction
5. **Personalized Ranking**: Dynamic content ordering based on individual user preferences and current context

**Personalization Features:**
- **Behavioral Learning**: Continuous adaptation based on user content consumption patterns
- **Category Preference Tracking**: Learning and reinforcement of preferred content categories
- **Engagement-Based Optimization**: Real-time adjustment of recommendations based on user interaction quality
- **Mood-Contextual Filtering**: Content selection appropriate for current emotional state
- **Therapeutic Progression**: Difficulty and complexity adaptation based on user growth and engagement

**Recommendation Performance Metrics:**
- **Click-Through Rate**: Percentage of recommended content accessed by users
- **Engagement Duration**: Average time spent with recommended content
- **Bookmark Rate**: Percentage of recommendations saved for future reference
- **Therapeutic Effectiveness**: User-reported improvement correlation with recommended content
- **Diversity Score**: Balance of content types and categories in recommendations

### 3.3 Mood-Contextual Affirmation System
**Description:** Therapeutic affirmation delivery system providing personalized positive messaging based on user emotional state and psychological needs.

**Functional Requirements:**
- FR-3.3.1: System shall provide categorized affirmations for specific mental health contexts (confidence, self-compassion, acceptance, resilience)
- FR-3.3.2: System shall support mood-contextual affirmation selection based on emotional state indicators
- FR-3.3.3: System shall implement random affirmation delivery to prevent habituation and maintain therapeutic impact
- FR-3.3.4: System shall track affirmation engagement and effectiveness for optimization
- FR-3.3.5: System shall provide fallback affirmations when specific mood-context matches are unavailable

**Affirmation Categories and Therapeutic Focus:**
```yaml
affirmation_categories:
  confidence:
    focus: ["self-efficacy", "capability", "strength"]
    mood_contexts: ["anxious", "insecure", "doubtful"]
    sample: "I am capable of handling whatever comes my way today."
  
  self_compassion:
    focus: ["self-kindness", "acceptance", "emotional validation"]
    mood_contexts: ["sad", "self-critical", "overwhelmed"]
    sample: "My feelings are valid, and it's okay to take time to process them."
  
  acceptance:
    focus: ["letting go", "present moment", "control"]
    mood_contexts: ["worried", "anxious", "frustrated"]
    sample: "I choose to focus on what I can control and let go of what I cannot."
  
  resilience:
    focus: ["growth", "strength", "perseverance"]
    mood_contexts: ["difficult", "challenging", "discouraged"]
    sample: "I am growing stronger through every challenge I face."
  
  self_love:
    focus: ["worth", "compassion", "acceptance"]
    mood_contexts: ["low", "critical", "lonely"]
    sample: "I deserve love, kindness, and compassion, especially from myself."
```

**Affirmation Delivery System:**
- **Contextual Selection**: Algorithm-based selection of affirmations matching current user emotional state
- **Randomization**: Intelligent randomization to prevent habituation while maintaining therapeutic relevance
- **Engagement Tracking**: View count and user interaction measurement for effectiveness assessment
- **Fallback Mechanisms**: Default affirmations ensuring users always receive supportive messaging
- **Therapeutic Validation**: Evidence-based affirmation content with psychological research backing

### 3.4 Advanced Content Search and Discovery
**Description:** Comprehensive content search system with intelligent filtering, full-text search, and discovery optimization.

**Functional Requirements:**
- FR-3.4.1: System shall provide full-text search across content titles, descriptions, and body text
- FR-3.4.2: System shall support advanced filtering by category, content type, difficulty level, and duration
- FR-3.4.3: System shall implement tag-based search for specific therapeutic focus areas
- FR-3.4.4: System shall provide search result ranking based on relevance, popularity, and therapeutic value
- FR-3.4.5: System shall support wellness-specific content discovery with curated category browsing

**Search Capabilities:**
- **Full-Text Search**: PostgreSQL-powered text search with relevance ranking and stemming
- **Multi-Filter Support**: Simultaneous filtering across multiple content dimensions
- **Tag Intelligence**: Therapeutic tag search for specific mental health focus areas
- **Popularity Integration**: Search result boosting based on community engagement and effectiveness
- **Wellness Categories**: Curated browsing for specific mental health topics and interventions

**Discovery Optimization:**
- **Relevance Scoring**: Multi-factor ranking including text relevance, user preferences, and content quality
- **Therapeutic Value Weighting**: Search result boosting for evidence-based, high-effectiveness content
- **User Context Integration**: Search personalization based on user history and current emotional state
- **Performance Optimization**: Query optimization and result caching for sub-200ms search response times

### 3.5 Content Curation and Bookmark System
**Description:** Advanced personal content library system enabling users to curate, organize, and access their preferred therapeutic resources.

**Functional Requirements:**
- FR-3.5.1: System shall provide bookmark functionality for saving content to personal libraries
- FR-3.5.2: System shall support bookmark organization by category and custom collections
- FR-3.5.3: System shall track bookmark engagement for understanding user content preferences
- FR-3.5.4: System shall provide bookmark-based recommendations for discovering similar content
- FR-3.5.5: System shall implement bookmark sharing and collaborative curation features

**Bookmark Management Features:**
- **Content Preservation**: Secure saving of therapeutic content for future access and reference
- **Category Organization**: Automatic and manual categorization of bookmarked content
- **Engagement Analytics**: Tracking of bookmark usage patterns for recommendation enhancement
- **Discovery Enhancement**: Bookmark-based content recommendations for expanding therapeutic resource libraries
- **Collaborative Features**: Sharing of curated content collections within therapeutic communities

---

## 4. External Interface Requirements

### 4.1 User Interfaces
**Content Discovery Interfaces:**
- Personalized content feed with intelligent recommendations
- Advanced search interface with multi-dimensional filtering
- Content detail view with engagement tracking and related content suggestions
- Bookmark management interface with organization and curation tools

### 4.2 API Interfaces

**Content Discovery Endpoints:**
```
GET /content/feed
- Input: Pagination (skip, limit), filters (category, content_type, difficulty)
- Output: Personalized content recommendations with engagement metadata

GET /content/wellness
- Input: Pagination and filtering parameters
- Output: Wellness-specific content with therapeutic focus

GET /content/search
- Input: Search query (q), filters (category, content_type), pagination
- Output: Ranked search results with relevance scoring

GET /content/category/{category}
- Input: Category name and pagination parameters
- Output: Category-specific content with popularity ranking
```

**Content Management Endpoints:**
```
GET /content/{content_id}
- Input: Content UUID and optional user context
- Output: Complete content with metadata and engagement tracking

POST /content/view/{content_id}
- Input: Content ID and user authentication
- Output: View tracking confirmation (background processing)
```

**Affirmation System Endpoints:**
```
GET /affirmations
- Input: Category filter, mood context, limit
- Output: Categorized affirmations with therapeutic metadata

GET /affirmations/random
- Input: Category and mood context filters
- Output: Single contextually-appropriate affirmation with engagement tracking
```

**Bookmark Management Endpoints:**
```
POST /bookmark/{content_id}
- Input: Content ID and user authentication
- Output: Bookmark creation confirmation with collection options

DELETE /bookmark/{content_id}
- Input: Content ID and user authentication
- Output: Bookmark removal confirmation

GET /bookmarks
- Input: Pagination, category filter, user authentication
- Output: User's bookmarked content with organization metadata
```

### 4.3 Hardware Interfaces
**Compute Resources:**
- CPU: Multi-core processor for content recommendation processing and search operations
- Memory: Minimum 1GB RAM for content caching and recommendation algorithm execution
- Storage: SSD storage for content metadata, user interactions, and recommendation model data

### 4.4 Software Interfaces

**Database Interfaces:**
- PostgreSQL: Content metadata storage with full-text search capabilities
- Content tables: Articles, affirmations, user bookmarks, engagement analytics
- User interaction tracking: View counts, bookmark patterns, recommendation effectiveness

**Caching Interfaces:**
- Redis: High-performance content caching for recommendation optimization
- Feed caching: Personalized content feed caching for sub-300ms response times
- Search result caching: Query result optimization for frequently accessed searches

**Event System Interfaces:**
- Enhanced Event Bus V3: Content engagement event publishing for AI analytics
- AI Context Store: User content interaction context for cross-service personalization
- Content recommendation events: Real-time publishing of recommendation effectiveness data

### 4.5 Communication Protocols
- HTTP/HTTPS for REST API communication
- JSON for data serialization and API responses
- Background task processing for view count incrementation and analytics
- Event-driven messaging for real-time content analytics integration

---

## 5. Non-Functional Requirements

### 5.1 Performance
- **Content Feed Generation:** 95% of personalized feeds delivered within 300ms
- **Search Response Time:** <200ms for complex multi-filter search queries
- **Content Delivery:** Sub-second response time for content access and display
- **Concurrent Users:** Support 500+ simultaneous content requests with optimal performance

### 5.2 Reliability
- **Availability:** 99.9% uptime for content services and recommendation systems
- **Data Consistency:** ACID compliance for content metadata and user interaction tracking
- **Recommendation Accuracy:** 80%+ accuracy in personalized content recommendations
- **Content Integrity:** 100% preservation of therapeutic content and user bookmark data

### 5.3 Therapeutic Effectiveness
- **Evidence-Based Content:** 100% compliance with mental health content standards
- **Accessibility:** Full WCAG 2.1 AA compliance for diverse user accessibility needs
- **Cultural Sensitivity:** Content review and adaptation for multicultural user base
- **Therapeutic Value:** Measurable positive impact on user mental wellness outcomes

### 5.4 Scalability
- **Content Volume:** Efficient handling of 10,000+ therapeutic content items
- **User Growth:** Scalable recommendation algorithms supporting growing user base
- **Recommendation Processing:** Distributed processing for high-volume personalization
- **Cache Optimization:** Intelligent caching strategies for optimal content delivery performance

### 5.5 Security
- **Content Protection:** Secure storage and delivery of proprietary therapeutic content
- **User Privacy:** Anonymous analytics with strict personal data protection
- **Access Control:** Authenticated access for personalized features and bookmark management
- **Data Encryption:** TLS 1.3 for all content delivery and user interaction data

---

## 6. Glossary and Appendix

### 6.1 Glossary
- **Content Curation**: AI-powered organization and recommendation of therapeutic content
- **Mood-Contextual Affirmations**: Positive messaging adapted to user emotional state
- **Personalized Recommendations**: Algorithm-based content suggestions using behavioral analysis
- **Therapeutic Value Scoring**: Measurement of content effectiveness for mental wellness
- **Wellness Content Taxonomy**: Evidence-based categorization system for mental health resources

### 6.2 Appendix A: Content Type Specifications
```yaml
# Content Type Definitions
content_types:
  article:
    description: "Long-form educational and therapeutic text content"
    required_fields: [title, content, category, difficulty_level]
    optional_fields: [author, source_url, tags]
    therapeutic_focus: ["education", "guidance", "self-help"]
    
  video:
    description: "Visual therapeutic content including guided meditations"
    required_fields: [title, content, category, duration_minutes]
    optional_fields: [author, source_url, tags]
    therapeutic_focus: ["guided practice", "visual learning", "demonstration"]
    
  audio:
    description: "Audio-based therapeutic content and mindfulness recordings"
    required_fields: [title, content, category, duration_minutes]
    optional_fields: [author, source_url, tags]
    therapeutic_focus: ["meditation", "relaxation", "sleep support"]
    
  exercise:
    description: "Interactive wellness activities and therapeutic interventions"
    required_fields: [title, content, category, duration_minutes]
    optional_fields: [difficulty_level, tags]
    therapeutic_focus: ["practice", "skill building", "intervention"]
```

### 6.3 Appendix B: Recommendation Algorithm Architecture
```python
class PersonalizedRecommendationEngine:
    """
    Advanced content recommendation system with multi-factor scoring
    
    Components:
    - User behavior analysis
    - Mood integration
    - Collaborative filtering
    - Content quality scoring
    - Real-time adaptation
    """
    
    def generate_recommendations(self, user_id, limit=20):
        # 1. User Profile Analysis
        user_profile = self.analyze_user_behavior(user_id)
        
        # 2. Mood Context Integration
        current_mood = self.get_user_mood_context(user_id)
        
        # 3. Content Scoring
        candidate_content = self.get_candidate_content(user_profile)
        scored_content = self.apply_multi_factor_scoring(
            candidate_content, user_profile, current_mood
        )
        
        # 4. Collaborative Filtering
        similar_users = self.find_similar_users(user_profile)
        collaborative_boost = self.apply_collaborative_filtering(
            scored_content, similar_users
        )
        
        # 5. Final Ranking and Selection
        final_recommendations = self.rank_and_select(
            collaborative_boost, limit
        )
        
        return final_recommendations
    
    def apply_multi_factor_scoring(self, content, user_profile, mood):
        """
        Multi-factor content scoring algorithm
        
        Factors:
        - User preference match (40%)
        - Mood appropriateness (25%)
        - Content quality/effectiveness (20%)
        - Novelty/diversity (10%)
        - Trending/popularity (5%)
        """
        scoring_weights = {
            'preference_match': 0.40,
            'mood_appropriateness': 0.25,
            'content_quality': 0.20,
            'novelty_diversity': 0.10,
            'trending_popularity': 0.05
        }
        
        for item in content:
            item['recommendation_score'] = sum(
                item[factor] * weight 
                for factor, weight in scoring_weights.items()
            )
        
        return sorted(content, key=lambda x: x['recommendation_score'], reverse=True)
```

### 6.4 Appendix C: Affirmation Therapeutic Categories
```yaml
# Complete Affirmation System Configuration
affirmation_categories:
  confidence_building:
    therapeutic_focus: ["self-efficacy", "capability", "empowerment"]
    mood_contexts: ["anxious", "insecure", "doubtful", "overwhelmed"]
    evidence_base: "Cognitive Behavioral Therapy, Self-Efficacy Theory"
    sample_affirmations:
      - "I am capable of handling whatever comes my way today."
      - "I have overcome challenges before, and I can do it again."
      - "My abilities and strengths are enough to face this situation."
  
  self_compassion:
    therapeutic_focus: ["self-kindness", "emotional validation", "acceptance"]
    mood_contexts: ["sad", "self-critical", "disappointed", "guilty"]
    evidence_base: "Self-Compassion Theory (Kristin Neff), Mindfulness-Based Therapy"
    sample_affirmations:
      - "My feelings are valid, and it's okay to take time to process them."
      - "I treat myself with the same kindness I would show a good friend."
      - "I am human, and making mistakes is part of learning and growing."
  
  mindful_acceptance:
    therapeutic_focus: ["present moment", "letting go", "control acceptance"]
    mood_contexts: ["worried", "anxious", "frustrated", "controlling"]
    evidence_base: "Acceptance and Commitment Therapy, Mindfulness-Based Stress Reduction"
    sample_affirmations:
      - "I choose to focus on what I can control and let go of what I cannot."
      - "This moment is the only one I truly have, and I embrace it fully."
      - "I accept my thoughts and feelings without judgment."
  
  resilience_strength:
    therapeutic_focus: ["growth mindset", "perseverance", "inner strength"]
    mood_contexts: ["difficult", "challenging", "discouraged", "defeated"]
    evidence_base: "Resilience Theory, Post-Traumatic Growth, Positive Psychology"
    sample_affirmations:
      - "I am growing stronger through every challenge I face."
      - "Difficult times reveal my inner strength and resilience."
      - "Every setback is an opportunity for growth and learning."
```

### 6.5 Appendix D: Content Analytics and Effectiveness Metrics
```yaml
# Content Effectiveness Measurement Framework
analytics_metrics:
  engagement_metrics:
    view_duration:
      description: "Average time spent consuming content"
      therapeutic_indicator: "Content relevance and user interest"
      target_thresholds:
        articles: "> 3 minutes average"
        videos: "> 70% completion rate"
        audio: "> 80% completion rate"
        exercises: "> 90% completion rate"
    
    bookmark_rate:
      description: "Percentage of viewers who bookmark content"
      therapeutic_indicator: "Long-term value and reference utility"
      target_threshold: "> 15% bookmark rate"
    
    return_engagement:
      description: "Users returning to same content multiple times"
      therapeutic_indicator: "Therapeutic value and practical utility"
      target_threshold: "> 25% return rate"
  
  therapeutic_effectiveness:
    mood_improvement_correlation:
      description: "Content consumption correlation with mood improvements"
      measurement: "Pre/post mood tracking integration"
      target_threshold: "> 0.3 correlation coefficient"
    
    user_reported_helpfulness:
      description: "Direct user feedback on content therapeutic value"
      measurement: "Optional rating system (1-5 scale)"
      target_threshold: "> 4.0 average rating"
    
    behavioral_change_indicators:
      description: "Long-term user behavior improvements"
      measurement: "Platform engagement and wellness metric improvements"
      target_threshold: "Measurable positive trends over 30+ days"
```

### 6.6 Appendix E: Content Caching and Performance Optimization
```yaml
# Redis Caching Strategy
caching_configuration:
  content_feeds:
    cache_duration: 600  # 10 minutes
    cache_key_pattern: "feed:{user_id}:{filters_hash}"
    invalidation_triggers: ["new_content", "user_preference_change"]
    
  search_results:
    cache_duration: 1800  # 30 minutes
    cache_key_pattern: "search:{query_hash}:{filters_hash}"
    invalidation_triggers: ["content_updates", "ranking_algorithm_changes"]
    
  popular_content:
    cache_duration: 3600  # 1 hour
    cache_key_pattern: "popular:{category}:{content_type}"
    invalidation_triggers: ["engagement_threshold_changes"]
    
  user_bookmarks:
    cache_duration: 300   # 5 minutes
    cache_key_pattern: "bookmarks:{user_id}"
    invalidation_triggers: ["bookmark_add", "bookmark_remove"]

# Performance Optimization Strategies
performance_targets:
  api_response_times:
    content_feed: "< 300ms for 95% of requests"
    search_queries: "< 200ms for complex multi-filter searches"
    content_detail: "< 100ms for cached content"
    affirmation_delivery: "< 50ms for random selection"
    
  concurrent_capacity:
    simultaneous_users: "500+ concurrent content requests"
    recommendation_processing: "100+ recommendations per second"
    search_throughput: "200+ search queries per second"
```



