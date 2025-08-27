# Story V3-BK-008: Proactive Assistance Engine
**Epic**: Cross-Service Intelligence  
**Priority**: P0 | **Points**: 8 | **Assignee**: Mid Dev 2

## Story Description
Implement a proactive assistance engine that performs early intervention detection, optimal timing prediction for assistance, contextual help trigger system, and cultural sensitivity in proactive assistance based on real-time analysis across all platform interactions.

## Current State Analysis

### Existing Infrastructure
- ✅ Unified AI Context Service (from V3-BK-007) - IMPLEMENTED
- ✅ AI Event Processing Pipeline (from V3-BK-005) - IMPLEMENTED  
- ✅ Enhanced event bus for real-time processing - IMPLEMENTED
- ✅ Cultural intelligence schemas and processing - IMPLEMENTED
- ✅ Predictive Intervention Engine - PARTIALLY IMPLEMENTED (in ai_event_processor)
- ✅ Crisis Detection System - IMPLEMENTED (in ML service and chatbot)
- ✅ Mood Analysis and Risk Assessment - IMPLEMENTED

### Current Gaps - ANALYSIS UPDATE
- ❌ **No dedicated Proactive Assistance Service** - Main gap identified
- ❌ **No optimal timing prediction for assistance** - Timing logic exists but not comprehensive
- ❌ **No contextual help trigger system** - No help content matching engine
- ❌ **No cultural sensitivity in proactive assistance** - Cultural adaptation exists but not for assistance

### Available Foundation Components
- ✅ **PredictiveInterventionEngine**: Behavioral analysis, risk assessment, recommendations
- ✅ **Crisis Detection**: Multiple services (ML, chatbot) have crisis detection capabilities  
- ✅ **Mood Analysis**: Real-time mood pattern analysis and trend detection
- ✅ **Cultural Intelligence**: Cultural adaptation for content and interactions
- ✅ **AI Context Store**: Cross-service user context aggregation
- ✅ **Event System**: Real-time event publishing and consumption

### Implementation Strategy
Rather than building from scratch, we need to:
1. **Create dedicated Proactive Assistance Service** that orchestrates existing components
2. **Enhance timing prediction** using existing behavioral data from AI Context Store
3. **Build contextual help system** with cultural adaptation
4. **Integrate existing crisis detection** into proactive assistance workflow

## Acceptance Criteria

### 🎯 Primary Acceptance Criteria
- [ ] **Early intervention detection** that identifies when users need support before they ask
- [ ] **Optimal timing prediction** for assistance that maximizes helpfulness and minimizes intrusion
- [ ] **Contextual help trigger system** that provides relevant assistance based on user context
- [ ] **Cultural sensitivity** in proactive assistance that respects cultural norms and preferences

### 🔍 Technical Acceptance Criteria
- [ ] Intervention detection accuracy >85% for critical situations
- [ ] Timing prediction accuracy >75% for user receptiveness
- [ ] False positive rate <10% for proactive interventions
- [ ] Cultural adaptation accuracy >90% for supported regions
- [ ] Response time <500ms for assistance trigger evaluation

### 📊 Performance Acceptance Criteria
- [ ] Process 1,000+ assistance evaluations per minute
- [ ] Support cultural sensitivity for 11+ cultural regions
- [ ] Intervention detection latency <200ms
- [ ] Context analysis for assistance <300ms

## Detailed Implementation Plan

### Task 1: Intervention Detection Algorithms (3h)
**Objective**: Implement algorithms to detect when users need early intervention

