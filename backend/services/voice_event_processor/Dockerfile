FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    # Audio processing
    ffmpeg \
    sox \
    libsox-fmt-all \
    # Audio libraries
    libsndfile1-dev \
    portaudio19-dev \
    libportaudio2 \
    libasound2-dev \
    # General utilities
    gcc \
    g++ \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY services/voice_event_processor/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY shared/ ./shared/

# Copy the service code
COPY services/voice_event_processor/ .

# Create logs directory
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV VOICE_EVENT_PROCESSOR_PORT=8015
ENV LOG_LEVEL=INFO

# Expose the port
EXPOSE 8015

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8015/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8015", "--reload"]
