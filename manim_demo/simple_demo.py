"""
Professional Traffic Demo with Detailed City Map
Shows USER-controlled traffic first, then AI-coordinated traffic with statistics
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Polygon, Wedge
import math
import time

class TrafficDemo:
    def __init__(self):
        self.fig, self.ax = plt.subplots(1, 1, figsize=(16, 12))
        self.fig.patch.set_facecolor('#2b2b2b')
        
        # Simulation state
        self.mode = 'user'  # 'user', 'stats_user', 'ai', 'stats_ai', 'comparison', 'complete'
        self.frame = 0
        self.mode_frame = 0
        
        # Statistics
        self.user_collisions = 0
        self.user_start_time = 0
        self.user_end_time = 0
        self.ai_collisions = 0
        self.ai_start_time = 0
        self.ai_end_time = 0
        
        # Create detailed road network
        self.road_network = self.create_city_map()
        
        # Define routes
        self.routes = self.define_city_routes()
        
        # Initialize cars
        self.user_cars = self.init_user_cars()
        self.ai_cars = self.init_ai_cars()
        
        self.collision_pairs = set()
        
    def create_city_map(self):
        """Create a detailed city map with roads, buildings, and intersections."""
        network = {
            'intersections': [
                (-2.5, -2.5), (-2.5, 0), (-2.5, 2.5),  # Left column
                (0, -2.5), (0, 0), (0, 2.5),           # Middle column
                (2.5, -2.5), (2.5, 0), (2.5, 2.5),     # Right column
            ],
            'roads': [
                # Horizontal roads
                ((-3.5, -2.5), (3.5, -2.5)),
                ((-3.5, 0), (3.5, 0)),
                ((-3.5, 2.5), (3.5, 2.5)),
                # Vertical roads
                ((-2.5, -3.5), (-2.5, 3.5)),
                ((0, -3.5), (0, 3.5)),
                ((2.5, -3.5), (2.5, 3.5)),
            ],
            'buildings': [
                # Top row
                ((-3.3, 0.3), 1.4, 1.9),
                ((-1.0, 0.3), 1.6, 1.9),
                ((0.8, 0.3), 1.3, 1.9),
                ((2.9, 0.3), 1.2, 1.9),
                # Middle row
                ((-3.3, -2.2), 1.4, 1.4),
                ((-1.0, -2.2), 1.6, 1.4),
                ((0.8, -2.2), 1.3, 1.4),
                ((2.9, -2.2), 1.2, 1.4),
                # Bottom row
                ((-3.3, -3.3), 1.4, 0.5),
                ((-1.0, -3.3), 1.6, 0.5),
                ((0.8, -3.3), 1.3, 0.5),
                ((2.9, -3.3), 1.2, 0.5),
            ]
        }
        return network
    
    def define_city_routes(self):
        """Define realistic city routes with multiple turns."""
        return [
            # Route 1: Long route with 3 turns (bottom-left to top-right)
            {
                'start': (-3.5, -2.5),
                'waypoints': [(-2.5, -2.5), (-2.5, 0), (0, 0), (0, 2.5), (2.5, 2.5)],
                'end': (3.5, 2.5),
                'color': '#FF4444',
                'label': 'A'
            },
            # Route 2: Cross-town route (top-left to bottom-right)
            {
                'start': (-3.5, 2.5),
                'waypoints': [(-2.5, 2.5), (0, 2.5), (0, 0), (2.5, 0), (2.5, -2.5)],
                'end': (3.5, -2.5),
                'color': '#4444FF',
                'label': 'B'
            },
            # Route 3: Simple horizontal (right to left)
            {
                'start': (3.5, 0),
                'waypoints': [(2.5, 0), (0, 0), (-2.5, 0)],
                'end': (-3.5, 0),
                'color': '#44FF44',
                'label': 'C'
            },
            # Route 4: L-shaped route (top-middle to bottom-right)
            {
                'start': (0, 3.5),
                'waypoints': [(0, 2.5), (0, 0), (2.5, 0), (2.5, -2.5)],
                'end': (3.5, -2.5),
                'color': '#FF8800',
                'label': 'D'
            },
            # Route 5: Vertical route (bottom-left to top-left)
            {
                'start': (-2.5, -3.5),
                'waypoints': [(-2.5, -2.5), (-2.5, 0), (-2.5, 2.5)],
                'end': (-2.5, 3.5),
                'color': '#FF44FF',
                'label': 'E'
            },
        ]
    
    def init_user_cars(self):
        """Initialize cars for user-controlled mode - FAST and RECKLESS."""
        cars = []
        for route in self.routes:
            car = {
                'route': route,
                'current_waypoint': 0,
                'x': route['start'][0],
                'y': route['start'][1],
                'color': route['color'],
                'label': route['label'],
                'speed': 1.2 + np.random.random() * 0.3,  # FAST: 1.2-1.5x speed
                'active': True,
                'completed': False,
                'crashed': False,
                'start_frame': 0,
            }
            cars.append(car)
        return cars
    
    def init_ai_cars(self):
        """Initialize cars for AI-coordinated mode - SLOWER but SAFER."""
        cars = []
        for i, route in enumerate(self.routes):
            car = {
                'route': route,
                'current_waypoint': 0,
                'x': route['start'][0],
                'y': route['start'][1],
                'color': route['color'],
                'label': route['label'],
                'speed': 0.75,  # SLOWER: 0.75x speed (safer, more cautious)
                'active': True,
                'completed': False,
                'crashed': False,
                'delay': i * 15,  # Staggered starts
                'thinking': False,
                'communicating_with': [],
                'status': 'normal',
                'message': '',
                'start_frame': 0,
            }
            cars.append(car)
        return cars
    
    def draw_city_background(self, ax):
        """Draw the detailed city background."""
        ax.set_xlim(-4, 4)
        ax.set_ylim(-4, 4)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_facecolor('#1a1a1a')
        
        # Draw buildings
        for building in self.road_network['buildings']:
            pos, width, height = building
            # Building
            rect = Rectangle(pos, width, height, 
                           facecolor='#3d3d3d', edgecolor='#555', linewidth=1.5, zorder=1)
            ax.add_patch(rect)
            # Windows
            window_rows = int(height / 0.3)
            window_cols = int(width / 0.3)
            for row in range(max(1, window_rows)):
                for col in range(max(1, window_cols)):
                    if np.random.random() > 0.3:  # Random lit windows
                        wx = pos[0] + 0.15 + col * 0.3
                        wy = pos[1] + 0.15 + row * 0.3
                        if wx < pos[0] + width - 0.1 and wy < pos[1] + height - 0.1:
                            window = Rectangle((wx, wy), 0.12, 0.12,
                                             facecolor='#FFDD88', alpha=0.6, zorder=2)
                            ax.add_patch(window)
        
        # Draw roads with lanes
        for road in self.road_network['roads']:
            # Road base (dark gray)
            ax.plot([road[0][0], road[1][0]], [road[0][1], road[1][1]], 
                   'k-', linewidth=22, color='#2a2a2a', alpha=1.0, zorder=3, solid_capstyle='round')
            # Road surface (lighter gray)
            ax.plot([road[0][0], road[1][0]], [road[0][1], road[1][1]], 
                   'k-', linewidth=18, color='#404040', alpha=1.0, zorder=4, solid_capstyle='round')
            
            # Lane markings (dashed yellow)
            if road[0][0] == road[1][0]:  # Vertical road
                x = road[0][0]
                y_start, y_end = sorted([road[0][1], road[1][1]])
                ax.plot([x, x], [y_start, y_end], 
                       'y--', linewidth=1.5, alpha=0.7, zorder=5, dashes=(10, 10))
            else:  # Horizontal road
                y = road[0][1]
                x_start, x_end = sorted([road[0][0], road[1][0]])
                ax.plot([x_start, x_end], [y, y], 
                       'y--', linewidth=1.5, alpha=0.7, zorder=5, dashes=(10, 10))
        
        # Draw intersections
        for intersection in self.road_network['intersections']:
            # Intersection square
            square = Rectangle((intersection[0] - 0.3, intersection[1] - 0.3), 
                             0.6, 0.6, facecolor='#404040', alpha=1.0, zorder=4)
            ax.add_patch(square)
            # Center marker
            circle = Circle(intersection, 0.08, color='yellow', alpha=0.5, zorder=6)
            ax.add_patch(circle)
    
    def draw_title_and_info(self, ax):
        """Draw title and current mode information."""
        if self.mode == 'user':
            title = 'USER-CONTROLLED TRAFFIC'
            subtitle = 'Fast & reckless - each car makes independent decisions'
            color = '#FF4444'
        elif self.mode == 'ai':
            title = 'AI-COORDINATED TRAFFIC'
            subtitle = 'Slower & safer - cars communicate and coordinate'
            color = '#44FF44'
        else:
            return
        
        ax.text(0, 3.7, title, ha='center', va='center',
               fontsize=24, fontweight='bold', color=color,
               bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.9),
               zorder=50)
        ax.text(0, 3.3, subtitle, ha='center', va='center',
               fontsize=14, color='white', style='italic', zorder=50)
    
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
        # Don't move if crashed
        if car.get('crashed', False):
            return True  # Still render it
        
        # Extra safety check for AI: don't move if status is explicitly stopped
        if is_ai and car.get('status') == 'stopped':
            return True  # Stay in place
        
        segment = self.get_path_segment(car)
        if segment is None:
            car['completed'] = True
            return False
        
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
            if car['status'] == 'stopped':
                speed_mult = 0
            elif car['status'] == 'slowing':
                speed_mult = 0.3  # Slower to give more time for coordination
        
        move_dist = 0.04 * speed_mult
        progress = move_dist / dist
        
        car['x'] += dx * progress
        car['y'] += dy * progress
        
        # Check if reached waypoint
        dist_to_end = np.sqrt((end[0] - car['x'])**2 + (end[1] - car['y'])**2)
        if dist_to_end < 0.2:
            car['current_waypoint'] += 1
        
        return True
    
    def get_car_direction(self, car):
        """Get the direction vector of a car's current movement."""
        segment = self.get_path_segment(car)
        if segment is None:
            return None
        start, end = segment
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = np.sqrt(dx**2 + dy**2)
        if length < 0.01:
            return None
        return (dx / length, dy / length)  # Normalized direction vector
    
    def check_collisions(self, cars):
        """Check for collisions between cars and mark them as crashed.
        Cars going in opposite directions on the same road won't collide (different lanes)."""
        collisions = []
        for i, car1 in enumerate(cars):
            if not car1['active'] or car1['completed'] or car1.get('crashed', False):
                continue
            for j, car2 in enumerate(cars[i+1:], i+1):
                if not car2['active'] or car2['completed'] or car2.get('crashed', False):
                    continue
                
                # Check physical distance
                dist = np.sqrt((car1['x'] - car2['x'])**2 + (car1['y'] - car2['y'])**2)
                if dist < 0.35:
                    # Get directions
                    dir1 = self.get_car_direction(car1)
                    dir2 = self.get_car_direction(car2)
                    
                    # If we can't determine direction, count as collision
                    if dir1 is None or dir2 is None:
                        pair = tuple(sorted([car1['label'], car2['label']]))
                        if pair not in self.collision_pairs:
                            car1['crashed'] = True
                            car2['crashed'] = True
                            collisions.append((car1, car2))
                            self.collision_pairs.add(pair)
                        continue
                    
                    # Calculate dot product to determine if going same/opposite direction
                    # dot = 1 means same direction, -1 means opposite, 0 means perpendicular
                    dot_product = dir1[0] * dir2[0] + dir1[1] * dir2[1]
                    
                    # Only collide if NOT going in opposite directions
                    # If dot < -0.7, they're going opposite ways (different lanes) - NO COLLISION
                    if dot_product > -0.7:
                        pair = tuple(sorted([car1['label'], car2['label']]))
                        if pair not in self.collision_pairs:
                            # Mark both cars as crashed - they stop immediately!
                            car1['crashed'] = True
                            car2['crashed'] = True
                            collisions.append((car1, car2))
                            self.collision_pairs.add(pair)
        return collisions
    
    def find_nearby_cars(self, car, all_cars, threshold=1.5):
        """Find cars within communication range."""
        nearby = []
        for other in all_cars:
            if other == car or other['completed'] or other['delay'] > self.mode_frame:
                continue
            dist = np.sqrt((car['x'] - other['x'])**2 + (car['y'] - other['y'])**2)
            if dist < threshold:
                nearby.append((other, dist))
        return nearby
    
    def ai_coordinate(self, cars):
        """AI coordination logic with improved collision prevention."""
        for car in cars:
            if car['delay'] > self.mode_frame or car['completed'] or car.get('crashed', False):
                continue
            
            # Check if near intersection (increased detection range)
            near_intersection = False
            closest_intersection_dist = float('inf')
            for intersection in self.road_network['intersections']:
                dist = np.sqrt((car['x'] - intersection[0])**2 + (car['y'] - intersection[1])**2)
                if dist < 1.5:  # Increased from 1.0 to detect earlier
                    near_intersection = True
                    closest_intersection_dist = min(closest_intersection_dist, dist)
                    break
            
            if near_intersection:
                # Find nearby cars (increased threshold)
                nearby = self.find_nearby_cars(car, cars, threshold=2.0)
                
                if nearby:
                    car['thinking'] = True
                    car['communicating_with'] = [other for other, _ in nearby]
                    
                    # Improved priority system: use distance to intersection + arrival time
                    my_arrival = self.mode_frame - car['delay']
                    should_wait = False
                    should_slow = False
                    
                    for other, dist in nearby:
                        # Skip if other car is already stopped or crashed
                        if other.get('status') == 'stopped' or other.get('crashed', False):
                            continue
                        
                        other_arrival = self.mode_frame - other['delay']
                        
                        # If another car is very close, definitely wait
                        if dist < 0.8:
                            # Check who arrived at the intersection area first
                            if other_arrival < my_arrival - 3:
                                should_wait = True
                                break
                            # If they're about the same time, use label as tiebreaker for consistency
                            elif abs(other_arrival - my_arrival) < 3:
                                if car['label'] > other['label']:  # Alphabetical priority
                                    should_wait = True
                                    break
                        # If car is nearby but not too close, slow down
                        elif dist < 1.5:
                            should_slow = True
                    
                    if should_wait:
                        car['status'] = 'stopped'
                        car['message'] = 'WAIT'
                    elif should_slow:
                        car['status'] = 'slowing'
                        car['message'] = 'SLOW'
                    else:
                        car['status'] = 'normal'
                        car['message'] = 'GO'
                else:
                    car['thinking'] = False
                    car['status'] = 'normal'
                    car['message'] = ''
            else:
                # Far from intersections, drive normally
                car['thinking'] = False
                car['status'] = 'normal'
                car['message'] = ''
    
    def draw_car(self, ax, car, is_ai=False):
        """Draw a car with rotation and optional AI indicators."""
        segment = self.get_path_segment(car)
        if segment:
            start, end = segment
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            angle = math.atan2(dy, dx)
        else:
            angle = 0
        
        # Car body
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
        corners_rotated[:, 0] += car['x']
        corners_rotated[:, 1] += car['y']
        
        # Change appearance if crashed
        if car.get('crashed', False):
            car_poly = Polygon(corners_rotated, facecolor='#333333', 
                              edgecolor='red', linewidth=3, zorder=15, linestyle='--')
            ax.add_patch(car_poly)
            # Add crash symbol
            ax.text(car['x'], car['y'] + 0.45, '💥', ha='center', va='center',
                   fontsize=16, zorder=20)
        else:
            car_poly = Polygon(corners_rotated, facecolor=car['color'], 
                              edgecolor='white', linewidth=2, zorder=15)
            ax.add_patch(car_poly)
            
            # Headlights (only if not crashed)
            headlight_offset = car_length / 2 + 0.05
            headlight_x = car['x'] + headlight_offset * cos_a
            headlight_y = car['y'] + headlight_offset * sin_a
            headlight = Circle((headlight_x, headlight_y), 0.04, 
                              color='yellow', alpha=0.8, zorder=16)
            ax.add_patch(headlight)
        
        # Label
        label_color = '#888888' if car.get('crashed', False) else 'white'
        ax.text(car['x'], car['y'], car['label'], 
               ha='center', va='center', fontsize=11, 
               color=label_color, fontweight='bold', zorder=17)
        
        # AI-specific indicators
        if is_ai:
            if car.get('thinking', False):
                # Thinking animation
                dot_frame = (self.mode_frame // 8) % 3
                for i in range(3):
                    alpha = 0.3 if i != dot_frame else 1.0
                    circle = Circle((car['x'] + (i - 1) * 0.18, car['y'] + 0.5), 
                                  0.06, color='#00FFFF', alpha=alpha, zorder=18)
                    ax.add_patch(circle)
            
            # Status indicator
            if car.get('status') == 'stopped':
                stop_circle = Circle((car['x'], car['y'] + 0.4), 0.12, 
                                    color='#FF4444', alpha=0.9, zorder=18)
                ax.add_patch(stop_circle)
                ax.text(car['x'], car['y'] + 0.4, '⏸', ha='center', va='center',
                       fontsize=14, color='white', fontweight='bold', zorder=19)
            elif car.get('status') == 'slowing':
                slow_circle = Circle((car['x'], car['y'] + 0.4), 0.12,
                                    color='#FFAA00', alpha=0.9, zorder=18)
                ax.add_patch(slow_circle)
                ax.text(car['x'], car['y'] + 0.4, '⚠', ha='center', va='center',
                       fontsize=14, color='white', fontweight='bold', zorder=19)
            
            # Message
            if car.get('message'):
                ax.text(car['x'], car['y'] - 0.5, car['message'], 
                       ha='center', va='top', fontsize=10, 
                       color='#00FF00', fontweight='bold', 
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.8),
                       zorder=18)
    
    def draw_ai_communication(self, ax, cars):
        """Draw communication lines between AI cars."""
        for car in cars:
            if car['delay'] > self.mode_frame or car['completed']:
                continue
            
            if car.get('communicating_with'):
                for other_car in car['communicating_with']:
                    # Communication line
                    line = FancyArrowPatch(
                        (car['x'], car['y']), (other_car['x'], other_car['y']),
                        arrowstyle='->', color='#00FFFF', alpha=0.5,
                        linewidth=2, linestyle='--', zorder=12
                    )
                    ax.add_patch(line)
                    
                    # Animated data packet
                    progress = (self.mode_frame % 40) / 40.0
                    packet_x = car['x'] + (other_car['x'] - car['x']) * progress
                    packet_y = car['y'] + (other_car['y'] - car['y']) * progress
                    packet = Circle((packet_x, packet_y), 0.08, 
                                   color='#00FFFF', alpha=0.9, zorder=13)
                    ax.add_patch(packet)
    
    def draw_statistics(self, ax, mode):
        """Draw statistics after a mode completes."""
        if mode == 'user':
            title = 'USER-CONTROLLED RESULTS'
            collisions = self.user_collisions
            time_taken = (self.user_end_time - self.user_start_time) / 20.0  # Convert frames to seconds
            cars = self.user_cars
            color = '#FF4444'
        else:  # AI
            title = 'AI-COORDINATED RESULTS'
            collisions = self.ai_collisions
            time_taken = (self.ai_end_time - self.ai_start_time) / 20.0
            cars = self.ai_cars
            color = '#44FF44'
        
        # Count completed vs crashed
        completed = sum(1 for car in cars if car['completed'])
        crashed = sum(1 for car in cars if car.get('crashed', False))
        total = len(cars)
        
        ax.text(0, 2.5, title, ha='center', va='center',
               fontsize=28, fontweight='bold', color=color,
               bbox=dict(boxstyle='round,pad=0.8', facecolor='black', alpha=0.95),
               zorder=50)
        
        # Statistics box
        stats_text = f"""
━━━━━━━━━━━━━━━━━━━━━━━━

  COLLISIONS:  {collisions}

  TIME TAKEN:  {time_taken:.1f}s

  COMPLETED:   {completed}/{total}

  CRASHED:     {crashed}/{total}

━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax.text(0, -0.2, stats_text, ha='center', va='center',
               fontsize=18, color='white', fontweight='bold',
               bbox=dict(boxstyle='round,pad=1.2', facecolor='#1a1a1a', 
                        edgecolor=color, linewidth=4, alpha=0.95),
               zorder=50, family='monospace')
        
        # Next action text
        if mode == 'user':
            ax.text(0, -3.0, 'Next: AI Coordination Mode...', ha='center', va='center',
                   fontsize=16, color='#44FF44', style='italic', zorder=50)
    
    def draw_comparison(self, ax):
        """Draw side-by-side comparison of USER vs AI results."""
        ax.text(0, 3.5, 'FINAL COMPARISON', ha='center', va='center',
               fontsize=32, fontweight='bold', color='white',
               bbox=dict(boxstyle='round,pad=0.8', facecolor='black', alpha=0.95),
               zorder=50)
        
        # USER stats
        user_completed = sum(1 for car in self.user_cars if car['completed'])
        user_crashed = sum(1 for car in self.user_cars if car.get('crashed', False))
        user_time = (self.user_end_time - self.user_start_time) / 20.0
        
        user_stats = f"""
