# MantraPath Data Models

This document defines the key data models used across the MantraPath platform, focusing on the structures that enable deep integration between services with the Mood Service as the central intelligence hub.

## 1. Core Models

### 1.1 User Model

The base user model that's consistent across all services:

```python
class User(BaseModel):
    """
    Core user model shared across all services
    """
    id: str  # UUID format
    email: str
    display_name: str
    created_at: datetime
    updated_at: datetime
    
    # Profile data
    profile_image_url: Optional[str]
    bio: Optional[str]
    timezone: str = "UTC"
    locale: str = "en-US"
    
    # Account status
    is_active: bool = True
    is_verified: bool = False
    last_active_at: Optional[datetime]
    
    # Privacy & security
    privacy_level: PrivacyLevel
    data_sharing_preferences: DataSharingPreferences
    
    # Cross-service settings
    notification_preferences: NotificationPreferences
    interface_preferences: InterfacePreferences
    
    class Config:
        orm_mode = True
```

### 1.2 Emotional State Model

The comprehensive representation of a user's emotional state:

```python
class EmotionalState(BaseModel):
    """
    Multi-dimensional emotional state representation
    """
    # Core affect dimensions
    valence: float  # -1.0 to 1.0 (negative to positive)
    arousal: float  # -1.0 to 1.0 (low to high energy)
    
    # Specific emotions with intensities (0.0 to 1.0)
    primary_emotions: Dict[str, float]  # {"joy": 0.8, "calm": 0.6}
    secondary_emotions: Dict[str, float]  # {"nostalgia": 0.3}
    
    # Overall emotional characteristics
    emotional_stability: float  # 0.0 to 1.0
    emotional_complexity: float  # 0.0 to 1.0
    emotional_clarity: float  # 0.0 to 1.0
    
    # Measurement metadata
    confidence: float  # 0.0 to 1.0
    sources: List[EmotionSource]
    timestamp: datetime
    
    # Contextual factors
    triggers: Optional[List[EmotionTrigger]]
    environmental_factors: Optional[Dict[str, Any]]
    
    def to_simple_state(self) -> Dict[str, Any]:
        """
        Returns simplified emotional state for services that don't need full detail
        """
        return {
            "valence": self.valence,
            "arousal": self.arousal,
            "primary_emotion": max(self.primary_emotions.items(), key=lambda x: x[1])[0],
            "intensity": max(self.primary_emotions.values()),
            "timestamp": self.timestamp.isoformat()
        }

class EmotionSource(BaseModel):
    """
    Source of emotional data
    """
    type: str  # "direct_report", "journal_analysis", "chat_inference", "voice_analysis"
    confidence: float  # 0.0 to 1.0
    service: str  # "mood_service", "journal_service", "chatbot_service"
    context_id: Optional[str]  # ID of specific content that generated this emotion

class EmotionTrigger(BaseModel):
    """
    Identified trigger for an emotion
    """
    type: str  # "event", "thought", "interaction", "environment"
    description: str
    confidence: float  # 0.0 to 1.0
```

### 1.3 User Context Model

The comprehensive user context maintained by the Mood Service:

```python
class UserContext(BaseModel):
    """
    Comprehensive user context aggregated from all platform services
    """
    user_id: str
    timestamp: datetime
    
    # Emotional state synthesis
    current_emotional_state: EmotionalState
    emotional_trajectory: EmotionalTrajectory
    emotional_volatility: float  # 0.0 to 1.0
    
    # Behavioral patterns
    interaction_patterns: InteractionPatterns
    activity_effectiveness: Dict[str, float]  # Activity type to effectiveness mapping
    engagement_trends: EngagementTrends
    
    # Social wellness
    social_connections_quality: float  # 0.0 to 1.0
    community_engagement_health: CommunityEngagementMetrics
    support_network_strength: float  # 0.0 to 1.0
    
    # Content and communication
    communication_style_preferences: CommunicationStyle
    content_consumption_patterns: ContentPatterns
    writing_patterns: WritingPatterns
    
    # Intervention history
    intervention_effectiveness_history: Dict[str, InterventionEffectiveness]
    preferred_intervention_types: List[str]
    crisis_risk_indicators: List[RiskIndicator]
    
    # Contextual factors
    environmental_factors: EnvironmentalContext
    temporal_patterns: TemporalPatterns
    life_context: LifeContext
    
    # Metadata
    context_quality: float  # 0.0 to 1.0
    context_sources: List[ContextSource]
    last_updated_by: str  # Service that last updated this context
    
    def get_for_service(self, service_name: str, access_level: AccessLevel) -> Dict[str, Any]:
        """
        Returns service-appropriate subset of context based on access level
        """
        # Implement access control and context filtering
        pass

class EmotionalTrajectory(BaseModel):
    """
    Pattern of emotional change over time
    """
    overall_trend: str  # "improving", "declining", "stable", "fluctuating"
    trend_confidence: float  # 0.0 to 1.0
    
    recent_changes: List[EmotionalChange]
    significant_shifts: List[EmotionalShift]
    cyclical_patterns: List[CyclicalPattern]
    
    forecast: Optional[EmotionalForecast]

class InteractionPatterns(BaseModel):
    """
    Cross-platform interaction patterns
    """
    # Communication patterns
    chatbot_interaction_frequency: float  # 0.0 to 1.0
    chatbot_session_quality: float  # 0.0 to 1.0
    voice_interaction_preference: float  # 0.0 to 1.0
    
    # Community engagement
    community_posting_frequency: float  # 0.0 to 1.0
    community_response_patterns: ResponsePatterns
    peer_interaction_quality: float  # 0.0 to 1.0
    
    # Content creation
    journal_writing_frequency: float  # 0.0 to 1.0
    journal_emotional_depth: float  # 0.0 to 1.0
    content_sharing_willingness: float  # 0.0 to 1.0
    
    # Platform navigation
    feature_usage_patterns: Dict[str, float]  # Feature name to usage frequency mapping
    session_engagement_quality: float  # 0.0 to 1.0
```

