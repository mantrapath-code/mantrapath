#!/bin/bash

# MantraPath Backend Stop Script
# This script stops all MantraPath backend services gracefully

echo "🛑 Stopping MantraPath Backend Services..."

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "⚠️  Docker is not running or not accessible"
    exit 1
fi

# Stop all compose services
echo "🛑 Stopping Docker Compose services..."
docker-compose down

# Also check for alternative compose files
if [ -f "docker-compose-dev.yml" ]; then
    echo "🛑 Stopping development compose services..."
    docker-compose -f docker-compose-dev.yml down
fi

if [ -f "docker-compose-clean.yml" ]; then
    echo "🛑 Stopping clean compose services..."
    docker-compose -f docker-compose-clean.yml down
fi

# Stop any MantraPath containers that might be running independently
echo "🛑 Stopping any remaining MantraPath containers..."
docker ps --filter "name=mantrapath" --format "table {{.Names}}" | grep -v "NAMES" | xargs -r docker stop

# Optional: Remove stopped containers
read -p "🗑️  Remove stopped MantraPath containers? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removing stopped containers..."
    docker ps -a --filter "name=mantrapath" --format "table {{.Names}}" | grep -v "NAMES" | xargs -r docker rm
    
    # Clean up unused Docker resources
    echo "🧹 Cleaning up unused Docker resources..."
    docker system prune -f
fi

# Show final status
echo ""
echo "📊 Remaining MantraPath containers:"
docker ps --filter "name=mantrapath" --format "table {{.Names}}\t{{.Status}}" || echo "   None found"

echo ""
echo "✅ All MantraPath services stopped successfully!"
echo "💡 To start services again, run: ./start-dev.sh"
