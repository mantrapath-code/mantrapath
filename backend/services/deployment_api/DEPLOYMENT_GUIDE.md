# MantraPath Deployment API Service - Deployment Guide

## 🎯 Overview

The Deployment API Service provides frontend engineers with controlled access to:
- **API Documentation** - Complete API reference without backend code access
- **Model Training Status** - Real-time updates on AI model training progress
- **Service Health Monitoring** - Service availability and performance metrics
- **API Testing Tools** - Interactive API testing and validation
- **Usage Metrics & Quotas** - Controlled access with usage monitoring

## 🏗️ Architecture

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
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Docker & Docker Compose** (for containerized deployment)
- **Access to MantraPath backend services**

### Option 1: Local Development

1. **Clone and navigate to the service**
   ```bash
   cd backend/services/deployment_api
   ```

2. **Make startup script executable**
   ```bash
   chmod +x start.sh
   ```

3. **Run the startup script**
   ```bash
   ./start.sh
   ```

4. **Access the service**
   - **API Documentation**: http://localhost:8086/docs
   - **Health Check**: http://localhost:8086/health
   - **Service Root**: http://localhost:8086/

### Option 2: Docker Deployment

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Start the deployment API service**
   ```bash
   docker-compose -f docker-compose.deployment.yml up -d
   ```

3. **Check service status**
   ```bash
   docker-compose -f docker-compose.deployment.yml ps
   ```

4. **View logs**
   ```bash
   docker-compose -f docker-compose.deployment.yml logs -f deployment-api
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `deployment_api` directory:

```bash
# Service Configuration
DEPLOYMENT_API_PORT=8086
DEPLOYMENT_API_HOST=0.0.0.0
ENVIRONMENT=development
DEBUG=true

# Authentication
FRONTEND_ENGINEER_SECRET=your-super-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Rate Limiting
RATE_LIMIT_ENABLED=true
DEFAULT_RATE_LIMIT=1000
FRONTEND_ENGINEER_LIMIT=500

# Service Discovery
API_GATEWAY_URL=http://localhost:8000
VOICE_SERVICE_URL=http://localhost:8011
MODELS_SERVICE_URL=http://localhost:8085
COMMUNITY_SERVICE_URL=http://localhost:8012
ML_SERVICE_URL=http://localhost:8013

# Redis Configuration
REDIS_URL=redis://localhost:6380
REDIS_DB=0

# Database Configuration
DATABASE_URL=postgresql://deployment_user:deployment_password@localhost:5433/mantrapath_deployment
```

### Permission Levels

The service supports three permission levels:

1. **Basic Access** (100 requests/minute)
   - API documentation
   - Service health monitoring
   - Model training status
   - Limited API testing

2. **Enhanced Access** (500 requests/minute)
   - All basic features
   - Full API testing
   - Usage metrics

3. **Premium Access** (1000 requests/minute)
   - All enhanced features
   - Advanced analytics
   - Custom dashboards
   - Priority support

## 🔐 Authentication

### Frontend Engineer Setup

1. **Get JWT Token**
   ```bash
   # Contact admin to get your engineer ID and token
   curl -X POST "http://localhost:8086/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"engineer_id": "fe_001", "password": "your_password"}'
   ```

2. **Use Token in Requests**
   ```bash
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     "http://localhost:8086/api/docs"
   ```

### Admin Operations

1. **Add New Engineer**
   ```bash
   # This would typically be done through admin interface
   # For now, manually add to the auth service
   ```

2. **Update Permissions**
   ```bash
   # Update permission level for an engineer
   ```

## 📚 API Endpoints

### Core Endpoints

| Endpoint | Method | Description | Permission Required |
|-----------|--------|-------------|-------------------|
| `/` | GET | Service information | None |
| `/health` | GET | Service health check | None |
| `/docs` | GET | Interactive API docs | None |

### Protected Endpoints

| Endpoint | Method | Description | Permission Required |
|-----------|--------|-------------|-------------------|
| `/api/docs` | GET | Complete API documentation | Basic |
| `/api/docs/{service}` | GET | Service-specific docs | Basic |
| `/api/models/status` | GET | Model training status | Basic |
| `/api/models/status/{type}` | GET | Model type status | Basic |
| `/api/health/services` | GET | All services health | Basic |
| `/api/health/services/{service}` | GET | Service health | Basic |
| `/api/testing/test-endpoint` | POST | Test API endpoints | Enhanced |
| `/api/usage/metrics` | GET | Usage metrics | Enhanced |

## 🧪 Testing the Service

### 1. Health Check
```bash
curl http://localhost:8086/health
```

### 2. Get API Documentation
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8086/api/docs"
```

