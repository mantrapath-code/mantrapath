FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy service-specific requirements first
COPY services/translation_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir grpcio grpcio-tools

# Copy shared modules to make them importable
COPY shared /app/shared

# Copy the service files directly to the app directory
COPY services/translation_service /app/

# Add the app directory to Python path
ENV PYTHONPATH=/app:/app/shared/protos

# Create directories for data and cache
RUN mkdir -p data/models data/glossaries data/cache

# Compile gRPC protos
RUN python -m grpc_tools.protoc \
    -I /app/shared/protos \
    --python_out=/app/shared/protos \
    --grpc_python_out=/app/shared/protos \
    /app/shared/protos/translation.proto

# Expose port
EXPOSE 8010 9010

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8010/health || exit 1

# Run the service
RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]
