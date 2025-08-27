# Media Service Deployment Guide

## Overview

This guide covers deploying the MantraPath Media Service in various environments, from development to production.

## Prerequisites

- Python 3.11+
- PostgreSQL database
- Redis server
- Docker (optional)
- Storage provider access (AWS S3, MinIO, or local filesystem)

## Environment Setup

### 1. Development Environment

```bash
# Clone and navigate to media service
cd /path/to/mantrapath/backend/services/media_service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env file with your configuration

# Create local storage directory
mkdir -p uploads

# Run the service
python main.py
```

### 2. Docker Development

```bash
# Build the image
docker build -t mantrapath-media-service .

# Run with docker-compose (from backend root)
cd ../../
docker-compose up media_service
```

### 3. Production Environment

#### Database Setup
```sql
-- Create media service tables
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Run migrations (when available)
-- alembic upgrade head
```

#### Storage Configuration

**AWS S3 Setup:**
```bash
# Set environment variables
export AWS_S3_BUCKET=mantrapath-media-prod
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY=your_access_key
export AWS_SECRET_KEY=your_secret_key
export PRIMARY_STORAGE_PROVIDER=aws_s3
```

**MinIO Setup:**
```bash
# Start MinIO server
docker run -d \
  --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  -v /data:/data \
  minio/minio server /data --console-address ":9001"

# Configure environment
export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=minioadmin
export MINIO_SECRET_KEY=minioadmin
export PRIMARY_STORAGE_PROVIDER=minio
```

#### Redis Setup
```bash
# Install and start Redis
# Ubuntu/Debian:
sudo apt-get install redis-server
sudo systemctl start redis-server

# macOS:
brew install redis
brew services start redis

# Docker:
docker run -d --name redis -p 6379:6379 redis:alpine
```

## Deployment Options

### 1. Standalone Deployment

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
  python3 \
  python3-pip \
  python3-venv \
  libmagic1 \
  libmagic-dev

# Create application user
sudo useradd -m -s /bin/bash mediaservice
sudo su - mediaservice

# Set up application
git clone https://github.com/your-org/mantrapath.git
cd mantrapath/backend/services/media_service

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production settings

# Create systemd service
sudo tee /etc/systemd/system/media-service.service << EOF
[Unit]
Description=MantraPath Media Service
After=network.target

[Service]
Type=exec
User=mediaservice
Group=mediaservice
WorkingDirectory=/home/mediaservice/mantrapath/backend/services/media_service
Environment=PATH=/home/mediaservice/mantrapath/backend/services/media_service/venv/bin
ExecStart=/home/mediaservice/mantrapath/backend/services/media_service/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8009
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl enable media-service
sudo systemctl start media-service
```

### 2. Docker Deployment

**Dockerfile** (already exists):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libmagic1 \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

EXPOSE 8009

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8009"]
```

**docker-compose.yml** (add to main backend docker-compose):
```yaml
version: '3.8'

services:
  media_service:
    build:
      context: ./services/media_service
      dockerfile: Dockerfile
    ports:
      - "8009:8009"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/mantrapath
      - REDIS_URL=redis://redis:6379
      - PRIMARY_STORAGE_PROVIDER=local
      - LOCAL_STORAGE_PATH=/app/uploads
    volumes:
      - media_uploads:/app/uploads
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

volumes:
  media_uploads:
```

### 3. Kubernetes Deployment

**k8s/deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: media-service
  labels:
    app: media-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: media-service
  template:
    metadata:
      labels:
        app: media-service
    spec:
      containers:
      - name: media-service
        image: mantrapath/media-service:latest
        ports:
        - containerPort: 8009
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: AWS_S3_BUCKET
          valueFrom:
            configMapKeyRef:
              name: media-config
              key: s3-bucket
        - name: PRIMARY_STORAGE_PROVIDER
          value: "aws_s3"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8009
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8009
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: media-service
spec:
  selector:
    app: media-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8009
  type: ClusterIP
