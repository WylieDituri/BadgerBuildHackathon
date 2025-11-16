#!/usr/bin/env python3
"""
Side-by-side comparison demo: NO AI vs WITH AI
Shows realistic car physics and collision avoidance.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation
import numpy as np
import random
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# Color scheme
COLOR_BG = '#0f1419'
COLOR_ROAD = '#2a3f5f'
COLOR_CAR = '#3b82f6'
COLOR_EMERGENCY = '#f59e0b'
COLOR_COLLISION = '#ef4444'
COLOR_WARNING = '#fbbf24'
COLOR_TEXT = '#e5e7eb'


@dataclass
class Car:
    """Car with realistic physics and lane awareness."""
    id: str
    x: float
    y: float
    vx: float = 0.0  # velocity x
    vy: float = 0.0  # velocity y
    heading: float = 0.0  # degrees
    speed: float = 0.0  # current speed
    target_speed: float = 0.3  # desired speed
    max_speed: float = 0.4
    acceleration: float = 0.02
    is_emergency: bool = False
    crashed: bool = False
    collision_time: float = 0.0
    stopped_by_ai: bool = False
    yielding: bool = False
    route: List[Tuple[float, float]] = field(default_factory=list)  # Path through intersections
    current_waypoint: int = 0  # Index in route
    at_intersection: bool = False
    turn_decision_made: bool = False
    
    def update_physics(self, dt: float = 1.0):
        """Update position with realistic physics and steering."""
        if self.crashed:
            # Crashed cars don't move
            self.speed = 0
            self.vx = 0
            self.vy = 0
            return
        
        # Follow route if we have one
        if self.route and self.current_waypoint < len(self.route):
            target_x, target_y = self.route[self.current_waypoint]
            dx = target_x - self.x
            dy = target_y - self.y
            dist_to_waypoint = math.sqrt(dx**2 + dy**2)
            
            # Reached waypoint - move to next
            if dist_to_waypoint < 0.5:
                self.current_waypoint += 1
                if self.current_waypoint < len(self.route):
                    target_x, target_y = self.route[self.current_waypoint]
                    dx = target_x - self.x
                    dy = target_y - self.y
            
            # Update heading to face target (smooth turning)
            target_heading = math.degrees(math.atan2(dy, dx))
            heading_diff = (target_heading - self.heading + 180) % 360 - 180
            
            # Limit turn rate for realism
            max_turn_rate = 5.0  # degrees per frame
            if abs(heading_diff) > max_turn_rate:
                self.heading += max_turn_rate if heading_diff > 0 else -max_turn_rate
            else:
                self.heading = target_heading
        
        # Speed control
        if self.stopped_by_ai or self.yielding:
            # Slow down quickly
            self.speed = max(0, self.speed - self.acceleration * 2)
        else:
            # Accelerate toward target speed
            if self.speed < self.target_speed:
                self.speed = min(self.target_speed, self.speed + self.acceleration)
            elif self.speed > self.target_speed:
                self.speed = max(self.target_speed, self.speed - self.acceleration)
        
        # Update velocity based on heading
        rad = math.radians(self.heading)
        self.vx = self.speed * math.cos(rad)
        self.vy = self.speed * math.sin(rad)
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
    
    def distance_to(self, other: 'Car') -> float:
        """Calculate distance to another car."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def in_opposite_lanes(self, other: 'Car') -> bool:
        """Check if two cars are in opposite lanes (won't collide)."""
        # Calculate direction vectors
        dir1_x = math.cos(math.radians(self.heading))
        dir1_y = math.sin(math.radians(self.heading))
        dir2_x = math.cos(math.radians(other.heading))
        dir2_y = math.sin(math.radians(other.heading))
        
        # Dot product: 1 = same direction, -1 = opposite, 0 = perpendicular
        dot_product = dir1_x * dir2_x + dir1_y * dir2_y
        
        # If dot < -0.7, they're going opposite directions (different lanes)
        # Also check if they're on a road (not at intersection)
        on_same_road = False
        
        # Check if both on horizontal road (around y=-3, 0, or 3)
        for road_y in [-3, 0, 3]:
            if abs(self.y - road_y) < 0.8 and abs(other.y - road_y) < 0.8:
                on_same_road = True
                break
        
        # Check if both on vertical road (around x=-3, 0, or 3)
        for road_x in [-3, 0, 3]:
            if abs(self.x - road_x) < 0.8 and abs(other.x - road_x) < 0.8:
                on_same_road = True
                break
        
        # Opposite lanes if: same road AND opposite directions
        return on_same_road and dot_product < -0.7
    
    def will_collide_with(self, other: 'Car', time_horizon: float = 3.0) -> Tuple[bool, float]:
        """Predict if this car will collide with another car."""
        if self.crashed or other.crashed:
            return False, float('inf')
        
        # Don't collide if in opposite lanes
        if self.in_opposite_lanes(other):
            return False, float('inf')
        
        # Simple collision prediction: extrapolate positions
        future_x1 = self.x + self.vx * time_horizon
        future_y1 = self.y + self.vy * time_horizon
        future_x2 = other.x + other.vx * time_horizon
        future_y2 = other.y + other.vy * time_horizon
        
        future_dist = math.sqrt((future_x1 - future_x2)**2 + (future_y1 - future_y2)**2)
        
        # Check closest point of approach
        min_dist = float('inf')
        collision_time = float('inf')
        
        for t in np.linspace(0, time_horizon, 20):
            px1 = self.x + self.vx * t
            py1 = self.y + self.vy * t
            px2 = other.x + other.vx * t
            py2 = other.y + other.vy * t
            dist = math.sqrt((px1 - px2)**2 + (py1 - py2)**2)
            
            if dist < min_dist:
                min_dist = dist
                collision_time = t
        
        collision_threshold = 0.3  # Collision if closer than this
        return min_dist < collision_threshold, collision_time


