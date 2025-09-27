FROM python:3.11-slim

WORKDIR /app

# Minimal system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install minimal Python deps
COPY services/ai_context_store/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules and service code
COPY shared ./shared
COPY services/ai_context_store ./

# Runtime env
ENV PYTHONPATH=/app:/app/shared:/app/models:/app/services:/app/api
EXPOSE 8013

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://ai-context-store:8013/health || exit 1

CMD ["python", "run.py"]