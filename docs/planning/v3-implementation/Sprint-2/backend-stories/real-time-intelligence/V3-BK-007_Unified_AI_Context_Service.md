# Story V3-BK-007: Unified AI Context Service
**Epic**: Cross-Service Intelligence  
**Priority**: P0 | **Points**: 10 | **Assignee**: Mid Dev 1

## Story Description
Create a unified AI context service that manages global user AI profiles, coordinates cross-feature learning, implements predictive personalization context, and enables cultural adaptation context sharing across all services.

## Current State Analysis

### Existing Infrastructure
- ✅ Action Orchestrator service foundation
- ✅ Enhanced event bus with cross-service capabilities
- ✅ Individual service AI context (partial)
- ✅ Cultural intelligence schemas

### Current Gaps
- ❌ No unified AI context across services
- ❌ No global user AI profile management
- ❌ No cross-feature learning coordination
- ❌ No predictive personalization context
- ❌ No cultural adaptation context sharing

## Acceptance Criteria

### 🎯 Primary Acceptance Criteria
- [ ] **Global user AI profile management** that aggregates intelligence from all services
- [ ] **Cross-feature learning coordination** that enables services to learn from each other
- [ ] **Predictive personalization context** that anticipates user needs
- [ ] **Cultural adaptation context sharing** that ensures culturally-aware responses

### 🔍 Technical Acceptance Criteria
- [ ] AI context retrieval latency <100ms for 95% of requests
- [ ] Context synchronization across services <200ms
- [ ] Support for 25+ languages and 11+ cultural regions
- [ ] Context data integrity 99.9% across service boundaries
- [ ] Predictive accuracy >80% for user behavior patterns

### 📊 Performance Acceptance Criteria
- [ ] Handle 10,000+ context updates per minute
- [ ] Context storage efficiency <100MB per active user
- [ ] Cross-service context sharing <50ms latency
- [ ] Learning algorithm convergence within 24h for new patterns

## Detailed Implementation Plan

### Task 1: AI Context Data Model (2h)
**Objective**: Design comprehensive AI context data model and storage architecture

#### Implementation Steps
1. **Unified AI Context Schema**
   ```python
   # File: backend/services/unified_ai_context/src/models/context.py
   class UserAIContext(BaseModel):
       user_id: str
       version: int = Field(default=1)
       last_updated: datetime = Field(default_factory=datetime.utcnow)
       
       # Service-Specific Contexts
       mood_context: MoodAIContext
       journal_context: JournalAIContext
       voice_context: VoiceAIContext
       chat_context: ChatAIContext
       
       # Cross-Service Intelligence
       behavioral_patterns: Dict[str, BehavioralPattern]
       emotional_profile: EmotionalProfile
       learning_preferences: LearningPreferences
       cultural_profile: CulturalProfile
       
       # Predictive Context
       predicted_needs: List[PredictedNeed]
       intervention_triggers: List[InterventionTrigger]
       personalization_weights: Dict[str, float]
       
   class BehavioralPattern(BaseModel):
       pattern_id: str
       pattern_type: str  # daily_routine, interaction_style, response_preference
       confidence: float = Field(ge=0.0, le=1.0)
       evidence_count: int
       last_observed: datetime
       cultural_adaptations: Dict[str, Any]
   ```

2. **Context Storage Architecture**
   ```python
   class AIContextStore:
       def __init__(self):
           self.redis_client = Redis()  # Fast access cache
           self.postgres_client = PostgreSQLClient()  # Persistent storage
           self.vector_store = ChromaDB()  # Similarity search
           
       async def store_context(self, user_id: str, context: UserAIContext):
           # Store in Redis for fast access
           await self.redis_client.setex(
               f"ai_context:{user_id}",
               3600,  # 1 hour TTL
               context.json()
           )
           
           # Store in PostgreSQL for persistence
           await self.postgres_client.upsert_context(user_id, context)
           
           # Store embeddings for similarity search
           await self.vector_store.store_context_embeddings(user_id, context)
   ```

3. **Context Versioning and History**
   ```python
   class ContextVersionManager:
       async def create_context_snapshot(self, user_id: str, reason: str):
           current_context = await self.get_current_context(user_id)
           snapshot = ContextSnapshot(
               user_id=user_id,
               version=current_context.version,
               context_data=current_context,
               snapshot_reason=reason,
               created_at=datetime.utcnow()
           )
           await self.store_snapshot(snapshot)
   ```

#### Deliverables
- Comprehensive AI context data models
- Multi-layer context storage architecture
- Context versioning and history system

### Task 2: Cross-Service Context Sharing (3h)
**Objective**: Implement real-time context sharing and synchronization across services

