# API Gateway Service

## Overview

The API Gateway serves as the central entry point for all client requests in the MantraPath microservices architecture. It routes requests to appropriate backend services, handles CORS, and provides service discovery capabilities.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   API Gateway    │───▶│  Microservices  │
│   (Port 5174)   │    │   (Port 8000)    │    │  (Ports 8001+)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Key Features

### 🚀 **Request Routing**
- **Intelligent Path-Based Routing**: Routes requests to appropriate services based on URL patterns
- **Service Discovery**: Maintains registry of all backend services
- **Universal Handler**: Single endpoint handles all HTTP methods (GET, POST, PUT, DELETE, PATCH, OPTIONS)

### 🔒 **Security & CORS**
- **CORS Middleware**: Configured for development environments (localhost:3000, 5173, 5174)
- **Header Management**: Properly forwards and manages HTTP headers
- **Preflight Handling**: Automatic OPTIONS request handling for CORS

### 🔄 **Request Proxying**
- **Async HTTP Client**: Uses httpx for high-performance async requests
- **Body Forwarding**: Handles request bodies for POST/PUT/PATCH operations
- **Query Parameter Preservation**: Maintains all query parameters in forwarded requests
- **Response Streaming**: Efficient response forwarding with proper status codes

### 📊 **Monitoring & Health**
- **Health Checks**: Built-in health endpoint for service monitoring
- **Service Registry**: Endpoint to list all registered services
- **Request Logging**: Comprehensive logging of all routed requests
- **Error Handling**: Graceful error handling with appropriate HTTP status codes

## Service Registry

The gateway maintains a registry of all microservices:

```python
SERVICES = {
    "auth": "http://localhost:8001",           # Authentication & User Management
    "profile": "http://localhost:8002",        # User Profiles & Preferences  
    "mood": "http://localhost:8003",           # Mood Tracking & Analytics
    "chatbot": "http://localhost:8004",        # AI Chatbot (Mitra)
    "content": "http://localhost:8005",         # Content & Affirmations
    "community": "http://localhost:8006",      # Forums & Community
    "notification": "http://localhost:8007",   # Real-time Notifications
    "ml": "http://localhost:8008",             # Machine Learning Services
    "media": "http://localhost:8009",          # Media & File Management
}
```

## Routing Logic

### **Authentication Service Routes**
```
/auth/*           → Auth Service (8001)
/register         → Auth Service (8001)
/login            → Auth Service (8001)
/logout           → Auth Service (8001)
/refresh-token    → Auth Service (8001)
/me               → Auth Service (8001)
/users/*          → Auth Service (8001)
```

### **Profile Service Routes**
```
/api/profiles/*     → Profile Service (8002)
/api/preferences/*  → Profile Service (8002)
```

### **Mood Service Routes**
```
/api/v1/mood/*      → Mood Service (8003)
/api/v1/journal/*   → Mood Service (8003)
/api/v1/habits/*    → Mood Service (8003)
/api/v1/insights/*  → Mood Service (8003)
/api/v1/analytics/* → Mood Service (8003)
```

### **Chatbot Service Routes**
```
/api/chatbot/*      → Chatbot Service (8004)
```

### **Content Service Routes**
```
/content/*          → Content Service (8005)
/affirmations       → Content Service (8005)
/bookmark/*         → Content Service (8005)
/challenge/*        → Content Service (8005)
```

### **Community Service Routes**
```
/forums             → Community Service (8006)
/user/stats         → Community Service (8006)
/user/activity      → Community Service (8006)
```

### **Notification Service Routes**
```
/notify/*           → Notification Service (8007)
/notifications      → Notification Service (8007)
```

### **ML Service Routes**
```
/api/v1/ml/*        → ML Service (8008) [strips /api/v1/ml/ prefix]
/api/ml/*           → ML Service (8008) [strips /api/ml/ prefix]
/ml/*               → ML Service (8008) [direct routing]
```

### **Media Service Routes**
```
/api/v1/media/*     → Media Service (8009)
```

## Core Functions

### `get_service_url(path: str) -> tuple[str, str]`
**Purpose**: Determines which service to route to based on the request path

**Logic**:
1. Analyzes the incoming path
2. Matches against predefined route patterns
3. Returns service URL and modified path
4. Defaults to auth service for unmatched routes

**Example**:
```python
# Input: "/api/v1/mood/entries"
# Output: ("http://localhost:8003", "/api/v1/mood/entries")

# Input: "/api/ml/predict-timing"  
# Output: ("http://localhost:8008", "/ml/predict-timing")
```

### `proxy_request(request, service_url, path)`
**Purpose**: Forwards the request to the appropriate microservice

**Process**:
1. **URL Construction**: Builds target service URL with proper path
2. **Header Processing**: Extracts and cleans request headers (removes 'host')
3. **Query Parameters**: Preserves all query parameters
4. **Body Handling**: Extracts request body for POST/PUT/PATCH requests
5. **HTTP Client**: Uses async httpx client with 30-second timeout
6. **Response Forwarding**: Returns response with original status code and headers
7. **Error Handling**: Catches and handles network/service errors

## API Endpoints

### **Health Check**
```http
GET /health
```
**Response**:
```json
{
  "status": "healthy",
  "service": "api-gateway"
}
```

