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
    # Coqui TTS dependencies
    libsndfile1-dev \
    portaudio19-dev \
    libportaudio2 \
    # Build tools
    gcc \
    g++ \
    cmake \
    pkg-config \
    make \
    # Python development headers
    python3-dev \
    # Rust compiler for some dependencies
    rustc \
    cargo \
    # Other utilities
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY services/models_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY services/models_service/ ./
COPY shared/ ./shared/

# Ensure startup scripts are executable
RUN chmod +x ./start_simple.sh ./start_full.sh || true

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
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run with full startup (loads Phi-3 model)
CMD ["./start_full.sh"]