#### Implementation Steps
1. **Context Synchronization Service**
   ```python
   # File: backend/services/unified_ai_context/src/sync/context_sync.py
   class ContextSynchronizer:
       def __init__(self):
           self.event_bus = get_enhanced_event_bus()
           self.context_store = AIContextStore()
           self.service_clients = ServiceClientManager()
           
       async def sync_context_update(self, user_id: str, source_service: str, update_data: dict):
           # Get current context
           current_context = await self.context_store.get_context(user_id)
           
           # Apply update from source service
           updated_context = await self.apply_service_update(
               current_context, source_service, update_data
           )
           
           # Store updated context
           await self.context_store.store_context(user_id, updated_context)
           
           # Notify other services of context change
           await self.broadcast_context_update(user_id, updated_context, source_service)
   ```

2. **Service Integration Adapters**
   ```python
   class ServiceContextAdapter:
       """Adapts service-specific context to unified format"""
       
       async def mood_service_adapter(self, mood_data: dict) -> MoodAIContext:
           return MoodAIContext(
               current_mood_trend=mood_data.get("trend"),
               emotional_stability=mood_data.get("stability"),
               mood_triggers=mood_data.get("triggers", []),
               cultural_mood_expression=mood_data.get("cultural_context")
           )
       
       async def journal_service_adapter(self, journal_data: dict) -> JournalAIContext:
           return JournalAIContext(
               writing_patterns=journal_data.get("patterns"),
               emotional_themes=journal_data.get("themes"),
               language_preferences=journal_data.get("language_prefs"),
               cultural_expression_style=journal_data.get("cultural_style")
           )
   ```

3. **Context Event Processing**
   ```python
   @context_service.subscribe("mood_entry_created")
   async def handle_mood_context_update(event: Event):
       mood_data = event.data
       user_id = event.user_id
       
       # Extract AI context from mood data
       mood_context = await service_adapter.mood_service_adapter(mood_data)
       
       # Update unified context
       await context_sync.sync_context_update(user_id, "mood_service", mood_context)
   
   @context_service.subscribe("journal_entry_created")
   async def handle_journal_context_update(event: Event):
       journal_data = event.data
       user_id = event.user_id
       
       # Extract AI context from journal data
       journal_context = await service_adapter.journal_service_adapter(journal_data)
       
       # Update unified context
       await context_sync.sync_context_update(user_id, "journal_service", journal_context)
   ```

#### Deliverables
- Context synchronization service
- Service integration adapters
- Real-time context event processing

### Task 3: Predictive Personalization (3h)
**Objective**: Implement predictive personalization based on unified AI context

#### Implementation Steps
1. **Behavioral Pattern Analysis**
   ```python
   # File: backend/services/unified_ai_context/src/prediction/pattern_analyzer.py
   class BehavioralPatternAnalyzer:
       def __init__(self):
           self.pattern_models = PatternModelManager()
           self.cultural_adapter = CulturalPatternAdapter()
           
       async def analyze_user_patterns(self, user_context: UserAIContext) -> List[BehavioralPattern]:
           patterns = []
           
           # Analyze daily routine patterns
           daily_patterns = await self.analyze_daily_patterns(user_context)
           patterns.extend(daily_patterns)
           
           # Analyze interaction style patterns
           interaction_patterns = await self.analyze_interaction_patterns(user_context)
           patterns.extend(interaction_patterns)
           
           # Analyze cultural behavior patterns
           cultural_patterns = await self.cultural_adapter.analyze_cultural_patterns(
               user_context, user_context.cultural_profile
           )
           patterns.extend(cultural_patterns)
           
           return patterns
   ```

2. **Predictive Need Detection**
   ```python
   class PredictiveNeedDetector:
       async def predict_user_needs(self, user_context: UserAIContext) -> List[PredictedNeed]:
           predictions = []
           
           # Predict emotional support needs
           emotional_needs = await self.predict_emotional_needs(user_context)
           predictions.extend(emotional_needs)
           
           # Predict content preferences
           content_needs = await self.predict_content_preferences(user_context)
           predictions.extend(content_needs)
           
           # Predict interaction timing
           timing_needs = await self.predict_optimal_timing(user_context)
           predictions.extend(timing_needs)
           
           return predictions
   
   class PredictedNeed(BaseModel):
       need_type: str  # emotional_support, content_suggestion, interaction_timing
       description: str
       confidence: float = Field(ge=0.0, le=1.0)
       urgency: float = Field(ge=0.0, le=1.0)
       cultural_adaptations: Dict[str, Any]
       predicted_for: datetime
       expires_at: datetime
   ```