### **Service Registry**
```http
GET /services
```
**Response**:
```json
{
  "services": {
    "auth": "http://localhost:8001",
    "profile": "http://localhost:8002",
    "mood": "http://localhost:8003",
    // ... other services
  }
}
```

### **Universal Route Handler**
```http
{METHOD} /{path:path}
```
**Supported Methods**: GET, POST, PUT, DELETE, PATCH, OPTIONS

**Process**:
1. CORS preflight handling for OPTIONS requests
2. Path analysis and service determination
3. Request proxying to target service
4. Response forwarding to client

## Configuration

### **Environment Variables**
```bash
# Service URLs (with defaults)
AUTH_SERVICE_URL=http://localhost:8001
PROFILE_SERVICE_URL=http://localhost:8002
MOOD_SERVICE_URL=http://localhost:8003
CHATBOT_SERVICE_URL=http://localhost:8004
CONTENT_SERVICE_URL=http://localhost:8005
COMMUNITY_SERVICE_URL=http://localhost:8006
NOTIFICATION_SERVICE_URL=http://localhost:8007
ML_SERVICE_URL=http://localhost:8008
MEDIA_SERVICE_URL=http://localhost:8009
```

### **CORS Configuration**
```python
allow_origins=[
    "http://localhost:3000",   # React dev server
    "http://localhost:5173",   # Vite dev server (old)
    "http://localhost:5174"    # Vite dev server (current)
]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

## Docker Configuration

### **Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y curl

# Install dependencies
COPY services/api_gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules and service code
COPY shared /app/shared
COPY services/api_gateway /app/

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Dependencies** (`requirements.txt`)
```
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.2
python-dotenv==1.0.0
```

## Error Handling

### **Service Unavailable (503)**
- Triggered when target service is unreachable
- Returns: `{"detail": "Service temporarily unavailable"}`

### **Internal Server Error (500)**
- Triggered by unexpected errors during proxying
- Returns: `{"detail": "Internal server error"}`

### **Request Timeout**
- 30-second timeout for all proxied requests
- Prevents hanging connections

## Logging

The gateway provides comprehensive request logging:

```python
logger.info(f"Routing {request.method} /{path} to {service_url}{service_path}")
```

**Log Format**: `Routing GET /api/v1/mood/entries to http://localhost:8003/api/v1/mood/entries`

## Performance Features

### **Async Architecture**
- Built on FastAPI's async foundation
- Non-blocking request handling
- Concurrent request processing

### **Connection Pooling**
- httpx.AsyncClient with automatic connection pooling
- Efficient resource utilization
- Reduced connection overhead

### **Minimal Processing**
- Direct request/response forwarding
- No unnecessary data transformation
- Low-latency routing

## Development

### **Local Development**
```bash
# Start the gateway
cd backend/services/api_gateway
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Test health endpoint
curl http://localhost:8000/health

# Test service registry
curl http://localhost:8000/services
```

### **Docker Development**
```bash
# Build and run with Docker Compose
cd backend
docker-compose up api-gateway

# Check logs
docker-compose logs -f api-gateway
```

## Security Considerations

### **Header Security**
- Removes 'host' header to prevent conflicts
- Forwards authentication headers properly
- Maintains request integrity

### **CORS Policy**
- Configured for development environments
- Should be restricted in production
- Supports credentials for authenticated requests

### **Request Validation**
- No request modification or validation at gateway level
- Delegates all validation to target services
- Maintains service autonomy

## Monitoring & Observability

### **Health Monitoring**
```bash
# Gateway health
curl http://localhost:8000/health

# Service discovery
curl http://localhost:8000/services
```

### **Request Tracing**
- All requests logged with method, path, and target service
- Error logging for failed requests
- Performance monitoring capabilities

## Future Enhancements

### **Planned Features**
- [ ] **Rate Limiting**: Request throttling per client
- [ ] **Authentication**: JWT validation at gateway level
- [ ] **Load Balancing**: Multiple instances per service
- [ ] **Circuit Breaker**: Fault tolerance patterns
- [ ] **Request Caching**: Response caching for GET requests
- [ ] **Metrics Collection**: Prometheus metrics integration
- [ ] **Request Transformation**: Header/body modification capabilities

### **Production Readiness**
- [ ] **SSL/TLS Termination**: HTTPS support
- [ ] **Production CORS**: Restricted origin configuration
- [ ] **Health Check Endpoints**: Deep health checks for all services
- [ ] **Graceful Shutdown**: Proper connection cleanup
- [ ] **Configuration Management**: External config support

## Troubleshooting

### **Common Issues**

**Service Unavailable Errors**:
- Check if target service is running
- Verify service URLs in environment variables
- Check network connectivity between containers

**CORS Errors**:
- Verify frontend URL is in allowed origins
- Check if credentials are properly configured
- Ensure preflight requests are handled

**Timeout Errors**:
- Check if target service is responding within 30 seconds
- Monitor service performance and response times
- Consider increasing timeout for slow operations

### **Debug Commands**
```bash
# Check service connectivity
curl http://localhost:8001/health  # Auth service
curl http://localhost:8003/health  # Mood service

# Test gateway routing
curl -X GET http://localhost:8000/health
curl -X GET http://localhost:8000/services

# Check logs
docker-compose logs -f api-gateway
```