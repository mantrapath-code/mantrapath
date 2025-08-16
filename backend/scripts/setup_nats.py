#!/usr/bin/env python3
"""
NATS Setup and Validation Script for MantraPath BK-004
Sets up NATS server with proper JetStream configuration for production use
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import nats
    from nats.js import JetStreamContext
    NATS_AVAILABLE = True
except ImportError:
    logger.error("❌ NATS package not installed. Run: pip install nats-py")
    NATS_AVAILABLE = False
    sys.exit(1)


class NATSSetup:
    """NATS server setup and configuration manager"""
    
    def __init__(self, nats_url: str = "nats://localhost:4222"):
        self.nats_url = nats_url
        self.nc = None
        self.js = None
        
    async def connect(self) -> bool:
        """Connect to NATS server"""
        try:
            self.nc = await nats.connect(
                servers=[self.nats_url],
                name="mantrapath-setup",
                connect_timeout=10.0
            )
            self.js = self.nc.jetstream()
            logger.info(f"✅ Connected to NATS server at {self.nats_url}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to NATS: {e}")
            return False
    
    async def setup_production_streams(self) -> bool:
        """Set up all MantraPath production streams"""
        if not self.js:
            logger.error("❌ No JetStream connection available")
            return False
        
        streams_config = [
            {
                "name": "mantrapath-voice",
                "subjects": ["voice.*"],
                "description": "Voice activity, speech recognition, and intent classification events",
                "max_msgs": 1000000,
                "max_age": 7 * 24 * 3600,  # 7 days
                "storage": "file"
            },
            {
                "name": "mantrapath-ai",
                "subjects": ["ai.*", "intelligence.*"],
                "description": "AI processing, inference, and intelligence events",
                "max_msgs": 2000000,
                "max_age": 14 * 24 * 3600,  # 14 days
                "storage": "file"
            },
            {
                "name": "mantrapath-mood",
                "subjects": ["mood.*"],
                "description": "Mood tracking, analysis, and trend events",
                "max_msgs": 500000,
                "max_age": 30 * 24 * 3600,  # 30 days
                "storage": "file"
            },
            {
                "name": "mantrapath-journal",
                "subjects": ["journal.*"],
                "description": "Journal entry creation and analysis events",
                "max_msgs": 1000000,
                "max_age": 90 * 24 * 3600,  # 90 days
                "storage": "file"
            },
            {
                "name": "mantrapath-cultural",
                "subjects": ["cultural.*", "regional.*"],
                "description": "Cultural intelligence and regional adaptation events",
                "max_msgs": 100000,
                "max_age": 30 * 24 * 3600,  # 30 days
                "storage": "file"
            },
            {
                "name": "mantrapath-system",
                "subjects": ["system.*", "health.*", "metrics.*"],
                "description": "System health, metrics, and monitoring events",
                "max_msgs": 500000,
                "max_age": 7 * 24 * 3600,  # 7 days
                "storage": "file"
            }
        ]
        
        success_count = 0
        
        for config in streams_config:
            try:
                # Try to get existing stream info
                try:
                    info = await self.js.stream_info(config["name"])
                    logger.info(f"✅ Stream '{config['name']}' already exists (msgs: {info.state.messages})")
                    success_count += 1
                    continue
                except:
                    pass  # Stream doesn't exist, create it
                
                # Create new stream
                await self.js.add_stream(
                    name=config["name"],
                    subjects=config["subjects"],
                    max_msgs=config["max_msgs"],
                    max_age=config["max_age"],
                    storage=config["storage"],
                    description=config["description"]
                )
                
                logger.info(f"✅ Created stream '{config['name']}' with subjects {config['subjects']}")
                success_count += 1
                
            except Exception as e:
                logger.error(f"❌ Failed to create stream '{config['name']}': {e}")
        
        logger.info(f"📊 Stream setup complete: {success_count}/{len(streams_config)} streams ready")
        return success_count == len(streams_config)
    
    async def validate_setup(self) -> Dict[str, Any]:
        """Validate NATS setup and return status"""
        if not self.js:
            return {"status": "error", "message": "No JetStream connection"}
        
        try:
            # Get account info
            account_info = await self.js.account_info()
            
            # List all streams
            streams = []
            async for stream in self.js.streams_info():
                streams.append({
                    "name": stream.config.name,
                    "subjects": stream.config.subjects,
                    "messages": stream.state.messages,
                    "bytes": stream.state.bytes,
                    "consumers": stream.state.consumers
                })
            
            validation = {
                "status": "healthy",
                "jetstream": {
                    "memory": account_info.memory,
                    "storage": account_info.store,
                    "streams": len(streams),
                    "api_total": account_info.api.total,
                    "api_errors": account_info.api.errors
                },
                "streams": streams,
                "timestamp": time.time()
            }
            
            return validation
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": time.time()
            }
    
    async def test_publish_subscribe(self) -> bool:
        """Test basic publish/subscribe functionality"""
        if not self.js:
            return False
        
        try:
            test_subject = "system.test"
            test_data = {
                "test_id": "bk004-validation",
                "timestamp": time.time(),
                "message": "BK-004 NATS validation test"
            }
            
            # Publish test message
            ack = await self.js.publish(test_subject, json.dumps(test_data).encode())
            logger.info(f"✅ Test message published to {test_subject} (seq: {ack.seq})")
            
            # Try to consume the message
            psub = await self.js.pull_subscribe(test_subject, "test-consumer")
            msgs = await psub.fetch(1, timeout=5.0)
            
            if msgs:
                msg = msgs[0]
                received_data = json.loads(msg.data.decode())
                await msg.ack()
                
                if received_data["test_id"] == test_data["test_id"]:
                    logger.info("✅ Test message successfully received and validated")
                    return True
                else:
                    logger.error("❌ Test message data mismatch")
                    return False
            else:
                logger.error("❌ No test message received")
                return False
                
        except Exception as e:
            logger.error(f"❌ Publish/subscribe test failed: {e}")
            return False
    
    async def close(self):
        """Close NATS connection"""
        if self.nc:
            await self.nc.close()
            logger.info("🔌 NATS connection closed")


async def check_nats_server_running() -> bool:
    """Check if NATS server is running"""
    try:
        proc = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return "nats-server" in proc.stdout
    except:
        return False


async def start_nats_server() -> bool:
    """Start NATS server with JetStream enabled"""
    try:
        # Check if nats-server is available
        proc = subprocess.run(
            ["which", "nats-server"],
            capture_output=True,
            text=True
        )
        
        if proc.returncode != 0:
            logger.error("❌ nats-server not found. Install from: https://docs.nats.io/running-a-nats-service/introduction/installation")
            return False
        
        # Start NATS server with JetStream
        logger.info("🚀 Starting NATS server with JetStream...")
        proc = subprocess.Popen([
            "nats-server",
            "--jetstream",
            "--store_dir", "/tmp/nats-jetstream",
            "--port", "4222"
        ])
        
        # Give it time to start
        await asyncio.sleep(3)
        
        # Check if it's running
        if await check_nats_server_running():
            logger.info("✅ NATS server started successfully")
            return True
        else:
            logger.error("❌ Failed to start NATS server")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error starting NATS server: {e}")
        return False


async def main():
    """Main setup and validation function"""
    logger.info("🚀 MantraPath NATS Setup and Validation")
    logger.info("=" * 50)
    
    # Check if NATS server is running
    if not await check_nats_server_running():
        logger.warning("⚠️  NATS server not running")
        
        # Ask user if they want to start it
        response = input("Start NATS server? (y/n): ").lower().strip()
        if response == 'y':
            if not await start_nats_server():
                logger.error("❌ Cannot start NATS server. Please start manually.")
                return 1
        else:
            logger.info("ℹ️  To start manually: nats-server --jetstream")
            return 1
    
    # Initialize NATS setup
    setup = NATSSetup()
    
    try:
        # Connect to NATS
        if not await setup.connect():
            return 1
        
        # Setup production streams
        logger.info("\n📦 Setting up production streams...")
        if await setup.setup_production_streams():
            logger.info("✅ All streams configured successfully")
        else:
            logger.warning("⚠️  Some streams failed to configure")
        
        # Validate setup
        logger.info("\n🔍 Validating NATS setup...")
        validation = await setup.validate_setup()
        
        if validation["status"] == "healthy":
            logger.info("✅ NATS validation successful")
            logger.info(f"📊 JetStream Stats:")
            logger.info(f"  Streams: {validation['jetstream']['streams']}")
            logger.info(f"  API calls: {validation['jetstream']['api_total']}")
            logger.info(f"  API errors: {validation['jetstream']['api_errors']}")
            
            # Show stream details
            logger.info(f"\n📋 Configured Streams:")
            for stream in validation["streams"]:
                logger.info(f"  • {stream['name']}: {stream['messages']} messages, {stream['consumers']} consumers")
        else:
            logger.error(f"❌ Validation failed: {validation.get('message', 'Unknown error')}")
            return 1
        
        # Test publish/subscribe
        logger.info("\n🧪 Testing publish/subscribe...")
        if await setup.test_publish_subscribe():
            logger.info("✅ Publish/subscribe test passed")
        else:
            logger.error("❌ Publish/subscribe test failed")
            return 1
        
        logger.info("\n🎉 NATS setup and validation complete!")
        logger.info("🔧 BK-004 Service Event Integration is ready for production use")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return 1
    finally:
        await setup.close()


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)
