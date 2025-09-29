# MantraPath API Gateway Service

## 🧭 Overview
The **API Gateway** is the unified entry point for all MantraPath backend services. It provides intelligent request routing, load balancing, service discovery, resiliency (rate limiting + circuit breaker), WebSocket proxying, and an extensible AI-enhanced middleware layer (voice routing, cultural context, AI context injection, performance hooks).

> Version: 1.0.0 (Gateway Core) • Architecture Generation: V3 Enhanced Stack • File Generated: 2025-09-26

---

## 📂 Directory & File Structure

```
api_gateway/
├── Dockerfile                # Container build definition
├── requirements.txt          # Python dependencies
├── .env                      # Environment configuration (loaded via pydantic-settings)
├── README.md                 # (This document)
├── config/                   # (Reserved for future externalized configs)
├── config_old/               # Legacy / deprecated configuration artifacts
├── scripts/                  # Helper scripts (startup, maintenance)
├── src/
│   ├── main.py               # FastAPI application & all route definitions
│   ├── core/
│   │   ├── config.py         # Gateway & service configuration models
│   │   └── models.py         # Core dataclasses (ServiceInstance, RouteRule, ProxyRequest ...)
│   ├── registry/
│   │   └── service_registry.py  # Service discovery & periodic health checking
│   ├── routing/
│   │   ├── router.py         # Rule-based path → service resolution
│   │   ├── load_balancer.py  # Strategy factory (round‑robin, weighted, etc.)
│   │   └── proxy.py          # Outbound request proxy (httpx pooled clients)
│   ├── middleware/
│   │   ├── rate_limiter.py   # Token bucket implementation
│   │   ├── circuit_breaker.py# Service circuit state machine
│   │   ├── performance.py    # Request timing + metrics hook (stub impl)
│   │   ├── ai_context.py     # AI context injection (placeholder)
│   │   ├── cultural_context.py # Cultural adaptation (placeholder)
│   │   └── voice_routing.py  # Voice request detection & enrichment
│   ├── services/
│   │   ├── voice_router.py   # Advanced voice command routing engine
│   │   ├── context_manager.py# AI context manager (stub)
│   │   ├── cultural_manager.py # Cultural adaptation manager (stub)
│   │   └── websocket_manager.py # WebSocket session registry & proxy support
│   ├── models/
│   │   └── voice_models.py   # Pydantic + dataclasses for voice intents & routing
│   ├── health/
│   │   └── health_checker.py # Aggregated & detailed health logic
│   ├── utils/
│   │   ├── cache_manager.py  # In‑memory cache abstraction (stub)
│   │   ├── connection_pool.py# httpx AsyncClient pool helper
│   │   ├── language_detector.py # Multi‑method language detection utility
│   │   └── performance_monitor.py # Metrics recorder (stub)
│   ├── shared_integration.py # (Potential future cross‑service helpers)
│   └── grpc/ & grpc_services/ # (Reserved for future gRPC exposure)
├── tests/                    # Pytest suites (routing, voice, registry, limiter, etc.)
└── venv/                     # Local virtual environment (not for production)
```

### Notable Design Characteristics
| Concern | Implementation | Notes |
|---------|----------------|-------|
| Service Discovery | `ServiceRegistry` | Static bootstrap + periodic health polling |
| Routing | `RequestRouter` (regex rules) | Supports prefix stripping & auth flags |
| Load Balancing | Strategy factory | Default: Round‑Robin (others selectable) |
| Resilience | RateLimiter + CircuitBreaker | In‑memory; no distributed state yet |
| Observability | Health + (stub) metrics | Metrics recording mostly placeholders |
| Voice Intelligence | `VoiceCommandRouter` + middleware | Intent classification: rule / keyword based |
| Context Enrichment | AI & Cultural middleware | Currently stubbed (returns None) |
| WebSockets | Proxy + manager | Notification & Assistance passthrough |
| Security | Optional HTTP Bearer per endpoint | JWT verification via shared `shared.auth` |

---

