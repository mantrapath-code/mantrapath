# MantraPath Deployment API Service

## Overview

The **MantraPath Deployment API Service** is a specialized gateway service that provides frontend engineers with controlled access to backend services without exposing the entire codebase. This service acts as an intelligent proxy that offers API documentation, model training monitoring, service health checks, and usage analytics while maintaining strict access control and rate limiting.

### Key Features

- 🔐 **Controlled Access** - Multi-tiered permission system for frontend engineers
- 📚 **API Documentation** - Comprehensive, interactive API documentation for all services
- 🤖 **Model Training Monitor** - Real-time AI model training progress and metrics
- 🩺 **Health Monitoring** - Backend service health status and performance tracking
- 🧪 **API Testing Tools** - Interactive endpoint testing and validation
- 📊 **Usage Analytics** - Request tracking, quotas, and usage metrics
- 🚦 **Rate Limiting** - Intelligent rate limiting per engineer and permission level
- 🔑 **JWT Authentication** - Secure token-based authentication system

## Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Engineers                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   React     │  │   Vue.js    │  │     Angular         │ │
│  │  Developer  │  │ Developer   │  │    Developer        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Deployment API Service                       │
│                    (Port 8086)                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Auth &    │  │ Rate       │  │   API               │ │
│  │  Permissions│  │ Limiting   │  │ Documentation       │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Model     │  │ Service    │  │   Usage             │ │
│  │  Monitoring │  │ Health     │  │   Tracking          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Backend Services                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Voice     │  │   Models    │  │   Community         │ │
│  │  Service    │  │  Service    │  │   Service           │ │
│  │ (Port 8011) │  │ (Port 8080) │  │  (Port 8006)        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │     ML      │  │  API        │  │   Auth              │ │
│  │  Service    │  │  Gateway    │  │   Service           │ │
│  │ (Port 8008) │  │ (Port 8000) │  │  (Port 8001)        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
deployment_api/
├── src/                                 # Source code directory
│   ├── main.py                         # FastAPI application entry point (527 lines)
│   ├── config/                         # Configuration management
│   │   ├── settings.py                 # Application settings (113 lines)
│   │   └── permissions.py              # Access control configuration (248 lines)
│   ├── services/                       # Core service modules
│   │   ├── api_documentation.py        # API documentation generator (524 lines)
│   │   ├── model_monitor.py            # Model training monitor (230 lines)
│   │   ├── health_checker.py           # Service health monitoring (265 lines)
│   │   └── usage_tracker.py            # Usage analytics and tracking
│   └── utils/                          # Utility modules
│       ├── auth.py                     # JWT authentication (158 lines)
│       └── rate_limiting.py            # Rate limiting implementation (197 lines)
├── requirements.txt                     # Python dependencies
├── Dockerfile                          # Container configuration (Port 8086)
├── start.sh                            # Local development startup script (98 lines)
├── DEPLOYMENT_GUIDE.md                 # Step-by-step deployment guide (439 lines)
└── IMPLEMENTATION_SUMMARY.md           # Implementation overview (340 lines)
```

## API Endpoints

### Core Service Information

#### GET `/`
**Service Root Information**
```json
Response:
{
  "service": "MantraPath Deployment API",
  "version": "1.0.0",
  "description": "Controlled API access for frontend engineers",
  "features": [
    "API Documentation",
    "Model Training Status",
    "Service Health Monitoring", 
    "API Testing Tools",
    "Usage Metrics"
  ],
  "documentation": "/docs",
  "health": "/health"
}
```

#### GET `/health`
**Service Health Check**
```json
Response:
{
  "status": "healthy",
  "timestamp": 1705320600.0,
  "service": "deployment_api",
  "details": {
    "services": {
      "api_gateway": {"status": "healthy", "response_time": 45},
      "voice_service": {"status": "healthy", "response_time": 23},
      "models_service": {"status": "healthy", "response_time": 67}
    }
  }
}
```

### API Documentation

#### GET `/api/docs` 🔒
**Get Complete API Documentation** *(Requires Authentication)*
```json
Response:
{
  "status": "success",
  "data": {
    "services": {
      "voice_service": {
        "name": "Voice Service",
        "description": "Speech-to-text and text-to-speech capabilities",
        "endpoints": [
          {
            "path": "/api/voice/stt",
            "method": "POST",
            "description": "Convert speech to text",
            "parameters": {
              "audio_file": "Audio file (WAV, MP3, etc.)",
              "language": "Language code (en, hi, bn, etc.)"
            }
          }
        ]
      }
    }
  },
  "timestamp": 1705320600.0,
  "permissions": {"api_docs": "read", "rate_limit": 500}
}
```

#### GET `/api/docs/{service_name}` 🔒
**Get Service-Specific Documentation** *(Requires Authentication)*
```json
Path Parameters:
- service_name: str (voice_service|community_service|models_service|ml_service)

