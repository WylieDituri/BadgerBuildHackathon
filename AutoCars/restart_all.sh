#!/bin/bash
# Restart all AutoCars services

echo "🔄 Restarting AutoCars Traffic Visualizer..."
echo ""

# Kill existing processes
echo "1️⃣  Stopping existing servers..."
lsof -ti:4000 | xargs kill -9 2>/dev/null && echo "   ✅ Killed backend on port 4000" || echo "   ℹ️  No backend running"
lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "   ✅ Killed web server on port 3000" || echo "   ℹ️  No web server running"
echo ""

# Wait a moment
sleep 1

# Start backend
echo "2️⃣  Starting backend server..."
cd "$(dirname "$0")/server"
npm run dev > /dev/null 2>&1 &
BACKEND_PID=$!
echo "   ✅ Backend started (PID: $BACKEND_PID)"
echo ""

# Wait for backend to start
sleep 2

# Check backend health
echo "3️⃣  Checking backend health..."
if curl -s http://localhost:4000/health > /dev/null 2>&1; then
    echo "   ✅ Backend responding on http://localhost:4000"
else
    echo "   ⚠️  Backend may need more time to start"
fi
echo ""

# Start web server
echo "4️⃣  Starting web form server..."
cd "$(dirname "$0")/web"
npx serve -l 3000 > /dev/null 2>&1 &
WEB_PID=$!
echo "   ✅ Web server started (PID: $WEB_PID)"
echo ""

sleep 2

echo "════════════════════════════════════════════════════════════"
echo ""
echo "✅ ALL SYSTEMS STARTED"
echo ""
echo "   Backend:  http://localhost:4000"
echo "   Web Form: http://localhost:3000"
echo ""
echo "To stop, run: kill $BACKEND_PID $WEB_PID"
echo "Or use: lsof -ti:4000,3000 | xargs kill -9"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📖 Next: Open Godot and import AutoCars/godot/traffic_sim/"
echo ""

