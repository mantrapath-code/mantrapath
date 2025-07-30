#!/bin/bash

# Quick backend startup script for development
echo "🚀 Starting MantraPath Backend (Development Mode)"

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo "⚠️  Please run this from the backend directory"
    exit 1
fi

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt >/dev/null 2>&1

# Set environment variables for development
export DATABASE_URL="sqlite:///./mantrapath_dev.db"
export JWT_SECRET_KEY="dev-secret-key-change-in-production"
export OPENAI_API_KEY="your-openai-api-key-here"

# Start services in background
echo "🔧 Starting microservices..."

# API Gateway
echo "  → API Gateway (port 8000)"
cd services/gateway && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
GATEWAY_PID=$!

# Auth Service
echo "  → Auth Service (port 8001)"
cd ../auth && python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
AUTH_PID=$!

# Mood Service
echo "  → Mood Service (port 8003)"
cd ../mood && python -m uvicorn main:app --host 0.0.0.0 --port 8003 --reload &
MOOD_PID=$!

# Return to backend root
cd ../..

echo ""
echo "✅ Backend services starting..."
echo "🌐 API Gateway: http://localhost:8000"
echo "🔐 Auth Service: http://localhost:8001" 
echo "😊 Mood Service: http://localhost:8003"
echo ""
echo "📚 API Documentation available at each service's /docs endpoint"
echo "💡 Frontend should now be able to connect to the backend"
echo ""
echo "Press Ctrl+C to stop all services"

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $GATEWAY_PID $AUTH_PID $MOOD_PID 2>/dev/null
    echo "✅ Backend stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for background processes
wait