#!/bin/bash

# MantraPath API Gateway - Development Start Script

set -e

echo "🚀 Starting MantraPath API Gateway Development Environment..."

# Check if Python 3.11+ is available
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11+ is required but not found"
    exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not found"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3.11 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment configuration..."
    cp config/.env.example .env
    echo "✏️ Please edit .env file with your configuration"
fi

# Check if Redis is running
echo "🔍 Checking Redis connection..."
if ! redis-cli ping &> /dev/null; then
    echo "⚠️ Redis is not running. Starting Redis with Docker..."
    docker run -d --name redis-gateway -p 6379:6379 redis:7-alpine
    echo "⏳ Waiting for Redis to start..."
    sleep 3
fi

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

# Start the gateway
echo "🌟 Starting API Gateway..."
echo "📍 Gateway will be available at: http://localhost:8000"
echo "📋 Health check: http://localhost:8000/health"
echo "📊 Detailed health: http://localhost:8000/health/detailed"
echo "📈 Metrics: http://localhost:8000/metrics"
echo ""

python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
