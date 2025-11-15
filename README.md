# BadgerBuildHackathon - Centralized Car Intelligence Demo

A full-stack real-time multi-car coordination system with centralized path planning.

## 🚀 Quick Start

### Frontend (Next.js)
```bash
cd frontend
npm run dev
```
Open http://localhost:3000

### Backend (FastAPI)
```bash
cd backend
python3 -m uvicorn app.main:app --reload --port 8000
```
API docs at http://localhost:8000/docs

## 📁 Project Structure

- **`/frontend`** - Next.js 14 app with TypeScript & Tailwind CSS
  - `/app/page.tsx` - Main map view with real-time car tracking
  - `/app/mobile/page.tsx` - Mobile driver interface (use arrow keys)
  - `/app/admin/page.tsx` - Admin dashboard with planner control
  - `/components` - React components (MapDisplay, MobileDriver, AdminDashboard, QRCode)
  - `/lib/firebase.ts` - Firebase client SDK setup

- **`/backend`** - FastAPI Python backend
  - `/app/main.py` - FastAPI app with CORS and routes
  - `/app/api/v1/endpoints.py` - Planning API endpoints
  - `/app/services/agent.py` - Multi-step planning agent
  - `/app/services/firebase_admin.py` - Firebase Admin SDK
  - `/app/models/schemas.py` - Pydantic data models

## ✨ Features

1. **Map View** (Desktop) - Real-time visualization of all cars on a shared map
2. **Mobile Driver** - Join via QR code, move your car with arrow keys
3. **Admin Dashboard** - Run centralized planner to coordinate multiple cars
4. **Firebase Integration** - Real-time sync via Firestore
5. **Planning Agent** - Multi-step path planning with conflict resolution (scaffolded)

## 🔧 Setup

### Prerequisites
- Node.js 18+
- Python 3.10+
- Firebase project with Firestore enabled

### Frontend Setup
```bash
cd frontend
npm install
# Update .env.local with your Firebase config
npm run dev
```

### Backend Setup
```bash
cd backend
pip3 install -r requirements.txt
# Update .env with your Firebase Admin SDK credentials
python3 -m uvicorn app.main:app --reload --port 8000
```

## 🎮 How to Use

1. **Start both servers** (frontend on :3000, backend on :8000)
2. **Open the map view** at http://localhost:3000
3. **Scan QR code** with your phone to join as a mobile driver
4. **Select start node** and click "Start Driving"
5. **Use arrow keys** to move your car - it appears on the map in real-time!
6. **Open admin dashboard** at http://localhost:3000/admin
7. **Click "Run Planner"** to generate coordinated paths for all cars

## 🗃️ Firestore Data Model

Collection: `/artifacts/{appId}/public/cars/{userId}`

```json
{
  "start": "Alpha",
  "end": "Charlie", 
  "x": 120,
  "y": 450,
  "last_updated": "2025-11-15T15:51:00Z",
  "path": [{"x": 120, "y": 450}, {"x": 130, "y": 440}],
  "plan_id": "uuid",
  "status": "planned"
}
```

## 🔌 API Endpoints

### `POST /api/v1/run-plan`
Run the centralized planner for all active cars.

**Request:**
```json
{
  "cars": [{
    "id": "user-id",
    "start_node": "Alpha",
    "end_node": "Charlie",
    "current_pos": [120, 450]
  }]
}
```

**Response:**
```json
{
  "plan_id": "uuid",
  "paths": [{
    "car_id": "user-id",
    "path": [[120, 450], [130, 440]],
    "status": "planned"
  }]
}
```

## 🚧 Future Enhancements

- [ ] Implement Dijkstra's or A* pathfinding
- [ ] Add conflict detection between car paths
- [ ] Implement conflict resolution strategies
- [ ] Visualize planned paths on the map
- [ ] Add WebSocket broadcasting for live updates
- [ ] Deploy to production (Vercel + Cloud Run)

## 📝 License

MIT