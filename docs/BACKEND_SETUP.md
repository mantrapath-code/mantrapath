# MantraPath Backend Setup

## Quick Start (Development)

The frontend will work with mock data if the backend is not running. To enable full functionality:

### Option 1: Quick Development Setup
```bash
cd backend
chmod +x quick-start.sh
./quick-start.sh
```

This will:
- Install Python dependencies
- Start API Gateway (port 8000)
- Start Auth Service (port 8001) 
- Start Mood Service (port 8003)
- Use SQLite database for development

### Option 2: Full Docker Setup
```bash
cd backend
docker-compose up -d
```

This will start all services with PostgreSQL and Redis.

## Services

- **API Gateway**: http://localhost:8000 (main entry point)
- **Auth Service**: http://localhost:8001 (authentication)
- **Mood Service**: http://localhost:8003 (mood tracking)
- **Chatbot Service**: http://localhost:8004 (AI chat)
- **Community Service**: http://localhost:8006 (forums)

## API Documentation

Visit any service's `/docs` endpoint for interactive API documentation:
- http://localhost:8000/docs (Gateway)
- http://localhost:8001/docs (Auth)
- http://localhost:8003/docs (Mood)

## Frontend Integration

The frontend automatically detects backend availability:
- ✅ **Backend Available**: Full functionality with real data
- 🔧 **Backend Unavailable**: Mock data mode for development

## Troubleshooting

1. **Port conflicts**: Check if ports 8000-8009 are available
2. **Python dependencies**: Ensure Python 3.11+ is installed
3. **Database issues**: SQLite file will be created automatically
4. **API connection**: Frontend will show connection status in development banner

## Development Workflow

1. Start backend services
2. Frontend will automatically detect and connect
3. All data persists in the local database
4. Use the API docs to test endpoints directly