# Software Requirements Specification (SRS)
## Action Orchestrator Service

**Version:** 1.0.0  
**Date:** December 2024  
**Project:** MantraPath - Mental Health and Wellness Platform

---

## 1. Introduction

### 1.1 Purpose
This document specifies the requirements for the Action Orchestrator Service, a critical component of the MantraPath platform that provides voice-driven cross-service workflow coordination. The service acts as the central orchestration engine that processes voice intents, coordinates actions across multiple microservices, and manages complex workflows with cultural context awareness.

### 1.2 Scope
The Action Orchestrator Service encompasses:
- Voice intent processing and classification with multi-language support
- Cross-service workflow orchestration and coordination
- Cultural context processing and adaptation
- Workflow execution with rollback capabilities
- Service health monitoring and circuit breaker patterns
- Real-time workflow status tracking and management

### 1.3 Definitions and Acronyms
- **Intent**: A user's purpose or goal extracted from voice input
- **Workflow**: A sequence of coordinated actions across multiple services
- **Cultural Context**: User's language, communication style, and cultural preferences
- **Action Dispatcher**: Component responsible for executing service calls
- **Rollback Manager**: Component handling workflow failure recovery
- **Circuit Breaker**: Pattern for handling service failures gracefully

### 1.4 References
- MantraPath System Architecture Documentation
- Voice Processing Integration Specifications
- Cultural Adaptation Guidelines
- Service Integration Protocols

### 1.5 Document Overview
This SRS details functional requirements, non-functional requirements, system interfaces, and implementation constraints for the Action Orchestrator Service within the MantraPath ecosystem.

---

## 2. Overall Description

### 2.1 Product Perspective
The Action Orchestrator Service operates as the central coordination hub in MantraPath's microservices architecture. It:
- Receives voice input from the Voice Service
- Coordinates with Authentication, Profile, Mood, Community, Content, and Notification services
- Integrates with ML Service for intent classification
- Communicates with Translation Service for multi-language support
- Reports to API Gateway for external access

### 2.2 Product Functions
**Core Functions:**
- Voice Intent Classification with 95%+ accuracy using transformer models
- Cross-service workflow orchestration with parallel and sequential execution
- Cultural context processing and adaptation for 25+ languages
- Workflow rollback and error recovery with ACID transaction support
- Service health monitoring and circuit breaking with automatic failover
- Real-time workflow status management with WebSocket notifications

**Supported Intent Types:**
- **Journal Entry Creation**: Voice-to-text journal entries with sentiment analysis
- **Mood Tracking**: Emotional state recording with cultural context adaptation
- **Chat Conversations**: AI chatbot interactions with conversation history
- **Community Interactions**: Social platform engagement and content sharing
- **Profile Updates**: User preference and setting modifications
- **Analytics Queries**: Personal wellness data analysis and reporting
- **Content Search**: Intelligent content discovery and recommendations
- **Voice Commands**: System navigation and control via voice
- **Crisis Intervention**: High-priority mental health emergency detection

**Workflow Execution Patterns:**
- **Sequential Workflows**: Step-by-step execution with dependency management
- **Parallel Workflows**: Concurrent action execution for performance optimization
- **Conditional Workflows**: Dynamic path selection based on context and results
- **Compensating Workflows**: Rollback actions for failed operations

### 2.3 User Classes and Characteristics
**Primary Users:**
- End Users: Mental health platform users interacting via voice
- System Administrators: Monitoring and managing orchestrator health
- Service Developers: Integrating new services with orchestrator

**User Characteristics:**
- Multi-cultural user base requiring language adaptation
- Varying technical proficiency levels
- Need for reliable, fast response times (<2 seconds)
- Require privacy and security compliance

### 2.4 Operating Environment
**Deployment Environment:**
- Containerized deployment using Docker
- Kubernetes orchestration for scaling
- Port 8012 for HTTP API access
- Redis for caching and session management
- PostgreSQL for persistent workflow data
- NATS for event streaming

**Dependencies:**
- Python 3.11+ runtime environment
- FastAPI web framework
- AsyncPG for database connectivity
- NATS-py for message streaming
- Transformers library for ML processing