## ⚙️ Service Functionality Overview
The gateway centralizes:
1. Public & authenticated HTTP ingress
2. Intelligent routing to domain microservices (auth, profile, mood, chatbot, content, media, translation, AI event/context, memory, proactive assistance, models, voice)
3. Voice-aware request transformation (intent detection, parameter extraction, fallback routing)
4. Resilience controls (rate limiting + circuit breaker around target services)
5. Health aggregation & service status surfacing
6. WebSocket proxy bridging front-end → downstream real-time services
7. Foundational hooks for AI & cultural adaptation (extensible future capability)

Fits Into Platform:
- Sits in front of all user-facing backend HTTP APIs
- Simplifies frontend integration: consistent headers, observability, error semantics
- Enables future cross-cutting concerns (auth hardening, quota, tracing, adaptive personalization)

---

## 🌐 Routing & API Endpoints

### 1. Core Health & Operational
| Endpoint | Method | Purpose | Auth | Notes |
|----------|--------|---------|------|-------|
| `/health` | GET | Basic heartbeat | No | Lightweight status |
| `/api/health` | GET | Alias basic heartbeat | No | For frontend uniformity |
| `/health/live` | GET | Liveness probe | No | Container / K8s |
| `/health/ready` | GET | Readiness (checks essential services) | No | Uses `HealthChecker.readiness_check()` |
| `/api/health/detailed` | GET | Full subsystem + registered services | No | Aggregates feature health |
| `/api/health/voice` | GET | Voice subsystem | No | From `VoiceCommandRouter` |
| `/api/health/ai-context` | GET | AI context manager | No | Stub returns healthy if initialized |
| `/api/health/cultural` | GET | Cultural subsystem | No | Stub |
| `/api/services/status` | GET | Raw registry instance listing | Yes | JWT required |

### 2. Metrics (Current Mostly Placeholders)
| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/metrics` | GET | Global metrics snapshot | Yes |
| `/api/metrics/voice` | GET | Voice command metrics | Yes |
| `/api/metrics/cultural` | GET | Cultural adaptation metrics | Yes |
| `/api/metrics/services` | GET | Per-service performance | Yes |
| `/api/v3/metrics/performance` | GET | V3 consolidated metrics | No (design choice) |
| `/api/v3/metrics/voice` | GET | Voice metrics mirror | No |
| `/api/v3/metrics/cultural` | GET | Cultural metrics mirror | No |

### 3. Voice Processing
| Endpoint | Method | Body Model | Description |
|----------|--------|-----------|-------------|
| `/api/voice/command` | POST | `VoiceCommand` | Classify & route structured voice command; proxies downstream |
| `/api/voice/stream` | WS | - | Bi-directional streaming (echo prototype) |

### 4. WebSocket Proxies
| Endpoint | Type | Proxies To | Purpose |
|----------|------|-----------|---------|
| `/api/notifications/ws/{user_id}` | WS | `ws://notification-service:8007/ws/{user_id}` | Notifications channel |
| `/api/assistance/ws/{user_id}` | WS | `ws://proactive-assistance-engine:8018/ws/{user_id}` | Proactive assistance stream |

### 5. Generic Service Proxying
1. Pattern-based dispatch via `RequestRouter`
2. Fallback catch-all route `/{path:path}` (excludes `/api/v3/*` special cases)
3. Explicit enhanced proxy endpoint: `/api/service/{service_name}/{path:path}` (skips router)

Example Flow:
```
Client -> /api/v1/mood/entries -> Gateway
	Router matches ^/api/v1/mood/.* -> service_name=mood
	RateLimiter -> CircuitBreaker check
	ServiceRegistry -> healthy instances
	LoadBalancer -> select instance
	RequestProxy -> forward (httpx pooled)
	Response -> optional cultural adaptation -> return
```

### 6. Representative Routing Rules (from `router.py`)
| Path Regex | Service | Strip Prefix | Auth | Notes |
|------------|---------|--------------|------|-------|
| `^/auth/.*` | auth | Yes | No | Direct auth ops |
| `^/api/auth/.*` | auth | Custom | No | Supports both prefixed forms |
| `^/api/v1/mood/.*` | mood | No | Yes | Mood API v1 |
| `^/api/chatbot/.*` | chatbot | No | Yes | Higher timeout (AI) |
| `^/voice/.*` | voice | Yes | Yes | Voice backend forwarding |
| `^/ai-events/.*` | ai-events | Yes | Yes | AI Event Processor passthrough |
| `^/ai-context/.*` | ai-context | Yes | Yes | AI Context Store |
| `^/media/.*` | media | Yes | Yes | Upload / retrieval |
| `^/api/v1/translation/.*` | translation | No | Yes | Translation endpoints |

