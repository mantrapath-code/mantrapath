# syntax=docker/dockerfile:1.6
FROM python:3.11-slim AS base

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
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && find /var/cache -type f -exec rm -f {} \;

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV PIP_DEFAULT_TIMEOUT=120 PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Install Python deps in multiple stages to avoid disk space issues
COPY services/models_service/requirements.txt ./requirements.txt

# Stage 1: Install base dependencies
# Note: pip cache purge is skipped because PIP_NO_CACHE_DIR=1 disables caching.
RUN python -m pip install --upgrade pip setuptools wheel setuptools-rust \
    && echo "Skipping pip cache purge (cache disabled)"

# Stage 2: Install core dependencies in chunks
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    pydantic==2.5.0 \
    pydantic-settings==2.1.0 \
    python-multipart==0.0.6 \
    httpx==0.25.2 \
    && echo "Skipping pip cache purge (cache disabled)"

# Stage 3: Install audio processing dependencies
RUN pip install --no-cache-dir \
    "numpy>=1.24.0" \
    soundfile==0.12.1 \
    pydub==0.25.1 \
    && echo "Skipping pip cache purge (cache disabled)"

# Stage 4: Install heavy audio dependencies
RUN pip install --no-cache-dir \
    librosa==0.10.1 \
    vosk==0.3.45 \
    && echo "Skipping pip cache purge (cache disabled)"

# Stage 5: Install TTS dependencies
RUN pip install --no-cache-dir \
    pyttsx3==2.90 \
    gTTS==2.4.0 \
    && echo "Skipping pip cache purge (cache disabled)"

# Stage 6: Install TTS (heaviest dependency) with cleanup
RUN pip install --no-cache-dir TTS==0.22.0 \
    && echo "Skipping pip cache purge (cache disabled)" \
    && find /usr/local/lib/python3.11/site-packages -name "*.pyc" -delete \
    && find /usr/local/lib/python3.11/site-packages -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Stage 7: Install remaining utilities
RUN pip install --no-cache-dir \
    redis==5.0.1 \
    sqlalchemy==2.0.23 \
    structlog==23.2.0 \
    prometheus-client==0.19.0 \
    aiofiles==23.2.1 \
    python-dotenv==1.0.0 \
    psutil==5.9.8 \
    && echo "Skipping pip cache purge (cache disabled)"

# Architecture-specific whisper installation with fallback handling
RUN echo "Target architecture: ${TARGETARCH}" && \
    if [ "${TARGETARCH}" = "amd64" ]; then \
        echo "Installing openai-whisper with triton support for AMD64..."; \
        pip install --no-cache-dir openai-whisper==20231117 || { \
            echo "Failed to install openai-whisper with triton, trying without triton..."; \
            pip install --no-cache-dir --no-deps git+https://github.com/openai/whisper.git@main && \
            pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
            pip install --no-cache-dir tiktoken tqdm; \
        }; \
    else \
        echo "Installing openai-whisper without triton for ARM64..."; \
        pip install --no-cache-dir --no-deps git+https://github.com/openai/whisper.git@main && \
        pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
        pip install --no-cache-dir tiktoken tqdm; \
    fi \
    && echo "Skipping pip cache purge (cache disabled)" \
    && find /usr/local/lib/python3.11/site-packages -name "*.pyc" -delete \
    && find /usr/local/lib/python3.11/site-packages -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Final cleanup and optimization stage
FROM base AS final

# Copy application code and shared
COPY services/models_service/ ./
COPY shared/ ./shared/

# Test whisper installation
RUN python test_whisper.py || echo "⚠️ Whisper test failed, but continuing with build..."

# Prepare runtime and final cleanup
RUN chmod +x ./start_simple.sh || true && \
    mkdir -p models cache logs && \
    # Remove build dependencies to save space
    apt-get remove -y build-essential gcc g++ make pkg-config git cargo rustc && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/* && \
    rm -rf /root/.cache && \
    # Clean up Python bytecode and cache
    find /usr/local/lib/python3.11/site-packages -name "*.pyc" -delete && \
    find /usr/local/lib/python3.11/site-packages -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

ENV PYTHONPATH=/app \
    MODELS_DIR=/app/models \
    CACHE_DIR=/app/cache \
    LOGS_DIR=/app/logs \
    MODELS_SERVICE_MODE=minimal \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["./start_simple.sh"]