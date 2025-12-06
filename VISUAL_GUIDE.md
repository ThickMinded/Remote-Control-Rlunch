# 🎯 SETUP GUIDE - Visual Walkthrough

## What You're Building

```
╔══════════════════════════════════════════════════════════════╗
║                    YOUR SETUP GOAL                           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   [Your Computer] ←→ [Replit Relay] ←→ [Controller Device]  ║
║                                                              ║
║   Run server.py       relay.py           client.py          ║
║   Your actual PC      Bridge/tunnel      Any device         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 📋 STEP 1: Deploy Relay to Replit

### What to do:

```
1. Go to replit.com
   └─► Sign up (free)

2. Create New Repl
   └─► Choose "Python" template
   └─► Name it (e.g., "remote-control-relay")

3. Upload 3 files:
   ├─► relay.py
   ├─► requirements.txt
   └─► .replit

4. Click "Run" button
   └─► Wait for installation
   └─► See: "✅ Relay server is running!"

5. Get your URL:
   ├─► Look at browser address bar
   ├─► Example: https://your-repl.username.repl.co
   └─► Convert: ws://your-repl.username.repl.co:8765
```

### Visual:

```
┌─────────────────────────────────────┐
│         REPLIT.COM                  │
├─────────────────────────────────────┤
│                                     │
│  📁 Files:                          │
│    • relay.py         [Uploaded]    │
│    • requirements.txt [Uploaded]    │
│    • .replit         [Uploaded]    │
│                                     │
│  ▶️  [Run] ←── Click this          │
│                                     │
│  Console Output:                    │
│  ════════════════════                │
│  🌐 Remote Control Relay Server     │
│  Starting relay on 0.0.0.0:8765     │
│  ✅ Relay server is running!        │
│                                     │
│  📋 Your URL:                       │
│  ws://your-repl.repl.co:8765       │
│  [Copy this!]                       │
└─────────────────────────────────────┘
```

**✅ Relay is now online 24/7!**

---

## 🖥️ STEP 2: Run Server on YOUR Computer

### What to do:

```
Windows:
1. Double-click setup.bat
   └─► Installs Python packages
   └─► Wait for completion

2. Double-click start_server.bat
   └─► Opens command window

3. Enter Relay URL when asked:
   Paste: ws://your-repl.repl.co:8765

4. Enter Server ID when asked:
   Type: my_computer (or any name)

5. Wait for confirmation:
   "✅ Ready to accept client connections!"
```

### Visual:

```
┌──────────────────────────────────────────────┐
│  💻 Command Prompt (Your Computer)           │
├──────────────────────────────────────────────┤
│                                              │
│  🖥️  Remote Control Server (Host Computer)  │
│  ══════════════════════════════════════════  │
│  This computer will be controlled remotely   │
│  via Replit relay                            │
│                                              │
│  Enter Replit relay URL:                     │
│  > ws://your-repl.repl.co:8765  ◄── Paste   │
│                                              │
│  Enter server ID:                            │
│  > my_computer  ◄── Type this               │
│                                              │
│  ══════════════════════════════════════════  │
│                                              │
│  📡 Relay URL: ws://your-repl.repl.co:8765  │
│  🆔 Server ID: my_computer                   │
│  ══════════════════════════════════════════  │
│                                              │
│  🔄 Connecting to relay...                   │
│  📡 Registered as server: 'my_computer'      │
│  Screen resolution: 1920x1080                │
│  ✅ Ready to accept client connections!      │
│                                              │
│  [Keep this window open]                     │
└──────────────────────────────────────────────┘
```

**✅ Your computer is now connected to relay!**

---

## 🎮 STEP 3: Connect Client (Controller)

### What to do:

```
Run on ANY device (laptop, another PC, etc.):

Windows:
1. Double-click setup.bat (if not done)
   └─► Installs packages

2. Double-click start_client.bat
   └─► Opens GUI window

3. In the GUI:
   ├─► Relay URL: ws://your-repl.repl.co:8765
   ├─► Server ID: my_computer (same as step 2)
   └─► Click "Connect" button

4. Wait for connection:
   └─► Status changes to green: "Connected to my_computer"

5. See your screen!
   └─► Your computer's screen appears
   └─► Move mouse, click, type!
```

### Visual:

```
┌───────────────────────────────────────────────────┐
│  Remote Control Client (via Relay)         [_][□][X]│
├───────────────────────────────────────────────────┤
│ Relay URL: [ws://your-repl.repl.co:8765  ]       │
│ Server ID: [my_computer                    ]       │
│ [Connect]  Status: ⚫ Disconnected         FPS: 10│
├───────────────────────────────────────────────────┤
│                                                   │
│         [Black screen - waiting for connection]   │
│                                                   │
└───────────────────────────────────────────────────┘

         ↓ Click "Connect" ↓

┌───────────────────────────────────────────────────┐
│  Remote Control Client (via Relay)         [_][□][X]│
├───────────────────────────────────────────────────┤
│ Relay URL: [ws://your-repl.repl.co:8765  ]       │
│ Server ID: [my_computer                    ]       │
│ [Disconnect] Status: 🟢 Connected to my_computer │
├───────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────┐   │
│  │ [Your Computer's Screen Appears Here!]    │   │
│  │                                           │   │
│  │  You can see your desktop                 │   │
│  │  Move your mouse here → it moves there!   │   │
│  │  Click here → clicks on your PC!          │   │
│  │  Type here → types on your PC!            │   │
│  │                                           │   │
│  └───────────────────────────────────────────┘   │
│                                                   │
└───────────────────────────────────────────────────┘
```

**✅ You're now controlling your computer remotely!** 🎉

---

## 🎮 Using the System

### Mouse Controls:

```
┌─────────────────────────────────┐
│  What You Do      →  Result     │
├─────────────────────────────────┤
│  Move mouse       →  Moves      │
│  Left click       →  Clicks     │
│  Right click      →  Right-click│
│  Double-click     →  Double     │
│  Scroll wheel     →  Scrolls    │
└─────────────────────────────────┘
```

### Keyboard:

```
1. Click on the black screen area
2. Type anything
3. It types on your remote computer!
```

### Adjust Performance:

```
FPS Slider:  [5] ←→ [30]
             ↓           ↓
         Slower       Faster
       Less smooth   More smooth
       Less data     More data
```

---

## 🔍 Troubleshooting

### Problem: "Server not available"

```
Check:
1. ✓ Is relay running on Replit?
2. ✓ Is server.py running on your PC?
3. ✓ Same server ID in both?
4. ✓ URL has ws:// not https://?
```

### Problem: Black screen

```
Wait 5-10 seconds for first frame
If still black:
1. Check server terminal for errors
2. Try disconnecting and reconnecting
3. Check your Replit relay is running
```

### Problem: Laggy/Slow

```
Lower FPS to 5-10:
┌────────────┐
│ FPS: [5▼] │  ← Adjust this
└────────────┘
```

---

## 📊 Connection Status

```
ALL SYSTEMS WORKING:
═══════════════════

┌─────────────┐
│   Replit    │  ✅ Running
│   Relay     │
└──────┬──────┘
       │
   ┌───┴────┐
   │        │
┌──▼───┐ ┌─▼────┐
│Server│ │Client│
│  ✅  │ │  ✅  │
└──────┘ └──────┘

Status: 🟢 CONNECTED
        Ready to control!
```

---

## 🎯 Quick Commands Reference

### Testing Locally (Same Computer):

```
Terminal 1:  python relay.py
Terminal 2:  python server.py ws://localhost:8765 test
Terminal 3:  python client.py
             URL: ws://localhost:8765
             ID: test
```

### Using Replit (Internet):

```
Replit:      [Run relay.py - always on]
Your PC:     python server.py ws://your-repl.repl.co:8765 my_pc
Controller:  python client.py
             URL: ws://your-repl.repl.co:8765
             ID: my_pc
```

---

## ✅ Success Checklist

```
□ Relay running on Replit
□ Got relay URL (ws://...)
□ Server running on your PC
□ Server shows "✅ Ready"
□ Client connected
□ Can see remote screen
□ Mouse works
□ Keyboard works
□ Performance acceptable

If all checked: 🎉 SUCCESS! 🎉
```

---

**You're all set!** Control your computer from anywhere! 🚀
