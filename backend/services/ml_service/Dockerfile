FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy minimal requirements first for better caching
COPY services/ml_service/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download required NLTK data to avoid runtime network calls
RUN python - <<'PY'
import nltk
packages = [
  'vader_lexicon',
  'punkt',
  'stopwords',
  'averaged_perceptron_tagger',
  'wordnet'
]
for p in packages:
  try:
    nltk.download(p)
  except Exception as e:
    print(f"Warning: failed to download {p}: {e}")
PY

# Copy shared modules
COPY shared /app/shared

# Copy application code
COPY services/ml_service /app/

# Expose the port
EXPOSE 8008

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://ml-service:8008/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8008", "--reload"]
