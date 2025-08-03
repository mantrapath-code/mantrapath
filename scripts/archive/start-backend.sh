#!/bin/bash

# MantraPath Backend Services Only
echo "🔧 Starting MantraPath Backend Services..."

# Kill any existing backend processes
echo "🧹 Cleaning up existing backend processes..."
lsof -ti:8000,8002,8003 | xargs kill -9 2>/dev/null || true

# Set working directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT/backend"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required"
    exit 1
fi

# Setup virtual environment
if [ ! -f ".venv/bin/activate" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python3 -c "
import sys
sys.path.append('.')
from shared.database import create_tables
create_tables()
print('✅ Database initialized')
"

# Start services
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
cd ../..

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

check_service "http://localhost:8002/health" "Notification Service"
check_service "http://localhost:8003/health" "Mood Service"
check_service "http://localhost:8000/health" "API Gateway"

echo ""
echo "🎉 Backend services are running!"
echo "📍 API Gateway: http://localhost:8000"
echo "📍 Notification Service: http://localhost:8002" 
echo "📍 Mood Service: http://localhost:8003"
echo ""
echo "📋 Available endpoints:"
echo "   • Mood tracking: http://localhost:8003/api/v1/mood/"
echo "   • Notifications: http://localhost:8002/notify/"
echo "   • Health checks: http://localhost:8000/health"
echo ""
echo "💡 Services have auto-reload enabled"
echo "🛑 Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'echo "🛑 Stopping services..."; kill $NOTIFICATION_PID $MOOD_PID $GATEWAY_PID; deactivate; exit' INT
wait
