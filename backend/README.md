# MantraPath Backend

This directory contains the FastAPI-based microservices backend for MantraPath.

## Architecture

The backend follows a microservices architecture with the following services:

- **API Gateway** (Port 8000) - Main entry point
- **Auth Service** (Port 8001) - Authentication & authorization
- **Profile Service** (Port 8002) - User profiles & preferences  
- **Mood Service** (Port 8003) - Mood tracking & analytics
- **Chatbot Service** (Port 8004) - AI chatbot functionality
- **Content Service** (Port 8005) - Content management
- **Community Service** (Port 8006) - Forums & community features
- **Notification Service** (Port 8007) - Notifications
- **Media Service** (Port 8009) - Media upload & management

## Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start all services:
```bash
python start_services.py
```

3. Access API documentation:
- API Gateway: http://localhost:8000/docs
- Individual services: http://localhost:{port}/docs

## Database

- PostgreSQL for persistent data
- Redis for caching and real-time features
- SQLAlchemy for ORM

## Real-time Features

- WebSocket support for live notifications
- Redis pub/sub for cross-service communication
- Event-driven architecture for data sync