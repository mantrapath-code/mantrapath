#!/usr/bin/env python3
"""
Simple WebSocket server for development - provides basic WebSocket connectivity
"""
import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Set

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connected clients
connected_clients: Set[websockets.WebSocketServerProtocol] = set()

async def handle_websocket(websocket):
    """Handle WebSocket connection"""
    connected_clients.add(websocket)
    logger.info(f"Client connected. Total clients: {len(connected_clients)}")
    
    try:
        # Send welcome message
        welcome_message = {
            "type": "connection",
            "data": {"message": "Connected to MantraPath WebSocket"},
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send(json.dumps(welcome_message))
        
        # Keep connection alive and handle incoming messages
        async for message in websocket:
            try:
                data = json.loads(message)
                logger.info(f"Received message: {data}")
                
                # Echo back the message
                response = {
                    "type": "echo",
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(response))
                
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received: {message}")
                
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        connected_clients.discard(websocket)
        logger.info(f"Client removed. Total clients: {len(connected_clients)}")

async def broadcast_periodic_message():
    """Send periodic messages to all connected clients"""
    while True:
        await asyncio.sleep(30)  # Send every 30 seconds
        if connected_clients:
            message = {
                "type": "heartbeat",
                "data": {"message": "WebSocket connection is healthy"},
                "timestamp": datetime.now().isoformat()
            }
            # Send to all connected clients
            disconnected = set()
            for client in connected_clients:
                try:
                    await client.send(json.dumps(message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            # Remove disconnected clients
            for client in disconnected:
                connected_clients.discard(client)

async def main():
    """Start the WebSocket server"""
    logger.info("Starting WebSocket server on ws://localhost:8007/ws")
    
    # Start the heartbeat task
    asyncio.create_task(broadcast_periodic_message())
    
    # Start WebSocket server
    server = await websockets.serve(handle_websocket, "localhost", 8007)
    
    logger.info("WebSocket server is running...")
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("WebSocket server stopped")
