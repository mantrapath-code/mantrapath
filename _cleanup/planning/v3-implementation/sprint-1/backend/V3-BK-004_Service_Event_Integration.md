# V3-BK-004: Service Event Integration — Implementation Plan

Owner: Mid Dev 2  |  Priority: P0  |  Points: 8  |  Sprint: 1

## Summary
Integrate core services with the V3 event-driven architecture so all user interactions (mood, journal, chatbot) are emitted and consumed in real time. Keep backward compatibility with the existing in-memory bus while enabling the Enhanced NATS Event Bus with JetStream.

Acceptance criteria mapping:
- Mood service publishes voice-aware events → mood.entry.created (+ optional voice_context)
- Journal service emits AI-ready events → journal.entry.created (includes sentiment, themes)
- Chatbot service coordinates with other services → subscribes to voice/mood/journal events and shares context
- Real-time processing across services → cross-service consumers on NATS ensure <100ms propagation locally

---

## Current Architecture Assessment
- Event buses:
  - Legacy: `backend/shared/events.py` provides `InMemoryEventBus`, `EventChannels`, and helpers like `publish_mood_entry_created`, `publish_journal_entry_created`.
  - V3 Enhanced: `backend/shared/events/enhanced_bus.py` provides `EnhancedEventBus` (NATS-enabled), `V3EventChannels`, and helpers to publish voice/AI/cultural events.
  - NATS integration: `backend/shared/events/nats_bus.py` and Docker Compose `backend/docker-compose.yml` run `nats:2.10-alpine` with JetStream using `backend/config/nats.conf`.
- Relevant services:
  - Mood Service (`backend/services/mood_service/main.py`): already publishes legacy events when `USE_EVENT_BUS` flag is on.
  - Journal endpoints live inside Mood Service: also publish legacy events.
  - Chatbot Service (`backend/services/chatbot_service/main.py`): no event bus integration yet (uses Redis, FastAPI).
  - Translation Service (`backend/services/translation_service/main.py`): already uses `get_enhanced_event_bus()` and `V3EventChannels`.
  - ML Service (`backend/services/ml_service/main.py`): subscribes to legacy channels via `get_event_bus()` and `EventChannels`.

Run/dev:
- Docker dev: `backend/start-dev.sh` starts NATS and services via Compose.
- VS Code tasks: API Gateway dev and Translation Service dev are available; others run via Docker or service-specific entrypoints.

---

## Target Event Channels (V3)
To align with planning and keep streams organized:
- mood.entry.created (general stream)
- journal.entry.created (general stream)
- voice.intent_classified (voice stream; already defined in V3 events)
- intelligence.context_shared (optional for chatbot context propagation)

Backward compatibility:
- Continue publishing legacy `EventChannels.MOOD_ENTRY_CREATED` and `EventChannels.JOURNAL_ENTRY_CREATED` until all consumers migrate. During this sprint, dual-publish to both legacy and V3 channels.

---

## Minimal Schemas
### mood.entry.created
- id, user_id
- mood_score, energy_level, stress_level, sleep_quality
- emotional_granularity, mood_confidence
- context_tags[], created_at (ISO)
- voice_context? (optional)
  - activity_event_id, emotion_confidence{}, language_detected, quality_score

### journal.entry.created
- id, user_id
- title, content (short), sentiment_score, sentiment_label, themes[]
- mood_before?, mood_after?
- is_private, created_at (ISO)
- ai_ready: { language?, tokens?, processing_notes? } (optional, allow expansion later)

---

## Service-Level Changes

### 1) Mood Service — voice-aware publishing
Files: `backend/services/mood_service/main.py`
- On `create_mood_entry`:
  - Keep legacy publish: `publish_mood_entry_created(...)` (already present under `USE_EVENT_BUS`).
  - Add V3 publish via Enhanced Bus: `get_enhanced_event_bus().publish("mood.entry.created", payload, user_id)`.
  - Include `voice_context` if available (optional fields; safe to omit).
- Feature flags/env:
  - `USE_NATS_EVENT_BUS=true` (default) enables Enhanced Bus; falls back gracefully.
  - Keep `USE_EVENT_BUS=true` for legacy path until migration completes.

