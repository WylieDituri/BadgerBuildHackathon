"""
Combined Traffic Demo: Human Driving → AI Coordination
Shows human driving first, then transitions to AI-coordinated driving
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.patches import Rectangle, Polygon, FancyBboxPatch, Wedge
import sys
import os

# Import both demo classes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from practice_demo_human import TrafficDemo as HumanTrafficDemo
from practice_demo import TrafficDemo as AITrafficDemo

class CombinedDemo:
    def __init__(self):
        self.fig, self.ax = plt.subplots(1, 1, figsize=(12, 10))
        self.fig.patch.set_facecolor('#2b2b2b')
        
        # Animation state
        self.frame = 0
        self.total_frames = 0
        self.current_mode = 'human'  # 'human' or 'ai'
        self.human_completed = False
        self.transition_frames = 60  # 3 seconds transition (60 frames at 20 fps)
        self.transition_counter = 0
        
        # Initialize both demos
        print("Initializing Human Driving Demo...")
        self.human_demo = HumanTrafficDemo()
        # Close the figure created by human_demo (we'll use our own)
        plt.close(self.human_demo.fig)
        self.human_demo.fig = self.fig
        self.human_demo.ax = self.ax
        
        print("Initializing AI Coordination Demo...")
        self.ai_demo = AITrafficDemo()
        # Close the figure created by ai_demo (we'll use our own)
        plt.close(self.ai_demo.fig)
        self.ai_demo.fig = self.fig
        self.ai_demo.ax = self.ax
        
        # Reset AI demo cars to starting positions
        self.ai_demo.all_cars_reached_destination = False
        self.ai_demo.start_time = None
        self.ai_demo.end_time = None
        for car in self.ai_demo.cars:
            car['active'] = True
            car['reached_destination'] = False
            # Reset car positions to initial positions
            if 'R' in car['label']:
                car['x'] = self.ai_demo.x_min
            elif 'L' in car['label']:
                car['x'] = self.ai_demo.x_max
            elif 'U' in car['label']:
                car['y'] = self.ai_demo.y_min
            elif 'D' in car['label']:
                car['y'] = self.ai_demo.y_max
    
    def animate(self, frame):
        """Main animation function that switches between human and AI demos."""
        self.frame = frame
        self.total_frames += 1
        
        # Check if human demo is complete
        if self.current_mode == 'human':
            if not self.human_completed:
                # Run human demo
                self.human_demo.frame = frame
                self.human_demo.total_frames += 1
                self.human_demo.update_cars()
                
                # Check if all human cars reached destination
                if self.human_demo.check_all_destinations():
                    self.human_demo.end_frame = self.human_demo.total_frames
                    self.human_demo.all_cars_reached_destination = True
                    self.human_completed = True
                    self.transition_counter = 0
                    print(f"Human demo completed in {self.human_demo.end_frame / 20.0:.2f} seconds")
            
            # Draw human demo
            self.ax.clear()
            self.human_demo.draw_roads(self.ax)
            
            for car in self.human_demo.cars:
                self.human_demo.draw_car(self.ax, car)
            
            # Draw title
            if self.human_completed:
                # Show transition message
                self.ax.text(0, 2.8, 'HUMAN DRIVING COMPLETE', 
                            ha='center', va='center', fontsize=20, 
                            color='#FFAA44', fontweight='bold',
                            bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.8))
                self.ax.text(0, 2.3, 'Transitioning to AI Mode...', 
                            ha='center', va='center', fontsize=16, 
                            color='#44FF44', fontweight='bold',
                            bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.8))
                
                # Countdown transition
                self.transition_counter += 1
                if self.transition_counter >= self.transition_frames:
                    self.current_mode = 'ai'
                    print("Switching to AI demo...")
            else:
                self.ax.text(0, 2.8, 'HUMAN DRIVING MODE', 
                            ha='center', va='center', fontsize=20, 
                            color='#FFAA44', fontweight='bold',
                            bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.8))
            
            # Draw timer
            fps = 20
            if self.human_demo.all_cars_reached_destination:
                elapsed = self.human_demo.end_frame / fps
                timer_text = f"✓ Human: {elapsed:.2f} seconds"
                self.ax.text(1.5, -1.1, timer_text, fontsize=14, color='#00FF00', 
                            ha='center', weight='bold', bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
            else:
                elapsed = self.human_demo.total_frames / fps
                timer_text = f"Human Time: {elapsed:.2f} seconds"
                self.ax.text(1.5, -1.1, timer_text, fontsize=14, color='white', 
                            ha='center', weight='bold', bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        else:
            # AI mode
            # Calculate AI frame (reset to 0 when switching)
            if not hasattr(self, 'ai_start_frame'):
                self.ai_start_frame = frame
                self.ai_demo.start_time = None
            
            ai_frame = frame - self.ai_start_frame
            
            # Run AI demo
            self.ai_demo.frame = ai_frame
            if self.ai_demo.start_time is None:
                self.ai_demo.start_time = ai_frame / 20.0
            
            self.ai_demo.update_cars()
            
            # Check if all AI cars reached destination
            if not self.ai_demo.all_cars_reached_destination and self.ai_demo.check_all_destinations():
                self.ai_demo.end_time = ai_frame / 20.0
                self.ai_demo.all_cars_reached_destination = True
            
            # Draw AI demo
            self.ax.clear()
            self.ai_demo.draw_roads(self.ax)
            
            for car in self.ai_demo.cars:
                self.ai_demo.draw_car(self.ax, car)
            
            # Draw title
            self.ax.text(0, 2.8, 'AI COORDINATION MODE', 
                        ha='center', va='center', fontsize=20, 
                        color='#44FF44', fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.8))
            
            # Draw timer
            fps = 20
            if self.ai_demo.all_cars_reached_destination:
                elapsed = self.ai_demo.end_time - self.ai_demo.start_time
                timer_text = f"✓ AI: {elapsed:.2f} seconds"
                self.ax.text(1.5, -1.1, timer_text, fontsize=14, color='#00FF00', 
                            ha='center', weight='bold', bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
            else:
                elapsed = ai_frame / 20.0 - (self.ai_demo.start_time or 0)
                timer_text = f"AI Time: {elapsed:.2f} seconds"
                self.ax.text(1.5, -1.1, timer_text, fontsize=14, color='white', 
                            ha='center', weight='bold', bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        return []
    
    def run(self, save_mp4=False, filename='combined_demo.mp4'):
        """Run the combined animation."""
        # Calculate total frames needed (human + transition + AI)
        # Estimate: human ~300 frames, transition 60 frames, AI ~200 frames
        total_frames = 600  # Enough for both demos
        
        anim = animation.FuncAnimation(self.fig, self.animate, frames=total_frames, 
                                      interval=50, blit=False, repeat=False)
        plt.tight_layout()
        
        if save_mp4:
            print(f"\n🎬 Saving animation to {filename}...")
            print("This may take a few minutes...")
            try:
                # Try FFmpeg writer first (best quality)
                writer = animation.FFMpegWriter(fps=20, bitrate=1800)
                anim.save(filename, writer=writer)
                print(f"✅ Successfully saved to {filename}")
            except Exception as e:
                print(f"⚠️  FFmpeg not available, trying Pillow writer...")
                try:
                    # Fallback to Pillow writer (creates GIF, then we'd need to convert)
                    # Actually, let's try ImageMagick or just use a different approach
                    writer = animation.PillowWriter(fps=20)
                    anim.save(filename.replace('.mp4', '.gif'), writer=writer)
                    print(f"✅ Saved as GIF (Pillow writer). For MP4, install ffmpeg:")
                    print("   macOS: brew install ffmpeg")
                    print("   Linux: sudo apt-get install ffmpeg")
                    print("   Windows: Download from https://ffmpeg.org/")
                except Exception as e2:
                    print(f"❌ Error saving animation: {e2}")
                    print("Please install ffmpeg to save as MP4:")
                    print("   macOS: brew install ffmpeg")
                    print("   Linux: sudo apt-get install ffmpeg")
            return anim
        else:
            plt.show()
            return anim

if __name__ == '__main__':
    import sys
    
    print("🚗 Combined Traffic Demo: Human → AI")
    print("=" * 60)
    print("This demo shows:")
    print("  1. HUMAN DRIVING MODE first")
    print("     - Realistic human behavior with stopping")
    print("     - Uniform speeds, reaction delays")
    print("  2. Transition period (3 seconds)")
    print("  3. AI COORDINATION MODE")
    print("     - Optimized speeds and coordination")
    print("     - Smooth, efficient traffic flow")
    print("=" * 60)
    print()
    
    # Automatically save as MP4
    save_mp4 = True
    filename = 'combined_demo.mp4'
    
    print("📹 MP4 recording mode enabled")
    print()
    
    demo = CombinedDemo()
    demo.run(save_mp4=save_mp4, filename=filename)