#### Implementation Steps
1. **Crisis Detection System**
   ```python
   # File: backend/services/proactive_assistance/src/detection/crisis_detector.py
   class CrisisDetector:
       def __init__(self):
           self.safety_models = SafetyModelManager()
           self.mood_analyzer = MoodTrendAnalyzer()
           self.pattern_detector = BehavioralPatternDetector()
           
       async def detect_crisis_indicators(self, user_context: UserAIContext) -> CrisisAssessment:
           # Analyze recent mood trends
           mood_risk = await self.assess_mood_risk(user_context)
           
           # Check for safety concerns in journal/chat
           safety_risk = await self.assess_safety_risk(user_context)
           
           # Analyze behavioral pattern changes
           behavioral_risk = await self.assess_behavioral_risk(user_context)
           
           # Cultural context for crisis interpretation
           cultural_context = await self.get_cultural_crisis_context(user_context)
           
           return CrisisAssessment(
               overall_risk=max(mood_risk, safety_risk, behavioral_risk),
               mood_risk=mood_risk,
               safety_risk=safety_risk,
               behavioral_risk=behavioral_risk,
               cultural_considerations=cultural_context,
               intervention_urgency=self.calculate_urgency(mood_risk, safety_risk, behavioral_risk),
               recommended_actions=await self.recommend_interventions(user_context)
           )
   ```

2. **Mood Trend Analysis**
   ```python
   class MoodTrendAnalyzer:
       async def assess_mood_risk(self, user_context: UserAIContext) -> float:
           mood_history = user_context.mood_context.mood_history[-14:]  # Last 2 weeks
           
           # Calculate trend indicators
           trend_slope = self.calculate_mood_slope(mood_history)
           volatility = self.calculate_mood_volatility(mood_history)
           low_point_duration = self.calculate_low_mood_duration(mood_history)
           
           # Cultural adaptation for mood interpretation
           cultural_adjustments = await self.get_cultural_mood_adjustments(
               user_context.cultural_profile
           )
           
           risk_score = self.calculate_mood_risk_score(
               trend_slope, volatility, low_point_duration, cultural_adjustments
           )
           
           return min(max(risk_score, 0.0), 1.0)
   ```

3. **Behavioral Pattern Change Detection**
   ```python
   class BehavioralPatternDetector:
       async def assess_behavioral_risk(self, user_context: UserAIContext) -> float:
           current_patterns = user_context.behavioral_patterns
           historical_patterns = await self.get_historical_patterns(user_context.user_id)
           
           # Detect significant pattern changes
           pattern_changes = []
           for pattern_type, current_pattern in current_patterns.items():
               historical_pattern = historical_patterns.get(pattern_type)
               if historical_pattern:
                   change_magnitude = self.calculate_pattern_change(
                       current_pattern, historical_pattern
                   )
                   pattern_changes.append((pattern_type, change_magnitude))
           
           # Consider cultural norms for behavioral changes
           cultural_norms = await self.get_cultural_behavioral_norms(
               user_context.cultural_profile
           )
           
           return self.evaluate_behavioral_risk(pattern_changes, cultural_norms)
   ```

#### Deliverables
- Crisis detection algorithms
- Mood trend analysis system
- Behavioral pattern change detection

### Task 2: Timing Prediction System (2h)
**Objective**: Predict optimal timing for proactive assistance

#### Implementation Steps
1. **User Receptiveness Prediction**
   ```python
   # File: backend/services/proactive_assistance/src/timing/timing_predictor.py
   class TimingPredictor:
       def __init__(self):
           self.activity_analyzer = UserActivityAnalyzer()
           self.attention_predictor = AttentionPredictor()
           self.cultural_timing = CulturalTimingAdapter()
           
       async def predict_optimal_timing(self, user_context: UserAIContext) -> TimingPrediction:
           # Analyze current user activity
           activity_state = await self.activity_analyzer.get_current_activity(user_context)
           
           # Predict user attention and receptiveness
           attention_score = await self.attention_predictor.predict_attention(user_context)
           
           # Consider cultural timing preferences
           cultural_timing = await self.cultural_timing.get_timing_preferences(
               user_context.cultural_profile
           )
           
           # Calculate optimal timing
           optimal_time = await self.calculate_optimal_intervention_time(
               activity_state, attention_score, cultural_timing
           )
           
           return TimingPrediction(
               optimal_time=optimal_time,
               confidence=self.calculate_timing_confidence(activity_state, attention_score),
               cultural_considerations=cultural_timing,
               user_receptiveness_score=attention_score
           )
   ```

