# 🏁 Race Mode Guide

A competitive racing system where users race from different starting points to a common destination. Admin controls the race, players see only their limited view, and crashes eliminate players.

## Quick Start

### 1. Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### 2. Open Admin Panel (Race Control)

Open in browser:

```
web/admin_race.html
```

Or with a local server:

```bash
cd web
python3 -m http.server 3000
# Then go to: http://localhost:3000/admin_race.html
```

### 3. Open Player Interface (For Racers)

Open in browser:

```
web/race.html
```

Or:

```
http://localhost:3000/race.html
```

## How to Run a Race

### Admin Steps:

1. **Create Race**

   - Enter race name (e.g., "Campus Sprint")
   - Select destination point
   - Click "Create Race"

2. **Wait for Players**

   - Players join and select starting points
   - Watch player count increase
   - All players see "Waiting" status

3. **Start Race**

   - Click "Start Race 🚦"
   - Race begins immediately
   - All players can now drive

4. **Watch Live**

   - Leaderboard updates in real-time
   - See racing/finished/crashed counts
   - Track individual player times

5. **End Race** (Optional)
   - Click "End Race" to force-finish
   - Or let it run until all players finish/crash

### Player Steps:

1. **Join**

   - Enter your name
   - Select starting point (North/South/East/West Campus)
   - Click "Join Race"

2. **Wait for Start**

   - See "Waiting" status
   - Admin must start the race

3. **Race!**

   - Use arrow keys to drive:
     - 🔼 Forward
     - 🔽 Reverse (brake)
     - ◀️ Turn Left
     - ▶️ Turn Right
   - Green arrow points to destination
   - Watch your distance decrease

4. **Results**
   - **Finish**: See your time and rank
   - **Crash**: Eliminated (collision with another player)

## Features

### Admin Panel

- ✅ Create and control races
- ✅ Live leaderboard with rankings
- ✅ Real-time stats (racing/finished/crashed)
- ✅ Individual player tracking
- ✅ Time and distance metrics

### Player Interface

- ✅ **Limited view** - only see your car and destination
- ✅ Simple driving controls (arrow keys)
- ✅ Real-time HUD (speed, time, distance)
- ✅ Direction indicator to destination
- ✅ Automatic crash detection
- ✅ Final stats display

### Race System

- ✅ Multiple starting points
- ✅ Common destination
- ✅ Crash detection (3m collision radius)
- ✅ Real-time position tracking
- ✅ Finish line detection (20m radius)
- ✅ Automatic timing
- ✅ Ranking system

## API Endpoints

### Admin

- `POST /api/v2/race/admin/race/create` - Create race
- `POST /api/v2/race/admin/race/{race_id}/start` - Start race
- `POST /api/v2/race/admin/race/{race_id}/end` - End race
- `GET /api/v2/race/admin/race/{race_id}/status` - Get full status
- `GET /api/v2/race/admin/race/active` - Get active race

### Players

- `POST /api/v2/race/player/register` - Join race
- `POST /api/v2/race/player/position` - Update position
- `GET /api/v2/race/player/{player_id}/stats` - Get your stats
- `GET /api/v2/race/player/{player_id}/race` - Get race info (limited)

## Configuration

### Race Settings (in `race_manager.py`)

```python
max_players: int = 20  # Maximum players per race
crash_detection_enabled: bool = True  # Enable/disable crashes
collision_radius_meters: float = 3.0  # Crash distance
destination_radius_meters: float = 20.0  # Finish line size
```

### Campus Coordinates

- **North Campus**: (43.078, -89.401)
- **South Campus**: (43.068, -89.401)
- **East Campus**: (43.073, -89.396)
- **West Campus**: (43.073, -89.406)

## Tips for Demo

1. **Test with 2-3 friends** before the hackathon presentation
2. **Project admin panel** on screen for audience
3. **Give players phones/laptops** with race.html open
4. **Create dramatic destinations** (opposite ends of campus)
5. **Narrate the race** as admin watching the leaderboard
6. **Celebrate finishers and crashes** - it's entertaining!

## Troubleshooting

**"No active race"**

- Admin must create a race first
- Check backend is running

**"Failed to join race"**

- Race may be full (max 20 players)
- Race may have already started
- Check starting point selection

**Players not moving**

- Make sure race is started (admin panel)
- Check arrow keys are working
- Verify backend connection

**Crashes not detected**

- Players must be within 3 meters
- Check `crash_detection_enabled` setting

## Architecture

```
┌─────────────────┐
│  Admin Panel    │ ← Controls race, sees all
│  (admin_race)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Race Manager   │ ← Backend service
│  (FastAPI)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Player View    │ ← Limited view, drives
│  (race.html)    │
└─────────────────┘
```

Race data is stored **in-memory** on the backend. Perfect for live demos, but resets on server restart.

## Next Steps

Want to enhance it? Ideas:

- Add countdown timer (3, 2, 1, GO!)
- Power-ups on the map
- Multiple laps/checkpoints
- Team races
- Replay system
- Photo finish camera
- Speed traps/zones
- Weather effects

Have fun racing! 🏁🚗💨