---

## 🔌 Ports & Configuration

### Primary Runtime Ports
| Purpose | Default | Source |
|---------|---------|--------|
| HTTP Gateway | 8000 | `GatewayConfig.port` |
| Metrics (future) | 9090 | `GatewayConfig.metrics_port` |
| WebSocket (logical) | 8001 | `ServiceConfig.websocket_port` (not separately bound yet) |

### Key Environment Variables (`.env` via pydantic-settings)  
Prefix: `GATEWAY_` (gateway) / `SERVICE_` (service URLs)

| Variable | Default | Description |
|----------|---------|-------------|
| `GATEWAY_ENVIRONMENT` | development | Environment enum |
| `GATEWAY_PORT` | 8000 | HTTP bind port |
| `GATEWAY_RATE_LIMIT_REQUESTS_PER_MINUTE` | 100 | Global rate cap |
| `GATEWAY_RATE_LIMIT_BURST` | 20 | Burst tokens |
| `GATEWAY_CIRCUIT_BREAKER_FAILURE_THRESHOLD` | 5 | Failures before open |
| `GATEWAY_CIRCUIT_BREAKER_RECOVERY_TIMEOUT` | 60 | Seconds to half-open |
| `SERVICE_AUTH_SERVICE_PORT` | 8001 | Downstream auth service port |
| `SERVICE_AI_EVENT_PROCESSOR_PORT` | 8014 | AI event processor |
| `SERVICE_MODELS_SERVICE_INTERNAL_PORT` | 8080 | Models service internal |
| ... | ... | Similar for all microservices |

> NOTE: All service base URLs: `http://<service-name>:<PORT>` are composed inside `ServiceConfig` with overridable env ports.

---

## 🔄 Request Processing Flow

### A. Generic HTTP Request (non-voice)
```
Client → FastAPI → PerformanceMiddleware (start timer)
	 → CulturalContextMiddleware (stub returns None)
	 → AIContextMiddleware (stub returns None)
	 → VoiceRoutingMiddleware (skips if not voice)
	 → Catch-all route handler (main.py)
			 • Find RouteRule (regex)
			 • RateLimiter check (ip/user)
			 • (Optional) Auth -> JWT verify -> user context
			 • AI Context fetch (stub)
			 • Cultural Context fetch (stub)
			 • CircuitBreaker.is_call_allowed
			 • ServiceRegistry.get_healthy_services
			 • LoadBalancer.select_instance
			 • RequestProxy.proxy_request (connection pool)
			 • circuit_breaker.record_success/failure
			 • performance_monitor.record_service_request (stub)
			 • Optional cultural response adaptation
	 ← Response headers enriched (X-Request-ID, X-Processing-Time)
Return to client
```

### B. Voice Command (`/api/voice/command`)
```
POST voice command JSON
 → Validate (Pydantic VoiceCommand)
 → Language detection if missing
 → VoiceCommandRouter.route_command
		 • Intent -> rule match / fallback classification
		 • Parameter extraction (keywords, time, mood)
		 • Build target service + endpoint + headers
 → Construct ProxyRequest with enriched headers
 → RequestProxy → Downstream
 → Cultural adaptation (stub)
 → Build VoiceResponse (routing info + processing time)
```

### C. WebSocket Proxy (Notifications / Assistance)
```
Client WS → Gateway WS endpoint
	→ Establish upstream WS to service
	→ Bi-directional async gather copy loops
	→ Close & cleanup in WebSocketManager
```

---

## 🔗 Service Communication

| Channel | Direction | Type | Mechanism | Notes |
|---------|-----------|------|-----------|-------|
| HTTP Proxy | Gateway → Services | Request/Response | httpx pooled clients | Core routing |
| Health Polling | Gateway → Services | Periodic GET | Async tasks | Updates ServiceInstance.status |
| WebSocket Proxy | Client ↔ Gateway ↔ Service | Duplex | `websockets` + FastAPI WS | Notification & assistance streams |
| Headers Enrichment | Gateway → Services | Metadata | X-Request-ID, X-AI-Context, X-Cultural-Context | Extensible |

