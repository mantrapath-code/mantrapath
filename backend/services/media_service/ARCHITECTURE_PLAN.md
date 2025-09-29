# MantraPath Media Service - Scalable Architecture Plan

## 🎯 **Service Overview**
Advanced media processing service handling images, audio, video, and file uploads with real-time processing, CDN integration, and AI-powered content analysis.

## 🏗️ **Architecture Design**

### **Core Capabilities**
- **File Upload & Storage**: Multi-provider cloud storage (AWS S3, Google Cloud, Azure)
- **Image Processing**: Real-time resizing, compression, format conversion
- **Audio Processing**: Meditation audio, voice notes, podcast streaming
- **Video Processing**: Guided meditation videos, user-generated content
- **Content Analysis**: AI-powered content moderation and tagging
- **CDN Integration**: Global content delivery for performance
- **Security**: End-to-end encryption, access controls, virus scanning

### **🔧 Technical Stack**

#### **Core Framework**
```python
# FastAPI with async processing
FastAPI + Uvicorn
Python 3.11+
Pydantic v2 (data validation)
SQLAlchemy (database ORM)
```

#### **Storage Solutions**
```yaml
Primary Storage:
  - AWS S3 (production)
  - MinIO (development/testing)
  - Local filesystem (fallback)

CDN Integration:
  - CloudFlare (global distribution)
  - AWS CloudFront (backup)
  - Cache headers optimization
```

#### **Processing Engines**
```python
Image Processing:
  - Pillow (PIL) - Basic operations
  - OpenCV - Advanced computer vision
  - ImageIO - Format conversion
  - Wand (ImageMagick) - Professional editing

Audio Processing:
  - FFmpeg - Comprehensive audio/video
  - pydub - Audio manipulation
  - librosa - Audio analysis
  - scipy - Signal processing

Video Processing:
  - FFmpeg - Video encoding/decoding
  - OpenCV - Video analysis
  - moviepy - Video editing
```

#### **AI & ML Integration**
```python
Content Analysis:
  - NSFW detection (Yahoo Open NSFW)
  - Object recognition (YOLO v8)
  - Text extraction (OCR - Tesseract)
  - Sentiment analysis (integration with ML service)

Image Enhancement:
  - Noise reduction algorithms
  - Quality assessment
  - Auto-enhancement filters
```

### **🚀 Service Architecture**

#### **Directory Structure**
```
media_service/
├── main.py                     # FastAPI application
├── requirements.txt            # Dependencies
├── Dockerfile                  # Container configuration
├── .env                        # Environment variables
├── config/
│   ├── __init__.py
│   ├── settings.py            # Configuration management
│   └── storage_config.py      # Storage provider configs
├── models/
│   ├── __init__.py
│   ├── media_models.py        # Database models
│   └── request_models.py      # API request/response models
├── services/
│   ├── __init__.py
│   ├── storage_service.py     # Multi-provider storage
│   ├── image_processor.py     # Image processing engine
│   ├── audio_processor.py     # Audio processing engine
│   ├── video_processor.py     # Video processing engine
│   ├── content_analyzer.py    # AI content analysis
│   └── cdn_service.py         # CDN management
├── utils/
│   ├── __init__.py
│   ├── security.py           # Security utilities
│   ├── validation.py         # File validation
│   └── helpers.py            # Common utilities
├── middleware/
│   ├── __init__.py
│   ├── auth_middleware.py    # JWT authentication
│   └── rate_limiter.py       # Upload rate limiting
├── tests/
│   ├── test_upload.py        # Upload functionality tests
│   ├── test_processing.py    # Processing engine tests
│   └── test_security.py      # Security tests
└── docs/
    ├── API.md                # API documentation
    └── DEPLOYMENT.md         # Deployment guide
```

### **📡 API Endpoints**

#### **File Upload & Management**
```python
POST /media/upload           # Upload single file
POST /media/upload-multiple  # Upload multiple files
GET /media/{media_id}        # Get media metadata
DELETE /media/{media_id}     # Delete media file
GET /media/user/{user_id}    # Get user's media files
```

#### **Processing & Transformation**
```python
POST /media/{media_id}/resize      # Resize image
POST /media/{media_id}/compress    # Compress file
POST /media/{media_id}/convert     # Format conversion
POST /media/{media_id}/enhance     # AI enhancement
GET /media/{media_id}/variants     # Get all variants
```

#### **Streaming & CDN**
```python
GET /media/{media_id}/stream       # Stream media content
GET /media/{media_id}/thumbnail    # Get thumbnail
GET /media/{media_id}/preview      # Get preview/low-res
POST /media/{media_id}/cdn-sync    # Sync to CDN
```

