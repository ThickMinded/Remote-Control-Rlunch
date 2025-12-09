#!/usr/bin/env python3
"""
Remote Control Client - Controller side
Displays remote screen and sends mouse/keyboard commands
Connects through Replit relay to control remote computer
"""

import asyncio
import websockets
import json
import base64
import io
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import logging
import threading
import pyperclip

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RemoteControlClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Remote Control Client (via Relay)")
        self.root.geometry("1024x768")
        
        self.websocket = None
        self.connected = False
        self.running = True
        self.registered = False
        
        # Remote screen info
        self.remote_width = 1920
        self.remote_height = 1080
        self.display_scale = 1.0
        
        # Relay and server info
        self.server_id = "my_computer"
        
        # Create UI
        self.create_ui()
        
        # Frame rate control
        self.fps = 10
        self.frame_interval = 1.0 / self.fps
        
        # Track displayed image dimensions for accurate coordinate mapping
        self.displayed_img_width = 0
        self.displayed_img_height = 0
        self.img_offset_x = 0
        self.img_offset_y = 0
        
    def create_ui(self):
        """Create the user interface"""
        # Top control panel
        control_frame = tk.Frame(self.root, bg='#2b2b2b', height=50)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        control_frame.pack_propagate(False)
        
        # Connection controls
        tk.Label(control_frame, text="Relay URL:", bg='#2b2b2b', fg='white').pack(side=tk.LEFT, padx=5)
        self.url_entry = tk.Entry(control_frame, width=30)
        self.url_entry.insert(0, "wss://obscure-crag-09189-c525dbc46d88.herokuapp.com")
        self.url_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(control_frame, text="Server ID:", bg='#2b2b2b', fg='white').pack(side=tk.LEFT, padx=5)
        self.server_entry = tk.Entry(control_frame, width=15)
        self.server_entry.insert(0, "my_computer")
        self.server_entry.pack(side=tk.LEFT, padx=5)
        
        self.connect_btn = tk.Button(control_frame, text="Connect", command=self.toggle_connection, 
                                     bg='#4CAF50', fg='white', padx=10)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(control_frame, text="Disconnected", bg='#2b2b2b', fg='red')
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # FPS control
        tk.Label(control_frame, text="FPS:", bg='#2b2b2b', fg='white').pack(side=tk.LEFT, padx=5)
        self.fps_var = tk.StringVar(value="10")
        fps_spinbox = tk.Spinbox(control_frame, from_=1, to=30, width=5, 
                                textvariable=self.fps_var, command=self.update_fps)
        fps_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Clipboard status indicator
        tk.Label(control_frame, text="📋 Auto-sync", bg='#2b2b2b', fg='#4CAF50', 
                font=('Arial', 9)).pack(side=tk.LEFT, padx=10)
        
        # Screen display canvas
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.canvas.bind('<Button-1>', self.on_mouse_click)
        self.canvas.bind('<Button-3>', self.on_right_click)
        self.canvas.bind('<Double-Button-1>', self.on_double_click)
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.canvas.bind('<MouseWheel>', self.on_scroll)
        
        # Bind keyboard events
        self.canvas.bind('<KeyPress>', self.on_key_press)
        self.canvas.bind('<KeyRelease>', self.on_key_release)
        self.canvas.focus_set()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def update_fps(self):
        """Update frame rate"""
        try:
            self.fps = int(self.fps_var.get())
            self.frame_interval = 1.0 / self.fps
            logger.info(f"FPS updated to {self.fps}")
        except ValueError:
            pass
    
    def send_clipboard(self):
        """Send local clipboard content to server"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to server first")
            return
        
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text:
                message = {
                    'type': 'clipboard_sync',
                    'text': clipboard_text
                }
                asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
                logger.info(f"📋 Sent clipboard to server: {len(clipboard_text)} chars")
                messagebox.showinfo("Clipboard", f"Sent {len(clipboard_text)} characters to server")
            else:
                messagebox.showinfo("Clipboard", "Clipboard is empty")
        except Exception as e:
            logger.error(f"Clipboard send error: {e}")
            messagebox.showerror("Error", f"Failed to send clipboard: {e}")
    
    def auto_send_clipboard(self):
        """Automatically send clipboard after Ctrl+C (no popup)"""
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
                logger.info(f"📋 Auto-synced clipboard to server: {len(clipboard_text)} chars")
        except Exception as e:
            logger.error(f"Auto clipboard send error: {e}")
    
    def get_clipboard(self):
        """Request clipboard content from server"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to server first")
            return
        
        try:
            message = {'type': 'clipboard_request'}
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
            logger.info("📋 Requested clipboard from server")
        except Exception as e:
            logger.error(f"Clipboard request error: {e}")
            messagebox.showerror("Error", f"Failed to request clipboard: {e}")
    
    def auto_get_clipboard(self):
        """Automatically request clipboard before Ctrl+V (no popup)"""
        if not self.connected:
            return
        
        try:
            message = {'type': 'clipboard_request'}
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
            logger.info("📋 Auto-requesting clipboard from server for paste")
        except Exception as e:
            logger.error(f"Auto clipboard request error: {e}")
    
    def get_normalized_coords(self, event):
        """Convert canvas coordinates to normalized coordinates (0-1 range)"""
        if self.displayed_img_width == 0 or self.displayed_img_height == 0:
            return 0.0, 0.0
        
        # Adjust for image offset (since image is centered on canvas)
        img_x = event.x - self.img_offset_x
        img_y = event.y - self.img_offset_y
        
        # Convert to normalized coordinates based on displayed image size
        norm_x = img_x / self.displayed_img_width
        norm_y = img_y / self.displayed_img_height
        
        # Clamp to valid range
        norm_x = max(0.0, min(1.0, norm_x))
        norm_y = max(0.0, min(1.0, norm_y))
        
        return norm_x, norm_y
    
    async def send_message(self, message):
        """Send message to server"""
        if self.websocket and self.connected:
            try:
                await self.websocket.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Send error: {e}")
    
    def on_mouse_move(self, event):
        """Handle mouse movement"""
        if self.connected:
            norm_x, norm_y = self.get_normalized_coords(event)
            message = {
                'type': 'mouse',
                'event': 'move',
                'x': norm_x,
                'y': norm_y
            }
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
    
    def on_mouse_click(self, event):
        """Handle mouse click"""
        self.canvas.focus_set()  # Ensure canvas has focus for keyboard events
        if self.connected:
            norm_x, norm_y = self.get_normalized_coords(event)
            message = {
                'type': 'mouse',
                'event': 'click',
                'x': norm_x,
                'y': norm_y,
                'button': 'left'
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
                'button': 'right'
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
                'y': norm_y
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
                'button': 'left'
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
                'button': 'left'
            }
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
    
    def on_scroll(self, event):
        """Handle mouse scroll"""
        if self.connected:
            norm_x, norm_y = self.get_normalized_coords(event)
            scroll_amount = event.delta // 120  # Normalize scroll amount
            message = {
                'type': 'mouse',
                'event': 'scroll',
                'x': norm_x,
                'y': norm_y,
                'amount': scroll_amount
            }
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
    
    def on_key_press(self, event):
        """Handle key press with automatic clipboard sync"""
        if self.connected:
            key = event.keysym
            
            # Check for Ctrl+C (copy) - sync local clipboard to server
            if event.state & 0x4 and key.lower() == 'c':  # 0x4 is Ctrl modifier
                # Give time for system to update clipboard, then sync
                self.root.after(50, self.auto_send_clipboard)
                logger.info("📋 Ctrl+C detected - will sync clipboard to server")
            
            # Check for Ctrl+V (paste) - get server clipboard first then paste
            elif event.state & 0x4 and key.lower() == 'v':  # 0x4 is Ctrl modifier
                # Request clipboard from server and send paste after a delay
                self.auto_get_clipboard()
                # Send the paste command after clipboard sync (small delay)
                self.root.after(100, lambda: self.send_key_command(key))
                logger.info("📋 Ctrl+V detected - syncing clipboard from server then pasting")
                return  # Don't send immediately, will send after delay
            
            message = {
                'type': 'keyboard',
                'event': 'press',
                'key': key
            }
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
    
    def send_key_command(self, key):
        """Send a key command to the server"""
        if self.connected:
            message = {
                'type': 'keyboard',
                'event': 'press',
                'key': key
            }
            asyncio.run_coroutine_threadsafe(self.send_message(message), self.loop)
    
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
    
    def display_frame(self, frame_data):
        """Display received frame on canvas"""
        try:
            # Decode base64 image
            img_bytes = base64.b64decode(frame_data['data'])
            img = Image.open(io.BytesIO(img_bytes))
            
            # Get canvas size
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                # Store original size before thumbnail
                original_width, original_height = img.size
                
                # Resize to fit canvas while maintaining aspect ratio
                img.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                
                # Store actual displayed image size and offset
                self.displayed_img_width = img.width
                self.displayed_img_height = img.height
                self.img_offset_x = (canvas_width - img.width) // 2
                self.img_offset_y = (canvas_height - img.height) // 2
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(img)
                
                # Display on canvas
                self.canvas.delete("all")
                self.canvas.create_image(canvas_width//2, canvas_height//2, 
                                        image=photo, anchor=tk.CENTER)
                self.canvas.image = photo  # Keep reference
                
        except Exception as e:
            logger.error(f"Display frame error: {e}")
    
    async def receive_frames(self):
        """Continuously request and receive frames"""
        # First request screen info
        await self.send_message({'type': 'info_request'})
        
        while self.connected:
            try:
                # Request frame
                await self.send_message({
                    'type': 'request_frame',
                    'quality': 95,
                    'scale': 1.0
                })
                
                # Wait for frame
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
                    # Received clipboard content from server
                    clipboard_text = data.get('text', '')
                    if clipboard_text:
                        pyperclip.copy(clipboard_text)
                        logger.info(f"📋 Clipboard synced from server: {len(clipboard_text)} chars")
                elif msg_type == 'server_disconnected':
                    logger.warning("Server disconnected")
                    self.root.after(0, lambda: messagebox.showwarning("Disconnected", "Server disconnected"))
                    self.connected = False
                    break
                elif msg_type == 'error':
                    error_msg = data.get('message', 'Unknown error')
                    logger.error(f"Server error: {error_msg}")
                    self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                    self.connected = False
                    break
                
                # Control frame rate
                await asyncio.sleep(self.frame_interval)
                
            except asyncio.TimeoutError:
                logger.warning("Frame timeout")
            except Exception as e:
                logger.error(f"Receive frame error: {e}")
                break
    
    async def connect_to_server(self, relay_url, server_id):
        """Connect to relay server and request specific server"""
        try:
            logger.info(f"Connecting to relay: {relay_url}")
            self.websocket = await websockets.connect(relay_url, ping_interval=20, ping_timeout=10)
            
            # Register as client and request server
            register_msg = {
                'type': 'register_client',
                'server_id': server_id
            }
            await self.websocket.send(json.dumps(register_msg))
            
            # Wait for registration confirmation
            response = await asyncio.wait_for(self.websocket.recv(), timeout=10.0)
            data = json.loads(response)
            
            if data.get('type') == 'registered' and data.get('status') == 'success':
                self.connected = True
                self.registered = True
                logger.info(f"✅ Connected to server '{server_id}' via relay")
                
                self.root.after(0, lambda: self.status_label.config(text=f"Connected to {server_id}", fg='green'))
                self.root.after(0, lambda: self.connect_btn.config(text="Disconnect"))
                
                # Start receiving frames
                await self.receive_frames()
            elif data.get('type') == 'error':
                error_msg = data.get('message', 'Connection failed')
                raise Exception(error_msg)
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.connected = False
            self.root.after(0, lambda: messagebox.showerror("Connection Error", 
                                                           f"Failed to connect:\n{str(e)}"))
            self.root.after(0, lambda: self.status_label.config(text="Disconnected", fg='red'))
            self.root.after(0, lambda: self.connect_btn.config(text="Connect"))
    
    def toggle_connection(self):
        """Toggle connection to server"""
        if not self.connected:
            relay_url = self.url_entry.get().strip()
            server_id = self.server_entry.get().strip()
            
            if not relay_url:
                messagebox.showwarning("Invalid URL", "Please enter a relay URL")
                return
            
            if not server_id:
                messagebox.showwarning("Invalid Server ID", "Please enter a server ID")
                return
            
            self.server_id = server_id
            
            # Start connection in background
            asyncio.run_coroutine_threadsafe(self.connect_to_server(relay_url, server_id), self.loop)
        else:
            # Disconnect
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
        """Run asyncio event loop in background thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def start(self):
        """Start the client"""
        # Start asyncio loop in background thread
        async_thread = threading.Thread(target=self.run_async_loop, daemon=True)
        async_thread.start()
        
        # Start tkinter main loop
        self.root.mainloop()

def main():
    """Main entry point"""
    print("=" * 70)
    print("🎮 Remote Control Client (Controller)")
    print("=" * 70)
    print("Use this to control a remote computer via Replit relay")
    print("Enter the Replit relay URL and target server ID")
    print("=" * 70)
    
    client = RemoteControlClient()
    client.start()

if __name__ == "__main__":
    main()
