# syntax=docker/dockerfile:1.6
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for audio processing and TTS
RUN apt-get update && apt-get install -y --no-install-recommends \
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

# Install Python dependencies (with retry and cache)
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV PIP_DEFAULT_TIMEOUT=120 \
        PIP_DISABLE_PIP_VERSION_CHECK=1
COPY services/models_service/requirements.txt ./requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
        set -euo pipefail; \
        for i in {1..3}; do \
            echo "[models_service] pip install attempt $i"; \
            if python -m pip install --upgrade pip && pip install -r requirements.txt; then \
                break; \
            fi; \
            if [[ $i -eq 3 ]]; then \
                echo "[models_service] pip install failed after $i attempts" >&2; exit 1; \
            fi; \
            sleep $((i*5)); \
        done

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
