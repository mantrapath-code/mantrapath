#!/bin/bash
# MantraPath Voice Chatbot Demo Runner

echo "🚀 Starting MantraPath Voice Chatbot Demo"
echo "=========================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if required packages are available
echo "📦 Checking dependencies..."
python3 -c "import httpx, numpy, wave, io, asyncio" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Some dependencies are missing. Installing..."
    pip3 install httpx numpy
fi

# Check if services are running
echo "🔍 Checking services..."
services=(
    "http://localhost:8004/health"
    "http://localhost:8081/health" 
    "http://localhost:8011/health"
)

for service in "${services[@]}"; do
    if curl -s "$service" > /dev/null 2>&1; then
        echo "✅ Service is running: $service"
    else
        echo "❌ Service is not running: $service"
        echo "   Please start the services before running the demo."
        exit 1
    fi
done

echo ""
echo "🎮 Starting interactive demo..."
echo "==============================="

# Run the demo
python3 demo_chatbot_voice.py

echo ""
echo "🎉 Demo completed!"
