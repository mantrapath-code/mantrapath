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
COPY services/mood_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules to make them importable
COPY shared /app/shared

# Copy the service files directly to the app directory
COPY services/mood_service /app/

# Add the app directory to Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://mood-service:8003/health || exit 1

# Command to run the service
CMD ["python", "main.py"]