#### **Analytics & Insights**
```python
GET /media/{media_id}/analytics    # Media analytics
POST /media/{media_id}/analyze     # AI content analysis
GET /media/insights/usage          # Usage statistics
GET /media/insights/performance    # Performance metrics
```

### **🔒 Security Architecture**

#### **Upload Security**
```python
# File validation pipeline
1. File type validation (whitelist)
2. File size limits (configurable)
3. Virus scanning (ClamAV integration)
4. Content analysis (NSFW detection)
5. Metadata sanitization
6. Secure filename generation
```

#### **Access Control**
```python
# Multi-layer security
- JWT authentication (integration with auth service)
- Resource-based permissions
- Rate limiting (per user/IP)
- CORS configuration
- Input sanitization
- SQL injection prevention
```

#### **Storage Security**
```python
# Encrypted storage
- AES-256 encryption at rest
- TLS 1.3 for data in transit
- Signed URLs for secure access
- Time-limited access tokens
- Audit logging for all operations
```

### **⚡ Performance Optimization**

#### **Async Processing**
```python
# Background task processing
- Celery + Redis for task queue
- Async file processing
- Progressive upload for large files
- Thumbnail generation in background
- CDN synchronization queues
```

#### **Caching Strategy**
```python
# Multi-level caching
- Redis for metadata caching
- CDN edge caching
- Browser cache headers
- Thumbnail cache
- Processing result cache
```

#### **Scaling Considerations**
```python
# Horizontal scaling
- Stateless service design
- Load balancer compatibility
- Database connection pooling
- Shared storage architecture
- Container orchestration ready
```

### **📊 Database Schema**

```sql
-- Media files table
CREATE TABLE media_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    storage_provider VARCHAR(50) NOT NULL,
    storage_path TEXT NOT NULL,
    cdn_url TEXT,
    thumbnail_url TEXT,
    metadata JSONB,
    processing_status VARCHAR(50) DEFAULT 'pending',
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Media variants table (resized, compressed versions)
CREATE TABLE media_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    media_file_id UUID NOT NULL REFERENCES media_files(id) ON DELETE CASCADE,
    variant_type VARCHAR(50) NOT NULL, -- 'thumbnail', 'compressed', 'resized'
    variant_config JSONB NOT NULL,     -- Processing parameters
    storage_path TEXT NOT NULL,
    cdn_url TEXT,
    file_size BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Content analysis results
CREATE TABLE content_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    media_file_id UUID NOT NULL REFERENCES media_files(id) ON DELETE CASCADE,
    analysis_type VARCHAR(50) NOT NULL, -- 'nsfw', 'objects', 'sentiment'
    confidence_score DECIMAL(5,4),
    results JSONB NOT NULL,
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_media_files_user_id ON media_files(user_id);
CREATE INDEX idx_media_files_type ON media_files(file_type);
CREATE INDEX idx_media_files_created ON media_files(created_at);
CREATE INDEX idx_media_variants_file_id ON media_variants(media_file_id);
CREATE INDEX idx_content_analysis_file_id ON content_analysis(media_file_id);
```

### **🚀 Implementation Phases**

#### **Phase 1: Core Upload & Storage** (Week 1-2)
- [ ] Basic FastAPI setup with authentication
- [ ] File upload endpoints
- [ ] Multi-provider storage (S3, MinIO, local)
- [ ] Basic security validation
- [ ] Database schema implementation

#### **Phase 2: Processing Engines** (Week 3-4)
- [ ] Image processing (resize, compress, convert)
- [ ] Audio processing (format conversion, compression)
- [ ] Thumbnail generation
- [ ] Background task processing with Celery

#### **Phase 3: Advanced Features** (Week 5-6)
- [ ] AI content analysis integration
- [ ] CDN integration and synchronization
- [ ] Advanced security (virus scanning)
- [ ] Performance optimization
- [ ] Monitoring and analytics

#### **Phase 4: Production Ready** (Week 7-8)
- [ ] Comprehensive testing suite
- [ ] Load testing and optimization
- [ ] Documentation completion
- [ ] Deployment automation
- [ ] Monitoring and alerting

### **💾 Storage Configuration**

