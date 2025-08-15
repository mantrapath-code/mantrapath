# Media Service Testing Guide

## Overview

This guide covers comprehensive testing strategies for the MantraPath Media Service, including unit tests, integration tests, and end-to-end testing.

## Test Structure

```
tests/
├── unit/
│   ├── test_config.py
│   ├── test_models.py
│   ├── test_storage_service.py
│   ├── test_image_processor.py
│   └── test_utils.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_storage_integration.py
│   ├── test_database_operations.py
│   └── test_background_tasks.py
├── e2e/
│   ├── test_upload_flow.py
│   ├── test_processing_pipeline.py
│   └── test_cdn_integration.py
├── fixtures/
│   ├── test_images/
│   ├── test_documents/
│   └── test_media/
└── conftest.py
```

## Setup

### Installation

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Or individual packages
pip install pytest pytest-asyncio pytest-mock httpx pytest-cov
```

### Configuration

Create `tests/conftest.py`:

```python
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from main import app
from config.settings import get_settings
from models.media_models import Base
from services.storage_service import StorageService

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_settings():
    """Override settings for testing."""
    return {
        "DATABASE_URL": "sqlite:///test.db",
        "REDIS_URL": "redis://localhost:6379/1",
        "PRIMARY_STORAGE_PROVIDER": "local",
        "LOCAL_STORAGE_PATH": "test_uploads",
        "JWT_SECRET_KEY": "test-secret-key",
        "ENVIRONMENT": "testing"
    }

@pytest.fixture
def test_db():
    """Create test database."""
    engine = create_engine("sqlite:///test.db")
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield TestingSessionLocal()
    
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_settings):
    """Create test client."""
    with patch.dict('os.environ', test_settings):
        with TestClient(app) as test_client:
            yield test_client

