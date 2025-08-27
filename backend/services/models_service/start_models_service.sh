#!/bin/bash

# MantraPath Models Service Startup Script

echo "🚀 Starting MantraPath Models Service..."

# Activate virtual environment
source venv/bin/activate

# Set Python path
export PYTHONPATH=$(pwd)

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start the service
echo "Starting Models Service on port ${SERVICE_PORT:-8080}..."
uvicorn main:app --host 0.0.0.0 --port ${SERVICE_PORT:-8080} --workers 1 --reload
