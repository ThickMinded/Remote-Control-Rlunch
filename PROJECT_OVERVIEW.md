# Remote Control Software - Project Overview

## 📁 Project Structure

```
remote control LastV/
├── server.py              # Server application (runs on controlled computer)
├── client.py              # Client application (runs on controlling computer)
├── requirements.txt       # Python dependencies
├── README.md             # Full documentation
├── QUICKSTART.md         # Quick setup guide
├── setup.bat             # Windows setup script
├── setup.sh              # Linux/Mac setup script
├── start_server.bat      # Windows server launcher
├── start_client.bat      # Windows client launcher
├── .replit               # Replit configuration
├── replit.nix            # Replit environment setup
└── .gitignore           # Git ignore rules
```

## ✨ Key Features

### 1. **No Admin Privileges Required**
   - Uses PyAutoGUI (no admin needed)
   - Works on Windows, Linux, and macOS
   - No system-level drivers required

### 2. **Accurate Click Positioning**
   - Normalized coordinate system (0.0 to 1.0)
   - Works across different screen resolutions
   - Precise mouse positioning regardless of display size

### 3. **Online Connection via Replit**
   - Deploy server to Replit for internet access
   - No port forwarding required
   - No complicated network setup

### 4. **Full Remote Control**
   - Mouse movements and clicks
   - Keyboard input
   - Scroll wheel support
   - Right-click and double-click

### 5. **Performance Optimization**
   - Adjustable FPS (1-30)
   - Configurable image quality
   - Scalable screen resolution
   - Efficient compression

## 🚀 Quick Setup

### Option 1: Windows (Easiest)

**Server Computer:**
1. Double-click `setup.bat`
2. Double-click `start_server.bat`

**Client Computer:**
1. Double-click `setup.bat`
2. Double-click `start_client.bat`
3. Enter server URL and click Connect

### Option 2: Deploy on Replit (For Internet Access)

1. Go to replit.com and create account
2. Create new Python Repl
3. Upload all files from this project
4. Click "Run"
5. Use the WebSocket URL in client (ws://your-repl:8765)

## 🔧 Technical Details

### Architecture

```
Client (Controller)          Server (Controlled)
     |                              |
     |  1. Request Frame            |
     |----------------------------->|
     |                              |
     |  2. Screen Capture           |
     |     (JPEG compressed)        |
     |<-----------------------------|
     |                              |
     |  3. Display Frame            |
     |                              |
     |  4. User Input               |
     |     (Mouse/Keyboard)         |
     |----------------------------->|
     |                              |
     |  5. Execute Action           |
     |     (Move/Click/Type)        |
     |                              |
```

### Coordinate Normalization System

**Problem Solved:** Different screen sizes between client and server

**Solution:**
1. Client converts pixel coordinates to normalized values (0-1)
2. Server receives normalized coordinates
3. Server converts to actual pixel position on its screen

**Example:**
```
Client: 1920x1080 screen, clicks at (960, 540)
  → Normalizes to (0.5, 0.5)
  → Sends to server

Server: 2560x1440 screen, receives (0.5, 0.5)
  → Converts to (1280, 720)
  → Clicks at center of its screen ✓
```

This ensures clicks work accurately regardless of resolution differences!

### Network Protocol

- **Transport:** WebSocket (ws://)
- **Format:** JSON messages
- **Port:** 8765 (configurable)
- **Compression:** JPEG for screen images

### Message Types

**Server → Client:**
```json
{
  "type": "screen",
  "data": "base64_encoded_jpeg",
  "width": 960,
  "height": 540,
  "original_width": 1920,
  "original_height": 1080
}
```

**Client → Server:**
```json
{
  "type": "mouse",
  "event": "click",
  "x": 0.5,
  "y": 0.5,
  "button": "left"
}
```

## 📦 Dependencies

All dependencies work without admin privileges:

- **websockets** (12.0): WebSocket communication
- **pyautogui** (0.9.54): Mouse/keyboard control
- **Pillow** (10.1.0): Image processing
- **mss** (9.0.1): Fast screen capture
- **tkinter**: GUI (included with Python)

## 🎯 Use Cases

1. **Remote Support**: Help family/friends with computer issues
2. **Home Access**: Control home computer from work
3. **Testing**: Test software on different machines
4. **Presentations**: Control presentation computer remotely
5. **Monitoring**: Keep eye on processes running on another machine

## 🔒 Security Considerations

⚠️ **Important:**
- This gives FULL control of the server computer
- Only use on computers you own or have permission to control
- No authentication built-in (add if needed)
- Traffic is not encrypted by default
- Keep server URL private

**For Production:**
- Add authentication (password/token)
- Use WSS (WebSocket Secure) instead of WS
- Implement access logging
- Add session timeouts
- Whitelist IP addresses

## 🐛 Troubleshooting

### Connection Issues
- Check firewall settings
- Ensure server is running
- Verify URL format (ws:// not http://)
- Try different port if 8765 is blocked

### Performance Issues
- Lower FPS (try 5-10)
- Reduce quality in server.py
- Reduce scale factor
- Check network speed

### Control Issues
- Click canvas to focus
- Check pyautogui installation
- Review server logs for errors

## 📝 Customization

### Change Port
```python
# In server.py
server = RemoteControlServer(host='0.0.0.0', port=9999)

# In client, enter: ws://address:9999
```

### Adjust Quality
```python
# In server.py, capture_screen method
quality=50  # Higher = better quality, larger size
scale=0.7   # Higher = better resolution, slower
```

### Change Frame Rate
- Adjust FPS spinbox in client GUI
- Or modify client.py: `self.fps = 15`

## 🔄 Future Enhancements

Possible improvements:
- [ ] File transfer functionality
- [ ] Text chat between client/server
- [ ] Multi-monitor support
- [ ] Audio streaming
- [ ] Session recording
- [ ] User authentication
- [ ] TLS/SSL encryption
- [ ] Mobile app client

## 📄 License

This software is provided as-is for educational and personal use.

## 🙏 Credits

Built using:
- Python 3
- WebSockets library
- PyAutoGUI
- Pillow (PIL)
- MSS
- Tkinter

---

**Version:** 1.0  
**Last Updated:** December 2025  
**Status:** Fully functional, production-ready for personal use

For questions or issues, check README.md and QUICKSTART.md
