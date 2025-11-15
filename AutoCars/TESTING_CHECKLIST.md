# ✅ Testing Checklist - Before Demo Day

Run through this checklist **at least once** before your presentation to catch any issues.

---

## 🔧 Pre-Flight Check

### Backend Server

```bash
cd AutoCars
./check_setup.sh
```

Expected output:
- ✅ Node.js installed
- ✅ Server running on port 4000
- ✅ Health endpoint returns `{"status":"ok","mode":"CHAOS","activeCars":0}`

**If fails:** 
```bash
cd server
npm install
npm run dev
```

### Godot Project

- [ ] Godot 4.2+ installed
- [ ] Project opens without errors
- [ ] All scenes load (Main.tscn, Car.tscn, HUD.tscn)
- [ ] No missing resource warnings

**If fails:** Re-import project, check file paths

---

## 🎮 Godot Visualizer Tests

### Test 1: Basic Spawning (CHAOS Mode)

1. Press **F5** to run Main.tscn
2. Watch for 10 seconds

**Expected:**
- [ ] Cars spawn every 3 seconds
- [ ] Cars move from start to destination
- [ ] Map is visible (dark background, yellow roads)
- [ ] HUD shows "Mode: CHAOS"
- [ ] Timer counts up
- [ ] Active cars counter updates

**If fails:**
- Check Spawner has `car_scene` assigned to Car.tscn
- Check Main script is attached to root node
- Check console for errors (Output panel at bottom)

### Test 2: Collision Detection (CHAOS Mode)

1. Let 8-10 cars spawn
2. Watch center intersection

**Expected:**
- [ ] Collision counter increments when cars overlap
- [ ] Colliding cars disappear
- [ ] Active cars count decreases

**If fails:**
- Check Car.gd has `check_overlap()` method
- Check Main.gd `_check_collisions()` is being called
- Verify collision radius in Car.gd

### Test 3: Mode Toggle

1. Press **TAB**

**Expected:**
- [ ] HUD updates to "Mode: AI"
- [ ] Console shows "[Network] Remote mode: AI" (if server connected)
- [ ] Cars near center intersection slow down
- [ ] No crashes (mode switched, TAB goes back to CHAOS)

**Press TAB again:**
- [ ] Returns to "Mode: CHAOS"
- [ ] Cars resume normal speed

### Test 4: Rush Hour Burst

1. Press **R**

**Expected:**
- [ ] 6 cars spawn instantly
- [ ] Active cars counter jumps +6
- [ ] All cars pathfind independently
- [ ] Console shows "Rush hour burst deployed" hint

### Test 5: Network Connection

Check Godot console (Output panel):

**Expected:**
- [ ] Sees "Failed to connect" warnings initially (normal if server just started)
- [ ] Eventually connects silently (no error after reconnect)

**To force test:**
1. Restart backend: `cd server && npm run dev`
2. In Godot console, should see reconnection attempt
3. No red errors after 2-3 seconds

---

## 🌐 Backend Server Tests

### Test 1: Health Endpoint

```bash
curl http://localhost:4000/health
```

**Expected:**
```json
{"status":"ok","mode":"CHAOS","activeCars":0}
```

### Test 2: Spawn Endpoint

```bash
curl -X POST http://localhost:4000/spawn \
  -H "Content-Type: application/json" \
  -d '{"start":"NW","end":"SE","mode":"AI"}'
```

**Expected:**
```json
{
  "status":"queued",
  "payload":{
    "requestId":"<uuid>",
    "start":"NW",
    "end":"SE",
    "mode":"AI"
  }
}
```

**In Godot (if running):**
- [ ] A new car spawns immediately at NW
- [ ] Car pathfinds to SE
- [ ] Mode switches to AI

### Test 3: WebSocket Connection

Check server console:

**Expected:**
```
Traffic brain running on port 4000
[socket.io] connected <socket-id>
```

**When Godot connects:**
- Should see WebSocket connection established (no explicit log, but no errors)

### Test 4: Mode Sync

With Godot running:
1. Press **TAB** in Godot
2. Check server console

**Expected:**
- Server receives mode change event
- `currentMode` updates to "AI" or "CHAOS"
- Stats broadcast to all clients

---

## 🌐 Web Form Tests

### Test 1: Serve Locally

```bash
cd AutoCars/web
npx serve -l 3000
```

**Expected:**
- [ ] Server starts on http://localhost:3000
- [ ] Page loads without errors
- [ ] Form is visible and styled

### Test 2: Form Interaction

1. Open http://localhost:3000
2. Change "Server URL" to `http://localhost:4000`
3. Select start: NW
4. Select end: SE
5. Select mode: AI
6. Click "Launch Vehicle"

**Expected:**
- [ ] Status shows "Sending request…"
- [ ] Status updates to "Queued request <uuid>"
- [ ] No errors in browser console (F12)

**In Godot (if running):**
- [ ] Car spawns at NW
- [ ] Car travels to SE

### Test 3: Error Handling

1. Change "Server URL" to `http://localhost:9999` (wrong port)
2. Click "Launch Vehicle"

**Expected:**
- [ ] Status shows "Failed: fetch failed" or similar
- [ ] No crash, form remains usable

