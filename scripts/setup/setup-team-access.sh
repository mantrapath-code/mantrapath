#!/bin/bash

# 🚀 MantraPath Team Setup Script
# This script helps team members quickly set up ngrok for external access

set -e

echo "🚀 MantraPath Team Setup"
echo "========================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo -e "${RED}❌ ngrok is not installed!${NC}"
    echo ""
    echo "Please install ngrok first:"
    echo "  macOS: brew install ngrok/ngrok/ngrok"
    echo "  Linux: https://ngrok.com/download"
    echo "  Windows: https://ngrok.com/download"
    exit 1
fi

echo -e "${GREEN}✅ ngrok is installed${NC}"

# Check if auth token is configured
if ngrok config check 2>&1 | grep -q "authentication"; then
    echo -e "${YELLOW}⚠️ ngrok auth token is not configured${NC}"
    echo ""
    echo "To set up ngrok authentication:"
    echo -e "1. Sign up at: ${BLUE}https://dashboard.ngrok.com/signup${NC}"
    echo -e "2. Get your token at: ${BLUE}https://dashboard.ngrok.com/get-started/your-authtoken${NC}"
    echo -e "3. Run: ${BLUE}ngrok config add-authtoken YOUR_TOKEN_HERE${NC}"
    echo ""
    read -p "Press Enter after configuring your auth token..."
    
    # Check again
    if ngrok config check 2>&1 | grep -q "authentication"; then
        echo -e "${RED}❌ Auth token still not configured${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ ngrok auth token is configured${NC}"

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"

# Check if the secure setup is running
if ! curl -s -f http://localhost:8000/health &> /dev/null; then
    echo -e "${YELLOW}⚠️ MantraPath backend is not running${NC}"
    echo ""
    echo "Starting MantraPath backend services..."
    cd backend && docker-compose -f docker-compose.secure.yml up -d
    echo ""
    echo "Waiting for services to start..."
    sleep 10
    
    # Check again
    if ! curl -s -f http://localhost:8000/health &> /dev/null; then
        echo -e "${RED}❌ Failed to start backend services${NC}"
        echo "Please check Docker logs: docker-compose -f backend/docker-compose.secure.yml logs"
        exit 1
    fi
fi

echo -e "${GREEN}✅ MantraPath backend is running${NC}"

# Start ngrok
echo ""
echo -e "${BLUE}🌐 Starting ngrok tunnel...${NC}"
echo ""

# Start ngrok in background and capture the URL
nohup ngrok http 8000 --config ngrok.yml > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!

# Wait for ngrok to start
sleep 3

# Get the public URL
PUBLIC_URL=""
for i in {1..10}; do
    PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url // empty' 2>/dev/null)
    if [ ! -z "$PUBLIC_URL" ] && [ "$PUBLIC_URL" != "null" ]; then
        break
    fi
    sleep 1
done

if [ -z "$PUBLIC_URL" ] || [ "$PUBLIC_URL" = "null" ]; then
    echo -e "${RED}❌ Failed to get ngrok public URL${NC}"
    kill $NGROK_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✅ ngrok tunnel is active!${NC}"
echo ""
echo "📊 Connection Details:"
echo "====================="
echo -e "🌍 Public URL: ${GREEN}${PUBLIC_URL}${NC}"
echo -e "📊 Dashboard:  ${BLUE}http://localhost:4040${NC}"
echo -e "🏠 Local API:  ${BLUE}http://localhost:8000${NC}"
echo ""

# Test the connection
echo "🧪 Testing connection..."
HEALTH_RESPONSE=$(curl -s "${PUBLIC_URL}/health" || echo "failed")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Public URL is working!${NC}"
else
    echo -e "${YELLOW}⚠️ Public URL test failed, but tunnel is running${NC}"
fi

echo ""
echo "🎯 Quick API Test:"
echo "=================="
echo "# Test health endpoint:"
echo -e "${BLUE}curl ${PUBLIC_URL}/health${NC}"
echo ""
echo "# Login to get token:"
echo -e "${BLUE}curl -X POST ${PUBLIC_URL}/auth/login \\${NC}"
echo -e "${BLUE}  -H \"Content-Type: application/json\" \\${NC}"
echo -e "${BLUE}  -d '{\"email_or_username\": \"sa@gmail.com\", \"password\": \"Dev@#123\"}'${NC}"
echo ""

echo "📚 Documentation:"
echo "================="
echo -e "📖 Full API Guide: ${BLUE}TEAM_ACCESS_GUIDE.md${NC}"
echo -e "🔧 Setup Guide:    ${BLUE}NGROK_SETUP_GUIDE.md${NC}"
echo ""

echo -e "${YELLOW}💡 Share this URL with your team: ${GREEN}${PUBLIC_URL}${NC}"
echo ""
echo "Press Ctrl+C to stop the tunnel..."

# Keep the script running
trap 'echo -e "\n${YELLOW}🛑 Stopping ngrok tunnel...${NC}"; kill $NGROK_PID 2>/dev/null; exit 0' INT

while true; do
    sleep 1
done
