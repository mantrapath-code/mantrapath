#!/bin/bash

# MantraPath Deployment API Service Startup Script

echo "🚀 Starting MantraPath Deployment API Service..."

# Check if Python 3.11+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11+ is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION+ is required, but found $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version: $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cat > .env << EOF
# Deployment API Service Configuration
DEPLOYMENT_API_PORT=8086
DEPLOYMENT_API_HOST=0.0.0.0
ENVIRONMENT=development
DEBUG=true

# Authentication
FRONTEND_ENGINEER_SECRET=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Rate Limiting
RATE_LIMIT_ENABLED=true
DEFAULT_RATE_LIMIT=1000
FRONTEND_ENGINEER_LIMIT=500

# Service Discovery
API_GATEWAY_URL=http://localhost:8000
VOICE_SERVICE_URL=http://localhost:8011
MODELS_SERVICE_URL=http://localhost:8085
COMMUNITY_SERVICE_URL=http://localhost:8012
ML_SERVICE_URL=http://localhost:8013

# Redis Configuration
REDIS_URL=redis://localhost:6380
REDIS_DB=0

# Database Configuration
DATABASE_URL=postgresql://deployment_user:deployment_password@localhost:5433/mantrapath_deployment
EOF
    echo "✅ .env file created. Please update the values as needed."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p database

# Start the service
echo "🚀 Starting Deployment API Service on port 8086..."
echo "📚 API Documentation available at: http://localhost:8086/docs"
echo "🔍 Health check available at: http://localhost:8086/health"
echo "⏹️  Press Ctrl+C to stop the service"

# Start the service with uvicorn
uvicorn src.main:app \
    --host 0.0.0.0 \
    --port 8086 \
    --reload \
    --log-level info \
    --access-log

