FROM python:3.11-slim

WORKDIR /app

# Install system build dependencies (Debian-based)
# 'postgresql-dev' is an Alpine package name; on Debian/Ubuntu use libpq-dev
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY shared/ ./shared/

# Default command (will be overridden by specific services)
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]