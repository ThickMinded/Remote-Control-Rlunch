# Installation & Testing Checklist

Use this checklist to ensure proper setup and testing.

## ✅ Pre-Installation Checklist

- [ ] Python 3.7 or higher installed
- [ ] Internet connection available
- [ ] Two computers available for testing (or one for local test)
- [ ] Administrator privileges NOT required ✓

## ✅ Installation Steps

### On Server Computer (to be controlled):

- [ ] Download/extract all project files
- [ ] Run `setup.bat` (Windows) or `bash setup.sh` (Linux/Mac)
- [ ] Verify no errors during installation
- [ ] Test Python: `python --version`
- [ ] Test imports: `python -c "import websockets, pyautogui, mss"`

### On Client Computer (controller):

- [ ] Download/extract all project files
- [ ] Run `setup.bat` (Windows) or `bash setup.sh` (Linux/Mac)
- [ ] Verify no errors during installation
- [ ] Test Python: `python --version`
- [ ] Test imports: `python -c "import websockets, tkinter"`

## ✅ Local Testing (Same Computer)

- [ ] Open Terminal/Command Prompt #1
- [ ] Run `python server.py` (or `start_server.bat`)
- [ ] Verify message: "Server is running"
- [ ] Open Terminal/Command Prompt #2
- [ ] Run `python client.py` (or `start_client.bat`)
- [ ] In client, enter URL: `ws://localhost:8765`
- [ ] Click "Connect" button
- [ ] Verify status changes to "Connected" (green)
- [ ] See your screen displayed in client window
- [ ] Test mouse click on client window
- [ ] Test mouse movement
- [ ] Test keyboard input (click canvas first)
- [ ] Test right-click
- [ ] Test scroll
- [ ] Adjust FPS (try 5, 10, 20)
- [ ] Verify FPS changes affect smoothness
- [ ] Click "Disconnect"
- [ ] Close both applications

## ✅ Local Network Testing (Two Computers)

### Server Computer:

- [ ] Run `python server.py`
- [ ] Note the IP address displayed (e.g., 192.168.1.100)
- [ ] Verify "Server is running" message
- [ ] Keep terminal open

### Client Computer:

- [ ] Run `python client.py`
- [ ] Enter URL: `ws://SERVER_IP:8765` (replace SERVER_IP)
- [ ] Click "Connect"
- [ ] Verify connection successful
- [ ] Test all controls (mouse, keyboard, scroll)
- [ ] Test performance at different FPS settings
- [ ] Verify clicks are accurate
- [ ] Test for 5+ minutes to check stability

### Firewall Configuration (if connection fails):

- [ ] Windows: Allow Python through Windows Firewall
- [ ] Mac: System Preferences → Security → Firewall → Allow
- [ ] Linux: `sudo ufw allow 8765` (if using ufw)

## ✅ Replit Deployment (Internet Access)

### Setup Replit:

- [ ] Create account at replit.com
- [ ] Click "Create Repl"
- [ ] Select "Python" template
- [ ] Name your Repl (e.g., "remote-control-server")
- [ ] Upload `server.py`
- [ ] Upload `requirements.txt`
- [ ] Upload `.replit`
- [ ] Upload `replit.nix`
- [ ] Click "Run" button
- [ ] Wait for dependencies to install
- [ ] Verify "Server is running" appears

### Get Replit URL:

- [ ] Note your Replit URL (shown at top)
- [ ] Format: `https://your-repl.your-username.repl.co`
- [ ] Convert to WebSocket: `ws://your-repl.your-username.repl.co:8765`
- [ ] Copy this URL for client

### Test from Client:

- [ ] Run client on your local computer
- [ ] Enter Replit WebSocket URL
- [ ] Click "Connect"
- [ ] Verify connection (may take 10-20 seconds first time)
- [ ] Test all controls
- [ ] Test from different network (mobile hotspot, etc.)

## ✅ Performance Testing

### Bandwidth Test:

