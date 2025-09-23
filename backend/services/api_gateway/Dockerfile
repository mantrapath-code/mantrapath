# MantraPath API Gateway Dockerfile (Minimal)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy minimal requirements first for better caching
COPY services/api_gateway/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/src /app/config /app/logs /app/cache

# Copy shared modules to make them importable
COPY shared /app/shared

# Copy source code (service-only)
COPY services/api_gateway/src/ ./src/
COPY services/api_gateway/config/ ./config/

# Set Python path to include app directory
ENV PYTHONPATH="/app"

# Expose API Gateway port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the API Gateway
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]