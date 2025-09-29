FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for image processing
RUN apt-get update && apt-get install -y \
    curl \
    libmagic1 \
    libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    && rm -rf /var/lib/apt/lists/* 2>/dev/null || \
    apt-get update && apt-get install -y \
    curl \
    libmagic1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy minimal requirements
COPY services/media_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules to make them importable
COPY shared /app/shared

# Copy the service files directly to the app directory
COPY services/media_service /app/

# Add the app directory to Python path
ENV PYTHONPATH=/app

# Create media storage directory
RUN mkdir -p /app/uploads /app/media

EXPOSE 8021

# Health check
# Health check aligned to standardized port 8021
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://media-service:8021/health || exit 1

# Production media service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8021"]