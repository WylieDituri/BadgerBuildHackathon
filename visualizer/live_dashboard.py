#!/usr/bin/env python3
"""
Real-time visualization dashboard for the traffic intelligence system.
Connects to the API and shows live car positions, collision predictions,
intersection coordination, and traffic congestion.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch, Wedge
import requests
import numpy as np
import math
from datetime import datetime
import time

# API Configuration
API_BASE = "http://localhost:8000/api/v2/intelligence"

# Colors
COLOR_BG = '#1a1a1a'
COLOR_ROAD = '#404040'
COLOR_BUILDING = '#3d3d3d'
COLOR_CAR_NORMAL = '#4444FF'
COLOR_CAR_EMERGENCY = '#FF4444'
COLOR_COLLISION_WARNING = '#FF8800'
COLOR_COLLISION_CRITICAL = '#FF0000'
COLOR_TEXT = 'white'


class LiveDashboard:
    """Real-time visualization of traffic intelligence system."""
    
    def __init__(self):
        self.fig = plt.figure(figsize=(18, 10))
        self.fig.patch.set_facecolor(COLOR_BG)
        
        # Create subplots
        gs = self.fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        self.ax_map = self.fig.add_subplot(gs[:, :2])  # Large map view
        self.ax_collisions = self.fig.add_subplot(gs[0, 2])  # Collision list
        self.ax_metrics = self.fig.add_subplot(gs[1, 2])  # System metrics
        
        # State
        self.cars = {}
        self.collision_predictions = []
        self.system_status = {}
        
        # Setup
        self._setup_map()
        self._setup_collision_panel()
        self._setup_metrics_panel()
    
    def _setup_map(self):
        """Setup main map display."""
        self.ax_map.set_xlim(-5, 5)
        self.ax_map.set_ylim(-4, 4)
        self.ax_map.set_aspect('equal')
        self.ax_map.axis('off')
        self.ax_map.set_facecolor(COLOR_BG)
        
        # Draw road grid
        for x in [-3, 0, 3]:
            self.ax_map.plot([x, x], [-4, 4], color=COLOR_ROAD, linewidth=15, alpha=0.8, zorder=1)
        for y in [-3, 0, 3]:
            self.ax_map.plot([-5, 5], [y, y], color=COLOR_ROAD, linewidth=15, alpha=0.8, zorder=1)
        
        # Draw intersections
        for x in [-3, 0, 3]:
            for y in [-3, 0, 3]:
                circle = Circle((x, y), 0.3, color='yellow', alpha=0.3, zorder=2)
                self.ax_map.add_patch(circle)
        
        # Draw buildings
        buildings = [
            (-4.5, 0.5, 1.2, 1.2),
            (-1.5, 0.5, 1.2, 1.2),
            (1.5, 0.5, 1.2, 1.2),
            (-4.5, -2.5, 1.2, 1.2),
            (-1.5, -2.5, 1.2, 1.2),
            (1.5, -2.5, 1.2, 1.2),
        ]
        for x, y, w, h in buildings:
            rect = Rectangle((x, y), w, h, facecolor=COLOR_BUILDING, 
                           edgecolor='#555', linewidth=1, zorder=1)
            self.ax_map.add_patch(rect)
        
        # Title
        self.ax_map.text(0, 3.7, 'LIVE TRAFFIC INTELLIGENCE', 
                        ha='center', va='center', fontsize=20, 
                        color=COLOR_TEXT, fontweight='bold')
    
    def _setup_collision_panel(self):
        """Setup collision prediction panel."""
        self.ax_collisions.set_xlim(0, 1)
        self.ax_collisions.set_ylim(0, 1)
        self.ax_collisions.axis('off')
        self.ax_collisions.set_facecolor('#0a0a0a')
        
        self.ax_collisions.text(0.5, 0.95, '⚠️ COLLISION PREDICTIONS', 
                               ha='center', va='top', fontsize=12, 
                               color=COLOR_TEXT, fontweight='bold')
    
    def _setup_metrics_panel(self):
        """Setup metrics panel."""
        self.ax_metrics.set_xlim(0, 1)
        self.ax_metrics.set_ylim(0, 1)
        self.ax_metrics.axis('off')
        self.ax_metrics.set_facecolor('#0a0a0a')
        
        self.ax_metrics.text(0.5, 0.95, '📊 SYSTEM METRICS', 
                            ha='center', va='top', fontsize=12, 
                            color=COLOR_TEXT, fontweight='bold')
    
    def fetch_data(self):
        """Fetch data from API."""
        try:
            # Get system status
            resp = requests.get(f"{API_BASE}/analytics/system-status", timeout=1)
            if resp.status_code == 200:
                self.system_status = resp.json()
            
            # Get cars
            resp = requests.get(f"{API_BASE}/cars?active_only=true", timeout=1)
            if resp.status_code == 200:
                data = resp.json()
                self.cars = {car['car_id']: car for car in data['cars']}
            
            # Get collision predictions
            resp = requests.get(f"{API_BASE}/collisions/predict", timeout=1)
            if resp.status_code == 200:
                data = resp.json()
                self.collision_predictions = data['predictions']
            
            return True
        except Exception as e:
            print(f"Error fetching data: {e}")
            return False
    
    def update(self, frame):
        """Update visualization."""
        # Fetch latest data
        if not self.fetch_data():
            return
        
        # Clear dynamic elements (patches and texts)
        # Remove patches that have the '_dynamic' attribute
        for patch in list(self.ax_map.patches):
            if hasattr(patch, '_dynamic'):
                patch.remove()
        
        # Remove texts that have the '_dynamic' attribute
        for text in list(self.ax_map.texts):
            if hasattr(text, '_dynamic'):
                text.remove()
        
        # Draw collision warnings
        self._draw_collision_warnings()
        
        # Draw cars
        self._draw_cars()
        
        # Update collision panel
        self._update_collision_panel()
        
        # Update metrics panel
        self._update_metrics_panel()
    
    def _draw_cars(self):
        """Draw all cars on map."""
        for car_data in self.cars.values():
            pos = car_data.get('current_position')
            if not pos:
                continue
            
            # Map real lat/lon to visualization coordinates
            # For demo, we'll place cars randomly if no real position
            x = np.random.uniform(-4, 4)
            y = np.random.uniform(-3.5, 3.5)
            
            # Try to use actual position if available
            if 'lat' in pos and 'lon' in pos:
                # Simple projection (for demo)
                x = (pos['lon'] + 89.39) * 100 - 3
                y = (pos['lat'] - 43.075) * 100 - 3
                x = np.clip(x, -4, 4)
                y = np.clip(y, -3.5, 3.5)
            
            # Determine color
            is_emergency = car_data.get('is_emergency', False)
            color = COLOR_CAR_EMERGENCY if is_emergency else COLOR_CAR_NORMAL
            
            # Check if involved in collision prediction
            car_id = car_data['car_id']
            in_collision = any(
                p['car1_id'] == car_id or p['car2_id'] == car_id
                for p in self.collision_predictions
            )
            
            if in_collision:
                # Pulsing warning
                pulse = 0.5 + 0.5 * math.sin(time.time() * 5)
                circle = Circle((x, y), 0.25, color=COLOR_COLLISION_WARNING, 
                              alpha=pulse * 0.5, zorder=10)
                circle._dynamic = True
                self.ax_map.add_patch(circle)
            
            # Car body
            circle = Circle((x, y), 0.15, color=color, alpha=0.9, 
                          edgecolor='white', linewidth=2, zorder=11)
            circle._dynamic = True
            self.ax_map.add_patch(circle)
            
            # Car label
            label = car_data['car_id'].split('_')[-1][:3].upper()
            text = self.ax_map.text(x, y, label, ha='center', va='center',
                                   fontsize=8, color='white', fontweight='bold', zorder=12)
            text._dynamic = True
            
            # Emergency indicator
            if is_emergency:
                siren = self.ax_map.text(x, y + 0.3, '🚨', ha='center', va='center',
                                        fontsize=10, zorder=12)
                siren._dynamic = True
    
    def _draw_collision_warnings(self):
        """Draw collision warning indicators."""
        for pred in self.collision_predictions:
            # Get collision point
            point = pred['collision_point']
            x = (point['lon'] + 89.39) * 100 - 3
            y = (point['lat'] - 43.075) * 100 - 3
            x = np.clip(x, -4, 4)
            y = np.clip(y, -3.5, 3.5)
            
            # Severity color
            severity = pred['severity']
            if severity == 'critical':
                color = '#FF0000'
                size = 0.5
            elif severity == 'high':
                color = '#FF4400'
                size = 0.4
            else:
                color = '#FF8800'
                size = 0.3
            
            # Pulsing warning circle
            pulse = 0.5 + 0.5 * math.sin(time.time() * 3)
            circle = Circle((x, y), size, color=color, alpha=pulse * 0.3, zorder=5)
            circle._dynamic = True
            self.ax_map.add_patch(circle)
            
            # Warning icon
            text = self.ax_map.text(x, y, '⚠️', ha='center', va='center',
                                   fontsize=16, zorder=6)
            text._dynamic = True
    
    def _update_collision_panel(self):
        """Update collision prediction list."""
        self.ax_collisions.clear()
        self._setup_collision_panel()
        
        if not self.collision_predictions:
            self.ax_collisions.text(0.5, 0.5, 'No collision risks detected\n✓ All clear',
                                   ha='center', va='center', fontsize=10,
                                   color='#00FF00', fontweight='bold')
            return
        
        y_pos = 0.85
        for i, pred in enumerate(self.collision_predictions[:5]):  # Show top 5
            severity = pred['severity']
            
            if severity == 'critical':
                icon = '🔴'
                color = '#FF0000'
            elif severity == 'high':
                icon = '🟠'
                color = '#FF8800'
            else:
                icon = '🟡'
                color = '#FFAA00'
            
            # Collision info
            car1 = pred['car1_id'].split('_')[-1][:5]
            car2 = pred['car2_id'].split('_')[-1][:5]
            time_left = pred['time_to_collision_seconds']
            distance = pred['closest_distance_meters']
            
            text = f"{icon} {car1} ↔ {car2}"
            self.ax_collisions.text(0.05, y_pos, text, ha='left', va='top',
                                   fontsize=9, color=color, fontweight='bold')
            
            details = f"   {time_left:.1f}s • {distance:.0f}m"
            self.ax_collisions.text(0.05, y_pos - 0.05, details, ha='left', va='top',
                                   fontsize=7, color='#AAAAAA')
            
            y_pos -= 0.15
            
            if i >= 4:
                break
        
        if len(self.collision_predictions) > 5:
            self.ax_collisions.text(0.5, 0.05, f"+ {len(self.collision_predictions) - 5} more",
                                   ha='center', va='bottom', fontsize=8,
                                   color='#666666', style='italic')
    
    def _update_metrics_panel(self):
        """Update system metrics."""
        self.ax_metrics.clear()
        self._setup_metrics_panel()
        
        if not self.system_status:
            self.ax_metrics.text(0.5, 0.5, 'Connecting to API...',
                                ha='center', va='center', fontsize=10,
                                color='#888888', style='italic')
            return
        
        cars = self.system_status.get('cars', {})
        collisions = self.system_status.get('collisions', {})
        traffic = self.system_status.get('traffic', {})
        intersections = self.system_status.get('intersections', {})
        
        metrics_text = f"""