2. **Activity State Analysis**
   ```python
   class UserActivityAnalyzer:
       async def get_current_activity(self, user_context: UserAIContext) -> ActivityState:
           # Analyze recent platform interactions
           recent_interactions = await self.get_recent_interactions(user_context.user_id)
           
           # Determine current engagement level
           engagement_level = self.calculate_engagement_level(recent_interactions)
           
           # Detect interaction patterns
           interaction_patterns = await self.detect_interaction_patterns(user_context)
           
           # Consider timezone and cultural time preferences
           local_time_context = await self.get_local_time_context(user_context)
           
           return ActivityState(
               engagement_level=engagement_level,
               last_interaction_time=recent_interactions[-1].timestamp if recent_interactions else None,
               interaction_frequency=len(recent_interactions),
               patterns=interaction_patterns,
               local_time_context=local_time_context
           )
   ```

3. **Cultural Timing Adaptation**
   ```python
   class CulturalTimingAdapter:
       async def get_timing_preferences(self, cultural_profile: CulturalProfile) -> CulturalTimingPreferences:
           # Get cultural norms for timing
           timing_norms = await self.get_cultural_timing_norms(cultural_profile.primary_culture)
           
           # Adapt for communication style
           communication_adaptations = await self.adapt_for_communication_style(
               cultural_profile.communication_style
           )
           
           return CulturalTimingPreferences(
               preferred_interaction_times=timing_norms.preferred_times,
               avoided_times=timing_norms.avoided_times,
               communication_urgency_thresholds=communication_adaptations.urgency_thresholds,
               cultural_sensitivity_factors=timing_norms.sensitivity_factors
           )
   ```

#### Deliverables
- User receptiveness prediction system
- Activity state analysis
- Cultural timing adaptation

### Task 3: Contextual Trigger Engine (2h)
**Objective**: Create contextual help trigger system based on user context

#### Implementation Steps
1. **Context-Aware Trigger System**
   ```python
   # File: backend/services/proactive_assistance/src/triggers/trigger_engine.py
   class ContextualTriggerEngine:
       def __init__(self):
           self.context_analyzer = ContextAnalyzer()
           self.help_matcher = HelpMatcher()
           self.cultural_adapter = CulturalHelpAdapter()
           
       async def evaluate_assistance_triggers(self, user_context: UserAIContext) -> List[AssistanceTrigger]:
           triggers = []
           
           # Analyze current context for help opportunities
           context_analysis = await self.context_analyzer.analyze_help_context(user_context)
           
           # Match context to available help resources
           help_matches = await self.help_matcher.find_relevant_help(context_analysis)
           
           # Adapt help for cultural context
           culturally_adapted_help = await self.cultural_adapter.adapt_help_content(
               help_matches, user_context.cultural_profile
           )
           
           # Create assistance triggers
           for help_item in culturally_adapted_help:
               trigger = AssistanceTrigger(
                   trigger_id=str(uuid.uuid4()),
                   trigger_type=help_item.help_type,
                   context_relevance=help_item.relevance_score,
                   suggested_action=help_item.suggested_action,
                   content=help_item.content,
                   cultural_adaptations=help_item.cultural_adaptations,
                   urgency=help_item.urgency
               )
               triggers.append(trigger)
           
           return sorted(triggers, key=lambda x: x.urgency, reverse=True)
   ```

2. **Help Content Matching**
   ```python
   class HelpMatcher:
       def __init__(self):
           self.help_database = HelpContentDatabase()
           self.context_embeddings = ContextEmbeddingService()
           
       async def find_relevant_help(self, context_analysis: ContextAnalysis) -> List[HelpMatch]:
           # Convert context to embeddings
           context_embedding = await self.context_embeddings.embed_context(context_analysis)
           
           # Search for similar help content
           similar_help = await self.help_database.semantic_search(
               context_embedding, limit=10
           )
           
           # Score relevance
           help_matches = []
           for help_content in similar_help:
               relevance_score = await self.calculate_relevance_score(
                   context_analysis, help_content
               )
               
               if relevance_score > 0.6:  # Minimum relevance threshold
                   help_matches.append(HelpMatch(
                       content=help_content,
                       relevance_score=relevance_score,
                       help_type=help_content.type,
                       suggested_action=help_content.suggested_action
                   ))
           
           return help_matches
   ```