### 2) Journal (inside Mood Service) — AI-ready publishing
Files: `backend/services/mood_service/main.py`
- On `create_journal_entry`:
  - Keep legacy publish: `publish_journal_entry_created(...)` (already present under `USE_EVENT_BUS`).
  - Add V3 publish: `get_enhanced_event_bus().publish("journal.entry.created", payload, user_id)` including sentiment and themes already computed.
  - Optional `ai_ready` section for future enrichment (tokens/language) without breaking schema.

### 3) Chatbot Service — cross-service coordination
Files: `backend/services/chatbot_service/main.py`
- Initialize Enhanced Event Bus once on startup; subscribe to:
  - `voice.intent_classified`: cache last intent per user; optionally trigger supportive reply generation in background.
  - `mood.entry.created` and `journal.entry.created`: store last mood/journal summary in Redis for context-aware responses.
- Publish `intelligence.context_shared` when the chatbot updates user context (optional, small payload).
- Keep behavior no-op if NATS is unreachable (Enhanced Bus falls back gracefully).

### 4) Cross-Service Consumers — ensure real-time processing
- ML Service: extend subscriptions to also listen to `mood.entry.created` and `journal.entry.created` (V3) in addition to legacy channels it already consumes. Keep handlers pointing to existing processors.
- Optional Bridge (if needed later): lightweight re-publisher subscribing to legacy and publishing to V3 (or vice versa). Not required if dual-publish is implemented at the producer side as above.

---

## Testing Plan
- Unit tests (fast): validate V3 payloads built in mood/journal handlers (shape, required fields, optional voice_context).
- Integration tests (async):
  - Start NATS via Compose.
  - Use `get_enhanced_event_bus()` to subscribe to `mood.entry.created` and `journal.entry.created`, trigger API calls, and assert receipt within 100–300ms locally.
- Chatbot subscription test: spin service with test handler to verify it reacts to events without blocking request path.

Suggested pytest targets:
- `tests/services/test_bk004_events.py` (new, async with `pytest-asyncio`)
- Include coverage for dual-publish (legacy and V3) and consumer receipts.

---

## Dev/Run Instructions
- Ensure NATS is running: `backend/start-dev.sh` (Docker) will start `nats:2.10` with JetStream.
- Env vars:
  - `USE_EVENT_BUS=true` (legacy) — keeps current ML consumers working.
  - `USE_NATS_EVENT_BUS=true` — enables Enhanced Bus in producers/consumers.
  - `NATS_SERVERS=nats://localhost:4222` (default).
- Local smoke:
  - Create mood entry and journal entry via existing API routes; tail service logs to see V3 publish confirmations.

---

## Acceptance Criteria Checklist
- [ ] Mood service publishes `mood.entry.created` with optional `voice_context` and legacy event still emitted
- [ ] Journal service publishes `journal.entry.created` with sentiment/themes and legacy event still emitted
- [ ] Chatbot subscribes to `voice.intent_classified`, `mood.entry.created`, `journal.entry.created` and updates context
- [ ] ML service consumes V3 channels in addition to legacy
- [ ] Integration test demonstrates real-time flow E2E

---

## Task Breakdown (timebox)
1) Mood service V3 publish (dual-publish + voice_context hook) — 2h
2) Journal service V3 publish (dual-publish + ai_ready stub) — 2h
3) Chatbot subscriptions + background handlers — 2h
4) Cross-service consumers (ML add V3 subs) — 1h
5) Integration tests + docs — 1h

---

## Risks & Mitigations
- Duplicate processing due to dual-publish → Consumers made idempotent by `event_id` or by processing keys; ML keeps one handler path per payload type.
- NATS not available locally → Enhanced Bus falls back; still verify legacy path keeps system functional.
- Payload drift → Keep schemas minimal; optional blocks for voice/AI fields; validate in tests.

---

## Implementation Notes (code pointers)
- Mood/Journal V3 publish sites:
  - `backend/services/mood_service/main.py` in `create_mood_entry` and `create_journal_entry`
- Chatbot subscriptions (lifespan or startup hook):
  - `backend/services/chatbot_service/main.py` — add async startup init that subscribes to events and caches recent context
- ML service V3 consumers:
  - `backend/services/ml_service/main.py` — add `await bus.subscribe("mood.entry.created", ...)` and `await bus.subscribe("journal.entry.created", ...)` near existing legacy subscriptions

This plan keeps services running as-is while introducing V3 NATS-backed channels, enabling real-time, cross-service coordination without breaking existing consumers.