class TrafficSimulation:
    """Simulates traffic with realistic physics."""
    
    def __init__(self, mode: str = "chaos"):
        """
        mode: "chaos" (no AI) or "ai" (with coordination)
        """
        self.mode = mode
        self.cars: List[Car] = []
        self.time = 0.0
        self.collision_count = 0
        self.spawn_timer = 0.0
        self.spawn_interval = 3.0  # seconds
        self.car_counter = 0
        
        # Spawn zones (edges of map)
        self.spawn_zones = [
            {"x": 0, "y": 4, "heading": 270},     # Top, heading down
            {"x": 0, "y": -4, "heading": 90},     # Bottom, heading up
            {"x": 4, "y": 0, "heading": 180},     # Right, heading left
            {"x": -4, "y": 0, "heading": 0},      # Left, heading right
        ]
    
    def _generate_route(self, start_x: float, start_y: float, start_heading: float) -> List[Tuple[float, float]]:
        """Generate a random route through the city with turns."""
        route = [(start_x, start_y)]
        
        # Intersections
        intersections = [(-3, -3), (-3, 0), (-3, 3),
                        (0, -3), (0, 0), (0, 3),
                        (3, -3), (3, 0), (3, 3)]
        
        # Find nearest intersection to start
        current = min(intersections, 
                     key=lambda p: math.sqrt((p[0]-start_x)**2 + (p[1]-start_y)**2))
        route.append(current)
        
        # Navigate through 2-4 intersections with random turns
        num_waypoints = random.randint(2, 4)
        for _ in range(num_waypoints):
            # Find adjacent intersections
            neighbors = []
            for inter in intersections:
                if inter == current:
                    continue
                # Adjacent if one coordinate matches and other differs by 3
                if (abs(inter[0] - current[0]) == 3 and inter[1] == current[1]) or \
                   (abs(inter[1] - current[1]) == 3 and inter[0] == current[0]):
                    neighbors.append(inter)
            
            if neighbors:
                current = random.choice(neighbors)
                route.append(current)
        
        # Exit the map in the direction we're heading
        last_x, last_y = route[-1]
        # Determine exit based on position
        if abs(last_x) > abs(last_y):
            # Exit horizontally
            exit_x = 6 if last_x > 0 else -6
            exit_y = last_y
        else:
            # Exit vertically
            exit_x = last_x
            exit_y = 6 if last_y > 0 else -6
        route.append((exit_x, exit_y))
        
        return route
    
    def spawn_car(self):
        """Spawn a new car with a random route."""
        if len(self.cars) >= 15:  # Max cars to avoid overcrowding
            return
        
        self.car_counter += 1
        zone = random.choice(self.spawn_zones)
        
        # Add small random offset
        x = zone["x"] + random.uniform(-0.3, 0.3)
        y = zone["y"] + random.uniform(-0.3, 0.3)
        
        is_emergency = random.random() < 0.15  # 15% emergency vehicles
        
        # Generate route
        route = self._generate_route(x, y, zone["heading"])
        
        car = Car(
            id=f"C{self.car_counter:02d}",
            x=x,
            y=y,
            heading=zone["heading"],
            target_speed=0.4 if is_emergency else 0.3,
            is_emergency=is_emergency,
            route=route
        )
        
        self.cars.append(car)
    
    def check_collisions(self):
        """Check for actual collisions between cars (lane-aware)."""
        for i, car1 in enumerate(self.cars):
            if car1.crashed:
                continue
            for car2 in self.cars[i+1:]:
                if car2.crashed:
                    continue
                
                # Don't collide if in opposite lanes
                if car1.in_opposite_lanes(car2):
                    continue
                
                dist = car1.distance_to(car2)
                if dist < 0.35:  # Collision! (slightly larger for realism)
                    car1.crashed = True
                    car2.crashed = True
                    car1.collision_time = self.time
                    car2.collision_time = self.time
                    self.collision_count += 1
    
    def ai_coordination(self):
        """AI coordination to prevent collisions (only in AI mode)."""
        if self.mode != "ai":
            return
        
        # Reset AI flags
        for car in self.cars:
            car.stopped_by_ai = False
            car.yielding = False
        
        # Check for potential collisions and coordinate
        for i, car1 in enumerate(self.cars):
            if car1.crashed:
                continue
            
            for car2 in self.cars[i+1:]:
                if car2.crashed:
                    continue
                
                will_collide, time_to_collision = car1.will_collide_with(car2, time_horizon=3.0)
                
                if will_collide and time_to_collision < 2.5:
                    # Collision predicted! Coordinate
                    # Priority: emergency vehicles > regular cars
                    # If same priority, the one further from center yields
                    
                    car1_priority = 10 if car1.is_emergency else 1
                    car2_priority = 10 if car2.is_emergency else 1
                    
                    if car1_priority > car2_priority:
                        car2.yielding = True
                    elif car2_priority > car1_priority:
                        car1.yielding = True
                    else:
                        # Same priority - car closer to center has priority
                        dist1 = math.sqrt(car1.x**2 + car1.y**2)
                        dist2 = math.sqrt(car2.x**2 + car2.y**2)
                        if dist1 < dist2:
                            car2.yielding = True
                        else:
                            car1.yielding = True
    
    def remove_offscreen_cars(self):
        """Remove cars that left the map."""
        self.cars = [car for car in self.cars 
                    if abs(car.x) < 6 and abs(car.y) < 6]
    
    def update(self, dt: float):
        """Update simulation."""
        self.time += dt
        
        # Spawn new cars
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_car()
            self.spawn_timer = 0.0
        
        # AI coordination (only if mode is "ai")
        self.ai_coordination()
        
        # Update all cars
        for car in self.cars:
            car.update_physics(dt)
        
        # Check collisions (in chaos mode, or to detect failures in AI mode)
        self.check_collisions()
        
        # Remove offscreen cars
        self.remove_offscreen_cars()


