# 🚀 Starting MantraPath Backend for Development

## Quick Start (Recommended)

### Option 1: Simple Python Start
```bash
cd backend
python3 simple_start.py
```

### Option 2: Manual Service Start
```bash
cd backend

# Terminal 1 - Auth Service
cd services/auth
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Mood Service  
cd services/mood
python3 -m uvicorn main:app --host 0.0.0.0 --port 8003 --reload

# Terminal 3 - API Gateway
cd services/gateway  
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Prerequisites

Make sure you have Python 3.8+ installed:
```bash
python3 --version
```

Install dependencies:
```bash
cd backend
pip3 install -r requirements.txt
```

## Testing Backend Connection

Once started, you should see:
- 🌐 API Gateway: http://localhost:8000
- 🔐 Auth Service: http://localhost:8001  
- 😊 Mood Service: http://localhost:8003

Test the health endpoints:
```bash
# Test API Gateway
curl http://localhost:8000/health

# Test Auth Service
curl http://localhost:8001/health

# Test Mood Service  
curl http://localhost:8003/health
```

## Frontend Integration

When the backend is running:
1. Refresh the MantraPath web app
2. The authentication screen will show "Backend Connected" 
3. Registration and login will work with real data persistence
4. All mood tracking, journaling, and community features will use real backend APIs

## Troubleshooting

### Port Already in Use
If you get "port already in use" errors:
```bash
# Kill processes on specific ports
sudo lsof -ti:8000 | xargs kill -9
sudo lsof -ti:8001 | xargs kill -9
sudo lsof -ti:8003 | xargs kill -9
```

### Database Issues
Reset the database:
```bash
cd backend
rm -f mantrapath.db
python3 setup_backend.py
```

### Python Path Issues
Make sure the shared directory is in Python path:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/shared"
```

## Development Notes

- SQLite database is created automatically in `backend/mantrapath.db`
- All services support hot reload with `--reload` flag
- API documentation available at `/docs` on each service port
- JWT tokens are used for authentication with 1-hour expiry
- WebSocket connections for real-time features are on the same ports

## Production Deployment

For production deployment, see `DEPLOYMENT.md` for Docker and environment configuration.