FROM python:3.11-slim

# Set wo# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8013/health || exit 1ng directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY services/ai_context_store/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules from the backend directory
COPY shared/ ./shared/

# Copy AI Context Store service files directly to /app
COPY services/ai_context_store/ ./

# Create necessary directories
RUN mkdir -p logs data

# Set Python path to include /app and /app/shared
ENV PYTHONPATH=/app:/app/shared:/app/models:/app/services:/app/api

# Expose port
EXPOSE 8013

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 CMD curl -f http://localhost:8013/health || exit 1

# Run the application
CMD ["python", "run.py"]