## 2. Mood Service Models

### 2.1 Mood Entry Model

Direct mood entries from users:

```python
class MoodEntry(BaseModel):
    """
    Direct mood entry from user
    """
    id: str  # UUID format
    user_id: str
    timestamp: datetime
    
    # Core affect ratings
    valence: float  # -1.0 to 1.0 (negative to positive)
    arousal: float  # -1.0 to 1.0 (low to high energy)
    
    # Selected emotions
    emotions: List[EmotionSelection]
    
    # Optional context
    notes: Optional[str]
    factors: Optional[List[MoodFactor]]
    activities: Optional[List[Activity]]
    location: Optional[Location]
    
    # Entry metadata
    entry_method: str  # "manual", "prompted", "inferred"
    platform: str  # "mobile", "web", "voice"
    
    class Config:
        orm_mode = True

class EmotionSelection(BaseModel):
    """
    User-selected emotion with intensity
    """
    emotion: str
    intensity: float  # 0.0 to 1.0
    is_primary: bool = False

class MoodFactor(BaseModel):
    """
    Factor affecting mood
    """
    factor_type: str  # "person", "event", "thought", "physical", "environment"
    description: str
    impact: float  # -1.0 to 1.0 (negative to positive impact)
```

### 2.2 Mood Intelligence Models

Models used by the Mood Service's intelligence engine:

```python
class MoodInsights(BaseModel):
    """
    Comprehensive mood insights for a user
    """
    user_id: str
    generated_at: datetime
    
    # Current state
    current_state: EmotionalState
    
    # Temporal patterns
    patterns: MoodPatterns
    trajectory: EmotionalTrajectory
    
    # Contributing factors
    identified_triggers: List[EmotionTrigger]
    frequent_factors: List[FrequentFactor]
    
    # Risk assessment
    risk_indicators: List[RiskIndicator]
    protective_factors: List[ProtectiveFactor]
    
    # Intervention insights
    effective_interventions: List[EffectiveIntervention]
    suggested_interventions: List[InterventionSuggestion]
    
    # Metadata
    data_quality: float  # 0.0 to 1.0
    coverage_period: DateRange
    
    def get_shareable_summary(self, privacy_level: PrivacyLevel) -> Dict[str, Any]:
        """
        Returns privacy-respecting summary for sharing with other services
        """
        pass

class MoodPatterns(BaseModel):
    """
    Identified patterns in mood data
    """
    cyclical_patterns: List[CyclicalPattern]
    trigger_patterns: List[TriggerPattern]
    activity_impact_patterns: List[ActivityImpactPattern]
    social_impact_patterns: List[SocialImpactPattern]
    environmental_patterns: List[EnvironmentalPattern]

class RiskIndicator(BaseModel):
    """
    Indicator of potential mental health risk
    """
    type: str  # "mood_decline", "isolation", "crisis_language", "behavioral_change"
    severity: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    supporting_evidence: List[EvidenceItem]
    first_detected: datetime
    trend: str  # "increasing", "decreasing", "stable"
```

### 2.3 Platform Orchestration Models

Models used for coordinating adaptations across services:

```python
class PlatformAdaptations(BaseModel):
    """
    Platform-wide adaptations based on mood intelligence
    """
    user_id: str
    generated_at: datetime
    based_on_context_timestamp: datetime
    
    # Service-specific adaptations
    chatbot: ChatbotAdaptations
    community: CommunityAdaptations
    content: ContentAdaptations
    journal: JournalAdaptations
    interface: InterfaceAdaptations
    
    # Cross-service coordination
    priority_interventions: List[PriorityIntervention]
    feature_highlighting: List[FeatureHighlight]
    cross_service_themes: List[CrossServiceTheme]
    
    # Metadata
    confidence: float  # 0.0 to 1.0
    adaptation_strategy: str  # "supportive", "growth", "stabilizing", "crisis"

class ChatbotAdaptations(BaseModel):
    """
    Adaptations for the Chatbot Service
    """
    # Conversation approach
    response_tone: str  # "supportive", "encouraging", "reflective", "directive"
    communication_style: CommunicationStyle
    
    # Content generation
    content_focus_areas: List[str]  # Themes to emphasize
    topic_suggestions: List[TopicSuggestion]
    
    # Intervention guidance
    intervention_approach: str
    suggested_techniques: List[TechniqueSuggestion]
    
    # Risk management
    risk_awareness_level: float  # 0.0 to 1.0
    safety_protocols: List[SafetyProtocol]

class CommunityAdaptations(BaseModel):
    """
    Adaptations for the Community Service
    """
    # Connection recommendations
    connection_types: List[str]  # "peer", "mentor", "support_group"
    matching_priorities: List[MatchingPriority]
    
    # Content recommendations
    content_focus: List[str]  # "inspiration", "education", "connection"
    content_filters: ContentFilters
    
    # Engagement approach
    engagement_level: str  # "passive", "moderate", "active"
    interaction_style: str  # "supportive", "challenging", "collaborative"
    
    # Event/challenge recommendations
    event_suggestions: List[EventSuggestion]
    challenge_suggestions: List[ChallengeSuggestion]
```

## 3. Chatbot Service Models

### 3.1 Conversation Models

Models for chatbot conversations:

