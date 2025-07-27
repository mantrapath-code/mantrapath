#!/bin/bash

# Stop all MantraPath backend services

echo "🛑 Stopping MantraPath Backend Services..."

# Kill all uvicorn processes (our services)
echo "Stopping API services..."
pkill -f "uvicorn main:app"

# Stop Docker containers
echo "Stopping infrastructure services..."
docker-compose down

echo "✅ All services stopped successfully!"

# Show any remaining processes
echo ""
echo "🔍 Checking for any remaining processes..."
pgrep -f "uvicorn" || echo "No uvicorn processes running"
docker ps -q --filter "name=mantrapath" || echo "No MantraPath containers running"

echo ""
echo "🧹 To clean up completely, you can also run:"
echo "   docker-compose down -v  # Remove volumes"
echo "   docker system prune     # Clean up Docker"