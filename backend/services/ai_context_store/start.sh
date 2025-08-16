#!/bin/bash

# AI Context Store Service Deployment Script
# Starts the AI Context Store service with proper configuration

set -e

echo "🚀 Starting AI Context Store Service..."

# Set environment variables
export AI_CONTEXT_STORE_PORT=8010
export PYTHONPATH="${PWD}/../..:$PYTHONPATH"

# Check if Redis is running
if ! redis-cli ping >/dev/null 2>&1; then
    echo "⚠️ Redis is not running. Starting Redis..."
    redis-server --daemonize yes
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "✅ Environment ready. Starting AI Context Store..."

# Start the service
python main.py
