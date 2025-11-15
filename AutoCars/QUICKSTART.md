# Traffic Visualizer Quickstart Guide

## 🚀 What You've Built

A hackathon-ready traffic visualization system with:
- **Godot visualizer** with chaos vs AI modes
- **Node.js backend** that acts as traffic control
- **Web spawn form** for audience interaction

---

## ✅ Backend Server (RUNNING)

Your Node.js server is **already running** on `http://localhost:4000`

**Status Check:**
```bash
curl http://localhost:4000/health
# Should return: {"status":"ok","mode":"CHAOS","activeCars":0}
```

**What it does:**
- Manages intersection queues (AI mode)
- Broadcasts STOP/GO commands to cars
- Accepts spawn requests from the web form
- Tracks collisions and stats

**If you need to restart it:**
```bash
cd AutoCars/server
npm run dev
```

---

## 🎮 Godot Visualizer (NEXT STEP)

### Opening the Project

1. **Download Godot 4.2+** from https://godotengine.org/download if you don't have it
2. **Open Godot** and click "Import"
3. **Navigate to:** `AutoCars/godot/traffic_sim/project.godot`
4. Click "Import & Edit"

### Running the Demo

1. Press **F5** (or click the Play button) to run the scene
2. You should see:
   - A dark map with yellow road lines
   - Cars (colored sprites) spawning automatically
   - HUD showing Mode, Timer, Collisions, Active Cars

### Controls

- **TAB** = Toggle between CHAOS and AI modes
  - **CHAOS**: Cars pathfind independently (collisions happen!)
  - **AI**: Server controls the center intersection (CC) - cars queue and wait for permission
  
- **R** = Rush Hour Burst (spawns 6 random cars instantly)

### What to Watch For

**CHAOS Mode:**
- Cars move freely
- Collisions happen at intersections
- Counter increments when cars crash

**AI Mode:**
- Cars slow down near the center intersection
- Server manages queue (first-come-first-served)
- Fewer/no collisions at CC intersection

---

## 🌐 Web Form (Audience Interaction)

### Running Locally

```bash
cd AutoCars/web
npx serve -l 3000
```

Then open: `http://localhost:3000`

### What it does

1. Select **Start Intersection** (e.g., NW = North West)
2. Select **Destination** (e.g., SE = South East)
3. Choose **Mode** (Chaos or AI)
4. Click **Launch Vehicle**

The request goes to your Node server, which broadcasts it to all connected Godot clients.

### For Your Demo

**Deploy to Glitch/Replit:**

1. Go to https://glitch.com (or https://replit.com)
2. Create a new static HTML project
3. Upload these 3 files:
   - `AutoCars/web/index.html`
   - `AutoCars/web/styles.css`
   - `AutoCars/web/app.js`
4. Update the **Server URL** field in the form to point to your deployed backend (or use ngrok for localhost)
5. Generate a QR code pointing to your Glitch URL

**Audience Flow:**
- Scan QR code → Select route → Press button → Car appears on big screen!

---

## 🎯 Demo Script (Presentation)

### Opening (30 seconds)

> "Imagine a city where cars talk to each other. We built a live demo comparing chaos vs AI-controlled traffic."

### Part 1: Chaos Mode (1 minute)

1. Show Godot running in CHAOS mode
2. Let cars spawn for 10-15 seconds
3. Point out collision counter climbing
4. **Key line:** "Every car is making its own decisions. No coordination. See the crashes?"

### Part 2: AI Mode (1 minute)

1. Press **TAB** to switch to AI
2. Press **R** for rush hour burst
3. Watch cars queue at center intersection
4. Point to HUD: "Mode: AI" - "Active Cars: 10+" - "Collisions: same number"
5. **Key line:** "Now the server is the traffic cop. Cars ask permission. Watch—they wait, then go one by one."

### Part 3: Audience Interaction (1 minute)

1. Show the web form on your phone/laptop
2. Pick NW → SE, AI mode, hit Launch
3. **Live on screen:** A new car spawns and follows that exact route
4. **Key line:** "Anyone can spawn a car. This is how autonomous vehicles could coordinate in real-time."

### Closing (30 seconds)

> "This whole system—visualizer, backend, web form—was built in a weekend. It's not perfect, but it shows the core idea: centralized coordination beats chaos. Thanks!"

---

## 🔧 Architecture Overview

```
┌──────────────────┐
│  Web Form        │  (Audience phone/laptop)
│  localhost:3000  │
└────────┬─────────┘
         │ POST /spawn
         ▼
┌──────────────────┐
│  Node Server     │  (Traffic brain)
│  localhost:4000  │
│  - Socket.io     │
│  - WebSocket /ws │
└────────┬─────────┘
         │ commands (STOP/GO)
         │ spawn:request
         ▼
┌──────────────────┐
│  Godot Client    │  (Visualizer on big screen)
│  - Connects via  │
│    ws://...4000  │
│  - A* pathfinding│
│  - Collision det.│
└──────────────────┘
```

---

## 🐛 Troubleshooting

### "Failed to connect to server"
- Check backend is running: `curl localhost:4000/health`
- Restart backend: `cd AutoCars/server && npm run dev`

### Cars not spawning in Godot
- Make sure `Network.gd` server_url is `ws://localhost:4000/ws`
- Check Godot console for errors (Output panel at bottom)

### Web form says "Failed: 404"
- Server URL field must be `http://localhost:4000` (no trailing slash)
- CORS is enabled, so any origin should work

### Collisions still happen in AI mode
- AI mode only controls the **CENTER (CC)** intersection
- Cars can still collide at other 8 intersections
- This is intentional to show the difference

---

## 📦 What's Included

```
AutoCars/
├── godot/traffic_sim/       # Godot 4.2 project
│   ├── assets/
│   │   ├── map.svg          # Road background
│   │   └── car.svg          # Car sprite
│   ├── scenes/
│   │   ├── Main.tscn        # Main scene
│   │   └── Car.tscn         # Reusable car
│   ├── scripts/
│   │   ├── Main.gd          # Graph, spawning, mode logic
│   │   ├── Car.gd           # Movement, collision
│   │   ├── Spawner.gd       # Car instantiation
│   │   ├── Network.gd       # WebSocket client
│   │   └── HUD.gd           # UI updates
│   └── ui/
│       └── HUD.tscn         # HUD scene
├── server/                   # Node.js backend
│   ├── src/index.js         # Socket.io + Express
│   ├── package.json
│   └── README.md
└── web/                      # Static HTML form
    ├── index.html
    ├── styles.css
    ├── app.js
    └── README.md
```

---

## 🎓 Hackathon Tips

1. **Practice the demo** 3-4 times before presenting
2. **Have a backup video** in case WiFi/projection fails
3. **Emphasize the "fake it" philosophy**: "We didn't build real traffic simulation—we built a compelling story"
4. **Mention the tech stack**: Godot, Node.js, Socket.io, WebSockets, A* pathfinding
5. **Show the code briefly** if judges ask—Main.gd is clean and readable

---

## 🚦 Good Luck!

You've got:
- ✅ Backend running
- ✅ Godot project ready to open
- ✅ Web form ready to deploy
- ✅ All code written
- ✅ Demo script prepared

**All that's left:** Open Godot, press F5, and tell your story! 🎉

