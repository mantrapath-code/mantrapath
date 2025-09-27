FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy ultra minimal requirements first
COPY services/translation_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules to make them importable
COPY shared /app/shared

# Copy the service files directly to the app directory
COPY services/translation_service /app/

# Add the app directory to Python path
ENV PYTHONPATH=/app

# Create directories for data and cache
RUN mkdir -p data/models data/glossaries data/cache

# Expose port
EXPOSE 8010

# Health check (avoid 'localhost' to align with service-discovery style)
# Using the Docker Compose service DNS name so patterns stay consistent across services.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://translation-service:8010/health || exit 1

# Run the service
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010"]