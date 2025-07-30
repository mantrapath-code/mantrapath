#!/bin/bash

# MantraPath Backend Stop Script

echo "🛑 Stopping MantraPath Backend Services..."

# Stop development services
docker-compose -f docker-compose-dev.yml down

# Stop all services if development compose doesn't exist
docker-compose -f docker-compose-clean.yml down 2>/dev/null || true
docker-compose down 2>/dev/null || true

# Clean up unused containers and volumes
echo "🧹 Cleaning up Docker resources..."
docker system prune -f

echo "✅ All services stopped successfully!"
