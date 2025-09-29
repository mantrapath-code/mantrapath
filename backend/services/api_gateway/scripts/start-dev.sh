#!/bin/bash

# MantraPath API Gateway - Development Start Script

set -e

echo "🚀 Starting MantraPath API Gateway Development Environment..."

# Resolve a Python 3 interpreter (>=3.11)
PYTHON_CMD=""
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Python 3.11+ interpreter not found (python3.11 or python3 missing)"; exit 1; fi

PY_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQ_MAJOR=3
REQ_MINOR=11
MAJOR=${PY_VERSION%%.*}
MINOR=${PY_VERSION##*.}
if [ "$MAJOR" -lt $REQ_MAJOR ] || { [ "$MAJOR" -eq $REQ_MAJOR ] && [ "$MINOR" -lt $REQ_MINOR ]; }; then
    echo "❌ Python >=3.11 required, found $PY_VERSION"; exit 1; fi
echo "✅ Using Python $PY_VERSION ($PYTHON_CMD)"

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not found"
    exit 1
fi

VENV_DIR="venv"
# Create virtual environment if it doesn't exist (idempotent)
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment (via $PYTHON_CMD -m venv $VENV_DIR)..."
    $PYTHON_CMD -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$VENV_DIR"/bin/activate

# Install dependencies
echo "📚 Ensuring pip & installing dependencies..."
python -m ensurepip --upgrade >/dev/null 2>&1 || true
python -m pip install --upgrade pip >/dev/null 2>&1 || true
python -m pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment configuration..."
    if [ -f config/.env.example ]; then
        cp config/.env.example .env
        echo "✏️ Please edit .env file with your configuration"
    else
        cat > .env <<'EOF'
# Auto-generated minimal .env (no config/.env.example present)
APP_NAME=mantrapath_api_gateway
LOG_LEVEL=info
REDIS_URL=\${REDIS_URL:-redis://redis:6379/0}
JWT_AUDIENCE=mantrapath
JWT_ISSUER=mantrapath
EOF
        echo "📝 Generated minimal .env (edit as needed)"
    fi
fi

# Check if Redis is running
echo "🔍 Checking Redis connection..."
if ! redis-cli ping &> /dev/null; then
    # If ping failed, check if something is already listening on 6379
    if ss -ltn 2>/dev/null | grep -q ':6379'; then
        echo "ℹ️ redis-cli ping failed but port 6379 is in use; assuming external Redis instance."
    else
        echo "⚠️ Redis not reachable. Starting ephemeral Docker Redis..."
        if docker ps --format '{{.Names}}' | grep -q '^redis-gateway$'; then
            echo "ℹ️ redis-gateway container exists but not responding; restarting..."
            docker restart redis-gateway || true
        else
            docker run -d --name redis-gateway -p 6379:6379 redis:7-alpine || true
        fi
        echo "⏳ Waiting for Redis to start..."
        sleep 3
    fi
fi

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

# Start the gateway
GATEWAY_HOST=\${GATEWAY_HOST:-localhost}
echo "🌟 Starting API Gateway..."
echo "📍 Gateway will be available at: http://\$GATEWAY_HOST:8000"
echo "📋 Health check: http://\$GATEWAY_HOST:8000/health"
echo "📊 Detailed health: http://\$GATEWAY_HOST:8000/health/detailed"
echo "📈 Metrics: http://\$GATEWAY_HOST:8000/metrics"
echo ""

python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
