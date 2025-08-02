# 🚀 MantraPath ML Service - Production Deployment Guide

## Overview

This guide covers the production deployment of the **Phase 2A Crisis Prediction & Early Warning System** - a life-saving mental health intelligence platform with real-time monitoring capabilities.

## 📋 Pre-Deployment Checklist

### 🔒 Security & Authentication
- [ ] API authentication configured and tested
- [ ] Rate limiting implemented for crisis endpoints
- [ ] User data encryption at rest and in transit
- [ ] HIPAA compliance review completed
- [ ] Crisis hotline integration tested
- [ ] Healthcare provider integration permissions configured

### 🛡️ Data Privacy & Compliance
- [ ] User consent mechanisms implemented
- [ ] Data anonymization protocols active
- [ ] Crisis prediction logging complies with privacy regulations
- [ ] User data retention policies configured
- [ ] Emergency contact permissions verified

### 🔧 Infrastructure Requirements

#### **Minimum System Specifications**
- **CPU**: 4+ cores (crisis prediction is CPU-intensive)
- **RAM**: 8GB+ (ML models + Redis caching)
- **Storage**: 50GB+ SSD (model storage + metrics)
- **Network**: Low-latency connection (crisis response times critical)

#### **Dependencies**
```bash
# Core ML Dependencies
tensorflow>=2.13.0
scikit-learn>=1.3.0
prophet>=1.1.4
numpy>=1.24.0
pandas>=2.0.0

# API & Web Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.4.0

# Database & Caching
redis>=5.0.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0

# Monitoring & Dashboard
plotly>=5.17.0
dash>=2.14.0
dash-bootstrap-components>=1.5.0

# Security & Authentication
cryptography>=41.0.0
python-jose[cryptography]>=3.3.0
```

## 🚀 Deployment Steps

### **Step 1: Environment Configuration**

Create production environment file:
```bash
# /backend/services/ml_service/.env.production
NODE_ENV=production
ML_SERVICE_PORT=8008
ML_SERVICE_HOST=0.0.0.0

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/mantrapath_prod
REDIS_URL=redis://localhost:6379/0

# ML Model Configuration
ML_MODEL_PATH=/opt/mantrapath/models/
ML_TRAINING_DATA_PATH=/opt/mantrapath/data/
MODEL_UPDATE_INTERVAL_HOURS=24

# Crisis Prediction Settings
CRISIS_PREDICTION_ENABLED=true
CRISIS_THRESHOLD_HIGH=0.75
CRISIS_THRESHOLD_MEDIUM=0.45
CRISIS_THRESHOLD_LOW=0.25

# Emergency Response Configuration
CRISIS_HOTLINE_NUMBER=988
EMERGENCY_CONTACT_SERVICE_URL=https://api.mantrapath.com/emergency
HEALTHCARE_PROVIDER_API_URL=https://api.mantrapath.com/healthcare
ENABLE_HEALTHCARE_INTEGRATION=true

# Monitoring & Alerting
ENABLE_DASHBOARD=true
DASHBOARD_PORT=8050
METRICS_COLLECTION_INTERVAL=60
ALERT_WEBHOOK_URL=https://api.mantrapath.com/alerts

# Security Configuration
JWT_SECRET_KEY=your-production-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Performance Tuning
MAX_CONCURRENT_PREDICTIONS=10
MODEL_INFERENCE_TIMEOUT=30
REDIS_CONNECTION_POOL_SIZE=20
```

### **Step 2: Docker Production Configuration**

```dockerfile
# Dockerfile.production
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for ML libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for ML models and data
RUN mkdir -p /opt/mantrapath/models /opt/mantrapath/data

# Set environment variables
ENV PYTHONPATH=/app
ENV ML_MODEL_PATH=/opt/mantrapath/models/
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8008/health || exit 1

# Expose ports
EXPOSE 8008 8050

# Run application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8008", "--workers", "1"]
```

### **Step 3: Docker Compose Production Setup**

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  ml-service:
    build:
      context: .
      dockerfile: Dockerfile.production
    ports:
      - "8008:8008"
      - "8050:8050"
    environment:
      - NODE_ENV=production
    env_file:
      - .env.production
    volumes:
      - ./models:/opt/mantrapath/models
      - ./data:/opt/mantrapath/data
      - ./logs:/app/logs
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: "2"
        reservations:
          memory: 2G
          cpus: "1"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: mantrapath_prod
      POSTGRES_USER: mantrapath
      POSTGRES_PASSWORD: your-secure-password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl/certs:ro
    depends_on:
      - ml-service
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
```

### **Step 4: Nginx Load Balancer Configuration**

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream ml_service {
        server ml-service:8008;
    }

    upstream dashboard {
        server ml-service:8050;
    }

    # ML Service API
    server {
        listen 80;
        server_name api.mantrapath.com;

        location / {
            proxy_pass http://ml_service;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Crisis prediction endpoints need low timeout
            proxy_connect_timeout 5s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # Health check endpoint
        location /health {
            proxy_pass http://ml_service/health;
            access_log off;
        }
    }

    # Crisis Monitoring Dashboard
    server {
        listen 80;
        server_name dashboard.mantrapath.com;

        location / {
            proxy_pass http://dashboard;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support for real-time dashboard
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

## 📊 **Step 5: Production Monitoring & Alerting**

### **Monitoring Stack Setup**
```bash
# Install monitoring tools
pip install prometheus-client grafana-api datadog

