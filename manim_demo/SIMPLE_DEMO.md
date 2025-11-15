# 🚗 Simple Traffic Demo (No Manim Needed!)

## ✅ **Easy Setup - Just Matplotlib!**

This version uses **matplotlib** instead of Manim - much easier to install and works reliably!

---

## 🚀 **Quick Start**

### 1. Install Dependencies

```bash
pip install matplotlib numpy
```

That's it! No ffmpeg, no complex dependencies.

### 2. Run the Demo

```bash
cd manim_demo
python simple_demo.py
```

**That's it!** A window opens showing the side-by-side comparison.

---

## 🎥 **What You Get**

- **Left side:** CHAOS mode - cars crash at intersection
- **Right side:** AI mode - coordinated movement, no crashes
- **Smooth animation** - 20 frames per second
- **Visual indicators** - Collision markers, success messages

---

## 💾 **Save as Video (Optional)**

If you want to save it as a video file:

```python
# Add this to simple_demo.py before demo.run():

from matplotlib.animation import FFMpegWriter

writer = FFMpegWriter(fps=20, metadata=dict(artist='Your Name'), bitrate=1800)
anim.save('traffic_demo.mp4', writer=writer)
```

**But you don't need to!** Just run it live during your presentation.

---

## 🎤 **Presentation Tips**

1. **Run it before judges arrive** - Make sure it works
2. **Full screen the window** - Looks more professional
3. **Point to specific moments** - "Watch the collision here..."
4. **Let it play through** - Takes ~10 seconds

---

## 🎯 **Why This is Better**

✅ **No complex dependencies** - Just matplotlib  
✅ **Works immediately** - No ffmpeg issues  
✅ **Easy to customize** - Simple Python code  
✅ **Reliable** - Runs every time  
✅ **Fast setup** - Install and go  

---

## 🔧 **Customization**

Edit `simple_demo.py` to:
- Change car colors
- Adjust speeds
- Add more cars
- Change timing
- Modify road layout

---

## 🏆 **Perfect for Hackathons!**

- ✅ No setup issues
- ✅ Works on any Mac/Windows/Linux
- ✅ Professional look
- ✅ Easy to explain
- ✅ Reliable every time

**Just run `python simple_demo.py` and you're done!** 🚀

