# Remote Control Software

A Python-based remote desktop control solution that allows you to control one computer from another over the internet. Works without administrator privileges and uses accurate coordinate mapping for precise mouse control.

## Features

- **No Admin Required**: Works without administrator privileges on the server side
- **Online Connection**: Uses Replit for internet-based remote control
- **Accurate Mouse Control**: Normalized coordinate system ensures precise clicks
- **Real-time Screen Sharing**: Live screen capture and streaming
- **Full Control**: Mouse movements, clicks, keyboard input, and scrolling
- **Cross-platform**: Works on Windows, macOS, and Linux

## Components

- **server.py**: Runs on the computer to be controlled (host/server)
- **client.py**: Runs on the controlling computer (client)

## Installation

### Prerequisites

- Python 3.7 or higher
- No administrator privileges required

### Step 1: Install Python Dependencies

#### On the Server (Computer to be Controlled)

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install websockets pyautogui Pillow mss
```

#### On the Client (Controlling Computer)

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install websockets pyautogui Pillow
```

### Step 2: Deploy Server on Replit (For Online Access)

To enable online remote control, deploy the server on Replit:

1. **Create a Replit Account**
   - Go to [replit.com](https://replit.com)
   - Sign up or log in

2. **Create New Repl**
   - Click "Create Repl"
   - Choose "Python" template
   - Name it (e.g., "remote-control-server")

3. **Upload Files**
   - Upload `server.py`
   - Upload `requirements.txt`
   - Upload `.replit` (included in this project)

4. **Install Dependencies**
   - Replit will automatically install dependencies from `requirements.txt`
   - Or manually run: `pip install -r requirements.txt`

5. **Run the Server**
   - Click the "Run" button
   - Note the URL shown (e.g., `https://your-repl-name.your-username.repl.co`)

6. **Get WebSocket URL**
   - Replace `https://` with `ws://`
   - Add port `:8765`
   - Example: `ws://your-repl-name.your-username.repl.co:8765`

## Usage

### Option 1: Local Network (Same WiFi)

#### On Server Computer:
```bash
python server.py
```

The server will display its IP address. Note this down.

#### On Client Computer:
```bash
python client.py
```

1. Enter server URL: `ws://SERVER_IP:8765` (replace SERVER_IP with actual IP)
2. Click "Connect"
3. Control the remote computer!

### Option 2: Over Internet (Using Replit)

#### On Server Computer (via Replit):
- Ensure server is running on Replit
- Note your Replit WebSocket URL

#### On Client Computer:
```bash
python client.py
```

1. Enter server URL: `ws://your-repl.repl.co:8765`
2. Click "Connect"
3. Control the remote computer!

## Configuration

### Server Settings (in server.py)

```python
# Change port (default: 8765)
server = RemoteControlServer(host='0.0.0.0', port=8765)

# Adjust screen capture quality (lower = faster, higher = better quality)
quality=30  # Range: 1-100

# Adjust screen scale (lower = faster, higher = better resolution)
scale=0.5   # Range: 0.1-1.0
```

### Client Settings (in GUI)

- **FPS**: Adjust frame rate (1-30 fps) for performance
- Higher FPS = smoother but more bandwidth
- Lower FPS = better for slow connections

## How It Works

### Accurate Click Positioning

The system uses **normalized coordinates (0.0 to 1.0)** to ensure clicks work regardless of screen size differences:

1. Client captures click position on its display
2. Converts to normalized coordinates (0-1 range)
3. Sends to server
4. Server converts to its actual screen coordinates
5. Executes click at precise location

Example:
- Client clicks at center of 1920x1080 screen → (0.5, 0.5)
- Server with 2560x1440 screen receives (0.5, 0.5) → clicks at (1280, 720)
- Result: Click happens at center of server screen, regardless of resolution

### Security Considerations

⚠️ **Important Security Notes:**

- This software allows **full control** of the server computer
- Only connect to computers you own or have permission to control
- Use secure networks when possible
- Consider adding authentication for production use
- Monitor Replit usage to prevent unauthorized access

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to server
- Check firewall settings
- Ensure server is running
- Verify URL is correct (ws:// not http://)
- Check port 8765 is not blocked

**Problem**: "Connection refused" on Replit
- Ensure Replit is running (click Run button)
- Check if Replit URL is correct
- Try different port if 8765 is blocked

### Performance Issues

**Problem**: Laggy or slow performance
- Lower FPS in client (try 5-10 fps)
- Reduce quality in server.py (try quality=20)
- Reduce scale in server.py (try scale=0.3)
- Check internet connection speed

### Mouse/Keyboard Not Working

**Problem**: Clicks not registering
- Click on the canvas area to give it focus
- Check server logs for errors
- Ensure pyautogui is installed correctly

**Problem**: Keyboard not working
- Click canvas area first
- Check if server supports the key
- Some special keys may not work cross-platform

## Requirements

### Server Side:
- Python 3.7+
- websockets
- pyautogui
- Pillow (PIL)
- mss (for screen capture)

### Client Side:
- Python 3.7+
- websockets
- Pillow (PIL)
- tkinter (usually included with Python)

## License

This software is provided as-is for educational and personal use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review server/client logs for error messages
3. Ensure all dependencies are installed correctly

## Advanced Usage

### Custom Port

Change port in both server and client:

Server:
```python
server = RemoteControlServer(host='0.0.0.0', port=9999)
```

Client URL:
```
ws://server-address:9999
```

### Running as Background Service

**Windows:**
```bash
pythonw server.py
```

**Linux/Mac:**
```bash
nohup python3 server.py &
```

### Multiple Monitors

The server currently captures the primary monitor. To capture a specific monitor, modify `server.py`:

```python
# In capture_screen method
monitor = sct.monitors[2]  # Change 1 to desired monitor number
```

## Development

To modify or extend the software:

1. **Add Authentication**: Implement password/token system
2. **File Transfer**: Add file upload/download capability
3. **Chat**: Add text chat between client/server
4. **Multi-client**: Support multiple simultaneous connections
5. **Encryption**: Add TLS/SSL for secure connections

## Version History

- **v1.0**: Initial release with basic remote control functionality
  - Screen sharing
  - Mouse control
  - Keyboard control
  - Replit support

---

**Note**: Always ensure you have permission to remotely control a computer and follow local laws and regulations regarding remote access software.
