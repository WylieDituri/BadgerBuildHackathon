# 🚗 AutoCars: Traffic Visualization Demo

> **A hackathon project showcasing Chaos vs AI-controlled traffic management**

Live demonstration of how autonomous vehicles could coordinate through a centralized "traffic brain" instead of making independent decisions.

## 🎯 The Pitch

**Problem:** Self-driving cars making independent decisions = traffic chaos and collisions

**Solution:** Centralized AI coordination that manages intersections like a traffic controller

**This Demo:** Side-by-side comparison of CHAOS (every car for itself) vs AI (coordinated queueing)

---

## ✨ Features

- **Real-time 2D visualization** with Godot engine
- **Chaos Mode:** Cars pathfind independently, collisions tracked
- **AI Mode:** Server manages intersection queue, cars wait for permission
- **Live audience interaction** via web form (spawn cars with specific routes)
- **Instant mode switching** (press TAB to toggle)
- **Rush hour simulation** (press R to spawn burst traffic)
- **WebSocket-based coordination** between visualizer and backend

---

## 🚀 Quick Start

### Backend is Already Running! ✅

Your Node.js server is live on `http://localhost:4000`

### Next: Open the Visualizer

1. **Download Godot 4.2+** from https://godotengine.org/download
2. Open Godot → **Import** → Select: `AutoCars/godot/traffic_sim/project.godot`
3. Press **F5** to run
4. Use **TAB** to toggle modes, **R** for rush hour

### Optional: Web Form

```bash
cd web
npx serve -l 3000
```

Open `http://localhost:3000` to spawn cars remotely.

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Complete setup guide with troubleshooting
- **[server/README.md](server/README.md)** - Backend API documentation
- **[web/README.md](web/README.md)** - Web form deployment guide

---

## 🏗️ Architecture

```
Web Form (audience) 
    ↓ HTTP POST
Node.js Server (traffic brain)
    ↓ WebSocket commands
Godot Visualizer (big screen)
```

**Tech Stack:**
- Godot 4.2 (game engine for visualization)
- Node.js + Express + Socket.io (backend coordination)
- Vanilla HTML/CSS/JS (audience interaction)
- WebSockets (real-time communication)
- A* pathfinding (car navigation)

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| **TAB** | Toggle CHAOS ↔ AI mode |
| **R** | Spawn rush hour burst (6 random cars) |
| **F5** | Run/restart in Godot |

---

## 🎬 Demo Flow

1. **Start in CHAOS mode** - let collisions accumulate
2. **Switch to AI mode (TAB)** - show coordinated queueing
3. **Trigger rush hour (R)** - stress test the system
4. **Show web form** - audience spawns a car live

**Total demo time:** ~3-4 minutes

---

## 📊 What Makes This a Good Hackathon Project

✅ **Visually compelling** - everyone understands traffic  
✅ **Clear comparison** - chaos vs order is obvious  
✅ **Audience participation** - people love spawning their own cars  
✅ **Technically interesting** - WebSockets, pathfinding, state management  
✅ **Realistic scope** - built in a weekend with "fake it" philosophy  

---

## 🔧 Project Structure

```
AutoCars/
├── godot/traffic_sim/       # Godot visualizer
│   ├── assets/              # Map & car sprites
│   ├── scenes/              # Main & Car scenes
│   ├── scripts/             # GDScript logic
│   └── ui/                  # HUD overlay
├── server/                  # Node.js backend
│   ├── src/index.js         # Main server logic
│   └── package.json
├── web/                     # Static web form
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── QUICKSTART.md            # Setup guide
├── check_setup.sh           # Health check script
└── README.md                # This file
```

---

## 🐛 Common Issues

**Server not starting?**
```bash
cd server && npm install && npm run dev
```

**Godot can't connect?**
- Check `scripts/Network.gd` has `ws://localhost:4000/ws`
- Verify server is running: `curl localhost:4000/health`

**Cars not moving?**
- Make sure you're running Main.tscn (not Car.tscn)
- Check Godot console for errors

---

## 🎓 Built With the Hackathon Philosophy

> **"You are not building a realistic traffic simulator; you are building a compelling visualizer for your idea."**

We didn't build:
- ❌ Realistic physics
- ❌ Complex AI algorithms
- ❌ Multi-intersection coordination
- ❌ Scalable distributed systems

We DID build:
- ✅ A clear visual comparison
- ✅ Simple queue-based coordination
- ✅ Audience engagement
- ✅ A story people understand

---

## 🏆 Presentation Tips

1. **Lead with the problem** - "Self-driving cars all making independent decisions"
2. **Show chaos first** - let collisions happen, build tension
3. **Reveal the solution** - TAB to AI mode, smooth coordination
4. **Let audience participate** - web form demo
5. **End with impact** - "This is how autonomous vehicles could actually work"

---

## 📝 License

MIT - Built for BadgerBuild Hackathon

---

## 🙏 Acknowledgments

Inspired by the "Fake It 'Til You Make It" hackathon philosophy - focus on the compelling story, not perfect engineering.

---

**Ready to demo?** Run `./check_setup.sh` to verify everything is working! 🚦

