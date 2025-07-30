FROM python:3.11-slim

WORKDIR /app

# Copy service-specific requirements first
COPY services/community_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules to make them importable
COPY shared /app/shared

# Copy the service files directly to the app directory
COPY services/community_service /app/

# Add the app directory to Python path
ENV PYTHONPATH=/app

EXPOSE 8006

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8006"]
