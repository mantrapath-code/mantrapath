# MantraPath Project Walkthrough

## 🎯 Project Overview

MantraPath is a comprehensive mental health platform built with a microservices architecture. This walkthrough will guide you through the project structure, key components, and how to get started with development.

## 📁 Project Structure

```
mantrapath/
├── backend/                    # Backend services
│   ├── services/              # Microservices
│   │   ├── api_gateway/       # Central API gateway
│   │   ├── auth_service/      # Authentication service
│   │   ├── mood_service/      # Mood tracking service
│   │   ├── ai_event_processor/ # AI processing service
│   │   ├── ai_context_store/  # AI context management
│   │   ├── models_service/    # Centralized AI models
│   │   ├── chatbot_service/   # Conversational AI
│   │   ├── voice_service/     # Voice processing
│   │   ├── translation_service/ # Multi-language support
│   │   ├── community_service/ # Social features
│   │   ├── notification_service/ # Push notifications
│   │   ├── content_service/   # Content management
│   │   ├── memory_service/    # User behavior tracking
│   │   ├── ml_service/        # Machine learning
│   │   └── ...               # Other services
│   ├── shared/               # Shared utilities
│   │   ├── database.py       # Database connection
│   │   ├── auth.py          # Authentication utilities
│   │   ├── events/          # Event definitions
│   │   └── models.py        # Shared data models
│   ├── config/              # Configuration files
│   └── docker-compose.yml   # Local development setup
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   └── package.json
├── project-doc/             # Project documentation
│   ├── architecture/        # Architecture docs
│   ├── design/             # Design docs
│   ├── system/             # System design
│   ├── walkthrough/        # This file
│   └── workflows/          # User workflows
└── README.md               # Main project README
```

## 🚀 Getting Started

### **Prerequisites**

1. **Python 3.11+**
2. **Node.js 18+**
3. **Docker & Docker Compose**
4. **PostgreSQL 14+**
5. **Redis 6+**
6. **NATS JetStream**

### **Quick Start**

1. **Clone the repository**
   ```bash
   git clone https://github.com/mantrapath/mantrapath.git
   cd mantrapath
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start infrastructure services**
   ```bash
   docker-compose up -d postgres redis nats
   ```

4. **Install Python dependencies**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. **Run database migrations**
   ```bash
   python -m alembic upgrade head
   ```

6. **Start the services**
   ```bash
   # Start all services
   docker-compose up -d
   
   # Or start individual services
   python -m uvicorn services.auth_service.main:app --port 8001
   python -m uvicorn services.mood_service.main:app --port 8003
   python -m uvicorn services.ai_event_processor.main:app --port 8014
   ```

7. **Start the frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 🔧 Development Workflow

### **1. Service Development**

#### **Creating a New Service**

1. **Create service directory**
   ```bash
   mkdir backend/services/my_new_service
   cd backend/services/my_new_service
   ```

2. **Create basic structure**
   ```bash
   touch main.py
   touch requirements.txt
   touch README.md
   mkdir api models services tests
   ```

3. **Implement the service**
   ```python
   # main.py
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware
   
   app = FastAPI(title="My New Service")
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   
   @app.get("/health")
   async def health_check():
       return {"status": "healthy", "service": "my_new_service"}
   
   if __name__ == "__main__":
       import uvicorn
       uvicorn.run(app, host="0.0.0.0", port=8000)
   ```

4. **Add to docker-compose.yml**
   ```yaml
   my_new_service:
     build: ./services/my_new_service
     ports:
       - "8000:8000"
     environment:
       - DATABASE_URL=postgresql://user:pass@postgres:5432/mantrapath
       - REDIS_URL=redis://redis:6379/0
     depends_on:
       - postgres
       - redis
   ```

#### **Service Communication Patterns**

**Synchronous Communication (HTTP)**
```python
import httpx

class ServiceClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def call_service(self, endpoint: str, data: dict):
        response = await self.client.post(
            f"{self.base_url}{endpoint}",
            json=data,
            timeout=30.0
        )
        return response.json()
```

**Asynchronous Communication (Events)**
```python
from shared.events import get_enhanced_event_bus

class EventPublisher:
    def __init__(self):
        self.event_bus = get_enhanced_event_bus()
    
    async def publish_event(self, event_type: str, data: dict, user_id: str = None):
        await self.event_bus.publish(event_type, data, user_id)
```

### **2. Database Development**

#### **Creating New Models**
```python
# shared/models.py
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class MyNewModel(Base):
    __tablename__ = "my_new_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### **Creating Migrations**
```bash
# Create a new migration
alembic revision --autogenerate -m "Add my_new_model table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### **3. API Development**

#### **Creating API Endpoints**
```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.database import get_db
from shared.auth import get_current_user
from models.my_models import MyModel, MyModelCreate, MyModelResponse

@app.post("/api/v1/my-models", response_model=MyModelResponse)
async def create_my_model(
    model_data: MyModelCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Create new model instance
    db_model = MyModel(
        name=model_data.name,
        description=model_data.description,
        data=model_data.data,
        user_id=current_user["user_id"]
    )
    
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    return MyModelResponse.from_orm(db_model)

@app.get("/api/v1/my-models", response_model=List[MyModelResponse])
async def get_my_models(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    models = db.query(MyModel).filter(
        MyModel.user_id == current_user["user_id"]
    ).offset(skip).limit(limit).all()
    
    return [MyModelResponse.from_orm(model) for model in models]
```

### **4. Testing**

#### **Unit Testing**
```python
# tests/test_my_service.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_my_model():
    model_data = {
        "name": "Test Model",
        "description": "Test Description",
        "data": {"key": "value"}
    }
    
    response = client.post("/api/v1/my-models", json=model_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Model"
```

#### **Integration Testing**
```python
# tests/test_integration.py
import pytest
import asyncio
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_service_integration():
    async with AsyncClient() as client:
        # Test service communication
        response = await client.post(
            "http://localhost:8000/api/v1/process",
            json={"data": "test"}
        )
        assert response.status_code == 200
```

## 🔍 Key Components Deep Dive

### **1. API Gateway**

The API Gateway is the central entry point for all client requests. It handles:

- **Authentication & Authorization**: JWT token validation
- **Request Routing**: Routes requests to appropriate services
- **Rate Limiting**: Prevents abuse and DoS attacks
- **CORS**: Cross-origin resource sharing
- **Load Balancing**: Distributes load across service instances

**Key Files:**
- `backend/services/api_gateway/src/main.py` - Main application
- `backend/services/api_gateway/src/routing/` - Request routing logic
- `backend/services/api_gateway/src/middleware/` - Middleware components

### **2. Authentication Service**

Handles user registration, login, and token management.

**Key Features:**
- User registration with email verification
- JWT token generation and validation
- Password strength validation
- Account cleanup for unverified users

**Key Files:**
- `backend/services/auth_service/main.py` - Main application
- `backend/shared/auth.py` - Authentication utilities

### **3. Mood Service**

Core service for mood tracking and analytics.

**Key Features:**
- Daily mood entry collection
- Mood pattern analysis
- Emotional weather forecasting
- Celebration moment detection

**Key Files:**
- `backend/services/mood_service/main.py` - Main application
- `backend/services/mood_service/analytics.py` - Analytics engine
- `backend/services/mood_service/emotional_weather.py` - Weather forecasting

### **4. AI Event Processor**

Real-time AI analysis of all platform events.

**Key Features:**
- Multi-language emotion analysis
- Cultural intelligence processing
- Predictive intervention recommendations
- Real-time event processing

**Key Files:**
- `backend/services/ai_event_processor/main.py` - Main application
- `backend/services/ai_event_processor/core/ai_processor.py` - Core processor
- `backend/services/ai_event_processor/core/emotion_analyzer.py` - Emotion analysis

### **5. Models Service**

Centralized AI model management and inference.

**Key Features:**
- STT (Speech-to-Text) models
- TTS (Text-to-Speech) models
- NLP models for emotion analysis
- Translation models

**Key Files:**
- `backend/services/models_service/main.py` - Main application
- `backend/services/models_service/models/` - Model implementations
- `backend/services/models_service/api/` - API endpoints

## 🔧 Configuration Management

### **Environment Variables**

Each service uses environment variables for configuration:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mantrapath

# Redis
REDIS_URL=redis://localhost:6379/0

# NATS
NATS_URL=nats://localhost:4222

# Service URLs
AUTH_SERVICE_URL=http://localhost:8001
MOOD_SERVICE_URL=http://localhost:8003
AI_EVENT_PROCESSOR_URL=http://localhost:8014

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# AI Models
MODELS_SERVICE_URL=http://localhost:8080
USE_MODELS_SERVICE=true

# Feature Flags
USE_EVENT_BUS=true
USE_AI_PROCESSING=true
```

### **Docker Configuration**

Services are containerized using Docker:

```dockerfile
# Example Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🧪 Testing Strategy

### **1. Unit Tests**

Each service has comprehensive unit tests:

```bash
# Run unit tests for a specific service
cd backend/services/mood_service
python -m pytest tests/ -v

# Run all unit tests
cd backend
python -m pytest services/*/tests/ -v
```

### **2. Integration Tests**

Test service interactions:

```bash
# Run integration tests
cd backend
python -m pytest tests/integration/ -v
```

### **3. End-to-End Tests**

Test complete user workflows:

```bash
# Run E2E tests
cd backend
python -m pytest tests/e2e/ -v
```

## 📊 Monitoring and Debugging

### **1. Health Checks**

Each service provides health check endpoints:

```bash
# Check service health
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8003/health
```

### **2. Logging**

Structured logging across all services:

```python
import structlog

logger = structlog.get_logger(__name__)

logger.info(
    "Processing request",
    user_id=user_id,
    endpoint=endpoint,
    method=method
)
```

### **3. Metrics**

Prometheus metrics for monitoring:

```python
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
```

## 🚀 Deployment

### **1. Local Development**

```bash
# Start all services locally
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### **2. Production Deployment**

```bash
# Build production images
docker build -t mantrapath/api-gateway:latest ./api-gateway

# Deploy to Kubernetes
kubectl apply -f k8s/

# Check deployment status
kubectl get pods
kubectl get services
```

## 🔧 Troubleshooting

### **Common Issues**

1. **Service won't start**
   - Check environment variables
   - Verify database connection
   - Check port conflicts

2. **Database connection errors**
   - Verify PostgreSQL is running
   - Check connection string
   - Run migrations

3. **Redis connection errors**
   - Verify Redis is running
   - Check Redis URL
   - Verify Redis configuration

4. **NATS connection errors**
   - Verify NATS is running
   - Check NATS URL
   - Verify JetStream is enabled

### **Debug Commands**

```bash
# Check service logs
docker-compose logs service_name

# Check database connection
psql $DATABASE_URL -c "SELECT 1"

# Check Redis connection
redis-cli -u $REDIS_URL ping

# Check NATS connection
nats server info
```

## 📚 Additional Resources

### **Documentation**
- [Service Architecture](architecture/service-architecture.md)
- [High-Level Design](design/high-level-design.md)
- [Low-Level Design](design/low-level-design.md)
- [System Design](system/system-design.md)

### **API Documentation**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### **Development Tools**
- Database Admin: `http://localhost:8080` (pgAdmin)
- Redis Admin: `http://localhost:8081` (RedisInsight)
- NATS Monitoring: `http://localhost:8222`

This walkthrough provides a comprehensive guide to understanding and working with the MantraPath project. For more specific information, refer to the individual service documentation and the detailed architecture documents.
