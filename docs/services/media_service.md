# Media Service

## Description

The Media Service is the comprehensive media management hub of the MantraPath platform, handling file uploads, processing, storage, and delivery across multiple formats and providers. This service manages profile pictures, community images, voice recordings, video content, and all other media assets used throughout the platform. It provides advanced media processing capabilities including image optimization, format conversion, content analysis, and multi-provider storage with CDN integration.

This service solves the complex challenge of managing diverse media types in a scalable, secure manner. It handles everything from simple profile picture uploads to complex video processing, ensuring optimal delivery performance, storage efficiency, and content security across all platform interactions.

## Table of Contents

- [Installation / Setup](#installation--setup)
- [Usage](#usage)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)
- [License](#license)
- [Contact / Author Info](#contact--author-info)
- [FAQ / Troubleshooting](#faq--troubleshooting)
- [Future Implementation](#future-implementation)

## Installation / Setup

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- PostgreSQL database
- Storage providers (local, AWS S3, MinIO, etc.)
- Image processing libraries (system-level dependencies)

### System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y libmagic1 libmagic-dev

# MacOS
brew install libmagic

# For advanced image processing
sudo apt-get install -y libopencv-dev python3-opencv
```

### Installation Commands

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mantrapath-code/mantrapath.git
   cd mantrapath/backend/services/media_service
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up storage directories:**
   ```bash
   mkdir -p storage/uploads storage/processed
   ```

### Configuration

- Environment variables configuration:
  ```bash
  cp .env.example .env
  nano .env
  ```
- Key variables include `DATABASE_URL`, storage provider settings (`AWS_*`, `MINIO_*`), processing configuration, and CDN settings.

## Usage

The Media Service provides comprehensive media management through REST API endpoints.

- **Running the service locally:**
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8021 --reload
  ```

- **Alternative start method:**
  ```bash
  python start_service.py
  ```

- **Running with Docker:**
  ```bash
  docker-compose up -d media_service
  ```

- **Upload media file:**
  ```bash
  curl -X POST "http://localhost:8021/api/v1/media/upload" \
       -H "Authorization: Bearer <token>" \
       -F "file=@image.jpg" \
       -F "alt_text=Profile picture" \
       -F "is_public=true"
  ```

- **Get media file:**
  ```bash
  curl -X GET "http://localhost:8021/api/v1/media/{file_id}" \
       -H "Authorization: Bearer <token>"
  ```

- **API Documentation:**
  Interactive API documentation at `http://localhost:8021/docs`

## Features

- **Multi-Format Support:** Images (JPEG, PNG, GIF, WebP), videos (MP4, WebM), audio (MP3, WAV, OGG), documents (PDF)
- **Advanced Image Processing:** Automatic resizing, format conversion, optimization, and thumbnail generation
- **Multi-Provider Storage:** Support for local storage, AWS S3, MinIO, and other cloud storage providers
- **CDN Integration:** Seamless integration with content delivery networks for optimal performance
- **Content Analysis:** AI-powered content analysis for automatic tagging and moderation
- **Security Features:** File type validation, size limits, virus scanning, and access control
- **Media Variants:** Automatic generation of multiple sizes and formats for optimal delivery
- **Background Processing:** Asynchronous media processing using Celery for heavy operations
- **Metadata Management:** Comprehensive metadata storage including EXIF data, dimensions, and custom attributes
- **Search and Discovery:** Advanced search capabilities with filtering by type, size, tags, and metadata
- **Batch Operations:** Bulk upload, processing, and management operations
- **Performance Optimization:** Caching, compression, and efficient storage strategies

## Tech Stack

- **Backend:** Python 3.10+, FastAPI 0.104.1
- **Database:** PostgreSQL with SQLAlchemy 2.0.23 ORM
- **Image Processing:** Pillow 10.1.0, OpenCV 4.8.1 (headless)
- **File Handling:** Aiofiles 23.2.1, Python-magic 0.4.27
- **Storage Providers:** Boto3 1.34.0 (AWS), MinIO 7.2.0
- **Background Processing:** Celery 5.3.4 for asynchronous tasks
- **Authentication:** JWT token validation through shared auth system
- **HTTP Client:** HTTPX 0.25.2 for external service integration
- **Configuration:** Pydantic Settings for configuration management
- **Logging:** Loguru for comprehensive media operation logging
- **Database Migrations:** Alembic 1.12.1 for schema management
- **Containerization:** Docker

## Contributing

Contributions to enhance media processing capabilities are highly valued:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/video-processing`)
3. Implement media-focused improvements
4. Add comprehensive tests for new media formats
5. Ensure performance optimization and security
6. Update processing workflows and documentation
7. Submit a pull request with detailed media processing analysis

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

- **Author:** Sachin Sharma
- **Email:** sachin.sharma@mantrapath.com
- **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

- **"File upload fails with large files"**: Check file size limits and storage provider configuration. Ensure sufficient disk space and memory.
- **"Image processing slow"**: Verify OpenCV installation and consider enabling GPU acceleration for large batch operations.
- **"Storage provider connection failed"**: Review cloud storage credentials and network connectivity to storage endpoints.
- **"Generated thumbnails poor quality"**: Adjust image processing parameters and ensure source image quality is sufficient.

## Future Implementation

- **Advanced Video Processing:** Video transcoding, compression, and streaming optimization
- **AI Content Moderation:** Automatic detection and filtering of inappropriate content
- **Real-time Processing:** Live image filters and real-time media transformations
- **Advanced Analytics:** Media usage analytics and performance insights
- **Blockchain Integration:** Immutable media provenance and copyright protection
- **Edge Processing:** Edge computing integration for faster media processing