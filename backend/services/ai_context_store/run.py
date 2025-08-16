#!/usr/bin/env python3
"""
Entry point for AI Context Store Service
This file handles import paths and runs the FastAPI application
"""

import os
import sys
import logging

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.dirname(os.path.dirname(current_dir))

# Setup Python path for both local and Docker environments
paths_to_add = [
    current_dir,  # /app in Docker
    backend_root,  # backend root directory
    os.path.join(backend_root, 'shared'),  # shared modules
    '/app',  # Docker app directory
    '/app/shared',  # Docker shared directory
    '/app/models',  # Docker models directory  
    '/app/services',  # Docker services directory
    '/app/api',  # Docker api directory
]

for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug: Log the Python path
logger.info(f"Current directory: {current_dir}")
logger.info(f"Python path: {sys.path}")
logger.info(f"Files in current directory: {os.listdir(current_dir)}")
if os.path.exists(os.path.join(current_dir, 'models')):
    logger.info(f"Models directory exists: {os.listdir(os.path.join(current_dir, 'models'))}")
else:
    logger.warning("Models directory does not exist!")

def main():
    """Main entry point"""
    try:
        logger.info("🚀 Initializing AI Context Store Service...")
        
        # Import and run the main application
        # Import main module after setting up the path
        import main
        app = main.app
        
        # Get port from environment
        port = int(os.getenv("AI_CONTEXT_STORE_PORT", 8013))
        
        # Run with uvicorn
        import uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0", 
            port=port,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start AI Context Store Service: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