Response:
{
  "status": "success",
  "service": "voice_service",
  "data": {
    "endpoints": [...],
    "schemas": {...},
    "examples": {...}
  },
  "timestamp": 1705320600.0,
  "permissions": {...}
}
```

### Model Training Monitoring

#### GET `/api/models/status` 🔒
**Get Overall Model Training Status** *(Requires Authentication)*
```json
Response:
{
  "status": "success",
  "data": {
    "summary": {
      "total_models": 3,
      "training": 1,
      "completed": 1,
      "queued": 1,
      "average_progress": 75.0
    },
    "models": {
      "stt_hindi": {
        "id": "stt_hindi",
        "name": "Hindi Speech Recognition",
        "type": "speech_recognition",
        "status": "training",
        "progress": 75,
        "current_epoch": 15,
        "total_epochs": 20,
        "accuracy": 0.89,
        "loss": 0.12,
        "gpu_usage": 85,
        "memory_usage": 12.5
      }
    },
    "last_updated": "2024-01-15T10:30:00Z"
  },
  "timestamp": 1705320600.0,
  "permissions": {...}
}
```

#### GET `/api/models/status/{model_type}` 🔒
**Get Model Type Specific Status** *(Requires Authentication)*
```json
Path Parameters:
- model_type: str (speech_recognition|text_to_speech|natural_language_processing)