Currently **no** direct event bus inside gateway; eventing handled by other services.

---

## 🧠 Design Documentation

### High-Level Architecture
```
					+--------------+       +------------------+
Client -> |  API Gateway | ----> |  Auth / Profile  |
					| (FastAPI)    | ----> |  Mood / Chatbot  |
					|              | ----> |  Content / Media |
					|  Middleware  | ----> |  AI (Events/Ctx) |
					+--------------+ ----> |  Translation ... |
								 |                +------------------+
								 |-- WebSocket Proxy --> Real-time Services
```

### Component Interactions
| Component | Depends On | Responsibility |
|-----------|------------|----------------|
| `main.py` | All below | Composition root, endpoints |
| `ServiceRegistry` | httpx, config | Track service health/URLs |
| `RequestRouter` | Regex rules | Map path+method → service |
| `LoadBalancer` | Registry output | Instance selection strategy |
| `RequestProxy` | Connection pool | Execute outbound request |
| `CircuitBreaker` | Proxy outcomes | Failure isolation |
| `RateLimiter` | In-memory window | Abuse prevention |
| `VoiceCommandRouter` | Voice models | Intent routing decisions |
| `LanguageDetector` | langdetect/TextBlob | Language inference |

### Key Design Decisions & Rationale
| Decision | Rationale | Trade-offs |
|----------|-----------|-----------|
| In-memory registry | Simplicity & fast startup | No dynamic discovery, manual scaling complexity |
| Regex routing rules | Flexible matching | Harder to validate statically; order matters |
| httpx pooled clients | Connection reuse & perf | Need lifecycle management (handled in pool) |
| Custom circuit breaker | Lightweight internal control | Lacks advanced metrics / half-open testing nuance |
| Stubs for AI/Cultural | Enable interface-first development | Missing real enrichment today |
| Voice routing engine inside gateway | Reduce latency for intent dispatch | Couples gateway to domain semantics (may move out later) |

---

## 🚧 Incomplete Implementations & TODOs

| Area | Status | Gaps |
|------|--------|------|
| Performance Metrics | Stub | `PerformanceMonitor.record_*` are no-ops |
| AI Context Injection | Stub | `AIContextManager.get_context` always returns None |
| Cultural Adaptation | Stub | No transformation of requests/responses |
| Distributed Rate Limiting | Missing | Needs Redis/token bucket sync |
| Dynamic Service Discovery | Static only | No registration/deregistration at runtime (beyond manual) |
| Load Metrics Based Balancing | Not implemented | Only static strategies |
| Circuit Breaker Telemetry | Minimal | No persistence, no alerting hooks |
| Voice Intent ML Models | Keyword/rule based | Upgrade path to ML/NLP embeddings |
| Observability | Basic | No tracing, structured metrics, Prometheus export |
| Security Hardening | Basic JWT | No mTLS, no scope/role enforcement per route |
| WebSocket Robustness | Basic proxy | No backpressure, heartbeat, reconnection strategy |

Inline TODOs (selected):
```
# TODO (voice_router): load from external config / DB
# TODO (performance_monitor): implement aggregation & retention
# TODO (context_manager / cultural_manager): integrate real AI services
# TODO: Add tracing (OpenTelemetry) & correlation propagation
# TODO: Implement distributed cache & rate limits via Redis or NATS KV
```

---

## 🌟 Future Development Plans

### Phase 1 (Short Term)
| Goal | Description |
|------|-------------|
| Real Metrics | Implement counters/histograms; expose `/metrics` Prometheus format |
| Redis Backing | Move rate limiting + cache + circuit state to Redis |
| Tracing | OpenTelemetry spans (ingress → proxy) |
| Config Externalization | YAML/DB-driven routing rules with hot-reload |

### Phase 2 (Mid Term)
| Goal | Description |
|------|-------------|
| Dynamic Discovery | Service self-registration (heartbeat-based) |
| Adaptive LB | Latency & success-rate weighted balancing |
| Policy Layer | Per-route auth scopes, quota plans, feature flags |
| AI/Cultural Enrichment | Real context retrieval from AI Context Store + cultural adaptation algorithms |
| Voice ML Upgrade | Intent classification via embeddings / transformer model |

