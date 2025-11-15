# 🎬 Manim Traffic Coordination Demo

A visually impressive animation showing **Chaos vs AI** traffic coordination.

## 🚀 Quick Start

### 1. Install Manim

```bash
# macOS
brew install py3cairo ffmpeg
pip install manim

# Or using conda
conda install -c conda-forge manim
```

### 2. Run the Demo

```bash
cd manim_demo

# Quick 30-second demo
manim -pql traffic_demo.py QuickDemo

# Full side-by-side comparison
manim -pqh traffic_demo.py TrafficDemo

# Detailed comparison with stats
manim -pqh traffic_demo.py DetailedComparison
```

## 🎥 Available Scenes

### `QuickDemo` (30 seconds)
- Simple, fast demo
- Shows basic coordination
- Perfect for quick presentations

### `TrafficDemo` (2-3 minutes)
- Side-by-side comparison
- Shows collisions in chaos mode
- Shows smooth coordination in AI mode
- **Recommended for hackathon!**

### `DetailedComparison` (3-4 minutes)
- More detailed road network
- Statistics at the end
- Best for judges who want details

## 🎨 What It Shows

1. **Chaos Mode (Left Side)**
   - Cars move independently
   - Random speeds
   - Collisions at intersections
   - Visual collision indicators

2. **AI Mode (Right Side)**
   - Coordinated movement
   - Staggered starts
   - No collisions
   - Success indicators

3. **Final Comparison**
   - Statistics
   - Clear visual difference
   - Professional presentation

## ⚙️ Quality Settings

- `-pql` = Preview, Low Quality (fast, for testing)
- `-pqm` = Preview, Medium Quality (good balance)
- `-pqh` = Preview, High Quality (best for demo)
- `-pqk` = Preview, 4K Quality (overkill for hackathon)

**For hackathon:** Use `-pqh` (high quality, looks professional)

## 🎤 Presentation Tips

1. **Start with QuickDemo** - Get attention fast
2. **Show TrafficDemo** - Main comparison
3. **End with stats** - Let judges see the numbers

**Total time:** ~3-4 minutes

## 🎯 Why Manim is Perfect

✅ **Professional look** - Like 3Blue1Brown videos  
✅ **Smooth animations** - Impressive visuals  
✅ **Hardcoded** - Runs reliably every time  
✅ **No dependencies** - Just Python + Manim  
✅ **Easy to customize** - Change colors, speeds, etc.  

## 🔧 Customization

Edit `traffic_demo.py` to:
- Change car colors
- Adjust speeds
- Add more cars
- Change road layout
- Modify timing

## 📊 Output

Videos are saved to:
```
manim_demo/media/videos/traffic_demo/1080p60/[SceneName].mp4
```

You can:
- Play directly from terminal (with `-p` flag)
- Show in presentation
- Upload to YouTube
- Embed in website

## 🏆 Perfect for Hackathons!

- ✅ No live demo needed
- ✅ Works every time
- ✅ Looks professional
- ✅ Easy to explain
- ✅ Impressive visuals

**Just render once, play anytime!** 🎬

