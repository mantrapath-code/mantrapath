#!/bin/bash

# MantraPath Chatbot Service Startup Script with Phi-3 Integration
# This script starts the chatbot service with proper Phi-3 model setup

set -e

echo "🤖 Starting MantraPath Chatbot Service with Phi-3 Integration"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check available memory (Phi-3 needs at least 4GB)
AVAILABLE_MEMORY=$(docker system info --format '{{.MemTotal}}' 2>/dev/null || echo "0")
REQUIRED_MEMORY=4294967296  # 4GB in bytes

if [ "$AVAILABLE_MEMORY" -lt "$REQUIRED_MEMORY" ]; then
    echo "⚠️  Warning: Available memory may be insufficient for Phi-3 model"
    echo "   Recommended: 4GB+ available memory"
    echo "   Available: $(($AVAILABLE_MEMORY / 1024 / 1024 / 1024))GB"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p ~/.cache/huggingface
mkdir -p ./logs

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp ../.env.example ../.env
    echo "📝 Please edit backend/.env with your configuration"
fi

# Function to check service health
check_service_health() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    echo "🔍 Checking $service_name health on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "http://localhost:$port/health" > /dev/null 2>&1; then
            echo "✅ $service_name is healthy"
            return 0
        fi
        
        echo "⏳ Waiting for $service_name... (attempt $attempt/$max_attempts)"
        sleep 10
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed to start properly"
    return 1
}

# Start core services first
echo "🚀 Starting core services (PostgreSQL, Redis)..."
docker-compose up -d postgres redis

# Wait for core services
echo "⏳ Waiting for core services to be ready..."
sleep 15

# Start Phi-3 agent (this may take a while on first run)
echo "🧠 Starting Phi-3 Mini agent (this may take 5-10 minutes on first run)..."
echo "   The model will be downloaded automatically if not cached"
docker-compose up -d phi3-agent agent-redis

# Start other services
echo "🔧 Starting other backend services..."
docker-compose up -d auth-service profile-service mood-service content-service community-service notification-service ml-service media-service

# Start chatbot service last
echo "💬 Starting chatbot service..."
docker-compose up -d chatbot-service

# Start API gateway
echo "🌐 Starting API gateway..."
docker-compose up -d api-gateway

echo ""
echo "🎉 All services started! Checking health..."
echo ""

# Check service health
services=(
    "postgres:5432"
    "redis:6379"
    "auth-service:8001"
    "chatbot-service:8004"
    "api-gateway:8000"
)

all_healthy=true
for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if ! check_service_health "$name" "$port"; then
        all_healthy=false
    fi
done

# Special check for Phi-3 agent (may take longer to start)
echo "🧠 Checking Phi-3 agent (may take up to 10 minutes)..."
if check_service_health "phi3-agent" "8010"; then
    echo "✅ Phi-3 agent is ready for AI-powered responses"
else
    echo "⚠️  Phi-3 agent not ready - chatbot will use fallback responses"
    echo "   Check logs: docker-compose logs phi3-agent"
fi

echo ""
if [ "$all_healthy" = true ]; then
    echo "🎉 MantraPath Chatbot Service is ready!"
    echo ""
    echo "📊 Service Status:"
    echo "   • API Gateway: http://localhost:8000"
    echo "   • Chatbot Service: http://localhost:8004"
    echo "   • Phi-3 Agent: http://localhost:8010"
    echo "   • Frontend: http://localhost:5173 (start separately)"
    echo ""
    echo "🔧 Management Commands:"
    echo "   • View logs: docker-compose logs -f chatbot-service"
    echo "   • Stop services: docker-compose down"
    echo "   • Restart chatbot: docker-compose restart chatbot-service"
    echo ""
    echo "🧠 AI Features:"
    echo "   • Local Phi-3 Mini model for privacy"
    echo "   • OpenAI GPT fallback (if API key provided)"
    echo "   • Crisis detection and intervention"
    echo "   • Therapeutic conversation support"
else
    echo "⚠️  Some services may not be fully ready. Check individual service logs:"
    echo "   docker-compose logs [service-name]"
fi

echo ""
echo "📝 Next Steps:"
echo "   1. Start the frontend: cd ../frontend && npm run dev"
echo "   2. Visit http://localhost:5173 to test the chatbot"
echo "   3. Monitor logs: docker-compose logs -f"