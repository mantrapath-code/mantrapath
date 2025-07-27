#!/bin/bash

# Simple backend starter for development
echo "🚀 Starting MantraPath Backend Services..."

# Set environment variables
export DATABASE_URL="sqlite:///./mantrapath.db"
export JWT_SECRET_KEY="dev-secret-key-change-in-production"
export AUTH_SERVICE_URL="http://localhost:8001"
export MOOD_SERVICE_URL="http://localhost:8003"

# Get the backend directory
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED_DIR="$BACKEND_DIR/shared"

echo "Backend Directory: $BACKEND_DIR"
echo "Shared Directory: $SHARED_DIR"

# Add shared directory to Python path
export PYTHONPATH="$SHARED_DIR:$PYTHONPATH"

echo ""
echo "Starting services..."
echo ""

# Function to start a service
start_service() {
    local service_name=$1
    local port=$2
    local service_dir=$3
    
    echo "🔧 Starting $service_name on port $port"
    
    if [ -d "$service_dir" ]; then
        cd "$service_dir"
        # Start the service in background
        python3 -m uvicorn main:app --host 0.0.0.0 --port $port --reload &
        SERVICE_PID=$!
        echo "   Started with PID: $SERVICE_PID"
        cd "$BACKEND_DIR"
        sleep 2
    else
        echo "   ⚠️  Service directory not found: $service_dir"
    fi
}

# Start Auth Service
start_service "Auth Service" 8001 "$BACKEND_DIR/services/auth"

# Start Mood Service  
start_service "Mood Service" 8003 "$BACKEND_DIR/services/mood"

# Start API Gateway
start_service "API Gateway" 8000 "$BACKEND_DIR/services/gateway"

echo ""
echo "✅ Backend services started!"
echo ""
echo "Available endpoints:"
echo "   🌐 API Gateway: http://localhost:8000"
echo "   🔐 Auth Service: http://localhost:8001"
echo "   😊 Mood Service: http://localhost:8003"
echo ""
echo "📚 API Documentation:"
echo "   Gateway: http://localhost:8000/docs"
echo "   Auth: http://localhost:8001/docs"
echo "   Mood: http://localhost:8003/docs"
echo ""
echo "💡 Frontend should now connect to: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all services"

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    jobs -p | xargs -r kill
    echo "✅ All services stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Wait for background jobs
wait