# Media Service API Documentation

## Overview

The MantraPath Media Service is a comprehensive, scalable media processing service that handles file uploads, storage, processing, and delivery. It supports multiple storage providers, real-time processing, and AI-powered content analysis.

## Features

- **Multi-Provider Storage**: AWS S3, MinIO, Local filesystem
- **Image Processing**: Resize, compress, format conversion, enhancement
- **Background Processing**: Asynchronous media processing with job queues
- **Security**: File validation, virus scanning, access controls
- **CDN Integration**: Global content delivery optimization
- **Analytics**: Usage tracking and performance metrics

## API Endpoints

### Upload & Management

#### Upload Media File
```http
POST /api/v1/media/upload
Content-Type: multipart/form-data

Parameters:
- file: Binary file data (required)
- alt_text: Alternative text for accessibility (optional)
- caption: Media caption (optional)
- tags: Comma-separated tags (optional)
- is_public: Boolean for public access (optional, default: false)
```

**Response:**
```json
{
  "id": "uuid",
  "filename": "safe_filename.jpg",
  "file_size": 1024000,
  "content_type": "image/jpeg",
  "file_type": "image",
  "upload_url": "/api/v1/media/{id}",
  "status": "uploaded_processing",
  "processing_job_id": "uuid"
}
```

#### Get Media File Details
```http
GET /api/v1/media/{media_id}
```

**Response:**
```json
{
  "id": "uuid",
  "filename": "safe_filename.jpg",
  "original_filename": "original.jpg",
  "file_type": "image",
  "file_size": 1024000,
  "mime_type": "image/jpeg",
  "storage_provider": "local",
  "cdn_url": null,
  "thumbnail_url": "/api/v1/media/{id}/thumbnail",
  "processing_status": "completed",
  "is_public": false,
  "metadata": {},
  "created_at": "2025-08-14T10:00:00Z",
  "updated_at": "2025-08-14T10:00:00Z"
}
```

#### List Media Files
```http
GET /api/v1/media/?page=1&per_page=20&file_type=image&is_public=true
```

**Response:**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "pages": 5,
  "has_next": true,
  "has_prev": false
}
```

#### Serve Media File
```http
GET /api/v1/media/{media_id}/file
```

Returns the actual media file content or a redirect to the file URL.

### Processing Operations

#### Process Image
```http
POST /api/v1/media/{media_id}/process
Content-Type: application/json

{
  "operation": "resize",
  "parameters": {
    "width": 800,
    "height": 600,
    "maintain_aspect_ratio": true,
    "quality": 85
  },
  "priority": 5
}
```

**Supported Operations:**
- `resize`: Change image dimensions
- `compress`: Reduce file size
- `convert`: Change format (JPEG, PNG, WEBP, GIF)
- `enhance`: Adjust brightness, contrast, saturation
- `thumbnail`: Generate thumbnail
- `crop`: Crop to specified area
- `rotate`: Rotate by angle
- `filter`: Apply image filters

#### Video Processing
```http
POST /api/v1/media/{media_id}/process
Content-Type: application/json

{
  "operation": "compress",
  "parameters": {
    "preset": "medium",
    "quality": "720p"
  }
}
```

**Supported Operations:**
- `compress`: Reduce video file size
- `convert`: Change format
- `thumbnail`: Extract frame as thumbnail
- `extract_audio`: Extract audio track

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "media_service",
  "timestamp": "2025-08-14T10:00:00Z",
  "storage_providers": {
    "local": "healthy",
    "aws_s3": "healthy"
  },
  "processing_queues": {
    "background_tasks": 0
  },
  "database": "connected",
  "disk_space": {
    "free_gb": 50.5,
    "used_gb": 25.2
  }
}
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Service Configuration
MEDIA_SERVICE_PORT=8009
MEDIA_SERVICE_HOST=0.0.0.0

# Database
DATABASE_URL=postgresql://username:password@localhost/mantrapath

# Storage (choose primary provider)
PRIMARY_STORAGE_PROVIDER=local  # or 'aws_s3' or 'minio'

# Local Storage
LOCAL_STORAGE_PATH=./uploads
LOCAL_URL_PREFIX=/static/uploads

# AWS S3 (for production)
AWS_S3_BUCKET=mantrapath-media-prod
AWS_REGION=us-east-1
AWS_ACCESS_KEY=your_access_key
AWS_SECRET_KEY=your_secret_key

# Security
MAX_UPLOAD_SIZE=500MB
UPLOAD_VIRUS_SCANNING=false

# Processing
IMAGE_QUALITY_DEFAULT=85
THUMBNAIL_SIZE=300x300
```

### File Type Limits

| Type | Max Size | Allowed Formats |
|------|----------|-----------------|
| Image | 10MB | JPEG, PNG, GIF, WEBP, SVG |
| Audio | 100MB | MP3, WAV, OGG, M4A, FLAC |
| Video | 500MB | MP4, AVI, MOV, WMV, FLV, WEBM |
| Document | 5MB | PDF, DOC, DOCX, TXT, MD |

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `413 Payload Too Large`: File size exceeds limits
- `415 Unsupported Media Type`: File type not allowed
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "error": "ValidationError",
  "message": "File type not allowed: application/x-executable",
  "details": {
    "allowed_types": ["image/jpeg", "image/png", ...]
  },
  "timestamp": "2025-08-14T10:00:00Z"
}
```

## Security

### File Validation
- MIME type detection using python-magic
- File size limits per category
- Filename sanitization
- Content analysis for malicious files

### Access Control
- JWT-based authentication
- Resource-level permissions
- Public/private file access
- Rate limiting

### Storage Security
- Optional virus scanning with ClamAV
- Encrypted storage support
- Secure file URLs with expiration
- Audit logging

## Performance

### Optimization Features
- Asynchronous file processing
- Background task queues
- Multi-level caching (Redis, CDN)
- Progressive upload for large files
- Responsive image variants

### Monitoring
- Health check endpoints
- Performance metrics
- Error tracking with Sentry
- Storage usage analytics

## Development

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run the service
python main.py
```

### Testing
```bash
# Upload a test image (internal DNS)
curl -X POST "media-service:8021/api/v1/media/upload" \
  -H "Authorization: Bearer your-jwt-token" \
  -F "file=@test.jpg" \
  -F "alt_text=Test image" \
  -F "is_public=true"

# Get file details
curl "media-service:8021/api/v1/media/{media_id}"

# Health check
curl "media-service:8021/health"

# Host examples (if ports exposed) prefix with http://localhost:8021 instead of media-service:8021
```

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8009

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8009"]
```

### Production Considerations
- Use external Redis for caching and task queues
- Configure proper storage providers (S3, etc.)
- Set up CDN for global delivery
- Enable monitoring and logging
- Configure SSL/TLS termination
- Set appropriate resource limits
