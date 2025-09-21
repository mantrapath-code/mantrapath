FROM python:3.11-slim

WORKDIR /app

# Copy service-specific requirements first
COPY services/chatbot_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules to make them importable
COPY shared /app/shared

# Copy the service files directly to the app directory
COPY services/chatbot_service /app/

# Add the app directory to Python path
ENV PYTHONPATH=/app

EXPOSE 8004

# Production chatbot service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
