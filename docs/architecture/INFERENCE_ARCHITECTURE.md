# MantraPath Inference Architecture

This document explains how “inference” works across MantraPath services: which components run models, how requests flow, what endpoints exist, and how configuration affects runtime. It synthesizes the current code and docs.

## Scope

- Central inference hub: Models Service (STT, TTS, NLP)
- Orchestrators and consumers: API Gateway, Voice Service, Translation Service, AI Event Processor, ML Service
- Data flows (voice, translation, text/NLP, event-driven)
- Configuration, performance, and health

## High-level Overview

```
Client/Web/Apps
   │
   ├─► API Gateway (Port 8000)
   │     ├─ Voice routes ─► Voice Service (8011)
   │     ├─ Text/NLP ─────► Translation/Chatbot/Services
   │     └─ Health/registry/routing
   │
   ├─► Translation Service (8010) [optional path]
   ├─► AI Event Processor (8014)
   ├─► ML Service (8008)
   │
   └─► Models Service (8085 external / 8080 internal)
             ├─ STT Engine (Whisper, Vosk, Wav2Vec2)
             ├─ TTS Engine (Coqui, eSpeak, Festival)
             └─ NLP Engine (Microsoft Phi‑3)
```

- Central model execution happens in Models Service: `backend/services/models_service/`.
- Other services call it over HTTP via shared clients (see `backend/shared/clients/models_service_client.py`).

## Core Components

### Models Service (Central AI Hub)
- Path: `backend/services/models_service/`
- Entry: `main.py` (FastAPI app, lifespan init of engines)
- Engines: `models/stt_engine.py`, `models/tts_engine.py`, `models/nlp_engine.py`
- Phi‑3 integration: `models/phi3_engine.py`
- Routes: `api/routes.py` (STT/TTS), `api/translation_routes.py` (NLP incl. translate)
- Model lifecycle: `models/model_manager.py`

Capabilities:
- STT: 17+ languages (Whisper, Vosk, Wav2Vec2)
- TTS: 21+ languages (Coqui XTTS v2, eSpeak, Festival), voice cloning
- NLP: Translation, sentiment, text generation, language detection via Phi‑3

Key endpoints (prefix varies by router):
- STT: `POST /api/v1/stt/transcribe`
- TTS: `POST /api/v1/tts/synthesize`, `POST /api/v1/tts/clone-voice`, `GET /api/v1/tts/languages`
- NLP/Translation: `POST /api/v1/translation/translate`, `POST /api/v1/translation/detect-language`, `POST /api/v1/translation/analyze-sentiment`, `POST /api/v1/translation/generate-text`
- Health/Status: `GET /health`, `GET /status`, `GET /models/available`, `GET /models/loaded`

Notes:
- Default port inside code is `MODELS_SERVICE_PORT` (defaults to 8080); docs and docker expose 8085 externally.
- Minimal mode: `MODELS_SERVICE_MODE=minimal` delays model loads until first use.
- Preload: `MODELS_PRELOAD_LIST`, `MODELS_PRELOAD_BACKGROUND` enable background downloads/loads.

### Voice Service (Abstraction over Models Service)
- Path: `backend/services/voice_service/`
- Routes proxy to Models Service for STT/TTS with extras: audio enhancement, caching, language detection, session management.
- Uses enhanced client: `app/core/models_client.py`.
- Example route: `POST /api/v1/voice/stt` reads audio, forwards to `/api/v1/stt/transcribe` in Models Service.

### API Gateway (Entry & Orchestration)
- Path: `backend/services/api_gateway/`
- Entry: `src/main.py`
- Responsibilities: routing, load-balancing, rate limiting, circuit breaking, voice routing, AI context and cultural context middleware.
- For inference, it typically forwards voice to Voice Service and text/NLP to appropriate services which in turn call Models Service.

### Translation Service (Specialized workflows)
- Path: `backend/services/translation_service/`
- Provides translation-focused APIs and likely delegates to Models Service Phi‑3 for inference.

### AI Event Processor (Real-time AI pipeline)
- Path: `backend/services/ai_event_processor/`
- Entry: `main.py` / `app.py`
- Components: Emotion Analyzer, Cultural Intelligence Processor, Predictive Intervention Engine.
- Delegates model-level inference to Models Service.

### ML Service (Analytics & Predictions)
- Path: `backend/services/ml_service/`
- Focused on mood pattern analysis, timing prediction, content generation, crisis prediction and early warnings.
- Not a primary model serving node for STT/TTS/NLP; integrates when needed.