```python
class Conversation(BaseModel):
    """
    Chatbot conversation
    """
    id: str  # UUID format
    user_id: str
    started_at: datetime
    updated_at: datetime
    ended_at: Optional[datetime]
    
    # Conversation metadata
    topic: Optional[str]
    intent: Optional[str]
    sentiment: Optional[float]  # -1.0 to 1.0
    
    # Messages
    messages: List[Message]
    
    # Context
    mood_context: Optional[SimpleMoodContext]
    detected_emotions: Dict[str, float]
    identified_needs: List[IdentifiedNeed]
    
    # Outcomes
    breakthroughs: List[Breakthrough]
    suggested_actions: List[SuggestedAction]
    mood_impact: Optional[MoodImpact]
    
    # Metadata
    quality_metrics: ConversationQualityMetrics
    
    class Config:
        orm_mode = True

class Message(BaseModel):
    """
    Individual message in conversation
    """
    id: str  # UUID format
    conversation_id: str
    timestamp: datetime
    sender_type: str  # "user" or "bot"
    
    # Content
    text: str
    attachments: Optional[List[Attachment]]
    
    # Analysis
    sentiment: Optional[float]  # -1.0 to 1.0
    emotions: Optional[Dict[str, float]]
    intents: Optional[List[Intent]]
    entities: Optional[List[Entity]]
    
    # Response metadata (for bot messages)
    response_type: Optional[str]  # "answer", "question", "reflection", "suggestion"
    strategy: Optional[str]  # "support", "challenge", "educate", "distract"
    
    # User interaction metadata (for user messages)
    typing_duration: Optional[float]  # seconds
    response_time: Optional[float]  # seconds after previous message

class Breakthrough(BaseModel):
    """
    Significant insight or progress identified in conversation
    """
    type: str  # "realization", "commitment", "emotion_processing"
    description: str
    confidence: float  # 0.0 to 1.0
    
    # Related content
    message_ids: List[str]
    key_phrases: List[str]
    
    # Potential uses
    sharable: bool  # Whether suitable for anonymized community sharing
    follow_up_needed: bool
    suggested_interventions: List[str]
```

### 3.2 Response Generation Models

Models for generating contextual responses:

```python
class ResponseGenerationContext(BaseModel):
    """
    Context for generating a response
    """
    # User message
    message: Message
    conversation: Conversation
    
    # User context
    mood_context: UserMoodContext
    user_profile: UserProfileContext
    
    # Conversation state
    conversation_history: List[Message]
    identified_topics: List[Topic]
    conversation_metrics: ConversationMetrics
    
    # Response parameters
    response_goals: List[ResponseGoal]
    constraints: List[ResponseConstraint]
    priority_strategies: List[ResponseStrategy]

class GeneratedResponse(BaseModel):
    """
    Response generated by chatbot
    """
    text: str
    
    # Response metadata
    response_type: str  # "answer", "question", "reflection", "suggestion"
    strategy: str  # "support", "challenge", "educate", "distract"
    emotional_tone: str  # "warm", "neutral", "professional", "encouraging"
    
    # Related content
    follow_up_questions: List[str]
    suggested_actions: List[SuggestedAction]
    suggested_content: List[ContentSuggestion]
    
    # Community integration
    community_tie_ins: List[CommunityTieIn]
    
    # Assessment
    expected_impact: ExpectedImpact
    confidence: float  # 0.0 to 1.0
```

### 3.3 Content Generation Models

Models for generating content for other services:

```python
class GeneratedContent(BaseModel):
    """
    Content generated by chatbot for other services
    """
    id: str  # UUID format
    user_id: str
    conversation_id: Optional[str]
    generated_at: datetime
    
    # Content
    content_type: str  # "community_post", "journal_prompt", "challenge"
    title: str
    body: str
    
    # Context
    mood_context: SimpleMoodContext
    generation_context: GenerationContext
    
    # Metadata
    suggested_tags: List[str]
    privacy_level: PrivacyLevel
    suitability_score: float  # 0.0 to 1.0
    
    # Service-specific fields
    community_metadata: Optional[CommunityContentMetadata]
    journal_metadata: Optional[JournalContentMetadata]
    challenge_metadata: Optional[ChallengeMetadata]

class CommunityContentMetadata(BaseModel):
    """
    Metadata for community content
    """
    post_type: str  # "breakthrough", "question", "reflection", "resource"
    target_audience: List[str]  # "similar_experience", "support_providers", "all"
    expected_responses: List[str]  # "emotional_support", "advice", "shared_experience"
    anonymization_level: str  # "full", "partial", "none"
```

## 4. Community Service Models

### 4.1 Social Connection Models

Models for social connections and interactions:

```python
class Connection(BaseModel):
    """
    Connection between users
    """
    id: str  # UUID format
    user_id: str
    connected_user_id: str
    
    # Connection details
    connection_type: str  # "peer", "mentor", "mentee", "support"
    strength: float  # 0.0 to 1.0
    established_at: datetime
    last_interaction_at: datetime
    
    # Connection metrics
    interaction_count: int
    quality_score: float  # 0.0 to 1.0
    reciprocity_score: float  # 0.0 to 1.0
    
    # Mood intelligence
    mood_compatibility: float  # 0.0 to 1.0
    support_effectiveness: float  # 0.0 to 1.0
    
    # Privacy/visibility
    visibility: str  # "public", "connections_only", "private"
    
    class Config:
        orm_mode = True

class Interaction(BaseModel):
    """
    Interaction between users
    """
    id: str  # UUID format
    initiator_id: str
    recipient_id: str
    timestamp: datetime
    
    # Interaction details
    interaction_type: str  # "comment", "reaction", "message", "recommendation"
    content_id: Optional[str]  # Related content
    content_type: Optional[str]  # "post", "challenge", "event"
    
    # Interaction quality
    sentiment: float  # -1.0 to 1.0
    supportiveness: float  # 0.0 to 1.0
    depth: float  # 0.0 to 1.0
    
    # Impact
    initiator_impact: Optional[InteractionImpact]
    recipient_impact: Optional[InteractionImpact]
```

### 4.2 Community Content Models

Models for community content:

