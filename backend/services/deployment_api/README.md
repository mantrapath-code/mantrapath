# MantraPath Deployment API Service

> 🚀 **Controlled API access service for frontend engineers with model training status, service health, and API documentation**

## 🎯 Purpose

The Deployment API Service provides frontend engineers with controlled access to:
- **API Documentation & Endpoints** - Complete API reference without backend code access
- **Model Training Status** - Real-time updates on AI model training progress
- **Service Health Monitoring** - Service availability and performance metrics
- **API Testing Tools** - Interactive API testing and validation
- **Rate Limiting & Quotas** - Controlled access with usage monitoring

## 🏗️ Architecture

### Service Components
```
deployment_api/
├── src/
│   ├── main.py                 # FastAPI application
│   ├── routes/
│   │   ├── api_docs.py        # API documentation endpoints
│   │   ├── model_status.py    # Model training status
│   │   ├── service_health.py  # Service health monitoring
│   │   ├── api_testing.py     # Interactive API testing
│   │   └── usage_metrics.py   # Usage tracking and quotas
│   ├── models/
│   │   ├── api_docs.py        # API documentation models
│   │   ├── model_status.py    # Model training models
│   │   └── service_health.py  # Health check models
│   ├── services/
│   │   ├── api_documentation.py # API documentation generator
│   │   ├── model_monitor.py   # Model training monitoring
│   │   ├── health_checker.py  # Service health checking
│   │   └── usage_tracker.py   # Usage tracking and quotas
│   └── utils/
│       ├── auth.py            # Frontend engineer authentication
│       ├── rate_limiting.py   # Rate limiting for frontend access
│       └── documentation.py   # Documentation generation utilities
├── config/
│   ├── settings.py            # Service configuration
│   └── permissions.py         # Access control configuration
├── tests/                     # Test suite
├── Dockerfile                 # Container configuration
└── requirements.txt           # Python dependencies
```

## 🔐 Access Control

### Frontend Engineer Permissions
- **Read-only access** to API documentation
- **View-only access** to model training status
- **Limited API testing** with rate limiting
- **No access** to backend source code or databases
- **Usage quotas** to prevent abuse

### Authentication Levels
1. **Basic Access** - API documentation and service health
2. **Enhanced Access** - Model training status and API testing
3. **Premium Access** - Advanced features and higher rate limits

## 📚 API Documentation Features

### Interactive Documentation
- **OpenAPI/Swagger UI** - Complete API reference
- **Endpoint Examples** - Request/response examples
- **Authentication Guide** - How to use the APIs
- **Error Handling** - Common error codes and solutions
- **Rate Limiting Info** - Usage limits and quotas

### Service-Specific Documentation
- **Voice Service APIs** - STT/TTS endpoints
- **Community Service APIs** - Social features
- **ML Service APIs** - AI model endpoints
- **Auth Service APIs** - Authentication flows

## 🤖 Model Training Status

### Real-time Updates
- **Training Progress** - Current model training status
- **Model Performance** - Accuracy and performance metrics
- **Deployment Status** - Model deployment pipeline
- **Resource Usage** - GPU/CPU utilization during training
- **Estimated Completion** - Training time estimates

### Model Categories
- **Speech Recognition** - STT model training status
- **Text-to-Speech** - TTS model training status
- **Language Models** - NLP model training status
- **Cultural Models** - Regional adaptation models

## 📊 Service Health Monitoring

### Health Metrics
- **Service Status** - Up/down status of all services
- **Response Times** - API response time metrics
- **Error Rates** - Error percentage and trends
- **Resource Usage** - CPU, memory, and disk usage
- **Dependencies** - Database, Redis, NATS status

### Alerts & Notifications
- **Service Down** - Immediate notification of service failures
- **Performance Degradation** - Slow response time alerts
- **Resource Issues** - High resource usage warnings
- **Model Training Issues** - Training failure notifications

## 🧪 API Testing Tools

### Interactive Testing
- **Endpoint Testing** - Test individual API endpoints
- **Authentication Testing** - Test auth flows and tokens
- **Rate Limit Testing** - Test rate limiting behavior
- **Error Testing** - Test error handling scenarios
- **Performance Testing** - Test response times

### Test Data Management
- **Sample Data** - Pre-configured test data
- **Mock Responses** - Simulated API responses
- **Test Scenarios** - Common testing scenarios
- **Result Validation** - Expected vs actual results

## 📈 Usage Metrics & Quotas

### Usage Tracking
- **API Calls** - Number of API calls per engineer
- **Data Transfer** - Amount of data transferred
- **Error Rates** - Error percentage per engineer
- **Response Times** - Average response times
- **Resource Usage** - Resource consumption metrics

### Rate Limiting
- **Per-Endpoint Limits** - Different limits for different APIs
- **Per-Engineer Limits** - Individual usage quotas
- **Time-based Limits** - Hourly, daily, monthly limits
- **Burst Limits** - Temporary higher rate allowances

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Access to MantraPath backend services
- Redis for caching and rate limiting
- PostgreSQL for usage tracking

