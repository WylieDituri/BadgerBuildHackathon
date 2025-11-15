# BadgerBuild Hackathon - AutoCars Project

## 🚦 Traffic Visualization: Chaos vs AI

A live demonstration comparing independent autonomous vehicles (chaos) versus centrally-coordinated traffic management (AI).

---

## 🚀 **READY TO DEMO** ✅

Your backend server is **currently running** on `http://localhost:4000`

### Next Step: Open the Visualizer

1. Download **Godot 4.2+** from https://godotengine.org/download
2. Open Godot → **Import** → `AutoCars/godot/traffic_sim/project.godot`
3. Press **F5** to run
4. Use **TAB** to toggle modes, **R** for rush hour

---

## 📁 Project Structure

```
AutoCars/
├── 📖 QUICKSTART.md           ← START HERE: Complete setup guide
├── 📖 README.md                ← Project overview
├── 📖 DEMO_SCRIPT.md           ← Your presentation script (3-4 min)
├── 📖 TESTING_CHECKLIST.md    ← Pre-demo testing steps
├── 🔧 check_setup.sh          ← Health check script
│
├── godot/traffic_sim/         ← Godot visualizer (2D game)
├── server/                    ← Node.js backend (traffic brain)
└── web/                       ← HTML form (audience interaction)
```

---

## 📚 Documentation Quick Links

| Document                                                  | Purpose                                    | When to Read       |
| --------------------------------------------------------- | ------------------------------------------ | ------------------ |
| **[QUICKSTART.md](AutoCars/QUICKSTART.md)**               | Setup guide, troubleshooting, architecture | First time setup   |
| **[DEMO_SCRIPT.md](AutoCars/DEMO_SCRIPT.md)**             | Word-for-word presentation script          | Before presenting  |
| **[TESTING_CHECKLIST.md](AutoCars/TESTING_CHECKLIST.md)** | Pre-demo testing steps                     | 30 min before demo |
| **[AutoCars/README.md](AutoCars/README.md)**              | Technical overview, features               | For judges/README  |

---

## ⚡ Quick Commands

### Check if everything is working

```bash
cd AutoCars
./check_setup.sh
```

### Start backend (already running for you)

```bash
cd AutoCars/server
npm run dev
```

### Start web form (optional)

```bash
cd AutoCars/web
npx serve -l 3000
```

### Test backend health

```bash
curl http://localhost:4000/health
```

---

## 🎮 Demo Controls

| Key     | Action                   |
| ------- | ------------------------ |
| **F5**  | Run Godot scene          |
| **TAB** | Toggle CHAOS ↔ AI mode   |
| **R**   | Rush hour burst (6 cars) |

---

## 🎯 The Story (30-second version)

> "Self-driving cars making independent decisions = chaos and collisions. But what if they could coordinate? We built a live demo comparing both approaches. Watch: [press TAB] The difference is immediate."

---

## ✨ What Makes This Project Stand Out

1. **Visually compelling** - Real-time animation, clear before/after
2. **Audience participation** - Web form lets judges spawn cars
3. **Technically solid** - WebSockets, A\* pathfinding, state management
4. **Realistic scope** - Built in a weekend using "fake it" philosophy
5. **Strong narrative** - Everyone understands traffic

---

## 🏗️ Tech Stack

- **Frontend:** Godot 4.2 (game engine)
- **Backend:** Node.js + Express + Socket.io + WebSockets
- **Communication:** Real-time bidirectional WebSocket protocol
- **Pathfinding:** A\* algorithm (built into Godot)
- **Web UI:** Vanilla HTML/CSS/JavaScript

---

## 📊 System Status

Run this anytime to check health:

```bash
cd AutoCars && ./check_setup.sh
```

Expected output:

```
✅ Node.js installed: v20.x.x
✅ Server is running on port 4000
✅ Godot project found at: godot/traffic_sim/
✅ Web form files found
```

---

## 🐛 Quick Troubleshooting

**Problem: Server not responding**

```bash
cd AutoCars/server && npm run dev
```

**Problem: Godot won't connect**

- Check `godot/traffic_sim/scripts/Network.gd` line 3
- Should be: `ws://localhost:4000/ws`

**Problem: Cars not spawning**

- Make sure you're running `Main.tscn` (not Car.tscn)
- Check Godot console (Output panel) for errors

**Problem: Collisions still happen in AI mode**

- Expected! AI only controls the CENTER intersection
- Other 8 intersections remain unmanaged

---

## 🎬 Demo Day Prep (15-minute checklist)

1. ✅ Backend running (already done!)
2. ⏳ Open Godot project
3. ⏳ Press F5, verify cars spawn
4. ⏳ Test TAB toggle (CHAOS ↔ AI)
5. ⏳ Test R key (rush hour)
6. ⏳ (Optional) Serve web form on phone
7. ⏳ Practice presentation 2-3 times

**Total prep time:** ~15 minutes  
**Demo time:** 3-4 minutes

---

## 📖 Full Documentation

- **Setup:** [QUICKSTART.md](AutoCars/QUICKSTART.md)
- **Presentation:** [DEMO_SCRIPT.md](AutoCars/DEMO_SCRIPT.md)
- **Testing:** [TESTING_CHECKLIST.md](AutoCars/TESTING_CHECKLIST.md)
- **Technical:** [AutoCars/README.md](AutoCars/README.md)

---

## 🎓 Hackathon Philosophy

This project follows the "Fake It 'Til You Make It" approach:

> "You are not building a realistic traffic simulator; you are building a compelling visualizer for your idea."

**What we built:**

- ✅ Clear visual comparison
- ✅ Simple queue-based coordination
- ✅ Engaging narrative

**What we skipped:**

- ❌ Realistic physics
- ❌ Complex multi-intersection AI
- ❌ Production-scale architecture

**Result:** A compelling demo that tells a powerful story in 3 minutes.

---

## 🏆 You're Ready!

Everything is set up and running. Just:

1. Open Godot
2. Press F5
3. Follow your demo script
4. Show the judges something cool!

**Good luck at BadgerBuild!** 🚗✨

---

_Built with Godot, Node.js, Socket.io, and weekend hustle._