```python
class CommunityPost(BaseModel):
    """
    User post in community
    """
    id: str  # UUID format
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    # Content
    title: str
    body: str
    media_attachments: List[MediaAttachment]
    
    # Categorization
    post_type: str  # "question", "story", "reflection", "resource", "breakthrough"
    tags: List[str]
    topics: List[str]
    
    # Visibility
    visibility: str  # "public", "group", "connections_only"
    anonymity_level: str  # "identified", "partial", "anonymous"
    
    # Engagement metrics
    view_count: int
    comment_count: int
    reaction_counts: Dict[str, int]
    
    # Mood context
    mood_context: Optional[SharedMoodContext]
    mood_tags: List[str]
    
    # Origin
    source: Optional[str]  # "user", "chatbot", "journal"
    
    class Config:
        orm_mode = True

class Challenge(BaseModel):
    """
    Community challenge
    """
    id: str  # UUID format
    creator_id: str
    created_at: datetime
    
    # Challenge details
    title: str
    description: str
    instructions: str
    duration_days: int
    
    # Categorization
    challenge_type: str  # "habit", "mindfulness", "creative", "social"
    difficulty: str  # "beginner", "intermediate", "advanced"
    tags: List[str]
    benefits: List[str]
    
    # Participation
    participant_count: int
    completion_rate: float  # 0.0 to 1.0
    
    # Mood intelligence
    target_mood_states: List[str]
    mood_impact_data: Optional[MoodImpactData]
    
    # Origin
    source: Optional[str]  # "user", "chatbot", "system"
    
    class Config:
        orm_mode = True
```

### 4.3 Matching Models

Models for connecting users based on mood and other factors:

```python
class MatchingCriteria(BaseModel):
    """
    Criteria for matching users
    """
    user_id: str
    
    # Basic criteria
    connection_type: str  # "peer", "mentor", "support_group"
    matching_priority: str  # "experience", "mood", "goals", "personality"
    
    # Mood-based criteria
    mood_matching_strategy: str  # "similar", "complementary", "supportive"
    target_mood_states: Optional[List[str]]
    
    # Experience criteria
    experience_matching: Optional[ExperienceMatching]
    
    # Communication preferences
    communication_style_preference: Optional[str]
    interaction_frequency_preference: Optional[str]
    
    # Exclusions
    excluded_user_ids: List[str]

class UserMatch(BaseModel):
    """
    Potential user match
    """
    matched_user_id: str
    requesting_user_id: str
    
    # Match quality
    match_score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    
    # Match reasons
    primary_match_reason: str
    match_factors: Dict[str, float]  # Factor name to strength mapping
    
    # Compatibility details
    mood_compatibility: float  # 0.0 to 1.0
    experience_compatibility: float  # 0.0 to 1.0
    communication_compatibility: float  # 0.0 to 1.0
    
    # Potential benefits
    potential_benefits: List[PotentialBenefit]
    suggested_activities: List[str]
    
    # Privacy-safe user preview
    user_preview: PrivacySafeUserPreview
```

## 5. Journal Service Models

### 5.1 Journal Entry Models

Models for journal entries:

```python
class JournalEntry(BaseModel):
    """
    User journal entry
    """
    id: str  # UUID format
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    # Content
    title: Optional[str]
    content: str
    media_attachments: List[MediaAttachment]
    
    # Metadata
    word_count: int
    writing_duration: Optional[int]  # seconds
    entry_method: str  # "manual", "prompted", "voice"
    
    # Categorization
    tags: List[str]
    topics: List[str]
    
    # Privacy
    visibility: str  # "private", "therapist", "selected_connections"
    shared_with: List[str]  # User IDs
    
    # Analysis results
    analysis: Optional[JournalAnalysis]
    
    # Mood context
    mood_before: Optional[SimpleMoodState]
    mood_after: Optional[SimpleMoodState]
    
    class Config:
        orm_mode = True

class JournalPrompt(BaseModel):
    """
    Writing prompt for journaling
    """
    id: str  # UUID format
    text: str
    
    # Categorization
    prompt_type: str  # "reflection", "gratitude", "processing", "growth"
    themes: List[str]
    target_emotions: List[str]
    
    # Usage guidance
    suitable_mood_states: List[str]
    therapeutic_goals: List[str]
    difficulty: str  # "gentle", "moderate", "challenging"
    
    # Effectiveness data
    usage_count: int
    average_response_length: Optional[int]  # words
    average_emotional_impact: Optional[float]  # -1.0 to 1.0
    
    # Origin
    source: str  # "system", "therapist", "chatbot", "user"
```

### 5.2 Journal Analysis Models

Models for analyzing journal content:

```python
class JournalAnalysis(BaseModel):
    """
    Analysis of journal entry
    """
    entry_id: str
    analyzed_at: datetime
    
    # Emotional analysis
    emotional_tone: Dict[str, float]  # Emotion to intensity mapping
    sentiment: float  # -1.0 to 1.0
    emotional_arc: List[EmotionalArcPoint]
    
    # Content analysis
    key_themes: List[IdentifiedTheme]
    key_concerns: List[IdentifiedConcern]
    linguistic_style: LinguisticStyle
    
    # Cognitive patterns
    thinking_patterns: List[ThinkingPattern]
    cognitive_distortions: List[CognitiveDistortion]
    strengths_identified: List[IdentifiedStrength]
    
    # Temporal analysis
    time_orientation: Dict[str, float]  # "past", "present", "future" to focus percentage
    change_indicators: List[ChangeIndicator]
    
    # Metadata
    analysis_confidence: float  # 0.0 to 1.0

class IdentifiedTheme(BaseModel):
    """
    Theme identified in journal entry
    """
    name: str
    confidence: float  # 0.0 to 1.0
    sentiment: float  # -1.0 to 1.0
    
    # Supporting evidence
    text_snippets: List[str]
    frequency: int
    
    # Historical context
    historical_presence: float  # 0.0 to 1.0 (how common in user's writing)
    trend: str  # "increasing", "decreasing", "stable", "new"

class CognitiveDistortion(BaseModel):
    """
    Cognitive distortion identified in writing
    """
    type: str  # "all_or_nothing", "overgeneralization", "catastrophizing", etc.
    confidence: float  # 0.0 to 1.0
    severity: float  # 0.0 to 1.0
    
    # Supporting evidence
    text_snippets: List[str]
    
    # Reframing opportunities
    reframing_suggestions: List[ReframingSuggestion]
```

### 5.3 Writing Assistance Models

Models for providing writing assistance:

