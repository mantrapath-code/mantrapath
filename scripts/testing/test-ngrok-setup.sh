#!/bin/bash

# MantraPath ngrok Setup Test Script
# This script validates the ngrok setup and provides guidance

echo "🔧 MantraPath ngrok Setup Validation"
echo "===================================="

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok is not installed or not in PATH"
    echo "   Please install ngrok: https://ngrok.com/download"
    exit 1
fi

echo "✅ ngrok is installed"

# Check ngrok version
NGROK_VERSION=$(ngrok version)
echo "📦 $NGROK_VERSION"

# Check if auth token is configured
echo ""
echo "🔑 Checking ngrok authentication..."

# Test ngrok config
if ngrok config check &> /dev/null; then
    echo "✅ ngrok configuration is valid"
else
    echo "⚠️  ngrok configuration has issues"
fi

# Check if API Gateway is running
echo ""
echo "🚪 Checking API Gateway status..."
if curl -s -f http://localhost:8000/health &> /dev/null; then
    echo "✅ API Gateway is running on port 8000"
    
    # Test a quick tunnel (for 10 seconds)
    echo ""
    echo "🧪 Testing ngrok tunnel (10 seconds)..."
    timeout 10s ngrok http 8000 --log stdout &> /tmp/ngrok-test.log &
    NGROK_PID=$!
    
    # Wait a bit for ngrok to start
    sleep 3
    
    # Check if ngrok is running
    if ps -p $NGROK_PID > /dev/null 2>&1; then
        echo "✅ ngrok tunnel test successful"
        
        # Try to get the tunnel URL from ngrok API
        if command -v jq &> /dev/null; then
            TUNNEL_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url // empty' 2>/dev/null)
            if [ ! -z "$TUNNEL_URL" ]; then
                echo "🌐 Test tunnel URL: $TUNNEL_URL"
                echo "🧪 Testing endpoint: $TUNNEL_URL/health"
                if curl -s -f "$TUNNEL_URL/health" &> /dev/null; then
                    echo "✅ External access test successful!"
                else
                    echo "⚠️  External access test failed (this might be due to auth requirements)"
                fi
            fi
        fi
        
        # Clean up
        kill $NGROK_PID 2>/dev/null
    else
        echo "❌ ngrok tunnel test failed"
        echo "   Check if auth token is configured:"
        echo "   ngrok config add-authtoken <your-token>"
    fi
    
else
    echo "❌ API Gateway is not running on port 8000"
    echo "   Start the API Gateway first:"
    echo "   cd backend && docker-compose up api-gateway"
fi

echo ""
echo "📋 Next Steps:"
echo "1. If auth token is missing, get it from: https://dashboard.ngrok.com/get-started/your-authtoken"
echo "2. Configure it: ngrok config add-authtoken <your-token>"
echo "3. Start API Gateway: cd backend && docker-compose up -d api-gateway"
echo "4. Run the full setup: ./start-ngrok.sh"

echo ""
echo "🔗 Useful Commands:"
echo "   - Check ngrok status: curl http://localhost:4040/api/tunnels"
echo "   - View ngrok dashboard: http://localhost:4040"
echo "   - Test API Gateway: curl http://localhost:8000/health"
