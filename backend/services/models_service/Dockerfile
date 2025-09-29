# syntax=docker/dockerfile:1.6
FROM python:3.11-slim AS base

WORKDIR /app

# Get target architecture for conditional package installation
ARG TARGETARCH
ENV TARGETARCH=${TARGETARCH}

# System deps kept minimal for audio I/O; avoid heavy toolchains unless required at runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    libasound2 \
    libgomp1 \
    build-essential \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* && apt-get clean && find /var/cache -type f -exec rm -f {} \;

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV PIP_DEFAULT_TIMEOUT=120 PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Install Python deps in multiple stages to avoid disk space issues
COPY services/models_service/requirements.txt ./requirements.txt

# Stage 1: Install base dependencies
# Note: pip cache purge is skipped because PIP_NO_CACHE_DIR=1 disables caching.
RUN python -m pip install --upgrade pip setuptools wheel setuptools-rust \
    && echo "Skipping pip cache purge (cache disabled)"

# Single consolidated install (pruned stack)
RUN pip install --no-cache-dir -r requirements.txt \
    && find /usr/local/lib/python3.11/site-packages -name "*.pyc" -delete \
    && find /usr/local/lib/python3.11/site-packages -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Final cleanup and optimization stage
FROM base AS final

# Copy application code and shared
COPY services/models_service/ ./
COPY shared/ ./shared/

# Removed whisper validation (stack no longer uses Whisper)

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