3. **Trigger Evaluation and Filtering**
   ```python
   class TriggerEvaluator:
       async def evaluate_trigger_appropriateness(
           self, 
           trigger: AssistanceTrigger, 
           user_context: UserAIContext,
           timing_prediction: TimingPrediction
       ) -> TriggerEvaluation:
           # Check if user is receptive to this type of help
           receptiveness = await self.check_user_receptiveness(trigger, user_context)
           
           # Verify timing is appropriate
           timing_appropriate = timing_prediction.optimal_time <= datetime.utcnow()
           
           # Cultural appropriateness check
           culturally_appropriate = await self.check_cultural_appropriateness(
               trigger, user_context.cultural_profile
           )
           
           # Calculate overall appropriateness score
           appropriateness_score = self.calculate_appropriateness_score(
               receptiveness, timing_appropriate, culturally_appropriate
           )
           
           return TriggerEvaluation(
               should_trigger=appropriateness_score > 0.7,
               appropriateness_score=appropriateness_score,
               reasons=self.get_evaluation_reasons(receptiveness, timing_appropriate, culturally_appropriate)
           )
   ```

#### Deliverables
- Contextual trigger engine
- Help content matching system
- Trigger evaluation and filtering

### Task 4: Cultural Sensitivity Integration (1h)
**Objective**: Ensure all proactive assistance respects cultural norms and preferences

#### Implementation Steps
1. **Cultural Appropriateness Checker**
   ```python
   # File: backend/services/proactive_assistance/src/cultural/cultural_checker.py
   class CulturalAppropriatenessChecker:
       def __init__(self):
           self.cultural_norms = CulturalNormsDatabase()
           self.adaptation_engine = CulturalAdaptationEngine()
           
       async def check_cultural_appropriateness(
           self, 
           assistance_trigger: AssistanceTrigger,
           cultural_profile: CulturalProfile
       ) -> CulturalAppropriatenessResult:
           # Get cultural norms for this type of assistance
           relevant_norms = await self.cultural_norms.get_assistance_norms(
               cultural_profile.primary_culture,
               assistance_trigger.trigger_type
           )
           
           # Check if assistance type is culturally appropriate
           type_appropriate = self.check_assistance_type_appropriateness(
               assistance_trigger.trigger_type, relevant_norms
           )
           
           # Check if timing is culturally appropriate
           timing_appropriate = self.check_timing_appropriateness(
               assistance_trigger, relevant_norms, cultural_profile
           )
           
           # Check if content is culturally sensitive
           content_appropriate = await self.check_content_sensitivity(
               assistance_trigger.content, cultural_profile
           )
           
           return CulturalAppropriatenessResult(
               is_appropriate=type_appropriate and timing_appropriate and content_appropriate,
               adaptations_needed=self.identify_needed_adaptations(
                   assistance_trigger, relevant_norms, cultural_profile
               ),
               cultural_considerations=relevant_norms
           )
   ```

2. **Cultural Help Content Adaptation**
   ```python
   class CulturalHelpAdapter:
       async def adapt_help_content(
           self, 
           help_matches: List[HelpMatch],
           cultural_profile: CulturalProfile
       ) -> List[CulturallyAdaptedHelp]:
           adapted_help = []
           
           for help_match in help_matches:
               # Adapt content for cultural context
               adapted_content = await self.adapt_content_for_culture(
                   help_match.content, cultural_profile
               )
               
               # Adapt suggested actions for cultural norms
               adapted_actions = await self.adapt_actions_for_culture(
                   help_match.suggested_action, cultural_profile
               )
               
               # Add cultural sensitivity warnings if needed
               cultural_warnings = await self.get_cultural_warnings(
                   help_match, cultural_profile
               )
               
               adapted_help.append(CulturallyAdaptedHelp(
                   original_help=help_match,
                   adapted_content=adapted_content,
                   adapted_actions=adapted_actions,
                   cultural_warnings=cultural_warnings,
                   cultural_confidence=self.calculate_cultural_confidence(
                       cultural_profile, help_match
                   )
               ))
           
           return adapted_help
   ```

#### Deliverables
- Cultural appropriateness checking system
- Cultural help content adaptation
- Cultural sensitivity validation

### Task 5: Testing and Integration (2h)
**Objective**: Comprehensive testing and integration with existing services

