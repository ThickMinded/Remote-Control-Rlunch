# System Architecture - Relay System## 🎨 Visual Overview - NEW Relay Architecture```┌──────────────────────────────────────────────────────────────────┐│              REMOTE CONTROL SYSTEM v2.0 (RELAY)                  │└──────────────────────────────────────────────────────────────────┘YOUR HOME/OFFICE                REPLIT CLOUD              ANYWHERE┌─────────────────┐          ┌──────────────┐        ┌─────────────┐│  YOUR COMPUTER  │          │    RELAY     │        │   CLIENT    ││   (Server)      │◄────────►│  (Bridge)    │◄──────►│(Controller) ││                 │          │              │        │             ││  • server.py    │          │  relay.py    │        │ client.py   ││  • Screen       │          │              │        │ • Display   ││  • Mouse/Keys   │          │  Forwards    │        │ • Input     ││                 │          │  Messages    │        │             │└─────────────────┘          └──────────────┘        └─────────────┘   Connects TO                  Always On              Connects TO     Relay                     (No Firewall            Relay                                 Issues!)```## 🔄 Complete Data Flow### 1. Initial Connection Setup```Step 1: Deploy Relay┌─────────────┐│   Replit    ││  relay.py   │ ◄─── Upload and run└─────┬───────┘      │ Listening on port 8765      │ ws://your-repl.repl.co:8765      ▼Step 2: Server Connects┌─────────────┐│ YOUR PC     ││ server.py   │ ──► Register as "my_computer"└─────────────┘      Send: {type: "register_server",                            server_id: "my_computer"}                     ▼                ┌─────────────┐                │   Relay     │                │ Stores:     │                │ "my_computer"│                │  → websocket │                └─────────────┘                     ▼              ✅ Server Ready!Step 3: Client Connects┌─────────────┐│   Client    ││ client.py   │ ──► Request "my_computer"└─────────────┘      Send: {type: "register_client",                           server_id: "my_computer"}                     ▼                ┌─────────────┐                │   Relay     │                │ Connects:   │                │ client ↔    │                │ "my_computer"│                └─────────────┘                     ▼              ✅ Connected!```### 2. Screen Streaming Flow```Client Requests Frame:┌────────┐                ┌───────┐                ┌────────┐│ Client │──request────►  │ Relay │──forward────► │ Server ││        │  frame         │       │  to server    │        │└────────┘                └───────┘               └───┬────┘                                                      │                                                  Capture                                                   Screen                                                      │                                                 ┌────▼────┐                                                 │   MSS   │                                                 │ Capture │                                                 └────┬────┘                                                      │                                                   Resize                                                   Compress                                                      │┌────────┐                ┌───────┐                ┌─▼──────┐│ Client │◄──display────  │ Relay │◄──image─────  │ Server ││ Shows  │  on screen     │       │  JPEG base64  │        ││ Screen │                └───────┘               └────────┘└────────┘  Repeat at 10-30 fps```### 3. Mouse Control Flow```User Clicks on Client:┌────────┐│ Client │ User clicks at (400, 300) on 800x600 window│ Canvas │└───┬────┘    │ Normalize: x = 400/800 = 0.5, y = 300/600 = 0.5    │    ▼{type: "mouse",  event: "click", x: 0.5,          ◄─── Normalized (0-1 range) y: 0.5}    │    ▼┌───────┐│ Relay │ Forwards message, adds client_id│       │└───┬───┘    │    ▼{type: "mouse", event: "click", x: 0.5, y: 0.5, client_id: "client_123"}  ◄─── Added by relay    │    ▼┌────────┐│ Server │ Receives normalized coordinates│        │ Denormalize: x = 0.5 * 1920 = 960│        │              y = 0.5 * 1080 = 540└───┬────┘    │    ▼┌────────────┐│ PyAutoGUI  │ Clicks at (960, 540) on server screen│ click(960, │ ✓ Precise positioning regardless of│       540) │   screen size differences!└────────────┘```## 🌐 Network Architecture### Relay Architecture (NEW)```                    INTERNET                       │          ┌────────────┼────────────┐          │            │            │      Firewall     Firewall     Firewall          │            │            │    ┌─────▼────┐  ┌───▼────┐  ┌───▼────┐    │  Server  │  │ Replit │  │ Client │    │   (PC)   │  │ Relay  │  │ (Ctrl) │    └──────────┘  └────────┘  └────────┘         │             │            │         └─────────────┴────────────┘          All connect TO relay       No port forwarding needed!```### OLD Architecture (v1.0 - Had Problems)```    ┌────────┐      Port        ┌────────┐    │ Client │◄──Forwarding────►│ Server │    └────────┘    Required!     └────────┘                  Firewall                  Issues!```## 📦 Component Details### Relay Server (relay.py) - Runs on Replit```┌───────────────────────────────────────┐│         RELAY SERVER                  │├───────────────────────────────────────┤│                                       ││  ┌─────────────────────────────┐     ││  │  WebSocket Server           │     ││  │  Port: 8765                 │     ││  └────────┬────────────────────┘     ││           │                           ││  ┌────────▼──────────────────┐       ││  │  Server Registry          │       ││  │  "my_computer" → ws1      │       ││  │  "office_pc" → ws2        │       ││  └────────┬──────────────────┘       ││           │                           ││  ┌────────▼──────────────────┐       ││  │  Client Registry          │       ││  │  "client_1" → server_id   │       ││  │  "client_2" → server_id   │       ││  └────────┬──────────────────┘       ││           │                           ││  ┌────────▼──────────────────┐       ││  │  Message Forwarder        │       ││  │  • Route to correct dest  │       ││  │  • Add client_id          │       ││  │  • Handle disconnects     │       ││  └───────────────────────────┘       ││                                       │└───────────────────────────────────────┘```### Server (server.py) - Runs on YOUR Computer```┌───────────────────────────────────────┐│         SERVER (YOUR PC)              │├───────────────────────────────────────┤│                                       ││  ┌─────────────────────────────┐     ││  │  WebSocket Client           │     ││  │  Connects TO relay          │     ││  └────────┬────────────────────┘     ││           │                           ││  ┌────────▼──────────────────┐       ││  │  Screen Capture Thread    │       ││  │  • MSS (fast capture)     │       ││  │  • Resize & compress      │       ││  │  • Base64 encode          │       ││  └────────┬──────────────────┘       ││           │                           ││  ┌────────▼──────────────────┐       ││  │  Control Handler          │       ││  │  • PyAutoGUI              │       ││  │  • Mouse control          │       ││  │  • Keyboard control       │       ││  │  • Coordinate conversion  │       ││  └───────────────────────────┘       ││                                       │└───────────────────────────────────────┘```### Client (client.py) - Controller Device```┌───────────────────────────────────────┐│         CLIENT (CONTROLLER)           │├───────────────────────────────────────┤│                                       ││  ┌─────────────────────────────┐     ││  │  Tkinter GUI                │     ││  │  • Display canvas           │     ││  │  • Control panel            │     ││  │  • FPS adjuster             │     ││  └────────┬────────────────────┘     ││           │                           ││  ┌────────▼──────────────────┐       ││  │  WebSocket Client         │       ││  │  Connects TO relay        │       ││  │  Requests server by ID    │       ││  └────────┬──────────────────┘       ││           │                           ││  ┌────────▼──────────────────┐       ││  │  Input Handler            │       ││  │  • Capture mouse/keyboard │       ││  │  • Normalize coordinates  │       ││  │  • Send to relay          │       ││  └────────┬──────────────────┘       ││           │                           ││  ┌────────▼──────────────────┐       ││  │  Display Handler          │       ││  │  • Decode base64 images   │       ││  │  • Show on canvas         │       ││  │  • Update at FPS rate     │       ││  └───────────────────────────┘       ││                                       │└───────────────────────────────────────┘```## 🔐 Security Model```┌──────────────────────────────────────────┐│          SECURITY LAYERS                 │├──────────────────────────────────────────┤│                                          ││  Layer 1: Server ID Authentication       ││  ✅ Only clients with correct ID        ││     can connect to server               │
│                                          │
│  Layer 2: Relay Validation               │
│  ✅ Relay checks server exists          │
│     before connecting client            │
│                                          │
│  Layer 3: No Direct Exposure             │
│  ✅ Server not directly accessible      │
│     from internet                       │
│                                          │
│  ⚠️  NO Encryption (use WSS for prod)   │
│  ⚠️  NO Password (add if needed)        │
│  ✅  PyAutoGUI Failsafe enabled         │
│                                          │
└──────────────────────────────────────────┘
```

## ⚡ Performance Optimization

```
RELAY SERVER (Replit)
├── Message routing only
├── No processing/compression
├── Low CPU usage
└── Handles multiple servers

