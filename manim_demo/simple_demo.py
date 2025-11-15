"""
Advanced Traffic Demo with Realistic Paths and AI Communication
Cars take turns, follow city-like routes, and AI mode shows communication
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Polygon
import math

class TrafficDemo:
    def __init__(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(18, 9))
        self.fig.suptitle('Traffic Coordination: CHAOS vs AI Communication', 
                         fontsize=22, fontweight='bold', y=0.97)
        
        # Create road network with intersections
        self.road_network = self.create_road_network()
        
        # Define realistic routes (point A to point B with turns)
        self.routes = self.define_routes()
        
        # Initialize cars with paths
        self.chaos_cars = self.init_chaos_cars()
        self.ai_cars = self.init_ai_cars()
        
        self.frame = 0
        self.collision_shown = False
        self.ai_communication_active = False
        
    def create_road_network(self):
        """Create a city-like road network with intersections."""
        network = {
            'intersections': [
                (-2, -2), (-2, 0), (-2, 2),  # Left column
                (0, -2), (0, 0), (0, 2),     # Middle column
                (2, -2), (2, 0), (2, 2),     # Right column
            ],
            'roads': []
        }
        
        # Horizontal roads
        for y in [-2, 0, 2]:
            network['roads'].append(((-2.5, y), (2.5, y)))
        
        # Vertical roads
        for x in [-2, 0, 2]:
            network['roads'].append(((x, -2.5), (x, 2.5)))
        
        return network
    
    def define_routes(self):
        """Define realistic routes with turns from point A to point B."""
        return [
            # Route 1: Bottom-left to top-right (2 turns)
            {
                'start': (-2.5, -2.5),
                'waypoints': [(-2, -2), (0, -2), (0, 0), (2, 0), (2, 2)],
                'end': (2.5, 2.5),
                'color': 'red',
                'label': '1'
            },
            # Route 2: Top-left to bottom-right (2 turns)
            {
                'start': (-2.5, 2.5),
                'waypoints': [(-2, 2), (0, 2), (0, 0), (2, 0), (2, -2)],
                'end': (2.5, -2.5),
                'color': 'blue',
                'label': '2'
            },
            # Route 3: Right to left through center (1 turn)
            {
                'start': (2.5, 0),
                'waypoints': [(2, 0), (0, 0), (-2, 0)],
                'end': (-2.5, 0),
                'color': 'green',
                'label': '3'
            },
            # Route 4: Top to bottom with turn (1 turn)
            {
                'start': (0, 2.5),
                'waypoints': [(0, 2), (0, 0), (2, 0), (2, -2)],
                'end': (2.5, -2.5),
                'color': 'orange',
                'label': '4'
            },
            # Route 5: Bottom to top (straight)
            {
                'start': (-2, -2.5),
                'waypoints': [(-2, -2), (-2, 0), (-2, 2)],
                'end': (-2, 2.5),
                'color': 'purple',
                'label': '5'
            },
        ]
    
    def init_chaos_cars(self):
        """Initialize cars for chaos mode."""
        cars = []
        for route in self.routes[:4]:  # Use first 4 routes
            car = {
                'route': route,
                'current_waypoint': 0,
                'x': route['start'][0],
                'y': route['start'][1],
                'color': route['color'],
                'label': route['label'],
                'speed': 0.7 + np.random.random() * 0.4,  # Random speed
                'path_progress': 0.0,
            }
            cars.append(car)
        return cars
    
    def init_ai_cars(self):
        """Initialize cars for AI mode with communication data."""
        cars = []
        for i, route in enumerate(self.routes[:4]):
            car = {
                'route': route,
                'current_waypoint': 0,
                'x': route['start'][0],
                'y': route['start'][1],
                'color': route['color'],
                'label': route['label'],
                'speed': 1.0,
                'path_progress': 0.0,
                'delay': i * 20,  # Staggered starts
                'thinking': False,
                'communicating_with': [],
                'status': 'normal',  # 'normal', 'slowing', 'stopped', 'accelerating'
                'message': '',
            }
            cars.append(car)
        return cars
    
    def setup_axes(self):
        """Setup the two side-by-side plots."""
        for ax, title in [(self.ax1, 'CHAOS MODE'), (self.ax2, 'AI COORDINATED MODE')]:
            ax.set_xlim(-3, 3)
            ax.set_ylim(-3, 3)
            ax.set_aspect('equal')
            ax.axis('off')
            ax.set_title(title, fontsize=18, fontweight='bold', 
                        color='red' if 'CHAOS' in title else 'green', pad=15)
            self.draw_roads(ax)
    
    def draw_roads(self, ax):
        """Draw the road network."""
        # Draw roads
        for road in self.road_network['roads']:
            ax.plot([road[0][0], road[1][0]], [road[0][1], road[1][1]], 
                   'k-', linewidth=10, color='gray', alpha=0.4, zorder=0)
        
        # Draw intersections
        for intersection in self.road_network['intersections']:
            # Intersection square
            square = Rectangle((intersection[0] - 0.15, intersection[1] - 0.15), 
                             0.3, 0.3, facecolor='yellow', alpha=0.3, zorder=0)
            ax.add_patch(square)
            # Center dot
            circle = Circle(intersection, 0.08, color='yellow', alpha=0.6, zorder=1)
            ax.add_patch(circle)
    
    def get_path_segment(self, car):
        """Get current path segment for a car."""
        route = car['route']
        waypoints = [route['start']] + route['waypoints'] + [route['end']]
        
        if car['current_waypoint'] >= len(waypoints) - 1:
            return None
        
        start = waypoints[car['current_waypoint']]
        end = waypoints[car['current_waypoint'] + 1]
        return (start, end)
    
    def update_car_position(self, car, is_ai=False):
        """Update car position along its path."""
        segment = self.get_path_segment(car)
        if segment is None:
            return False  # Car reached destination
        
        start, end = segment
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dist = np.sqrt(dx**2 + dy**2)
        
        if dist < 0.01:
            car['current_waypoint'] += 1
            return True
        
        # Move along segment
        speed_mult = car['speed']
        if is_ai:
            # AI can adjust speed based on status
            if car['status'] == 'stopped':
                speed_mult = 0
            elif car['status'] == 'slowing':
                speed_mult = 0.3
            elif car['status'] == 'accelerating':
                speed_mult = 1.5
        
        move_dist = 0.03 * speed_mult
        progress = move_dist / dist
        
        car['x'] += dx * progress
        car['y'] += dy * progress
        
        # Check if reached waypoint
        dist_to_end = np.sqrt((end[0] - car['x'])**2 + (end[1] - car['y'])**2)
        if dist_to_end < 0.15:
            car['current_waypoint'] += 1
        
        return True
    
    def find_nearby_cars(self, car, all_cars, threshold=1.5):
        """Find cars within communication range."""
        nearby = []
        for other in all_cars:
            if other == car:
                continue
            dist = np.sqrt((car['x'] - other['x'])**2 + (car['y'] - other['y'])**2)
            if dist < threshold:
                nearby.append((other, dist))
        return nearby
    
    def ai_coordinate(self, cars):
        """AI coordination logic - cars communicate and adjust."""
        self.frame
        # Check for potential conflicts at intersections
        for car in cars:
            if car['delay'] > self.frame:
                continue
            
            # Check if near intersection
            near_intersection = False
            for intersection in self.road_network['intersections']:
                dist = np.sqrt((car['x'] - intersection[0])**2 + (car['y'] - intersection[1])**2)
                if dist < 0.8:
                    near_intersection = True
                    break
            
            if near_intersection:
                # Find nearby cars
                nearby = self.find_nearby_cars(car, cars, threshold=1.2)
                
                if nearby:
                    car['thinking'] = True
                    car['communicating_with'] = [other for other, _ in nearby]
                    
                    # Determine priority (first come, first served)
                    my_arrival = self.frame - car['delay']
                    should_wait = False
                    
                    for other, dist in nearby:
                        other_arrival = self.frame - other['delay']
                        if other_arrival < my_arrival and dist < 0.6:
                            should_wait = True
                            break
                    
                    if should_wait:
                        car['status'] = 'stopped'
                        car['message'] = 'WAIT'
                    else:
                        car['status'] = 'normal'
                        car['message'] = 'GO'
                else:
                    car['thinking'] = False
                    car['status'] = 'normal'
                    car['message'] = ''
            else:
                car['thinking'] = False
                car['status'] = 'normal'
                car['message'] = ''
                if car['status'] != 'stopped':
                    car['status'] = 'normal'
    
    def draw_car(self, ax, car, is_ai=False):
        """Draw a car with optional AI indicators."""
        # Car body (rotated based on direction)
        segment = self.get_path_segment(car)
        if segment:
            start, end = segment
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            angle = math.atan2(dy, dx)
        else:
            angle = 0
        
        # Car rectangle (rotated)
        car_length = 0.25
        car_width = 0.15
        corners = np.array([
            [-car_length/2, -car_width/2],
            [car_length/2, -car_width/2],
            [car_length/2, car_width/2],
            [-car_length/2, car_width/2]
        ])
        
        # Rotate
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        rotation = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        corners_rotated = corners @ rotation.T
        corners_rotated[:, 0] += car['x']
        corners_rotated[:, 1] += car['y']
        
        car_poly = Polygon(corners_rotated, facecolor=car['color'], 
                          edgecolor='white', linewidth=1.5, zorder=10)
        ax.add_patch(car_poly)
        
        # Label
        ax.text(car['x'], car['y'], car['label'], 
               ha='center', va='center', fontsize=9, 
               color='white', fontweight='bold', zorder=11)
        
        # AI-specific indicators
        if is_ai:
            # Thinking indicator
            if car.get('thinking', False):
                # Animated dots above car
                dot_frame = (self.frame // 5) % 3
                for i in range(3):
                    alpha = 0.3 if i != dot_frame else 1.0
                    circle = Circle((car['x'] + (i - 1) * 0.15, car['y'] + 0.4), 
                                  0.05, color='cyan', alpha=alpha, zorder=12)
                    ax.add_patch(circle)
                
                # "Thinking..." text
                ax.text(car['x'], car['y'] + 0.6, 'Thinking...', 
                       ha='center', va='bottom', fontsize=8, 
                       color='cyan', style='italic', zorder=12)
            
            # Status indicator
            if car.get('status') == 'stopped':
                # Red stop indicator
                stop_circle = Circle((car['x'], car['y'] + 0.3), 0.08, 
                                    color='red', alpha=0.8, zorder=12)
                ax.add_patch(stop_circle)
                ax.text(car['x'], car['y'] + 0.3, '⏸', ha='center', va='center',
                       fontsize=10, zorder=13)
            elif car.get('status') == 'slowing':
                # Yellow slow indicator
                slow_circle = Circle((car['x'], car['y'] + 0.3), 0.08,
                                    color='yellow', alpha=0.8, zorder=12)
                ax.add_patch(slow_circle)
            elif car.get('status') == 'accelerating':
                # Green go indicator
                go_circle = Circle((car['x'], car['y'] + 0.3), 0.08,
                                  color='green', alpha=0.8, zorder=12)
                ax.add_patch(go_circle)
                ax.text(car['x'], car['y'] + 0.3, '▶', ha='center', va='center',
                       fontsize=8, zorder=13)
            
            # Message text
            if car.get('message'):
                ax.text(car['x'], car['y'] - 0.4, car['message'], 
                       ha='center', va='top', fontsize=9, 
                       color='lime', fontweight='bold', 
                       bbox=dict(boxstyle='round', facecolor='black', alpha=0.7),
                       zorder=12)
    
    def draw_ai_communication(self, ax, cars):
        """Draw communication lines and data flow between AI cars."""
        for car in cars:
            if car['delay'] > self.frame:
                continue
            
            if car.get('communicating_with'):
                for other_car in car['communicating_with']:
                    if other_car['delay'] > self.frame:
                        continue
                    
                    # Draw communication line
                    line = FancyArrowPatch(
                        (car['x'], car['y']), (other_car['x'], other_car['y']),
                        arrowstyle='->', color='cyan', alpha=0.6,
                        linewidth=2, linestyle='--', zorder=5
                    )
                    ax.add_patch(line)
                    
                    # Data packet indicator (animated)
                    mid_x = (car['x'] + other_car['x']) / 2
                    mid_y = (car['y'] + other_car['y']) / 2
                    
                    # Animated dot moving along line
                    progress = (self.frame % 30) / 30.0
                    packet_x = car['x'] + (other_car['x'] - car['x']) * progress
                    packet_y = car['y'] + (other_car['y'] - car['y']) * progress
                    
                    packet = Circle((packet_x, packet_y), 0.06, 
                                   color='cyan', alpha=0.9, zorder=6)
                    ax.add_patch(packet)
    
    def check_collisions(self, cars):
        """Check for collisions between cars."""
        for i, car1 in enumerate(cars):
            for car2 in cars[i+1:]:
                dist = np.sqrt((car1['x'] - car2['x'])**2 + (car1['y'] - car2['y'])**2)
                if dist < 0.25:  # Collision threshold
                    return (car1, car2)
        return None
    
    def animate(self, frame):
        """Animation function called for each frame."""
        self.frame = frame
        
        # Clear axes
        self.ax1.clear()
        self.ax2.clear()
        self.setup_axes()
        
        # CHAOS MODE (left)
        collision = None
        for car in self.chaos_cars:
            if self.update_car_position(car, is_ai=False):
                self.draw_car(self.ax1, car, is_ai=False)
        
        # Check collisions
        collision = self.check_collisions(self.chaos_cars)
        if collision and not self.collision_shown:
            car1, car2 = collision
            self.ax1.text(0, 2.5, '💥 COLLISION!', ha='center', va='center',
                         fontsize=28, color='red', fontweight='bold', zorder=20)
            collision_circle = Circle(((car1['x'] + car2['x'])/2, 
                                      (car1['y'] + car2['y'])/2), 
                                    0.4, color='red', alpha=0.5, zorder=19)
            self.ax1.add_patch(collision_circle)
            self.collision_shown = True
        
        # AI MODE (right)
        # Coordinate cars
        self.ai_coordinate(self.ai_cars)
        
        # Update and draw AI cars
        for car in self.ai_cars:
            if car['delay'] <= self.frame:
                if self.update_car_position(car, is_ai=True):
                    self.draw_car(self.ax2, car, is_ai=True)
        
        # Draw communication lines
        self.draw_ai_communication(self.ax2, self.ai_cars)
        
        # Show AI status
        if self.frame > 30 and not self.ai_communication_active:
            self.ai_communication_active = True
            self.ax2.text(0, 2.6, 'AI: Active Communication', ha='center',
                         fontsize=14, color='green', style='italic', 
                         bbox=dict(boxstyle='round', facecolor='black', alpha=0.7),
                         zorder=20)
        
        # Show success for AI mode
        if self.frame > 180:
            all_done = all(car['current_waypoint'] >= len(car['route']['waypoints']) + 1 
                          for car in self.ai_cars if car['delay'] <= self.frame)
            if all_done:
                self.ax2.text(0, -2.6, '✓ All Cars Coordinated Successfully', 
                             ha='center', fontsize=16, color='green', 
                             fontweight='bold', zorder=20)
        
        plt.tight_layout()
        return []
    
    def run(self):
        """Run the animation."""
        anim = animation.FuncAnimation(self.fig, self.animate, frames=250, 
                                      interval=40, blit=False, repeat=False)
        plt.tight_layout()
        plt.show()
        return anim


if __name__ == '__main__':
    print("🚗 Starting Advanced Traffic Coordination Demo...")
    print("Features:")
    print("  • Realistic city paths with turns")
    print("  • AI communication visualization")
    print("  • Thinking indicators")
    print("  • Data transmission lines")
    print("  • Speed coordination")
    print("\nClose the window when done.")
    
    demo = TrafficDemo()
    anim = demo.run()
    
    try:
        plt.show(block=True)
    except KeyboardInterrupt:
        print("\nDemo stopped.")