#### Implementation Steps
1. **Assistance Engine Integration Tests**
   ```python
   class TestProactiveAssistanceEngine:
       async def test_end_to_end_assistance_flow(self):
           # Test complete flow: detection → timing → triggers → cultural check
           user_context = await self.create_test_user_context()
           
           # Test intervention detection
           crisis_assessment = await crisis_detector.detect_crisis_indicators(user_context)
           assert crisis_assessment.overall_risk > 0.5
           
           # Test timing prediction
           timing_prediction = await timing_predictor.predict_optimal_timing(user_context)
           assert timing_prediction.confidence > 0.7
           
           # Test trigger evaluation
           triggers = await trigger_engine.evaluate_assistance_triggers(user_context)
           assert len(triggers) > 0
           
           # Test cultural appropriateness
           for trigger in triggers:
               cultural_check = await cultural_checker.check_cultural_appropriateness(
                   trigger, user_context.cultural_profile
               )
               assert cultural_check.is_appropriate
       
       async def test_cultural_sensitivity_across_regions(self):
           # Test assistance appropriateness for different cultural contexts
           for cultural_region in SUPPORTED_CULTURAL_REGIONS:
               user_context = await self.create_test_user_context_for_culture(cultural_region)
               
               # Test that assistance is culturally appropriate
               triggers = await trigger_engine.evaluate_assistance_triggers(user_context)
               for trigger in triggers:
                   cultural_check = await cultural_checker.check_cultural_appropriateness(
                       trigger, user_context.cultural_profile
                   )
                   assert cultural_check.is_appropriate, f"Inappropriate for {cultural_region}"
   ```

2. **Performance Testing**
   ```python
   class ProactiveAssistancePerformanceTests:
       async def test_assistance_evaluation_latency(self):
           # Test that assistance evaluation completes within 500ms
           start_time = time.time()
           
           user_context = await self.create_test_user_context()
           await assistance_engine.evaluate_user_assistance_needs(user_context)
           
           evaluation_time = time.time() - start_time
           assert evaluation_time < 0.5, f"Evaluation took {evaluation_time}s, expected <0.5s"
       
       async def test_concurrent_assistance_evaluations(self):
           # Test handling 1000+ assistance evaluations per minute
           tasks = []
           for i in range(100):  # Simulate 100 concurrent evaluations
               user_context = await self.create_test_user_context()
               task = assistance_engine.evaluate_user_assistance_needs(user_context)
               tasks.append(task)
           
           results = await asyncio.gather(*tasks)
           assert len(results) == 100
   ```

3. **Event Integration Testing**
   ```python
   @assistance_engine.subscribe("mood_entry_created")
   async def test_mood_triggered_assistance(event: Event):
       # Test that mood entries trigger assistance evaluation
       user_id = event.user_id
       mood_data = event.data
       
       # Simulate assistance evaluation triggered by mood event
       user_context = await context_store.get_context(user_id)
       assistance_evaluation = await assistance_engine.evaluate_user_assistance_needs(user_context)
       
       # Verify assistance is provided if needed
       if assistance_evaluation.assistance_needed:
           await assistance_engine.provide_proactive_assistance(user_id, assistance_evaluation)
   ```

#### Deliverables
- Comprehensive test suite
- Performance validation
- Event integration testing

## Integration Points

### Service Dependencies
1. **Unified AI Context Service**: User context and behavioral patterns
2. **AI Event Processing Pipeline**: Real-time analysis triggers
3. **Cultural Intelligence Service**: Cultural norms and adaptations
4. **Notification Service**: Delivery of proactive assistance
5. **All Core Services**: Context inputs for assistance evaluation

### External Dependencies
1. **Help Content Database**: Contextual help resources
2. **Cultural Norms Database**: Cultural appropriateness guidelines
3. **Vector Search Engine**: Semantic help content matching
4. **NATS JetStream**: Real-time assistance event processing

## Proactive Assistance Event Channels

