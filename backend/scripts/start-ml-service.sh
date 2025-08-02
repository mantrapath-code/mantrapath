#!/bin/bash

# Start ML Service - Machine Learning service for smart notifications
echo "🧠 Starting MantraPath ML Service..."

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:/app"
export ML_SERVICE_PORT=8008

# Navigate to ML service directory
cd "$(dirname "$0")/../services/ml_service"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the ML service
echo "Starting ML service on port $ML_SERVICE_PORT..."
uvicorn main:app --host 0.0.0.0 --port $ML_SERVICE_PORT --reload
