#!/bin/bash
"""
AI Context Store Development Setup
Run from backend/ directory to start AI Context Store service
"""

echo "🚀 Starting AI Context Store Service Development Setup"
echo "=================================================="

# Check if we're in the backend directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Please run this script from the backend/ directory"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️ Warning: .env file not found. Creating basic .env file..."
    cat > .env << EOF
# Database Configuration
POSTGRES_DB=mantrapath
POSTGRES_USER=mantrapath
POSTGRES_PASSWORD=mantrapath123
POSTGRES_PORT=5432
DATABASE_URL=postgresql://mantrapath:mantrapath123@localhost:5432/mantrapath

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PORT=6379

# AI Context Store Configuration
AI_CONTEXT_STORE_PORT=8010

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# Environment
ENVIRONMENT=development
DEBUG=true
EOF
    echo "✅ Created basic .env file"
fi

echo "📋 Starting infrastructure services..."

# Start core infrastructure (postgres, redis, nats)
docker-compose up -d postgres redis nats

echo "⏳ Waiting for infrastructure to be ready..."
sleep 10

# Check if infrastructure is ready
echo "🔍 Checking infrastructure health..."
docker-compose ps postgres redis nats

echo "🏗️ Building AI Context Store service..."
docker-compose build ai-context-store

echo "🚀 Starting AI Context Store service..."
docker-compose up -d ai-context-store

echo "⏳ Waiting for AI Context Store to be ready..."
sleep 15

echo "🔍 Checking AI Context Store health..."
if curl -f http://localhost:8010/health > /dev/null 2>&1; then
    echo "✅ AI Context Store is healthy and ready!"
    echo ""
    echo "📊 Service endpoints:"
    echo "   - Health: http://localhost:8010/health"
    echo "   - Metrics: http://localhost:8010/metrics"
    echo "   - API: http://localhost:8010/api/v1/context"
    echo "   - Intelligence: http://localhost:8010/api/v1/intelligence"
    echo ""
    echo "🧪 To test the service, run:"
    echo "   python test_ai_context_store.py"
    echo ""
    echo "📋 To view logs:"
    echo "   docker-compose logs -f ai-context-store"
    echo ""
    echo "🛑 To stop:"
    echo "   docker-compose down"
else
    echo "❌ AI Context Store failed to start properly"
    echo "📋 Check logs with: docker-compose logs ai-context-store"
    exit 1
fi
