#!/bin/bash
# Unified backend runner for MantraPath

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/venv"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found. Run ./setup-venv.sh first"
    exit 1
fi

echo -e "${BLUE}🚀 Starting MantraPath Backend Services${NC}"
echo "======================================"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Set environment variables
export PYTHONPATH="$PROJECT_ROOT/backend/shared:$PYTHONPATH"
export DATABASE_URL="sqlite:///$PROJECT_ROOT/backend/mantrapath.db"
export JWT_SECRET_KEY="dev-secret-key-change-in-production"

# Create database directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/backend/database"

echo -e "${GREEN}Environment Setup:${NC}"
echo "  Python: $(which python)"
echo "  PYTHONPATH: $PYTHONPATH"
echo "  DATABASE_URL: $DATABASE_URL"
echo ""

# Check if user wants to run specific service or all
if [ "$1" = "auth" ]; then
    echo "🔐 Starting Auth Service only..."
    cd "$PROJECT_ROOT/backend"
    python -m services.auth_service.main
elif [ "$1" = "gateway" ]; then
    echo "🌐 Starting API Gateway only..."
    cd "$PROJECT_ROOT/backend"
    python -m services.api_gateway.main
elif [ "$1" = "all" ] || [ -z "$1" ]; then
    echo "🌐 Starting all essential services..."
    echo "This will start services in the background..."
    
    cd "$PROJECT_ROOT/backend"
    
    # Start API Gateway
    echo "Starting API Gateway on port 8000..."
    python -m services.api_gateway.main &
    GATEWAY_PID=$!
    
    # Start Auth Service
    echo "Starting Auth Service on port 8001..."
    python -m services.auth_service.main &
    AUTH_PID=$!
    
    # Start Mood Service
    echo "Starting Mood Service on port 8003..."
    python -m services.mood_service.main &
    MOOD_PID=$!
    
    echo ""
    echo -e "${GREEN}✅ Services started!${NC}"
    echo "📍 Endpoints:"
    echo "   🌐 API Gateway: http://localhost:8000"
    echo "   🔐 Auth Service: http://localhost:8001"
    echo "   😊 Mood Service: http://localhost:8003"
    echo ""
    echo "Press Ctrl+C to stop all services..."
    
    # Wait for interrupt
    trap 'echo "Stopping services..."; kill $GATEWAY_PID $AUTH_PID $MOOD_PID 2>/dev/null; exit' INT
    wait
else
    echo "Usage: $0 [auth|gateway|all]"
    echo "  auth    - Start only auth service"
    echo "  gateway - Start only API gateway"
    echo "  all     - Start all services (default)"
fi
