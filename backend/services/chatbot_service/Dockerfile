FROM python:3.11-slim

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy minimal requirements
COPY services/chatbot_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules to make them importable
COPY shared /app/shared

# Copy the service files directly to the app directory
COPY services/chatbot_service /app/

# Add the app directory to Python path
ENV PYTHONPATH=/app

EXPOSE 8004

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://chatbot-service:8004/health || exit 1

# Production chatbot service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]