FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for audio processing and TTS
RUN apt-get update && apt-get install -y \
    # Audio processing
    ffmpeg \
    sox \
    libsox-fmt-all \
    # TTS engines
    festival \
    espeak \
    espeak-data \
    libespeak-ng-dev \
    # Build tools
    gcc \
    g++ \
    cmake \
    pkg-config \
    # Other utilities
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create models directory
RUN mkdir -p models cache logs

# Set environment variables
ENV PYTHONPATH=/app
ENV MODELS_DIR=/app/models
ENV CACHE_DIR=/app/cache
ENV LOGS_DIR=/app/logs

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
