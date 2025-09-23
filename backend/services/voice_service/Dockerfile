FROM python:3.11-slim

WORKDIR /app

# Install minimal system dependencies (avoid heavy audio toolchain for minimal image)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy minimal requirements
COPY services/voice_service/requirements.txt ./requirements.txt

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and shared
COPY services/voice_service/ .
COPY shared/ ./shared/

# Create logs directory
RUN mkdir -p /app/logs

ENV PYTHONPATH=/app
ENV VOICE_SERVICE_PORT=8011
ENV LOG_LEVEL=INFO

EXPOSE 8011

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8011/health || exit 1

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8011", "--reload"]
