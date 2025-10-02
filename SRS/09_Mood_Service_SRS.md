# Software Requirements Specification (SRS)
## Mood Service

**Version:** 1.0.0  
**Date:** October 2025  
**Project:** MantraPath - Mental Health and Wellness Platform

---

## 1. Introduction

### 1.1 Purpose
This document specifies the requirements for the Mood Service, a critical component of the MantraPath platform that provides AI-powered emotion detection, mood tracking, and comprehensive analytics for mental wellness insights. The service acts as the emotional intelligence hub that processes user mood entries, analyzes emotional patterns, and generates actionable insights for personal wellbeing management.

### 1.2 Scope
The Mood Service encompasses:
- AI-powered emotion detection using GoEmotions model with 27+ emotion categories
- Comprehensive mood tracking with multi-dimensional scoring (mood, stress, energy)
- Real-time sentiment analysis and emotional state classification
- Advanced analytics including pattern recognition and trend analysis
- Memory service integration for chatbot context enhancement
- Cultural sensitivity in emotion interpretation and response
- Crisis detection and early intervention alert systems

### 1.3 Definitions and Acronyms
- **Mood Score**: 1-10 numerical rating of user's emotional state
- **GoEmotions Model**: Google's advanced emotion classification AI model
- **Sentiment Types**: Positive, Negative, Neutral, Ambiguous emotional categories
- **Wellbeing Score**: Comprehensive metric combining mood, stress, energy metrics
- **Emotion Analysis**: AI-driven categorization of emotions from text input
- **Mood Patterns**: Statistical analysis of emotional trends over time
- **Context Tags**: User-defined labels for mood entry categorization

### 1.4 References
- MantraPath System Architecture Documentation
- GoEmotions Research Paper and Model Specifications
- Mental Health Clinical Guidelines
- AI Ethics and Bias Prevention Standards
- Cultural Psychology Research Framework

### 1.5 Document Overview
This SRS details functional requirements, non-functional requirements, system interfaces, and implementation constraints for the Mood Service within the MantraPath ecosystem.

---

## 2. Overall Description

### 2.1 Product Perspective
The Mood Service operates as the emotional intelligence center in MantraPath's microservices architecture. It:
- Receives mood entries from authenticated users via API Gateway
- Integrates with Memory Service for enhanced chatbot personalization
- Communicates with ML Service for advanced pattern recognition
- Provides analytics data to frontend dashboard components
- Triggers notifications for mood pattern alerts
- Supports crisis intervention through real-time monitoring

### 2.2 Product Functions
**Core Functions:**
- Multi-dimensional mood tracking with 1-10 scoring across mood, stress, and energy levels
- AI-powered emotion detection from text descriptions using GoEmotions model with 95%+ accuracy
- Real-time sentiment analysis with four-category classification (positive, negative, neutral, ambiguous)
- Comprehensive analytics dashboard with weekly, monthly, and yearly trend analysis
- Pattern recognition for identifying emotional cycles and trigger events
- Personalized insights generation based on individual mood history
- Crisis detection with automatic alert generation for concerning patterns

**Advanced Analytics Features:**
- Wellbeing score calculation combining multiple emotional dimensions
- Mood distribution analysis showing emotional state percentages
- Improvement trend tracking comparing temporal periods
- Correlation analysis between mood, stress, and energy levels
- Context-based mood categorization using user-defined tags
- Goal tracking for mood improvement initiatives
- Predictive modeling for mood forecasting

**Integration Capabilities:**
- Memory service synchronization for chatbot context enhancement
- Journal entry emotion analysis for comprehensive mood tracking
- Location and activity correlation for environmental mood factors
- Background task processing for non-blocking analytics computation

### 2.3 User Classes and Characteristics
**Primary Users:**
- Mental health platform users seeking mood tracking and emotional awareness
- Mental health professionals monitoring patient progress
- Researchers analyzing emotional wellbeing patterns
- Crisis intervention specialists requiring real-time alerts