### 3. Check Model Training Status
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8086/api/models/status"
```

### 4. Test API Endpoint
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"service": "voice_service", "endpoint": "/api/voice/stt"}' \
  "http://localhost:8086/api/testing/test-endpoint"
```

## 📊 Monitoring & Analytics

### Service Health
- **Health Check**: `/health` endpoint
- **Service Status**: Real-time monitoring of all backend services
- **Performance Metrics**: Response times, error rates, throughput

### Usage Analytics
- **Per-Engineer Metrics**: API call counts, success rates
- **Endpoint Usage**: Most used APIs, usage patterns
- **Rate Limiting**: Quota enforcement and monitoring

### Model Training Status
- **Training Progress**: Real-time updates on AI model training
- **Resource Usage**: GPU, memory, and disk utilization
- **Deployment Status**: Model deployment pipeline status

## 🔒 Security Features

### Access Control
- **JWT Authentication**: Secure token-based authentication
- **Role-based Permissions**: Different access levels for engineers
- **Rate Limiting**: Prevent abuse and ensure fair usage
- **Request Validation**: Validate all incoming requests

### Data Protection
- **No Sensitive Data**: Only public API information
- **Encrypted Communication**: HTTPS/TLS encryption
- **Input Validation**: Prevent injection attacks
- **Audit Logging**: Track all access and usage

## 🚀 Production Deployment

### 1. Environment Setup
```bash
# Set production environment
export ENVIRONMENT=production
export DEBUG=false
export LOG_LEVEL=WARNING

# Update secrets
export FRONTEND_ENGINEER_SECRET=your-production-secret
export JWT_SECRET_KEY=your-production-jwt-secret
```

### 2. Docker Production
```bash
# Build production image
docker build -t mantrapath/deployment-api:latest .

# Run with production config
docker run -d \
  --name deployment-api-prod \
  -p 8086:8086 \
  -e ENVIRONMENT=production \
  -e DEBUG=false \
  mantrapath/deployment-api:latest
```

### 3. Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deployment-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: deployment-api
  template:
    metadata:
      labels:
        app: deployment-api
    spec:
      containers:
      - name: deployment-api
        image: mantrapath/deployment-api:latest
        ports:
        - containerPort: 8086
        env:
        - name: ENVIRONMENT
          value: "production"
```

## 🔍 Troubleshooting

### Common Issues

1. **Service Won't Start**
   ```bash
   # Check Python version
   python3 --version
   
   # Check dependencies
   pip list
   
   # Check logs
   tail -f logs/deployment_api.log
   ```

2. **Authentication Errors**
   ```bash
   # Verify JWT token
   # Check token expiration
   # Verify engineer permissions
   ```

3. **Rate Limiting Issues**
   ```bash
   # Check current usage
   # Verify permission level
   # Check rate limit configuration
   ```

4. **Service Health Issues**
   ```bash
   # Check backend service availability
   # Verify network connectivity
   # Check service configuration
   ```

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

## 📈 Scaling & Performance

### Horizontal Scaling
- **Load Balancer**: Distribute traffic across multiple instances
- **Auto-scaling**: Scale based on CPU/memory usage
- **Health Checks**: Ensure only healthy instances receive traffic

### Performance Optimization
- **Caching**: Redis-based caching for frequently accessed data
- **Connection Pooling**: Efficient database and service connections
- **Async Processing**: Non-blocking I/O operations

### Monitoring
- **Metrics Collection**: Prometheus metrics
- **Logging**: Structured logging with ELK stack
- **Alerting**: Proactive monitoring and alerting

## 🔄 Updates & Maintenance

### Service Updates
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.deployment.yml down
docker-compose -f docker-compose.deployment.yml up -d --build
```

### Database Migrations
```bash
# Run database migrations
# Update schema if needed
```

### Configuration Updates
```bash
# Update environment variables
# Restart service to apply changes
```

## 📞 Support & Documentation

### Resources
- **API Documentation**: http://localhost:8086/docs
- **Service Health**: http://localhost:8086/health
- **GitHub Repository**: [MantraPath Backend](https://github.com/ssharmasachin/mantrapath)

### Contact
- **Development Team**: Contact the backend development team
- **Issues**: Report bugs and feature requests through GitHub
- **Documentation**: Check this guide and API docs first

## 🎯 Next Steps

1. **Deploy the service** using one of the methods above
2. **Configure authentication** for your frontend engineers
3. **Set up monitoring** and alerting
4. **Train your team** on using the deployment API
5. **Monitor usage** and adjust permissions as needed
6. **Scale the service** based on demand

---

**Happy Deploying! 🚀**

The Deployment API Service will provide your frontend engineers with the tools they need to build amazing user experiences while maintaining security and control over your backend infrastructure.

