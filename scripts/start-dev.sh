#!/bin/bash

# MantraPath Full Development Environment
echo "🚀 Starting MantraPath Full Development Environment..."

# Kill any existing processes on our ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:8000,8002,8003,5173 | xargs kill -9 2>/dev/null || true

# Set working directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Check dependencies
echo "🔍 Checking dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ Error: Node.js/npm is required"
    exit 1
fi

# Backend setup
echo "🔧 Setting up backend..."
cd backend

# Install Python dependencies
if [ ! -f ".venv/bin/activate" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt

# Start backend services
echo "🔄 Starting backend services..."

# Start Notification Service
cd services/notification_service
python3 -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload &
NOTIFICATION_PID=$!
cd ../..

# Start Mood Service  
cd services/mood_service
python3 -m uvicorn main:app --host 0.0.0.0 --port 8003 --reload &
MOOD_PID=$!
cd ../..

# Start API Gateway
cd services/api_gateway
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
GATEWAY_PID=$!
cd ../../..

# Frontend setup
echo "🎨 Setting up frontend..."
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start frontend dev server
npm run dev &
FRONTEND_PID=$!

# Health checks
echo "🏥 Performing health checks..."
sleep 5

check_service() {
    local url=$1
    local name=$2
    if curl -s "$url" > /dev/null; then
        echo "✅ $name is healthy"
        return 0
    else
        echo "❌ $name failed to start"
        return 1
    fi
}

# Check all services
check_service "http://localhost:8002/health" "Notification Service"
check_service "http://localhost:8003/health" "Mood Service" 
check_service "http://localhost:8000/health" "API Gateway"
check_service "http://localhost:5173" "Frontend Dev Server"

echo ""
echo "🎉 MantraPath Development Environment is running!"
echo "📍 Frontend: http://localhost:5173"
echo "📍 API Gateway: http://localhost:8000"
echo "📍 Notification Service: http://localhost:8002"
echo "📍 Mood Service: http://localhost:8003"
echo ""
echo "🔥 Features enabled:"
echo "   • Real-time notifications via WebSocket"
echo "   • Smart notification scheduling with user patterns"
echo "   • Mood analytics and pattern detection"
echo "   • Persistent data storage (SQLite)"
echo ""
echo "💡 Backend services have auto-reload enabled"
echo "🛑 Press Ctrl+C to stop all services"

# Open browser
if command -v open &> /dev/null; then
    echo "🌐 Opening browser..."
    sleep 2
    open http://localhost:5173
fi

# Wait for interrupt and cleanup
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $NOTIFICATION_PID $MOOD_PID $GATEWAY_PID $FRONTEND_PID 2>/dev/null
    deactivate 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

trap cleanup INT TERM
wait
