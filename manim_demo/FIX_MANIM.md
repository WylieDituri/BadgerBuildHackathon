# 🔧 Fix Manim FFmpeg Issue (Optional)

If you want to use Manim instead of the simple demo, here's how to fix the ffmpeg issue:

## **Option 1: Reinstall FFmpeg**

```bash
# Uninstall old ffmpeg
brew uninstall ffmpeg

# Reinstall
brew install ffmpeg

# Reinstall manim
pip uninstall manim
pip install manim
```

## **Option 2: Use Conda (More Reliable)**

```bash
# Install via conda (handles dependencies better)
conda install -c conda-forge manim

# Then run
manim -pqh traffic_demo.py TrafficDemo
```

## **Option 3: Use Simple Demo Instead (Recommended!)**

The `simple_demo.py` uses matplotlib and works immediately:

```bash
pip install matplotlib numpy
python simple_demo.py
```

**No ffmpeg issues, no complex setup!**

---

## 🎯 **Recommendation**

For a hackathon, **use `simple_demo.py`**:
- ✅ Works immediately
- ✅ No dependency issues
- ✅ Easy to customize
- ✅ Professional look
- ✅ Reliable

**Just run it and focus on your presentation!** 🚀

