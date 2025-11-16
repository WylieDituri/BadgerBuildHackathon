#!/usr/bin/env python3
"""
Interactive traffic demo where real users can join via web and drive cars.
The visualization shows both user-controlled and AI-controlled cars.
"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle, Circle
import random
import requests
import time
from threading import Thread
import json

# Backend API
API_BASE = "http://localhost:8000/api/v2/intelligence"

# Visual constants
COLOR_BG = '#0f1419'
COLOR_ROAD = '#2b3a55'
COLOR_LANE = '#f5d442'
COLOR_TEXT = '#e5e7eb'
COLOR_USER_CAR = '#10b981'  # Green for user cars
COLOR_AI_CAR = '#3b82f6'    # Blue for AI cars
COLOR_EMERGENCY = '#f97316'

LANES_X = [-3.2, -0.8, 0.8, 3.2]
LANES_Y = [-3.2, -0.8, 0.8, 3.2]

# Map coordinate conversion
MAP_SIZE = 11  # -5.5 to 5.5
LAT_BASE = 43.0730
LON_BASE = -89.4012
LAT_RANGE = 0.01
LON_RANGE = 0.01


def screen_to_latlon(x, y):
    """Convert screen coordinates to lat/lon"""
    lat = LAT_BASE + (y / MAP_SIZE) * LAT_RANGE
    lon = LON_BASE + (x / MAP_SIZE) * LON_RANGE
    return lat, lon


def latlon_to_screen(lat, lon):
    """Convert lat/lon to screen coordinates"""
    x = ((lon - LON_BASE) / LON_RANGE) * MAP_SIZE
    y = ((lat - LAT_BASE) / LAT_RANGE) * MAP_SIZE
    return x, y


class Car:
    def __init__(self, car_id, x, y, is_user=False, is_emergency=False):
        self.car_id = car_id
        self.x = x
        self.y = y
        self.is_user = is_user
        self.is_emergency = is_emergency
        self.active = True
        self.heading = random.uniform(0, 360)
        self.speed = random.uniform(0.03, 0.05)
        
    def position(self):
        return self.x, self.y


class InteractiveDemo:
    def __init__(self):
        self.fig = plt.figure(figsize=(12, 12), facecolor=COLOR_BG)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.cars = {}  # car_id -> Car object
        self.collisions = []
        self.last_fetch = 0
        
        print("🌐 Starting interactive demo...")
        print(f"📡 Backend: {API_BASE}")
        print("🎮 Users can join at: http://localhost:3000")
        print("   (Start the Next.js frontend to allow users to join)")

    def fetch_cars_from_backend(self):
        """Fetch all cars from the backend API"""
        try:
            response = requests.get(f"{API_BASE}/cars?active_only=true", timeout=1)
            if response.status_code == 200:
                data = response.json()
                return data.get('cars', [])
        except Exception as e:
            if time.time() - self.last_fetch > 5:  # Log errors only every 5 seconds
                print(f"⚠️  Backend not responding: {e}")
                self.last_fetch = time.time()
        return []

    def fetch_collisions(self):
        """Fetch collision predictions from backend"""
        try:
            response = requests.get(f"{API_BASE}/collisions/predict", timeout=1)
            if response.status_code == 200:
                data = response.json()
                return data.get('predictions', [])
        except:
            pass
        return []

    def update_cars(self):
        """Update car positions from backend"""
        backend_cars = self.fetch_cars_from_backend()
        current_ids = set()
        
        for car_data in backend_cars:
            car_id = car_data['car_id']
            current_ids.add(car_id)
            
            # Skip cars without position data
            if not car_data.get('current_position'):
                continue
            
            lat = car_data['current_position']['lat']
            lon = car_data['current_position']['lon']
            x, y = latlon_to_screen(lat, lon)
            
            # Check if this is a user-controlled car (car_id starts with "user_")
            is_user = car_data['car_id'].startswith('user_')
            is_emergency = car_data.get('vehicle_type') == 'emergency' or car_data.get('is_emergency', False)
            
            if car_id in self.cars:
                # Update existing car
                self.cars[car_id].x = x
                self.cars[car_id].y = y
                self.cars[car_id].active = True  # If we got position data, car is active
            else:
                # New car
                self.cars[car_id] = Car(car_id, x, y, is_user, is_emergency)
        
        # Remove cars that are no longer in backend
        for car_id in list(self.cars.keys()):
            if car_id not in current_ids:
                del self.cars[car_id]
        
        # Fetch collision warnings
        self.collisions = self.fetch_collisions()

    def draw_scene(self):
        """Draw the complete scene"""
        self.ax.clear()
        self.ax.set_xlim(-5.5, 5.5)
        self.ax.set_ylim(-5.5, 5.5)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor(COLOR_BG)
        self.ax.axis('off')

        # Draw roads
        for center in [-2, 2]:
            self.ax.add_patch(Rectangle((center - 1.2, -5.5), 2.4, 11, facecolor=COLOR_ROAD))
            self.ax.add_patch(Rectangle((-5.5, center - 1.2), 11, 2.4, facecolor=COLOR_ROAD))

        # Draw lane markers
        for lane in LANES_X:
            self.ax.plot([lane, lane], [-5.5, 5.5], color=COLOR_LANE, linestyle='--', alpha=0.4)
        for lane in LANES_Y:
            self.ax.plot([-5.5, 5.5], [lane, lane], color=COLOR_LANE, linestyle='--', alpha=0.4)

        # Draw intersections
        for x in [-2, 2]:
            for y in [-2, 2]:
                self.ax.add_patch(Circle((x, y), 0.55, facecolor='#fde047', alpha=0.2))

        # Title
        self.ax.set_title('🚗 Live Traffic with User Control', color=COLOR_TEXT, fontsize=16, pad=20)

        # Draw cars
        active_user_cars = 0
        active_ai_cars = 0
        
        for car in self.cars.values():
            if not car.active:
                continue
                
            if car.is_user:
                color = COLOR_USER_CAR
                active_user_cars += 1
                marker = 's'  # Square for users
            elif car.is_emergency:
                color = COLOR_EMERGENCY
                active_ai_cars += 1
                marker = 'o'
            else:
                color = COLOR_AI_CAR
                active_ai_cars += 1
                marker = 'o'
            
            self.ax.add_patch(Circle(car.position(), 0.24, facecolor=color, edgecolor='white', linewidth=1.5))
            
            # Label user cars
            if car.is_user:
                self.ax.text(car.x, car.y + 0.4, '👤', ha='center', fontsize=8)

        # Draw collision warnings
        critical_warnings = 0
        for collision in self.collisions:
            if collision.get('severity') == 'critical':
                critical_warnings += 1
                car1_id = collision.get('car1_id')
                car2_id = collision.get('car2_id')
                if car1_id in self.cars and car2_id in self.cars:
                    x1, y1 = self.cars[car1_id].position()
                    x2, y2 = self.cars[car2_id].position()
                    self.ax.plot([x1, x2], [y1, y2], 'r--', alpha=0.5, linewidth=1)

        # Stats panel
        stats_text = (
            f"👥 User Cars: {active_user_cars}\n"
            f"🤖 AI Cars: {active_ai_cars}\n"
            f"⚠️  Collision Warnings: {critical_warnings}"
        )
        self.ax.text(
            -5.3, 5.0, stats_text,
            color='white', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='#00000088', edgecolor='none'),
            verticalalignment='top'
        )
        
        # Legend
        legend_y = -4.5
        self.ax.add_patch(Circle((-4.5, legend_y), 0.2, facecolor=COLOR_USER_CAR, edgecolor='white'))
        self.ax.text(-4.2, legend_y, 'User', color='white', fontsize=9, va='center')
        
        self.ax.add_patch(Circle((-2.5, legend_y), 0.2, facecolor=COLOR_AI_CAR, edgecolor='white'))
        self.ax.text(-2.2, legend_y, 'AI', color='white', fontsize=9, va='center')
        
        self.ax.add_patch(Circle((-0.5, legend_y), 0.2, facecolor=COLOR_EMERGENCY, edgecolor='white'))
        self.ax.text(-0.2, legend_y, 'Emergency', color='white', fontsize=9, va='center')

    def update(self, frame):
        """Animation update function"""
        self.update_cars()
        self.draw_scene()

    def run(self):
        """Start the interactive demo"""
        # Initial draw
        self.draw_scene()
        
        # Create animation
        anim = FuncAnimation(self.fig, self.update, interval=500, blit=False)
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    demo = InteractiveDemo()
    demo.run()


