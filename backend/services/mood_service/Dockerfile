FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy service-specific requirements first
COPY services/mood_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules to make them importable
COPY shared /app/shared

# Copy the achievements engine for proper import
COPY services/achievements_engine.py /app/achievements_engine.py

# Copy the service files directly to the app directory
COPY services/mood_service /app/

# Add the app directory to Python path
ENV PYTHONPATH=/app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8003

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]