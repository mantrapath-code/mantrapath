# MantraPath API Gateway - Architecture Documentation

## Service Overview

The MantraPath API Gateway is the central entry point for all client requests, managing service orchestration, load balancing, security, and inter-service communication. It operates as a reverse proxy with advanced features for voice commands, AI context management, and cultural adaptation.

## Port Configuration

### External Ports (Client Access)
- **Main API Gateway**: `8000` - Primary HTTP/REST endpoint
- **WebSocket Server**: `8080` - Real-time communication, voice streaming
- **Metrics/Monitoring**: `9090` - Prometheus metrics, health monitoring

### Internal Service Ports (Container-to-Container)
All internal service communication uses the service names and their designated ports:

```yaml
Service Communication Map:
├── auth-service:8001          # Authentication & Authorization
├── profile-service:8002       # User Profile Management
├── mood-service:8003          # Mood Tracking & Analysis
├── chatbot-service:8004       # AI Chatbot Interface
├── content-service:8005       # Content Management
├── community-service:8006     # Community Features
├── notification-service:8007  # Notifications
├── ml-service:8008           # Machine Learning
├── media-service:8009        # Media Processing
├── translation-service:8010  # Language Translation
├── voice-service:8011        # Voice Processing
├── action-orchestrator:8012  # Action Coordination
├── ai-context-store:8013     # AI Context Storage
├── ai-event-processor:8014   # AI Event Processing
├── voice-event-processor:8015 # Voice Event Processing
├── memory-service:8017       # Memory & Pattern Analysis
├── proactive-assistance:8018 # Proactive Assistance
└── models-service:8080       # AI/ML Models (Internal: 8080, External: 8085)
```

## Core Components

### 1. Service Registry (`src/registry.py`)
**Purpose**: Dynamic service discovery and health management
**Features**:
- Automatic service registration/deregistration
- Health check monitoring with configurable intervals
- Service metadata storage (version, capabilities, load metrics)
- Load balancer integration

**Configuration**:
```python
class ServiceRegistry:
    def __init__(self):
        self.services = {}  # Active service instances
        self.health_checker = HealthChecker()
        self.load_balancer = LoadBalancerFactory.create_load_balancer()
```

### 2. Request Routing (`src/routing.py`)
**Purpose**: Intelligent request routing and load balancing
**Features**:
- Multiple load balancing strategies:
  - Round Robin (default)
  - Weighted round robin
  - Least connections
  - Random selection
- Request transformation and header management
- Timeout handling and retries
- Circuit breaker integration

**Routing Logic**:
```python
Route Resolution Process:
1. Parse incoming request (method, path, headers)
2. Identify target service from route patterns
3. Apply load balancing to select instance
4. Transform request (add auth headers, modify path)
5. Proxy request with timeout/retry logic
6. Transform response (add CORS, modify headers)
7. Return to client
```

### 3. Middleware Stack

#### Rate Limiting (`src/middleware.py`)
- **Implementation**: Redis-based sliding window
- **Default**: 100 requests/minute per client
- **Burst**: 20 requests in quick succession
- **Client ID**: IP + User-Agent hash

#### Circuit Breaker
- **Purpose**: Prevent cascade failures
- **Thresholds**: 50% error rate over 10 requests
- **States**: Closed → Open → Half-Open → Closed
- **Recovery**: 30-second timeout before retry

#### Security Middleware
- **JWT Validation**: Bearer token verification
- **CORS**: Configurable origins, methods, headers
- **Trusted Hosts**: Whitelist of allowed hosts
- **Rate Limiting**: Per-client request throttling

#### Enhanced V3 Middleware

##### Voice Routing Middleware (`src/middleware/voice_routing.py`)
- **Voice Command Processing**: Real-time voice command interpretation
- **Language Detection**: Automatic language identification
- **Voice Context**: Maintains voice session state
- **Integration**: Routes voice commands to appropriate services

##### AI Context Middleware (`src/middleware/ai_context.py`)
- **Context Preservation**: Maintains conversation context across requests
- **Memory Integration**: Links with memory service for pattern analysis
- **Cache Management**: Redis-based context caching (TTL: 300s)
- **Context Enrichment**: Adds AI insights to requests

