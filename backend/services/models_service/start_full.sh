#!/bin/bash
"""
Full Models Service Startup with Phi-3
Starts the service and loads Phi-3 for text generation
"""

echo "🚀 Starting Models Service (Full Mode with Phi-3)"
echo "================================================"

# Set environment variables for full startup
export PYTHONPATH="/app"
export MODELS_DIR="/app/models"
export CACHE_DIR="/app/cache"
export MODELS_SERVICE_MODE="full"
export MODELS_SERVICE_PORT="8080"

# Create necessary directories
mkdir -p /app/models /app/cache /app/logs

echo "📂 Created directories:"
echo "   - /app/models"
echo "   - /app/cache" 
echo "   - /app/logs"

echo ""
echo "🔧 Environment Configuration:"
echo "   - PYTHONPATH: $PYTHONPATH"
echo "   - MODELS_DIR: $MODELS_DIR"
echo "   - CACHE_DIR: $CACHE_DIR"
echo "   - SERVICE_MODE: $MODELS_SERVICE_MODE"
echo "   - SERVICE_PORT: $MODELS_SERVICE_PORT"

echo ""
echo "🤖 Loading Phi-3 model for text generation..."
echo "⚠️  Note: First startup may take 5-10 minutes to download Phi-3"

# Start the service with uvicorn
exec python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload
