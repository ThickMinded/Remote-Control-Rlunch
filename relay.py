#!/usr/bin/env python3
"""
WebSocket Relay Server for Remote Control
Runs on Render.com and relays messages between server and clients
"""

import asyncio
import websockets
import json
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RelayServer:
    def __init__(self):
        self.servers = {}  # {server_id: websocket}
        self.clients = {}  # {client_id: websocket}
        self.client_to_server = {}  # {client_id: server_id}
        
    async def register_server(self, websocket, server_id):
        """Register a new server (computer to be controlled)"""
        self.servers[server_id] = websocket
        logger.info(f"✅ Server registered: {server_id}")
        await websocket.send(json.dumps({'type': 'registered', 'server_id': server_id}))
        
    async def register_client(self, websocket, client_id, server_id):
        """Register a new client (controller)"""
        self.clients[client_id] = websocket
        self.client_to_server[client_id] = server_id
        logger.info(f"✅ Client {client_id} connected to server {server_id}")
        
        # Notify client of successful connection
        await websocket.send(json.dumps({
            'type': 'connected',
            'server_id': server_id
        }))
        
    async def handle_connection(self, websocket, path):
        """Handle new WebSocket connections"""
        client_id = None
        server_id = None
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get('type')
                    
                    # Handle registration
                    if msg_type == 'register_server':
                        server_id = data.get('server_id')
                        await self.register_server(websocket, server_id)
                        
                    elif msg_type == 'register_client':
                        client_id = data.get('client_id')
                        target_server = data.get('server_id')
                        
                        if target_server not in self.servers:
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': f'Server "{target_server}" not found'
                            }))
                            continue
                            
                        await self.register_client(websocket, client_id, target_server)
                    
                    # Relay messages from client to server
                    elif client_id and msg_type in ['mouse', 'keyboard', 'request_frame', 'info_request']:
                        target_server = self.client_to_server.get(client_id)
                        if target_server and target_server in self.servers:
                            data['client_id'] = client_id  # Add client ID for response routing
                            await self.servers[target_server].send(json.dumps(data))
                        else:
                            logger.warning(f"Client {client_id} has no valid server connection")
                    
                    # Relay messages from server to client
                    elif server_id and msg_type in ['screen', 'info']:
                        target_client = data.get('target_client')
                        if target_client and target_client in self.clients:
                            await self.clients[target_client].send(json.dumps(data))
                        else:
                            logger.warning(f"Server {server_id} tried to send to unknown client {target_client}")
                            
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received")
                except Exception as e:
                    logger.error(f"Message handling error: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            # Cleanup on disconnect
            if server_id and server_id in self.servers:
                del self.servers[server_id]
                logger.info(f"❌ Server disconnected: {server_id}")
            if client_id and client_id in self.clients:
                del self.clients[client_id]
                if client_id in self.client_to_server:
                    del self.client_to_server[client_id]
                logger.info(f"❌ Client disconnected: {client_id}")

async def main():
    """Start the relay server"""
    # Railway provides PORT environment variable
    port = int(os.environ.get('PORT', 8000))
    host = '0.0.0.0'
    
    relay = RelayServer()
    
    logger.info("=" * 70)
    logger.info("🌐 Remote Control Relay Server (Railway.app)")
    logger.info("=" * 70)
    logger.info(f"Starting relay on {host}:{port}")
    logger.info("=" * 70)
    
    async with websockets.serve(
        relay.handle_connection,
        host,
        port,
        ping_interval=20,
        ping_timeout=10,
        max_size=10*1024*1024
    ):
        logger.info("✅ Relay server is running on Railway!")
        logger.info("Waiting for servers and clients to connect...")
        await asyncio.Future()  # Run forever

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n🛑 Relay server stopped")