```python
class WritingAssistance(BaseModel):
    """
    Assistance for journal writing
    """
    # Structural assistance
    continuation_suggestions: List[ContinuationSuggestion]
    elaboration_prompts: List[ElaborationPrompt]
    
    # Emotional clarity
    emotional_vocabulary_suggestions: List[VocabularySuggestion]
    emotional_clarity_prompts: List[ClarityPrompt]
    
    # Cognitive reframing
    reframing_suggestions: List[ReframingSuggestion]
    perspective_prompts: List[PerspectivePrompt]
    
    # Growth-oriented
    strength_highlights: List[StrengthHighlight]
    insight_development_prompts: List[InsightPrompt]
    
    # Metadata
    based_on_entry: Optional[str]  # Entry ID
    based_on_mood: Optional[SimpleMoodContext]
    assistance_strategy: str  # "supportive", "challenging", "balancing"

class ReframingSuggestion(BaseModel):
    """
    Suggestion for cognitive reframing
    """
    original_text: str
    distortion_type: str  # "all_or_nothing", "catastrophizing", etc.
    
    # Suggestions
    reframing_prompt: str
    alternative_perspective: str
    reframed_example: str
    
    # Guidance
    approach: str  # "gentle", "direct", "socratic"
    explanation: str
```

## 6. ML/AI Service Models

### 6.1 Model Management

Models for managing machine learning models:

```python
class MLModel(BaseModel):
    """
    Machine learning model metadata
    """
    id: str  # UUID format
    name: str
    version: str
    
    # Model type
    model_type: str  # "emotion_detection", "text_analysis", "prediction", etc.
    framework: str  # "tensorflow", "pytorch", "scikit-learn", etc.
    
    # Usage
    input_format: Dict[str, Any]
    output_format: Dict[str, Any]
    performance_metrics: Dict[str, float]
    
    # Lifecycle
    created_at: datetime
    last_updated_at: datetime
    training_dataset_id: str
    
    # Deployment
    deployment_status: str  # "active", "staged", "archived"
    endpoint_url: Optional[str]
    
    class Config:
        orm_mode = True

class ModelTrainingJob(BaseModel):
    """
    Job for training or updating a model
    """
    id: str  # UUID format
    model_id: Optional[str]  # If updating existing model
    model_type: str
    
    # Training configuration
    training_dataset_ids: List[str]
    validation_dataset_ids: List[str]
    hyperparameters: Dict[str, Any]
    
    # Job metadata
    requested_by: str  # User or service ID
    requested_at: datetime
    status: str  # "queued", "running", "completed", "failed"
    progress: float  # 0.0 to 1.0
    
    # Results
    completed_at: Optional[datetime]
    resulting_model_id: Optional[str]
    performance_metrics: Optional[Dict[str, float]]
    
    class Config:
        orm_mode = True
```

### 6.2 Analysis Models

Models for text and data analysis:

```python
class TextAnalysisRequest(BaseModel):
    """
    Request for text analysis
    """
    text: str
    user_id: Optional[str]
    
    # Analysis types
    analysis_types: List[str]  # "emotion", "sentiment", "themes", "entities", etc.
    
    # Context
    context: Optional[AnalysisContext]
    
    # Configuration
    language: str = "en"
    response_format: str = "detailed"  # "simple", "detailed"

class TextAnalysisResponse(BaseModel):
    """
    Response from text analysis
    """
    request_id: str
    analyzed_at: datetime
    
    # Sentiment analysis
    sentiment: Optional[SentimentAnalysis]
    
    # Emotion analysis
    emotions: Optional[EmotionAnalysis]
    
    # Content analysis
    themes: Optional[List[IdentifiedTheme]]
    entities: Optional[List[IdentifiedEntity]]
    
    # Cognitive analysis
    thinking_patterns: Optional[List[ThinkingPattern]]
    cognitive_distortions: Optional[List[CognitiveDistortion]]
    
    # Metadata
    language_detected: str
    confidence: Dict[str, float]  # Analysis type to confidence mapping

class EmotionAnalysis(BaseModel):
    """
    Analysis of emotions in text
    """
    primary_emotions: Dict[str, float]  # Emotion to intensity mapping
    emotion_distribution: Dict[str, float]  # Normalized distribution
    emotional_tone: str  # Overall tone
    emotional_intensity: float  # 0.0 to 1.0
    emotional_complexity: float  # 0.0 to 1.0
    emotion_trajectory: Optional[List[EmotionTrajectoryPoint]]
```

### 6.3 Prediction Models

Models for predictions and recommendations:

```python
class PredictionRequest(BaseModel):
    """
    Request for prediction
    """
    prediction_type: str  # "mood_trajectory", "intervention_effectiveness", etc.
    user_id: str
    
    # Prediction parameters
    time_horizon: Optional[int]  # Days
    scenario: Optional[str]  # "baseline", "with_intervention", "stressor"
    
    # Context
    context_data: Optional[Dict[str, Any]]
    
    # Configuration
    confidence_intervals: bool = True
    detail_level: str = "standard"  # "minimal", "standard", "detailed"

class PredictionResponse(BaseModel):
    """
    Response for prediction
    """
    request_id: str
    prediction_type: str
    user_id: str
    generated_at: datetime
    
    # Prediction results
    predictions: Dict[str, Any]  # Type-specific prediction data
    
    # Quality indicators
    confidence: float  # 0.0 to 1.0
    prediction_intervals: Optional[Dict[str, List[float]]]
    data_completeness: float  # 0.0 to 1.0
    
    # Context
    factors_considered: List[str]
    limitations: List[str]

class MoodTrajectoryPrediction(BaseModel):
    """
    Prediction of mood trajectory
    """
    # Time points
    timestamps: List[datetime]
    
    # Predicted values
    valence_predictions: List[float]
    arousal_predictions: List[float]
    
    # Confidence intervals
    valence_confidence_intervals: Optional[List[List[float]]]  # [[lower, upper], ...]
    arousal_confidence_intervals: Optional[List[List[float]]]
    
    # Key events
    predicted_turning_points: List[TurningPoint]
    risk_periods: List[RiskPeriod]
    
    # Context
    baseline_comparison: Optional[BaselineComparison]
    contributing_factors: List[ContributingFactor]
```

