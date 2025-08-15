# Phase 2 Updated Implementation Roadmap (Code‑Aligned)

Source of truth: Derived from actual code base (backend/services, shared models, frontend unifiedInsightService, community service, ML service) + existing Phase 2 intent. Adjusted for what exists vs. what is only planned. Multilingual & real‑time scope is right‑sized to incremental, testable slices.

## Guiding Principles
1. Ship vertical slices: DB → backend endpoint → frontend integration → telemetry.
2. Avoid big bang multilingual refactor; start with language preference capture + passive translation pipeline.
3. Reuse existing unifiedInsightService (client side) until server‑side aggregator proves necessary.
4. Introduce streaming abstractions behind an interface; Kafka optional (feature flag) until production scale.
5. Observability baked into each epic (metrics + structured logs).

## Current Gaps (From Code Inspection)
- No user language preference table or model.
- No translation_service actual implementation files (directory present only as placeholder).
- unifiedInsightService aggregates client‑side; backend lacks unified insight endpoint.
- Celebration / achievements logic fragmented (frontend computes thresholds, backend only stores moments).
- ChallengeLeaderboard model unused; leaderboard computed ad hoc.
- No real websocket layer for insights; only ML service background loop.
- No scheduling executor for ScheduledNotification -> Notification promotion exposed.

## Epic Breakdown
E1: Multilingual Foundations
E2: Insight Data Quality & Unified Backend Aggregation
E3: Achievement & Engagement Cohesion
E4: Real‑Time Incremental Pipeline
E5: Advanced Sentiment & Translation Iteration
E6: Performance, Caching & Leaderboards
E7: Observability, Security & Hardening

---
## E1 Multilingual Foundations (Week 1)
Goal: Persist user language + expose preferences through auth/user profile endpoints; passive (no live translation yet).

Tasks:
1. DB Migration
   - Create Alembic migration: user_language_preferences (subset fields: user_id, primary_language, secondary_languages JSON, auto_detect_language, cultural_region, created_at/updated_at).
   - Add index on (user_id).
2. Shared Model
   - Add SQLAlchemy model UserLanguagePreference in shared/models.py (avoid large schema from doc initially).
3. Backend API (profile or new translation service minimal)
   - Endpoint: GET /user/language-preferences -> current preferences.
   - Endpoint: POST/PUT /user/language-preferences -> upsert.
   - Auth: reuse get_current_user.
4. Frontend Integration
   - Create hook useLanguagePreferences (fetch, optimistic update).
   - Add minimal LanguageSelector (list of languages constant) in header / profile dialog.
5. Telemetry
   - Log preference changes (structured JSON: event=language_pref_update user_id primary_language secondary_count).
6. Acceptance Criteria
   - User can set & retrieve primary language; persists across reload.
   - 95% success under concurrent updates (manual test with 5 parallel requests).

Dependencies: Alembic setup (ensure migrations folder), add env.* variable DEFAULT_LANGUAGE fallback.
Risks: Overcomplex initial schema -> keep MVP minimal.
Mitigation: Feature flag ADVANCED_LANGUAGE_SCHEMA for later.

---
## ## E2 Unified Insight Backend (Week 2) ✅ **COMPLETE**
**Goal**: Provide server endpoint /api/v1/insights/unified replicating client merge logic → reduce frontend coupling.

**Status**: ✅ **IMPLEMENTED AND TESTED**

**Completed Tasks**:
1. ✅ **Backend Service** - Implemented aggregator module in `ml_service/integrations/`
   - ✅ Collects mood stats, ML personalized insights, pattern analysis 
   - ✅ Cache layer (in‑process dict TTL 120s) keyed by user_id
   - ✅ Enhanced aggregator with ML model integration available
2. ✅ **Endpoint** - `/api/v1/insights/unified` returns structure matching frontend contract
3. ✅ **Frontend Refactor** - unifiedInsightService attempts server endpoint first; fallback works
   - ✅ Version param and header X-Insight-Version implemented