```python
# config/storage_config.py
STORAGE_PROVIDERS = {
    "aws_s3": {
        "bucket_name": os.getenv("AWS_S3_BUCKET"),
        "region": os.getenv("AWS_REGION", "us-east-1"),
        "access_key": os.getenv("AWS_ACCESS_KEY"),
        "secret_key": os.getenv("AWS_SECRET_KEY"),
        "endpoint_url": None  # Default AWS endpoints
    },
    "minio": {
        "bucket_name": os.getenv("MINIO_BUCKET", "mantrapath-media"),
        "endpoint_url": os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        "access_key": os.getenv("MINIO_ACCESS_KEY"),
        "secret_key": os.getenv("MINIO_SECRET_KEY"),
        "secure": os.getenv("MINIO_SECURE", "false").lower() == "true"
    },
    "local": {
        "base_path": os.getenv("LOCAL_STORAGE_PATH", "./uploads"),
        "url_prefix": os.getenv("LOCAL_URL_PREFIX", "/static/uploads")
    }
}

# File type configurations
ALLOWED_FILE_TYPES = {
    "image": ["jpg", "jpeg", "png", "gif", "webp", "svg"],
    "audio": ["mp3", "wav", "ogg", "m4a", "flac"],
    "video": ["mp4", "avi", "mov", "wmv", "flv", "webm"],
    "document": ["pdf", "doc", "docx", "txt", "md"]
}

MAX_FILE_SIZES = {
    "image": 10 * 1024 * 1024,      # 10MB
    "audio": 100 * 1024 * 1024,     # 100MB
    "video": 500 * 1024 * 1024,     # 500MB
    "document": 5 * 1024 * 1024      # 5MB
}
```

### **🔧 Environment Configuration**

```env
# Media Service Configuration
MEDIA_SERVICE_PORT=8021
MEDIA_SERVICE_HOST=0.0.0.0

# Database
DATABASE_URL=postgresql://user:password@localhost/mantrapath

# Redis (for caching and task queue)
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379

# Storage Providers
PRIMARY_STORAGE_PROVIDER=aws_s3  # or 'minio' or 'local'
AWS_S3_BUCKET=mantrapath-media-prod
AWS_REGION=us-east-1
AWS_ACCESS_KEY=your_access_key
AWS_SECRET_KEY=your_secret_key

# MinIO (for development)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=mantrapath-media-dev

# CDN Configuration
CDN_PROVIDER=cloudflare  # or 'aws_cloudfront'
CDN_BASE_URL=https://cdn.mantrapath.com
CLOUDFLARE_ZONE_ID=your_zone_id
CLOUDFLARE_API_TOKEN=your_api_token

# Security
UPLOAD_VIRUS_SCANNING=true
CLAMAV_HOST=localhost
CLAMAV_PORT=3310
MAX_UPLOAD_SIZE=500MB
ALLOWED_DOMAINS=mantrapath.com,localhost

# Processing
IMAGE_QUALITY_DEFAULT=85
THUMBNAIL_SIZE=300x300
VIDEO_COMPRESSION_PRESET=medium
AUDIO_BITRATE_DEFAULT=128k

# Monitoring
SENTRY_DSN=your_sentry_dsn
METRICS_ENABLED=true
LOG_LEVEL=INFO
```

### **📈 Monitoring & Analytics**

```python
# Key metrics to track
MEDIA_METRICS = {
    "upload_count": "Total files uploaded",
    "upload_size": "Total bytes uploaded",
    "processing_time": "Average processing time",
    "error_rate": "Upload/processing error rate",
    "storage_usage": "Total storage consumed",
    "cdn_cache_hit_rate": "CDN performance",
    "user_engagement": "Media interaction rates"
}

# Health check endpoints
@app.get("/health")
async def health_check():
    return {
        "service": "media_service",
        "status": "healthy",
        "storage_providers": check_storage_health(),
        "processing_queues": check_queue_health(),
        "database": check_db_health()
    }
```

### **🧪 Testing Strategy**

```python
# Test coverage areas
1. File Upload Tests
   - Various file types and sizes
   - Security validation
   - Error handling

2. Processing Tests
   - Image resize/compression
   - Audio/video conversion
   - Thumbnail generation

3. Storage Tests
   - Multi-provider compatibility
   - CDN synchronization
   - Backup and recovery

4. Security Tests
   - Authentication/authorization
   - Malware detection
   - Input sanitization

5. Performance Tests
   - Large file handling
   - Concurrent uploads
   - Processing speed
```

### **🎯 Success Metrics**

- **Upload Success Rate**: >99.5%
- **Processing Speed**: <30s for images, <5min for videos
- **API Response Time**: <200ms for metadata operations
- **Security Incidents**: Zero tolerance for malware/data breaches
- **CDN Cache Hit Rate**: >90%
- **User Satisfaction**: Seamless media experience

---

## 🎯 **IMPLEMENTATION PRIORITY**
1. **HIGH**: Basic upload/download functionality
2. **MEDIUM**: Image processing and thumbnails
3. **MEDIUM**: CDN integration
4. **LOW**: Advanced AI analysis features

This architecture provides a solid foundation for scalable, secure, and performant media handling in the MantraPath platform.
