#!/bin/bash

# Script to automatically update ngrok URLs in frontend environment

echo "🔧 Updating ngrok URLs in frontend environment..."

# Get ngrok tunnel information
NGROK_API_RESPONSE=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null)

if [ $? -ne 0 ] || [ -z "$NGROK_API_RESPONSE" ]; then
    echo "❌ Could not connect to ngrok API. Make sure ngrok is running."
    exit 1
fi

if command -v jq &> /dev/null; then
    # Extract URLs using jq
    BACKEND_URL=$(echo "$NGROK_API_RESPONSE" | jq -r '.tunnels[] | select(.config.addr | contains("8000")) | .public_url' | head -1)
    FRONTEND_URL=$(echo "$NGROK_API_RESPONSE" | jq -r '.tunnels[] | select(.config.addr | contains("517")) | .public_url' | head -1)
    
    if [ ! -z "$BACKEND_URL" ] && [ "$BACKEND_URL" != "null" ]; then
        echo "✅ Backend ngrok URL: $BACKEND_URL"
        # Update the environment file
        sed -i '' "s|VITE_NGROK_BACKEND_URL=.*|VITE_NGROK_BACKEND_URL=$BACKEND_URL|" /Users/sachin/Desktop/mantrapath/frontend/.env.development
    fi
    
    if [ ! -z "$FRONTEND_URL" ] && [ "$FRONTEND_URL" != "null" ]; then
        echo "✅ Frontend ngrok URL: $FRONTEND_URL"
        sed -i '' "s|VITE_NGROK_FRONTEND_URL=.*|VITE_NGROK_FRONTEND_URL=$FRONTEND_URL|" /Users/sachin/Desktop/mantrapath/frontend/.env.development
    fi
    
    echo ""
    echo "📋 Updated environment file:"
    cat /Users/sachin/Desktop/mantrapath/frontend/.env.development | grep VITE_NGROK
    
    echo ""
    echo "🔄 Please restart the frontend development server to apply changes:"
    echo "   cd frontend && npm run dev -- --host 0.0.0.0"
    
else
    echo "⚠️  jq not found. Please install jq for automatic URL extraction:"
    echo "   brew install jq"
    echo ""
    echo "📋 Current ngrok tunnels:"
    curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*"'
fi
