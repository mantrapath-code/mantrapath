#!/bin/bash

# MantraPath Backend Services Startup Script

set -e

echo "🚀 Starting MantraPath Backend Services..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start infrastructure services
echo "🗄️ Starting infrastructure services..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for database and Redis to be ready..."
sleep 10

# Initialize database
echo "🏗️ Initializing database..."
python -c "
from shared.database import db_config
from shared.models import Base
db_config.create_tables()
print('Database initialized successfully!')
"

# Function to start a service
start_service() {
    local service_name=$1
    local port=$2
    local service_path="services/${service_name}_service"
    
    echo "🚀 Starting $service_name service on port $port..."
    
    cd $service_path
    export PYTHONPATH="${PYTHONPATH}:../../"
    uvicorn main:app --host 0.0.0.0 --port $port --reload &
    cd ../../
    
    sleep 2
}

# Start all microservices
echo "🎯 Starting microservices..."

start_service "auth" 8001
start_service "profile" 8002  
start_service "mood" 8003
start_service "chatbot" 8004
start_service "content" 8005
start_service "community" 8006
start_service "notification" 8007
start_service "media" 8009

# Start API Gateway last
echo "🌐 Starting API Gateway..."
cd services/api_gateway
export PYTHONPATH="${PYTHONPATH}:../../"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
cd ../../

echo "✅ All services started successfully!"
echo ""
echo "📋 Service Status:"
echo "   🌐 API Gateway:      http://localhost:8000"
echo "   🔐 Auth Service:     http://localhost:8001"
echo "   👤 Profile Service:  http://localhost:8002"
echo "   😊 Mood Service:     http://localhost:8003"
echo "   🤖 Chatbot Service:  http://localhost:8004"
echo "   📝 Content Service:  http://localhost:8005"
echo "   👥 Community Service: http://localhost:8006"
echo "   🔔 Notification Service: http://localhost:8007"
echo "   📁 Media Service:    http://localhost:8009"
echo ""
echo "📚 API Documentation available at each service's /docs endpoint"
echo "🏥 Health checks available at each service's /health endpoint"
echo ""
echo "🛑 To stop all services, run: ./scripts/stop_services.sh"

# Keep script running
wait