4. ✅ **Data Quality & Confidence** - compute_quality(sources) function working in backend
5. ✅ **Tests** - Unit tests and integration tests verify functionality
6. ✅ **Acceptance Criteria** - All criteria verified:
   - ✅ Frontend unchanged visually; network waterfall reduced (parallel → single call)
   - ✅ Cache hit reduces backend subcall count (log metric insights_aggregate_subcalls)
   - ✅ Feature flag `USE_SERVER_UNIFIED_INSIGHTS=True` enables endpoint

**Evidence**: See `/docs/E2_IMPLEMENTATION_COMPLETE.md` for detailed verification report.

Risks: Circular import between services. Mitigation: aggregator only uses shared DB queries + direct function calls; avoid internal HTTP.

---
## E3 Achievement & Engagement Cohesion (Week 3)
Goal: Consolidate achievements logic server side and align celebration + challenge + community engagement.

Tasks:
1. Schema Adjustments (Optional initial)
   - Add table user_achievement_progress (id, user_id, key, current_value, target_value, unlocked_at).
2. Backend Logic
   - Service module achievements_engine.py: rules (first_mood_entry, seven_day_streak, thirty_entries, celebration_levels, community_posts_count, challenge_streak >= X).
   - Batch recompute function recompute_user_achievements(user_id).
   - Endpoint GET /api/v1/achievements returns list with progress + unlocked.
3. Frontend Refactor AchievementsPage
   - Replace local dynamicAchievements with API response; retain fallback if 404.
4. Event Triggers
   - Hook inside mood creation, challenge progress update, community thread creation to call async enqueue_achievement_recalc(user_id) (simple thread executor initially).
5. Metrics
   - achievement_rule_eval_ms, achievements_unlocked_total per rule.
6. Acceptance
   - Achievements page shows server derived values identical to previous client calculation for existing rules.

Risks: Performance of recompute. Mitigation: Rule deltas (pass event type to engine, update only affected counters).

---
## E4 Real‑Time Incremental Pipeline (Weeks 4–5)
Goal: Introduce minimal streaming abstraction without full Kafka dependency.

Slices:
1. Abstraction Interface
   - module shared/events.py with EventBus interface (publish(event), subscribe(channel, handler)).
   - In-memory implementation (asyncio.Queue) default; env flag USE_KAFKA for later.
2. Event Emission
   - Publish events: mood_entry_created, journal_entry_created, challenge_progress_updated, community_post_created.
3. Real-Time Insight Delta Processor (ml_service)
   - Listener updates small cache (recent mood streak, average last 7, engagement delta) and emits insight_delta event.
4. WebSocket Gateway (new lightweight service websocket_gateway or module in ml_service)
   - Endpoint /ws/insights -> pushes serialized delta messages.
5. Frontend Hook useRealtimeInsights
   - Subscribes; merges deltas into existing insights state (optimistic update of weeklySummary.daysTracked, moodStreak, achievements just unlocked).
6. Acceptance
   - When user logs new mood entry, dashboard’s tracked days increments within <1s (dev baseline).

Risks: Thread safety. Mitigation: Use asyncio locks around shared cache updates.

---
## E5 Advanced Sentiment & Translation Iteration (Weeks 6–7)
Goal: Add language detection + stub translation + sentiment per language (no deep cultural mapping yet).

Tasks:
1. Language Detection
   - Utility detect_language(text) using fast heuristic (langdetect) → store original_language on JournalEntry & MoodEntry notes (add column original_language nullable).
   - Migration to add original_language columns.
2. Sentiment Per Language
   - Extend ML weekly summary: group mood/journal by language counts.
   - Store summary snapshot (no new table yet) returned in unified insights under metadata.languageBreakdown.
3. Translation Service MVP
   - Directory backend/services/translation_service/
   - File main.py with /translate (POST) {text, target_lang} returning stub (echo) unless DIFFERENT lang → placeholder + note.
   - Integrate into aggregator: if user primary_language != entry.original_language add translation stub in journaling insights.
4. Frontend Optional Translation Toggle on journal list item.
5. Acceptance
   - Journal entries capture detected language.
   - Unified insights includes languageBreakdown and translationAvailable flags.

Risks: Performance impact of detection. Mitigation: Detect only if >20 chars and no cached detection.

---
## E6 Performance, Caching & Leaderboards (Week 8)
Goal: Optimize hotspots identified (challenge leaderboard, community N+1 queries, insights caching) + implement ChallengeLeaderboard usage.

