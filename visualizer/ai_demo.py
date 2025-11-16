#!/usr/bin/env python3
"""
Simple AI Traffic Demo - Connects to real backend
Shows cars moving with AI coordination from the actual API
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, Polygon, Rectangle
import numpy as np
import requests
import math
import time
import random

API_BASE = "http://localhost:8000/api/v2/intelligence"

class AITrafficDemo:
    def __init__(self):
        self.fig, self.ax = plt.subplots(1, 1, figsize=(14, 10))
        self.fig.patch.set_facecolor('#1a1a1a')
        
        self.cars = {}  # Local car state with positions
        self.collision_predictions = []
        self.frame = 0
        
        # Spawn cars initially
        self.spawn_initial_cars()
        
    def spawn_initial_cars(self):
        """Spawn a few cars to start with."""
        spawn_configs = [
            {"lat": 43.140, "lon": -89.39, "heading": 180, "speed": 0.0004},   # North
            {"lat": 43.070, "lon": -89.39, "heading": 0, "speed": 0.0004},     # South
            {"lat": 43.105, "lon": -89.32, "heading": 270, "speed": 0.0004},   # East
            {"lat": 43.105, "lon": -89.46, "heading": 90, "speed": 0.0004},    # West
        ]
        
        for i, config in enumerate(spawn_configs):
            car_id = f"demo_{i+1:02d}"
            is_emergency = i == 0  # Make first car emergency
            
            # Store locally
            self.cars[car_id] = {
                "car_id": car_id,
                "lat": config["lat"],
                "lon": config["lon"],
                "heading": config["heading"],
                "speed": config["speed"],
                "is_emergency": is_emergency,
                "status": "normal"
            }
            
            try:
                # Register car with backend
                requests.post(f"{API_BASE}/cars/register", json={
                    "car_id": car_id,
                    "vehicle_type": "emergency" if is_emergency else "sedan",
                    "is_emergency": is_emergency
                }, timeout=2)
                
                print(f"✓ Spawned {car_id}")
            except Exception as e:
                print(f"Failed to spawn {car_id}: {e}")
    
    def update_car_positions(self):
        """Update positions of all cars."""
        for car_id, car in list(self.cars.items()):
            # Move car based on heading
            heading_rad = math.radians(car['heading'])
            car['lat'] += car['speed'] * math.sin(heading_rad)
            car['lon'] += car['speed'] * math.cos(heading_rad)
            
            # Remove if off map
            x, y = self.lat_lon_to_xy(car['lat'], car['lon'])
            if abs(x) > 6 or abs(y) > 6:
                del self.cars[car_id]
                continue
            
            # Send position to backend
            try:
                requests.post(f"{API_BASE}/cars/location", json={
                    "car_id": car_id,
                    "lat": car['lat'],
                    "lon": car['lon'],
                    "speed": car['speed'] * 100000,  # Convert to m/s
                    "heading": car['heading']
                }, timeout=0.5)
            except:
                pass  # Don't block on backend issues
    
    def fetch_collision_predictions(self):
        """Fetch collision predictions from AI."""
        try:
            resp = requests.get(f"{API_BASE}/collisions/predict", timeout=1)
            if resp.status_code == 200:
                data = resp.json()
                self.collision_predictions = data['predictions']
        except:
            pass
    
    def draw_map(self, ax):
        """Draw city map."""
        ax.clear()
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.set_aspect('equal')
        ax.set_facecolor('#1a1a1a')
        ax.axis('off')
        
        # Roads
        for pos in [-3, 0, 3]:
            ax.plot([pos, pos], [-4.5, 4.5], color='#3a3a3a', linewidth=20, alpha=0.8, zorder=1)
            ax.plot([-4.5, 4.5], [pos, pos], color='#3a3a3a', linewidth=20, alpha=0.8, zorder=1)
            # Lane dividers
            ax.plot([pos, pos], [-4.5, 4.5], color='#ffeb3b', linewidth=1, 
                   alpha=0.3, linestyle='--', zorder=2)
            ax.plot([-4.5, 4.5], [pos, pos], color='#ffeb3b', linewidth=1, 
                   alpha=0.3, linestyle='--', zorder=2)
        
        # Intersections
        for x in [-3, 0, 3]:
            for y in [-3, 0, 3]:
                circle = Circle((x, y), 0.5, color='yellow', alpha=0.15, zorder=2)
                ax.add_patch(circle)
        
        # Buildings
        building_positions = [
            (-4.5, 1.2), (-4.5, -1.8), (-4.5, -4.2),
            (-1.2, 1.2), (-1.2, -1.8), (-1.2, -4.2),
            (1.2, 1.2), (1.2, -1.8), (1.2, -4.2),
            (4.2, 1.2), (4.2, -1.8), (4.2, -4.2),
        ]
        for (x, y) in building_positions:
            rect = Rectangle((x, y), 0.7, 0.7, 
                           facecolor='#2a2a2a', 
                           edgecolor='#555', 
                           linewidth=1, zorder=1)
            ax.add_patch(rect)
        
        # Title
        ax.text(0, 4.8, 'AI TRAFFIC COORDINATION - LIVE', 
               ha='center', va='center', fontsize=18, 
               color='#00ff00', fontweight='bold')
    
    def lat_lon_to_xy(self, lat, lon):
        """Convert lat/lon to map coordinates."""
        x = (lon + 89.39) * 100 - 3
        y = (lat - 43.075) * 100 - 3
        return np.clip(x, -4.5, 4.5), np.clip(y, -4.5, 4.5)
    
    def draw_cars(self, ax):
        """Draw all cars."""
        for car_id, car in self.cars.items():
            x, y = self.lat_lon_to_xy(car['lat'], car['lon'])
            heading = car['heading']
            is_emergency = car['is_emergency']
            
            # Car body
            angle = math.radians(heading)
            car_length = 0.3
            car_width = 0.18
            corners = np.array([
                [-car_length/2, -car_width/2],
                [car_length/2, -car_width/2],
                [car_length/2, car_width/2],
                [-car_length/2, car_width/2]
            ])
            
            cos_a, sin_a = np.cos(angle), np.sin(angle)
            rotation = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
            corners_rotated = corners @ rotation.T
            corners_rotated[:, 0] += x
            corners_rotated[:, 1] += y
            
            color = '#f59e0b' if is_emergency else '#3b82f6'
            car_poly = Polygon(corners_rotated, facecolor=color, 
                             edgecolor='white', linewidth=2, zorder=10)
            ax.add_patch(car_poly)
            
            # Label
            label = car_id.split('_')[-1][:3].upper()
            ax.text(x, y, label, ha='center', va='center',
                   fontsize=8, color='white', fontweight='bold', zorder=11)
            
            # Emergency indicator
            if is_emergency:
                ax.text(x, y + 0.35, '🚨', ha='center', va='center',
                       fontsize=10, zorder=12)
    
    def draw_collision_warnings(self, ax):
        """Draw collision prediction warnings."""
        for pred in self.collision_predictions:
            if pred['severity'] in ['critical', 'high']:
                point = pred['collision_point']
                x, y = self.lat_lon_to_xy(point['lat'], point['lon'])
                
                # Warning circle
                color = '#ef4444' if pred['severity'] == 'critical' else '#f59e0b'
                pulse = 0.3 + 0.2 * np.sin(self.frame * 0.3)
                circle = Circle((x, y), 0.4, color=color, alpha=pulse, zorder=8)
                ax.add_patch(circle)
                
                # Warning text
                time_str = f"{pred['time_to_collision']:.1f}s"
                ax.text(x, y + 0.6, f"⚠️ {time_str}", ha='center', va='center',
                       fontsize=9, color='white', fontweight='bold',
                       bbox=dict(boxstyle='round', facecolor=color, alpha=0.8),
                       zorder=9)
    
    def draw_stats(self, ax):
        """Draw statistics."""
        stats_text = (
            f"Active Cars: {len(self.cars)}\n"
            f"Collision Warnings: {len(self.collision_predictions)}\n"
            f"Frame: {self.frame}"
        )
        ax.text(-4.8, 4.5, stats_text, fontsize=10, 
               color='white', va='top',
               bbox=dict(boxstyle='round', facecolor='black', alpha=0.7),
               zorder=20)
    
    def update(self, frame):
        """Update animation frame."""
        self.frame = frame
        
        # Update car positions (move them)
        self.update_car_positions()
        
        # Fetch collision predictions from AI
        self.fetch_collision_predictions()
        
        # Draw everything
        self.draw_map(self.ax)
        self.draw_collision_warnings(self.ax)
        self.draw_cars(self.ax)
        self.draw_stats(self.ax)
        
        # Occasionally spawn new car
        if frame % 80 == 0 and len(self.cars) < 8:
            self.spawn_random_car()
    
    def spawn_random_car(self):
        """Spawn a random car."""
        spawn_configs = [
            {"lat": 43.140, "lon": -89.39 + random.uniform(-0.02, 0.02), "heading": 180, "speed": 0.0004},
            {"lat": 43.070, "lon": -89.39 + random.uniform(-0.02, 0.02), "heading": 0, "speed": 0.0004},
            {"lat": 43.105 + random.uniform(-0.02, 0.02), "lon": -89.32, "heading": 270, "speed": 0.0004},
            {"lat": 43.105 + random.uniform(-0.02, 0.02), "lon": -89.46, "heading": 90, "speed": 0.0004},
        ]
        
        config = random.choice(spawn_configs)
        car_id = f"demo_{int(time.time() * 1000) % 10000}"
        is_emergency = random.random() < 0.15
        
        # Store locally
        self.cars[car_id] = {
            "car_id": car_id,
            "lat": config["lat"],
            "lon": config["lon"],
            "heading": config["heading"],
            "speed": config["speed"] * (1.2 if is_emergency else 1.0),
            "is_emergency": is_emergency,
            "status": "normal"
        }
        
        try:
            requests.post(f"{API_BASE}/cars/register", json={
                "car_id": car_id,
                "vehicle_type": "emergency" if is_emergency else "sedan",
                "is_emergency": is_emergency
            }, timeout=1)
            print(f"✓ Spawned {car_id}")
        except:
            pass
    
    def run(self):
        """Run the demo."""
        print("🎬 Starting AI Traffic Demo...")
        print("📡 Connecting to:", API_BASE)
        print("\n✨ Cars will:")
        print("   • Move automatically")
        print("   • Send positions to AI backend")
        print("   • Show collision predictions from AI")
        print("\n⚠️  Make sure backend is running:")
        print("   cd backend && uvicorn app.main:app --reload")
        print("\n🚗 Starting with 4 cars...\n")
        
        anim = animation.FuncAnimation(
            self.fig, self.update, 
            interval=200,
            cache_frame_data=False
        )
        plt.show()


if __name__ == "__main__":
    demo = AITrafficDemo()
    demo.run()

