#!/bin/bash

# MantraPath API Gateway - Production Deployment Script

set -e

echo "🚀 Deploying MantraPath API Gateway to Production..."

# Configuration
IMAGE_NAME="mantrapath-gateway"
CONTAINER_NAME="mantrapath-gateway-prod"
NETWORK_NAME="mantrapath-network"
REDIS_CONTAINER="redis-prod"

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t $IMAGE_NAME:latest .

# Create network if it doesn't exist
echo "🌐 Setting up Docker network..."
docker network create $NETWORK_NAME 2>/dev/null || true

# Start Redis if not running
echo "🔧 Setting up Redis..."
if ! docker ps | grep -q $REDIS_CONTAINER; then
    docker run -d \
        --name $REDIS_CONTAINER \
        --network $NETWORK_NAME \
        -p 6379:6379 \
        --restart unless-stopped \
        redis:7-alpine
fi

# Stop existing container if running
echo "🛑 Stopping existing container..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Start the new container
echo "🌟 Starting API Gateway container..."
docker run -d \
    --name $CONTAINER_NAME \
    --network $NETWORK_NAME \
    -p 8000:8000 \
    -e GATEWAY_ENVIRONMENT=production \
    -e GATEWAY_DEBUG=false \
    -e GATEWAY_REDIS_URL=redis://$REDIS_CONTAINER:6379 \
    --restart unless-stopped \
    $IMAGE_NAME:latest

# Wait for container to start
echo "⏳ Waiting for gateway to start..."
sleep 10

# Health check
echo "🏥 Performing health check..."
if curl -f http://localhost:8000/health; then
    echo "✅ Gateway is healthy and running!"
    echo "📍 Gateway URL: http://localhost:8000"
    echo "📋 Health check: http://localhost:8000/health"
    echo "📈 Metrics: http://localhost:8000/metrics"
else
    echo "❌ Health check failed!"
    echo "📋 Checking logs..."
    docker logs $CONTAINER_NAME
    exit 1
fi

echo "🎉 Deployment completed successfully!"
