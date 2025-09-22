# MantraPath V3 Platform Enhancement Plan
*Voice-Enabled AI Mental Wellness Ecosystem Transformation*

## V3 Transformation Objective
Transform MantraPath from a collection of strong services into a **unified, voice-first, AI-everywhere mental wellness companion** that creates seamless, intelligent, culturally-aware experiences for global users.

### 🎯 **Core V3 Enhancements**
1. **Voice-First Architecture**: Every interaction naturally supports voice input/output
2. **AI Everywhere**: Intelligence extends beyond chatbot to all platform services
3. **Unified Orchestration**: Action Orchestrator coordinates complex cross-service workflows
4. **Real-time Intelligence**: Event-driven architecture with live AI processing
5. **Cultural Intelligence**: Deep understanding of diverse wellness expressions
6. **Proactive Experience**: Platform anticipates needs and provides contextual assistance

---

## 1. Enhanced API Gateway (Intelligence Hub)

### **Voice-Enabled Gateway Capabilities**
- **Voice Request Routing**: Direct voice commands to appropriate services
- **AI-Powered Load Balancing**: Intelligent routing based on user context and service health
- **Cultural Context Processing**: Route requests with cultural and language context
- **Real-time Coordination**: WebSocket support for voice streaming and live AI processing

### **Service JWT Enhancement** 
- **Voice-Aware Authentication**: Service tokens include voice processing permissions
- **AI Service Authorization**: Granular permissions for AI model access across services
- **Cultural Context Tokens**: Include user cultural preferences in service communication
- **Extended Session Management**: Longer sessions for conversational workflows (30min+)

### **Advanced Middleware Stack**
- **Voice Activity Detection**: Identify and route voice vs text requests
- **AI Context Injection**: Add user AI preferences and history to all requests
- **Cultural Adaptation**: Apply cultural context to all service communications
- **Proactive Caching**: AI-predicted request caching for faster response times

---

## 2. Action Orchestrator Service (Central Intelligence)

### **Voice-Driven Orchestration**
- **Voice Intent Processing**: Convert natural speech to structured actions across services
- **Conversational Workflows**: Multi-turn conversations that span multiple services
- **Voice State Management**: Maintain conversation context across service boundaries
- **Cultural Voice Adaptation**: Process voice commands with cultural context

### **Cross-Service AI Coordination**
```yaml
Intent Processing:
  Voice Input: "I'm feeling anxious about work today"
  Analysis: Emotion detection + context understanding
  Actions:
    - Log mood with anxiety level
    - Suggest breathing exercise
    - Offer journal prompt
    - Trigger supportive chat response
    - Schedule follow-up check-in
```

### **Intelligent Workflow Engine**
- **Predictive Action Chains**: AI predicts likely next actions in user workflows
- **Cultural Workflow Adaptation**: Adjust workflows based on cultural wellness approaches
- **Voice Command Macros**: Complex workflows triggered by simple voice commands
- **Contextual Permission Escalation**: Smart permission requests for sensitive actions

---

## 3. Voice-Enhanced Multilingual & Cultural Intelligence Service

### **Advanced Voice Processing Pipeline**
```yaml
Voice Intelligence Stack:
  Speech Recognition: Enhanced Whisper + cultural accent models
  Emotion Detection: Real-time voice emotion analysis
  Cultural Context: Cultural expression pattern recognition
  Intent Classification: Voice-to-action mapping with cultural awareness
  Response Generation: Culturally-appropriate voice responses
```

### **Cultural Voice Intelligence**
- **Cultural Emotion Mapping**: Understand emotional expressions across cultures
- **Voice Tone Analysis**: Detect cultural communication patterns in speech
- **Regional Accent Processing**: Accurate recognition for diverse regional accents
- **Cultural Response Generation**: Generate culturally-appropriate voice responses

### **Cross-Service Voice Integration**
- **Mood Voice Analysis**: Detect mood through voice patterns, not just words
- **Journal Voice Dictation**: Natural voice-to-text with emotional context preservation
- **Chat Voice Synthesis**: AI responses delivered via natural-sounding voice
- **Insights Voice Narration**: AI insights delivered through personalized voice

---

## 4. Event-Driven Real-Time Intelligence

### **Enhanced Event Bus Architecture (NATS)**
```yaml
Voice & AI Event Streams:
  voice.user.{user_id}.speaking: Real-time voice activity
  ai.emotion.{user_id}.detected: Live emotion recognition
  mood.{user_id}.inferred: AI-inferred mood from voice/text
  journal.{user_id}.dictated: Voice journal entries
  chat.{user_id}.voice_response: AI voice responses
  insights.{user_id}.proactive: AI-generated proactive insights
```