### Installation
```bash
cd backend/services/deployment_api
pip install -r requirements.txt
```

### Configuration
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Running the Service
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8086 --reload
```

## 🔧 Configuration

### Environment Variables
```bash
# Service Configuration
DEPLOYMENT_API_PORT=8086
DEPLOYMENT_API_HOST=0.0.0.0
ENVIRONMENT=development

# Authentication
FRONTEND_ENGINEER_SECRET=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256

# Rate Limiting
RATE_LIMIT_ENABLED=true
DEFAULT_RATE_LIMIT=1000  # requests per minute
FRONTEND_ENGINEER_LIMIT=500  # requests per minute

# Service Discovery
API_GATEWAY_URL=http://localhost:8000
VOICE_SERVICE_URL=http://localhost:8011
MODELS_SERVICE_URL=http://localhost:8085
```

### Access Control Configuration
```python
# config/permissions.py
FRONTEND_ENGINEER_PERMISSIONS = {
    "basic": {
        "api_docs": "read",
        "service_health": "read",
        "model_status": "read",
        "api_testing": "limited",
        "rate_limit": 100  # requests per minute
    },
    "enhanced": {
        "api_docs": "read",
        "service_health": "read",
        "model_status": "read",
        "api_testing": "full",
        "rate_limit": 500  # requests per minute
    },
    "premium": {
        "api_docs": "read",
        "service_health": "read",
        "model_status": "read",
        "api_testing": "full",
        "advanced_features": "read",
        "rate_limit": 1000  # requests per minute
    }
}
```

## 📱 Frontend Integration

### API Documentation Access
```typescript
// Frontend code to access API documentation
const getApiDocs = async () => {
  const response = await fetch('/api/deployment/docs', {
    headers: {
      'Authorization': `Bearer ${frontendEngineerToken}`,
      'Content-Type': 'application/json'
    }
  });
  return response.json();
};
```

### Model Training Status
```typescript
// Frontend code to get model training status
const getModelStatus = async () => {
  const response = await fetch('/api/deployment/models/status', {
    headers: {
      'Authorization': `Bearer ${frontendEngineerToken}`,
      'Content-Type': 'application/json'
    }
  });
  return response.json();
};
```

### Service Health Check
```typescript
// Frontend code to check service health
const getServiceHealth = async () => {
  const response = await fetch('/api/deployment/health', {
    headers: {
      'Authorization': `Bearer ${frontendEngineerToken}`,
      'Content-Type': 'application/json'
    }
  });
  return response.json();
};
```

## 🔒 Security Features

### Access Control
- **JWT Authentication** - Secure token-based authentication
- **Role-based Access** - Different permission levels
- **Rate Limiting** - Prevent abuse and ensure fair usage
- **Request Validation** - Validate all incoming requests
- **Audit Logging** - Track all access and usage

### Data Protection
- **No Sensitive Data** - Only public API information
- **Encrypted Communication** - HTTPS/TLS encryption
- **Input Validation** - Prevent injection attacks
- **Output Sanitization** - Clean all responses
- **Privacy Compliance** - GDPR and privacy compliance

## 📊 Monitoring & Analytics

### Performance Metrics
- **Response Times** - API response time tracking
- **Throughput** - Requests per second
- **Error Rates** - Error percentage tracking
- **Resource Usage** - CPU, memory, disk usage
- **User Activity** - Frontend engineer usage patterns

### Business Intelligence
- **API Popularity** - Most used endpoints
- **Usage Patterns** - Peak usage times
- **Feature Adoption** - Most used features
- **User Engagement** - Engineer activity levels
- **Service Dependencies** - Most critical services

## 🚀 Future Enhancements

### Planned Features
- **Real-time Notifications** - WebSocket-based updates
- **Advanced Analytics** - Machine learning insights
- **Custom Dashboards** - Personalized views
- **API Versioning** - Multiple API versions support
- **Integration Testing** - Automated API testing
- **Performance Optimization** - Caching and optimization

### Scalability Plans
- **Horizontal Scaling** - Multiple service instances
- **Load Balancing** - Distribute traffic across instances
- **Caching Strategy** - Redis and CDN integration
- **Database Optimization** - Query optimization and indexing
- **Microservice Architecture** - Service decomposition

## 🤝 Contributing

### Development Guidelines
- Follow PEP 8 coding standards
- Write comprehensive tests
- Document all new features
- Use type hints throughout
- Follow security best practices

### Testing
```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_api_docs.py
```

## 📄 License

This service is part of the MantraPath project and follows the same licensing terms.

## 🆘 Support

For support and questions:
- **Documentation** - Check this README and API docs
- **Issues** - Report bugs and feature requests
- **Discussions** - Join community discussions
- **Email** - Contact the development team
