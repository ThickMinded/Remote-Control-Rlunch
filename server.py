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
import tkinter as tk
from threading import Thread

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
        self.event_loop = None  # Store the asyncio event loop
        self.comm_window = None  # Communication input window
        
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
        ctrl_pressed = False
        both_pressed = False  # Track if both were pressed together
        
        def on_press(key):
            nonlocal shift_pressed, ctrl_pressed, both_pressed
            
            # Track shift and ctrl keys
            if key in [keyboard.Key.shift, keyboard.Key.shift_r]:
                shift_pressed = True
            if key in [keyboard.Key.ctrl, keyboard.Key.ctrl_r, keyboard.Key.ctrl_l]:
                ctrl_pressed = True
            
            # Check if both are now pressed and we haven't triggered yet
            if shift_pressed and ctrl_pressed and not both_pressed:
                both_pressed = True
                # Toggle communication mode
                logger.info(f"🔄 Toggling communication mode from {self.communication_mode} to {not self.communication_mode}")
                self.toggle_communication_mode(not self.communication_mode)
            
            # Don't capture text here - the tkinter window handles it
            # This prevents double sending
        
        def on_release(key):
            nonlocal shift_pressed, ctrl_pressed, both_pressed
            
            # Track key releases
            if key in [keyboard.Key.shift, keyboard.Key.shift_r]:
                shift_pressed = False
                # Reset both_pressed only after both are released
                if not ctrl_pressed:
                    both_pressed = False
            if key in [keyboard.Key.ctrl, keyboard.Key.ctrl_r, keyboard.Key.ctrl_l]:
                ctrl_pressed = False
                # Reset both_pressed only after both are released
                if not shift_pressed:
                    both_pressed = False
        
        self.keyboard_listener = keyboard.Listener(
            on_press=on_press, 
            on_release=on_release
        )
        self.keyboard_listener.start()
        logger.info("⌨️ Keyboard listener started for communication mode")
        
        # Start communication window immediately and keep it running
        self.open_communication_window()
        logger.info("💬 Communication window ready (Ctrl+Shift to activate)")
    
    def toggle_communication_mode(self, enabled):
        """Toggle communication mode on/off"""
        self.communication_mode = enabled
        if enabled:
            logger.info("🗨️ Communication mode ENABLED - typing will be sent to client")
            self.communication_buffer = ""
            # Open invisible input window
            self.open_communication_window()
            # Send notification to client using thread-safe method
            if self.event_loop:
                asyncio.run_coroutine_threadsafe(
                    self.send_communication_notification(True), 
                    self.event_loop
                )
        else:
            logger.info("🚫 Communication mode DISABLED - normal typing restored")
            # Close communication window first
            self.close_communication_window()
            # Wait to ensure all pending text messages are sent before sending disable notification
            import time
            time.sleep(0.3)
            # Send notification to client using thread-safe method
            if self.event_loop:
                asyncio.run_coroutine_threadsafe(
                    self.send_communication_notification(False), 
                    self.event_loop
                )
            self.communication_buffer = ""
    
    def open_communication_window(self):
        """Open an invisible focused window for communication input"""
        import time
        
        # First, simulate a click on empty space to remove focus from any text box
        try:
            import pyautogui
            # Click on a corner of the screen to remove focus
            pyautogui.click(5, 5)
            time.sleep(0.05)
        except:
            pass
        
        def create_window():
            # Small delay to ensure click is processed
            time.sleep(0.1)
            
            window = tk.Tk()
            window.title("Communication Mode Active")
            
            # Make window fullscreen and invisible
            window.attributes('-alpha', 0.01)  # Almost invisible
            window.attributes('-topmost', True)  # Always on top
            window.attributes('-fullscreen', True)  # Fullscreen to block everything
            window.overrideredirect(True)  # No window decorations
            
            # Store reference
            self.comm_window = window
            
            # Create text widget to capture input
            text_widget = tk.Text(window, width=1, height=1, bg='black')
            text_widget.pack()
            
            # Force focus to this window aggressively
            window.update()
            window.lift()
            window.focus_force()
            text_widget.focus_set()
            window.update()
            
            # Bind key events - only send when communication mode is active
            last_key_time = [0]  # Use list to allow modification in nested function
            
            def on_key(event):
                import time
                current_time = time.time()
                
                # Prevent double key events (tkinter can fire twice)
                if current_time - last_key_time[0] < 0.01:
                    return "break"
                
                last_key_time[0] = current_time
                
                # Only send if communication mode is active
                if not self.communication_mode:
                    return "break"  # Still block the key from typing
                
                char = event.char
                keysym = event.keysym
                
                if char and char.isprintable():  # Regular printable character
                    self.communication_buffer += char
                elif keysym == 'BackSpace':
                    self.communication_buffer += '\b'
                elif keysym == 'Return':
                    self.communication_buffer += '\n'
                elif keysym == 'space':
                    self.communication_buffer += ' '
                
                return "break"  # Always block the key from typing in widget
            
            text_widget.bind('<KeyPress>', on_key)
            
            # Keep window alive indefinitely with focus stealing
            def keep_focus():
                try:
                    if self.comm_window is window:
                        window.lift()
                        window.attributes('-topmost', True)
                        window.focus_force()
                        text_widget.focus_set()
                        window.after(100, keep_focus)  # 100ms - stable and efficient
                except tk.TclError:
                    pass
                except:
                    pass
            
            keep_focus()
            
            try:
                window.mainloop()
            except:
                pass
            finally:
                try:
                    window.destroy()
                except:
                    pass
        
        # Run in separate thread
        thread = Thread(target=create_window, daemon=True)
        thread.start()
    
    def close_communication_window(self):
        """Close the communication window"""
        if self.comm_window:
            try:
                # Just clear reference - the keep_focus loop will handle cleanup
                self.comm_window = None
            except:
                pass
    
    async def send_communication_notification(self, enabled):
        """Send communication mode status to client"""
        if self.websocket and self.current_client_id:
            try:
                message = {
                    'type': 'communication_mode',
                    'enabled': enabled,
                    'target_client': self.current_client_id
                }
                await self.websocket.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send communication notification: {e}")
    
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
                        # Store event loop for thread-safe async calls
                        self.event_loop = asyncio.get_running_loop()
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
                            # Include communication text in frame if available
                            if self.communication_buffer:
                                frame['communication_text'] = self.communication_buffer
                                self.communication_buffer = ""  # Clear after sending
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
                    ping_interval=30,      # Send ping every 30 seconds
                    ping_timeout=60,       # Wait 60 seconds for pong
                    close_timeout=10,      # Wait 10 seconds for close frame
                    max_size=10*1024*1024  # 10MB max message size
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
    finally:
        # Cleanup resources
        if server.comm_window:
            server.close_communication_window()
        if server.keyboard_listener:
            try:
                server.keyboard_listener.stop()
            except:
                pass
        logger.info("✅ Server cleanup complete")
        raise

if __name__ == "__main__":
    main()
