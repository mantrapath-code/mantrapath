#!/bin/bash

echo "🚀 Starting MantraPath Backend Services..."
echo "==========================================="

# Check if uvicorn is available
if ! command -v uvicorn &> /dev/null; then
    echo "❌ uvicorn not found. Installing..."
    pip install uvicorn fastapi sqlalchemy pydantic python-jose passlib bcrypt httpx
fi

# Set environment variables
export DATABASE_URL="sqlite:///./mantrapath.db"
export JWT_SECRET_KEY="dev-secret-key-change-in-production"
export AUTH_SERVICE_URL="http://localhost:8001"
export MOOD_SERVICE_URL="http://localhost:8003"

# Create logs directory
mkdir -p backend/logs

# Function to start a service
start_service() {
    local name=$1
    local port=$2
    local path=$3
    
    echo "🔄 Starting $name on port $port..."
    
    cd "backend/$path"
    
    # Set Python path to include shared directory
    export PYTHONPATH="../shared:$PYTHONPATH"
    
    # Start service in background
    uvicorn main:app --host 0.0.0.0 --port $port --reload > "../logs/${name,,}.log" 2>&1 &
    local pid=$!
    
    # Save PID for later cleanup
    echo $pid > "../logs/${name,,}.pid"
    
    cd - > /dev/null
    
    # Wait for service to start
    sleep 3
    
    # Check if service is running
    if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "✅ $name started successfully"
    else
        echo "⚠️  $name may be starting (check logs if issues persist)"
    fi
}

# Start services in order
start_service "Auth-Service" 8001 "services/auth"
start_service "Mood-Service" 8003 "services/mood"  
start_service "API-Gateway" 8000 "services/gateway"

echo ""
echo "🌟 Backend Services Status:"
echo "🔐 Auth Service: http://localhost:8001"
echo "😊 Mood Service: http://localhost:8003"
echo "🌐 API Gateway: http://localhost:8000"
echo ""
echo "📚 API Documentation:"
echo "   Auth: http://localhost:8001/docs"
echo "   Mood: http://localhost:8003/docs"
echo "   Gateway: http://localhost:8000/docs"
echo ""
echo "📋 Service logs are in backend/logs/"
echo "🛑 To stop services, run: ./stop-backend.sh"
echo ""
echo "✨ Your frontend should now connect to the real backend!"