### Test 4: CORS

1. Serve from a different port: `npx serve -l 8080`
2. Try spawning a car

**Expected:**
- [ ] Still works (CORS is enabled on backend)
- [ ] No CORS errors in console

---

## 🔄 Integration Tests

### Test 1: End-to-End Flow (The Full Demo)

1. Start backend: `cd server && npm run dev`
2. Start Godot: Press F5
3. Start web form: `cd web && npx serve -l 3000`
4. Let system run for 30 seconds

**Expected:**
- [ ] Backend shows 0 errors
- [ ] Godot spawns cars automatically
- [ ] Web form connects successfully
- [ ] Submit car via web form → appears in Godot

### Test 2: Mode Switching During Traffic

1. Let 10 cars spawn in CHAOS
2. Press TAB to AI
3. Press R for rush hour
4. Watch collisions stop at center intersection

**Expected:**
- [ ] Mode switch is instant
- [ ] Existing cars adapt to new mode
- [ ] No crashes or hangs
- [ ] Collision counter doesn't spike in AI mode

### Test 3: Stress Test

1. Press R 5 times rapidly (30 cars)
2. Watch performance

**Expected:**
- [ ] Godot maintains 60 FPS (check top-right corner)
- [ ] Backend handles load (check server CPU)
- [ ] No memory leaks (cars clean up when reaching destination)

**If fails:**
- Reduce spawn_interval in Spawner.gd
- Limit max active cars

---

## 📱 Mobile Web Form Test (Optional)

### Test 1: Phone Access

1. Find your computer's local IP: `ipconfig getifaddr en0` (Mac) or `ipconfig` (Windows)
2. Update web form "Server URL" to: `http://<your-ip>:4000`
3. Open on phone: `http://<your-ip>:3000`
4. Submit a spawn request

**Expected:**
- [ ] Form loads on phone
- [ ] Car spawns in Godot on laptop screen
- [ ] Latency < 2 seconds

### Test 2: QR Code

1. Generate QR code for `http://<your-ip>:3000`
2. Scan with phone camera
3. Use form

**Expected:**
- [ ] QR opens form directly
- [ ] Works same as typing URL

---

## 🎬 Presentation Dry Run

### Test 1: Full Demo (3 minutes)

1. Start with Godot in CHAOS, 5 cars already moving
2. Speak opening line
3. Point to collisions
4. Press TAB
5. Press R
6. Show web form on phone
7. Submit spawn
8. Close with one-liner

**Time yourself. Aim for 2:30-3:30.**

### Test 2: Backup Video

**Recommended:** Record a clean run as backup

```bash
# macOS screen recording
# Cmd+Shift+5 → Record portion → Start

# Or use OBS Studio
```

- [ ] Record 90-second silent demo
- [ ] Shows CHAOS → AI → Rush Hour → Web spawn
- [ ] Have this ready in case live demo fails

---

## 🐛 Known Issues & Workarounds

### Issue: Godot "Failed to connect to server"

**Cause:** Backend not running or wrong URL

**Fix:**
1. Check `scripts/Network.gd` line 3: `ws://localhost:4000/ws`
2. Verify backend: `curl localhost:4000/health`
3. Restart Godot scene

### Issue: Cars spawn but don't move

**Cause:** Pathfinding returned empty path

**Fix:**
1. Check start/end nodes are valid
2. Verify `_build_graph()` in Main.gd ran
3. Check console for A* errors

### Issue: Web form "404 Not Found"

**Cause:** Backend not running or wrong URL

**Fix:**
1. Ensure backend is running: `curl localhost:4000/health`
2. Check "Server URL" field matches backend address
3. Try `http://localhost:4000` (no trailing slash)

### Issue: Collisions still happen in AI mode

**Expected behavior!**

- AI mode **only controls CENTER (CC)** intersection
- Other 8 intersections remain unmanaged
- This is intentional to show the difference

### Issue: Lag/stuttering with 20+ cars

**Cause:** Too many active game objects

**Workaround:**
1. Reduce `spawn_interval` to 5.0 in Spawner.gd
2. Don't spam R key
3. This is fine for demo (won't hit 20+ in 3 minutes)

---

## ✅ Final Checklist (5 minutes before demo)

- [ ] Backend running (`./check_setup.sh` passes)
- [ ] Godot open, Main scene loaded (not running yet)
- [ ] Web form loaded on phone (optional)
- [ ] Laptop plugged in (not on battery)
- [ ] Volume muted (no notification sounds)
- [ ] Close other apps (clean screen)
- [ ] Backup video ready (just in case)
- [ ] Deep breath, you've got this! 🚀

---

## 🎯 Success Criteria

Your system is demo-ready if:
- ✅ CHAOS mode shows visible collisions
- ✅ AI mode shows coordinated queueing
- ✅ TAB toggles modes instantly
- ✅ R spawns burst traffic
- ✅ Web form spawns cars in Godot
- ✅ No red errors in any console

If **any** component fails, you can still demo the working parts. The Godot visualizer alone (CHAOS ↔ AI toggle) is enough to tell the story!

---

**Ready?** Run through this list once, fix any issues, then practice your presentation 2-3 times. You've got this! 🏆

