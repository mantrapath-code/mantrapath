# Voice Service Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app/services/voice_service

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    portaudio19-dev \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first
COPY services/voice_service/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend code to maintain import paths
COPY . /app/

# Create non-root user for security
RUN useradd -m -u 1000 voiceuser && chown -R voiceuser:voiceuser /app
USER voiceuser

# Expose port
EXPOSE 8011

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8011/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8011"]
