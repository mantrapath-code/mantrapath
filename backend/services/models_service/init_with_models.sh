#!/bin/bash
"""
Pre-initialization script for Models Service
Ensures all required models are downloaded before the service starts
"""

echo "🚀 Models Service Pre-Initialization"
echo "===================================="

# Set environment variables
export PYTHONPATH="/app"
export MODELS_DIR="/app/models"
export CACHE_DIR="/app/cache"

# Create necessary directories
mkdir -p /app/models /app/cache /app/logs

# Function to check if models service is responding
check_service() {
    curl -s -f http://localhost:8080/health >/dev/null 2>&1
    return $?
}

# Function to wait for service startup
wait_for_service() {
    echo "⏳ Waiting for Models Service to start..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if check_service; then
            echo "✅ Models Service is responding!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo "   Attempt $attempt/$max_attempts - waiting..."
        sleep 2
    done
    
    echo "❌ Models Service failed to start after 60 seconds"
    return 1
}

# Start the models service in background
echo "🔄 Starting Models Service..."
python main.py &
SERVICE_PID=$!

# Wait for service to be ready
if wait_for_service; then
    echo "📦 Downloading essential models..."
    
    # Download models using our enhanced script
    python3 /app/setup_enhanced_voice_models.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Models downloaded successfully!"
    else
        echo "⚠️ Some models failed to download, but service will continue"
    fi
else
    echo "❌ Service startup failed"
    exit 1
fi

# Keep the service running
echo "🎯 Models Service ready with Voice models!"
wait $SERVICE_PID
