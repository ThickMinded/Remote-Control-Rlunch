# Troubleshooting Guide

## Installation Issues

### "Python not found"
**Solution:**
1. Download Python from python.org (version 3.7 or higher)
2. During installation, check "Add Python to PATH"
3. Restart terminal/command prompt
4. Run `python --version` to verify

### "pip not found"
**Solution:**
```bash
# Windows
python -m ensurepip

# Linux/Mac
python3 -m ensurepip
```

### Package installation fails
**Solution:**
```bash
# Try with --user flag
pip install --user websockets pyautogui Pillow mss

# Or upgrade pip first
python -m pip install --upgrade pip
```

### "Permission denied" during setup
**Solution:**
- Don't use admin/sudo - the software is designed to work without it
- Use `--user` flag: `pip install --user <package>`
- Or use virtual environment (see below)

## Connection Issues

### "Connection refused"
**Causes:**
- Server not running
- Wrong IP address or port
- Firewall blocking connection

**Solutions:**
1. Verify server is running (you should see "Server is running" message)
2. Check IP address is correct
3. Test on same computer first: `ws://localhost:8765`
4. Check firewall:
   - Windows: Allow Python through Windows Firewall
   - Mac: System Preferences → Security → Firewall
   - Linux: Check iptables or ufw settings

### "Connection timeout"
**Solutions:**
1. Verify network connectivity (ping the server)
2. Check if port 8765 is open:
   ```bash
   # Windows
   netstat -an | findstr 8765
   
   # Linux/Mac
   netstat -an | grep 8765
   ```
3. Try different port (change in both server and client)

### Replit connection fails
**Solutions:**
1. Ensure Replit is running (click Run button)
2. Check URL format: `ws://your-repl-name.your-username.repl.co:8765`
3. Some corporate networks block WebSockets - try different network
4. Replit may require paid plan for always-on servers

## Performance Issues

### Laggy/slow screen updates
**Solutions:**
1. **Lower FPS**: Set to 5-10 fps in client
2. **Reduce quality**: In server.py, change `quality=30` to `quality=20`
3. **Reduce scale**: In server.py, change `scale=0.5` to `scale=0.3`
4. **Close other programs**: Free up CPU/network
5. **Check network speed**: Minimum 1 Mbps recommended

### High CPU usage
**Solutions:**
1. Lower FPS in client
2. Reduce screen capture quality
3. Close other programs
4. Check for infinite loops in code

### Memory issues
**Solutions:**
1. Restart server every few hours
2. Reduce screen capture resolution
3. Close unused programs

## Control Issues

### Mouse clicks not working
**Solutions:**
1. **Click on canvas**: The black display area must have focus
2. **Check server logs**: Look for error messages
3. **Test locally first**: Use `ws://localhost:8765`
4. **Verify pyautogui**: Run `python -c "import pyautogui; print(pyautogui.position())"`

### Keyboard not working
**Solutions:**
1. **Focus canvas**: Click on the display area first
2. **Check special keys**: Some keys may not work cross-platform
3. **Try simple keys first**: Test with 'a', 'b', 'c' before special keys
4. **Language issues**: Ensure both computers use same keyboard layout

### Clicks are offset/inaccurate
**This should be rare with normalized coordinates, but if it happens:**

**Debug:**
1. Check server logs for coordinate values
2. Verify screen resolution detection
3. Test with full screen client window

**Solutions:**
1. Restart both client and server
2. Ensure client window is not resized during use
3. Check if multiple monitors are causing issues
4. Verify pyautogui is working: `python -c "import pyautogui; pyautogui.click()"`

### Scroll not working
**Solutions:**
1. Some applications don't respond to programmatic scrolling
2. Try using keyboard (Page Up/Down) instead
3. Check if mouse is over scrollable area

## Display Issues

### Black screen
**Solutions:**
1. Wait a few seconds - first frame may take time
2. Check server is running
3. Look for errors in server terminal
4. Verify MSS is installed: `python -c "import mss"`

### Frozen screen
**Solutions:**
1. Check FPS is > 0
2. Verify network connection
3. Restart client
4. Check server logs for errors

### Poor quality/pixelated
**Solutions:**
1. Increase quality: Change `quality=30` to `quality=60`
2. Increase scale: Change `scale=0.5` to `scale=0.8`
3. Note: Higher quality = slower performance

### Colors wrong
**Solutions:**
1. This is normal with JPEG compression
2. Increase quality setting
3. Some color loss is expected for performance

## Platform-Specific Issues

### Windows

**"vcruntime140.dll missing"**
- Install Visual C++ Redistributable from Microsoft

**"Failed to get screen size"**
- Update display drivers
- Check display scaling settings

### macOS

**"Screen capture not permitted"**
1. System Preferences → Security & Privacy → Privacy
2. Select "Screen Recording"
3. Add Python or Terminal
4. Restart terminal

**"Accessibility permissions needed"**
1. System Preferences → Security & Privacy → Accessibility
2. Add Python or Terminal
3. Restart application

### Linux

**"X server not found"**
- Install X11: `sudo apt-get install xorg`
- Or use Xvfb for headless: `xvfb-run python3 server.py`

**"Tkinter not found"**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

## Replit-Specific Issues

### "Display :99 not found"
- Replit uses virtual display
- This is normal, server should still work
- Replit may have limitations with GUI applications

### Server stops after inactivity
- Free Replit accounts sleep after inactivity
- Consider upgrading to paid plan for always-on
- Or use alternative hosting (AWS, Heroku, etc.)

### Packages won't install
- Check replit.nix is present
- Manually add packages to replit.nix
- Try installing in Shell tab

## Error Messages

### "Fail-safe triggered"
**Cause:** PyAutoGUI safety feature (mouse in corner)
**Solution:** 
- Move mouse away from screen corners on server
- Or disable: `pyautogui.FAILSAFE = False` (not recommended)

### "WebSocket closed with code 1006"
**Cause:** Connection unexpectedly closed
**Solution:**
- Check network stability
- Look for errors on server side
- Verify both sides are using same protocol version

### "Message too large"
**Cause:** Screen capture too big
**Solution:**
- Reduce scale factor
- Reduce quality
- Increase max_size in server.py websocket settings

### "JSON decode error"
**Cause:** Corrupted message
**Solution:**
- Check network quality
- Restart both client and server
- This is usually temporary

## Getting Help

If issues persist:

1. **Check logs**: Look at server/client terminal output
2. **Test locally**: Try `ws://localhost:8765` first
3. **Isolate problem**: Test each component separately
4. **Check dependencies**: Verify all packages are installed
5. **Review code**: Look for commented debug options

## Debug Mode

Enable detailed logging:

**In server.py:**
```python
logging.basicConfig(level=logging.DEBUG)
```

**In client.py:**
```python
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed information about all operations.

## Still Having Issues?

Create a detailed bug report including:
- Operating system and version
- Python version (`python --version`)
- Error messages (full text)
- Steps to reproduce
- Server and client logs
- Network setup (local/internet/Replit)

---

**Remember:** Most issues are network or permissions related. Start with local testing, then move to internet once working.
