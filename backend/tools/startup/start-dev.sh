#!/bin/bash

# MantraPath Backend Development Startup Script
# This script first sets up the environment, then starts services

echo "🚀 Starting MantraPath Backend Services..."

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$SCRIPT_DIR"

# Check if integrated startup script exists
INTEGRATED_STARTUP="$PROJECT_ROOT/scripts/start-backend-integrated.sh"

if [ -f "$INTEGRATED_STARTUP" ]; then
    echo "📦 Using integrated startup script..."
    chmod +x "$INTEGRATED_STARTUP"
    exec "$INTEGRATED_STARTUP" --docker
else
    echo "⚠️  Integrated startup script not found, falling back to Docker-only mode..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker first."
        echo "💡 Or use the integrated script: $PROJECT_ROOT/scripts/start-backend-integrated.sh"
        exit 1
    fi

    # Stop any existing containers
    echo "🛑 Stopping existing containers..."
    docker-compose down

    # Build and start services
    echo "🔨 Building and starting services..."
    docker-compose up --build -d

    # Wait a moment for services to initialize
    echo "⏳ Waiting for services to initialize..."
    sleep 10

echo "✅ All services started successfully!"
echo ""
echo "📍 Service Endpoints:"
echo "   🌐 API Gateway: http://localhost:8000"
echo "   🔐 Auth Service: http://localhost:8001"
echo "   👤 Profile Service: http://localhost:8002"
echo "   😊 Mood Service: http://localhost:8003"
echo "   🤖 Chatbot Service: http://localhost:8004"
echo "   📝 Content Service: http://localhost:8005"
echo "   👥 Community Service: http://localhost:8006"
echo "   🔔 Notification Service: http://localhost:8007"
echo "   🧠 ML Service: http://localhost:8008"
echo "   📁 Media Service: http://localhost:8009"
echo "   🌍 Translation Service: http://localhost:8010"
echo "   🎙️  Voice Service: http://localhost:8011"
echo "   🎯 Action Orchestrator: http://localhost:8012"
echo "   � AI Context Store: http://localhost:8013"
echo "   ⚡ AI Event Processor: http://localhost:8014"
echo "   🎵 Voice Event Processor: http://localhost:8015"
echo ""
echo "🏗️  Infrastructure:"
echo "   �🗄️  PostgreSQL: localhost:5432"
echo "   ⚡ Redis: localhost:6379"
echo "   📡 NATS: localhost:4222 (Monitor: localhost:8222)"
echo ""
echo "🔍 Health Checks:"
echo "   curl http://localhost:8000/health  # API Gateway"
echo "   curl http://localhost:8001/health  # Auth Service"
echo "   curl http://localhost:8002/health  # Profile Service"
echo "   curl http://localhost:8003/health  # Mood Service"
echo "   curl http://localhost:8004/health  # Chatbot Service"
echo "   curl http://localhost:8005/health  # Content Service"
echo "   curl http://localhost:8006/health  # Community Service"
echo "   curl http://localhost:8007/health  # Notification Service"
echo "   curl http://localhost:8008/health  # ML Service"
echo "   curl http://localhost:8009/health  # Media Service"
echo "   curl http://localhost:8010/health  # Translation Service"
echo "   curl http://localhost:8011/health  # Voice Service"
echo "   curl http://localhost:8012/health  # Action Orchestrator"
echo "   curl http://localhost:8013/health  # AI Context Store"
echo "   curl http://localhost:8014/health  # AI Event Processor"
echo "   curl http://localhost:8015/health  # Voice Event Processor"
echo ""
echo "🧪 Quick Health Check:"
echo "   python ../scripts/quick_health_check_fixed.py"
echo ""
echo "🧪 Test Community Features:"
echo "   # Register a user:"
echo "   curl -X POST http://localhost:8000/register -H 'Content-Type: application/json' -d '{\"email\":\"test@example.com\",\"username\":\"testuser\",\"password\":\"password123\"}'"
echo "   # Get forums:"
echo "   curl -H 'Authorization: Bearer YOUR_TOKEN' http://localhost:8000/forums"
echo ""
echo "✨ Ready to develop! All services are running."
fi