## 7. Profile Service Models

### 7.1 User Profile Models

Models for user profiles:

```python
class UserProfile(BaseModel):
    """
    Comprehensive user profile
    """
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    # Basic profile
    display_name: str
    bio: Optional[str]
    profile_image_url: Optional[str]
    
    # Preferences
    language: str = "en"
    timezone: str = "UTC"
    theme: str = "system"
    
    # Platform preferences
    notification_preferences: NotificationPreferences
    privacy_settings: PrivacySettings
    interface_preferences: InterfacePreferences
    
    # Therapeutic context
    therapeutic_goals: List[TherapeuticGoal]
    tracked_conditions: List[TrackedCondition]
    coping_strategies: List[CopingStrategy]
    
    # Activity patterns
    activity_summary: ActivitySummary
    
    # Consent records
    active_consents: List[ConsentRecord]
    
    class Config:
        orm_mode = True

class PrivacySettings(BaseModel):
    """
    User privacy settings
    """
    # Profile visibility
    profile_visibility: str  # "public", "connections", "private"
    activity_visibility: str  # "public", "connections", "private"
    
    # Data sharing
    data_sharing_preferences: Dict[str, bool]
    mood_sharing_level: str  # "none", "summary", "detailed"
    
    # Content privacy
    journal_default_visibility: str  # "private", "therapist", "selected"
    community_content_anonymity: str  # "identified", "anonymous", "custom"
    
    # Third-party sharing
    allow_anonymized_research: bool = False
    allow_service_improvement: bool = True
    
    # Advanced settings
    ip_tracking: bool = True
    usage_analytics: bool = True
```

### 7.2 Activity Tracking Models

Models for tracking user activity:

```python
class UserActivity(BaseModel):
    """
    Record of user activity
    """
    id: str  # UUID format
    user_id: str
    timestamp: datetime
    
    # Activity details
    activity_type: str  # "login", "feature_use", "content_creation", "engagement"
    service: str  # "mood", "chatbot", "community", "journal"
    feature: Optional[str]  # Specific feature used
    
    # Context
    session_id: Optional[str]
    content_id: Optional[str]  # If activity involves content
    duration: Optional[int]  # seconds
    
    # Engagement metrics
    engagement_depth: Optional[float]  # 0.0 to 1.0
    completion: Optional[bool]
    
    # Platform context
    platform: str  # "web", "mobile", "tablet"
    client_version: str
    
    class Config:
        orm_mode = True

class ActivityPattern(BaseModel):
    """
    Pattern of user activity
    """
    user_id: str
    analyzed_period: DateRange
    
    # Temporal patterns
    typical_usage_times: Dict[str, List[TimeRange]]  # Day of week to time ranges
    session_frequency: float  # Sessions per week
    average_session_duration: int  # seconds
    
    # Service usage
    service_usage_distribution: Dict[str, float]  # Service to usage percentage
    primary_services: List[str]
    feature_usage_distribution: Dict[str, float]
    
    # Engagement quality
    engagement_depth: float  # 0.0 to 1.0
    completion_rates: Dict[str, float]  # Activity type to completion rate
    
    # Trends
    usage_trend: str  # "increasing", "stable", "decreasing"
    engagement_trend: str  # "deepening", "stable", "declining"
```

### 7.3 Consent Models

Models for managing user consent:

```python
class ConsentRecord(BaseModel):
    """
    Record of user consent
    """
    id: str  # UUID format
    user_id: str
    
    # Consent details
    consent_type: str  # "data_processing", "sharing", "research", "communication"
    scope: List[str]  # What the consent covers
    granted_at: datetime
    expires_at: Optional[datetime]
    
    # Version information
    terms_version: str
    privacy_policy_version: str
    
    # Grant context
    grant_method: str  # "explicit", "imported", "default"
    grant_context: Optional[Dict[str, Any]]
    
    # Revocation
    revoked_at: Optional[datetime]
    revocation_reason: Optional[str]
    
    # Validation
    is_valid: bool = True
    validation_issues: List[str] = []
    
    class Config:
        orm_mode = True

class ConsentRequest(BaseModel):
    """
    Request for user consent
    """
    user_id: str
    consent_type: str
    
    # Request details
    scope: List[str]
    justification: str
    terms_url: str
    privacy_policy_url: str
    
    # Request context
    requesting_service: str
    feature_dependency: str  # "required", "optional", "enhancement"
    
    # UI guidance
    display_text: str
    additional_information: Optional[str]
    options: List[ConsentOption]
```

## 8. Content Service Models

### 8.1 Content Models

Models for platform content:

```python
class Content(BaseModel):
    """
    Platform content item
    """
    id: str  # UUID format
    created_at: datetime
    updated_at: datetime
    
    # Content details
    title: str
    description: Optional[str]
    content_type: str  # "article", "exercise", "video", "audio", "infographic"
    
    # Content body (type-specific)
    text_content: Optional[str]
    media_url: Optional[str]
    attachments: List[ContentAttachment]
    
    # Categorization
    categories: List[str]
    tags: List[str]
    therapeutic_focuses: List[str]
    
    # Metadata
    author: Optional[str]
    source: str  # "platform", "partner", "community", "chatbot"
    license: Optional[str]
    
    # Targeting
    suitable_moods: List[str]
    suitable_contexts: List[str]
    readability_level: float  # 0.0 to 1.0
    
    # Effectiveness
    engagement_metrics: ContentEngagementMetrics
    effectiveness_metrics: Optional[ContentEffectivenessMetrics]
    
    class Config:
        orm_mode = True

class ContentAttachment(BaseModel):
    """
    Attachment to content
    """
    id: str  # UUID format
    content_id: str
    
    # Attachment details
    attachment_type: str  # "image", "audio", "video", "document", "link"
    url: str
    title: Optional[str]
    description: Optional[str]
    
    # Media metadata
    mime_type: str
    file_size: Optional[int]  # bytes
    duration: Optional[int]  # seconds (for audio/video)
    dimensions: Optional[Dict[str, int]]  # width, height (for images/video)
```

