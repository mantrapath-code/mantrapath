FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including libmagic and minimal OpenCV requirements
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libmagic1 \
    libmagic-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    gfortran \
    libblas3 \
    liblapack3 \
    && rm -rf /var/lib/apt/lists/*

# Copy service-specific requirements first
COPY services/media_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules to make them importable
COPY shared /app/shared

# Copy the service files directly to the app directory
COPY services/media_service /app/

# Add the app directory to Python path
ENV PYTHONPATH=/app

EXPOSE 8009

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8009"]
