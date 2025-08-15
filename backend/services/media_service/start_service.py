#!/usr/bin/env python3
"""
Media Service Startup Script
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the service directory to Python path
service_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(service_dir))

def start_media_service():
    """Start the media service"""
    print("🚀 Starting MantraPath Media Service...")
    print(f"📁 Service directory: {service_dir}")
    
    # Create uploads directory if it doesn't exist
    uploads_dir = service_dir / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    print(f"📦 Uploads directory: {uploads_dir}")
    
    # Set environment defaults
    os.environ.setdefault("DATABASE_URL", "sqlite:///media_service.db")
    os.environ.setdefault("PRIMARY_STORAGE_PROVIDER", "local")
    os.environ.setdefault("LOCAL_STORAGE_PATH", str(uploads_dir))
    
    try:
        # Import the app
        from main import app
        
        # Run the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8009,
            reload=True,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Failed to import media service: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start media service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_media_service()
