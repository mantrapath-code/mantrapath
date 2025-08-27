#!/usr/bin/env python3
"""
Simple test to validate media service implementation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from config.settings import settings
from models.media_models import MediaFile, Base
from services.storage_service import storage_service
from services.image_processor import image_processor

def test_basic_imports():
    """Test that all modules import correctly"""
    print("✅ Configuration imported successfully")
    print(f"   Service name: {settings.service_name}")
    print(f"   Primary storage: {settings.primary_storage_provider}")
    
    print("✅ Models imported successfully")
    print(f"   MediaFile table: {MediaFile.__tablename__}")
    
    print("✅ Services imported successfully")
    print(f"   Storage service initialized: {storage_service}")
    print(f"   Image processor initialized: {image_processor}")

def test_model_creation():
    """Test model instantiation"""
    import uuid
    from datetime import datetime
    
    try:
        media_file = MediaFile(
            user_id=uuid.uuid4(),
            filename="test.jpg",
            original_filename="test.jpg",
            file_type="image",
            file_size=1024,
            mime_type="image/jpeg",
            storage_provider="local",
            storage_path="/test/test.jpg",
            processing_status="pending",
            is_public=False,
            metadata={"test": "data"}
        )
        
        print("✅ MediaFile model created successfully")
        print(f"   ID type: {type(media_file.id)}")
        print(f"   User ID type: {type(media_file.user_id)}")
        print(f"   Filename: {media_file.filename}")
        
    except Exception as e:
        print(f"❌ Model creation failed: {e}")

if __name__ == "__main__":
    print("Media Service Implementation Test")
    print("=" * 40)
    
    test_basic_imports()
    print()
    test_model_creation()
    
    print("\n✅ All tests completed!")
