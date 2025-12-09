#!/usr/bin/env python3
"""
Remote Control Server - Host side
Captures screen and handles remote mouse/keyboard control
Connects to Heroku relay for internet access
Works without admin privileges
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure pyautogui for safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01

class RemoteControlServer:
    def __init__(self, relay_url='wss://obscure-crag-09189-c525dbc46d88.herokuapp.com', server_id='my_computer'):
        self.relay_url = relay_url
        self.server_id = server_id
        self.websocket = None
        self.screen_width, self.screen_height = pyautogui.size()
        self.running = False
        self.connected = False
        # Store last client cursor position without moving actual cursor
        self.client_cursor_x = 0
        self.client_cursor_y = 0
        
        # Communication mode state
        self.communication_mode = False
        self.communication_buffer = ""
        self.keyboard_listener = None
        self.current_client_id = None
        
    async def capture_screen(self, quality=95, scale=1.0):
        """Capture screen and return as base64 encoded JPEG"""
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]  # Primary monitor
                screenshot = sct.grab(monitor)
                
                # Convert to PIL Image
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                
                # Scale down for better performance
                new_size = (int(img.width * scale), int(img.height * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Compress as JPEG
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality, optimize=True)
                img_bytes = buffer.getvalue()
                
                # Encode to base64
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
    
    async def handle_mouse_event(self, data):
        """Handle mouse events with accurate positioning"""
        try:
            event_type = data.get('event')
            
            # Convert coordinates from client to server screen
            x = int(data.get('x', 0) * self.screen_width)
            y = int(data.get('y', 0) * self.screen_height)
            
            # Store position but don't move cursor for 'move' events
            if event_type == 'move':
                # Just store the position, don't actually move the cursor
                self.client_cursor_x = x
                self.client_cursor_y = y
                # Don't call pyautogui.moveTo() - this keeps cursor stationary
                
            elif event_type == 'click':
                # Move to position, click, then return cursor to original position
                original_pos = pyautogui.position()
                button = data.get('button', 'left')
                pyautogui.moveTo(x, y, duration=0)  # Move first
                await asyncio.sleep(0.01)  # Small delay to ensure movement completes
                pyautogui.click(button=button)  # Click at current position
                await asyncio.sleep(0.01)  # Small delay to ensure click registers
                pyautogui.moveTo(original_pos[0], original_pos[1], duration=0)  # Return
                
            elif event_type == 'double_click':
                original_pos = pyautogui.position()
                pyautogui.moveTo(x, y, duration=0)
                await asyncio.sleep(0.01)
                pyautogui.doubleClick()
                await asyncio.sleep(0.01)
                pyautogui.moveTo(original_pos[0], original_pos[1], duration=0)
                
            elif event_type == 'down':
                original_pos = pyautogui.position()
                button = data.get('button', 'left')
                pyautogui.moveTo(x, y, duration=0)
                await asyncio.sleep(0.01)
                pyautogui.mouseDown(button=button)
                await asyncio.sleep(0.01)
                pyautogui.moveTo(original_pos[0], original_pos[1], duration=0)
                
            elif event_type == 'up':
                original_pos = pyautogui.position()
                button = data.get('button', 'left')
                pyautogui.moveTo(x, y, duration=0)
                await asyncio.sleep(0.01)
                pyautogui.mouseUp(button=button)
                await asyncio.sleep(0.01)
                pyautogui.moveTo(original_pos[0], original_pos[1], duration=0)
                
            elif event_type == 'scroll':
                scroll_amount = data.get('amount', 0)
                pyautogui.scroll(int(scroll_amount), x, y)
                
            logger.debug(f"Mouse event: {event_type} at ({x}, {y})")
            
        except Exception as e:
            logger.error(f"Mouse event error: {e}")
    
    def handle_keyboard_event(self, data):
        """Handle keyboard events"""
        try:
            event_type = data.get('event')
            key = data.get('key', '')
            
            if event_type == 'press':
                # Handle Ctrl+C and Ctrl+V as hotkeys for proper execution
                if key.lower() == 'c':
                    # This is Ctrl+C from client, execute copy
                    pyautogui.hotkey('ctrl', 'c')
                    logger.info("📋 Executed Ctrl+C (copy) on server")
                elif key.lower() == 'v':
                    # This is Ctrl+V from client, execute paste
                    pyautogui.hotkey('ctrl', 'v')
                    logger.info("📋 Executed Ctrl+V (paste) on server")
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
        """Start listening to server keyboard for communication mode"""
        shift_pressed = False
        
        def on_press(key):
            nonlocal shift_pressed
            
            # Track shift key
            if key in [keyboard.Key.shift, keyboard.Key.shift_r]:
                shift_pressed = True
            
            # Check for CapsLock while shift is pressed
            if key == keyboard.Key.caps_lock and shift_pressed:
                # Toggle communication mode
                self.toggle_communication_mode(not self.communication_mode)
                return
            
            # If in communication mode, capture text
            if self.communication_mode:
                try:
                    if hasattr(key, 'char') and key.char:
                        # Regular character
                        self.send_communication_text(key.char)
                    elif key == keyboard.Key.space:
                        self.send_communication_text(' ')
                    elif key == keyboard.Key.backspace:
                        self.send_communication_text('\b')  # Backspace signal
                    elif key == keyboard.Key.enter:
                        self.send_communication_text('\n')
                except Exception as e:
                    logger.error(f"Communication text error: {e}")
        
        def on_release(key):
            nonlocal shift_pressed
            
            # Track shift key release
            if key in [keyboard.Key.shift, keyboard.Key.shift_r]:
                shift_pressed = False
        
        self.keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.keyboard_listener.start()
        logger.info("⌨️ Keyboard listener started for communication mode")
        logger.info("⌨️ Keyboard listener started for communication mode")
    
    def toggle_communication_mode(self, enabled):
        """Toggle communication mode on/off"""
        self.communication_mode = enabled
        if enabled:
            logger.info("🗨️ Communication mode ENABLED - typing will be sent to client")
            self.communication_buffer = ""
            # Send notification to client
            asyncio.create_task(self.send_communication_notification(True))
        else:
            logger.info("🚫 Communication mode DISABLED - normal typing restored")
            # Send notification to client
            asyncio.create_task(self.send_communication_notification(False))
            self.communication_buffer = ""
    
    def send_communication_text(self, text):
        """Send communication text to client"""
        if self.websocket and self.current_client_id:
            message = {
                'type': 'communication_text',
                'text': text,
                'target_client': self.current_client_id
            }
            asyncio.create_task(self.websocket.send(json.dumps(message)))
    
    async def send_communication_notification(self, enabled):
        """Send communication mode status to client"""
        if self.websocket and self.current_client_id:
            message = {
                'type': 'communication_mode',
                'enabled': enabled,
                'target_client': self.current_client_id
            }
            await self.websocket.send(json.dumps(message))
    
    async def handle_relay_messages(self):
        """Handle messages from relay (forwarded from clients)"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get('type')
                    client_id = data.get('client_id')  # Added by relay
                    
                    if msg_type == 'registered':
                        logger.info(f"✅ Successfully registered with relay as '{self.server_id}'")
                        self.connected = True
                        # Start keyboard listener for communication mode
                        if not self.keyboard_listener:
                            self.start_keyboard_listener()
                        continue
                    
                    # Store current client ID for communication
                    if client_id:
                        self.current_client_id = client_id
                    
                    if msg_type == 'mouse':
                        await self.handle_mouse_event(data)
                    elif msg_type == 'keyboard':
                        self.handle_keyboard_event(data)
                    elif msg_type == 'clipboard_sync':
                        # Receive clipboard content from client
                        clipboard_text = data.get('text', '')
                        if clipboard_text:
                            pyperclip.copy(clipboard_text)
                            logger.info(f"📋 Clipboard synced from client: {len(clipboard_text)} chars")
                    elif msg_type == 'clipboard_request':
                        # Send clipboard content to client
                        try:
                            clipboard_text = pyperclip.paste()
                            clipboard_msg = {
                                'type': 'clipboard_data',
                                'text': clipboard_text,
                                'target_client': client_id
                            }
                            await self.websocket.send(json.dumps(clipboard_msg))
                            logger.info(f"📋 Sent clipboard to client: {len(clipboard_text)} chars")
                        except Exception as e:
                            logger.error(f"Clipboard read error: {e}")
                    elif msg_type == 'request_frame':
                        # Send screen capture back through relay
                        frame = await self.capture_screen(
                            quality=data.get('quality', 95),
                            scale=data.get('scale', 1.0)
                        )
                        if frame and client_id:
                            frame['target_client'] = client_id
                            await self.websocket.send(json.dumps(frame))
                    elif msg_type == 'info_request':
                        # Send screen info to requesting client
                        info = {
                            'type': 'info',
                            'screen_width': self.screen_width,
                            'screen_height': self.screen_height,
                            'target_client': client_id
                        }
                        await self.websocket.send(json.dumps(info))
                            
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received from relay")
                except Exception as e:
                    logger.error(f"Message handling error: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("⚠️ Connection to relay closed")
            self.connected = False
        except Exception as e:
            logger.error(f"Relay message handler error: {e}")
            self.connected = False
    
    async def connect_to_relay(self):
        """Connect to Heroku relay server"""
        self.running = True
        retry_count = 0
        max_retries = 5
        
        while self.running and retry_count < max_retries:
            try:
                logger.info(f"🔄 Connecting to relay: {self.relay_url}")
                
                self.websocket = await websockets.connect(
                    self.relay_url,
                    ping_interval=20,
                    ping_timeout=10,
                    max_size=10*1024*1024
                )
                
                # Register as server
                register_msg = {
                    'type': 'register_server',
                    'server_id': self.server_id
                }
                await self.websocket.send(json.dumps(register_msg))
                
                logger.info(f"📡 Registered as server: '{self.server_id}'")
                logger.info(f"Screen resolution: {self.screen_width}x{self.screen_height}")
                logger.info("✅ Ready to accept client connections!")
                logger.info(f"Clients should connect to relay and request server: '{self.server_id}'")
                
                # Handle messages from relay
                await self.handle_relay_messages()
                
            except websockets.exceptions.WebSocketException as e:
                retry_count += 1
                logger.error(f"❌ Connection failed (attempt {retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    wait_time = min(5 * retry_count, 30)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("Max retries reached. Please check relay URL and try again.")
                    break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                break
        
        if self.websocket:
            await self.websocket.close()

def main():
    """Main entry point"""
    print("=" * 70)
    print("🖥️  Remote Control Server (Host Computer)")
    print("=" * 70)
    print("This computer will be controlled remotely via Heroku relay")
    print()
    
    # Get relay URL from user or use default
    if len(sys.argv) > 1:
        relay_url = sys.argv[1]
    else:
        relay_url = input("Enter Heroku relay URL (or press Enter for default): ").strip()
        if not relay_url:
            relay_url = "wss://obscure-crag-09189-c525dbc46d88.herokuapp.com"
    
    # Get server ID
    if len(sys.argv) > 2:
        server_id = sys.argv[2]
    else:
        server_id = input("Enter server ID (or press Enter for 'my_computer'): ").strip()
        if not server_id:
            server_id = "my_computer"
    
    print()
    print(f"📡 Relay URL: {relay_url}")
    print(f"🆔 Server ID: {server_id}")
    print("=" * 70)
    print()
    
    server = RemoteControlServer(relay_url=relay_url, server_id=server_id)
    
    try:
        asyncio.run(server.connect_to_relay())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    main()
