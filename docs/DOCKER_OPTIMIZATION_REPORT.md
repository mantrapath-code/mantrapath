# Docker Requirements Optimization Report

## Translation Service Analysis (COMPLETED)

### Original vs Optimized Comparison

| Version | Image Size | Build Time | Dependencies | Status |
|---------|------------|------------|--------------|---------|
| Original | 5.61GB | ~120s | 71 packages | ✅ Working |
| Minimal | 5.61GB | ~130s | 16 packages | ✅ Working |
| Ultra-Minimal | 213MB | ~19s | 10 packages | ✅ Working |

### Key Findings

1. **AI/ML Dependencies Impact**: torch + transformers = ~5.4GB
2. **Build Time Improvement**: 85% faster (19s vs 130s) 
3. **Size Reduction**: 96% smaller (213MB vs 5.61GB)

### Optimized Requirements (Ultra-Minimal)

```txt
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# HTTP clients
httpx==0.25.2
aiohttp==3.9.1

# Caching & Database
redis==5.0.1

# Language detection
langdetect==1.0.9

# Basic HTTP requests
requests==2.31.0

# Testing (optional)
pytest==7.4.3
pytest-asyncio==0.21.1
```

### Recommendations

1. **Use ultra-minimal for production** - Relies on external APIs (Bhashini, Models Service)
2. **Keep AI dependencies only if local models needed** - Use minimal version
3. **Remove unused packages**: spacy, nltk, celery, sqlalchemy, etc.

### Files Created
- `requirements_ultra_minimal.txt` - Production ready
- `Dockerfile.ultra_minimal` - Optimized build
- `requirements_minimal_actual.txt` - With AI dependencies

---

## Voice Service Analysis (COMPLETED - Minimal Build Verified)

### Results

| Version | Image Size | Build Time | Dependencies | Health/Tests |
|---------|------------|------------|--------------|--------------|
| Original | 1.43GB | ~78s | Full `requirements.txt` (includes librosa/soundfile/scipy/dev deps) | ✅ /health OK |
| Minimal | 279MB | ~14s | `requirements.min.txt` (no librosa/soundfile/scipy/dev deps) | ✅ /health OK |

Notes:
- VoiceEnhancer reports healthy with basic features; advanced resampling depends on librosa which is excluded in minimal build.
- Container logs show no errors; one Pydantic protected_namespaces warning in request model (non-blocking).
- Redis is optional; if absent, service falls back to memory as designed.

### Artifacts
- `backend/services/voice_service/requirements.min.txt`
- `backend/services/voice_service/Dockerfile.minimal`

### Recommendation
- Use minimal build in environments where advanced audio processing (librosa/scipy) is not required. Switch to original for full audio tooling support.

## Auth Service Analysis (COMPLETED)

### Results
- **Original**: 252MB, 12 dependencies, ~14s build
- **Optimized**: 252MB, 12 dependencies, ~13s build
- **Status**: ✅ Already minimal - no optimization needed

The auth service was already well-optimized with only necessary dependencies.

---

## Voice Event Processor Analysis (COMPLETED - Minimal Build Verified)

### Results

| Version | Image Size | Build Time | Dependencies | Health/Tests |
|---------|------------|------------|--------------|--------------|
| Original | 6.64GB | ~181s | Full `requirements.txt` (audio stack + ML) | ✅ /health OK |
| Minimal | 190MB | ~8s | `requirements.min.txt` (FastAPI + websockets via uvicorn) | ✅ /health OK |

Notes:
- Minimal build excludes heavy audio/ML deps (librosa, soundfile, scipy, webrtcvad, pyaudio, torch/torchaudio/transformers) and DB/messaging clients.
- Current `main.py` relies only on FastAPI/WebSocket core—the minimal image fully supports health and base endpoints.
- Use the original build where real audio processing or emotion detection is required.

### Artifacts
- `backend/services/voice_event_processor/requirements.min.txt`
- `backend/services/voice_event_processor/Dockerfile.minimal`

## API Gateway Analysis (COMPLETED) 

### Original vs Optimized Comparison

| Version | Image Size | Build Time | Dependencies | Status |
|---------|------------|------------|--------------|---------|
| Original | 592MB | ~32s | 32+ packages | ✅ Working |
| Minimal | 218MB | ~11s | 11 packages | ✅ Working |

### Key Findings

1. **Development Dependencies Removed**: pytest, black, isort, flake8, etc.
2. **Build Time Improvement**: 66% faster (11s vs 32s)
3. **Size Reduction**: 63% smaller (218MB vs 592MB)

### Optimized Requirements (Minimal)

```txt
# Core Framework
fastapi>=0.104.1
uvicorn[standard]>=0.24.0

# HTTP Client & Config
httpx>=0.25.2
pydantic>=2.5.0
pydantic-settings>=2.1.0

# Security
python-jose[cryptography]>=3.3.0
pyjwt>=2.8.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6

# Redis & Utilities
redis[hiredis]>=5.0.1
python-dateutil>=2.8.2
structlog>=24.1.0
```