### **Real-Time AI Processing**
- **Live Emotion Streaming**: Continuous emotion analysis during voice interactions
- **Cross-Service Intelligence**: Real-time AI insights shared across all services
- **Proactive Intervention Detection**: AI monitors for early intervention opportunities
- **Cultural Context Broadcasting**: Share cultural context across all user interactions

### **Voice-Triggered Event Chains**
- **Voice Mood Logging**: "I'm feeling stressed" → mood log + coping suggestions + calendar block
- **Voice Journal Entry**: Dictated thoughts → transcription + sentiment + theme extraction + insight generation
- **Voice Crisis Detection**: Distress detection → immediate support + professional escalation + family notification

---

## 5. AI-Everywhere Platform Integration

### **Cross-Service AI Intelligence**
```yaml
AI Service Enhancement:
  Mood Service: AI mood prediction, pattern recognition, intervention suggestions
  Journal Service: AI writing assistance, theme extraction, emotional insights
  Chat Service: Enhanced conversational AI with platform context
  Voice Service: Emotion detection, cultural adaptation, natural synthesis
  Insights Service: Predictive analytics, proactive recommendations
```

### **Unified AI Context Management**
- **Global User AI Profile**: Centralized AI understanding of each user
- **Cross-Feature Learning**: AI learns from all user interactions across services
- **Predictive Feature Recommendations**: AI suggests optimal feature usage timing
- **Cultural AI Adaptation**: AI behavior adapts to user's cultural background

### **Proactive AI Assistant**
- **Contextual Presence**: AI assistant available in all platform areas
- **Predictive Assistance**: AI anticipates needs before user requests
- **Cross-Feature Coordination**: AI coordinates actions across multiple services
- **Cultural Sensitivity**: AI adapts communication style to cultural preferences

---

## 6. Enhanced User Experience Architecture

### **Voice-First Interface Design**
- **Conversational Navigation**: Navigate platform through natural voice commands
- **Multimodal Interactions**: Seamless transitions between voice, text, and touch
- **Voice Accessibility**: Full platform accessibility through voice-only interaction
- **Cultural Voice Preferences**: Voice interface adapts to cultural communication styles

### **Intelligent User Journey Orchestration**
```yaml
Example Unified Flow:
  User: "I had a rough day"
  Response:
    - Voice: "I'm sorry to hear that. Would you like to talk about it?"
    - Action: Open journal with voice dictation ready
    - Context: Load supportive chat personality
    - Background: Log mood, prepare coping resources
    - Prediction: Anticipate need for relaxation exercises
```

### **Proactive Experience Features**
- **Contextual Onboarding**: AI guides user through personalized setup
- **Predictive Feature Introduction**: Introduce features when user needs them
- **Adaptive Interface**: UI complexity adapts to user comfort and experience
- **Cultural Interface Adaptation**: Visual and interaction patterns match cultural preferences

---

## 7. Technical Architecture Consolidation

### **Streamlined Service Architecture**
```
API Gateway (Voice & AI Enhanced)
├── Action Orchestrator (NEW - Central Coordination)
├── Event Bus (NATS - Real-time Intelligence) 
├── Auth & Profile Service (Cultural Context)
├── Unified Wellness Service (Mood + Journal + Insights)
├── Enhanced Chatbot (AI + Voice + Platform Context)
├── Voice & Cultural Intelligence Service (Multi-language)
├── ML Intelligence Service (Cross-platform AI)
└── Notification & Communication Service (Proactive)
```

### **Performance & Scalability Enhancements**
- **Voice Processing Optimization**: Edge processing for low-latency voice interaction
- **AI Model Caching**: Intelligent caching of AI responses and predictions
- **Cultural Context Caching**: Cache cultural preferences and adaptation patterns
- **Predictive Resource Allocation**: AI-driven infrastructure scaling

---

## 8. Implementation Strategy & Success Metrics

### **Phase 1: Foundation (Weeks 1-3)**
- Service orchestration and event-driven architecture
- Enhanced API Gateway with voice routing
- Complete frontend-backend integration

### **Phase 2: Voice & AI Integration (Weeks 4-7)**  
- Voice capabilities across all major workflows
- AI intelligence extended to all services
- Conversational interfaces and cultural adaptation

### **Phase 3: User Journey Optimization (Weeks 8-10)**
- Intelligent onboarding and personalization
- Proactive assistance and predictive features
- Unified experience with cross-feature intelligence

