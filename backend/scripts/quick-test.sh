#!/bin/bash

# Quick test script for MantraPath services
echo "🧪 Quick MantraPath Service Test"
echo "================================"

# Test core services
echo "🔍 Testing core services..."

services=(
    "postgres:5432"
    "redis:6379"
    "api-gateway:8000"
    "auth-service:8001"
    "chatbot-service:8004"
    "phi3-agent:8010"
)

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    
    if curl -s -f "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "✅ $name (port $port) - healthy"
    else
        echo "❌ $name (port $port) - not responding"
    fi
done

echo ""
echo "🤖 Testing chatbot status..."
if curl -s -f "http://localhost:8004/api/chatbot/status" > /dev/null 2>&1; then
    echo "✅ Chatbot service is responding"
    
    # Get detailed status
    status=$(curl -s "http://localhost:8004/api/chatbot/status" | python3 -m json.tool 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "📊 Chatbot Status:"
        echo "$status" | grep -E "(phi3_available|openai_available|version)" | sed 's/^/   /'
    fi
else
    echo "❌ Chatbot service not responding"
fi

echo ""
echo "🧠 Testing Phi-3 agent..."
if curl -s -f "http://localhost:8010/health" > /dev/null 2>&1; then
    echo "✅ Phi-3 agent is healthy"
else
    echo "⚠️  Phi-3 agent not responding (may still be loading)"
    echo "   Check status: docker-compose logs phi3-agent"
fi

echo ""
echo "📋 Service URLs:"
echo "   • API Gateway: http://localhost:8000"
echo "   • Chatbot Service: http://localhost:8004"
echo "   • Phi-3 Agent: http://localhost:8010"
echo "   • Frontend: http://localhost:5173 (start separately)"

echo ""
echo "🔧 Quick Commands:"
echo "   • View logs: docker-compose logs -f [service-name]"
echo "   • Restart service: docker-compose restart [service-name]"
echo "   • Full test: python scripts/test-chatbot.py"