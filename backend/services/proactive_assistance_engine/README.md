# Proactive Assistance Engine

**Service Status**: IMPLEMENTED - V3-BK-008  
**Port**: 8018  
**Sprint**: Sprint 2 - Cross-Service Intelligence  

## Overview

The Proactive Assistance Engine is a sophisticated orchestration service that coordinates existing AI capabilities into a cohesive proactive assistance system. It provides timely, contextually relevant, and culturally sensitive assistance by analyzing user behavior patterns, predicting optimal intervention timing, and delivering personalized support.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Proactive Assistance Engine                 │
│                           (8018)                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Orchestrator                       │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐ │
│  │ Timing Predictor│ │Contextual Help  │ │  Cultural    │ │
│  │                 │ │    Engine       │ │ Sensitivity  │ │
│  └─────────────────┘ └─────────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Integrations                     │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐ │
│  │AI Event Processor│ │ AI Context Store│ │  Cultural    │ │
│  │     (8014)      │ │     (8013)      │ │Intelligence  │ │
│  └─────────────────┘ └─────────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. **Intelligent Timing Prediction**
- Analyzes user activity patterns and recent assistance history
- Considers cultural timing preferences and optimal intervention windows
- Implements urgency override for critical situations

### 2. **Contextual Help Matching**
- Matches assistance content to specific user needs
- Prioritizes suggestions based on relevance and impact
- Maintains a dynamic help content database

### 3. **Cultural Sensitivity**
- Evaluates content appropriateness for different cultural contexts
- Adapts assistance delivery timing and content
- Respects cultural guidelines and preferences

### 4. **Service Integration**
- Seamlessly integrates with AI Event Processor for intervention analysis
- Leverages AI Context Store for comprehensive user intelligence
- Utilizes Cultural Intelligence for adaptation and sensitivity

## API Endpoints

### Health & Status
- `GET /health` - Service health check
- `GET /health/live` - Kubernetes liveness probe
- `GET /health/ready` - Kubernetes readiness probe

### Core Assistance
- `POST /api/v1/assistance/evaluate/{user_id}` - Evaluate assistance needs
- `GET /api/v1/assistance/status/{user_id}` - Get current assistance status
- `POST /api/v1/assistance/trigger/{user_id}` - Manually trigger assistance

### System Information
- `GET /api/v1/integrations/status` - Check integrated services status
- `GET /api/v1/metrics` - Get performance metrics

## Configuration

The service is configured via environment variables and the `config/assistance.yaml` file:

### Environment Variables
```bash
# Service Configuration
PROACTIVE_ASSISTANCE_HOST=0.0.0.0
PROACTIVE_ASSISTANCE_PORT=8018

# Service Integration URLs
AI_EVENT_PROCESSOR_URL=http://ai-event-processor:8014
AI_CONTEXT_STORE_URL=http://ai-context-store:8013
CULTURAL_INTELLIGENCE_URL=http://cultural-intelligence:8017

# Performance Configuration
MAX_CONCURRENT_EVALUATIONS=50
EVALUATION_TIMEOUT=30
ASSISTANCE_CACHE_TTL=1800

# Cultural Configuration
CULTURAL_ADAPTATION_ENABLED=true
CULTURAL_FALLBACK_ENABLED=true
DEFAULT_CULTURE=neutral
```

### Configuration File
The `config/assistance.yaml` file contains detailed configuration for:
- Evaluation thresholds and parameters
- Timing preferences and constraints
- Cultural guidelines and adaptation rules
- Help content categories and matching rules
- Performance monitoring settings

## Service Dependencies

### Required Services
- **PostgreSQL** - User data and assistance history
- **Redis** - Caching and real-time features
- **NATS** - Event streaming and messaging
- **AI Event Processor** - Intervention analysis and predictions
- **AI Context Store** - User context and intelligence insights

### Optional Services
- **Cultural Intelligence** - Cultural adaptation and sensitivity (if available)

## Event Integration

### Subscribed Events
- User behavior changes
- Crisis detection alerts
- Mood fluctuations
- Activity pattern updates

### Published Events
- Assistance recommendations
- Intervention triggers
- Cultural adaptation requests
- Performance metrics

## Performance Metrics

The service tracks comprehensive metrics including:
- Successful evaluations per minute
- Average response time
- Cultural adaptation success rate
- Service integration health
- Error rates and types

## Testing

### Test Coverage
- **Unit Tests**: 80%+ coverage for all functions
- **Integration Tests**: Service integration validation
- **Performance Tests**: Load and stress testing

### Running Tests
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/test_assistance_orchestrator.py
pytest tests/test_timing_predictor.py
pytest tests/test_contextual_help_engine.py
pytest tests/test_cultural_sensitivity_engine.py
```

## Development

### Local Setup
```bash
# Clone the repository
cd backend/services/proactive_assistance_engine

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export PROACTIVE_ASSISTANCE_PORT=8018
export DATABASE_URL=postgresql://user:pass@localhost:5432/mantrapath
export REDIS_URL=redis://localhost:6379

# Run the service
python main.py
```

### Docker Development
```bash
# Build the service
docker build -t proactive-assistance-engine .

# Run with dependencies
docker-compose up proactive-assistance-engine

# View logs
docker-compose logs -f proactive-assistance-engine
```

## Monitoring & Observability

### Health Checks
- Service availability monitoring
- Dependency health validation
- Performance threshold alerts

### Logging
- Structured logging with structlog
- Configurable log levels
- Performance and error tracking

### Metrics
- Prometheus-compatible metrics
- Custom business metrics
- Real-time performance monitoring

## Security Considerations

- JWT-based authentication
- Environment-based configuration
- Secure service-to-service communication
- Input validation and sanitization

## Deployment

### Docker Compose
The service is integrated into the main `docker-compose.yml` with:
- Proper dependency management
- Health check configuration
- Network isolation
- Volume management

### Production Considerations
- Environment-specific configuration
- Resource limits and requests
- Horizontal scaling support
- Backup and recovery procedures

## Troubleshooting

### Common Issues
1. **Service Dependencies**: Ensure all required services are healthy
2. **Configuration**: Verify environment variables and config files
3. **Network**: Check service-to-service connectivity
4. **Database**: Validate database connections and permissions

### Debug Mode
Enable debug logging by setting:
```bash
export LOG_LEVEL=debug
export ENVIRONMENT=development
```

## Contributing

When contributing to this service:
1. Follow the existing code structure and patterns
2. Maintain 80%+ test coverage
3. Update documentation for new features
4. Follow the established API design patterns
5. Ensure proper error handling and logging

## License

This service is part of the MantraPath V3 platform and follows the same licensing terms.

---

*This service successfully implements the V3-BK-008 Proactive Assistance Engine requirements, providing a robust foundation for intelligent, culturally-sensitive proactive assistance in MantraPath V3.*
