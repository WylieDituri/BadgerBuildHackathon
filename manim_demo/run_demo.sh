#!/bin/bash
# Quick script to render and play the Manim demo

echo "🎬 Rendering Manim Traffic Demo..."
echo ""

# Check if manim is installed
if ! command -v manim &> /dev/null; then
    echo "❌ Manim not found!"
    echo ""
    echo "Install with:"
    echo "  pip install manim"
    echo "  # or"
    echo "  conda install -c conda-forge manim"
    exit 1
fi

# Render and play
echo "Rendering TrafficDemo (high quality)..."
manim -pqh traffic_demo.py TrafficDemo

echo ""
echo "✅ Done! Video saved to:"
echo "   media/videos/traffic_demo/1080p60/TrafficDemo.mp4"
echo ""
echo "To render other scenes:"
echo "  manim -pqh traffic_demo.py QuickDemo"
echo "  manim -pqh traffic_demo.py DetailedComparison"

