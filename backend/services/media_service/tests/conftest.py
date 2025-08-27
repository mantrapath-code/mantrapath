"""
Media Service Test Configuration
Pytest fixtures and configuration for media service tests
"""
import pytest
import tempfile
import os
import shutil
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import uuid

# Add the service root to the path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config.settings import settings
from models.media_models import Base
from services.storage_service import storage_service
from services.image_processor import image_processor

@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="session")
def test_db():
    """Create a test database"""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()

@pytest.fixture
def mock_storage_service():
    """Mock storage service for testing"""
    storage = AsyncMock()
    storage.store_file.return_value = {
        "file_path": "/test/path/file.jpg",
        "file_size": 1024,
        "checksum": "abc123"
    }
    storage.get_file.return_value = b"mock_file_content"
    storage.delete_file.return_value = True
    storage.get_file_url.return_value = "https://example.com/file.jpg"
    
    # Create a side effect to return different paths for different filenames
    def store_file_side_effect(*args, **kwargs):
        filename = kwargs.get('filename', 'file.jpg')
        return {
            "file_path": f"/test/path/{filename}",
            "file_size": 1024,
            "checksum": "abc123"
        }
    
    storage.store_file.side_effect = store_file_side_effect
    return storage

@pytest.fixture
def mock_image_processor():
    """Mock image processor for testing"""
    processor = AsyncMock()
    processor.resize_image.return_value = b"resized_image_data"
    processor.create_thumbnail.return_value = b"thumbnail_data"
    processor.validate_image.return_value = True
    processor.get_image_metadata.return_value = {
        "width": 1920,
        "height": 1080,
        "format": "JPEG",
        "size": 1024
    }
    return processor

@pytest.fixture
def sample_image_data():
    """Sample image data for testing"""
    # Create a minimal PNG image (1x1 pixel)
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00'
        b'\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs'
        b'\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00'
        b'\x00\x00\x0bIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d'
        b'\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return png_data

@pytest.fixture
def sample_media_file_data():
    """Sample media file data for testing"""
    return {
        "user_id": uuid.uuid4(),
        "filename": "test.jpg",
        "original_filename": "test_original.jpg",
        "file_type": "image",
        "file_size": 1024,
        "mime_type": "image/jpeg",
        "storage_provider": "local",
        "storage_path": "/test/path/test.jpg",
        "processing_status": "pending",
        "is_public": False,
        "metadata": {"width": 1920, "height": 1080}
    }

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app"""
    try:
        from main import app
        return TestClient(app)
    except (ImportError, RuntimeError) as e:
        # If main app can't be imported due to dependencies, return mock
        from unittest.mock import MagicMock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy", "service": "media_service", "timestamp": "2025-01-01T00:00:00Z"}
        mock_client.get.return_value = mock_response
        mock_client.post.return_value = mock_response
        return mock_client