##### Cultural Context Middleware (`src/middleware/cultural_context.py`)
- **Cultural Adaptation**: Applies cultural context to responses
- **Localization**: Dynamic content localization
- **Cultural Patterns**: Recognition of cultural communication patterns
- **Fallback**: Neutral culture when detection fails

##### Performance Middleware (`src/middleware/performance.py`)
- **Request Timing**: Tracks request/response times
- **Resource Monitoring**: CPU, memory, and connection tracking
- **Metrics Collection**: Prometheus-compatible metrics
- **Performance Alerts**: Automatic alerting on threshold breaches

### 4. WebSocket Management (`src/services/websocket_manager.py`)
**Purpose**: Real-time bidirectional communication
**Features**:
- Connection pooling and management
- Voice streaming support
- NATS integration for clustering
- Automatic reconnection handling
- Message queuing and delivery guarantees

**Architecture**:
```
WebSocket Flow:
Client ↔ API Gateway (8080) ↔ NATS (4222) ↔ Service Instances
                ↓
        Connection Pool Manager
                ↓
        Voice Stream Processor
                ↓
        AI Context Manager
```

### 5. Proxy Implementation (`src/routing.py`)
**Purpose**: Transparent request proxying to backend services
**Features**:
- HTTP/HTTPS support
- Request/response streaming
- Header manipulation
- Connection pooling
- Automatic retries

**Proxy Configuration**:
```python
class RequestProxy:
    def __init__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(
                limit=100,  # Connection pool size
                limit_per_host=10
            )
        )
```

## Security Architecture

### Authentication Flow
```
1. Client Request → API Gateway
2. Extract JWT from Authorization header
3. Validate token signature and expiration
4. Extract user context (user_id, roles, permissions)
5. Add X-User-* headers to service requests
6. Forward to target service
7. Service validates X-User headers
8. Process request and return response
```

### Service-to-Service Communication
- **Internal Network**: Docker bridge network `mantrapath-network`
- **Service Discovery**: DNS-based using service names
- **Authentication**: X-User headers added by gateway
- **Encryption**: TLS for external communication, internal network isolation

## Performance Characteristics

### Connection Management
- **HTTP Keep-Alive**: Enabled for all backend connections
- **Connection Pooling**: 100 total connections, 10 per service
- **Timeout Configuration**:
  - Connection: 5 seconds
  - Request: 30 seconds
  - Total: 60 seconds

### Caching Strategy
- **Response Caching**: Redis-based with 60-second TTL
- **Context Caching**: AI/Cultural context cached for 300 seconds
- **Service Discovery Cache**: 30-second TTL for service health status
- **Rate Limiting Cache**: Sliding window data in Redis

### Load Balancing Performance
```
Round Robin: O(1) selection time
Weighted: O(n) where n = number of instances
Least Connections: O(n) with connection tracking
Random: O(1) with good distribution
```

## Monitoring and Observability

### Health Checks
- **Endpoint**: `/health/live` - Basic liveness check
- **Endpoint**: `/health/ready` - Readiness including dependencies
- **Endpoint**: `/health/detailed` - Full system status
- **Service Health**: Continuous monitoring of backend services

### Metrics Collection
```
Prometheus Metrics (Port 9090):
- http_requests_total{method, path, status}
- request_duration_seconds{service, method}
- active_connections{service}
- circuit_breaker_state{service}
- cache_hit_ratio{type}
- websocket_connections_active
```

### Logging
```
Structured JSON Logging:
{
  "timestamp": "2025-08-27T10:30:00Z",
  "level": "INFO",
  "service": "api-gateway",
  "request_id": "req_123456",
  "user_id": "user_789",
  "method": "POST",
  "path": "/api/v1/chat",
  "target_service": "chatbot-service",
  "duration_ms": 150,
  "status": 200
}
```

## Configuration Management

### Environment Variables
All configuration is externalized through environment variables defined in `.env`:

