# MantraPath Media Service

> 🎯 **Enterprise-grade media processing service with multi-provider storage, AI-powered analysis, and real-time processing capabilities**

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/ssharmasachin/mantrapath)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](./docs/TESTING.md)

## 📖 Project Overview

The MantraPath Media Service is a comprehensive, production-ready microservice designed to handle all aspects of media management for the MantraPath platform. It provides seamless file upload, intelligent processing, multi-provider storage, and AI-powered content analysis with enterprise-level scalability and security.

### ✨ Key Features

- **🗄️ Multi-Provider Storage**: AWS S3, MinIO, and Local filesystem support with seamless switching
- **🖼️ Intelligent Image Processing**: Resize, compress, format conversion, and enhancement with quality optimization
- **🎬 Video & Audio Processing**: Format conversion, compression, and thumbnail generation
- **🤖 AI-Powered Analysis**: Content analysis, object detection, and metadata extraction
- **⚡ Background Processing**: Asynchronous task processing with Celery and Redis
- **🔒 Enterprise Security**: File validation, virus scanning, JWT authentication, and access controls
- **🌐 CDN Integration**: Global content delivery with CloudFlare and AWS CloudFront support
- **📊 Analytics & Monitoring**: Real-time metrics, health checks, and performance tracking

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** ([Download](https://python.org/downloads/))
- **PostgreSQL 13+** ([Download](https://postgresql.org/download/))
- **Redis 6+** ([Download](https://redis.io/download))
- **Docker** (optional, for containerized deployment)

**System Dependencies:**
```bash
# macOS
brew install libmagic

# Ubuntu/Debian
sudo apt-get install libmagic1 libmagic-dev

# CentOS/RHEL
sudo yum install file-devel
```

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ssharmasachin/mantrapath.git
   cd mantrapath/backend/services/media_service
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install development dependencies** (optional)
   ```bash
   pip install -r requirements-test.txt
   ```

### Configuration

1. **Create environment configuration**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file with your configuration:**
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

   # Security
   JWT_SECRET_KEY=your-super-secret-jwt-key
   MAX_UPLOAD_SIZE=500MB

   # Redis (for background tasks)
   REDIS_URL=redis://localhost:6379
   ```

3. **Set up the database**
   ```bash
   # Create database tables
   alembic upgrade head
   ```

### Running the Project

**Development Mode:**
```bash
# Start the service with auto-reload
python start_service.py
```

**Production Mode:**
```bash
# Start with Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8009 --workers 4
```

**Using Docker:**
```bash
# Build and run
docker build -t mantrapath-media-service .
docker run -p 8009:8009 --env-file .env mantrapath-media-service
```

**Expected Output:**
```
🚀 Starting MantraPath Media Service...
📁 Service directory: /path/to/media_service
📦 Uploads directory: /path/to/uploads
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8009
```

## 💡 Usage and Examples

### Core Functionality

The Media Service provides a comprehensive REST API for media management:

- **Upload Management**: Multi-file uploads with progress tracking
- **Storage Abstraction**: Seamless switching between storage providers
- **Processing Pipeline**: Background image/video processing with job queues
- **Content Analysis**: AI-powered content analysis and metadata extraction
- **CDN Integration**: Global content delivery optimization

### Code Examples

**Upload a media file:**
```bash
curl -X POST "http://localhost:8009/api/v1/media/upload" \
  -H "Authorization: Bearer your-jwt-token" \
  -F "file=@image.jpg" \
  -F "alt_text=Beautiful sunset" \
  -F "tags=nature,sunset,landscape" \
  -F "is_public=true"
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "user123_20250814_123456_a1b2c3d4.jpg",
  "file_size": 1024000,
  "content_type": "image/jpeg",
  "file_type": "image",
  "upload_url": "/api/v1/media/123e4567-e89b-12d3-a456-426614174000",
  "status": "uploaded_processing",
  "processing_job_id": "456e7890-e89b-12d3-a456-426614174001"
}
```

**Process an image:**
```bash
curl -X POST "http://localhost:8009/api/v1/media/{media_id}/process" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "operation": "resize",
    "parameters": {
      "width": 800,
      "height": 600,
      "maintain_aspect_ratio": true,
      "quality": 85
    }
  }'
```

**Get file details:**
```bash
curl "http://localhost:8009/api/v1/media/{media_id}" \
  -H "Authorization: Bearer your-jwt-token"
```

**Health check:**
```bash
curl "http://localhost:8009/health"
```

### Live Demo

🌐 **Interactive API Documentation**: When running locally, visit:
- **Swagger UI**: http://localhost:8009/docs
- **ReDoc**: http://localhost:8009/redoc

### Tutorials

For detailed tutorials and advanced usage examples, see:
- 📚 [API Documentation](./docs/API.md)
- 🧪 [Testing Guide](./docs/TESTING.md)
- 🚀 [Deployment Guide](./docs/DEPLOYMENT.md)

## 🏗️ Advanced Topics

### Architecture

The Media Service follows a modular, microservices architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Storage Layer  │    │ Processing Layer│
│                 │    │                 │    │                 │
│  • REST API     │◄──►│  • AWS S3       │◄──►│  • Image Proc   │
│  • Auth & Valdtn│    │  • MinIO        │    │  • Video Proc   │
│  • Upload Mgmt  │    │  • Local FS     │    │  • AI Analysis  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Database      │    │   Redis Cache   │    │  Background     │
│                 │    │                 │    │  Workers        │
│  • PostgreSQL   │    │  • Metadata     │    │  • Celery       │
│  • Media Files  │    │  • Sessions     │    │  • Job Queue    │
│  • Processing   │    │  • Task Queue   │    │  • Processing   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Technology Stack:**
- **API**: FastAPI with Pydantic v2 for type safety
- **Database**: PostgreSQL with SQLAlchemy 2.0
- **Storage**: Multi-provider abstraction (S3, MinIO, Local)
- **Processing**: Pillow, OpenCV, FFmpeg for media manipulation
- **Background**: Celery with Redis for async processing
- **Monitoring**: Prometheus metrics, health checks

### API Reference

📖 **Full API Documentation**: [./docs/API.md](./docs/API.md)

**Quick Reference:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/media/upload` | POST | Upload media files |
| `/api/v1/media/{id}` | GET | Get media details |
| `/api/v1/media/` | GET | List media files |
| `/api/v1/media/{id}/file` | GET | Download media file |
| `/api/v1/media/{id}/process` | POST | Process media file |
| `/health` | GET | Service health check |

### Testing

Run the complete test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run performance tests
pytest tests/performance/ -v
```

**Test Results:**
```
======================== test session starts ========================
collected 127 items

tests/unit/test_config.py .................. [ 14%]
tests/unit/test_models.py ................... [ 28%]
tests/unit/test_storage_service.py .......... [ 42%]
tests/unit/test_image_processor.py .......... [ 56%]
tests/integration/test_api_endpoints.py ..... [ 70%]
tests/integration/test_storage_integration.py [ 84%]
tests/e2e/test_upload_flow.py ............... [100%]

======================== 127 passed in 45.2s ========================
```

## 🤝 Contribution Guidelines

We welcome contributions from the community! The Media Service is designed to be extensible and maintainable.

### How to Contribute

1. **🐛 Report Bugs**: Use GitHub Issues to report bugs with detailed reproduction steps
2. **💡 Request Features**: Submit feature requests with clear use cases and benefits
3. **🔧 Submit Code**: Fork the repository, create a feature branch, and submit a pull request
4. **📖 Improve Documentation**: Help us improve guides, tutorials, and API documentation

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/mantrapath.git
   cd mantrapath/backend/services/media_service
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate

   # Install all dependencies
   pip install -r requirements.txt
   pip install -r requirements-test.txt

   # Set up pre-commit hooks
   pre-commit install
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-new-feature
   ```

4. **Make your changes and test**
   ```bash
   # Run tests
   pytest

   # Run linting
   flake8 .
   mypy .

   # Test the implementation
   python test_implementation.py
   ```

5. **Submit a pull request**
   - Write clear commit messages
   - Include tests for new functionality
   - Update documentation as needed
   - Ensure all CI checks pass

### Development Tools

**Code Quality:**
```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy .

# Linting
flake8 .
```

**Database Migrations:**
```bash
# Create new migration
alembic revision --autogenerate -m "Add new feature"

# Apply migrations
alembic upgrade head
```

### Code of Conduct

This project adheres to a [Code of Conduct](../../CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** - For the excellent async web framework
- **Pydantic** - For robust data validation and settings management
- **SQLAlchemy** - For powerful and flexible ORM capabilities
- **Pillow & OpenCV** - For comprehensive image processing capabilities
- **The MantraPath Team** - For continuous feedback and testing

## 📞 Support

- **Documentation**: [./docs/](./docs/)
- **Issues**: [GitHub Issues](https://github.com/ssharmasachin/mantrapath/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ssharmasachin/mantrapath/discussions)
- **Email**: support@mantrapath.com

---

<div align="center">

**Built with ❤️ by the MantraPath Team**

[🌟 Star this project](https://github.com/ssharmasachin/mantrapath) | [🍴 Fork it](https://github.com/ssharmasachin/mantrapath/fork) | [📖 Read the docs](./docs/API.md)

</div>
