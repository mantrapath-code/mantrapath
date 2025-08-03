#!/bin/bash

# MantraPath Backend Services Startup Script
echo "🚀 Starting MantraPath Backend Services..."

# Set working directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT/backend"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Install requirements if needed
if [ ! -f "requirements_installed.flag" ]; then
    echo "📦 Installing Python requirements..."
    pip3 install -r requirements.txt
    touch requirements_installed.flag
fi

# Start services
echo "🔄 Starting Notification Service (Port 8002)..."
cd services/notification_service
python3 -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload &
NOTIFICATION_PID=$!

echo "🔄 Starting Mood Service (Port 8003)..."
cd ../mood_service
python3 -m uvicorn main:app --host 0.0.0.0 --port 8003 --reload &
MOOD_PID=$!

echo "✅ Backend services started!"
echo "📍 Notification Service: http://localhost:8002"
echo "📍 Mood Service: http://localhost:8003"
echo ""
echo "💡 Services are running with auto-reload enabled"
echo "🛑 Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'echo "🛑 Stopping services..."; kill $NOTIFICATION_PID $MOOD_PID; exit' INT
wait
