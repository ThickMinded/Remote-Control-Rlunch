# 🖥️ Remote Control Software v2.0 - RELAY ARCHITECTURE

## 🎯 What is This?

A complete Python-based remote desktop control solution using a **3-component relay architecture**:
1. **relay.py** - Runs on Replit (bridge/meeting point)
2. **server.py** - Runs on YOUR computer (to be controlled)
3. **client.py** - Runs on controller's device

**No administrator privileges required!**

## 🌐 How It Works

```
YOUR COMPUTER (Server) ←→ REPLIT (Relay) ←→ CONTROLLER (Client)
  (To be controlled)      (Bridge/Tunnel)     (Controls remotely)
```

## ⚡ Quick Start (5 Minutes)

### Step 1: Deploy Relay to Replit

1. Go to [replit.com](https://replit.com) and create account
2. Click "Create Repl" → Choose "Python"
3. Upload these files: `relay.py`, `requirements.txt`, `.replit`
4. Click **"Run"** button
5. Note your URL: `https://your-repl.username.repl.co`
6. Convert to WebSocket: `ws://your-repl.username.repl.co:8765`

### Step 2: Setup Server (Your Computer)

**Windows:**
1. Run `setup.bat`
2. Run `start_server.bat`
3. Enter your Replit relay URL: `ws://your-repl.repl.co:8765`
4. Enter server ID: `my_computer` (or any name)
5. Wait for "✅ Ready to accept client connections!"

**Linux/Mac:**
```bash
bash setup.sh
python3 server.py ws://your-repl.repl.co:8765 my_computer
```

### Step 3: Connect Client (Controller)

**Windows:**
1. Run `start_client.bat` on controlling device
2. Enter Relay URL: `ws://your-repl.repl.co:8765`
3. Enter Server ID: `my_computer` (same as Step 2)
4. Click "Connect"
5. **Done!** Control your computer remotely 🎉

## 📚 Quick Links

| File | Purpose |
|------|---------|
| **QUICKSTART.md** | Detailed setup guide |
| **ARCHITECTURE.md** | How relay system works |
| **TROUBLESHOOTING.md** | Fix common problems |

## ✨ Key Features

✅ **No Admin Required** - Works without administrator privileges  
✅ **Accurate Clicks** - Normalized coordinates for precision  
✅ **Internet Ready** - Use Replit as relay/bridge  
✅ **Cross-Platform** - Windows, Linux, macOS  
✅ **Full Control** - Mouse, keyboard, scroll  
✅ **Your Computer** - Control YOUR actual PC (not Replit's)  

## 🔧 Architecture

### NEW 3-Component System:

1. **Relay (relay.py)** - Runs on Replit
   - Acts as meeting point/bridge
   - Forwards messages between server and clients
   - Always online (Replit hosting)

2. **Server (server.py)** - Runs on YOUR computer
   - Connects TO relay
   - Captures screen, executes commands
   - Your actual computer being controlled

3. **Client (client.py)** - Runs on controller device
   - Connects TO relay
   - Displays screen, sends commands
   - Can be laptop, another PC, etc.

## 📦 What's Included

- **relay.py** - Replit bridge server (NEW!)
- **server.py** - Runs on computer to be controlled (UPDATED)
- **client.py** - Runs on controlling computer (UPDATED)
- **Setup scripts** - Automatic installation
- **Launch scripts** - Quick start buttons
- **Complete docs** - Updated guides

## 🎯 Next Steps

1. **Deploy relay to Replit** (see Step 1 above)
2. **Run server on your computer** (see Step 2)
3. **Connect client from anywhere** (see Step 3)
4. **Start controlling!** 🚀

---

**Version**: 2.0 (Relay Architecture)  
**Updated**: December 2025  
**Status**: ✅ Fully functional with relay system

Read **QUICKSTART.md** for detailed setup!