Response:
{
  "status": "success",
  "model_type": "speech_recognition",
  "data": {
    "stt_hindi": {...},
    "stt_bengali": {...}
  },
  "count": 2,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

### Service Health Monitoring

#### GET `/api/health/services` 🔒
**Get All Services Health Status** *(Requires Authentication)*
```json
Response:
{
  "status": "success",
  "data": {
    "api_gateway": {
      "status": "healthy",
      "response_time": 45,
      "last_check": "2024-01-15T10:30:00Z",
      "critical": true
    },
    "voice_service": {
      "status": "healthy", 
      "response_time": 23,
      "last_check": "2024-01-15T10:30:00Z",
      "critical": true
    },
    "community_service": {
      "status": "degraded",
      "response_time": 150,
      "last_check": "2024-01-15T10:30:00Z",
      "critical": false
    }
  },
  "last_updated": "2024-01-15T10:30:00Z"
}
```

#### GET `/api/health/services/{service_name}` 🔒
**Get Specific Service Health** *(Requires Authentication)*
```json
Path Parameters:
- service_name: str (api_gateway|voice_service|models_service|community_service|ml_service)

Response:
{
  "status": "success",
  "service": "voice_service",
  "data": {
    "status": "healthy",
    "response_time": 23,
    "uptime": "99.8%",
    "last_error": null,
    "metrics": {
      "requests_per_minute": 145,
      "avg_response_time": 23,
      "error_rate": 0.002
    }
  },
  "timestamp": 1705320600.0
}
```

### API Testing Tools

#### POST `/api/testing/test-endpoint` 🔒
**Test API Endpoint** *(Requires Enhanced+ Permissions)*
```json
Request:
{
  "service": "voice_service",
  "endpoint": "/api/voice/models", 
  "method": "GET",
  "parameters": {},
  "headers": {}
}

Response:
{
  "status": "success",
  "data": {
    "test_result": "passed",
    "response_time": 45,
    "status_code": 200,
    "response_body": {...}
  },
  "timestamp": 1705320600.0,
  "permissions": {...}
}
```

### Usage Analytics

#### GET `/api/usage/metrics` 🔒
**Get Usage Metrics for Authenticated Engineer** *(Requires Authentication)*
```json
Response:
{
  "status": "success",
  "data": {
    "engineer_id": "fe_001",
    "current_period": {
      "requests_made": 245,
      "requests_limit": 500,
      "requests_remaining": 255,
      "reset_time": "2024-01-15T11:00:00Z"
    },
    "popular_endpoints": [
      {"endpoint": "/api/docs", "count": 89},
      {"endpoint": "/api/models/status", "count": 67},
      {"endpoint": "/api/health/services", "count": 45}
    ],
    "last_30_days": {
      "total_requests": 3420,
      "avg_daily_requests": 114,
      "most_active_day": "2024-01-10"
    }
  },
  "timestamp": 1705320600.0
}
```

## Configuration

### Environment Variables

```bash
# Service Configuration  
DEPLOYMENT_API_PORT=8086
DEPLOYMENT_API_HOST=0.0.0.0
ENVIRONMENT=development  # development|staging|production
DEBUG=true

# Authentication
FRONTEND_ENGINEER_SECRET=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Rate Limiting
RATE_LIMIT_ENABLED=true
DEFAULT_RATE_LIMIT=1000        # requests per minute
FRONTEND_ENGINEER_LIMIT=500    # requests per minute

# CORS Configuration
FRONTEND_URL=http://frontend:5173
CORS_ADDITIONAL_ORIGINS=http://localhost:3000,http://localhost:5173
ALLOWED_HOSTS_ADDITIONAL=localhost,127.0.0.1

# Service Discovery (Backend Services)
API_GATEWAY_URL=http://api-gateway:8000
VOICE_SERVICE_URL=http://voice-service:8011
MODELS_SERVICE_URL=http://models-service:8080
COMMUNITY_SERVICE_URL=http://community-service:8006
ML_SERVICE_URL=http://ml-service:8008

# Data Storage
REDIS_URL=redis://redis:6379
REDIS_DB=0
DATABASE_URL=postgresql://mantrapath:mantrapath123@postgres:5432/mantrapath

# Monitoring Configuration
MODEL_TRAINING_CHECK_INTERVAL=30   # seconds
MODEL_TRAINING_TIMEOUT=300         # seconds
HEALTH_CHECK_INTERVAL=30           # seconds
HEALTH_CHECK_TIMEOUT=10            # seconds

# Documentation & Caching
DOCS_CACHE_TTL=300                 # seconds (5 minutes)
DOCS_MAX_SIZE=1024                 # MB

# Usage Tracking
USAGE_TRACKING_ENABLED=true
USAGE_RETENTION_DAYS=90

# Logging
LOG_LEVEL=INFO
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Permission Levels

The service implements a three-tier permission system:

#### Basic Permission Level
```python
"basic": {
    "api_docs": "read",
    "service_health": "read", 
    "model_status": "read",
    "api_testing": "limited",
    "rate_limit": 100,  # requests per minute
    "features": [
        "view_api_documentation",
        "view_service_health",
        "view_model_training_status",
        "limited_api_testing"
    ]
}
```

#### Enhanced Permission Level
```python
"enhanced": {
    "api_docs": "read",
    "service_health": "read",
    "model_status": "read", 
    "api_testing": "full",
    "rate_limit": 500,  # requests per minute
    "features": [
        "view_api_documentation",
        "view_service_health",
        "view_model_training_status",
        "full_api_testing",
        "view_usage_metrics"
    ]
}
```

#### Premium Permission Level
```python
"premium": {
    "api_docs": "read",
    "service_health": "read",
    "model_status": "read",
    "api_testing": "full",
    "advanced_features": "read",
    "rate_limit": 1000,  # requests per minute
    "features": [
        "view_api_documentation",
        "view_service_health", 
        "view_model_training_status",
        "full_api_testing",
        "view_usage_metrics",
        "advanced_analytics",
        "custom_dashboards",
        "priority_support"
    ]
}
```

## Request Flow

```mermaid
sequenceDiagram
    participant FE as Frontend Engineer
    participant Auth as Auth Service
    participant Rate as Rate Limiter
    participant API as Deployment API
    participant Backend as Backend Services

    FE->>API: Request with JWT token
    API->>Auth: Validate JWT token
    Auth-->>API: Engineer permissions
    API->>Rate: Check rate limits
    Rate-->>API: Limit status
    
    alt Rate limit OK
        API->>Backend: Fetch requested data
        Backend-->>API: Service response
        API-->>FE: Formatted response + usage data
    else Rate limit exceeded
        API-->>FE: HTTP 429 Too Many Requests
    end
    
    Note over API: Track usage metrics
    Note over API: Update engineer activity
```

## Authentication & Security

### JWT Token Authentication
```python
# JWT Token Payload
{
    "sub": "fe_001",                    # Engineer ID
    "iat": 1705320600,                  # Issued at
    "exp": 1705324200,                  # Expires at (1 hour)
    "permission_level": "enhanced",      # Permission tier
    "features": [...]                   # Available features
}
```

### Frontend Engineer Registration
```python
# Mock engineer database (production would use real DB)
engineers_db = {
    "fe_001": {
        "id": "fe_001",
        "name": "Frontend Engineer 1",
        "email": "fe1@example.com",
        "permission_level": "enhanced",
        "created_at": "2024-01-01T00:00:00Z",
        "last_active": "2024-01-15T10:30:00Z"
    }
}
```

### Rate Limiting Strategy
- **Sliding Window**: 60-second rolling window for request counting
- **Per-Engineer Limits**: Based on permission level (100-1000 req/min)
- **Per-Endpoint Limits**: Specific limits for resource-intensive operations
- **Graceful Degradation**: Fail-open approach if rate limiter encounters errors

## Service Communication

### Backend Service Integration
The deployment API communicates with backend services via HTTP:

```python
# Service endpoints for health monitoring
services = {
    "api_gateway": {
        "url": "http://api-gateway:8000/health",
        "critical": True
    },
    "voice_service": {
        "url": "http://voice-service:8011/health", 
        "critical": True
    },
    "models_service": {
        "url": "http://models-service:8080/health",
        "critical": True
    },
    "community_service": {
        "url": "http://community-service:8006/health",
        "critical": False
    },
    "ml_service": {
        "url": "http://ml-service:8008/health", 
        "critical": False
    }
}
```

### Model Training Integration
```python
# Real-time model training status (mock data)
models = {
    "stt_hindi": {
        "status": "training",
        "progress": 75,
        "current_epoch": 15,
        "total_epochs": 20,
        "accuracy": 0.89,
        "gpu_usage": 85
    }
}
```

## Development & Testing

### Running Locally

```bash
# Quick start with startup script
chmod +x start.sh
./start.sh

# Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8086 --reload
```

### Docker Deployment

```bash
# Build and run container
docker build -t mantrapath/deployment-api .
docker run -d \
  --name deployment-api \
  -p 8086:8086 \
  -e ENVIRONMENT=production \
  -e DEBUG=false \
  mantrapath/deployment-api
```

### Testing Strategy

```bash
# Unit Testing (to be implemented)
python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Test Categories
python -m pytest tests/test_auth.py -v           # Authentication tests
python -m pytest tests/test_permissions.py -v   # Permission system tests
python -m pytest tests/test_rate_limiting.py -v # Rate limiting tests
python -m pytest tests/test_api_docs.py -v      # API documentation tests
python -m pytest tests/test_health.py -v        # Health monitoring tests
python -m pytest tests/test_models.py -v        # Model monitoring tests
```

### Integration Testing
- **Authentication Flow**: JWT token creation, validation, and expiration
- **Permission Enforcement**: Access control for different engineer tiers
- **Rate Limiting**: Request throttling and quota management
- **Service Health**: Backend service connectivity and health status
- **Model Monitoring**: Training progress and metrics collection

## Monitoring & Analytics

### Health Monitoring
```json
{
  "status": "healthy",
  "components": {
    "authentication": "operational",
    "rate_limiting": "operational", 
    "service_health": "operational",
    "model_monitoring": "operational",
    "usage_tracking": "operational"
  },
  "metrics": {
    "active_engineers": 12,
    "requests_per_minute": 340,
    "avg_response_time": 45,
    "cache_hit_ratio": 0.85
  }
}
```

### Usage Analytics
- **Request Patterns**: Peak usage times and popular endpoints
- **Engineer Activity**: Individual and aggregate usage statistics
- **Performance Metrics**: Response times and error rates
- **Resource Utilization**: CPU, memory, and network usage
- **Rate Limit Analysis**: Throttling effectiveness and limit violations

### Logging Strategy
```python
# Structured logging for operations
logger.info(f"Engineer {engineer_id} authenticated with {permission_level} permissions")
logger.warning(f"Rate limit exceeded for engineer {engineer_id} on {endpoint}")
logger.error(f"Failed to fetch health status from {service_name}: {error}")
```

## Security Considerations

### Access Control
- **JWT Token Security**: Secure token generation and validation
- **Permission Isolation**: Strict enforcement of permission boundaries
- **Rate Limiting**: Protection against abuse and DoS attacks
- **Input Validation**: Comprehensive request parameter validation

### Data Protection
- **No Backend Access**: Engineers cannot access backend codebases
- **Filtered Responses**: Only permitted data is exposed in responses
- **Usage Tracking**: All access is logged for audit purposes
- **Secure Communication**: HTTPS enforcement in production

## Performance Optimization

### Caching Strategy
```python
# Multi-level caching approach
class CacheStrategy:
    api_docs_cache = 300 seconds      # 5 minutes
    health_status_cache = 30 seconds   # 30 seconds
    model_status_cache = 60 seconds    # 1 minute
    engineer_permissions = 3600 seconds # 1 hour
```

### Scalability Features
- **Horizontal Scaling**: Stateless design supports multiple instances
- **Connection Pooling**: Efficient HTTP client management
- **Background Tasks**: Async health checks and metrics collection
- **Resource Management**: Intelligent caching and request batching

## Future Development Plans

### Phase 1 - Enhanced Monitoring (Q2 2024)
- [ ] **Real-Time Dashboards** - Interactive monitoring dashboards for engineers
- [ ] **Advanced Analytics** - Detailed usage patterns and performance metrics
- [ ] **Alert System** - Proactive notifications for service issues
- [ ] **Custom Filters** - Advanced filtering for API documentation and health data

### Phase 2 - Developer Tools (Q3 2024)
- [ ] **API Playground** - Interactive API testing environment
- [ ] **Code Generation** - Auto-generated SDK and client libraries
- [ ] **Mock Services** - Mock backend services for frontend development
- [ ] **Debugging Tools** - Request tracing and performance profiling

### Phase 3 - Advanced Features (Q4 2024)
- [ ] **GraphQL Support** - GraphQL endpoint for complex data queries
- [ ] **Webhook Integration** - Real-time notifications via webhooks
- [ ] **Custom Dashboards** - Engineer-specific dashboard customization
- [ ] **API Versioning** - Version management for evolving APIs

### Phase 4 - Enterprise Features (2025)
- [ ] **SSO Integration** - Single sign-on with enterprise identity providers
- [ ] **Advanced RBAC** - Role-based access control with fine-grained permissions
- [ ] **Audit Logging** - Comprehensive audit trails for compliance
- [ ] **Multi-tenant Support** - Support for multiple organizations

## Incomplete Implementations & TODOs

### Current Limitations
- **Test Coverage**: No automated test suite implemented
- **Real Model Integration**: Mock model training data instead of real ML pipeline
- **Database Persistence**: In-memory storage for engineers and usage data
- **Advanced Analytics**: Basic usage tracking without detailed insights
- **Error Recovery**: Limited error handling and retry mechanisms

### Known TODOs
```python
# From main.py and service modules analysis
# TODO: Implement comprehensive test suite with pytest
# TODO: Integrate with real ML training pipeline for model monitoring
# TODO: Add database persistence for engineers and usage analytics
# TODO: Implement advanced caching with Redis
# TODO: Add comprehensive error handling and retry logic
# TODO: Create interactive API playground interface
# TODO: Add webhook support for real-time notifications
# TODO: Implement SSO integration for enterprise environments
# TODO: Add GraphQL support for complex queries
# TODO: Create custom dashboard builder for engineers
```

### Technical Debt
- **Hardcoded Data**: Mock data for engineers, models, and services
- **Error Handling**: Basic exception handling needs enhancement
- **Configuration Management**: Environment-specific configuration needs refinement
- **Documentation**: OpenAPI schema generation needs improvement
- **Performance**: Response caching and optimization opportunities

### Missing Features
- **Real-time Updates**: WebSocket support for live data updates
- **API Versioning**: Version management for backward compatibility
- **Advanced Filtering**: Complex query capabilities for large datasets
- **Custom Alerts**: User-defined alert rules and notifications
- **Integration Testing**: End-to-end testing with real backend services

## Production Deployment

### Container Configuration
```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY shared/ ./shared/

# Create non-root user
RUN useradd --create-home app && chown -R app:app /app
USER app

# Expose port and run
EXPOSE 8086
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8086"]
```

### Environment-Specific Configuration
```python
# Production overrides
if ENVIRONMENT == "production":
    DEBUG = False
    LOG_LEVEL = "WARNING"
    ALLOWED_ORIGINS = ["https://yourdomain.com"]
    RATE_LIMIT_ENABLED = True
    USAGE_TRACKING_ENABLED = True
```

## Contributing

### Development Guidelines
1. **Security First**: All changes must maintain strict access control
2. **Performance Aware**: Consider rate limiting and caching implications
3. **Documentation**: Update API docs for all endpoint changes
4. **Testing**: Write tests for authentication and permission logic
5. **Monitoring**: Add logging for all significant operations

### Key Areas for Contribution
- **Authentication Systems** - Enhanced security and SSO integration
- **Performance Optimization** - Caching strategies and response optimization
- **Developer Tools** - Interactive testing and debugging utilities
- **Analytics & Monitoring** - Advanced usage insights and alerting
- **API Enhancement** - GraphQL support and advanced query capabilities

---

**Service Status**: ✅ Active Development  
**Port**: 8086  
**Version**: 1.0.0  
**Last Updated**: January 2024  
**Maintainer**: MantraPath Development Team  
**Security Level**: Controlled Access - Frontend Engineers Only