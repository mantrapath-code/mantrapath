#!/bin/bash

# Development Environment Setup

set -e

echo "🛠️ Setting up MantraPath development environment..."

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required. Please install Docker first."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required. Please install Node.js first."
    exit 1
fi

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
npm install

# Set up backend environment
echo "🔧 Setting up backend environment..."
cd backend

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "📝 Created backend/.env from example"
fi

# Start development databases
echo "🗄️ Starting development databases..."
docker-compose up -d postgres redis mongodb influxdb

# Wait for databases
echo "⏳ Waiting for databases to start..."
sleep 15

# Run database migrations
echo "🔄 Running database migrations..."
# Note: Add migration commands here when available

echo "✅ Development environment ready!"
echo ""
echo "🚀 To start development:"
echo "   Frontend: npm run dev"
echo "   Backend: cd backend && ./start-dev.sh"
echo ""
echo "🌐 Development URLs:"
echo "   Frontend: ${PROTOCOL}://${DOMAIN}:${FRONTEND_PORT}"
echo "   API Gateway: ${PROTOCOL}://${DOMAIN}:${API_GATEWAY_PORT}"
echo "   Database: postgresql://mantrapath:mantrapath123@${DOMAIN}:${DB_PORT}/mantrapath"