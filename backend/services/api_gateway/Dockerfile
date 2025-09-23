# MantraPath API Gateway Dockerfile (V3 Enhanced)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for V3 enhanced features
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    build-essential \
    libffi-dev \
    libssl-dev \
    libsqlite3-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy service-specific requirements first for better caching
COPY services/api_gateway/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/src /app/config /app/logs /app/cache /app/models

# Copy source code (service-only)
COPY services/api_gateway/src/ ./src/
COPY services/api_gateway/config/ ./config/

# Copy shared modules (required for authentication)
COPY shared/ ./shared/

# Copy required global config files from backend/config
COPY config/voice_config.yaml ./config/
COPY config/cultural_config.yaml ./config/
COPY config/performance_config.yaml ./config/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose ports (main + websocket + metrics)
EXPOSE 8000 8001 9090

# Health check for V3 enhanced features
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:8000/api/v3/health/enhanced || exit 1

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    GATEWAY_VERSION=v3_enhanced \
    GATEWAY_PORT=8000 \
    WEBSOCKET_PORT=8001 \
    METRICS_PORT=9090

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--access-log"]