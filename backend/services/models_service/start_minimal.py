#!/usr/bin/env python3
"""
Minimal Models Service Startup
Starts the service without requiring model downloads to complete first
"""

import os
import sys
import logging
from pathlib import Path
import uvicorn

# Add the service directory to Python path
service_dir = Path(__file__).parent
sys.path.insert(0, str(service_dir))

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_minimal_environment():
    """Setup minimal environment for service to start"""
    # Ensure models directory exists
    models_dir = service_dir / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Create minimal model cache directories
    (models_dir / "stt").mkdir(exist_ok=True)
    (models_dir / "tts").mkdir(exist_ok=True)
    (models_dir / "nlp").mkdir(exist_ok=True)
    
    # Set environment variables for minimal startup
    os.environ.setdefault("MODELS_SERVICE_PORT", "8080")
    os.environ.setdefault("MODELS_DIR", str(models_dir))
    os.environ.setdefault("MODELS_SERVICE_MODE", "minimal")
    
    logger.info(f"✅ Minimal environment setup complete")
    logger.info(f"   Models directory: {models_dir}")
    logger.info(f"   Service port: {os.environ['MODELS_SERVICE_PORT']}")

def main():
    """Start models service in minimal mode"""
    try:
        setup_minimal_environment()
        
        # Import main after environment setup
        from main import app
        
        port = int(os.environ.get("MODELS_SERVICE_PORT", 8080))
        
        logger.info(f"🚀 Starting Models Service (Minimal Mode) on port {port}")
        logger.info("   Service will start without pre-loaded models")
        logger.info("   Models will be loaded on-demand when requested")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            reload=False,
            workers=1,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start Models Service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
