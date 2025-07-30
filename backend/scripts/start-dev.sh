#!/bin/bash

# MantraPath Backend Startup Script

echo "🚀 Starting MantraPath Backend Services..."

# Check if Python 3.11+ is installed
if ! python3 --version | grep -E "3\.(11|12)" > /dev/null; then
    echo "❌ Python 3.11+ is required"
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Start all services in development mode
echo "🔧 Starting microservices..."

# API Gateway (Port 8000)
echo "Starting API Gateway on port 8000..."
python -m services.api_gateway.main &
API_GATEWAY_PID=$!

# Wait a bit for the gateway to start
sleep 2

# Auth Service (Port 8001)
echo "Starting Auth Service on port 8001..."
python -m services.auth_service.main &
AUTH_PID=$!

# Mood Service (Port 8003)
echo "Starting Mood Service on port 8003..."
python -m services.mood_service.main &
MOOD_PID=$!

# Chatbot Service (Port 8004)
echo "Starting Chatbot Service on port 8004..."
python -m services.chatbot_service.main &
CHATBOT_PID=$!

# Community Service (Port 8006)
echo "Starting Community Service on port 8006..."
python -m services.community_service.main &
COMMUNITY_PID=$!

echo ""
echo "✅ All services started successfully!"
echo ""
echo "🌐 API Gateway: http://localhost:8000"
echo "🔐 Auth Service: http://localhost:8001"
echo "😊 Mood Service: http://localhost:8003"
echo "🤖 Chatbot Service: http://localhost:8004"
echo "👥 Community Service: http://localhost:8006"
echo ""
echo "📚 API Documentation:"
echo "   - API Gateway: http://localhost:8000/docs"
echo "   - Auth Service: http://localhost:8001/docs"
echo "   - Mood Service: http://localhost:8003/docs"
echo "   - Chatbot Service: http://localhost:8004/docs"
echo "   - Community Service: http://localhost:8006/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $API_GATEWAY_PID $AUTH_PID $MOOD_PID $CHATBOT_PID $COMMUNITY_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for all background processes
wait