🚗 CARS
  Active: {cars.get('currently_active', 0)}
  Total: {cars.get('total_registered', 0)}
  Emergency: {cars.get('emergency_vehicles', 0)}

⚠️ COLLISIONS
  Predictions: {collisions.get('total_predictions', 0)}
  Critical: {collisions.get('critical_risk', 0)}
  At Risk: {collisions.get('at_risk_cars', 0)}

🚥 TRAFFIC
  Segments: {traffic.get('monitored_segments', 0)}
  Congestion: {traffic.get('average_congestion', 0):.0%}
  Incidents: {traffic.get('active_incidents', 0)}

🚦 INTERSECTIONS
  Requests: {intersections.get('total_requests', 0)}
  Approval: {intersections.get('approval_rate', 0):.0%}
  Avg Wait: {intersections.get('average_wait_time', 0):.1f}s
        """
        
        self.ax_metrics.text(0.05, 0.85, metrics_text.strip(), ha='left', va='top',
                            fontsize=9, color=COLOR_TEXT, family='monospace',
                            linespacing=1.5)
        
        # Status indicator
        status_color = '#00FF00'
        status_text = '● OPERATIONAL'
        if collisions.get('critical_risk', 0) > 0:
            status_color = '#FF0000'
            status_text = '● CRITICAL ALERTS'
        elif collisions.get('total_predictions', 0) > 0:
            status_color = '#FFAA00'
            status_text = '● WARNINGS ACTIVE'
        
        self.ax_metrics.text(0.5, 0.05, status_text, ha='center', va='bottom',
                            fontsize=10, color=status_color, fontweight='bold')
    
    def run(self):
        """Start the live dashboard."""
        print("🎨 Starting Live Dashboard...")
        print(f"📡 Connecting to API: {API_BASE}")
        print("🔄 Updating every 1 second")
        print("\n⚠️  Make sure the backend is running:")
        print("   cd backend && uvicorn app.main:app --reload\n")
        
        # Animation
        anim = animation.FuncAnimation(
            self.fig,
            self.update,
            interval=1000,  # Update every 1 second
            blit=False,
            cache_frame_data=False
        )
        
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    dashboard = LiveDashboard()
    dashboard.run()