Tasks:
1. Challenge Leaderboard Materialization
   - Nightly (or on progress update) update ChallengeLeaderboard rows with denormalized stats.
   - Modify /forums/challenges/{id}/leaderboard endpoint to read from ChallengeLeaderboard (fallback to on-the-fly if missing row).
2. Query Optimization
   - Add selective eager loading for thread author & reply counts (use subquery for counts instead of counting inside loop).
3. Insight Cache Externalization
   - Replace in‑process with Redis if REDIS_URL set.
4. Add DB Indexes
   - challenge_progress (challenge_id, user_id, date)
   - forum_threads (forum_id, created_at)
5. Benchmarks Script scripts/perf_insights.py to measure aggregate latency with & without cache.
6. Acceptance
   - Leaderboard endpoint P95 latency < 120ms for 1k participants (synthetic seeded data).
   - Unified insights endpoint returns cached response on second call (log cache_hit=true).

Risks: Cache invalidation complexity. Mitigation: Simple key delete on relevant event publish.

---
## E7 Observability, Security & Hardening (Parallel / Final)
Goal: Production readiness of new features.

Tasks:
1. Structured Logging Standard
   - Helper log_event(service, action, user_id, **fields) central in shared/logging.py.
2. Metrics Endpoints
   - /metrics (Prometheus) on ml_service & community_service exposing counters & histograms (fastapi_instrumentator).
3. Rate Limiting
   - Simple token bucket for high‑mutation endpoints (mood create, challenge progress) via dependency.
4. Security Review
   - Remove debug endpoints /debug/auth /debug/test-thread-creation or guard behind ENV DEBUG_ENABLED.
5. Alerting
   - Basic health check script + GitHub Action to hit /health & /api/v1/insights/unified daily.
6. Acceptance
   - All new endpoints return 401 without token.
   - No debug endpoints exposed in prod build.

---
## Cross‑Epic Supporting Work
- Documentation: Update /docs with endpoint specs after each epic (short OpenAPI excerpt + examples).
- Migration Log: Maintain migrations/README with applied hashes.
- Feature Flags: SIMPLE dict in shared/feature_flags.py (read env); flags: USE_SERVER_UNIFIED_INSIGHTS, USE_EVENT_BUS_KAFKA, ENABLE_TRANSLATION_MVP.
- Testing Strategy:
  - Unit: achievement rules, aggregator merges, language detection util.
  - Integration: unified insights endpoint, real-time delta flow.
  - E2E (later): mood entry → websocket delta → dashboard update.

## Dependency Map
E1 → (E2, E5). E2 → (E3, E4). E3 uses E2 outputs. E4 depends on minimal events from E2/E3. E5 builds on E1 (language data). E6 can start after E2 baseline. E7 spans all.

## Risk Register (Focused)
| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| Overengineering translation early | Delays core insights | Medium | MVP stub, iterate |
| Cache inconsistency unified insights | Stale UI | Medium | TTL + event invalidation |
| Leaderboard write amplification | DB load | Low | Batch recompute, not per request |
| Real-time queue backpressure | Latency | Medium | Backpressure metrics + drop policy for low priority |
| Rule drift (achievements) | User confusion | Medium | Central rule metadata & versioning |

## Acceptance Metrics Summary
- Unified insights P95 < 300ms (warm), < 600ms (cold).
- Real-time delta latency < 1s dev environment.
- Achievement recompute < 150ms for standard user (100 mood entries, 10 challenges).
- Cache hit ratio unified insights > 60% after 5 min steady state.

## Initial Sequencing (Calendar)
Week1: E1
Week2: E2 (start), partial E7 logging baseline
Week3: Finish E2, implement E3
Weeks4-5: E4 real-time slices incrementally
Week6-7: E5 advanced language + sentiment extensions
Week8: E6 performance + wrap E7 hardening

## Immediate Next Actions (Day 0)
1. Create migration + model for user_language_preferences.
2. Scaffold unified insights endpoint returning current client merge.
3. Draft achievements_engine with basic rules (mood_first, mood_7, mood_30, challenge_participation_1).

---
Prepared: 2025-08-13
