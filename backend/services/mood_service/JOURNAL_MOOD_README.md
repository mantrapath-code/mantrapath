# Truth or Dare Integration Guide (Mood & Journal Services)

This document captures the end-to-end implementation plan for integrating the Truth or Dare wellness challenge with the unified journal/mood pipeline. It combines reference material (endpoints, defaults) with step-by-step tasks so engineers can execute the rollout.

---

## Table of Contents

- [Phase Overview](#phase-overview)
- [Phase 1 – Journal Pipeline Readiness](#phase-1--journal-pipeline-readiness)
- [Phase 2 – Authentication Alignment](#phase-2--authentication-alignment)
- [Phase 3 – Game Flow Enhancements](#phase-3--game-flow-enhancements)
- [Phase 4 – Analytics & Telemetry](#phase-4--analytics--telemetry)
- [Phase 5 – Documentation & Client Updates](#phase-5--documentation--client-updates)
- [Deployment Checklist](#deployment-checklist)
- [Reference: Service Endpoints](#reference-service-endpoints)
- [Reference: Computed Values & Defaults](#reference-computed-values--defaults)
- [Next Steps & Risks](#next-steps--risks)

---

## Phase Overview

1. **Journal Pipeline Readiness**
   - Implement richer payload contract.
   - Ensure journal GET returns data (complete ✅).
   - Validate schema and migrations.

2. **Authentication Alignment**
   - Trust upstream bearer tokens.
  - Remove redundant auth logic.

3. **Game Flow Enhancements**
   - Update journal service to feed Truth/Dare.
   - Load level metadata.
   - Generate tailored tasks with fallback support.

4. **Analytics & Telemetry**
   - Capture engagement metrics.
   - Monitor fallback usage.

5. **Documentation & Client Updates**
   - Align frontends with new contract.
   - Publish developer references.

Each phase builds on the previous. The rest of the document dives into executor-level detail for every phase.

---

## Phase 1 – Journal Pipeline Readiness

### 1. Confirm Journal GET (Done)
- ✅ `GET /api/v1/journal/` now returns real entries ordered by `created_at DESC`.
- Verify the frontend hits the root path (preferred) and handles pagination (`limit`, `offset`).

### 2. Expand Journal Create Contract
- Update the POST handler to validate the new schema:
  ```json
  {
    "title": "string?",
    "content": "string (required)",
    "mood_before": 1-5?,
    "mood_after": 1-5?,
    "is_private": true|false (default true),
    "entry_type": "text"|"video",
    "video_analysis": { ...MoodAnalysisResult }
  }
  ```
- Store `video_analysis` JSON as-is; no transformations.
- Consider indexing `video_analysis->primary_emotion` or storing it in a separate column if queries require it.

### 3. Schema Audit & Migration
- Ensure `journal_entries` table has columns for `entry_type`, `video_analysis`, mood fields.
- If older records lack these columns, run migrations/backfills:
  - Set `entry_type` to `"text"` where null.
  - Leave `video_analysis` as `NULL` unless video entries exist.
  - Keep `mood_before` and `mood_after` as `NULL` when unknown.
  - `is_private` defaults to `true` (already enforced).

### 4. Frontend Contract Update
- Modify journal form (and future unified reflection form) to send the enriched payload.
- For video submissions, call `/api/v1/mood/analyze` or other media pipeline to produce `video_analysis` before POSTing.
- Document error responses so the UI can surface validation issues clearly.

---

## Phase 2 – Authentication Alignment

### 1. Middle Layer Token Parsing
- Introduce FastAPI dependency/middleware that:
  - Extracts the bearer token.
  - Validates signature (if required) or trusts upstream gateway.
  - Populates `current_user` with `user_id`, `role`, etc.
- Remove or disable local `/api/auth/*` endpoints if authentication is entirely delegated upstream.

### 2. Authorization Checks
- Verify all routes (mood, journal, Truth/Dare game) use the token-derived `user_id`.
- Private entries (`is_private=true`) must remain accessible only to their owners; ensure join queries respect this.
- Log auth failures clearly for observability.

---

## Phase 3 – Game Flow Enhancements

### 1. Level Metadata Loader
- Load `data/levels.json` at app startup (singleton service or config).
- Provide helper functions to retrieve:
  - Level name, XP range, descriptions.
  - Example truth/dare prompts per level.
- Keep JSON under version control for easy updates.

### 2. Journal Service for Truth/Dare
- Extend or create a service method that:
  - Filters journal entries by `entry_type`, recency, and `is_private=false` (or owner match).
  - Exposes `video_analysis.primary_emotion` / `primary_sentiment`, plus mood deltas.
  - Orders entries to highlight negative/high-impact content first.
  - Returns both text and video entries; fall back to text when video analysis missing.

### 3. Fallback Journals
- If fewer than three qualifying entries exist:
  - Load items from `data/mock_journals.json` (ensure the file matches the new schema).
  - Log fallback usage for monitoring.

### 4. LLM Prompt Generation
- Update `llm_service.generate_truths_and_dares()` to consume:
  - Level metadata (e.g., current XP → level).
  - Themes/primary emotions from journals.
  - Mood delta context (`mood_before` → `mood_after`).
- Include safe-guard to prevent exposing private entry content in prompts shown to other users.

### 5. Task completion flows
- `POST /api/game/submit_truth` & `/submit_dare` should:
  - Validate submission payload.
  - Update XP using level metadata (check level boundaries).
  - Issue badges or achievements if thresholds met.
  - Record analytics (completion time, mood changes, etc.).
- Consider rate limiting or idempotency guards if submissions can be retried.

---

## Phase 4 – Analytics & Telemetry

### 1. Operational Metrics
- Instrument counters/metrics for:
  - Journal entries ingested for Truth/Dare.
  - Fallback usage frequency.
  - Task completion rates, XP progression, badge unlocks.
- Extend `/api/v1/metrics` or export Prometheus metrics as needed.

### 2. Mood Delta Insights
- Optionally extend mood analytics to summarize how gameplay affects `mood_after` vs `mood_before`.
- Could be exposed through a new endpoint or reused by admin dashboards.

### 3. Logging
- Log key context: user ID, entry ID, level, fallback usage, LLM latency (for monitoring).
- Ensure logs omit sensitive journal content when not necessary.

---

## Phase 5 – Documentation & Client Updates

### 1. Developer Docs
- Update API docs (this file + general README) with journaling contract and Truth/Dare flow.
- Provide sample requests/responses for the game endpoints.

### 2. Client Alignments
- Modify frontends/mobile apps to:
  - Send bearer tokens only (no local login).
  - Use the enriched journal payload (including `entry_type`, `video_analysis`).
  - Respect private entries and error messages.
- Add QA coverage for video entries, mood deltas, and fallback content.

---

## Deployment Checklist

- [ ] Populate `data/levels.json` with final content.
- [ ] Audit/migrate journal schema for new fields.
- [ ] Remove or guard legacy auth routes.
- [ ] Ensure CORS/session config matches parent application.
- [ ] Update frontends to send the new payload and token.
- [ ] Re-run integration tests: journal create/list, game start, truth/dare submission.
- [ ] Monitor logs/metrics post-deployment for fallback usage and errors.

---

## Service Project Layout

Use this as the canonical map of the Truth or Dare service when it runs as a standalone Flask app.

| Path | Role |
|------|------|
| `app.py` | Monolithic Flask application hosting all API routes, service bootstrapping, logging, and helper utilities. |
| `auth.py` | Local authentication helpers (bcrypt hashing, username validation, Flask-Login integration). Present even when auth is delegated upstream. |
| `config.py` | Loads `.env` via `python-dotenv`; exposes Gemini, MongoDB, Flask, and XP thresholds through `Config`. |
| `database.py` | MongoDB wrapper for users, sessions, task completions, badges. Requires MongoDB. |
| `services/` | Business logic helpers (`journal_service`, `llm_service`, `validation_service`, `badge_service`, `cache_service`, `emotion_service`, `frontend_emotion_service`). |
| `data/levels.json` | Canonical level metadata (seed → diamond). Loaded at startup. |
| `data/mock_journals.json` | Fallback journal entries when live data is unavailable. Currently the only journal source. |
| `templates/index.html` | Standalone HTML/JS test page for manual testing (no bundler). |
| `test.py` | Experimental Flask app targeting external mood/journal APIs (`https://139.84.213.185/api`). Not part of the production flow. |
| `run.sh` / `run.bat` | Convenience scripts to launch the Flask server with required env vars. |
| `requirements.txt` | Python dependencies (Flask, Flask-Login, pymongo, redis, google-genai, bcrypt, python-dotenv, etc.). |
| `TRUTH_OR_DARE_DOC.md` | Integration guide focused on the new journal payload and upstream auth hand-off. |
| `TRUTH_OR_DARE_OVERVIEW.md` | Structural/API documentation (single-file service reference). |

> No React/Vite build artifacts are shipped. UI is limited to `templates/index.html` and the experimental `test.py`.

---

## Truth or Dare API Surface

### Health & Metadata

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Service status, DB/Redis connectivity, timestamp. |
| `GET` | `/api/levels/info` | Exposes level copy/icons from `data/levels.json`. |

### Authentication (optional if upstream handles tokens)

| Method | Path | Notes |
|--------|------|-------|
| `POST` | `/api/auth/register` | Local username/password registration via `AuthService`. |
| `POST` | `/api/auth/login` | Verifies credentials, issues Flask-Login session. |
| `POST` | `/api/auth/logout` | Clears the session. |
| `GET` | `/api/auth/me` | Returns user stats (requires session). |

### Game Lifecycle

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/game/start` | Starts/resumes a session. Loads journals, generates truths/dares with Gemini, caches results, persists session in Mongo. Supports `force_new`, `override_level`, `resume_session_id`. |
| `GET` | `/api/game/session/<session_id>` | Returns raw session document from Mongo. |
| `POST` | `/api/game/submit_truth` | Validates response (word count, emotion analysis), awards XP, updates session, recalculates badges. |
| `POST` | `/api/game/submit_dare` | Dare-specific validation, proof handling, XP updates. |
| `POST` | `/api/cache/clear` | Clears cached game content for a user/level pair. |

### User Insights & Badges

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/user/<user_id>` | Returns user document. |
| `GET` | `/api/user/<user_id>/sessions` | Lists prior sessions (`limit` optional). |
| `GET` | `/api/user/<user_id>/level-progress` | Aggregated completions per level. |
| `GET` | `/api/session/<session_id>/completions` | Detailed task analytics. |
| `GET` | `/api/user/<user_id>/progress` | Combines XP totals, badges, level history, upcoming requirements. |
| `GET` | `/api/badges` | Lists badge configurations from `badge_service`. |
| `POST` | `/api/user/<user_id>/equip-badge` | Marks a badge as equipped (must be unlocked). |

### Developer Utilities

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/dev/toggle-levels` | Toggle developer mode (bypass level locks). |
| `POST` | `/api/dev/set-xp` | Force-set XP and recalc level. |
| `POST` | `/api/dev/reset-progress` | Reset user progress to seed level. |

> Dev endpoints only guard on `Config.DEBUG`; remove or harden in production.

---

## Supporting Services & Assets

### Runtime Architecture
1. **Boot (`app.py`)** – Configures logging, loads `Config`, initialises Flask, Flask-Login, CORS, and instantiates global services (`database`, `journal_service`, `llm_service`, `cache_service`, `auth`).
2. **Persistence (`database.py`)** – MongoDB wrapper for users, sessions, completions, badges. Journals still read from `data/mock_journals.json` until the new pipeline is wired in.
3. **External Integrations** – Gemini (truth/dare generation, emotion analysis); optional Redis caching.
4. **Authentication** – Local username/password flow exists but can be bypassed when tokens come from the parent platform.

### Service Modules

| File | Purpose | Notes |
|------|---------|-------|
| `services/journal_service.py` | Loads mock journals, scores them via Gemini. Placeholder until real journal ingestion arrives. |
| `services/llm_service.py` | Calls Gemini to produce truths/dares using journal context & level metadata. |
| `services/validation_service.py` | Validates truth/dare submissions (word count, coherence, authenticity penalties). |
| `services/emotion_service.py` | Text emotion analysis via Gemini; falls back to neutral when parsing fails. |
| `services/frontend_emotion_service.py` | Handles sentiment data supplied by clients (currently unused). |
| `services/badge_service.py` | Calculates badge progression/dominant XP categories from Mongo stats. |
| `services/cache_service.py` | Redis wrapper for caching generated content (no-op when Redis unavailable). |

### Frontend Assets
- `templates/index.html` – Static HTML/JS testbed using `fetch`. Useful for manual QA, not production.
- `test.py` – Experimental Flask app hitting external mood/journal APIs (`https://139.84.213.185/api`). Separate from main service.
- **Missing** – No React/Vite frontend or build pipeline.

### Known Gaps
- `JournalService` still consumes `data/mock_journals.json`; integrate with the unified journal API as part of Phase 3.
- Auth routes remain even when upstream tokens are used; remove or bypass as needed.
- Error handling often returns generic `500`s; layer more granular responses for clients.
- No automated tests; add pytest/integration coverage (XP awards, badge logic, fallback flows).
- Dev endpoints rely solely on `Config.DEBUG`; harden or remove before launch.
- `GEMINI_API_KEY` must be set; services fail otherwise.
- `video_analysis` fields are expected but not yet used—wire them into journal selection once upstream supplies them.

---

## Reference: Service Endpoints

### Health & Info
- `GET /api/v1/health`
- `GET /api/v1/info`
- `GET /api/v1/metrics`
- `GET /health`

### Mood Entry Management
- `POST /api/v1/mood/entries`
- `GET /api/v1/mood/entries`
- `GET /api/v1/mood/entries/{entry_id}`
- `PUT /api/v1/mood/entries/{entry_id}`
- `DELETE /api/v1/mood/entries/{entry_id}`

### Emotion Analysis
- `POST /api/v1/mood/analyze`

### Mood Analytics
- `GET /api/v1/mood/analytics/overview`
- `GET /api/v1/mood/analytics/patterns`
- `POST /api/v1/mood/context`
- `GET /api/v1/mood/context`

### Journal Management
- `POST /api/v1/journal/`
- `GET /api/v1/journal/`
- `POST /api/v1/journal/entries`
- `GET /api/v1/journal/entries`
- `GET /api/v1/journal/entries/{entry_id}` (placeholder 404)
- `PUT /api/v1/journal/entries/{entry_id}` (501 planned)
- `DELETE /api/v1/journal/entries/{entry_id}` (501 planned)

### Legacy Redirects
- `/mood` → `/api/v1/mood/entries`
- `/analyze` → `/api/v1/mood/analyze`

---

## Reference: Computed Values & Defaults

See original sections for full details. Highlights:

- **Mood defaults**: `mood_score`, `stress_level`, `energy_level` default to 5; `emotional_granularity`=3; `mood_confidence`=1.0.
- **Emotion analysis**: GoEmotions model; fallback returns neutral/50%; cached in Redis with TTL 3600s.
- **Analytics**:
  - Mood trend thresholds ±0.2.
  - Weekly pattern slope thresholds ±0.1.
  - Recommendations triggered for low averages (<4.0) or recurring negative dominant emotions.
- **Journal defaults**:
  - `is_private` true.
  - `entry_type` default `"text"`.
  - `sentiment_score/label`, `themes`, `word_count`, `reading_time` stored but not auto-populated yet.
- **Frontend journal analytics**: Uses client-side sentiment when backend doesn’t supply values; ensure unified flow sets them intentionally.

---

## Next Steps & Risks

| Risk | Mitigation |
|------|------------|
| Insufficient journal data | Maintain `mock_journals.json`; prompt users to write entries. |
| Payload mismatch | Enforce validation with clear 400 responses; update clients simultaneously. |
| Auth token issues | Version token parser; rollout via feature flag; log parsing errors. |
| LLM latency | Cache prompts per level; pre-generate truth/dare sets. |
| Analytics skew | Collect real mood slider values to avoid defaults dominating averages. |

**Timeline suggestion (high level)**:
1. Week 1 – Journal schema & payload updates.
2. Week 2 – Auth middleware, level metadata loader.
3. Week 3 – Game service adjustments, LLM integration.
4. Week 4 – Analytics/telemetry, QA, deployment.

Revisit this document as tasks complete; treat it as the source of truth for Truth/Dare integration within the mood/journal ecosystem.

---

These routes help with health checks, service discovery, and lightweight metrics.

### `GET /api/v1/health`
- **Purpose:** Validate connectivity to PostgreSQL, Redis, and the emotion-analysis model.
- **Response:** `{"status": "healthy"|"degraded", "timestamp": "...", "version": "...", "dependencies": {...}}`

### `GET /api/v1/info`
- **Purpose:** Return service metadata, advertised endpoints, and feature toggles.
- **Response:** `{"name": "...", "version": "...", "description": "...", "endpoints": [...], "features": {...}}`

### `GET /api/v1/metrics`
- **Purpose:** Provide a lightweight metrics snapshot (service, version, UTC timestamp). Designed to be extended with real telemetry.

### `GET /health`
- **Purpose:** Root-level health endpoint used by Docker and external load balancers. Returns `{"status": "healthy", "service": "mood-service"}`.

---

## Mood Entry Management

### `POST /api/v1/mood/entries`
- **Purpose:** Create a new mood entry and automatically attach emotion analysis when text is provided.
- **Body (JSON):**
  ```json
  {
    "mood_score": 1-10,
    "stress_level": 1-10,
    "energy_level": 1-10,
    "sleep_quality": 1-10,
    "description": "Optional text used for analysis",
    "notes": "Legacy text field",
    "input_text": "Alternative text field",
    "input_type": "text" | "voice",
    "language": "ISO code",
    "context_tags": ["work", "family"],
    "location": "string",
    "activity": "string",
    "emotional_granularity": 1-5,
    "mood_confidence": 0.0-1.0,
    "environmental_context": {},
    "adaptive_responses": []
  }
  ```
- **Response:** `200 OK` with full `MoodEntryResponse` including `primary_emotion`, `primary_sentiment`, and cached `emotion_analysis`.

### `GET /api/v1/mood/entries`
- **Purpose:** List mood entries for the authenticated user.
- **Query Parameters:**
  - `limit` (default `50`, max `100`)
  - `offset` (default `0`)
- **Response:** Array of mood entries ordered by `created_at` descending.

### `GET /api/v1/mood/entries/{entry_id}`
- **Purpose:** Retrieve a single mood entry by ID.
- **Response:** `200 OK` with the entry if it belongs to the user, otherwise `404`.

### `PUT /api/v1/mood/entries/{entry_id}`
- **Purpose:** Update a mood entry and rerun emotion analysis if text changes.
- **Body:** Same shape as create request.
- **Response:** Updated mood entry.

### `DELETE /api/v1/mood/entries/{entry_id}`
- **Purpose:** Delete a mood entry belonging to the user.
- **Response:** `200 OK` with confirmation or `404` if not found.

---

## Emotion Analysis

### `POST /api/v1/mood/analyze`
- **Purpose:** Run GoEmotions-based emotion analysis on arbitrary text.
- **Body:**
  ```json
  {
    "text": "Required text to analyze",
    "include_mood_entry": false,
    "mood_score": 1-10 (required if include_mood_entry = true)
  }
  ```
- **Response:** `MoodAnalysisResult` containing:
  - `top_emotions` (up to five emotions with sentiment, confidence %, color)
  - `primary_emotion`
  - `primary_sentiment`
  - `confidence_score`
- **Side effect:** When `include_mood_entry` is `true`, a mood entry is created automatically.

---

## Mood Analytics

### `GET /api/v1/mood/analytics/overview`
- **Purpose:** Return aggregate statistics: total entries, average mood, streaks, distributions, etc.
- **Response:** `MoodAnalyticsOverview`.

### `GET /api/v1/mood/analytics/patterns`
- **Purpose:** Weekly patterns, insights, recommendations.
- **Response:** `MoodPatternsResponse`.

### `POST /api/v1/mood/context`
- **Purpose:** Create mood context summaries for the memory/chatbot services.
- **Body:** `MoodContextRequest` (`session_id`, `context_summary`, `time_range_hours`).
- **Response:** `MoodContextResponse`.

### `GET /api/v1/mood/context`
- **Purpose:** Retrieve stored mood contexts with optional `session_id` filter and `limit`.
- **Response:** Array of `MoodContextResponse`.

---

## Journal Entry Management

All journal endpoints live under `/api/v1/journal` and reuse the shared `JournalEntry` SQLAlchemy model.

### `POST /api/v1/journal/`
- **Purpose:** Create a new journal entry (text or video).
- **Body:**
  ```json
  {
    "title": "string?",
    "content": "string (required)",
    "mood_before": 1-5?,
    "mood_after": 1-5?,
    "is_private": true|false (default true),
    "entry_type": "text" | "video" (default "text"),
    "video_analysis": {}
  }
  ```
- **Response:** Persisted journal entry with timestamps.

### `GET /api/v1/journal/`
- **Purpose:** Fetch journal entries for the current user.
- **Query Parameters:**
  - `limit` (default `50`, capped at `100`)
  - `offset` (default `0`)
- **Response:** Array of `JournalEntry` records sorted by `created_at` descending. Fields include `id`, `title`, `content`, `mood_before`, `mood_after`, `sentiment_score`, `sentiment_label`, `themes`, `is_private`, `word_count`, `reading_time`, `entry_type`, `video_analysis`, `created_at`, `updated_at`.

### `POST /api/v1/journal/entries`
- **Purpose:** Alternate create endpoint kept for compatibility (identical behavior to root POST).

### `GET /api/v1/journal/entries`
- **Purpose:** Alternate list endpoint (same response as root GET).

### `GET /api/v1/journal/entries/{entry_id}`
- **Status:** Currently returns `404` placeholder (“Journal functionality is not yet implemented”).

### `PUT /api/v1/journal/entries/{entry_id}`
- **Status:** Returns `501` (“planned for future release”).

### `DELETE /api/v1/journal/entries/{entry_id}`
- **Status:** Returns `501` (“planned for future release”).

---

## Legacy / Redirect Endpoints

The mood service keeps several endpoints outside `/api/v1/*` for backward compatibility. These respond with HTTP `301` redirects to the new routes.

| Legacy Path | Method | Redirect Target |
|-------------|--------|-----------------|
| `/mood` | `GET`, `POST` | `/api/v1/mood/entries` |
| `/analyze` | `POST` | `/api/v1/mood/analyze` |

All new integrations should use the `/api/v1/...` endpoints listed above.

---

## Computed Values & Defaults

Understanding existing fallbacks and calculations helps prevent surprises when extending the service (for example, when adding a unified reflection flow).

### Mood Entry Defaults (Backend)
- `mood_score`, `stress_level`, `energy_level` default to **5** when not supplied.
- `emotional_granularity` defaults to **3**.
- `mood_confidence` defaults to **1.0**.
- `collection_method` defaults to `"manual"`.
- `environmental_context`, `follow_up_responses`, `celebration_triggers` default to empty dict/list.

### Emotion Analysis
- Model: `joeddav/distilbert-base-uncased-go-emotions-student`.
- Sentiment colors: positive `#22c55e`, negative `#ef4444`, ambiguous `#f59e0b`, neutral `#6b7280`.
- Cache TTL: `settings.emotion_cache_ttl` (default **3600** seconds).
- Fallback result if model unavailable: primary emotion `neutral`, confidence `50.0`.

### Mood Analytics Calculations
- **Average mood**: arithmetic mean of `mood_score`.
- **Mood trend string**: \
  `improving` if improvement trend > 0.2, `declining` if < -0.2, else `stable`.
- **Mood distribution buckets**: `"Low (1-3)"`, `"Below Average (4-5)"`, `"Good (6-7)"`, `"Excellent (8-10)"`.
- **Current streak**: number of consecutive days (ending today) with at least one entry.
- **Longest streak**: maximum consecutive-day run historically.
- **Improvement trend**: `(avg(last 7 days) - avg(previous 7 days)) / 10`, clamped to [-1, 1].
- **Weekly patterns**:
  - Last 12 ISO weeks; average mood per week.
  - Dominant emotion = most frequent `primary_emotion`.
  - Insights flag positive vs concerning trends and stability/volatility using variance thresholds (<0.5 vs >2.0).
  - Recommendations trigger for low recent averages (<4.0) or recurring negative dominant emotions.
- **Trend slope**: linear regression over weekly averages; slope thresholds ±0.1.

### Journal Entry Defaults
- `is_private` defaults to **true**.
- `sentiment_score`, `sentiment_label`, `themes`, `word_count`, `reading_time` remain `null`/`0` unless provided (no automatic computation yet).
- `entry_type` defaults to `"text"`.
- `video_analysis` simply stored when present (no transformation).

### Frontend Journal Analytics (Hooks)
- `useJournal.generateAnalytics`:
  - Average sentiment uses client-side `sentiment.score` (falls back to neutral 0 if backend doesn’t supply values).
  - Writing streak mirrors mood streak logic (client-side date comparisons).
  - Monthly progress groups entries by `YYYY-MM`.
  - Sentiment trend captures up to 30 recent entries as `{date, sentiment}` pairs.

Documenting these behaviors ensures future enhancements can intentionally replace defaults rather than inherit them silently.

---

### Notes for Developers

- **Authentication:** Every route depends on `shared.auth.get_current_user`, which validates the JWT and surfaces `user_id`.
- **Pagination guardrails:** Journal GET handlers clamp `limit` between 1 and 100; offset is forced to be ≥ 0.
- **Emotion analysis caching:** The GoEmotions pipeline caches results in Redis keyed by MD5 hash of the text. Repeated analysis on identical text will return faster responses.
- **Sentiment fields in journals:** `sentiment_score`, `sentiment_label`, `themes`, `word_count`, and `reading_time` are present but currently remain `null` or `0` unless explicitly provided—suitable targets for future enhancements (e.g., unified reflection flow).
- **Deployment:** When running through Docker (recommended), the API Gateway exposes all routes at `https://139.84.213.185`. Direct access to the mood service (port `8003`) is available inside the Docker network or development environments.


