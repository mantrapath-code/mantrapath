# MantraPath API Gateway

A modular, scalable API Gateway built with FastAPI for the MantraPath platform.

## Overview

The MantraPath API Gateway serves as the central entry point for all backend services, providing:

- **Service Discovery & Registry**: Automatic service registration and health monitoring
- **Load Balancing**: Multiple strategies (round-robin, weighted, least connections, random)
- **Rate Limiting**: Configurable request rate limiting per user/IP
- **Circuit Breaker**: Service resilience and failure protection
- **Health Monitoring**: Comprehensive health checks and metrics
- **Request Proxying**: Intelligent request routing to backend services

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │    │   Mobile App    │    │   3rd Party     │
│   (React/Vue)   │    │     (React      │    │     APIs        │
│                 │    │     Native)     │    │                 │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 │         API Gateway           │
                 │  ┌─────────────────────────┐  │
                 │  │  Rate Limiting         │  │
                 │  │  Circuit Breaker       │  │
                 │  │  Load Balancing        │  │
                 │  │  Service Discovery     │  │
                 │  └─────────────────────────┘  │
                 └───────────────┬───────────────┘
                                 │
      ┌──────────────────────────┼──────────────────────────┐
      │                          │                          │
┌─────┴─────┐            ┌─────┴─────┐            ┌─────┴─────┐
│   Auth    │            │   Mood    │            │  Content  │
│  Service  │            │  Service  │            │  Service  │
│           │            │           │            │           │
└───────────┘            └───────────┘            └───────────┘
```

## Features

### Service Registry
- Automatic service discovery
- Health check monitoring (30s intervals)
- Service instance management
- Failover and recovery

### Load Balancing
- **Round Robin**: Evenly distribute requests
- **Weighted**: Distribute based on service weights
- **Least Connections**: Route to least busy service
- **Random**: Random distribution

### Rate Limiting
- Per-user and per-IP rate limiting
- Configurable limits (default: 100 req/min)
- Token bucket algorithm
- Graceful degradation

### Circuit Breaker
- Automatic failure detection
- Service protection during outages
- Configurable failure thresholds
- Auto-recovery mechanisms

### Health Monitoring
- Gateway health endpoints
- Per-service health status
- Detailed service metrics
- Prometheus-compatible metrics

## Quick Start

### Prerequisites
- Python 3.11+
- Redis (for caching and rate limiting)
- Backend services running

### Installation

1. **Install dependencies**:
```bash
cd backend/services/api_gateway
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp config/.env.example .env
# Edit .env with your settings
```

3. **Start the gateway**:
```bash
# Development
python src/main.py

# Production with Uvicorn
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Docker Deployment

```bash
# Build the image
docker build -t mantrapath-gateway .

# Run the container
docker run -p 8000:8000 \
  -e GATEWAY_REDIS_URL=redis://redis:6379 \
  mantrapath-gateway
```

## Configuration

The gateway uses environment variables for configuration. See `config/.env.example` for all available options.

### Key Configuration Options

- `GATEWAY_PORT`: Gateway port (default: 8000)
- `GATEWAY_RATE_LIMIT_REQUESTS_PER_MINUTE`: Rate limit (default: 100)
- `GATEWAY_LOAD_BALANCING_STRATEGY`: Load balancing strategy
- `SERVICE_*_URL`: Backend service URLs

## API Endpoints

### Health Endpoints
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health with service info
- `GET /health/ready` - Kubernetes readiness probe
- `GET /health/live` - Kubernetes liveness probe
- `GET /health/services/{service_name}` - Specific service health

### Metrics
- `GET /metrics` - Gateway and service metrics

### Proxy Endpoints
All other requests are proxied to backend services based on routing rules.

## Service Integration

### Adding a New Service

1. **Add service configuration**:
```env
SERVICE_MYSERVICE_URL=http://localhost:8012
SERVICE_MYSERVICE_HEALTH_PATH=/health
```

2. **Update routing rules** in `src/routing/router.py`:
```python
RouteRule(
    path_pattern=r"^/myservice/.*",
    methods=[HTTPMethod.GET, HTTPMethod.POST],
    service_name="myservice",
    timeout=30,
    retries=2,
    auth_required=True
)
```

3. **Register service** in `src/registry/service_registry.py`:
```python
("myservice", service_config.myservice_service_url, service_config.myservice_service_health_path)
```

### Service Requirements

Backend services must implement:
- Health check endpoint (default: `/health`)
- Return HTTP 200 for healthy status
- Standard HTTP error codes

## Monitoring

### Health Checks
The gateway continuously monitors all registered services:
- Health check interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3

### Metrics
Available metrics:
- Request count per service
- Response times
- Error rates
- Circuit breaker states
- Service health status

### Logging
Structured logging with:
- Request/response details
- Service health events
- Error tracking
- Performance metrics

## Development

### Project Structure
```
src/
├── core/           # Core configuration and models
├── registry/       # Service discovery and registry
├── routing/        # Request routing and load balancing
├── middleware/     # Rate limiting and circuit breaker
├── health/         # Health monitoring
└── main.py         # Main application

tests/              # Test suite
config/             # Configuration files
docs/               # Documentation
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_gateway.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Production Deployment

### Docker Compose

```yaml
version: '3.8'
services:
  gateway:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GATEWAY_REDIS_URL=redis://redis:6379
      - GATEWAY_ENVIRONMENT=production
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: gateway
        image: mantrapath-gateway:latest
        ports:
        - containerPort: 8000
        env:
        - name: GATEWAY_REDIS_URL
          value: "redis://redis-service:6379"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
```

## Security

- JWT token validation
- Rate limiting per user/IP
- CORS configuration
- Request/response header filtering
- Service-to-service authentication

## Performance

- Async/await throughout
- Connection pooling
- Response caching
- Circuit breaker protection
- Load balancing

## Troubleshooting

### Common Issues

1. **Service Unavailable (503)**
   - Check if backend services are running
   - Verify service URLs in configuration
   - Check service health endpoints

2. **Rate Limit Exceeded (429)**
   - Increase rate limits in configuration
   - Check Redis connectivity
   - Verify client identification

3. **Circuit Breaker Open**
   - Check backend service health
   - Review failure thresholds
   - Monitor service recovery

### Debug Mode

Enable debug logging:
```env
GATEWAY_DEBUG=true
GATEWAY_LOG_LEVEL=DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