### 2.5 Design and Implementation Constraints
**Technical Constraints:**
- Must maintain <2 second response time for 95% of requests
- Support for 10+ concurrent workflows per user
- Memory usage limited to 512MB per instance
- CPU usage optimized for horizontal scaling

**Regulatory Constraints:**
- HIPAA compliance for health data handling
- GDPR compliance for European users
- Cultural sensitivity requirements
- Data retention policies (7 years for health data)

### 2.6 Assumptions and Dependencies
**Assumptions:**
- Voice Service provides pre-processed audio transcription
- All integrated services maintain <500ms response times
- Redis cluster maintains 99.9% availability
- Network latency between services <50ms

**Dependencies:**
- Authentication Service for user validation
- Profile Service for user preferences
- ML Service for intent classification models
- Translation Service for multi-language support

---

## 3. System Features

### 3.1 Voice Intent Processing
**Description:** Process and classify voice input into actionable intents with cultural context using advanced NLP models.

**Functional Requirements:**
- FR-3.1.1: System shall classify voice intents with minimum 95% accuracy using transformer-based models
- FR-3.1.2: System shall support English and Hindi languages initially, with extensibility for 25+ languages
- FR-3.1.3: System shall extract structured parameters from voice input including:
  - Mood values (1-10 scale with emotional descriptors)
  - Time references (relative and absolute temporal expressions)
  - Entity extraction (names, locations, activities)
  - Intent confidence levels (HIGH, MEDIUM, LOW, VERY_LOW)
- FR-3.1.4: System shall handle cultural communication styles with adaptive processing:
  - **Direct Style**: Western communication patterns with explicit intent
  - **Respectful Style**: Asian communication patterns with implicit context
  - **Formal Style**: Professional and hierarchical communication patterns
- FR-3.1.5: System shall process crisis intervention intents with highest priority and immediate escalation

**Processing Pipeline:**
1. **Text Normalization**: Cultural and linguistic text preprocessing
2. **Language Detection**: Automatic language identification with 98% accuracy
3. **Intent Classification**: Multi-class classification using fine-tuned BERT models
4. **Parameter Extraction**: Named entity recognition and slot filling
5. **Cultural Adaptation**: Context-aware response formatting

**Input:** Voice transcription text, user cultural preferences, session context
**Output:** VoiceIntent object with classified intent, confidence score, extracted parameters, and cultural adaptations

### 3.2 Workflow Orchestration
**Description:** Coordinate complex workflows across multiple microservices.

**Functional Requirements:**
- FR-3.2.1: System shall build workflows based on classified intents
- FR-3.2.2: System shall execute workflow steps sequentially or in parallel
- FR-3.2.3: System shall track workflow progress and status in real-time
- FR-3.2.4: System shall support workflow cancellation at any stage
- FR-3.2.5: System shall estimate workflow execution duration

**Input:** Voice intent with parameters and cultural context
**Output:** Executed workflow with results from all participating services

### 3.3 Cultural Context Adaptation
**Description:** Adapt workflows and responses based on user cultural context.

**Functional Requirements:**
- FR-3.3.1: System shall detect language from voice input
- FR-3.3.2: System shall adapt communication style (formal/informal)
- FR-3.3.3: System shall apply cultural sensitivities to responses
- FR-3.3.4: System shall normalize text based on cultural context
- FR-3.3.5: System shall maintain cultural preferences across sessions

### 3.4 Error Handling and Rollback
**Description:** Handle workflow failures and perform rollback operations.

**Functional Requirements:**
- FR-3.4.1: System shall detect service failures during workflow execution
- FR-3.4.2: System shall trigger rollback for failed workflows
- FR-3.4.3: System shall maintain transaction consistency across services
- FR-3.4.4: System shall retry failed operations with exponential backoff
- FR-3.4.5: System shall log all failure events for analysis

### 3.5 Service Health Monitoring
**Description:** Monitor health of integrated services and implement circuit breaker patterns.

**Functional Requirements:**
- FR-3.5.1: System shall monitor response times of all integrated services
- FR-3.5.2: System shall implement circuit breaker for failing services
- FR-3.5.3: System shall provide service status dashboard
- FR-3.5.4: System shall alert administrators of service degradation
- FR-3.5.5: System shall maintain service availability metrics

