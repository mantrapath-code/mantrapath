import asyncio
import os
import sys
from pathlib import Path

# Add the shared directory to Python path
current_dir = Path(__file__).parent
shared_dir = current_dir.parent.parent / "shared"
sys.path.insert(0, str(shared_dir))

import uvicorn
from app import create_app
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

async def main():
    """Main entry point for Voice Event Processor Service"""
    try:
        logger.info("Starting Voice Event Processor Service")
        
        # Create the FastAPI app (not async)
        app = create_app()
        
        # Start the service
        config = uvicorn.Config(
            app=app,
            host=os.getenv("VOICE_EVENT_PROCESSOR_HOST", "0.0.0.0"),
            port=int(os.getenv("VOICE_EVENT_PROCESSOR_PORT", 8015)),
            log_level=os.getenv("LOG_LEVEL", "info").lower(),
            reload=os.getenv("ENVIRONMENT", "production") == "development"
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        logger.error("Failed to start Voice Event Processor Service", error=str(e))
        raise

if __name__ == "__main__":
    asyncio.run(main())