### **Phase 4: Polish & Launch (Weeks 11-12)**
- Performance optimization and mobile PWA
- Quality assurance and production readiness

### **Success Metrics**
- **Voice Adoption**: >80% users engage with voice features
- **Response Latency**: <300ms voice-to-action timing
- **AI Satisfaction**: >95% accuracy in emotion detection and response quality
- **User Experience**: >4.6/5.0 platform satisfaction rating
- **Business Impact**: 40% increase in user growth and 35% retention improvement

---

*MantraPath V3: The future of mental wellness is conversational, intelligent, and culturally aware*
- user.* (created, updated, locale.changed)
- mood.entry.* (created, enriched)
- journal.entry.* (created, enriched)
- community.activity.* (thread.created, reply.created)
- challenge.progress.* (updated, streak)
- notification.rule.* (created, updated, executed)
- crisis.alert.* (raised, escalated, resolved)
- action.* (submitted, executed, failed)
- chatbot.analysis.* (tone, engagement, misunderstanding, clarification)
- enrichment.delta.* (journal.emotion, mood.correlation)

Contract Governance:
- Protobuf schemas in central repo; backward-compatible evolution only (additive fields).
- CI contract tests (producer → serialize → schema registry → consumer decode).

---
## 5. Notification & Rule Engine Service
- Extract from current notification logic.
- Rule DSL:
  WHEN <event pattern | metric condition> [AND time_window/quiet_hours] THEN <action(channel_set, template, priority)>
- Priority Score Pipeline Inputs: risk_signals, novelty, user_goals, suppression_budget, channel_cost.
- Quiet Hours + Escalation Ladder.
- RAFT-backed Schedule Queue (dedupe, ordering, failover). Only minimal metadata in consensus: {job_id, run_at, fingerprint, priority, state}.
- Suppression Windows (content_hash within timeframe) prevent spam.

---
## 6. Crisis & Alert Consensus Micro-Cluster
- Separate microservice cluster running RAFT (raftos or Go-based sidecar) managing active_alerts, timers, escalation chains.
- Emits crisis.alert.* events on state transitions.
- Integrates safety classifier & risk aggregation (mood signals + journal + chatbot safety scores).

---
## 7. Challenge & Event Intelligence Service
- Owns events/challenges lifecycle & engagement scoring.
- Post-event reflective prompt generation (feeds Action Orchestrator for journaling suggestions).
- Mood linkage: subscribes to mood.entry.created; correlates participation with mood deltas; emits challenge.engagement.delta.

---
## 8. Multimodal Signal Ingestion Service (Opt-In)
- Edge capture (browser / mobile) → local preprocessing → anonymized affect metrics (valence, arousal, stress probability, speech sentiment).
- No raw audio/video stored; ephemeral inference; only derived scalar features + timestamp + consent flags.
- Emits mood.signal.affect events; aggregator fuses with textual sentiment.

---
## 9. Journal Enrichment Pipeline
- Stream processor subscribing to journal.entry.created.
- Performs: language detect (fallback), sentiment, emotion, entity, safety, thematic clustering, risk phrase extraction.
- Outputs journal.entry.enriched; stores enrichment doc (versioned) linking to original entry.
- Supports reprocessing on model upgrade (replay topic partition or maintain enrichment backlog table).

---
## 10. Unified Feature Flag & Config Service
- Flag types: boolean, gradual rollout %, multivariate (model_provider), dynamic numeric (thresholds).
- Storage: Postgres + Redis cache; signed snapshot distributed to services.
- SDK: get_flag(key, user_context) with variation evaluation.

---
## 11. Privacy & Policy Guard
- Pre-LLM redaction pipeline: detect PII & sensitive health phrases; generate masked prompt + reversible token map (scoped lifetime).
- Pseudonymization: user_id → HMAC_SHA256(user_id, rotating_salt_daily) for analytics.
- Consent ledger: user_id, consent_type, granted_at, revoked_at; downstream processors query state before using signals.

---
## 12. Observability Hub
- OTEL Collector sidecar; export: Prometheus, Jaeger/Tempo, Loki.
- Standard log fields: ts, svc, lvl, trace_id, span_id, user_id, intent, latency_ms, outcome.
- SLO Dashboards: crisis alert latency, notification timeliness, enrichment backlog, translation cache hit rate.

---
## 13. Data & State Model Refinements
- ULID for primary keys (time-ordered, shard friendly).
- Event sourcing domains: actions, notification_rules, crisis_alerts.
- Derived projections: materialized views (Postgres) + Redis for hot sets.
- Embeddings store: vector DB (pgvector) for multilingual semantic queries (journal similarity, memory retrieval for chatbot).