**User Characteristics:**
- Diverse cultural backgrounds requiring sensitive emotion interpretation
- Varying levels of emotional awareness and expression capabilities
- Range from casual mood tracking to intensive therapeutic monitoring
- Need for privacy-first, secure emotional data handling

### 2.4 Operating Environment
**Deployment Environment:**
- Containerized deployment using Docker on port 8003
- Kubernetes orchestration for horizontal scaling
- PostgreSQL database for persistent mood data storage
- Redis caching for performance optimization
- Integration with GoEmotions transformer model
- NATS messaging for real-time event streaming

**Dependencies:**
- Python 3.11+ runtime environment
- FastAPI web framework for API services
- SQLAlchemy ORM for database operations
- Transformers library for AI model integration
- PostgreSQL 13+ for relational data storage
- Redis 6+ for caching and session management

### 2.5 Design and Implementation Constraints
**Technical Constraints:**
- Must maintain <500ms response time for mood entry creation
- AI emotion analysis must complete within 2 seconds
- Support for 1000+ concurrent mood entries per minute
- Memory usage optimized for transformer model efficiency
- Cultural sensitivity compliance for global user base

**Regulatory Constraints:**
- HIPAA compliance for mental health data protection
- GDPR compliance for European users' emotional data
- FDA guidelines for digital therapeutic applications
- Ethical AI standards for bias prevention in emotion detection
- Data retention policies for mental health records

### 2.6 Assumptions and Dependencies
**Assumptions:**
- Users provide authentic emotional state information
- GoEmotions model maintains consistent accuracy across cultures
- Network connectivity supports real-time emotion analysis
- Database performance scales with user growth

**Dependencies:**
- Authentication Service for user validation and session management
- Memory Service for chatbot context integration
- ML Service for advanced pattern recognition algorithms
- API Gateway for request routing and load balancing
- PostgreSQL database cluster for data persistence

---

## 3. System Features

### 3.1 Multi-Dimensional Mood Tracking
**Description:** Comprehensive mood entry system capturing emotional state, stress levels, and energy levels with contextual information.

**Functional Requirements:**
- FR-3.1.1: System shall accept mood scores on 1-10 scale with integer precision
- FR-3.1.2: System shall capture optional stress levels (1-10) and energy levels (1-10)
- FR-3.1.3: System shall support text descriptions up to 1000 characters for emotional context
- FR-3.1.4: System shall accept user-defined context tags for mood categorization
- FR-3.1.5: System shall record optional location and activity information
- FR-3.1.6: System shall timestamp all mood entries with UTC precision
- FR-3.1.7: System shall validate all numerical inputs within specified ranges
- FR-3.1.8: System shall support batch processing for historical mood data import

**Input:** User mood data including scores, descriptions, context tags, location, activity
**Output:** Structured mood entry with unique ID, timestamps, and validation status

### 3.2 AI-Powered Emotion Detection
**Description:** Advanced emotion analysis using GoEmotions model to classify emotional states from text descriptions.

**Functional Requirements:**
- FR-3.2.1: System shall analyze text descriptions using GoEmotions model with 27 emotion categories
- FR-3.2.2: System shall classify emotions into sentiment groups: positive, negative, neutral, ambiguous
- FR-3.2.3: System shall provide confidence scores for emotion detection (0-100%)
- FR-3.2.4: System shall assign color coding for visual emotion representation
- FR-3.2.5: System shall cache emotion analysis results for performance optimization
- FR-3.2.6: System shall handle multiple languages with appropriate model selection
- FR-3.2.7: System shall detect and flag potentially concerning emotional content for crisis intervention
- FR-3.2.8: System shall provide fallback analysis when AI model is unavailable