## Inference Flows

### A. Voice STT Flow
1. Client uploads audio to API Gateway voice route or directly to Voice Service.
2. Voice Service may enhance audio and detect language (optional).
3. Voice Service sends multipart form to Models Service `/api/v1/stt/transcribe`.
4. Models Service STT Engine runs Whisper/Vosk/Wav2Vec2, returns transcript + meta (confidence, language, model_used).
5. Response goes back to client via Voice Service/API Gateway.

### B. TTS Flow
1. Client calls API Gateway voice TTS route or Voice Service directly with text/language/voice.
2. Voice Service calls Models Service `/api/v1/tts/synthesize`.
3. Models Service TTS Engine runs selected model (Coqui/eSpeak/Festival) and streams/returns audio.
4. Voice Service may stream audio back to client.

### C. NLP Translation (Phi‑3) Flow
1. Client or Translation Service sends `text`, `source_language` (or auto), `target_language` to `/api/v1/translation/translate`.
2. Models Service NLP Engine ensures Phi‑3 is loaded; if `auto`, language detection is performed first.
3. Phi‑3 prompt-based generation produces the translation, with timing and confidence metadata.
4. JSON result returned to caller.

### D. Event-driven AI Flow
1. Services publish events (e.g., `ai.inference_requested`) via shared bus (see `backend/shared/events`).
2. AI Event Processor consumes, orchestrates analysis (emotion, cultural), and calls Models Service as needed.
3. Results published (`ai.inference_completed`) and/or persisted in Context Store.

## Runtime & Configuration

- Models Service startup initializes ModelManager + Engines in `lifespan()` (`backend/services/models_service/main.py`).
- Minimal mode allows faster boot; models load on first request.
- Preloading supports background downloads to mitigate first-request latency.
- GPU detection: CUDA used when available; otherwise CPU.

Relevant env vars:
- `MODELS_SERVICE_PORT` (default 8080)
- `MODELS_SERVICE_MODE` ("minimal" for on-demand)
- `MODELS_PRELOAD_LIST` (comma-separated models)
- `MODELS_PRELOAD_BACKGROUND` (true/false)
- `MODELS_SERVICE_SKIP_DEFAULTS` (true/false)

## Health, Status, and Observability

- `GET /health` basic readiness.
- `GET /status` reports CPU, memory, GPU availability, loaded models, supported languages.
- Structured logging across services (structlog/logging) with error context.

## Clients and Integration

- Shared client: `backend/shared/clients/models_service_client.py` exposes:
  - `transcribe_audio(...)`
  - `synthesize_speech(...)`
  - `translate_text(...)`
  - `analyze_sentiment(...)`
  - `get_embeddings(...)`
  - Batch APIs and language support utility methods
- Voice Service has an enhanced client with typed results and caching.

## Model Inventory (Highlights)

- STT: Whisper (medium), Vosk (per-language), Wav2Vec2 variants.
- TTS: Coqui XTTS v2, eSpeak, Festival; voice cloning supported.
- NLP: Microsoft Phi‑3‑mini‑4k‑instruct (translation, detection, sentiment, generation).

## Error Modes & Resilience

- Service-level: API Gateway circuit breaker and rate limiter; retry-friendly clients.
- Models Service: returns structured errors for engine not initialized / model missing.
- Language auto-detect fallbacks and early exits when src=target.

## Performance Considerations

- Preload popular models to reduce cold-start latency.
- GPU preferred when available; model dtype adjusted accordingly.
- Streaming responses for TTS; batch endpoints for throughput.
- Caching layers in Voice Service; request-level time tracking.

## Quick Cross-Refs (Code)

- Models Service app: `backend/services/models_service/main.py`
- STT/TTS routes: `backend/services/models_service/api/routes.py`
- Translation/NLP routes: `backend/services/models_service/api/translation_routes.py`
- Phi‑3 engine: `backend/services/models_service/models/phi3_engine.py`
- Voice Service routes: `backend/services/voice_service/app/api/voice_routes.py`
- API Gateway app: `backend/services/api_gateway/src/main.py`
- Shared client: `backend/shared/clients/models_service_client.py`

## Future Enhancements

- Model registry and versioning (A/B tests, rollbacks)
- Advanced inference metrics and tracing
- Auto-scaling for inference load
- Model optimization (quantization/distillation) + edge deployment
- WebSocket streaming for STT/NLP where applicable

---
Last updated: 2025-09-11
