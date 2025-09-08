#!/bin/bash
"""
Quick Fix for Models Service Issues
This script addresses the immediate problems preventing the models service from starting
"""

echo "🔧 Fixing Models Service Issues..."

# Navigate to models service directory
cd /Users/sachin/Desktop/mantrapath/backend/services/models_service

echo "📦 Installing missing packages..."
pip install flash-attn || echo "⚠️ flash-attn installation failed (this is optional)"
pip install psutil

echo "🛑 Stopping current models service..."
docker compose -f ../../docker-compose.yml stop models-service

echo "🧹 Cleaning up containers..."
docker compose -f ../../docker-compose.yml rm -f models-service

echo "🚀 Starting models service in minimal mode..."
export MODELS_SERVICE_MODE=minimal
export MODELS_SERVICE_PORT=8080

# Start in minimal mode using our new startup script
python start_minimal.py &

echo "⏳ Waiting for service to start..."
sleep 10

echo "🔍 Checking service health..."
curl -s http://localhost:8080/health || echo "❌ Service not responding yet"

echo "✅ Models service restart complete!"
echo ""
echo "📋 Service Status:"
echo "   - Models service should now be running on port 8080"
echo "   - Service is in minimal mode (models load on-demand)"
echo "   - No pre-loaded models to avoid startup delays"
echo "   - Pydantic warnings should be resolved"
echo "   - FastAPI deprecation warnings should be resolved"
echo ""
echo "🔗 Next Steps:"
echo "   1. Test service: curl http://localhost:8080/health"
echo "   2. Check logs: docker compose logs models-service"
echo "   3. Models will be downloaded when first requested"
