# syntax=docker/dockerfile:1.6
FROM python:3.11-slim

WORKDIR /app

# System deps kept minimal for audio I/O; avoid heavy toolchains unless required at runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Runtime audio deps
    ffmpeg \
    sox \
    libsox-fmt-all \
    libsndfile1 \
    libportaudio2 \
    libasound2 \
    # Build toolchain for packages without wheels (arm64/amd64)
    build-essential \
    gcc \
    g++ \
    make \
    pkg-config \
    git \
    # Numpy/numba openmp runtime
    libgomp1 \
    # Rust toolchain for sudachipy and others
    cargo \
    rustc \
    # Optional: phonemizer/espeak for TTS backends
    espeak-ng \
    espeak-ng-data \
    libespeak-ng1 \
    festival \
    # Utilities
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV PIP_DEFAULT_TIMEOUT=120 PIP_DISABLE_PIP_VERSION_CHECK=1

# Install Python deps first for better caching
COPY services/models_service/requirements.txt ./requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip setuptools wheel setuptools-rust && \
    pip install -r requirements.txt

# Copy application code and shared
COPY services/models_service/ ./
COPY shared/ ./shared/

# Prepare runtime
RUN chmod +x ./start_simple.sh || true && \
    mkdir -p models cache logs

ENV PYTHONPATH=/app \
    MODELS_DIR=/app/models \
    CACHE_DIR=/app/cache \
    LOGS_DIR=/app/logs

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://models-service:8080/health || exit 1

CMD ["./start_simple.sh"]