# Configure metrics export endpoint
# Add to main.py:
from prometheus_client import Counter, Histogram, Gauge, generate_latest

CRISIS_PREDICTIONS_TOTAL = Counter('crisis_predictions_total', 'Total crisis predictions made')
CRISIS_PREDICTION_DURATION = Histogram('crisis_prediction_duration_seconds', 'Time spent on crisis predictions')
HIGH_RISK_ALERTS = Gauge('high_risk_alerts_active', 'Number of active high-risk alerts')
```

### **Critical Alerting Rules**
```yaml
# alerting-rules.yml
groups:
- name: crisis_prediction
  rules:
  - alert: HighRiskUserDetected
    expr: high_risk_alerts_active > 0
    for: 0s
    labels:
      severity: critical
    annotations:
      summary: "High risk user detected - immediate attention required"
      description: "Crisis prediction system has detected {{ $value }} high-risk users"

  - alert: MLServiceDown
    expr: up{job="ml-service"} == 0
    for: 30s
    labels:
      severity: critical
    annotations:
      summary: "ML Service is down - crisis prediction unavailable"

  - alert: HighPredictionLatency
    expr: crisis_prediction_duration_seconds > 5
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Crisis prediction response time too high"
```

## 🧪 **Step 6: Production Testing Protocol**

### **Pre-Production Testing Checklist**
- [ ] **Load Testing**: 1000+ concurrent users, crisis prediction under load
- [ ] **Stress Testing**: System behavior under resource constraints
- [ ] **Failover Testing**: Redis/DB connection loss scenarios
- [ ] **Security Testing**: Authentication, rate limiting, data protection
- [ ] **Integration Testing**: Notification service, emergency contacts
- [ ] **Dashboard Testing**: Real-time updates, metrics accuracy

### **Production Validation Commands**
```bash
# Health check
curl -f http://localhost:8008/health

# Crisis prediction test (with valid auth token)
curl -X POST http://localhost:8008/crisis/predict-risk \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user", "include_interventions": true}'

# Dashboard metrics test
curl -X GET http://localhost:8008/dashboard/metrics \
  -H "Authorization: Bearer $TOKEN"

# System metrics test
curl -X GET http://localhost:8008/crisis/system-metrics \
  -H "Authorization: Bearer $TOKEN"
```

## 🚨 **Step 7: Crisis Response Protocol**

### **Emergency Escalation Workflow**
1. **HIGH RISK DETECTED** → Immediate notification to support team
2. **System DOWN** → Activate backup crisis detection service
3. **ALERT FATIGUE** → Review threshold settings, false positive rate
4. **DATA BREACH** → Immediate isolation, security team notification

### **24/7 Monitoring Requirements**
- **Crisis prediction system uptime**: >99.9%
- **Alert response time**: <2 minutes
- **Dashboard availability**: >99.5%
- **Model accuracy**: >85% maintained

## 📈 **Success Metrics**

### **Phase 2A Production KPIs**
- **Early Detection Rate**: 85%+ of crises predicted 24-72h before
- **False Positive Rate**: <10%
- **System Response Time**: <2 seconds average
- **Intervention Success Rate**: >80%
- **User Satisfaction**: >4.5/5 with crisis support

### **System Performance Targets**
- **Prediction Throughput**: 1000+ predictions/hour
- **Dashboard Load Time**: <3 seconds
- **API Response Time**: 95th percentile <5 seconds
- **System Uptime**: 99.9%

## 🔄 **Continuous Deployment Pipeline**

### **Automated Deployment Steps**
1. **Code Review** → Security & performance review
2. **Automated Testing** → Full test suite + load testing
3. **Staging Deployment** → Production-like environment testing
4. **Model Validation** → ML model performance verification
5. **Canary Release** → 5% traffic to new version
6. **Full Production** → Complete rollout after validation
7. **Monitoring** → 24h enhanced monitoring post-deployment

---

## 🎯 **Next Steps for Production**

1. **Review and customize** environment configurations for your infrastructure
2. **Set up monitoring** and alerting systems
3. **Configure SSL certificates** for HTTPS endpoints
4. **Test emergency escalation** procedures
5. **Train support team** on crisis prediction dashboard
6. **Schedule go-live** with coordinated rollout plan

**⚠️ CRITICAL**: This system handles life-critical mental health predictions. Ensure thorough testing and have emergency procedures in place before production deployment.

---

*This production deployment enables the MantraPath platform to provide proactive, life-saving crisis prediction capabilities at scale.*
