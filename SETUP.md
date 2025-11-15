# 🚀 Quick Setup Guide

## ✅ Firebase Removed - Using In-Memory Storage!

**No Firebase account needed!** All data is stored in backend memory. Perfect for hackathon demos.

---

## 🔧 Backend Setup (Python)

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**If you get `pydantic-settings` error:**

```bash
pip install pydantic-settings
```

### 2. Run Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Expected output:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## 🌐 Frontend Setup (Next.js)

### 1. Install Dependencies (if needed)

```bash
cd frontend
npm install
```

### 2. Run Frontend

```bash
cd frontend
npm run dev
```

**Expected output:**

```
✓ Ready in 1852ms
- Local: http://localhost:3000 (or 3001 if 3000 is busy)
```

---

## ✅ Verify Everything Works

### Test Backend:

```bash
curl http://localhost:8000/health
```

**Expected:**

```json
{
  "status": "healthy",
  "service": "car-intelligence-backend",
  "storage": "memory"
}
```

### Test Frontend:

Open http://localhost:3000 (or 3001) in your browser.

---

## 🎯 What Changed

### ✅ Removed Firebase

- No API keys needed
- No Firebase account required
- No environment variables for Firebase

### ✅ Added In-Memory Storage

- Data stored in backend memory
- Fast and simple for demos
- Perfect for hackathon presentations

### ✅ Updated Components

- `MapDisplay` now polls backend API
- No Firebase Firestore listeners
- Works with simple HTTP requests

---

## 🐛 Troubleshooting

### Backend: `ModuleNotFoundError: No module named 'pydantic_settings'`

**Fix:**

```bash
cd backend
pip install pydantic-settings
```

### Frontend: `FirebaseError: auth/invalid-api-key`

**Fixed!** Firebase is removed. If you still see this:

1. Restart the frontend dev server
2. Clear browser cache
3. Check that `lib/firebase.ts` doesn't try to initialize Firebase

### Port Already in Use

**Backend (8000):**

```bash
lsof -ti:8000 | xargs kill -9
```

**Frontend (3000):**

```bash
lsof -ti:3000 | xargs kill -9
```

---

## 📊 Architecture

```
Frontend (Next.js)
    ↓ HTTP Polling (every 500ms)
Backend (FastAPI)
    ↓ In-Memory Storage
MemoryStore (Python dict)
```

**Data Flow:**

1. User submits car request → Frontend → Backend API
2. Backend stores in memory → Returns response
3. Frontend polls `/api/v1/cars` → Displays cars on map

---

## 🎤 For Your Demo

**Advantages of In-Memory Storage:**

- ✅ No setup required
- ✅ Works immediately
- ✅ No external dependencies
- ✅ Fast for demos
- ✅ Easy to explain to judges

**Trade-offs:**

- ⚠️ Data lost on server restart (fine for demo!)
- ⚠️ Not persistent (but you don't need it for a demo)

---

## 🚀 Ready to Demo!

1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Open browser: http://localhost:3000
4. Submit car requests and watch them appear!

**No Firebase needed!** 🎉