```env
# Core Gateway Settings
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8000
WEBSOCKET_PORT=8080
METRICS_PORT=9090

# Performance Tuning
CONNECTION_POOL_SIZE=100
RESPONSE_CACHE_TTL=60
CONTEXT_CACHE_SIZE=10000
RATE_LIMIT_REQUESTS_PER_MINUTE=100

# Feature Flags
VOICE_ROUTING_ENABLED=true
AI_CONTEXT_ENABLED=true
CULTURAL_ADAPTATION_ENABLED=true
PERFORMANCE_MONITORING=true

# Service URLs (Dynamic)
SERVICE_AUTH_SERVICE_URL=http://auth-service:${AUTH_SERVICE_PORT}
SERVICE_CHATBOT_SERVICE_URL=http://chatbot-service:${CHATBOT_SERVICE_PORT}
# ... (all other services)
```

### Service Registration
Services automatically register with the gateway on startup:
```python
# Each service registers itself
await service_registry.register_service(
    name="chatbot-service",
    host="chatbot-service",
    port=8004,
    health_endpoint="/health",
    capabilities=["chat", "voice", "translation"]
)
```

## API Routing Patterns

### RESTful API Routes
```
Pattern: /api/v1/{service}/{resource}
Examples:
- /api/v1/auth/login → auth-service:8001/login
- /api/v1/chat/messages → chatbot-service:8004/messages
- /api/v1/profile/users → profile-service:8002/users
```

### WebSocket Routes
```
Pattern: /ws/{service}/{feature}
Examples:
- /ws/chat/stream → chatbot-service WebSocket
- /ws/voice/stream → voice-service WebSocket
- /ws/notifications → notification-service WebSocket
```

### Health and Management Routes
```
Gateway Routes:
- /health/live → Gateway health
- /health/ready → Gateway + dependencies
- /health/services → All service status
- /metrics → Prometheus metrics
- /admin/services → Service registry view
```

## Deployment and Scaling

### Container Configuration
```dockerfile
# Multi-stage build for optimization
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
EXPOSE 8000 8080 9090
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Horizontal Scaling
- **Load Balancer**: Multiple API Gateway instances behind external load balancer
- **Session Affinity**: WebSocket connections require sticky sessions
- **State Management**: All state in Redis/PostgreSQL for stateless gateway instances

### Resource Requirements
```
Minimum: 512MB RAM, 0.5 CPU cores
Recommended: 1GB RAM, 1 CPU core
High Load: 2GB RAM, 2 CPU cores
```

## Troubleshooting Guide

### Common Issues

1. **Port Conflicts**
   - Check: `docker compose ps` for port mappings
   - Verify: `.env` file has unique ports for each service
   - Fix: Update conflicting ports and restart services

2. **Service Discovery Failures**
   - Check: Service health endpoints responding
   - Verify: Docker network connectivity
   - Debug: `docker network inspect backend_mantrapath-network`

3. **WebSocket Connection Issues**
   - Verify: Port 8080 accessible and not conflicting
   - Check: NATS service running for clustering
   - Debug: WebSocket connection logs

4. **Performance Issues**
   - Monitor: `/metrics` endpoint for bottlenecks
   - Check: Redis connectivity and memory usage
   - Tune: Connection pool sizes and timeouts

### Debug Commands
```bash
# Check all service status
docker compose ps

# View API Gateway logs
docker compose logs -f api-gateway

# Test service connectivity
curl http://localhost:8000/health/services

# Check WebSocket connectivity
curl -H "Upgrade: websocket" http://localhost:8080/ws/test

# View metrics
curl http://localhost:9090/metrics
```

## Conclusion

The API Gateway serves as the intelligent orchestration layer for the MantraPath platform, providing secure, scalable, and feature-rich access to all backend services. The architecture supports advanced features like voice processing, AI context management, and cultural adaptation while maintaining high performance and reliability.

**Key Benefits:**
- **Single Entry Point**: All client requests go through one gateway
- **Service Abstraction**: Clients don't need to know individual service locations
- **Security Centralization**: Authentication and authorization in one place
- **Performance Optimization**: Caching, load balancing, and connection pooling
- **Observability**: Centralized logging, metrics, and monitoring
- **Feature Enhancement**: Voice, AI, and cultural capabilities