---
## 14. Multilingual Strategy Details
Supported Locales Phase 1: en, hi.
Pipeline Decision Matrix:
- If locale in native_model_set → native inference.
- Else if locale transliteration available → normalize then translate for fallback.
- Cache both original and normalized forms; cross-locale embedding alignment (LASER / multilingual MPNet).
- Adaptive prompting: system sets response_language = user.primary_language unless safety override.

---
## 15. Security / Compliance Enhancements
- Access tokens 15m; refresh tokens 30d (encrypted + rotating key envelope). Sliding refresh.
- Service JWT 5m; minted via /service-token (mutual auth + signing key rotation in KMS).
- mTLS for internal gRPC; cert rotation via automated ACME internal CA.
- Intent permission matrix stored as policy bundles; hot-reloadable.
- Rate limiting tiers: user, intent_category, action_mutation.

---
## 16. AI Governance
- Tool registry signing (Ed25519). LLM only allowed tool subset per session risk score.
- Safety filter chain: pre (input) → generation guardrails → post (output). Crisis escalation triggers Action Orchestrator intent: crisis.escalate.
- Hallucination mitigation: retrieval augmentation from vetted memory indices (journal summaries, mood stats) with citation block.

---
## 17. User Journey (Daily Operational Flow)
Morning:
1. Notification engine proposes daily_digest.
2. Rule engine evaluates (quiet hours, novelty) → send localized digest.
Daytime Passive:
- Mood/journal events stream; if novelty_score > threshold OR risk spike → orchestrator triggers adaptive_checkin intent.
Challenges/Events:
- Completion → engagement delta → reflective_journal_suggestion.
Evening:
- Journal enrichment backlog ensures summary suggestion with emotional trend + protective factor highlight.
Weekly:
- Aggregator builds summary projection; chatbot answers "How was my week?" with factual trace.
Crisis:
- Risk aggregator consensus commit → escalation ladder (in-app banner → push → email) respecting locale.

---
## 18. Phased Migration
Phase 0 (Prep): Schemas, correlation IDs, proto repo.
Phase 1: Modular gateway, NATS, dual-write mood/journal events.
Phase 2: Multilingual service (detect + native sentiment en/hi) + Action Orchestrator MVP.
Phase 3: Notification & Rule Engine extraction + suppression.
Phase 4: Crisis RAFT cluster + alert events.
Phase 5: Journal enrichment streaming + embeddings.
Phase 6: Feature Flag service + advanced multilingual (emotion, safety hi/en parity).
Phase 7: Multimodal ingestion opt-in + privacy guard.
Phase 8: Decommission legacy gateway files, consolidate docs.

---
## 19. Minimal Initial Tasks (Actionable Sprint 1)
1. Create api_gateway/app/ scaffold (registry.py, routing.py, proxy.py, middleware/...).
2. Add correlation ID middleware across existing services.
3. Establish proto repository + define messages: MoodEntryCreated, JournalEntryCreated, CrisisAlertRaised.
4. Add NATS to docker-compose; implement publisher in mood & journal service (dual write to DB + event).
5. Multilingual service skeleton: /detect & /sentiment (English stub, Hindi placeholder) + tests.
6. Service JWT issuing endpoint in auth (/service-token) + gateway service-to-service auth header injection.
7. Documentation: update README with architecture diagram (V3 high-level).

---
## 20. Open Decisions / Inputs Needed
- NATS vs Kafka final (default: NATS Phase 1).
- Vector store: pgvector vs dedicated (Milvus/Weaviate) – propose pgvector Phase 1.
- RAFT implementation: Python raftos vs Go sidecar (performance vs language consistency) – leaning Go sidecar for latency.
- Translation provider fallback (OpenAI / DeepL / local model) – choose initial provider.

---
## 21. KPIs & Success Metrics
- <300ms p95 gateway proxy latency.
- >95% translation cache hit for repeated phrases after warmup.
- <1% duplicate notifications (content hash collisions accepted <0.1%).
- Crisis alert escalation detection latency <10s p95.
- Journal enrichment throughput parity with ingestion (lag < 2m at 95th percentile).

---
## 22. Risk Mitigation
- Dual-write with reconciliation script for event drift detection.
- Feature flag kill-switch for orchestrator automated actions.
- Back-pressure strategy: drop low-priority enrichment tasks first.
- Privacy guard fallback: if redaction fails → block LLM tool call.

---
## 23. Next Step
Await confirmation on open decisions to begin scaffold (Sprint 1 tasks).

---
*End of V3 Plan*
