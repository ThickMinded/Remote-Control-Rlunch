# Remote Control Software - File Index

## 📋 Quick Reference

### 🚀 Get Started (Read These First)
1. **QUICKSTART.md** - Fast setup instructions (5 minutes)
2. **README.md** - Complete documentation
3. **setup.bat / setup.sh** - Run this to install everything

### 💻 Main Applications
- **server.py** - Run on computer to be controlled (203 lines)
- **client.py** - Run on controlling computer (328 lines)

### 🎯 Easy Launchers (Windows)
- **start_server.bat** - Quick server start
- **start_client.bat** - Quick client start

### 📚 Documentation
- **PROJECT_OVERVIEW.md** - Architecture and technical details
- **TROUBLESHOOTING.md** - Solutions to common problems
- **README.md** - Full documentation with examples

### ⚙️ Configuration
- **requirements.txt** - Python dependencies
- **.replit** - Replit configuration for online hosting
- **replit.nix** - Replit environment setup
- **.gitignore** - Version control exclusions

### 🔧 Setup Scripts
- **setup.bat** - Windows automatic installation
- **setup.sh** - Linux/Mac automatic installation

---

## 📖 Reading Order

### For Beginners:
1. Read **QUICKSTART.md** (3 min)
2. Run **setup.bat** or **setup.sh**
3. Test locally with **start_server.bat** and **start_client.bat**
4. If issues, check **TROUBLESHOOTING.md**

### For Advanced Users:
1. Review **PROJECT_OVERVIEW.md** for architecture
2. Read **server.py** and **client.py** source code
3. Customize settings as needed
4. Deploy to Replit using **.replit** config

### For Deployment:
1. Create Replit account
2. Upload all files
3. Follow Replit section in **README.md**
4. Use **TROUBLESHOOTING.md** if issues arise

---

## 📁 File Details

| File | Purpose | When to Use |
|------|---------|------------|
| server.py | Main server application | Run on controlled computer |
| client.py | Main client application | Run on controlling computer |
| requirements.txt | Dependencies list | Reference for manual install |
| setup.bat | Windows installer | First time setup on Windows |
| setup.sh | Unix installer | First time setup on Linux/Mac |
| start_server.bat | Server launcher | Quick server start (Windows) |
| start_client.bat | Client launcher | Quick client start (Windows) |
| QUICKSTART.md | Quick guide | Want to start in 5 minutes |
| README.md | Full documentation | Need detailed instructions |
| PROJECT_OVERVIEW.md | Technical docs | Understanding architecture |
| TROUBLESHOOTING.md | Problem solving | Something not working |
| .replit | Replit config | Deploying to Replit |
| replit.nix | Replit environment | Replit dependencies |
| .gitignore | Git exclusions | Using version control |

---

## 🎯 Common Tasks

### Task: Install and Test Locally
1. Run `setup.bat` (Windows) or `bash setup.sh` (Unix)
2. Run `start_server.bat` in first terminal
3. Run `start_client.bat` in second terminal
4. In client, enter: `ws://localhost:8765`
5. Click "Connect"

### Task: Set Up on Local Network
1. Run server on Computer A
2. Note Computer A's IP address (shown in server)
3. Run client on Computer B
4. Enter: `ws://COMPUTER_A_IP:8765`
5. Click "Connect"

### Task: Deploy to Replit for Internet Access
1. Go to replit.com and sign up
2. Create new Python Repl
3. Upload all project files
4. Click "Run"
5. Note the URL (convert to ws:// format)
6. Use in client: `ws://your-repl-url:8765`

### Task: Troubleshoot Connection Issues
1. Check **TROUBLESHOOTING.md** → Connection Issues
2. Verify server is running
3. Test locally first (ws://localhost:8765)
4. Check firewall settings
5. Review server logs for errors

### Task: Improve Performance
1. Lower FPS in client (try 5-10)
2. Edit server.py: reduce quality (20-30)
3. Edit server.py: reduce scale (0.3-0.5)
4. Close unnecessary programs
5. See **TROUBLESHOOTING.md** → Performance Issues

### Task: Customize Settings
1. Read **PROJECT_OVERVIEW.md** → Customization
2. Edit server.py for quality/port changes
3. Edit client.py for default FPS
4. Restart both applications
5. Test changes

---

## 💡 Tips

- **Start Simple**: Test locally before internet deployment
- **Read Logs**: Terminal output shows what's happening
- **Check Docs**: Most questions answered in README.md
- **Security**: Only use on computers you own/control
- **Performance**: Lower FPS/quality for better speed

---

## 📞 Support Resources

| Issue Type | Check This File |
|------------|----------------|
| Installation problems | TROUBLESHOOTING.md → Installation Issues |
| Can't connect | TROUBLESHOOTING.md → Connection Issues |
| Slow performance | TROUBLESHOOTING.md → Performance Issues |
| Controls not working | TROUBLESHOOTING.md → Control Issues |
| Display problems | TROUBLESHOOTING.md → Display Issues |
| How does it work? | PROJECT_OVERVIEW.md → Technical Details |
| Quick setup | QUICKSTART.md |
| Complete guide | README.md |

---

## ✅ Project Status

**Version:** 1.0  
**Status:** ✅ Complete and tested  
**Files:** 14 total  
**Lines of Code:** ~550 (server + client)  
**Documentation:** 5 comprehensive guides  
**Platform Support:** Windows, Linux, macOS  
**Admin Required:** ❌ No  
**Internet Capable:** ✅ Yes (via Replit)  
**Click Accuracy:** ✅ Normalized coordinates  

---

**Need help?** Start with QUICKSTART.md, then README.md, then TROUBLESHOOTING.md
