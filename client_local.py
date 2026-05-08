#!/usr/bin/env python3
"""
Remote Control Client - Local Network Version
Connects directly to server on local network
No relay required
"""

import asyncio
import websockets
import json
import base64
import io
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import logging
import threading
import pyperclip
import time
import sys
import os
from datetime import datetime

# Configure logging
file_handler = logging.FileHandler('client_local.log', mode='w', encoding='utf-8')
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
logger.info("Local Client logging initialized")
logger.info("=" * 60)

class LocalRemoteControlClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Remote Control Client (Local Network)")
        self.root.geometry("1024x768")
        
        self.websocket = None
        self.connected = False
        self.running = True
        
        # Remote screen info
        self.remote_width = 1920
        self.remote_height = 1080
        
        # Last used server URL
        self.last_server_url = ""
        
        # Create UI
        self.create_ui()
        
        # Frame rate control
        self.fps = 20
        self.frame_interval = 1.0 / self.fps
        self.last_frame_time = 0
        
        # Image display tracking
        self.displayed_img_width = 0
        self.displayed_img_height = 0
        self.img_offset_x = 0
        self.img_offset_y = 0
        
        # Communication mode
        self.communication_mode = False
        self.comm_banner = None
        
        # Mouse detached mode
        self.mouse_detached = False
        self.mouse_mode_indicator = None
        
        # Screenshot directory
        self.screenshot_dir = "screenshots"
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
            logger.info(f"📸 Created screenshots directory: {self.screenshot_dir}")
        
    def create_ui(self):
        """Create user interface"""
        # Control panel
        control_frame = tk.Frame(self.root, bg='#2b2b2b', height=50)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        control_frame.pack_propagate(False)
        
        # Connection controls
        tk.Label(control_frame, text="Server IP:Port:", bg='#2b2b2b', fg='white').pack(side=tk.LEFT, padx=5)
        self.url_entry = tk.Entry(control_frame, width=25)
        self.url_entry.insert(0, "192.168.1.100:8765")
        self.url_entry.pack(side=tk.LEFT, padx=5)
        
        self.connect_btn = tk.Button(control_frame, text="Connect", command=self.toggle_connection, 
                                     bg='#4CAF50', fg='white', padx=10)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(control_frame, text="Disconnected", bg='#2b2b2b', fg='red')
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # FPS control
        tk.Label(control_frame, text="FPS:", bg='#2b2b2b', fg='white').pack(side=tk.LEFT, padx=5)
        self.fps_var = tk.StringVar(value="20")
        fps_spinbox = tk.Spinbox(control_frame, from_=1, to=60, width=5,
                                textvariable=self.fps_var, command=self.update_fps)
        fps_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Clipboard indicator
        tk.Label(control_frame, text="📋 Auto-sync", bg='#2b2b2b', fg='#4CAF50', 
                font=('Arial', 9)).pack(side=tk.LEFT, padx=10)
        
        # Mouse mode indicator
        self.mouse_mode_label = tk.Label(control_frame, text="🖱️ Attached", bg='#2b2b2b', fg='#4CAF50', 
                font=('Arial', 9))
        self.mouse_mode_label.pack(side=tk.LEFT, padx=10)
        
        # Canvas for screen display
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Mouse event bindings
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.canvas.bind('<Button-1>', self.on_mouse_click)
        self.canvas.bind('<Button-3>', self.on_right_click)
        self.canvas.bind('<Double-Button-1>', self.on_double_click)
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<MouseWheel>', self.on_scroll)
        
        # Keyboard event bindings
        self.canvas.bind('<KeyPress>', self.on_key_press)
        self.canvas.bind('<KeyRelease>', self.on_key_release)
        self.canvas.bind('<Control-c>', self.on_ctrl_c)
        self.canvas.bind('<Control-v>', self.on_ctrl_v)
        self.canvas.bind('<Control-backslash>', self.on_screenshot_key)
        
        # Mouse toggle hotkey (Ctrl+Shift+Z)
        self.root.bind('<Control-Shift-Z>', self.toggle_mouse_mode)
        self.root.bind('<Control-Shift-z>', self.toggle_mouse_mode)
        
        self.canvas.focus_set()
        
        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def update_fps(self):
        """Update frame rate"""
        try:
            self.fps = int(self.fps_var.get())
            self.frame_interval = 1.0 / self.fps
            logger.info(f"FPS updated to {self.fps}")
        except ValueError:
            pass
    
    def auto_send_clipboard(self):
        """Auto-send clipboard to server"""
        if not self.connected:
            return
        
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text:
                message = {
                    'type': 'clipboard_sync',
                    'text': clipboard_text
                }
                asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
                logger.info(f"📋 Auto-synced clipboard: {len(clipboard_text)} chars")
        except Exception as e:
            logger.error(f"Clipboard send error: {e}")
    
    def get_normalized_coords(self, event):
        """Convert canvas coords to normalized coords"""
        if self.displayed_img_width == 0 or self.displayed_img_height == 0:
            return 0.0, 0.0
        
        img_x = event.x - self.img_offset_x
        img_y = event.y - self.img_offset_y
        
        norm_x = img_x / self.displayed_img_width
        norm_y = img_y / self.displayed_img_height
        
        norm_x = max(0.0, min(1.0, norm_x))
        norm_y = max(0.0, min(1.0, norm_y))
        
        return norm_x, norm_y
    
    async def send_message(self, message):
        """Send message to server"""
        if not (self.websocket and self.connected):
            return
        try:
            await self.websocket.send(json.dumps(message))
        except Exception as e:
            logger.warning(f"Send error: {e}")
    
    def on_mouse_move(self, event):
        """Handle mouse movement"""
        if self.connected and not self.mouse_detached:
            norm_x, norm_y = self.get_normalized_coords(event)
            message = {
                'type': 'mouse',
                'event': 'move',
                'x': norm_x,
                'y': norm_y,
                'detached': False
            }
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
    
    def on_mouse_click(self, event):
        """Handle mouse click"""
        self.canvas.focus_set()
        if self.connected:
            norm_x, norm_y = self.get_normalized_coords(event)
            message = {
                'type': 'mouse',
                'event': 'click',
                'x': norm_x,
                'y': norm_y,
                'button': 'left',
                'detached': self.mouse_detached
            }
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
    
    def on_right_click(self, event):
        """Handle right click"""
        if self.connected:
            norm_x, norm_y = self.get_normalized_coords(event)
            message = {
                'type': 'mouse',
                'event': 'click',
                'x': norm_x,
                'y': norm_y,
                'button': 'right',
                'detached': self.mouse_detached
            }
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
    
    def on_double_click(self, event):
        """Handle double click"""
        if self.connected:
            norm_x, norm_y = self.get_normalized_coords(event)
            message = {
                'type': 'mouse',
                'event': 'double_click',
                'x': norm_x,
                'y': norm_y,
                'detached': self.mouse_detached
            }
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
    
    def on_mouse_down(self, event):
        """Handle mouse button down"""
        if self.connected:
            norm_x, norm_y = self.get_normalized_coords(event)
            message = {
                'type': 'mouse',
                'event': 'down',
                'x': norm_x,
                'y': norm_y,
                'button': 'left',
                'detached': self.mouse_detached
            }
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
    
    def on_mouse_up(self, event):
        """Handle mouse button up"""
        if self.connected:
            norm_x, norm_y = self.get_normalized_coords(event)
            message = {
                'type': 'mouse',
                'event': 'up',
                'x': norm_x,
                'y': norm_y,
                'button': 'left',
                'detached': self.mouse_detached
            }
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
    
    def on_scroll(self, event):
        """Handle mouse scroll"""
        if self.connected:
            norm_x, norm_y = self.get_normalized_coords(event)
            scroll_amount = event.delta // 120
            message = {
                'type': 'mouse',
                'event': 'scroll',
                'x': norm_x,
                'y': norm_y,
                'amount': scroll_amount,
                'detached': self.mouse_detached
            }
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
    
    def on_key_press(self, event):
        """Handle key press"""
        if self.connected:
            key = event.keysym
            
            is_ctrl = (event.state & 0x4) or (event.state & 0x40000)
            if is_ctrl and key.lower() in ['c', 'v']:
                return
            
            message = {
                'type': 'keyboard',
                'event': 'press',
                'key': key
            }
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
    
    def send_paste_command(self):
        """Send Ctrl+V to server"""
        if self.connected:
            message = {
                'type': 'keyboard',
                'event': 'press',
                'key': 'v'
            }
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
            logger.info("📋 Sent paste command")
    
    def sync_from_server_clipboard(self):
        """Get clipboard from server after Ctrl+C"""
        if self.connected:
            message = {'type': 'clipboard_request'}
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
            logger.info("📋 Requesting clipboard from server")
    
    def on_ctrl_c(self, event):
        """Handle Ctrl+C"""
        if not self.connected:
            return
        
        logger.info("📋 Ctrl+C - copying on server")
        message = {
            'type': 'keyboard',
            'event': 'press',
            'key': 'c'
        }
        asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
        self.root.after(300, self.sync_from_server_clipboard)
        return "break"
    
    def on_ctrl_v(self, event):
        """Handle Ctrl+V"""
        if not self.connected:
            return
        
        logger.info("📋 Ctrl+V - syncing clipboard to server")
        self.auto_send_clipboard()
        self.root.after(300, self.send_paste_command)
        return "break"
    
    def on_key_release(self, event):
        """Handle key release"""
        if self.connected:
            key = event.keysym
            message = {
                'type': 'keyboard',
                'event': 'up',
                'key': key
            }
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
    
    def on_screenshot_key(self, event):
        """Handle Ctrl+\ screenshot shortcut"""
        if not self.connected:
            return
        
        logger.info("📸 Ctrl+\\ pressed - requesting screenshot")
        message = {'type': 'screenshot_request'}
        asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
        self.show_screenshot_notification()
        return "break"    
    def toggle_mouse_mode(self, event=None):
        """Toggle between attached and detached mouse mode"""
        self.mouse_detached = not self.mouse_detached
        
        if self.mouse_detached:
            logger.info("🖱️ Mouse DETACHED - cursor will not move on server")
            self.mouse_mode_label.config(text="🖱️ Detached", fg='#FF9800')
            self.show_mouse_mode_notification("Mouse Detached")
        else:
            logger.info("🖱️ Mouse ATTACHED - cursor will move on server")
            self.mouse_mode_label.config(text="🖱️ Attached", fg='#4CAF50')
            self.show_mouse_mode_notification("Mouse Attached")
        
        return "break"    
    def display_frame(self, frame_data):
        """Display frame on canvas"""
        try:
            img_bytes = base64.b64decode(frame_data['data'])
            img = Image.open(io.BytesIO(img_bytes))
            
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                img.thumbnail((canvas_width, canvas_height), Image.Resampling.BILINEAR)
                
                self.displayed_img_width = img.width
                self.displayed_img_height = img.height
                self.img_offset_x = (canvas_width - img.width) // 2
                self.img_offset_y = (canvas_height - img.height) // 2
                
                photo = ImageTk.PhotoImage(img)
                
                self.canvas.delete("all")
                self.canvas.create_image(canvas_width//2, canvas_height//2, 
                                        image=photo, anchor=tk.CENTER)
                self.canvas.image = photo
                
                if self.communication_mode:
                    self.show_communication_banner()
                
        except Exception as e:
            logger.error(f"Display error: {e}")
    
    def toggle_communication_display(self, enabled):
        """Toggle communication mode display"""
        self.communication_mode = enabled
        if enabled:
            logger.info("💬 Communication mode enabled")
            self.show_communication_banner()
        else:
            logger.info("💬 Communication mode disabled")
            self.hide_communication_banner()
    
    def show_communication_banner(self):
        """Show communication banner"""
        if self.comm_banner:
            return
        canvas_width = self.canvas.winfo_width()
        self.comm_banner = self.canvas.create_rectangle(
            0, 0, canvas_width, 40,
            fill='#4CAF50', outline=''
        )
        self.canvas.create_text(
            canvas_width // 2, 20,
            text="💬 Communication Mode Active",
            fill='white',
            font=('Arial', 12, 'bold'),
            tags='comm_banner_text'
        )
        self.canvas.tag_raise('comm_banner_text')
    
    def hide_communication_banner(self):
        """Hide communication banner"""
        if self.comm_banner:
            self.canvas.delete(self.comm_banner)
            self.canvas.delete('comm_banner_text')
            self.comm_banner = None
    
    def save_screenshot(self, data):
        """Save screenshot to local file"""
        try:
            # Decode base64 image data
            img_bytes = base64.b64decode(data.get('data', ''))
            img = Image.open(io.BytesIO(img_bytes))
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            # Save screenshot
            img.save(filepath, format='PNG')
            logger.info(f"📸 Screenshot saved: {filepath}")
            
        except Exception as e:
            logger.error(f"Screenshot save error: {e}")
    
    def show_screenshot_notification(self):
        """Show screenshot notification"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Create notification
        notification = self.canvas.create_rectangle(
            canvas_width - 220, canvas_height - 60,
            canvas_width - 10, canvas_height - 10,
            fill='#2196F3', outline='white', width=2
        )
        text = self.canvas.create_text(
            canvas_width - 115, canvas_height - 35,
            text="📸 Screenshot Captured!",
            fill='white',
            font=('Arial', 11, 'bold')
        )
        
        # Remove after 2 seconds
        self.root.after(2000, lambda: self.canvas.delete(notification))
        self.root.after(2000, lambda: self.canvas.delete(text))
    
    def show_mouse_mode_notification(self, mode_text):
        """Show mouse mode change notification"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        color = '#FF9800' if self.mouse_detached else '#4CAF50'
        
        # Create notification
        notification = self.canvas.create_rectangle(
            canvas_width - 220, 10,
            canvas_width - 10, 60,
            fill=color, outline='white', width=2
        )
        text = self.canvas.create_text(
            canvas_width - 115, 35,
            text=f"🖱️ {mode_text}",
            fill='white',
            font=('Arial', 11, 'bold')
        )
        
        # Remove after 2 seconds
        self.root.after(2000, lambda: self.canvas.delete(notification))
        self.root.after(2000, lambda: self.canvas.delete(text))
    
    async def receive_frames(self):
        """Receive frames from server"""
        # Request screen info
        await self.send_message({'type': 'info_request'})
        
        while self.connected:
            try:
                current_time = time.time()
                if current_time - self.last_frame_time < self.frame_interval:
                    await asyncio.sleep(0.01)
                    continue
                
                self.last_frame_time = current_time
                
                # Request frame
                await self.send_message({
                    'type': 'request_frame',
                    'quality': 75,
                    'scale': 0.7
                })
                
                message = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
                data = json.loads(message)
                msg_type = data.get('type')
                
                if msg_type == 'screen':
                    self.root.after(0, self.display_frame, data)
                elif msg_type == 'info':
                    self.remote_width = data.get('screen_width', 1920)
                    self.remote_height = data.get('screen_height', 1080)
                    logger.info(f"Remote screen: {self.remote_width}x{self.remote_height}")
                elif msg_type == 'clipboard_data':
                    clipboard_text = data.get('text', '')
                    if clipboard_text:
                        pyperclip.copy(clipboard_text)
                        logger.info(f"📋 Clipboard synced: {len(clipboard_text)} chars")
                elif msg_type == 'communication_mode':
                    enabled = data.get('enabled', False)
                    self.root.after(0, self.toggle_communication_display, enabled)
                elif msg_type == 'screenshot_data':
                    self.save_screenshot(data)
                elif msg_type == 'screenshot_error':
                    error = data.get('error', '')
                    logger.error(f"📸 Screenshot error: {error}")
                
            except asyncio.TimeoutError:
                continue
            except websockets.exceptions.ConnectionClosed:
                logger.warning("⚠️ Connection closed")
                self.connected = False
                break
            except Exception as e:
                logger.error(f"Receive error: {e}")
                break
    
    async def connect_to_server(self, server_url):
        """Connect to server"""
        try:
            self.last_server_url = server_url
            
            # Add ws:// if not present
            if not server_url.startswith('ws://'):
                server_url = f'ws://{server_url}'
            
            logger.info(f"Connecting to {server_url}")
            
            # Try connection with timeout
            self.websocket = await asyncio.wait_for(
                websockets.connect(
                    server_url,
                    ping_interval=30,
                    ping_timeout=60,
                    close_timeout=10,
                    max_size=10*1024*1024
                ),
                timeout=10.0
            )
            
            self.connected = True
            logger.info(f"✅ Connected to server")
            
            self.root.after(0, lambda: self.status_label.config(text="Connected", fg='green'))
            self.root.after(0, lambda: self.connect_btn.config(text="Disconnect"))
            
            await self.receive_frames()
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.connected = False
            self.root.after(0, lambda: messagebox.showerror("Connection Error", 
                                                           f"Failed to connect:\n{str(e)}"))
            self.root.after(0, lambda: self.status_label.config(text="Disconnected", fg='red'))
            self.root.after(0, lambda: self.connect_btn.config(text="Connect"))
    
    def toggle_connection(self):
        """Toggle connection"""
        if not self.connected:
            server_url = self.url_entry.get().strip()
            
            if not server_url:
                messagebox.showwarning("Invalid", "Please enter server IP:Port")
                return
            
            asyncio.run_coroutine_threadsafe(self.connect_to_server(server_url), self.loop)
        else:
            self.connected = False
            if self.websocket:
                asyncio.run_coroutine_threadsafe(self.websocket.close(), self.loop)
            self.status_label.config(text="Disconnected", fg='red')
            self.connect_btn.config(text="Connect")
            logger.info("Disconnected")
    
    def on_closing(self):
        """Handle window close"""
        self.running = False
        self.connected = False
        if self.websocket:
            asyncio.run_coroutine_threadsafe(self.websocket.close(), self.loop)
        self.root.quit()
    
    def run_async_loop(self):
        """Run asyncio loop in background"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def start(self):
        """Start client"""
        async_thread = threading.Thread(target=self.run_async_loop, daemon=True)
        async_thread.start()
        self.root.mainloop()

def main():
    """Main entry point"""
    print("=" * 70)
    print("🎮 Remote Control Client (Local Network)")
    print("=" * 70)
    print("Direct connection to server on local network")
    print("Example: 192.168.1.100:8765")
    print("=" * 70)
    
    client = LocalRemoteControlClient()
    try:
        client.start()
    except KeyboardInterrupt:
        print("\n🛑 Client stopped")
    except Exception as e:
        logger.error(f"Client error: {e}")
    finally:
        client.running = False
        if client.websocket:
            try:
                asyncio.run(client.websocket.close())
            except:
                pass
        logger.info("✅ Cleanup complete")

if __name__ == "__main__":
    main()