```

## Configuration Management

### Environment Variables

**Required:**
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret for JWT token validation
- `PRIMARY_STORAGE_PROVIDER`: Storage provider (local, aws_s3, minio)

**Storage-specific:**
- AWS S3: `AWS_S3_BUCKET`, `AWS_ACCESS_KEY`, `AWS_SECRET_KEY`
- MinIO: `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`
- Local: `LOCAL_STORAGE_PATH`

**Optional:**
- `REDIS_URL`: Redis connection string (default: redis://localhost:6379)
- `MAX_UPLOAD_SIZE`: Maximum file size (default: 500MB)
- `IMAGE_QUALITY_DEFAULT`: Default image quality (default: 85)
- `CDN_PROVIDER`: CDN configuration (cloudflare, aws_cloudfront)

### Secrets Management

**Kubernetes Secrets:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: media-secrets
type: Opaque
data:
  jwt-secret: <base64-encoded-secret>
  aws-access-key: <base64-encoded-key>
  aws-secret-key: <base64-encoded-secret>
  database-url: <base64-encoded-url>
```

**Docker Secrets:**
```bash
# Create secrets
echo "your-jwt-secret" | docker secret create jwt_secret -
echo "your-aws-key" | docker secret create aws_access_key -

# Use in compose
services:
  media_service:
    secrets:
      - jwt_secret
      - aws_access_key
```

## Monitoring and Logging

### Health Checks
```bash
# Basic health check
curl http://localhost:8009/health

# Detailed monitoring
curl http://localhost:8009/health | jq .
```

### Logging Configuration
```python
# In production.env
LOG_LEVEL=INFO
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project

# Structured logging
LOGGING_FORMAT=json
```

### Metrics Collection
```bash
# Prometheus metrics endpoint (if enabled)
curl http://localhost:8009/metrics
```

## Performance Optimization

### Scaling Considerations

1. **Horizontal Scaling**: Run multiple service instances
2. **Storage Scaling**: Use cloud storage (S3) for multi-instance setups
3. **Processing Scaling**: Implement Celery workers for background tasks
4. **Caching**: Use Redis for metadata and processed files

### Resource Requirements

**Minimum (Development):**
- CPU: 1 core
- Memory: 512MB
- Disk: 10GB

**Recommended (Production):**
- CPU: 2+ cores
- Memory: 2GB+
- Disk: 100GB+ (if using local storage)

### Load Balancer Configuration

**Nginx:**
```nginx
upstream media_service {
    server media-service-1:8009;
    server media-service-2:8009;
    server media-service-3:8009;
}

server {
    listen 80;
    server_name media.mantrapath.com;
    
    client_max_body_size 500M;
    
    location / {
        proxy_pass http://media_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout for large uploads
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

## Security

### Production Security Checklist

- [ ] Use HTTPS/TLS in production
- [ ] Set strong JWT secret keys
- [ ] Configure firewall rules
- [ ] Enable virus scanning if required
- [ ] Set up file size and type restrictions
- [ ] Use secure storage provider credentials
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Backup and disaster recovery plan

### SSL/TLS Setup

```bash
# Using Certbot for Let's Encrypt
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d media.mantrapath.com
```

## Backup and Recovery

### Database Backup
```bash
# Automated daily backup
0 2 * * * pg_dump mantrapath > /backups/media_db_$(date +\%Y\%m\%d).sql
```

### Storage Backup
```bash
# S3 cross-region replication (AWS)
aws s3api put-bucket-replication --bucket source-bucket --replication-configuration file://replication.json

# Local storage backup
rsync -av /app/uploads/ /backup/uploads/
```

## Troubleshooting

### Common Issues

1. **Storage Connection Errors**
   - Verify credentials and permissions
   - Check network connectivity
   - Validate bucket/container exists

2. **Large File Upload Timeouts**
   - Increase proxy timeouts
   - Configure progressive upload
   - Check disk space

3. **Image Processing Errors**
   - Verify Pillow/OpenCV installation
   - Check file format support
   - Monitor memory usage

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export ENVIRONMENT=development

# Run with detailed output
python main.py
```

### Log Analysis
```bash
# Follow logs
tail -f /var/log/media-service/app.log

# Search for errors
grep ERROR /var/log/media-service/app.log

# Monitor resource usage
htop
df -h
```
