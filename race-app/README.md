# 🏁 Carmonic Racing - Next.js App

A real-time multiplayer racing game built with Next.js and FastAPI, showcasing AI-powered traffic coordination.

## 🚀 Quick Start (Local Development)

### 1. Start the Backend

```bash
cd ../backend
uvicorn app.main:app --reload
```

Backend runs on `http://localhost:8000`

### 2. Start the Frontend

```bash
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

### 3. Open in Browser

- **Home**: http://localhost:3000
- **Play**: http://localhost:3000/race
- **Admin**: http://localhost:3000/admin

## 📦 Deploying to Vercel

### Step 1: Deploy Backend

The FastAPI backend needs to be deployed separately. Options:

#### Option A: Railway (Recommended)
1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your backend folder
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Copy your deployment URL (e.g., `https://your-app.railway.app`)

#### Option B: Render
1. Go to https://render.com
2. New → Web Service
3. Connect your repo
4. Root directory: `backend`
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. Copy your deployment URL

### Step 2: Deploy Frontend to Vercel

1. Push your code to GitHub

2. Go to https://vercel.com

3. Click "New Project"

4. Import your GitHub repository

5. **Configure Project**:
   - Framework: Next.js
   - Root Directory: `race-app`
   - Build Command: `npm run build` (default)
   - Output Directory: `.next` (default)

6. **Add Environment Variable**:
   - Key: `NEXT_PUBLIC_API_BASE_URL`
   - Value: `https://your-backend-url.railway.app/api/v2`
   - (Replace with your actual backend URL from Step 1)

7. Click "Deploy"

### Step 3: Share Your App!

After deployment, Vercel gives you a URL like:
- `https://your-app.vercel.app`

Share this link! Players can:
- Go to `/race` to play
- Admin can go to `/admin` to control

## 🎮 How to Use

### For Admin:
1. Open `/admin`
2. Create a race
3. Wait for players to join
4. Click "Start Race"
5. Watch the live map!

### For Players:
1. Open `/race`
2. Enter your name
3. Pick a car color
4. Click "Join Race"
5. Drive with WASD or Arrow Keys
6. Stay on the road!

## 🛠️ Environment Variables

### `.env.local` (for local development)
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v2
```

### Vercel Environment Variables (for production)
```
NEXT_PUBLIC_API_BASE_URL=https://your-backend.railway.app/api/v2
```

## 📁 Project Structure

```
race-app/
├── app/
│   ├── page.tsx          # Home page with links
│   ├── race/
│   │   └── page.tsx      # Player racing interface
│   └── admin/
│       └── page.tsx      # Admin control panel
├── .env.local            # Local environment variables
├── .env.example          # Example env file
└── package.json
```

## 🔧 Troubleshooting

### "Failed to fetch" errors
- Make sure backend is running
- Check `NEXT_PUBLIC_API_BASE_URL` is correct
- Backend must allow CORS from your frontend domain

### Backend CORS issues
Update `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.vercel.app"],  # Add your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Players can't join
- Admin must create a race first
- Check backend logs for errors
- Verify API URL in environment variables

## 🎯 Features

- ✅ Real-time multiplayer racing
- ✅ Live admin map showing all players
- ✅ Collision detection
- ✅ Off-road crash detection (3 second grace period)
- ✅ Auto-end race when all players finish/crash/AFK
- ✅ Leaderboard with rankings
- ✅ WASD + Arrow key controls
- ✅ Mobile responsive
- ✅ Beautiful Tailwind UI

## 🚗 Tech Stack

- **Frontend**: Next.js 15, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python)
- **Deployment**: Vercel (frontend) + Railway/Render (backend)

## 📝 License

Built for hackathon demo purposes.
