#!/usr/bin/env python3
"""
Remote Control Server - Local Network Version
Hosts a WebSocket server for direct local network connections
No relay required - client connects directly to this server
"""

import asyncio
import websockets
import json
import base64
import io
import pyautogui
import mss
from PIL import Image
import logging
import sys
import pyperclip
from pynput import keyboard
import socket
from datetime import datetime
import os
import ctypes

# Hide console window on Windows
if sys.platform == 'win32':
    try:
        # Get handle to console window
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        hwnd = kernel32.GetConsoleWindow()
        if hwnd:
            user32.ShowWindow(hwnd, 0)  # SW_HIDE = 0
    except Exception:
        pass  # Silently fail if hiding doesn't work

# Configure logging
file_handler = logging.FileHandler('server_local.log', mode='w', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)
logger.info("=" * 60)
logger.info("Local Server logging initialized")
logger.info("=" * 60)

# Configure pyautogui
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01

class LocalRemoteControlServer:
    def __init__(self, host='0.0.0.0', port=8765):
        self.host = host
        self.port = port
        self.websocket = None
        self.screen_width, self.screen_height = pyautogui.size()
        self.running = False
        self.connected_clients = set()
        
        # Communication mode
        self.communication_mode = False
        self.keyboard_listener = None
        self.current_client = None
    
    async def capture_screen(self, quality=95, scale=1.0):
        """Capture screen"""
        return await asyncio.to_thread(self._capture_screen_sync, quality, scale)

    def _capture_screen_sync(self, quality=95, scale=1.0):
        """Synchronous screen capture"""
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                new_size = (int(img.width * scale), int(img.height * scale))
                if scale != 1.0:
                    img = img.resize(new_size, Image.Resampling.BILINEAR)
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality, optimize=False)
                img_bytes = buffer.getvalue()
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                return {
                    'type': 'screen',
                    'data': img_base64,
                    'width': new_size[0],
                    'height': new_size[1],
                    'original_width': self.screen_width,
                    'original_height': self.screen_height
                }
        except Exception as e:
            logger.error(f"Screen capture error: {e}")
            return None
    
    async def capture_screenshot(self):
        """Capture screenshot and send to client"""
        try:
            # Capture full resolution screenshot
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                
                # Convert to PNG bytes
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                img_bytes = buffer.getvalue()
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                
                logger.info(f"Screenshot captured, sending to client")
                
                return {
                    'type': 'screenshot_data',
                    'data': img_base64,
                    'width': img.width,
                    'height': img.height
                }
        except Exception as e:
            logger.error(f"Screenshot capture error: {e}")
            return {
                'type': 'screenshot_error',
                'error': str(e)
            }
    
    async def handle_mouse_event(self, data):
        """Handle mouse events"""
        try:
            event_type = data.get('event')
            x = int(data.get('x', 0) * self.screen_width)
            y = int(data.get('y', 0) * self.screen_height)
            detached = data.get('detached', False)
            
            if event_type == 'move':
                # Always move cursor to make it visible (unless detached)
                if not detached:
                    pyautogui.moveTo(x, y, duration=0)
                
            elif event_type == 'click':
                button = data.get('button', 'left')
                if not detached:
                    pyautogui.moveTo(x, y, duration=0)
                pyautogui.click(button=button)
                
            elif event_type == 'double_click':
                if not detached:
                    pyautogui.moveTo(x, y, duration=0)
                pyautogui.doubleClick()
                
            elif event_type == 'down':
                button = data.get('button', 'left')
                if not detached:
                    pyautogui.moveTo(x, y, duration=0)
                pyautogui.mouseDown(button=button)
                
            elif event_type == 'up':
                button = data.get('button', 'left')
                if not detached:
                    pyautogui.moveTo(x, y, duration=0)
                pyautogui.mouseUp(button=button)
                
            elif event_type == 'scroll':
                scroll_amount = data.get('amount', 0)
                pyautogui.scroll(int(scroll_amount), x, y)
                
            logger.debug(f"Mouse event: {event_type} at ({x}, {y}), detached={detached}")
            
        except Exception as e:
            logger.error(f"Mouse event error: {e}")
    
    def handle_keyboard_event(self, data):
        """Handle keyboard events"""
        try:
            event_type = data.get('event')
            key = data.get('key', '')
            
            if event_type == 'press':
                if key.lower() == 'c':
                    pyautogui.hotkey('ctrl', 'c')
                    logger.info("📋 Executed Ctrl+C (copy)")
                elif key.lower() == 'v':
                    pyautogui.hotkey('ctrl', 'v')
                    logger.info("📋 Executed Ctrl+V (paste)")
                else:
                    pyautogui.press(key)
            elif event_type == 'down':
                pyautogui.keyDown(key)
            elif event_type == 'up':
                pyautogui.keyUp(key)
            elif event_type == 'write':
                text = data.get('text', '')
                pyautogui.write(text, interval=0.01)
                
            logger.debug(f"Keyboard event: {event_type} - {key}")
            
        except Exception as e:
            logger.error(f"Keyboard event error: {e}")
    
    def start_keyboard_listener(self):
        """Start keyboard listener for communication mode"""
        from pynput.keyboard import Key, KeyCode, Listener
        
        keys_pressed = set()
        
        def on_press(key):
            keys_pressed.add(key)
            
            ctrl = Key.ctrl_l in keys_pressed or Key.ctrl in keys_pressed
            shift = Key.shift in keys_pressed or Key.shift_r in keys_pressed
            c_key = KeyCode.from_char('c') in keys_pressed or KeyCode.from_char('C') in keys_pressed
            
            if ctrl and shift and c_key:
                self.toggle_communication_mode(not self.communication_mode)
        
        def on_release(key):
            try:
                keys_pressed.discard(key)
            except KeyError:
                pass
        
        self.keyboard_listener = Listener(on_press=on_press, on_release=on_release)
        self.keyboard_listener.start()
        logger.info("⌨️ Keyboard listener started (Ctrl+Shift+C for communication mode)")
    
    def toggle_communication_mode(self, enabled):
        """Toggle communication mode"""
        self.communication_mode = enabled
        logger.info(f"💬 Communication mode {'ENABLED' if enabled else 'DISABLED'}")
        
        # Notify client
        if self.current_client:
            asyncio.create_task(self.send_to_client(self.current_client, {
                'type': 'communication_mode',
                'enabled': enabled
            }))
    
    async def send_to_client(self, websocket, message):
        """Send message to specific client"""
        try:
            if websocket:
                await websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Send error: {e}")
    
    async def handle_client(self, websocket, path=None):
        """Handle client connection"""
        client_addr = websocket.remote_address
        logger.info(f"✅ Client connected: {client_addr}")
        self.connected_clients.add(websocket)
        self.current_client = websocket
        
        # Start keyboard listener if not already running
        if not self.keyboard_listener:
            self.start_keyboard_listener()
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get('type')
                    
                    if msg_type == 'mouse':
                        await self.handle_mouse_event(data)
                        
                    elif msg_type == 'keyboard':
                        self.handle_keyboard_event(data)
                        
                    elif msg_type == 'clipboard_sync':
                        clipboard_text = data.get('text', '')
                        if clipboard_text:
                            pyperclip.copy(clipboard_text)
                            logger.info(f"📋 Clipboard synced from client: {len(clipboard_text)} chars")
                            
                    elif msg_type == 'clipboard_request':
                        try:
                            clipboard_text = pyperclip.paste()
                            await self.send_to_client(websocket, {
                                'type': 'clipboard_data',
                                'text': clipboard_text
                            })
                            logger.info(f"📋 Sent clipboard to client: {len(clipboard_text)} chars")
                        except Exception as e:
                            logger.error(f"Clipboard error: {e}")
                            
                    elif msg_type == 'request_frame':
                        frame = await self.capture_screen(
                            quality=data.get('quality', 95),
                            scale=data.get('scale', 1.0)
                        )
                        if frame:
                            await self.send_to_client(websocket, frame)
                            
                    elif msg_type == 'info_request':
                        info = {
                            'type': 'info',
                            'screen_width': self.screen_width,
                            'screen_height': self.screen_height
                        }
                        await self.send_to_client(websocket, info)
                        
                    elif msg_type == 'screenshot_request':
                        result = await self.capture_screenshot()
                        await self.send_to_client(websocket, result)
                        
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received")
                except Exception as e:
                    logger.error(f"Message handling error: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"⚠️ Client disconnected: {client_addr}")
        except Exception as e:
            logger.error(f"Client handler error: {e}")
        finally:
            self.connected_clients.discard(websocket)
            if self.current_client == websocket:
                self.current_client = None
    
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    async def start_server(self):
        """Start WebSocket server"""
        self.running = True
        local_ip = self.get_local_ip()
        
        logger.info("=" * 70)
        logger.info("🖥️  Local Remote Control Server")
        logger.info("=" * 70)
        logger.info(f"Server starting on {self.host}:{self.port}")
        logger.info(f"Local IP: {local_ip}")
        logger.info(f"Screen resolution: {self.screen_width}x{self.screen_height}")
        logger.info("")
        logger.info("Clients should connect to:")
        logger.info(f"  ws://{local_ip}:{self.port}")
        logger.info(f"  or ws://127.0.0.1:{self.port} (if on same machine)")
        logger.info("=" * 70)
        
        try:
            async with websockets.serve(
                self.handle_client, 
                self.host, 
                self.port,
                ping_interval=30,
                ping_timeout=60,
                max_size=10*1024*1024
            ):
                logger.info("✅ Server is running and waiting for connections...")
                await asyncio.Future()  # Run forever
        except OSError as e:
            if "address already in use" in str(e).lower():
                logger.error(f"❌ Port {self.port} is already in use. Please choose a different port.")
            else:
                logger.error(f"❌ Server error: {e}")
            raise

def minimize_console():
    """Minimize the console window on Windows"""
    try:
        if sys.platform == 'win32':
            # Get console window handle
            kernel32 = ctypes.windll.kernel32
            user32 = ctypes.windll.user32
            
            SW_MINIMIZE = 6
            hwnd = kernel32.GetConsoleWindow()
            
            if hwnd:
                user32.ShowWindow(hwnd, SW_MINIMIZE)
                logger.info("Console window minimized")
    except Exception as e:
        logger.warning(f"Could not minimize console: {e}")

def main():
    """Main entry point"""
    # Auto-connect with defaults - no user interaction required
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    
    server = LocalRemoteControlServer(port=port)
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        pass  # Silent exit
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        if server.keyboard_listener:
            try:
                server.keyboard_listener.stop()
            except:
                pass
        logger.info("✅ Server cleanup complete")

if __name__ == "__main__":
    main()