3. **Personalization Weight Calculator**
   ```python
   class PersonalizationWeightCalculator:
       async def calculate_personalization_weights(self, user_context: UserAIContext) -> Dict[str, float]:
           weights = {}
           
           # Calculate mood sensitivity weight
           weights["mood_sensitivity"] = await self.calculate_mood_weight(user_context)
           
           # Calculate cultural adaptation weight
           weights["cultural_adaptation"] = await self.calculate_cultural_weight(user_context)
           
           # Calculate voice interaction preference weight
           weights["voice_preference"] = await self.calculate_voice_weight(user_context)
           
           # Calculate proactive assistance weight
           weights["proactive_assistance"] = await self.calculate_proactive_weight(user_context)
           
           return weights
   ```

#### Deliverables
- Behavioral pattern analysis system
- Predictive need detection algorithms
- Personalization weight calculation

### Task 4: Cultural Adaptation Context (2h)
**Objective**: Implement cultural intelligence context sharing across services

#### Implementation Steps
1. **Cultural Profile Management**
   ```python
   # File: backend/services/unified_ai_context/src/cultural/profile_manager.py
   class CulturalProfileManager:
       def __init__(self):
           self.cultural_models = CulturalModelManager()
           self.adaptation_engine = CulturalAdaptationEngine()
           
       async def build_cultural_profile(self, user_context: UserAIContext) -> CulturalProfile:
           return CulturalProfile(
               primary_culture=await self.detect_primary_culture(user_context),
               secondary_cultures=await self.detect_secondary_cultures(user_context),
               language_preferences=await self.analyze_language_preferences(user_context),
               communication_style=await self.analyze_communication_style(user_context),
               cultural_values=await self.extract_cultural_values(user_context),
               adaptation_preferences=await self.determine_adaptation_preferences(user_context)
           )
   ```

2. **Cultural Context Sharing**
   ```python
   class CulturalContextSharer:
       async def share_cultural_context(self, user_id: str, target_service: str):
           user_context = await self.context_store.get_context(user_id)
           cultural_profile = user_context.cultural_profile
           
           # Adapt cultural context for target service
           adapted_context = await self.adaptation_engine.adapt_for_service(
               cultural_profile, target_service
           )
           
           # Send cultural context to service
           await self.service_clients.send_cultural_context(
               target_service, user_id, adapted_context
           )
   ```

3. **Cultural Intelligence Updates**
   ```python
   @context_service.subscribe("cultural_intelligence_update")
   async def handle_cultural_intelligence_update(event: Event):
       cultural_data = event.data
       user_id = event.user_id
       
       # Update cultural profile
       user_context = await context_store.get_context(user_id)
       updated_profile = await cultural_manager.update_cultural_profile(
           user_context.cultural_profile, cultural_data
       )
       
       # Update unified context
       user_context.cultural_profile = updated_profile
       await context_store.store_context(user_id, user_context)
       
       # Share updated cultural context
       await cultural_sharer.broadcast_cultural_update(user_id, updated_profile)
   ```

#### Deliverables
- Cultural profile management system
- Cultural context sharing mechanisms
- Cultural intelligence update processing

### Task 5: API Integration and Testing (3h)
**Objective**: Create APIs for context access and comprehensive testing

#### Implementation Steps
1. **Context API Endpoints**
   ```python
   # File: backend/services/unified_ai_context/src/api/endpoints.py
   @router.get("/context/{user_id}")
   async def get_user_context(user_id: str) -> UserAIContext:
       """Get unified AI context for user"""
       return await context_store.get_context(user_id)
   
   @router.post("/context/{user_id}/update")
   async def update_user_context(user_id: str, update: ContextUpdate):
       """Update specific aspects of user context"""
       await context_sync.sync_context_update(
           user_id, update.source_service, update.data
       )
       return {"status": "updated"}
   
   @router.get("/context/{user_id}/predictions")
   async def get_predictions(user_id: str) -> List[PredictedNeed]:
       """Get predictive insights for user"""
       context = await context_store.get_context(user_id)
       return await need_detector.predict_user_needs(context)
   ```

2. **Context Service Integration Tests**
   ```python
   class TestUnifiedAIContext:
       async def test_cross_service_context_sync(self):
           # Test context updates from multiple services
           # Verify context synchronization
           # Check context integrity
           
       async def test_predictive_personalization(self):
           # Test behavioral pattern detection
           # Verify prediction accuracy
           # Check cultural adaptations
           
       async def test_cultural_context_sharing(self):
           # Test cultural profile management
           # Verify cultural adaptation
           # Check cross-service sharing
   ```

3. **Performance and Load Testing**
   ```python
   class ContextPerformanceTests:
       async def test_context_retrieval_latency(self):
           # Test <100ms context retrieval
           # Measure under concurrent load
           # Verify caching effectiveness
           
       async def test_context_synchronization_speed(self):
           # Test <200ms cross-service sync
           # Measure update propagation time
           # Check consistency guarantees
   ```

#### Deliverables
- Comprehensive context API
- Integration test suite
- Performance validation tests

