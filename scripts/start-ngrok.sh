#!/bin/bash

# MantraPath ngrok Setup Script
# Starts ngrok tunnels for both backend API and frontend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    print_error "ngrok is not installed or not in PATH"
    echo ""
    echo "To install ngrok:"
    echo "1. Visit https://ngrok.com/download"
    echo "2. Or use homebrew: brew install ngrok/ngrok/ngrok"
    echo "3. Sign up for a free account at https://dashboard.ngrok.com/signup"
    echo "4. Get your auth token: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "5. Configure it: ngrok config add-authtoken <your-token>"
    exit 1
fi

print_success "ngrok is installed"

# Check if auth token is configured
if ! ngrok config check &> /dev/null; then
    print_error "ngrok auth token is not configured"
    echo ""
    echo "Please configure your auth token:"
    echo "1. Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "2. Run: ngrok config add-authtoken <your-token>"
    exit 1
fi

print_success "ngrok auth token is configured"

# Default ports
API_PORT=${API_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-5173}

# Check if services are running
print_info "Checking if services are running..."

API_RUNNING=false
FRONTEND_RUNNING=false

if curl -s -f "http://localhost:$API_PORT/health" &> /dev/null; then
    print_success "API Gateway is running on port $API_PORT"
    API_RUNNING=true
else
    print_warning "API Gateway is not running on port $API_PORT"
fi

if curl -s -f "http://localhost:$FRONTEND_PORT" &> /dev/null; then
    print_success "Frontend is running on port $FRONTEND_PORT"
    FRONTEND_RUNNING=true
else
    print_warning "Frontend is not running on port $FRONTEND_PORT"
fi

if [ "$API_RUNNING" = false ] && [ "$FRONTEND_RUNNING" = false ]; then
    print_error "Neither API Gateway nor Frontend is running"
    echo ""
    echo "Please start the services first:"
    echo "  ./start.sh"
    exit 1
fi

# Create ngrok configuration
NGROK_CONFIG="$PROJECT_ROOT/ngrok.yml"

print_info "Creating ngrok configuration..."

cat > "$NGROK_CONFIG" << EOF
version: 2

tunnels:
EOF

if [ "$API_RUNNING" = true ]; then
    cat >> "$NGROK_CONFIG" << EOF
  api:
    proto: http
    addr: $API_PORT
    schemes:
      - https
    inspect: true
EOF
fi

if [ "$FRONTEND_RUNNING" = true ]; then
    cat >> "$NGROK_CONFIG" << EOF
  frontend:
    proto: http
    addr: $FRONTEND_PORT
    schemes:
      - https
    inspect: true
    host_header: "localhost:$FRONTEND_PORT"
EOF
fi

print_success "Created ngrok configuration at $NGROK_CONFIG"

# Start ngrok with the configuration
print_info "Starting ngrok tunnels..."

ngrok start --config="$NGROK_CONFIG" --all --log=stdout &
NGROK_PID=$!

# Wait for ngrok to start
sleep 5

# Check if ngrok is running
if ! ps -p $NGROK_PID > /dev/null 2>&1; then
    print_error "ngrok failed to start"
    exit 1
fi

print_success "ngrok is running (PID: $NGROK_PID)"

# Get tunnel URLs
print_info "Fetching tunnel URLs..."

# Function to get tunnel URLs
get_tunnel_urls() {
    local retries=0
    local max_retries=10
    
    while [ $retries -lt $max_retries ]; do
        if command -v jq &> /dev/null; then
            # Using jq for better parsing
            TUNNELS_JSON=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null)
            if [ $? -eq 0 ] && [ ! -z "$TUNNELS_JSON" ]; then
                if [ "$API_RUNNING" = true ]; then
                    API_URL=$(echo "$TUNNELS_JSON" | jq -r '.tunnels[] | select(.config.addr | contains("'$API_PORT'")) | .public_url' | head -1)
                    if [ ! -z "$API_URL" ] && [ "$API_URL" != "null" ]; then
                        print_success "API Gateway tunnel: $API_URL"
                        echo "🔗 API Health Check: $API_URL/health"
                    fi
                fi
                
                if [ "$FRONTEND_RUNNING" = true ]; then
                    FRONTEND_URL=$(echo "$TUNNELS_JSON" | jq -r '.tunnels[] | select(.config.addr | contains("'$FRONTEND_PORT'")) | .public_url' | head -1)
                    if [ ! -z "$FRONTEND_URL" ] && [ "$FRONTEND_URL" != "null" ]; then
                        print_success "Frontend tunnel: $FRONTEND_URL"
                        echo "🌐 Open your app: $FRONTEND_URL"
                    fi
                fi
                break
            fi
        else
            # Fallback without jq
            TUNNELS_RESPONSE=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null)
            if [ $? -eq 0 ] && [ ! -z "$TUNNELS_RESPONSE" ]; then
                print_success "ngrok tunnels are active"
                echo "🌐 View all tunnels at: http://localhost:4040"
                break
            fi
        fi
        
        retries=$((retries + 1))
        print_info "Waiting for tunnels to be ready... ($retries/$max_retries)"
        sleep 2
    done
}

get_tunnel_urls

echo ""
print_info "ngrok Dashboard: http://localhost:4040"
print_info "To stop ngrok: kill $NGROK_PID"

echo ""
echo "📋 Tunnel Information:"
echo "   • ngrok Dashboard: http://localhost:4040"
echo "   • Process ID: $NGROK_PID"
echo "   • Config file: $NGROK_CONFIG"

echo ""
echo "🛑 To stop ngrok:"
echo "   kill $NGROK_PID"
echo "   # or"
echo "   pkill -f ngrok"

# Keep the script running
echo ""
print_info "ngrok is running in the background. Press Ctrl+C to stop all tunnels."

# Trap to clean up on exit
trap 'kill $NGROK_PID 2>/dev/null; rm -f "$NGROK_CONFIG"; exit' INT TERM

# Wait for the ngrok process
wait $NGROK_PID