SERVER (Your PC)
├── Screen capture: MSS (fast)
├── Compression: JPEG quality 30
├── Scale: 0.5 (half resolution)
├── Configurable based on network
└── ~10-30 MB/s bandwidth

CLIENT (Controller)
├── Receive & decompress images
├── Display on canvas
├── Normalize input coordinates
├── Adjustable FPS (1-30)
└── ~5-20 MB/s bandwidth
```

## 🎯 Message Protocol

### Registration Messages

```json
// Server → Relay
{
  "type": "register_server",
  "server_id": "my_computer"
}

// Relay → Server
{
  "type": "registered",
  "server_id": "my_computer",
  "status": "success"
}

// Client → Relay
{
  "type": "register_client",
  "server_id": "my_computer"
}

// Relay → Client
{
  "type": "registered",
  "client_id": "client_123",
  "server_id": "my_computer",
  "status": "success"
}
```

### Control Messages

```json
// Client → Relay → Server (Mouse)
{
  "type": "mouse",
  "event": "click",
  "x": 0.5,
  "y": 0.5,
  "button": "left",
  "client_id": "client_123"  // Added by relay
}

// Client → Relay → Server (Frame Request)
{
  "type": "request_frame",
  "quality": 30,
  "scale": 0.5,
  "client_id": "client_123"  // Added by relay
}

// Server → Relay → Client (Screen Data)
{
  "type": "screen",
  "data": "base64_encoded_jpeg...",
  "width": 960,
  "height": 540,
  "original_width": 1920,
  "original_height": 1080,
  "target_client": "client_123"
}
```

## 🆚 Comparison: Old vs New

| Feature | v1.0 (Direct) | v2.0 (Relay) |
|---------|---------------|--------------|
| Port Forwarding | ❌ Required | ✅ Not needed |
| Firewall Issues | ❌ Common | ✅ Resolved |
| Controls What | ⚠️ Replit VM | ✅ Your PC |
| Setup Complexity | 🔴 Hard | 🟢 Easy |
| Multiple Servers | ❌ No | ✅ Yes (IDs) |
| Always Online | ❌ No | ✅ Replit relay |
| Network Config | 🔴 Complex | 🟢 Simple |

## 🌟 Key Advantages

1. **No Port Forwarding**: Server connects OUT, not listening
2. **Firewall Friendly**: All connections go TO relay
3. **Your Computer**: Control YOUR actual PC, not Replit
4. **Multiple Servers**: Different IDs for different computers
5. **Simple Setup**: Just need relay URL
6. **Always Available**: Relay runs 24/7 on Replit

---

**This relay architecture solves all the networking problems of v1.0!** 🎉
