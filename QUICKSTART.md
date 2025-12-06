# Quick Start Guide - Relay Architecture

## 🎯 3-Component System

1. **Relay** (Replit) - Bridge/meeting point
2. **Server** (Your PC) - Computer to control
3. **Client** (Controller) - Controls remotely

---

## 🚀 Setup in 3 Steps

### STEP 1: Deploy Relay to Replit (5 minutes)

1. Go to **replit.com** → Create account
2. Click **"Create Repl"** → Choose **"Python"**
3. Upload these 3 files:
   - `relay.py`
   - `requirements.txt`
   - `.replit`
4. Click **"Run"** button
5. **Copy your URL**: Look at top of page
   - Example: `https://your-repl.username.repl.co`
   - Convert to WebSocket: `ws://your-repl.username.repl.co:8765`
   - **Save this URL!** You'll need it for steps 2 and 3

✅ **Relay is now running 24/7 on Replit!**

---

### STEP 2: Run Server on YOUR Computer (2 minutes)

This is the computer you want to control.

#### Windows:
1. Double-click **`setup.bat`** (installs dependencies)
2. Double-click **`start_server.bat`**
3. When prompted:
   - **Relay URL**: Paste `ws://your-repl.repl.co:8765`
   - **Server ID**: Type `my_computer` (or any name you want)
4. Wait for message: **"✅ Ready to accept client connections!"**

#### Linux/Mac:
```bash
bash setup.sh
python3 server.py ws://your-repl.repl.co:8765 my_computer
```

✅ **Your computer is now connected to relay!**

---

### STEP 3: Connect Client (1 minute)

Run this on the device you want to use as controller.

#### Windows:
1. Double-click **`setup.bat`** (if not already done)
2. Double-click **`start_client.bat`**
3. In the GUI window:
   - **Relay URL**: Enter `ws://your-repl.repl.co:8765`
   - **Server ID**: Enter `my_computer` (same as Step 2)
4. Click **"Connect"**

#### Linux/Mac:
```bash
bash setup.sh
python3 client.py
# Then enter relay URL and server ID in GUI
```

✅ **You're now controlling your computer remotely!** 🎉

---

## 🧪 Test Locally First (Optional)

Before using Replit, test on one computer:

**Terminal 1:**
```bash
python relay.py
```

**Terminal 2:**
```bash
python server.py ws://localhost:8765 my_computer
```

**Terminal 3:**
```bash
python client.py
# Enter: ws://localhost:8765 and my_computer
```

---

## 🎮 Usage

### Controls:
- **Mouse**: Move, click, right-click, scroll
- **Keyboard**: Type anything (click on screen first)
- **FPS**: Adjust speed (1-30 fps)

### Tips:
- Click on black screen area to enable keyboard
- Lower FPS (5-10) for slower connections
- Keep server running while controlling

---

## ❓ Common Issues

| Problem | Solution |
|---------|----------|
| "Server not available" | Check server is running and connected to relay |
| Black screen | Wait 5-10 seconds for first frame |
| Can't connect | Verify relay URL has `ws://` not `https://` |
| Laggy | Lower FPS to 5-10 |
| Keyboard not working | Click on screen area first |

Full troubleshooting: **TROUBLESHOOTING.md**

---

## 🌍 Control from Anywhere

Once set up:
1. Keep relay running on Replit (free tier restarts after inactivity)
2. Run server.py on your computer anytime
3. Run client.py from any device with your relay URL
4. Control your PC from anywhere! 🌍

---

## 🔐 Security

⚠️ Keep your **Server ID** private! Anyone with your relay URL and server ID can control your computer.

For more security:
- Use unique server IDs
- Change ID regularly
- Only use on trusted networks

---

## 📚 More Info

- **Architecture details**: `ARCHITECTURE.md`
- **Full guide**: `README.md`
- **File reference**: `INDEX.md`
- **Problems?**: `TROUBLESHOOTING.md`

---

**That's it!** You now have a working remote control system. 🚀