### Phase 3 (Long Term)
| Goal | Description |
|------|-------------|
| Multi-Protocol | gRPC proxying & HTTP/2 multiplexing |
| Edge Decomposition | Split voice & AI enrichment into sidecar/edge workers |
| Intelligent Throttling | Adaptive rate limits based on risk & user tier |
| Zero-Downtime Reload | Hot rule & config swap without connection drops |
| Observability Suite | Unified dashboards (latency SLOs, error budgets) |

---

## 🧪 Testing Strategy
| Test File | Focus |
|-----------|-------|
| `test_gateway.py` | Health, readiness, error handling |
| `test_registry.py` | Service registration & health cycle |
| `test_load_balancer.py` | Strategy correctness |
| `test_rate_limiter_comprehensive.py` | Rate limiting edge cases |
| `test_voice_router_comprehensive.py` | Voice routing rules & parameters |
| `test_voice_integration.py` | End-to-end voice request path |
| `test_middleware_comprehensive.py` | Middleware chaining & headers |

Run All:
```bash
pytest -v
```

---

## 🔐 Security Model (Current State)
1. Optional Bearer token on most proxy endpoints. Router rules can mark `auth_required=False`.
2. JWT validation delegated to shared library (`shared.auth.verify_token`).
3. No per-scope / RBAC enforcement yet (future Policy Layer).
4. No rate limit differentiation (user tier vs anonymous) yet—straight token bucket.

Hardening Roadmap:
- Add per-route scopes & claims mapping
- Integrate WAF / basic request anomaly detection
- Enable mTLS for inter-service traffic (service mesh or sidecar)

---

## 🧵 Error Handling & Status Mapping
| Gateway Condition | Upstream Condition | Returned Status |
|-------------------|--------------------|-----------------|
| Rate limit exceeded | - | 429 |
| Circuit open | Service tripped | 503 |
| No healthy instances | All failing | 503 |
| Upstream timeout | httpx timeout | 504 |
| Connect error | DNS / network | 503 |
| Unexpected upstream error | 5xx generic | 502 |
| Unknown route | No rule matched | 404 |

Body Examples (error):
```json
{"error": "Bad Gateway", "message": "Service error occurred"}
```

---

## 🚀 Deployment Notes
Minimal (dev) run:
```bash
export GATEWAY_PORT=8000
python -m uvicorn src.main:app --reload --port $GATEWAY_PORT
```

Docker (example):
```bash
docker build -t mantrapath/api-gateway:latest .
docker run -p 8000:8000 --env-file .env mantrapath/api-gateway:latest
```

Kubernetes Readiness/Liveness already aligned: `/health/ready`, `/health/live`.

---

## 📏 Non-Functional Targets (Proposed)
| Dimension | Target |
|-----------|--------|
| P99 Latency (proxy passthrough) | < 250ms (intra-cluster) |
| Availability | 99.9% |
| Error Budget | 0.1% 5xx over 30d |
| Cold Start Time | < 3s |
| Config Reload | < 1s (future) |

---

## 🗂️ Glossary
| Term | Definition |
|------|------------|
| RouteRule | Declarative mapping regex → service metadata |
| ServiceInstance | Represents a concrete backend instance with health state |
| Circuit Breaker | Prevents repeated calls to failing dependencies |
| Voice Routing | Intent-driven dynamic service dispatch for speech-derived commands |
| AI Context | Planned enrichment describing user, session, emotional or behavioral state |
| Cultural Context | Planned localized adaptation profile for personalization |

---

## ✅ Summary
The API Gateway establishes a solid, extensible foundation: stable routing, resilience primitives, health visibility, and the scaffolding for advanced AI-driven personalization & voice-first interaction. Main immediate improvement vectors are production-grade metrics, distributed resilience state, and fully realized AI/cultural enrichment.

---

## 📄 License
Part of the MantraPath platform – see root project LICENSE.

---
_Generated: 2025-09-26 • Maintainers: Platform / AI Infrastructure Teams_