- [ ] Start with FPS = 10
- [ ] Monitor network usage
- [ ] Try FPS = 5 (slower but less bandwidth)
- [ ] Try FPS = 20 (faster but more bandwidth)
- [ ] Find optimal setting for your network

### Quality Test:

- [ ] Edit server.py, change `quality=30` to `quality=20`
- [ ] Restart server
- [ ] Test - should be faster but lower quality
- [ ] Try `quality=50` - better quality but slower
- [ ] Reset to `quality=30` (good balance)

### Scale Test:

- [ ] Edit server.py, change `scale=0.5` to `scale=0.3`
- [ ] Restart server
- [ ] Test - should be faster but lower resolution
- [ ] Try `scale=0.7` - better resolution but slower
- [ ] Reset to `scale=0.5` (good balance)

## ✅ Accuracy Testing

### Mouse Click Accuracy:

- [ ] On server, open Notepad or Text Editor
- [ ] From client, try clicking specific letters
- [ ] Verify clicks hit correct positions
- [ ] Try corners of screen
- [ ] Try center of screen
- [ ] Test with different client window sizes
- [ ] Verify clicks remain accurate

### Keyboard Accuracy:

- [ ] Click canvas in client to focus
- [ ] Type: "Hello World"
- [ ] Verify text appears correctly on server
- [ ] Test special keys (Enter, Backspace, Arrows)
- [ ] Test Ctrl+C, Ctrl+V (may vary by OS)

## ✅ Stability Testing

- [ ] Connect client to server
- [ ] Leave connected for 30 minutes
- [ ] Verify no disconnections
- [ ] Check memory usage (should be stable)
- [ ] Check CPU usage (should be reasonable)
- [ ] Disconnect and reconnect successfully

## ✅ Security Verification

- [ ] Verify server runs without admin privileges
- [ ] Check no elevation prompts appear
- [ ] Verify failsafe works (move mouse to corner on server)
- [ ] Only connect to computers you own/control

## ✅ Documentation Review

- [ ] Read QUICKSTART.md for fast setup
- [ ] Read README.md for complete guide
- [ ] Bookmark TROUBLESHOOTING.md for issues
- [ ] Review ARCHITECTURE.md to understand system
- [ ] Keep INDEX.md handy for file reference

## ✅ Troubleshooting Verification

If any test fails, check:

- [ ] Review error messages in terminal
- [ ] Check TROUBLESHOOTING.md for solution
- [ ] Verify all dependencies installed
- [ ] Test locally before testing remotely
- [ ] Check firewall settings
- [ ] Verify correct URLs being used
- [ ] Look for typos in configuration

## ✅ Final Verification

- [ ] Server starts without errors
- [ ] Client starts without errors
- [ ] Connection succeeds
- [ ] Screen displays properly
- [ ] Mouse control works accurately
- [ ] Keyboard control works
- [ ] Scroll works
- [ ] Performance is acceptable
- [ ] Can disconnect and reconnect
- [ ] Works over internet (if using Replit)

## 📋 Common Issues Quick Fix

| Issue | Quick Fix |
|-------|-----------|
| Connection refused | Check server is running, verify URL |
| Black screen | Wait 5 seconds, check server logs |
| Laggy | Lower FPS to 5-10 |
| Clicks offset | This shouldn't happen - report bug |
| Keyboard not working | Click canvas first |
| Can't install packages | Use `--user` flag |

## 🎉 Success Criteria

You're ready to use the software when:

✅ Server runs without admin  
✅ Client connects successfully  
✅ Screen displays in real-time  
✅ Mouse clicks are accurate  
✅ Keyboard input works  
✅ Performance is acceptable  
✅ Connection is stable  

---

**Congratulations!** If all checkboxes are complete, your remote control software is fully functional!

For daily use, simply:
1. Run server on computer to control
2. Run client on controlling computer
3. Connect and start controlling!

Keep TROUBLESHOOTING.md handy for any issues that arise.