@pytest.fixture
def temp_storage():
    """Create temporary storage directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_image():
    """Create a sample image for testing."""
    from PIL import Image
    import io
    
    image = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

@pytest.fixture
def sample_files():
    """Sample files for testing."""
    return {
        'image.jpg': b'fake-jpeg-content',
        'document.pdf': b'fake-pdf-content',
        'video.mp4': b'fake-video-content'
    }
```

## Unit Tests

### Test Configuration

```python
# tests/unit/test_config.py
import pytest
from unittest.mock import patch
from config.settings import MediaServiceSettings

class TestMediaServiceSettings:
    
    def test_default_settings(self):
        """Test default configuration values."""
        settings = MediaServiceSettings()
        assert settings.SERVICE_NAME == "media_service"
        assert settings.MAX_UPLOAD_SIZE == 500 * 1024 * 1024  # 500MB
        assert settings.ALLOWED_IMAGE_TYPES == ['jpeg', 'jpg', 'png', 'gif', 'webp']
    
    @patch.dict('os.environ', {
        'DATABASE_URL': 'postgresql://test:test@localhost/test',
        'JWT_SECRET_KEY': 'test-secret'
    })
    def test_environment_override(self):
        """Test environment variable override."""
        settings = MediaServiceSettings()
        assert settings.DATABASE_URL == 'postgresql://test:test@localhost/test'
        assert settings.JWT_SECRET_KEY == 'test-secret'
    
    def test_storage_provider_validation(self):
        """Test storage provider validation."""
        with pytest.raises(ValueError):
            MediaServiceSettings(PRIMARY_STORAGE_PROVIDER='invalid')
```

### Test Models

```python
# tests/unit/test_models.py
import pytest
from datetime import datetime
from models.media_models import MediaFile, MediaVariant
from sqlalchemy.orm import Session

class TestMediaModels:
    
    def test_media_file_creation(self, test_db: Session):
        """Test MediaFile model creation."""
        media_file = MediaFile(
            filename="test.jpg",
            file_size=1024,
            content_type="image/jpeg",
            storage_provider="local",
            storage_path="/uploads/test.jpg",
            uploaded_by="user123"
        )
        
        test_db.add(media_file)
        test_db.commit()
        
        assert media_file.id is not None
        assert media_file.created_at is not None
        assert media_file.is_active is True
    
    def test_media_variant_relationship(self, test_db: Session):
        """Test MediaVariant relationship with MediaFile."""
        # Create parent media file
        media_file = MediaFile(
            filename="original.jpg",
            file_size=2048,
            content_type="image/jpeg",
            storage_provider="local",
            storage_path="/uploads/original.jpg",
            uploaded_by="user123"
        )
        test_db.add(media_file)
        test_db.flush()
        
        # Create variant
        variant = MediaVariant(
            media_file_id=media_file.id,
            variant_type="thumbnail",
            filename="original_thumb.jpg",
            file_size=512,
            storage_path="/uploads/thumbs/original_thumb.jpg",
            metadata={"width": 150, "height": 150}
        )
        test_db.add(variant)
        test_db.commit()
        
        assert len(media_file.variants) == 1
        assert variant.media_file.filename == "original.jpg"
```

### Test Storage Service

```python
# tests/unit/test_storage_service.py
import pytest
from unittest.mock import Mock, patch, AsyncMock
from services.storage_service import StorageService, LocalStorageProvider
import tempfile
import os

class TestLocalStorageProvider:
    
    @pytest.fixture
    def provider(self, temp_storage):
        """Create local storage provider with temp directory."""
        config = {"base_path": temp_storage}
        return LocalStorageProvider(config)
    
    @pytest.mark.asyncio
    async def test_upload_file(self, provider, sample_image):
        """Test file upload."""
        result = await provider.upload(
            file_data=sample_image.getvalue(),
            file_path="test/image.jpg",
            content_type="image/jpeg"
        )
        
        assert result["success"] is True
        assert "url" in result
        assert os.path.exists(os.path.join(provider.config["base_path"], "test", "image.jpg"))
    
    @pytest.mark.asyncio
    async def test_download_file(self, provider, sample_image):
        """Test file download."""
        # Upload first
        await provider.upload(
            file_data=sample_image.getvalue(),
            file_path="test/download.jpg",
            content_type="image/jpeg"
        )
        
        # Download
        result = await provider.download("test/download.jpg")
        assert result is not None
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_delete_file(self, provider, sample_image):
        """Test file deletion."""
        # Upload first
        await provider.upload(
            file_data=sample_image.getvalue(),
            file_path="test/delete.jpg",
            content_type="image/jpeg"
        )
        
        # Delete
        result = await provider.delete("test/delete.jpg")
        assert result["success"] is True
        assert not os.path.exists(os.path.join(provider.config["base_path"], "test", "delete.jpg"))

class TestStorageService:
    
    @pytest.fixture
    def storage_service(self, temp_storage):
        """Create storage service for testing."""
        config = {
            "primary_provider": "local",
            "providers": {
                "local": {"base_path": temp_storage}
            }
        }
        return StorageService(config)
    
    @pytest.mark.asyncio
    async def test_provider_selection(self, storage_service):
        """Test storage provider selection."""
        provider = await storage_service.get_provider("local")
        assert provider is not None
        assert isinstance(provider, LocalStorageProvider)
    
    @pytest.mark.asyncio
    async def test_fallback_provider(self, storage_service):
        """Test fallback to primary provider."""
        provider = await storage_service.get_provider("nonexistent")
        assert provider is not None  # Should fallback to primary
```

### Test Image Processor

```python
# tests/unit/test_image_processor.py
import pytest
from PIL import Image
import io
from services.image_processor import ImageProcessor

class TestImageProcessor:
    
    @pytest.fixture
    def processor(self):
        """Create image processor instance."""
        return ImageProcessor()
    
    @pytest.fixture
    def test_image(self):
        """Create test image."""
        image = Image.new('RGB', (800, 600), color='blue')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes.getvalue()
    
    @pytest.mark.asyncio
    async def test_resize_image(self, processor, test_image):
        """Test image resizing."""
        result = await processor.resize(test_image, width=400, height=300)
        
        # Verify result
        resized_image = Image.open(io.BytesIO(result))
        assert resized_image.size == (400, 300)
    
    @pytest.mark.asyncio
    async def test_compress_image(self, processor, test_image):
        """Test image compression."""
        original_size = len(test_image)
        compressed = await processor.compress(test_image, quality=50)
        
        assert len(compressed) < original_size
    
    @pytest.mark.asyncio
    async def test_format_conversion(self, processor, test_image):
        """Test format conversion."""
        png_data = await processor.convert_format(test_image, "PNG")
        
        # Verify format
        converted_image = Image.open(io.BytesIO(png_data))
        assert converted_image.format == "PNG"
    
    @pytest.mark.asyncio
    async def test_metadata_extraction(self, processor, test_image):
        """Test metadata extraction."""
        metadata = await processor.get_metadata(test_image)
        
        assert metadata["width"] == 800
        assert metadata["height"] == 600
        assert metadata["format"] == "JPEG"
```

## Integration Tests

### Test API Endpoints

```python
# tests/integration/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
import io
from PIL import Image

class TestMediaEndpoints:
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_upload_image(self, client, sample_image):
        """Test image upload endpoint."""
        files = {"file": ("test.jpg", sample_image, "image/jpeg")}
        data = {"user_id": "test-user"}
        
        response = client.post("/upload", files=files, data=data)
        assert response.status_code == 200
        
        result = response.json()
        assert "file_id" in result
        assert result["filename"] == "test.jpg"
    
    def test_upload_invalid_file(self, client):
        """Test upload with invalid file type."""
        files = {"file": ("test.exe", b"fake-exe-content", "application/exe")}
        data = {"user_id": "test-user"}
        
        response = client.post("/upload", files=files, data=data)
        assert response.status_code == 400
    
    def test_get_file_info(self, client, sample_image):
        """Test file info retrieval."""
        # Upload file first
        files = {"file": ("info_test.jpg", sample_image, "image/jpeg")}
        upload_response = client.post("/upload", files=files, data={"user_id": "test-user"})
        file_id = upload_response.json()["file_id"]
        
        # Get info
        response = client.get(f"/files/{file_id}")
        assert response.status_code == 200
        
        info = response.json()
        assert info["filename"] == "info_test.jpg"
        assert info["content_type"] == "image/jpeg"
    
    def test_create_variant(self, client, sample_image):
        """Test variant creation."""
        # Upload original file
        files = {"file": ("variant_test.jpg", sample_image, "image/jpeg")}
        upload_response = client.post("/upload", files=files, data={"user_id": "test-user"})
        file_id = upload_response.json()["file_id"]
        
        # Create thumbnail variant
        variant_data = {
            "variant_type": "thumbnail",
            "width": 150,
            "height": 150
        }
        
        response = client.post(f"/files/{file_id}/variants", json=variant_data)
        assert response.status_code == 200
        
        variant = response.json()
        assert variant["variant_type"] == "thumbnail"
```

### Test Database Operations

```python
# tests/integration/test_database_operations.py
import pytest
from sqlalchemy.orm import Session
from models.media_models import MediaFile, MediaVariant, ContentAnalysis
from datetime import datetime

class TestDatabaseOperations:
    
    def test_cascade_delete(self, test_db: Session):
        """Test cascade deletion of media files and variants."""
        # Create media file with variants
        media_file = MediaFile(
            filename="cascade_test.jpg",
            file_size=1024,
            content_type="image/jpeg",
            storage_provider="local",
            storage_path="/test/cascade_test.jpg",
            uploaded_by="user123"
        )
        test_db.add(media_file)
        test_db.flush()
        
        # Add variants
        variant1 = MediaVariant(
            media_file_id=media_file.id,
            variant_type="thumbnail",
            filename="cascade_test_thumb.jpg",
            file_size=256,
            storage_path="/test/thumbs/cascade_test_thumb.jpg"
        )
        variant2 = MediaVariant(
            media_file_id=media_file.id,
            variant_type="compressed",
            filename="cascade_test_comp.jpg",
            file_size=512,
            storage_path="/test/compressed/cascade_test_comp.jpg"
        )
        
        test_db.add_all([variant1, variant2])
        test_db.commit()
        
        # Verify creation
        assert len(media_file.variants) == 2
        
        # Delete media file
        test_db.delete(media_file)
        test_db.commit()
        
        # Verify cascade deletion
        remaining_variants = test_db.query(MediaVariant).filter(
            MediaVariant.media_file_id == media_file.id
        ).all()
        assert len(remaining_variants) == 0
    
    def test_soft_delete(self, test_db: Session):
        """Test soft deletion functionality."""
        media_file = MediaFile(
            filename="soft_delete_test.jpg",
            file_size=1024,
            content_type="image/jpeg",
            storage_provider="local",
            storage_path="/test/soft_delete_test.jpg",
            uploaded_by="user123"
        )
        test_db.add(media_file)
        test_db.commit()
        
        # Soft delete
        media_file.is_active = False
        media_file.deleted_at = datetime.utcnow()
        test_db.commit()
        
        # Verify soft deletion
        active_files = test_db.query(MediaFile).filter(MediaFile.is_active == True).all()
        assert media_file not in active_files
        
        # Verify file still exists in database
        all_files = test_db.query(MediaFile).all()
        assert media_file in all_files
```

## End-to-End Tests

### Test Upload Flow

```python
# tests/e2e/test_upload_flow.py
import pytest
from fastapi.testclient import TestClient
import asyncio
import time

class TestUploadFlow:
    
    @pytest.mark.asyncio
    async def test_complete_upload_flow(self, client, sample_image):
        """Test complete upload and processing flow."""
        # Step 1: Upload file
        files = {"file": ("flow_test.jpg", sample_image, "image/jpeg")}
        data = {
            "user_id": "test-user",
            "create_variants": True,
            "variant_types": "thumbnail,compressed"
        }
        
        upload_response = client.post("/upload", files=files, data=data)
        assert upload_response.status_code == 200
        
        upload_result = upload_response.json()
        file_id = upload_result["file_id"]
        
        # Step 2: Wait for processing (in real scenario, this would be async)
        await asyncio.sleep(1)
        
        # Step 3: Check file info
        info_response = client.get(f"/files/{file_id}")
        assert info_response.status_code == 200
        
        # Step 4: Check variants were created
        variants_response = client.get(f"/files/{file_id}/variants")
        assert variants_response.status_code == 200
        
        variants = variants_response.json()
        variant_types = [v["variant_type"] for v in variants]
        assert "thumbnail" in variant_types
        assert "compressed" in variant_types
        
        # Step 5: Download original file
        download_response = client.get(f"/files/{file_id}/download")
        assert download_response.status_code == 200
        assert len(download_response.content) > 0
```

## Performance Tests

### Load Testing

```python
# tests/performance/test_load.py
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient

class TestPerformance:
    
    def test_concurrent_uploads(self, client, sample_image):
        """Test concurrent file uploads."""
        def upload_file(file_index):
            files = {"file": (f"load_test_{file_index}.jpg", sample_image, "image/jpeg")}
            data = {"user_id": f"user-{file_index}"}
            
            start_time = time.time()
            response = client.post("/upload", files=files, data=data)
            end_time = time.time()
            
            return {
                "status_code": response.status_code,
                "duration": end_time - start_time,
                "file_index": file_index
            }
        
        # Test with 10 concurrent uploads
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(upload_file, i) for i in range(10)]
            results = [future.result() for future in futures]
        
        # Verify all uploads succeeded
        successful_uploads = [r for r in results if r["status_code"] == 200]
        assert len(successful_uploads) == 10
        
        # Check average response time
        avg_duration = sum(r["duration"] for r in results) / len(results)
        assert avg_duration < 5.0  # Should complete within 5 seconds
    
    def test_large_file_upload(self, client):
        """Test large file upload performance."""
        # Create 50MB test file
        large_file_content = b"0" * (50 * 1024 * 1024)
        
        files = {"file": ("large_test.bin", large_file_content, "application/octet-stream")}
        data = {"user_id": "test-user"}
        
        start_time = time.time()
        response = client.post("/upload", files=files, data=data)
        end_time = time.time()
        
        assert response.status_code == 200
        duration = end_time - start_time
        
        # Should handle 50MB upload within reasonable time
        assert duration < 30.0  # 30 seconds max
        
        # Calculate throughput
        throughput_mbps = (50 / duration) if duration > 0 else 0
        assert throughput_mbps > 1.0  # At least 1 MB/s
```

## Test Data and Fixtures

### Sample Files

```python
# tests/fixtures/generate_test_files.py
from PIL import Image
import io
import json

def create_test_images():
    """Generate test images of various sizes and formats."""
    test_images = {}
    
    # Small thumbnail
    small_img = Image.new('RGB', (150, 150), color='red')
    small_bytes = io.BytesIO()
    small_img.save(small_bytes, format='JPEG')
    test_images['small.jpg'] = small_bytes.getvalue()
    
    # Medium image
    medium_img = Image.new('RGB', (800, 600), color='green')
    medium_bytes = io.BytesIO()
    medium_img.save(medium_bytes, format='PNG')
    test_images['medium.png'] = medium_bytes.getvalue()
    
    # Large image
    large_img = Image.new('RGB', (2048, 1536), color='blue')
    large_bytes = io.BytesIO()
    large_img.save(large_bytes, format='JPEG', quality=95)
    test_images['large.jpg'] = large_bytes.getvalue()
    
    return test_images

def create_test_documents():
    """Generate test documents."""
    return {
        'test.txt': b"This is a test text file.",
        'test.json': json.dumps({"test": "data"}).encode(),
        'test.csv': b"name,age,city\nJohn,25,NYC\nJane,30,LA"
    }
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run specific test file
pytest tests/unit/test_storage_service.py

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Test Configuration

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    slow: Slow running tests
```

### CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Test Media Service

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost/test
        REDIS_URL: redis://localhost:6379/1
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

This comprehensive testing guide provides a solid foundation for ensuring the reliability and performance of the media service through automated testing at multiple levels.
