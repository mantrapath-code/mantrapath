#!/bin/bash

# MantraPath Update Script

set -e

echo "🔄 Updating MantraPath services..."

cd backend

# Pull latest images
echo "📥 Pulling latest base images..."
docker-compose pull

# Rebuild services that have changes
echo "🔨 Rebuilding services..."
docker-compose build --no-cache

# Rolling update strategy
echo "🔄 Performing rolling update..."

# Update backend services one by one
services=("auth-service" "profile-service" "mood-service" "chatbot-service" "content-service" "community-service" "notification-service" "media-service")

for service in "${services[@]}"; do
    echo "🔄 Updating $service..."
    docker-compose up -d --no-deps $service
    sleep 10
done

# Update API gateway
echo "🔄 Updating API gateway..."
docker-compose up -d --no-deps api-gateway

# Update frontend
echo "🔄 Updating frontend..."
docker-compose up -d --no-deps frontend

echo "✅ Update completed!"
echo "📋 Service Status:"
docker-compose ps