---

## 4. External Interface Requirements

### 4.1 User Interfaces
**Voice Interface:**
- Input: Natural language voice commands in supported languages
- Output: Structured responses adapted to cultural context
- Accessibility: Support for speech impairments through text alternatives

### 4.2 API Interfaces

**REST API Endpoints:**
```
POST /api/v1/orchestrate
- Input: OrchestrationRequest (voice_input, user_id, cultural_preferences)
- Output: OrchestrationResponse (workflow_id, status, results)

GET /api/v1/workflow/{workflow_id}/status
- Output: Workflow status and progress information

POST /api/v1/workflow/{workflow_id}/cancel
- Output: Cancellation confirmation

POST /api/v1/voice/intent/classify
- Input: Voice input for classification only
- Output: Intent classification without execution

POST /api/v1/cultural/adapt
- Input: Content and cultural preferences
- Output: Culturally adapted content

GET /api/v1/services/status
- Output: Health status of all integrated services

GET /api/v1/metrics
- Output: Orchestrator performance metrics
```

### 4.3 Hardware Interfaces
**Compute Resources:**
- CPU: Multi-core processor for parallel workflow execution
- Memory: Minimum 512MB RAM for caching and processing
- Storage: SSD storage for workflow logs and temporary data

### 4.4 Software Interfaces

**Service Integrations:**
- Authentication Service (Port 8001): User validation and JWT processing
- Profile Service (Port 8002): User preferences and profile data
- Mood Service (Port 8003): Mood tracking and analytics
- Chatbot Service (Port 8004): Conversational AI interactions
- Content Service (Port 8005): Content search and recommendations
- Community Service (Port 8006): Social interactions and forums
- Notification Service (Port 8007): Alert and notification delivery
- ML Service (Port 8008): Machine learning model inference
- Translation Service (Port 8010): Multi-language translation
- Voice Service (Port 8011): Voice processing and TTS

**Database Interfaces:**
- PostgreSQL: Workflow persistence and audit logs
- Redis: Session caching and temporary data storage

**Message Queue Interfaces:**
- NATS: Event streaming and service communication

### 4.5 Communication Protocols
- HTTP/HTTPS for REST API communication
- WebSocket for real-time workflow status updates
- NATS protocol for event streaming
- Redis protocol for caching operations

---

## 5. Non-Functional Requirements

### 5.1 Performance
- **Response Time:** 95% of orchestration requests completed within 2 seconds
- **Throughput:** Support 1000+ concurrent workflow executions
- **Scalability:** Horizontal scaling to handle 10x load increases
- **Resource Usage:** Maximum 512MB memory per service instance

### 5.2 Reliability
- **Availability:** 99.9% uptime (8.76 hours downtime per year)
- **Error Recovery:** Automatic rollback for 100% of failed workflows
- **Data Consistency:** ACID compliance for workflow transactions
- **Fault Tolerance:** Graceful degradation when services are unavailable

### 5.3 Security
- **Authentication:** JWT token validation for all API requests
- **Authorization:** Role-based access control (user, admin)
- **Data Encryption:** TLS 1.3 for all external communications
- **Privacy:** No sensitive data logging or caching
- **Audit:** Complete audit trail for all workflow executions

### 5.4 Maintainability
- **Code Quality:** 90%+ test coverage with automated testing
- **Monitoring:** Comprehensive logging and metrics collection
- **Documentation:** API documentation with OpenAPI/Swagger
- **Deployment:** Zero-downtime deployments with blue-green strategy

### 5.5 Portability
- **Containerization:** Docker containers for consistent deployment
- **Cloud Agnostic:** Support for AWS, GCP, and Azure platforms
- **Environment Flexibility:** Development, staging, and production configurations

---

## 6. Glossary and Appendix

### 6.1 Glossary
- **Action Dispatcher:** Component that executes service calls and manages timeouts
- **Circuit Breaker:** Design pattern that prevents cascading failures
- **Cultural Processor:** Component handling language and cultural adaptations
- **Intent Classifier:** ML-powered component for voice intent recognition
- **Orchestration:** Coordination of multiple services to complete a workflow
- **Rollback Manager:** Component handling workflow failure recovery
- **Workflow Builder:** Component that constructs execution plans from intents

