#!/usr/bin/env python3
"""
Replit Relay Server - Bridge between server and clients
Runs on Replit to enable internet access without port forwarding
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RelayServer:
    def __init__(self, host='0.0.0.0', port=8765):
        self.host = host
        self.port = port
        self.servers = {}  # {server_id: websocket}
        self.clients = {}  # {client_id: websocket}
        self.server_to_clients = {}  # {server_id: [client_ids]}
        
    async def handle_connection(self, websocket, path):
        """Handle incoming WebSocket connection"""
        remote_addr = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        connection_id = None
        connection_type = None
        server_id = None
        
        try:
            # First message should identify connection type
            message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            data = json.loads(message)
            
            connection_type = data.get('type')
            
            if connection_type == 'register_server':
                # This is a server (host computer) connecting
                server_id = data.get('server_id', f'server_{len(self.servers)}')
                connection_id = server_id
                
                self.servers[server_id] = websocket
                self.server_to_clients[server_id] = []
                
                logger.info(f"✅ Server registered: {server_id} from {remote_addr}")
                
                # Send confirmation
                await websocket.send(json.dumps({
                    'type': 'registered',
                    'server_id': server_id,
                    'status': 'success'
                }))
                
                # Handle server messages
                await self.handle_server(server_id, websocket)
                
            elif connection_type == 'register_client':
                # This is a client (controller) connecting
                target_server = data.get('server_id', list(self.servers.keys())[0] if self.servers else None)
                
                if not target_server or target_server not in self.servers:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Server not available'
                    }))
                    return
                
                client_id = f'client_{len(self.clients)}_{remote_addr}'
                connection_id = client_id
                
                self.clients[client_id] = {
                    'websocket': websocket,
                    'server_id': target_server
                }
                self.server_to_clients[target_server].append(client_id)
                
                logger.info(f"✅ Client connected: {client_id} -> Server: {target_server}")
                
                # Send confirmation
                await websocket.send(json.dumps({
                    'type': 'registered',
                    'client_id': client_id,
                    'server_id': target_server,
                    'status': 'success'
                }))
                
                # Handle client messages
                await self.handle_client(client_id, target_server, websocket)
                
            else:
                logger.warning(f"Unknown connection type: {connection_type}")
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'Invalid connection type'
                }))
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for registration from {remote_addr}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from {remote_addr}")
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed during registration: {remote_addr}")
        except Exception as e:
            logger.error(f"Registration error: {e}")
        finally:
            # Cleanup
            if connection_type == 'register_server' and connection_id:
                if connection_id in self.servers:
                    del self.servers[connection_id]
                if connection_id in self.server_to_clients:
                    # Notify all clients that server disconnected
                    for client_id in self.server_to_clients[connection_id]:
                        if client_id in self.clients:
                            try:
                                await self.clients[client_id]['websocket'].send(json.dumps({
                                    'type': 'server_disconnected'
                                }))
                            except:
                                pass
                    del self.server_to_clients[connection_id]
                logger.info(f"❌ Server unregistered: {connection_id}")
                
            elif connection_type == 'register_client' and connection_id:
                if connection_id in self.clients:
                    target = self.clients[connection_id]['server_id']
                    del self.clients[connection_id]
                    if target in self.server_to_clients:
                        self.server_to_clients[target].remove(connection_id)
                logger.info(f"❌ Client disconnected: {connection_id}")
    
    async def handle_server(self, server_id, websocket):
        """Handle messages from server (host computer)"""
        try:
            async for message in websocket:
                data = json.loads(message)
                
                # Server is sending data (like screen frames) to clients
                target_client = data.get('target_client')
                
                if target_client and target_client in self.clients:
                    # Send to specific client
                    client_ws = self.clients[target_client]['websocket']
                    try:
                        await client_ws.send(message)
                    except Exception as e:
                        logger.error(f"Error sending to client {target_client}: {e}")
                else:
                    # Broadcast to all clients connected to this server
                    if server_id in self.server_to_clients:
                        for client_id in self.server_to_clients[server_id]:
                            if client_id in self.clients:
                                try:
                                    await self.clients[client_id]['websocket'].send(message)
                                except Exception as e:
                                    logger.error(f"Error broadcasting to {client_id}: {e}")
                                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Server connection closed: {server_id}")
        except Exception as e:
            logger.error(f"Server handler error: {e}")
    
    async def handle_client(self, client_id, server_id, websocket):
        """Handle messages from client (controller)"""
        try:
            async for message in websocket:
                # Client is sending commands (mouse/keyboard) to server
                if server_id in self.servers:
                    server_ws = self.servers[server_id]
                    try:
                        # Add client_id to message so server knows who to respond to
                        data = json.loads(message)
                        data['client_id'] = client_id
                        await server_ws.send(json.dumps(data))
                    except Exception as e:
                        logger.error(f"Error sending to server {server_id}: {e}")
                else:
                    # Server disconnected
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Server disconnected'
                    }))
                    break
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client connection closed: {client_id}")
        except Exception as e:
            logger.error(f"Client handler error: {e}")
    
    async def status_reporter(self):
        """Periodically report relay status"""
        while True:
            await asyncio.sleep(30)
            logger.info(f"📊 Status - Servers: {len(self.servers)}, Clients: {len(self.clients)}")
            for server_id, client_list in self.server_to_clients.items():
                logger.info(f"   Server '{server_id}': {len(client_list)} clients")
    
    async def start(self):
        """Start the relay server"""
        logger.info("=" * 60)
        logger.info("🌐 Remote Control Relay Server")
        logger.info("=" * 60)
        logger.info(f"Starting relay on {self.host}:{self.port}")
        logger.info("Waiting for servers and clients to connect...")
        logger.info("=" * 60)
        
        # Start status reporter
        asyncio.create_task(self.status_reporter())
        
        async with websockets.serve(
            self.handle_connection, 
            self.host, 
            self.port,
            ping_interval=20,
            ping_timeout=10,
            max_size=10*1024*1024  # 10MB max message size
        ):
            logger.info("✅ Relay server is running!")
            await asyncio.Future()  # Run forever

def main():
    """Main entry point"""
    relay = RelayServer(host='0.0.0.0', port=8080)
    
    try:
        asyncio.run(relay.start())
    except KeyboardInterrupt:
        print("\n🛑 Relay server stopped")
    except Exception as e:
        logger.error(f"Relay server error: {e}")
        raise

if __name__ == "__main__":
    main()