**Supported Emotions:**
- **Positive**: admiration, amusement, approval, caring, desire, excitement, gratitude, joy, love, optimism, pride, relief
- **Negative**: anger, annoyance, disappointment, disapproval, disgust, embarrassment, fear, grief, nervousness, remorse, sadness
- **Ambiguous**: confusion, curiosity, realization, surprise
- **Neutral**: neutral emotional state

**Input:** Text description from mood entry
**Output:** Emotion analysis with primary emotion, sentiment classification, confidence score, and color coding

### 3.3 Comprehensive Analytics Dashboard
**Description:** Advanced analytics engine providing insights, patterns, and trends from mood data.

**Functional Requirements:**
- FR-3.3.1: System shall calculate wellbeing scores combining mood, stress, and energy dimensions
- FR-3.3.2: System shall analyze mood trends across configurable time periods (7d, 30d, 90d, 1y)
- FR-3.3.3: System shall identify improvement trends comparing temporal periods
- FR-3.3.4: System shall generate mood distribution analysis showing emotional state percentages
- FR-3.3.5: System shall detect recurring patterns and cycles in emotional states
- FR-3.3.6: System shall provide correlation analysis between different mood dimensions
- FR-3.3.7: System shall generate personalized insights based on individual mood history
- FR-3.3.8: System shall support comparative analysis between different time periods

**Analytics Metrics:**
- **Wellbeing Score**: Composite metric (0-100) combining all mood dimensions
- **Average Mood**: Mean mood score over specified period
- **Trend Analysis**: Statistical trend direction and magnitude
- **Pattern Recognition**: Recurring cycles and emotional patterns
- **Correlation Analysis**: Relationships between mood, stress, energy

**Input:** Historical mood data, time period selection, analysis preferences
**Output:** Comprehensive analytics report with visualizations and insights

### 3.4 Crisis Detection and Intervention
**Description:** Real-time monitoring system for identifying concerning mood patterns requiring immediate attention.

**Functional Requirements:**
- FR-3.4.1: System shall monitor mood entries for crisis indicators including prolonged low mood scores
- FR-3.4.2: System shall detect concerning emotional content using natural language processing
- FR-3.4.3: System shall identify high-risk patterns such as sustained negative emotions
- FR-3.4.4: System shall generate immediate alerts for crisis intervention specialists
- FR-3.4.5: System shall maintain crisis detection sensitivity settings adjustable by professionals
- FR-3.4.6: System shall log all crisis detection events for review and improvement
- FR-3.4.7: System shall integrate with notification service for immediate alert delivery
- FR-3.4.8: System shall provide escalation pathways for different crisis severity levels

**Crisis Indicators:**
- Mood scores below 3 for consecutive entries over 7 days
- High-stress levels (8-10) combined with low mood for extended periods
- Emotional content indicating self-harm or severe depression
- Sudden dramatic changes in mood patterns
- Extended periods without mood entries after regular tracking

### 3.5 Memory Service Integration
**Description:** Seamless integration with Memory Service to enhance chatbot personalization with mood context.

**Functional Requirements:**
- FR-3.5.1: System shall automatically notify Memory Service of significant mood changes
- FR-3.5.2: System shall provide mood context summaries for chatbot conversations
- FR-3.5.3: System shall share emotional patterns relevant to conversation personalization
- FR-3.5.4: System shall maintain user privacy controls for mood data sharing
- FR-3.5.5: System shall support real-time mood updates for active chatbot sessions
- FR-3.5.6: System shall provide historical mood context for conversation continuity

---

## 4. External Interface Requirements

### 4.1 User Interfaces
**Web Dashboard Interface:**
- Mood entry forms with intuitive slider controls for scoring
- Visual emotion timeline with color-coded emotional states
- Interactive analytics charts showing trends and patterns
- Personalized insights panel with actionable recommendations
- Crisis support resources easily accessible during concerning patterns

**Mobile-Optimized Interface:**
- Quick mood check-in with minimal interaction steps
- Voice-to-text description input for accessibility
- Offline mood entry capability with synchronization
- Push notification integration for mood tracking reminders

