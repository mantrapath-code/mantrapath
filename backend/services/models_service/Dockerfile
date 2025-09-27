# syntax=docker/dockerfile:1.6
FROM python:3.11-slim

WORKDIR /app

# Get target architecture for conditional package installation
ARG TARGETARCH
ENV TARGETARCH=${TARGETARCH}

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

# Architecture-specific whisper installation with fallback handling
RUN --mount=type=cache,target=/root/.cache/pip \
    echo "Target architecture: ${TARGETARCH}" && \
    if [ "${TARGETARCH}" = "amd64" ]; then \
        echo "Installing openai-whisper with triton support for AMD64..."; \
        pip install openai-whisper==20231117 || { \
            echo "Failed to install openai-whisper with triton, trying without triton..."; \
            pip install --no-deps git+https://github.com/openai/whisper.git@main && \
            pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
            pip install tiktoken tqdm; \
        }; \
    else \
        echo "Installing openai-whisper without triton for ARM64..."; \
        pip install --no-deps git+https://github.com/openai/whisper.git@main && \
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
        pip install tiktoken tqdm; \
    fi

# Copy application code and shared
COPY services/models_service/ ./
COPY shared/ ./shared/

# Test whisper installation
RUN python test_whisper.py || echo "⚠️ Whisper test failed, but continuing with build..."

# Prepare runtime
RUN chmod +x ./start_simple.sh || true && \
    mkdir -p models cache logs

ENV PYTHONPATH=/app \
    MODELS_DIR=/app/models \
    CACHE_DIR=/app/cache \
    LOGS_DIR=/app/logs \
    MODELS_SERVICE_MODE=minimal

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["./start_simple.sh"]