```python
class V3AssistanceChannels:
    """Proactive assistance event channels"""
    # Detection Events
    CRISIS_DETECTED = "assistance.crisis_detected"
    INTERVENTION_NEEDED = "assistance.intervention_needed"
    PATTERN_CHANGE_DETECTED = "assistance.pattern_change_detected"
    
    # Timing Events
    OPTIMAL_TIMING_IDENTIFIED = "assistance.optimal_timing_identified"
    USER_RECEPTIVE = "assistance.user_receptive"
    
    # Assistance Events
    ASSISTANCE_TRIGGERED = "assistance.triggered"
    ASSISTANCE_DELIVERED = "assistance.delivered"
    ASSISTANCE_ACCEPTED = "assistance.accepted"
    ASSISTANCE_DECLINED = "assistance.declined"
    
    # Cultural Events
    CULTURAL_ADAPTATION_APPLIED = "assistance.cultural_adaptation_applied"
    CULTURAL_SENSITIVITY_ALERT = "assistance.cultural_sensitivity_alert"
```

## Monitoring and Metrics

### Assistance Engine Metrics
```python
assistance_metrics = {
    "intervention_detection_accuracy": Gauge("assistance_intervention_accuracy"),
    "timing_prediction_accuracy": Gauge("assistance_timing_accuracy"),
    "assistance_acceptance_rate": Gauge("assistance_acceptance_rate"),
    "cultural_appropriateness_score": Gauge("assistance_cultural_appropriateness"),
    "false_positive_rate": Gauge("assistance_false_positive_rate"),
    "assistance_evaluation_latency": Histogram("assistance_evaluation_seconds")
}
```

## Risk Mitigation

### High-Priority Risks
1. **False Positive Interventions**
   - Risk: Too many inappropriate assistance offers
   - Mitigation: Conservative thresholds, user feedback learning

2. **Cultural Insensitivity**
   - Risk: Assistance that violates cultural norms
   - Mitigation: Cultural expert validation, extensive testing

3. **Privacy Concerns**
   - Risk: Users feel monitored or judged
   - Mitigation: Transparent communication, user control options

## Definition of Done

### Technical Completion
- [ ] Early intervention detection functional
- [ ] Optimal timing prediction working
- [ ] Contextual trigger system operational
- [ ] Cultural sensitivity integrated
- [ ] All tests passing (>85% coverage)

### Performance Validation
- [ ] >85% intervention detection accuracy
- [ ] >75% timing prediction accuracy
- [ ] <10% false positive rate
- [ ] <500ms assistance evaluation time

### Integration Validation
- [ ] Integrated with all core services
- [ ] Cultural adaptation working for 11+ regions
- [ ] Real-time assistance triggers functional
- [ ] User feedback collection working

---

## Implementation Files Structure

```
backend/services/proactive_assistance/
├── main.py                          # FastAPI application
├── src/
│   ├── core/
│   │   ├── assistance_engine.py     # Main assistance engine
│   │   └── evaluation_coordinator.py # Assistance evaluation coordination
│   ├── detection/
│   │   ├── crisis_detector.py       # Crisis detection algorithms
│   │   ├── mood_analyzer.py         # Mood trend analysis
│   │   └── pattern_detector.py      # Behavioral pattern analysis
│   ├── timing/
│   │   ├── timing_predictor.py      # Optimal timing prediction
│   │   ├── activity_analyzer.py     # User activity analysis
│   │   └── cultural_timing.py       # Cultural timing adaptation
│   ├── triggers/
│   │   ├── trigger_engine.py        # Contextual trigger system
│   │   ├── help_matcher.py          # Help content matching
│   │   └── trigger_evaluator.py     # Trigger appropriateness evaluation
│   ├── cultural/
│   │   ├── cultural_checker.py      # Cultural appropriateness checking
│   │   └── cultural_adapter.py      # Cultural content adaptation
│   └── api/
│       ├── endpoints.py             # REST API endpoints
│       └── models.py                # API request/response models
├── config/
│   ├── assistance.yaml             # Assistance configuration
│   ├── cultural_norms.yaml         # Cultural appropriateness rules
│   └── triggers.yaml               # Trigger configuration
└── tests/
    ├── unit/                       # Unit tests
    ├── integration/                # Integration tests
    └── cultural/                   # Cultural sensitivity tests
```

This proactive assistance engine enables culturally-sensitive, contextually-appropriate support that anticipates user needs while respecting cultural boundaries and preferences.
