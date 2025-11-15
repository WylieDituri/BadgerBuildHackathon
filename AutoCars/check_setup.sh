#!/bin/bash
# Quick setup checker for the Traffic Visualizer hackathon project

echo "🚦 Traffic Visualizer Setup Check"
echo "=================================="
echo ""

# Check Node.js
echo "1. Checking Node.js..."
if command -v node &> /dev/null; then
    echo "   ✅ Node.js installed: $(node --version)"
else
    echo "   ❌ Node.js not found. Install from https://nodejs.org"
fi
echo ""

# Check if server is running
echo "2. Checking backend server..."
if curl -s http://localhost:4000/health > /dev/null 2>&1; then
    echo "   ✅ Server is running on port 4000"
    echo "   Response: $(curl -s http://localhost:4000/health)"
else
    echo "   ⚠️  Server not responding. Run: cd AutoCars/server && npm run dev"
fi
echo ""

# Check Godot project exists
echo "3. Checking Godot project..."
if [ -f "godot/traffic_sim/project.godot" ]; then
    echo "   ✅ Godot project found at: godot/traffic_sim/"
else
    echo "   ❌ Godot project not found"
fi
echo ""

# Check web files
echo "4. Checking web form files..."
if [ -f "web/index.html" ] && [ -f "web/app.js" ]; then
    echo "   ✅ Web form files found"
    echo "   To serve: cd web && npx serve -l 3000"
else
    echo "   ❌ Web form files missing"
fi
echo ""

# Summary
echo "=================================="
echo "📋 NEXT STEPS:"
echo ""
echo "1. Open Godot Engine"
echo "2. Import project: AutoCars/godot/traffic_sim/project.godot"
echo "3. Press F5 to run"
echo "4. Use TAB to toggle modes, R for rush hour"
echo ""
echo "Optional: Serve web form"
echo "  cd AutoCars/web && npx serve -l 3000"
echo ""
echo "📖 Full guide: AutoCars/QUICKSTART.md"
echo "=================================="

