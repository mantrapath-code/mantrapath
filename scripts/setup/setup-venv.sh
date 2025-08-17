#!/bin/bash

# MantraPath Unified Virtual Environment Setup
# This script creates and manages a single virtual environment for the entire project

set -e  # Exit on any error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/venv"
PYTHON_VERSION="3.11"

echo "🐍 MantraPath Unified Virtual Environment Setup"
echo "================================================"
echo "Project Root: $PROJECT_ROOT"
echo "Virtual Environment: $VENV_DIR"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
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

# Function to check if Python version is available
check_python() {
    if command -v python$PYTHON_VERSION >/dev/null 2>&1; then
        print_success "Python $PYTHON_VERSION found: $(which python$PYTHON_VERSION)"
        return 0
    elif command -v python3 >/dev/null 2>&1; then
        local version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [[ "$version" == "$PYTHON_VERSION" ]]; then
            print_success "Python $PYTHON_VERSION found: $(which python3)"
            PYTHON_CMD="python3"
            return 0
        else
            print_warning "Python3 found but version is $version, need $PYTHON_VERSION"
        fi
    fi
    
    print_error "Python $PYTHON_VERSION not found. Please install Python $PYTHON_VERSION"
    echo "On macOS with Homebrew: brew install python@$PYTHON_VERSION"
    exit 1
}

# Function to clean up old virtual environments
cleanup_old_venvs() {
    print_status "Cleaning up old virtual environments..."
    
    # Remove backend specific venv
    if [ -d "$PROJECT_ROOT/backend/venv311" ]; then
        print_warning "Removing old backend venv: $PROJECT_ROOT/backend/venv311"
        rm -rf "$PROJECT_ROOT/backend/venv311"
    fi
    
    # Remove root .venv if it exists
    if [ -d "$PROJECT_ROOT/.venv" ]; then
        print_warning "Removing old root venv: $PROJECT_ROOT/.venv"
        rm -rf "$PROJECT_ROOT/.venv"
    fi
    
    print_success "Old virtual environments cleaned up"
}

# Function to create virtual environment
create_venv() {
    print_status "Creating new virtual environment..."
    
    # Determine Python command
    PYTHON_CMD="python$PYTHON_VERSION"
    if ! command -v $PYTHON_CMD >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    fi
    
    # Create the virtual environment
    $PYTHON_CMD -m venv "$VENV_DIR"
    print_success "Virtual environment created at $VENV_DIR"
}

# Function to activate virtual environment
activate_venv() {
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
}

# Function to upgrade pip
upgrade_pip() {
    print_status "Upgrading pip..."
    pip install --upgrade pip
    print_success "Pip upgraded"
}

# Function to install backend dependencies
install_backend_deps() {
    print_status "Installing backend dependencies..."
    
    if [ -f "$PROJECT_ROOT/backend/requirements.txt" ]; then
        pip install -r "$PROJECT_ROOT/backend/requirements.txt"
        print_success "Backend dependencies installed"
    else
        print_warning "No backend/requirements.txt found"
    fi
}

# Function to install frontend dependencies (if needed for any Python tools)
install_frontend_deps() {
    print_status "Checking frontend dependencies..."
    
    if [ -f "$PROJECT_ROOT/frontend/requirements.txt" ]; then
        pip install -r "$PROJECT_ROOT/frontend/requirements.txt"
        print_success "Frontend Python dependencies installed"
    else
        print_status "No frontend Python dependencies found (this is normal)"
    fi
}

# Function to create activation script
create_activation_script() {
    cat > "$PROJECT_ROOT/activate-venv.sh" << 'EOF'
#!/bin/bash
# Quick activation script for MantraPath virtual environment

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at $VENV_DIR"
    echo "Run ./setup-venv.sh first to create it"
    exit 1
fi

echo "🐍 Activating MantraPath virtual environment..."
source "$VENV_DIR/bin/activate"
echo "✅ Virtual environment activated"
echo "Python: $(which python)"
echo "Pip: $(which pip)"

# Set environment variables
export PYTHONPATH="$PROJECT_ROOT/backend/shared:$PYTHONPATH"
export MANTRAPATH_ROOT="$PROJECT_ROOT"

echo "🔧 Environment variables set:"
echo "   PYTHONPATH includes: $PROJECT_ROOT/backend/shared"
echo "   MANTRAPATH_ROOT: $MANTRAPATH_ROOT"
echo ""
echo "🚀 Ready to run MantraPath backend services!"
echo "To deactivate, run: deactivate"
EOF

    chmod +x "$PROJECT_ROOT/activate-venv.sh"
    print_success "Activation script created: activate-venv.sh"
}

# Function to create development runner script
create_dev_runner() {
    cat > "$PROJECT_ROOT/run-backend.sh" << 'EOF'
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
EOF

    chmod +x "$PROJECT_ROOT/run-backend.sh"
    print_success "Backend runner script created: run-backend.sh"
}

# Function to create requirements consolidation
consolidate_requirements() {
    print_status "Creating unified requirements.txt..."
    
    cat > "$PROJECT_ROOT/requirements.txt" << 'EOF'
# MantraPath Unified Requirements
# This file contains all Python dependencies for the entire project

# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
httpx==0.25.2

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Data Processing
pandas==2.1.3
numpy==1.25.2
scikit-learn==1.3.2

# AI/ML
openai==1.3.5
transformers==4.35.2
torch==2.1.1

# Async & Background Tasks
celery==5.3.4
redis==5.0.1

# Email
python-smtp==0.1.0

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
flake8==6.1.0

# Utilities
python-dotenv==1.0.0
pydantic==2.5.0
python-dateutil==2.8.2
requests==2.31.0
EOF

    print_success "Unified requirements.txt created"
}

# Main execution
main() {
    echo "Starting unified virtual environment setup..."
    
    # Check if we should clean up
    if [ "$1" = "--clean" ] || [ "$1" = "-c" ]; then
        cleanup_old_venvs
    fi
    
    # Check Python
    check_python
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        create_venv
    else
        print_status "Virtual environment already exists at $VENV_DIR"
    fi
    
    # Activate and upgrade
    activate_venv
    upgrade_pip
    
    # Install dependencies
    install_backend_deps
    install_frontend_deps
    
    # Create helper scripts
    create_activation_script
    create_dev_runner
    consolidate_requirements
    
    echo ""
    print_success "🎉 Unified virtual environment setup complete!"
    echo ""
    echo "📝 Quick Start Guide:"
    echo "   1. Activate environment: source ./activate-venv.sh"
    echo "   2. Start backend:        ./run-backend.sh"
    echo "   3. Start frontend:       cd frontend && npm run dev"
    echo ""
    echo "🔧 Available Scripts:"
    echo "   ./setup-venv.sh         - Setup/recreate virtual environment"
    echo "   ./activate-venv.sh      - Activate virtual environment"
    echo "   ./run-backend.sh        - Run backend services"
    echo "   ./run-backend.sh auth   - Run only auth service"
    echo "   ./run-backend.sh gateway - Run only API gateway"
    echo ""
    echo "🐍 Virtual Environment: $VENV_DIR"
    echo "📦 Python: $(which python)"
    echo ""
}

# Parse command line arguments
case "$1" in
    --help|-h)
        echo "MantraPath Unified Virtual Environment Setup"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --clean, -c    Clean up old virtual environments"
        echo "  --help, -h     Show this help message"
        echo ""
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
