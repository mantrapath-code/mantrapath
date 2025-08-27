#!/bin/bash

# MantraPath Quick Start with ngrok
# A simplified script to start everything including ngrok tunnels

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "🚀 MantraPath Quick Start with ngrok"
echo "====================================="

# Check if ngrok is available
NGROK_AVAILABLE=false
if command -v ngrok &> /dev/null && ngrok config check &> /dev/null; then
    NGROK_AVAILABLE=true
    print_success "ngrok is available and configured"
else
    print_warning "ngrok is not available or not configured"
    echo "   Install ngrok: https://ngrok.com/download"
    echo "   Configure auth: ngrok config add-authtoken <token>"
fi

echo ""
echo "Select startup mode:"
echo "1) 🖥️  Local Development (localhost only)"
echo "2) 🌐 Public Access (with ngrok tunnels)"
echo ""
read -p "Enter your choice (1-2): " choice

case $choice in
    1)
        print_info "Starting in local development mode..."
        cd "$PROJECT_ROOT"
        ./start.sh
        ;;
    2)
        if [ "$NGROK_AVAILABLE" = false ]; then
            echo "❌ ngrok is not available. Please install and configure it first."
            exit 1
        fi
        
        print_info "Starting in public access mode with ngrok..."
        
        # Start services in background
        cd "$PROJECT_ROOT"
        print_info "Starting backend services..."
        ./start.sh backend &
        BACKEND_PID=$!
        
        # Wait for backend to start
        print_info "Waiting for backend to start..."
        sleep 10
        
        # Start frontend in background
        print_info "Starting frontend..."
        cd "$PROJECT_ROOT/frontend"
        npm run dev -- --host 0.0.0.0 &
        FRONTEND_PID=$!
        
        # Wait for frontend to start
        print_info "Waiting for frontend to start..."
        sleep 5
        
        # Start ngrok
        print_info "Starting ngrok tunnels..."
        cd "$PROJECT_ROOT"
        ./scripts/start-ngrok.sh &
        NGROK_PID=$!
        
        echo ""
        print_success "All services started!"
        echo ""
        echo "📋 Process IDs:"
        echo "   Backend: $BACKEND_PID"
        echo "   Frontend: $FRONTEND_PID"
        echo "   ngrok: $NGROK_PID"
        echo ""
        echo "🛑 To stop all services:"
        echo "   kill $BACKEND_PID $FRONTEND_PID $NGROK_PID"
        echo "   # or"
        echo "   pkill -f 'npm run dev'"
        echo "   pkill -f ngrok"
        echo ""
        echo "🌐 View ngrok dashboard: http://localhost:4040"
        
        # Wait for user to stop
        read -p "Press Enter to stop all services..."
        kill $BACKEND_PID $FRONTEND_PID $NGROK_PID 2>/dev/null
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
