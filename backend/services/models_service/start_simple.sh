#!/bin/bash
#
# Simple Models Service Startup
# Starts the service without trying to download models first
#

echo "🚀 Starting Models Service"
echo "========================================"

# Set environment variables for minimal startup
export PYTHONPATH="/app"
export MODELS_DIR="/app/models"
export CACHE_DIR="/app/cache"
# MODELS_SERVICE_MODE can be set via Docker Compose environment
export MODELS_SERVICE_PORT="8080"

# Create necessary directories
mkdir -p /app/models /app/cache /app/logs

echo "📂 Created directories:"
echo "   - Models: $MODELS_DIR"
echo "   - Cache: $CACHE_DIR"

echo "🔧 Starting Models Service..."
echo "   - Mode: ${MODELS_SERVICE_MODE:-normal} (via environment)"
echo "   - Voice Stack: ${VOICE_STACK_MODE:-standard}"
echo "   - Port: $MODELS_SERVICE_PORT"

# Start the service directly
exec python main.py