### 8.2 Content Personalization Models

Models for personalizing content:

```python
class ContentPersonalizationRequest(BaseModel):
    """
    Request for personalized content
    """
    user_id: str
    
    # Request parameters
    content_types: List[str]
    count: int
    exclude_ids: List[str] = []
    
    # Context
    mood_context: Optional[SimpleMoodContext]
    situation: Optional[str]
    goal: Optional[str]
    
    # Personalization parameters
    personalization_strength: float = 0.8  # 0.0 to 1.0
    novelty_preference: float = 0.5  # 0.0 to 1.0 (familiar to novel)
    diversity: float = 0.5  # 0.0 to 1.0 (focused to diverse)

class PersonalizedContentResponse(BaseModel):
    """
    Response with personalized content
    """
    request_id: str
    user_id: str
    
    # Personalized content
    content_items: List[PersonalizedContentItem]
    
    # Personalization metrics
    personalization_confidence: float  # 0.0 to 1.0
    diversity_score: float  # 0.0 to 1.0
    
    # Context
    personalization_factors: List[PersonalizationFactor]
    user_context_quality: float  # 0.0 to 1.0

class PersonalizedContentItem(BaseModel):
    """
    Content item with personalization metadata
    """
    content: Content
    
    # Personalization metadata
    relevance_score: float  # 0.0 to 1.0
    personalization_factors: List[PersonalizationFactor]
    expected_engagement: float  # 0.0 to 1.0
    expected_benefit: float  # 0.0 to 1.0
    
    # Presentation guidance
    presentation_context: str
    suggested_framing: Optional[str]
```

### 8.3 Content Effectiveness Models

Models for tracking content effectiveness:

```python
class ContentEffectivenessMetrics(BaseModel):
    """
    Metrics for content effectiveness
    """
    content_id: str
    last_updated: datetime
    
    # Engagement metrics
    view_count: int
    completion_rate: float  # 0.0 to 1.0
    average_engagement_time: int  # seconds
    share_count: int
    
    # Feedback metrics
    average_rating: float  # 1.0 to 5.0
    feedback_count: int
    positive_feedback_percentage: float  # 0.0 to 1.0
    
    # Effectiveness metrics
    mood_impact: Dict[str, float]  # Mood aspect to impact mapping
    reported_helpfulness: float  # 0.0 to 1.0
    repeat_usage_rate: float  # 0.0 to 1.0
    
    # Audience metrics
    most_effective_segments: List[UserSegment]
    effectiveness_by_mood_state: Dict[str, float]
    effectiveness_by_goal: Dict[str, float]

class ContentEngagement(BaseModel):
    """
    Record of user engagement with content
    """
    id: str  # UUID format
    user_id: str
    content_id: str
    timestamp: datetime
    
    # Engagement details
    engagement_type: str  # "view", "complete", "save", "share", "rate"
    duration: Optional[int]  # seconds
    
    # Context
    service: str  # Where engagement occurred
    referrer: Optional[str]  # How user found content
    
    # Feedback
    rating: Optional[int]  # 1 to 5
    feedback: Optional[str]
    
    # Impact
    reported_helpfulness: Optional[int]  # 1 to 5
    mood_before: Optional[SimpleMoodState]
    mood_after: Optional[SimpleMoodState]
    
    class Config:
        orm_mode = True
```

## 9. Database Schema Examples

### 9.1 Mood Service Schema

```sql
-- User contexts table
CREATE TABLE user_contexts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Emotional state
    current_emotional_state JSONB NOT NULL,
    emotional_trajectory JSONB,
    emotional_volatility FLOAT,
    
    -- Behavioral patterns
    interaction_patterns JSONB,
    activity_effectiveness JSONB,
    engagement_trends JSONB,
    
    -- Social wellness
    social_connections_quality FLOAT,
    community_engagement_health JSONB,
    support_network_strength FLOAT,
    
    -- Content and communication
    communication_style_preferences JSONB,
    content_consumption_patterns JSONB,
    writing_patterns JSONB,
    
    -- Intervention history
    intervention_effectiveness_history JSONB,
    preferred_intervention_types JSONB,
    crisis_risk_indicators JSONB,
    
    -- Contextual factors
    environmental_factors JSONB,
    temporal_patterns JSONB,
    life_context JSONB,
    
    -- Metadata
    context_quality FLOAT,
    context_sources JSONB,
    last_updated_by VARCHAR(100),
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Mood entries table
CREATE TABLE mood_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Core affect
    valence FLOAT NOT NULL,
    arousal FLOAT NOT NULL,
    
    -- Selected emotions (JSONB array of objects)
    emotions JSONB NOT NULL,
    
    -- Optional context
    notes TEXT,
    factors JSONB,
    activities JSONB,
    location JSONB,
    
    -- Entry metadata
    entry_method VARCHAR(50) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Mood insights table
CREATE TABLE mood_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Current state
    current_state JSONB NOT NULL,
    
    -- Temporal patterns
    patterns JSONB NOT NULL,
    trajectory JSONB NOT NULL,
    
    -- Contributing factors
    identified_triggers JSONB,
    frequent_factors JSONB,
    
    -- Risk assessment
    risk_indicators JSONB,
    protective_factors JSONB,
    
    -- Intervention insights
    effective_interventions JSONB,
    suggested_interventions JSONB,
    
    -- Metadata
    data_quality FLOAT NOT NULL,
    coverage_period JSONB NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Platform adaptations table
CREATE TABLE platform_adaptations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    based_on_context_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Service-specific adaptations
    chatbot JSONB NOT NULL,
    community JSONB NOT NULL,
    content JSONB NOT NULL,
    journal JSONB NOT NULL,
    interface JSONB NOT NULL,
    
    -- Cross-service coordination
    priority_interventions JSONB,
    feature_highlighting JSONB,
    cross_service_themes JSONB,
    
    -- Metadata
    confidence FLOAT NOT NULL,
    adaptation_strategy VARCHAR(50) NOT NULL,
    
    executed BOOLEAN NOT NULL DEFAULT FALSE,
    execution_timestamp TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### 9.2 Chatbot Service Schema

```sql
-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    
    -- Conversation metadata
    topic VARCHAR(255),
    intent VARCHAR(100),
    sentiment FLOAT,
    
    -- Context
    mood_context JSONB,
    detected_emotions JSONB,
    identified_needs JSONB,
    
    -- Outcomes
    breakthroughs JSONB,
    suggested_actions JSONB,
    mood_impact JSONB,
    
    -- Metadata
    quality_metrics JSONB
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    sender_type VARCHAR(20) NOT NULL,
    
    -- Content
    text TEXT NOT NULL,
    attachments JSONB,
    
    -- Analysis
    sentiment FLOAT,
    emotions JSONB,
    intents JSONB,
    entities JSONB,
    
    -- Response metadata (for bot messages)
    response_type VARCHAR(50),
    strategy VARCHAR(50),
    
    -- User interaction metadata (for user messages)
    typing_duration FLOAT,
    response_time FLOAT
);

-- Generated content table
CREATE TABLE generated_contents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    conversation_id UUID REFERENCES conversations(id),
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Content
    content_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    
    -- Context
    mood_context JSONB,
    generation_context JSONB,
    
    -- Metadata
    suggested_tags JSONB,
    privacy_level VARCHAR(50) NOT NULL,
    suitability_score FLOAT NOT NULL,
    
    -- Service-specific fields
    community_metadata JSONB,
    journal_metadata JSONB,
    challenge_metadata JSONB,
    
    -- Usage tracking
    used BOOLEAN NOT NULL DEFAULT FALSE,
    used_at TIMESTAMP WITH TIME ZONE,
    usage_feedback JSONB
);
```

### 9.3 Community Service Schema

```sql
-- Connections table
CREATE TABLE connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    connected_user_id UUID NOT NULL REFERENCES users(id),
    
    -- Connection details
    connection_type VARCHAR(50) NOT NULL,
    strength FLOAT NOT NULL,
    established_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_interaction_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Connection metrics
    interaction_count INTEGER NOT NULL DEFAULT 0,
    quality_score FLOAT NOT NULL,
    reciprocity_score FLOAT NOT NULL,
    
    -- Mood intelligence
    mood_compatibility FLOAT NOT NULL,
    support_effectiveness FLOAT NOT NULL,
    
    -- Privacy/visibility
    visibility VARCHAR(50) NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Interactions table
CREATE TABLE interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    initiator_id UUID NOT NULL REFERENCES users(id),
    recipient_id UUID NOT NULL REFERENCES users(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Interaction details
    interaction_type VARCHAR(50) NOT NULL,
    content_id UUID,
    content_type VARCHAR(50),
    
    -- Interaction quality
    sentiment FLOAT,
    supportiveness FLOAT,
    depth FLOAT,
    
    -- Impact
    initiator_impact JSONB,
    recipient_impact JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Community posts table
CREATE TABLE community_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Content
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    media_attachments JSONB,
    
    -- Categorization
    post_type VARCHAR(50) NOT NULL,
    tags JSONB,
    topics JSONB,
    
    -- Visibility
    visibility VARCHAR(50) NOT NULL,
    anonymity_level VARCHAR(50) NOT NULL,
    
    -- Engagement metrics
    view_count INTEGER NOT NULL DEFAULT 0,
    comment_count INTEGER NOT NULL DEFAULT 0,
    reaction_counts JSONB NOT NULL DEFAULT '{}',
    
    -- Mood context
    mood_context JSONB,
    mood_tags JSONB,
    
    -- Origin
    source VARCHAR(50)
);
```

### 9.4 Journal Service Schema

```sql
-- Journal entries table
CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Content
    title VARCHAR(255),
    content TEXT NOT NULL,
    media_attachments JSONB,
    
    -- Metadata
    word_count INTEGER NOT NULL,
    writing_duration INTEGER,
    entry_method VARCHAR(50) NOT NULL,
    
    -- Categorization
    tags JSONB,
    topics JSONB,
    
    -- Privacy
    visibility VARCHAR(50) NOT NULL,
    shared_with JSONB,
    
    -- Analysis results
    analysis JSONB,
    
    -- Mood context
    mood_before JSONB,
    mood_after JSONB
);

-- Journal prompts table
CREATE TABLE journal_prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text TEXT NOT NULL,
    
    -- Categorization
    prompt_type VARCHAR(50) NOT NULL,
    themes JSONB NOT NULL,
    target_emotions JSONB NOT NULL,
    
    -- Usage guidance
    suitable_mood_states JSONB NOT NULL,
    therapeutic_goals JSONB NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    
    -- Effectiveness data
    usage_count INTEGER NOT NULL DEFAULT 0,
    average_response_length INTEGER,
    average_emotional_impact FLOAT,
    
    -- Origin
    source VARCHAR(50) NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Journal analyses table
CREATE TABLE journal_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id UUID NOT NULL REFERENCES journal_entries(id),
    analyzed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Emotional analysis
    emotional_tone JSONB NOT NULL,
    sentiment FLOAT NOT NULL,
    emotional_arc JSONB,
    
    -- Content analysis
    key_themes JSONB NOT NULL,
    key_concerns JSONB,
    linguistic_style JSONB NOT NULL,
    
    -- Cognitive patterns
    thinking_patterns JSONB,
    cognitive_distortions JSONB,
    strengths_identified JSONB,
    
    -- Temporal analysis
    time_orientation JSONB NOT NULL,
    change_indicators JSONB,
    
    -- Metadata
    analysis_confidence FLOAT NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```