### 4.2 API Interfaces

**REST API Endpoints:**
```
POST /api/v1/mood/entries
- Input: MoodCreateRequest (mood_score, description, stress_level, energy_level, context_tags)
- Output: MoodEntryResponse with emotion analysis

GET /api/v1/mood/entries
- Parameters: limit, offset for pagination
- Output: List of user's mood entries with analytics

GET /api/v1/mood/analytics/overview
- Parameters: period (7d, 30d, 90d, 1y)
- Output: Comprehensive analytics overview with insights

POST /api/v1/mood/emotion/analyze
- Input: EmotionAnalysisRequest (text, include_mood_entry)
- Output: Detailed emotion analysis with confidence scores

GET /api/v1/mood/patterns
- Parameters: start_date, end_date, pattern_type
- Output: Mood pattern analysis and predictions

GET /api/v1/mood/insights
- Parameters: user_id, time_range
- Output: Personalized insights and recommendations

POST /api/v1/mood/context
- Input: MoodContextRequest (mood_entry_id, context_data)
- Output: Enhanced mood context with environmental factors

GET /api/v1/mood/analytics/wellbeing-score
- Output: Current wellbeing score with contributing factors

GET /api/v1/mood/crisis/status
- Output: Current crisis risk assessment and support resources
```

### 4.3 Hardware Interfaces
**Compute Resources:**
- Multi-core CPU for AI model inference and analytics processing
- GPU acceleration support for transformer model optimization
- Minimum 2GB RAM for GoEmotions model and caching
- SSD storage for fast database access and model loading

**Network Requirements:**
- Stable internet connection for AI model updates
- Low-latency database connectivity for real-time mood tracking
- Integration bandwidth for Memory Service synchronization

### 4.4 Software Interfaces

**Database Interfaces:**
- PostgreSQL connection for persistent mood data storage
- Redis integration for emotion analysis caching
- Database migrations for schema evolution

**AI Model Interfaces:**
- HuggingFace Transformers API for GoEmotions model
- Model versioning support for continuous improvement
- Fallback mechanisms for model unavailability

**Service Integration:**
- Memory Service API for chatbot context sharing
- Notification Service for crisis alert delivery
- Authentication Service for user validation
- ML Service for advanced analytics processing

### 4.5 Communication Interfaces
**Internal Service Communication:**
- HTTP/HTTPS for REST API communication with other services
- NATS messaging for real-time event streaming
- WebSocket support for live dashboard updates
- gRPC for high-performance service-to-service communication

**External Integrations:**
- Secure API endpoints for third-party mental health platforms
- Webhook support for crisis intervention services
- Data export capabilities for mental health professionals

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements
- Response time for mood entry creation: <500ms for 95% of requests
- Emotion analysis completion time: <2 seconds using GoEmotions model
- Analytics dashboard loading: <3 seconds for 30-day period analysis
- Concurrent user support: 1000+ simultaneous mood entries
- Database query optimization: <100ms for mood retrieval operations
- Cache hit ratio: >90% for emotion analysis results

### 5.2 Scalability Requirements
- Horizontal scaling capability across multiple container instances
- Database partitioning support for large-scale mood data
- Load balancing for AI model inference across multiple nodes
- Auto-scaling based on usage patterns and peak periods
- Storage capacity planning for long-term mood data retention

### 5.3 Security Requirements
- End-to-end encryption for all mood data transmission
- HIPAA-compliant data handling and storage procedures
- Multi-factor authentication integration for administrative access
- Audit logging for all mood data access and modifications  
- Data anonymization capabilities for research purposes
- Secure API rate limiting to prevent abuse

### 5.4 Reliability Requirements
- System uptime: 99.9% availability with planned maintenance windows
- Data backup and disaster recovery procedures for mood data
- Graceful degradation when AI models are unavailable
- Error recovery mechanisms for failed emotion analysis
- Redundant database connections for high availability