class ComparisonDemo:
    """Side-by-side comparison visualization."""
    
    def __init__(self):
        # Create figure with two subplots
        self.fig = plt.figure(figsize=(16, 8), facecolor=COLOR_BG)
        self.fig.suptitle('TRAFFIC INTELLIGENCE: CHAOS vs AI COORDINATION', 
                         fontsize=20, color=COLOR_TEXT, fontweight='bold', y=0.98)
        
        # Left: Chaos mode
        self.ax_chaos = plt.subplot(1, 2, 1)
        self.ax_chaos.set_title('❌ NO AI - CHAOS MODE', fontsize=16, 
                               color='#ef4444', fontweight='bold', pad=20)
        self._setup_axis(self.ax_chaos)
        
        # Right: AI mode
        self.ax_ai = plt.subplot(1, 2, 2)
        self.ax_ai.set_title('✅ WITH AI - COORDINATED', fontsize=16, 
                            color='#10b981', fontweight='bold', pad=20)
        self._setup_axis(self.ax_ai)
        
        # Create simulations
        self.sim_chaos = TrafficSimulation(mode="chaos")
        self.sim_ai = TrafficSimulation(mode="ai")
        
        # Stats text
        self.stats_chaos = None
        self.stats_ai = None
        
        plt.tight_layout()
    
    def _setup_axis(self, ax):
        """Setup axis for traffic visualization with wider roads."""
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.set_aspect('equal')
        ax.set_facecolor(COLOR_BG)
        ax.tick_params(colors=COLOR_TEXT)
        
        # Draw road grid - MUCH WIDER for lane visualization
        for pos in [-3, 0, 3]:
            # Vertical roads (wider)
            ax.plot([pos, pos], [-4.5, 4.5], color=COLOR_ROAD, linewidth=24, alpha=0.6, zorder=1)
            # Horizontal roads (wider)
            ax.plot([-4.5, 4.5], [pos, pos], color=COLOR_ROAD, linewidth=24, alpha=0.6, zorder=1)
        
        # Draw lane dividers (dashed lines in middle of roads)
        for pos in [-3, 0, 3]:
            # Vertical lane dividers
            ax.plot([pos, pos], [-4.5, 4.5], color='#ffeb3b', linewidth=1, 
                   alpha=0.3, linestyle='--', zorder=2)
            # Horizontal lane dividers
            ax.plot([-4.5, 4.5], [pos, pos], color='#ffeb3b', linewidth=1, 
                   alpha=0.3, linestyle='--', zorder=2)
        
        # Draw intersections (larger)
        for x in [-3, 0, 3]:
            for y in [-3, 0, 3]:
                circle = mpatches.Circle((x, y), 0.6, color='yellow', alpha=0.15, zorder=2)
                ax.add_patch(circle)
        
        # Draw buildings (adjusted positions for wider roads)
        for x in [-4.5, -1.2, 1.2, 4.2]:
            for y in [1.2, -1.8, -4.2]:
                if abs(x) > 3.5 or abs(y) > 3.5:  # Only corners
                    rect = mpatches.Rectangle((x, y), 0.8, 0.8, 
                                             facecolor='#1a1a2e', 
                                             edgecolor='#444', 
                                             linewidth=1, zorder=1)
                    ax.add_patch(rect)
    
    def _draw_cars(self, ax, sim: TrafficSimulation):
        """Draw all cars for a simulation."""
        # Draw routes as faint lines (only for active cars, only first few waypoints)
        for car in sim.cars:
            if not car.crashed and car.route and car.current_waypoint < len(car.route):
                # Draw next 2-3 waypoints
                visible_route = car.route[car.current_waypoint:min(car.current_waypoint+3, len(car.route))]
                if len(visible_route) > 1:
                    xs = [car.x] + [p[0] for p in visible_route]
                    ys = [car.y] + [p[1] for p in visible_route]
                    color = COLOR_EMERGENCY if car.is_emergency else COLOR_CAR
                    ax.plot(xs, ys, color=color, alpha=0.1, linewidth=1, linestyle=':', zorder=3)
        
        # Draw cars
        for car in sim.cars:
            if car.crashed:
                # Crashed car - red with X
                circle = mpatches.Circle((car.x, car.y), 0.2, 
                                        color=COLOR_COLLISION, alpha=0.8, 
                                        edgecolor='white', linewidth=2, zorder=10)
                ax.add_patch(circle)
                ax.text(car.x, car.y, '💥', ha='center', va='center', 
                       fontsize=12, zorder=11)
            elif car.yielding:
                # Yielding car - yellow (slowing down)
                circle = mpatches.Circle((car.x, car.y), 0.18, 
                                        color=COLOR_WARNING, alpha=0.9, 
                                        edgecolor='white', linewidth=1.5, zorder=10)
                ax.add_patch(circle)
                ax.text(car.x, car.y, car.id, ha='center', va='center',
                       fontsize=7, color='black', fontweight='bold', zorder=11)
            elif car.is_emergency:
                # Emergency vehicle
                circle = mpatches.Circle((car.x, car.y), 0.18, 
                                        color=COLOR_EMERGENCY, alpha=0.9, 
                                        edgecolor='white', linewidth=1.5, zorder=10)
                ax.add_patch(circle)
                ax.text(car.x, car.y + 0.35, '🚨', ha='center', va='center',
                       fontsize=10, zorder=11)
            else:
                # Normal car
                circle = mpatches.Circle((car.x, car.y), 0.18, 
                                        color=COLOR_CAR, alpha=0.9, 
                                        edgecolor='white', linewidth=1.5, zorder=10)
                ax.add_patch(circle)
                ax.text(car.x, car.y, car.id, ha='center', va='center',
                       fontsize=7, color='white', fontweight='bold', zorder=11)
            
            # Draw velocity arrow
            if not car.crashed and (car.vx != 0 or car.vy != 0):
                ax.arrow(car.x, car.y, car.vx*0.8, car.vy*0.8,
                        head_width=0.15, head_length=0.1, 
                        fc='white', ec='white', alpha=0.6, zorder=9, linewidth=1)
    
    def update(self, frame):
        """Update animation frame."""
        # Update simulations
        self.sim_chaos.update(dt=0.2)
        self.sim_ai.update(dt=0.2)
        
        # Clear axes
        self.ax_chaos.clear()
        self.ax_ai.clear()
        
        # Reset axes
        self._setup_axis(self.ax_chaos)
        self._setup_axis(self.ax_ai)
        
        # Redraw titles
        self.ax_chaos.set_title('❌ NO AI - CHAOS MODE', fontsize=16, 
                               color='#ef4444', fontweight='bold', pad=20)
        self.ax_ai.set_title('✅ WITH AI - COORDINATED', fontsize=16, 
                            color='#10b981', fontweight='bold', pad=20)
        
        # Draw cars
        self._draw_cars(self.ax_chaos, self.sim_chaos)
        self._draw_cars(self.ax_ai, self.sim_ai)
        
        # Draw stats
        chaos_stats = (
            f'⏱️  Time: {self.sim_chaos.time:.1f}s\n'
            f'🚗 Active: {len([c for c in self.sim_chaos.cars if not c.crashed])}\n'
            f'💥 Collisions: {self.sim_chaos.collision_count}\n'
            f'📊 Total Spawned: {self.sim_chaos.car_counter}'
        )
        
        ai_stats = (
            f'⏱️  Time: {self.sim_ai.time:.1f}s\n'
            f'🚗 Active: {len([c for c in self.sim_ai.cars if not c.crashed])}\n'
            f'💥 Collisions: {self.sim_ai.collision_count}\n'
            f'🛡️  Prevented: {self.sim_ai.car_counter - self.sim_ai.collision_count}\n'
            f'📊 Total Spawned: {self.sim_ai.car_counter}'
        )
        
        self.ax_chaos.text(-4.8, 4.5, chaos_stats, fontsize=10, 
                          color=COLOR_TEXT, va='top', 
                          bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        self.ax_ai.text(-4.8, 4.5, ai_stats, fontsize=10, 
                       color=COLOR_TEXT, va='top',
                       bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        # Add legend on AI side
        legend_text = (
            '🚗 Normal Car\n'
            '🚨 Emergency\n'
            '🟡 Yielding (AI)\n'
            '💥 Crashed\n'
            '---\n'
            'Features:\n'
            '• Lane awareness\n'
            '• Random turning\n'
            '• Intersection logic'
        )
        self.ax_ai.text(4.8, 4.7, legend_text, fontsize=8, 
                       color=COLOR_TEXT, va='top', ha='right',
                       bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
    
    def run(self):
        """Run the comparison demo."""
        print("🎬 Starting Enhanced Comparison Demo...")
        print("   Left: NO AI (chaos mode)")
        print("   Right: WITH AI (coordinated)")
        print("\n✨ New Features:")
        print("   • Lane awareness (opposite traffic won't collide)")
        print("   • Cars turn at intersections randomly")
        print("   • Wider roads with lane markings")
        print("   • Realistic steering and physics")
        print("\n⏱️  Running simulation...")
        print("   Watch the collision counters!\n")
        
        anim = FuncAnimation(self.fig, self.update, interval=200, cache_frame_data=False)
        plt.show()
        
        # Print final stats
        print("\n" + "="*60)
        print("📊 FINAL RESULTS:")
        print("="*60)
        print(f"\n❌ NO AI (Chaos):")
        print(f"   Total Spawned: {self.sim_chaos.car_counter}")
        print(f"   Collisions: {self.sim_chaos.collision_count}")
        print(f"   Collision Rate: {self.sim_chaos.collision_count/max(self.sim_chaos.car_counter,1)*100:.1f}%")
        
        print(f"\n✅ WITH AI (Coordinated):")
        print(f"   Total Spawned: {self.sim_ai.car_counter}")
        print(f"   Collisions: {self.sim_ai.collision_count}")
        print(f"   Collision Rate: {self.sim_ai.collision_count/max(self.sim_ai.car_counter,1)*100:.1f}%")
        print(f"   Collisions Prevented: {self.sim_chaos.collision_count - self.sim_ai.collision_count}")
        
        improvement = (1 - self.sim_ai.collision_count/max(self.sim_chaos.collision_count, 1)) * 100
        print(f"\n🎯 AI Improvement: {improvement:.1f}% reduction in collisions!")
        print("="*60)


if __name__ == "__main__":
    demo = ComparisonDemo()
    demo.run()

