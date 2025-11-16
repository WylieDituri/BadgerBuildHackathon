"""
Script to create GIFs from practice_demo.py and practice_demo_human.py
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
import os

# Import both demo classes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from practice_demo_human import TrafficDemo as HumanTrafficDemo
from practice_demo import TrafficDemo as AITrafficDemo

def create_human_gif():
    """Create GIF from human driving demo."""
    print("🚗 Creating Human Driving Demo GIF...")
    print("=" * 60)
    
    demo = HumanTrafficDemo()
    
    # Calculate frames needed (estimate based on completion)
    total_frames = 400  # Enough for human demo to complete
    
    anim = animation.FuncAnimation(demo.fig, demo.animate, frames=total_frames, 
                                  interval=50, blit=False, repeat=False)
    plt.tight_layout()
    
    print("\n🎬 Saving human_demo.gif...")
    print("This may take a few minutes...")
    
    try:
        writer = animation.PillowWriter(fps=20)
        anim.save('human_demo.gif', writer=writer)
        print("✅ Successfully saved human_demo.gif")
        plt.close(demo.fig)
        return True
    except Exception as e:
        print(f"❌ Error saving human_demo.gif: {e}")
        plt.close(demo.fig)
        return False

def create_ai_gif():
    """Create GIF from AI coordination demo."""
    print("\n🤖 Creating AI Coordination Demo GIF...")
    print("=" * 60)
    
    demo = AITrafficDemo()
    
    # Calculate frames needed (estimate based on completion)
    total_frames = 300  # Enough for AI demo to complete
    
    anim = animation.FuncAnimation(demo.fig, demo.animate, frames=total_frames, 
                                  interval=50, blit=False, repeat=False)
    plt.tight_layout()
    
    print("\n🎬 Saving ai_demo.gif...")
    print("This may take a few minutes...")
    
    try:
        writer = animation.PillowWriter(fps=20)
        anim.save('ai_demo.gif', writer=writer)
        print("✅ Successfully saved ai_demo.gif")
        plt.close(demo.fig)
        return True
    except Exception as e:
        print(f"❌ Error saving ai_demo.gif: {e}")
        plt.close(demo.fig)
        return False

if __name__ == '__main__':
    print("📹 Creating GIFs for Google Slides Presentation")
    print("=" * 60)
    print()
    
    # Create human demo GIF
    human_success = create_human_gif()
    
    # Create AI demo GIF
    ai_success = create_ai_gif()
    
    print("\n" + "=" * 60)
    if human_success and ai_success:
        print("✅ Both GIFs created successfully!")
        print("   - human_demo.gif")
        print("   - ai_demo.gif")
        print("\nYou can now use these in your Google Slides presentation!")
    else:
        print("⚠️  Some GIFs failed to create. Check errors above.")
    print("=" * 60)