### 5.5 Usability Requirements
- Intuitive mood entry interface requiring minimal training
- Accessibility compliance (WCAG 2.1 AA) for users with disabilities
- Multi-language support for emotion detection and interface
- Cultural sensitivity in emotion interpretation and feedback
- Mobile-responsive design for cross-device consistency

### 5.6 Cultural and Ethical Requirements
- Bias detection and mitigation in AI emotion analysis
- Cultural context consideration in emotion interpretation
- Ethical guidelines for crisis detection sensitivity
- User consent management for mood data sharing
- Transparent AI decision-making processes

---

## 6. Data Requirements

### 6.1 Data Models
**Primary Entities:**
- MoodEntry: Core mood tracking record with multi-dimensional scoring
- EmotionAnalysis: AI-generated emotion classification and sentiment data
- MoodPattern: Statistical analysis results and trend identification
- CrisisAlert: Risk assessment and intervention trigger records
- UserPreference: Cultural and personal mood tracking preferences

### 6.2 Data Integrity
- Referential integrity between mood entries and user accounts
- Data validation for all numerical mood scores and timestamps
- Consistency checks between emotion analysis and mood scores
- Audit trails for all mood data modifications and access

### 6.3 Data Privacy
- User data ownership and control mechanisms
- Granular privacy settings for mood data sharing
- Data retention policies aligned with mental health regulations
- Anonymization procedures for research and analytics
- Right to erasure compliance for data deletion requests

---

## 7. User Experience Enhancements

### 7.1 Personalization Features
- Adaptive mood tracking based on user patterns and preferences
- Customizable analytics dashboards with user-selected metrics
- Personalized insights generation using individual mood history
- Smart reminders for mood tracking based on optimal timing
- Cultural adaptation of emotion interpretation and feedback

### 7.2 Gamification Elements
- Mood tracking streaks and consistency rewards
- Wellbeing improvement challenges and goal setting
- Achievement badges for emotional awareness milestones
- Progress visualization with engaging charts and graphics
- Social sharing options for mood improvement achievements

### 7.3 Educational Components
- Emotional intelligence resources and learning materials
- Mood pattern explanation and interpretation guides
- Crisis prevention education and coping strategy recommendations
- Integration with content service for relevant wellness resources
- Expert-reviewed mental health information and tips

### 7.4 Accessibility Features
- Voice input support for mood descriptions and entries
- Screen reader compatibility for visually impaired users
- Large text and high contrast options for better readability
- Simplified interface modes for users with cognitive challenges
- Multi-modal input methods including gestures and voice commands

---

## 8. Implementation Roadmap

### 8.1 Phase 1: Core Functionality (Completed)
- Basic mood entry system with 1-10 scoring
- GoEmotions AI model integration for emotion detection
- PostgreSQL database setup with mood data models
- REST API endpoints for mood tracking operations
- Basic analytics dashboard with trend visualization

### 8.2 Phase 2: Advanced Analytics (In Progress)
- Comprehensive wellbeing score calculation algorithm
- Pattern recognition system for mood cycle identification
- Correlation analysis between mood dimensions
- Personalized insights generation engine
- Crisis detection system with alert mechanisms

### 8.3 Phase 3: Enhanced User Experience (Planned)
- Cultural sensitivity improvements in emotion analysis
- Advanced personalization based on user behavior patterns
- Gamification elements for increased engagement
- Voice input integration for accessibility
- Mobile app optimization for seamless cross-device experience

### 8.4 Phase 4: Advanced AI Integration (Future)
- Predictive modeling for mood forecasting
- Advanced natural language processing for context analysis
- Integration with wearable devices for physiological mood indicators
- Machine learning optimization for personalized emotion detection
- Research collaboration features for mental health studies

---

This SRS document provides a comprehensive foundation for the Mood Service, ensuring all stakeholders understand the technical requirements, user experience goals, and implementation strategy for this critical component of the MantraPath mental health platform.