USER-CONTROLLED
━━━━━━━━━━━━━━━

  Collisions:  {self.user_collisions}
  
  Time:        {user_time:.1f}s
  
  Completed:   {user_completed}/5
  
  Crashed:     {user_crashed}/5
        """
        
        ax.text(-2.2, 0.5, user_stats, ha='center', va='center',
               fontsize=16, color='white', fontweight='bold',
               bbox=dict(boxstyle='round,pad=1.0', facecolor='#1a1a1a', 
                        edgecolor='#FF4444', linewidth=4, alpha=0.95),
               zorder=50, family='monospace')
        
        # AI stats
        ai_completed = sum(1 for car in self.ai_cars if car['completed'])
        ai_crashed = sum(1 for car in self.ai_cars if car.get('crashed', False))
        ai_time = (self.ai_end_time - self.ai_start_time) / 20.0
        
        ai_stats = f"""
AI-COORDINATED
━━━━━━━━━━━━━━━

  Collisions:  {self.ai_collisions}
  
  Time:        {ai_time:.1f}s
  
  Completed:   {ai_completed}/5
  
  Crashed:     {ai_crashed}/5
        """
        
        ax.text(2.2, 0.5, ai_stats, ha='center', va='center',
               fontsize=16, color='white', fontweight='bold',
               bbox=dict(boxstyle='round,pad=1.0', facecolor='#1a1a1a', 
                        edgecolor='#44FF44', linewidth=4, alpha=0.95),
               zorder=50, family='monospace')
        
        # Draw VS in the middle
        ax.text(0, 0.5, 'VS', ha='center', va='center',
               fontsize=36, color='yellow', fontweight='bold', zorder=50)
        
        # Calculate improvements
        if self.user_collisions > 0:
            collision_reduction = ((self.user_collisions - self.ai_collisions) / self.user_collisions) * 100
        else:
            collision_reduction = 0
        
        completion_improvement = ai_completed - user_completed
        
        # Results summary
        time_comparison = "Slower" if ai_time > user_time else "Faster"
        time_diff_pct = abs((ai_time - user_time) / max(user_time, 0.1)) * 100
        
        summary = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   AI COORDINATION RESULTS:

   ✓ {collision_reduction:.0f}% Collision Reduction

   ✓ {completion_improvement} More Cars Completed

   ✓ Better Traffic Flow & Safety

   ⚠ Slightly {time_comparison} ({time_diff_pct:.0f}%)
     (Safety over Speed)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        ax.text(0, -2.3, summary, ha='center', va='center',
               fontsize=16, color='#00FF00', fontweight='bold',
               bbox=dict(boxstyle='round,pad=1.0', facecolor='black', alpha=0.95),
               zorder=50, family='monospace')
    
    def animate(self, frame):
        """Main animation function."""
        self.frame = frame
        self.ax.clear()
        self.draw_city_background(self.ax)
        
        # USER MODE
        if self.mode == 'user':
            if self.mode_frame == 0:
                self.user_start_time = frame
                for car in self.user_cars:
                    car['start_frame'] = frame
            
            self.mode_frame += 1
            self.draw_title_and_info(self.ax)
            
            # Update and draw cars
            active_cars = 0
            for car in self.user_cars:
                if car['active'] and not car['completed']:
                    if self.update_car_position(car, is_ai=False):
                        self.draw_car(self.ax, car, is_ai=False)
                        active_cars += 1
            
            # Check collisions
            collisions = self.check_collisions(self.user_cars)
            for car1, car2 in collisions:
                self.user_collisions += 1
                # Show collision effect
                mid_x = (car1['x'] + car2['x']) / 2
                mid_y = (car1['y'] + car2['y']) / 2
                explosion = Circle((mid_x, mid_y), 0.4, color='red', alpha=0.6, zorder=20)
                self.ax.add_patch(explosion)
                self.ax.text(mid_x, mid_y + 0.6, '💥 COLLISION!', ha='center', va='center',
                           fontsize=16, color='red', fontweight='bold', zorder=21)
            
            # Check if all cars done (either completed or crashed)
            if all(car['completed'] or car.get('crashed', False) for car in self.user_cars):
                self.user_end_time = frame
                self.mode = 'stats_user'
                self.mode_frame = 0
        
        # USER STATS
        elif self.mode == 'stats_user':
            self.mode_frame += 1
            self.draw_statistics(self.ax, 'user')
            
            if self.mode_frame > 60:  # Show stats for 3 seconds
                self.mode = 'ai'
                self.mode_frame = 0
                self.collision_pairs.clear()
        
        # AI MODE
        elif self.mode == 'ai':
            if self.mode_frame == 0:
                self.ai_start_time = frame
                for car in self.ai_cars:
                    car['start_frame'] = frame
            
            self.mode_frame += 1
            self.draw_title_and_info(self.ax)
            
            # AI coordination
            self.ai_coordinate(self.ai_cars)
            
            # Update and draw cars
            for car in self.ai_cars:
                if car['delay'] <= self.mode_frame:
                    if car['active'] and not car['completed']:
                        if self.update_car_position(car, is_ai=True):
                            self.draw_car(self.ax, car, is_ai=True)
            
            # Draw communication
            self.draw_ai_communication(self.ax, self.ai_cars)
            
            # Check collisions (should be zero!)
            collisions = self.check_collisions(self.ai_cars)
            for car1, car2 in collisions:
                self.ai_collisions += 1
            
            # Check if all cars done (either completed or crashed)
            active_cars = [car for car in self.ai_cars if car['delay'] <= self.mode_frame]
            if active_cars and all(car['completed'] or car.get('crashed', False) for car in active_cars):
                self.ai_end_time = frame
                self.mode = 'stats_ai'
                self.mode_frame = 0
        
        # AI STATS
        elif self.mode == 'stats_ai':
            self.mode_frame += 1
            self.draw_statistics(self.ax, 'ai')
            
            if self.mode_frame > 60:  # Show stats for 3 seconds
                self.mode = 'comparison'
                self.mode_frame = 0
        
        # FINAL COMPARISON
        elif self.mode == 'comparison':
            self.mode_frame += 1
            self.draw_comparison(self.ax)
            
            if self.mode_frame > 100:  # Show comparison for 5 seconds
                self.mode = 'complete'
        
        plt.tight_layout()
        return []
    
    def run(self):
        """Run the animation."""
        anim = animation.FuncAnimation(self.fig, self.animate, frames=800, 
                                      interval=50, blit=False, repeat=False)
        plt.tight_layout()
        plt.show()
        return anim


if __name__ == '__main__':
    print("🚗 Starting Professional Traffic Coordination Demo")
    print("=" * 60)
    print("\nDemo Structure:")
    print("1. USER-CONTROLLED traffic (independent decisions)")
    print("   → Shows collisions & crashed cars")
    print("2. USER Statistics: collisions, time, completed vs crashed")
    print("3. AI-COORDINATED traffic (communication & coordination)")
    print("   → Cars coordinate to avoid collisions")
    print("4. AI Statistics: collisions, time, completed vs crashed")
    print("5. FINAL COMPARISON: Side-by-side results")
    print("\nFeatures:")
    print("  • Detailed city map with buildings & roads")
    print("  • Crashed cars STOP and don't complete route")
    print("  • 5 different car routes with multiple turns")
    print("  • AI communication visualization (thinking, messages)")
    print("  • Real-time collision detection with visual effects")
    print("  • Comprehensive statistics tracking")
    print("\n" + "=" * 60)
    print("Starting demo...\n")
    
    demo = TrafficDemo()
    anim = demo.run()
    
    try:
        plt.show(block=True)
    except KeyboardInterrupt:
        print("\nDemo stopped.")