### 6.2 Appendix A: Configuration Parameters
```yaml
# Service Configuration
ORCHESTRATOR_HOST: "0.0.0.0"
ORCHESTRATOR_PORT: 8012
MAX_RETRY_ATTEMPTS: 3
REQUEST_TIMEOUT: 30
CIRCUIT_BREAKER_THRESHOLD: 5

# Database Configuration
DATABASE_URL: "postgresql://user:pass@host:5432/db"
REDIS_URL: "redis://redis:6379"

# External Service URLs
AUTH_SERVICE_URL: "http://auth-service:8001"
PROFILE_SERVICE_URL: "http://profile-service:8002"
# ... additional service URLs
```

### 6.3 Appendix B: Supported Intent Types
1. **JOURNAL_ENTRY:** Creating personal journal entries
2. **MOOD_TRACKING:** Recording mood and emotional state
3. **CHAT_CONVERSATION:** Engaging with chatbot service
4. **COMMUNITY_INTERACTION:** Social platform interactions
5. **PROFILE_UPDATE:** Modifying user profile information
6. **ANALYTICS_QUERY:** Requesting personal analytics
7. **CONTENT_SEARCH:** Finding relevant content
8. **VOICE_COMMAND:** System navigation commands
9. **CRISIS_INTERVENTION:** Emergency mental health support

### 6.4 Appendix C: Cultural Context Parameters
**Core Cultural Attributes:**
- **Language:** User's preferred language (en, hi, es, fr, de, ar, etc.)
- **Cultural Region:** Geographic/cultural area (global, south_asia, east_asia, middle_east, europe, americas)
- **Communication Style:** Interaction preference (direct, respectful, neutral, hierarchical)
- **Formality Level:** Desired formality (casual, moderate, formal, very_formal)
- **Time Zone:** User's time zone for temporal context (UTC offset)
- **Date Format:** Preferred date representation (ISO, US, European, Asian)

**Extended Cultural Adaptations:**
- **Response Patterns:** Culture-specific acknowledgment and confirmation styles
- **Emotional Expression:** Cultural norms for emotional communication
- **Authority Recognition:** Hierarchical communication preferences
- **Collectivist vs Individualist:** Community-focused vs individual-focused messaging
- **High-Context vs Low-Context:** Implicit vs explicit communication preferences
- **Temporal Orientation:** Linear vs cyclical time perception

### 6.5 Appendix D: Workflow Templates and Patterns

**Journal Entry Workflow Template:**
```yaml
journal_entry_workflow:
  steps:
    - name: "authenticate_user"
      service: "auth_service"
      action: "validate_session"
      required: true
    - name: "process_content"
      service: "content_service" 
      action: "create_journal_entry"
      parameters: ["content", "mood_context", "cultural_context"]
      parallel: false
    - name: "analyze_sentiment"
      service: "ai_event_processor"
      action: "analyze_emotion"
      depends_on: ["process_content"]
      parallel: true
    - name: "update_analytics"
      service: "analytics_service"
      action: "update_user_metrics"
      depends_on: ["process_content"]
      parallel: true
  rollback_steps:
    - name: "delete_journal_entry"
      service: "content_service"
      action: "delete_entry"
    - name: "revert_analytics"
      service: "analytics_service" 
      action: "revert_metrics"
```

**Crisis Intervention Workflow Template:**
```yaml
crisis_intervention_workflow:
  priority: "CRITICAL"
  timeout: 30  # seconds
  steps:
    - name: "assess_risk"
      service: "ai_event_processor"
      action: "assess_crisis_level"
      required: true
    - name: "notify_emergency_contacts"
      service: "notification_service"
      action: "send_emergency_alert"
      parallel: true
    - name: "connect_professional"
      service: "community_service"
      action: "connect_crisis_counselor"
      parallel: true
    - name: "log_intervention"
      service: "audit_service"
      action: "log_crisis_event"
      parallel: true
```