---

## Next Services to Analyze

1. [✅] auth_service - Already minimal
2. [✅] api_gateway - Optimized (63% reduction)
3. [✅] translation_service - Ultra-optimized (96% reduction)  
4. [🚧] ml_service - In progress (minimal requirements + Dockerfile prepared)
5. [ ] voice_service
6. [ ] voice_event_processor
7. [✅] action_orchestrator - Minimal requirements added and Dockerfile wired
8. [ ] community_service
9. [ ] profile_service
10. [ ] deployment_api
11. [ ] mood_service

---

## AI Event Processor Analysis (COMPLETED - Full Deps Retained for Functionality)

### Changes
- Kept Dockerfile on full `requirements.txt` to avoid breaking local model features (torch/transformers available).
- Hardened `core/emotion_analyzer.py`:
	- Safe optional imports and GPU checks
	- Initialize `ModelsServiceClient` and skip local multilingual load when using Models Service
	- Health check now reflects initialized status
- Made runtime dependencies configurable:
	- Predictive engine can be disabled via `ENABLE_PREDICTIVE_ENGINE=false`; optional mode via `PREDICTIVE_OPTIONAL=true`; `REDIS_URL` configurable
	- Event bus can run without NATS via `USE_NATS=false` (falls back to in-memory)

### Impact
- Preserved full functionality for local models while improving resilience and configurability.
- Optional runtime toggles enable running service without Redis/NATS during local checks.

### Status
- Built image: `backend-ai-event-processor:full` — OK
- Ran with env: `ENABLE_PREDICTIVE_ENGINE=false USE_NATS=false` — OK
- Health: `/health` returned 200; components healthy, predictive engine disabled by choice
- Logs: NATS and Models Service gracefully handled when unavailable; no crashes

### Artifacts
- `backend/services/ai_event_processor/Dockerfile` (now uses full requirements)
- Code updates under `core/` for resilience and env toggles

---

## Action Orchestrator Analysis (COMPLETED - Minimal Path Verified)

### Changes
- Added `requirements.min.txt` without heavy ML/DB dependencies.
- Added `Dockerfile.minimal`; primary Dockerfile now references minimal requirements by default.

### Expected Impact
- Image size reduction to ~200–300MB range; faster builds.

### Status
- Built image: `backend-action-orchestrator:min` — OK
- Ran container and verified `/health` — 200 OK; logs show clean startup

### Artifacts
- `backend/services/action_orchestrator/requirements.min.txt`
- `backend/services/action_orchestrator/Dockerfile.minimal`
- `backend/services/action_orchestrator/Dockerfile` updated to minimal requirements

---

## Voice Event Processor Analysis (COMPLETED - Minimal Default)

### Changes
- Replaced `requirements.txt` with content of previously vetted `requirements.min.txt` removing audio/ML stack.
- For full audio/emotion features, use original `Dockerfile` + a full requirements file if needed.

### Impact
- Image size drops from 6.64GB to ~190MB; build time from ~181s to ~8s in prior tests.

### Status
- Health endpoint `/health` functional with current `main.py` feature set (no heavy imports).

### Artifacts
- `backend/services/voice_event_processor/requirements.min.txt` (reference)
- `backend/services/voice_event_processor/requirements.txt` now minimal

---

## ML Service Analysis (COMPLETED - Minimal Build Verified)

### Goal
Reduce heavy optional ML dependencies while keeping all endpoints responsive and tests green. Provide two builds: original (full) and minimal (lean).

### Changes
- Added `requirements.min.txt` excluding heavy libs: tensorflow, prophet, matplotlib, seaborn, pmdarima, celery, flower, dill, psycopg2-binary.
- Added `Dockerfile.minimal` to build with the minimal set.
- Kept NLTK data pre-download to satisfy content engine requirements.

### Expected Behavior
- CrisisPredictionSystem will run in fallback mode when advanced libs are absent; endpoints should still respond with valid assessments.
- Unit/integration tests should pass as long as they do not hard-require TensorFlow/Prophet.

### Results

| Version | Image Size | Build Time | Dependencies | Health/Tests |
|---------|------------|------------|--------------|--------------|
| Original | 2.71GB | ~104s | Full `requirements.txt` | ✅ /health OK |
| Minimal | 1.00GB | ~48s | `requirements.min.txt` | ✅ /health OK; 1 test passed |

Notes:
- CrisisPredictionSystem runs in fallback mode (no TensorFlow/Prophet) on minimal build but endpoints remain healthy.
- NLTK corpora are pre-downloaded; content engine is ready.
- Redis not required; service falls back to in-memory cache when Redis is absent.

### Verification
- Built both images and compared sizes/time.
- Launched minimal container and validated `/health` returns OK.
- Executed `test_health_check` inside container: 1 passed in 0.20s.

### Artifacts
- `backend/services/ml_service/requirements.min.txt`
- `backend/services/ml_service/Dockerfile.minimal`