## Integration Points

### Service Dependencies
1. **All Core Services**: Mood, Journal, Voice, Chat services for context inputs
2. **AI Event Processor**: For AI-driven context analysis
3. **Cultural Intelligence Service**: For cultural adaptation
4. **Action Orchestrator**: For context-driven action coordination

### External Dependencies
1. **Redis Cluster**: Fast context caching
2. **PostgreSQL**: Persistent context storage
3. **ChromaDB**: Vector similarity search for context patterns
4. **NATS JetStream**: Cross-service context event streaming

## API Specifications

### Context Management APIs
```python
# Context Retrieval
GET /api/v3/context/{user_id}
GET /api/v3/context/{user_id}/patterns
GET /api/v3/context/{user_id}/predictions
GET /api/v3/context/{user_id}/cultural

# Context Updates
POST /api/v3/context/{user_id}/update
PUT /api/v3/context/{user_id}/patterns
POST /api/v3/context/{user_id}/cultural/update

# Context Sharing
POST /api/v3/context/{user_id}/share/{service}
GET /api/v3/context/{user_id}/shared-with

# Context Analytics
GET /api/v3/context/{user_id}/analytics
GET /api/v3/context/{user_id}/learning-progress
```

## Monitoring and Metrics

### Context Service Metrics
```python
context_metrics = {
    "context_retrieval_latency": Histogram("context_retrieval_seconds"),
    "context_sync_duration": Histogram("context_sync_seconds"),
    "prediction_accuracy": Gauge("context_prediction_accuracy"),
    "cultural_adaptation_success": Counter("cultural_adaptation_success_total"),
    "context_cache_hit_rate": Gauge("context_cache_hit_ratio"),
    "cross_service_sync_errors": Counter("context_sync_errors_total")
}
```

### Health Checks
```python
class ContextHealthChecker:
    async def check_context_service_health(self):
        return {
            "context_store_status": await self.check_context_store(),
            "sync_service_status": await self.check_sync_service(),
            "prediction_service_status": await self.check_prediction_service(),
            "cultural_service_status": await self.check_cultural_service(),
            "average_context_latency": await self.measure_context_latency()
        }
```

## Risk Mitigation

### High-Priority Risks
1. **Context Data Volume**
   - Risk: Context data grows too large per user
   - Mitigation: Context pruning, efficient storage, archiving strategies

2. **Context Consistency**
   - Risk: Context becomes inconsistent across services
   - Mitigation: ACID transactions, conflict resolution, versioning

3. **Prediction Accuracy**
   - Risk: Predictive models not accurate enough
   - Mitigation: Continuous learning, feedback loops, model validation

### Fallback Strategies
1. **Context Store Unavailable**: Use service-local context
2. **Sync Service Down**: Queue updates for later synchronization
3. **Prediction Service Failed**: Fall back to rule-based personalization

## Definition of Done

### Technical Completion
- [ ] Unified AI context service operational
- [ ] Cross-service context sharing working
- [ ] Predictive personalization functional
- [ ] Cultural adaptation context active
- [ ] All tests passing (>90% coverage)

### Performance Validation
- [ ] <100ms context retrieval latency
- [ ] <200ms cross-service synchronization
- [ ] >80% prediction accuracy for user patterns
- [ ] Cultural adaptation working for 11+ regions

### Integration Validation
- [ ] All services using unified context
- [ ] Context-driven personalization working
- [ ] Cultural adaptations applied correctly
- [ ] Real-time context updates functional

---

## Implementation Files Structure

```
backend/services/unified_ai_context/
├── main.py                       # FastAPI application
├── src/
│   ├── core/
│   │   ├── context_manager.py    # Main context management
│   │   └── sync_coordinator.py   # Cross-service synchronization
│   ├── models/
│   │   ├── context.py           # Context data models
│   │   ├── patterns.py          # Behavioral pattern models
│   │   └── predictions.py       # Predictive models
│   ├── services/
│   │   ├── context_store.py     # Context storage service
│   │   ├── pattern_analyzer.py  # Pattern analysis service
│   │   ├── prediction_engine.py # Predictive personalization
│   │   └── cultural_manager.py  # Cultural context management
│   ├── sync/
│   │   ├── context_sync.py      # Context synchronization
│   │   └── service_adapters.py  # Service integration adapters
│   └── api/
│       ├── endpoints.py         # REST API endpoints
│       └── models.py           # API request/response models
├── config/
│   ├── patterns.yaml           # Pattern detection configuration
│   └── cultural.yaml           # Cultural adaptation settings
└── tests/
    ├── unit/                   # Unit tests
    ├── integration/            # Integration tests
    └── performance/            # Performance tests
```

This unified AI context service enables intelligent, culturally-aware, personalized experiences across all MantraPath services.
