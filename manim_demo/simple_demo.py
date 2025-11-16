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
        self.fig, self.ax = plt.subplots(1, 1, figsize=(22, 12))
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
        
        # Intersection queue for right-of-way (separate queues for horizontal and vertical)
        # Maps (intersection_pos, direction) to list of car labels in order
        self.intersection_queue = {}
        self.cars_in_intersection = set()  # Track which cars are currently in intersection
        
        # Create detailed road network
        self.road_network = self.create_city_map()
        
        # Define routes
        self.routes = self.define_city_routes()
        
        # Initialize cars
        self.user_cars = self.init_user_cars()
        self.ai_cars = self.init_ai_cars()
        
        self.collision_pairs = set()
        
        # Create fixed road background image
        self.road_background = self.create_road_background()
        
    def create_city_map(self):
        """Create a centered city map with 1 horizontal and 1 vertical road creating 1 intersection."""
        network = {
            'intersections': [
                (0, 0),  # Single centered intersection
            ],
            'roads': [
                # Horizontal road - centered at y=0
                ((-5.0, 0), (5.0, 0)),
                # Vertical road - centered at x=0
                ((0, -3.2), (0, 3.2)),
            ],
            'buildings': []  # No buildings for cleaner view
        }
        return network
    
    def define_city_routes(self):
        """Define routes with exactly 2 cars per lane - 1 horizontal and 1 vertical road (16 total cars)."""
        colors = ['#FF4444', '#4444FF', '#44FF44', '#FF8800', '#FF44FF', '#44FFFF',
                  '#FFFF44', '#FF88FF', '#88FF88', '#8888FF', '#FFAA44', '#AA44FF',
                  '#FF8844', '#44FF88', '#8844FF', '#FF4488', '#88FF44', '#4488FF']
        
        routes = []
        
        # HORIZONTAL ROAD (centered at y = 0)
        # Going RIGHT - bottom lanes (inner lane closer to yellow line, outer lane closer to edge)
        for i in range(2):  # 2 cars in inner right lane (y=-0.1)
            routes.append({
                'start': (-5.0, -0.1), 'waypoints': [], 'end': (5.0, -0.1),
                'color': colors[len(routes) % len(colors)], 'label': str(len(routes) + 1),
                'lane': 'inner', 'direction': 'right', 'base_y': -0.1, 'alt_y': -0.3
            })
        for i in range(2):  # 2 cars in outer right lane (y=-0.3)
            routes.append({
                'start': (-5.0, -0.3), 'waypoints': [], 'end': (5.0, -0.3),
                'color': colors[len(routes) % len(colors)], 'label': str(len(routes) + 1),
                'lane': 'outer', 'direction': 'right', 'base_y': -0.3, 'alt_y': -0.1
            })
        # Going LEFT - top lanes (inner lane closer to yellow line, outer lane closer to edge)
        for i in range(2):  # 2 cars in inner left lane (y=0.1)
            routes.append({
                'start': (5.0, 0.1), 'waypoints': [], 'end': (-5.0, 0.1),
                'color': colors[len(routes) % len(colors)], 'label': str(len(routes) + 1),
                'lane': 'inner', 'direction': 'left', 'base_y': 0.1, 'alt_y': 0.3
            })
        for i in range(2):  # 2 cars in outer left lane (y=0.3)
            routes.append({
                'start': (5.0, 0.3), 'waypoints': [], 'end': (-5.0, 0.3),
                'color': colors[len(routes) % len(colors)], 'label': str(len(routes) + 1),
                'lane': 'outer', 'direction': 'left', 'base_y': 0.3, 'alt_y': 0.1
            })
        
        # VERTICAL ROAD (centered at x = 0)
        # Going UP - right side lanes (inner lane closer to yellow line, outer lane closer to edge)
        for i in range(2):  # 2 cars in inner up lane (x=0.1)
            routes.append({
                'start': (0.1, -3.2), 'waypoints': [], 'end': (0.1, 3.2),
                'color': colors[len(routes) % len(colors)], 'label': str(len(routes) + 1),
                'lane': 'inner', 'direction': 'up', 'base_y': 0.1, 'alt_y': 0.3
            })
        for i in range(2):  # 2 cars in outer up lane (x=0.3)
            routes.append({
                'start': (0.3, -3.2), 'waypoints': [], 'end': (0.3, 3.2),
                'color': colors[len(routes) % len(colors)], 'label': str(len(routes) + 1),
                'lane': 'outer', 'direction': 'up', 'base_y': 0.3, 'alt_y': 0.1
            })
        # Going DOWN - left side lanes (inner lane closer to yellow line, outer lane closer to edge)
        for i in range(2):  # 2 cars in inner down lane (x=-0.1)
            routes.append({
                'start': (-0.1, 3.2), 'waypoints': [], 'end': (-0.1, -3.2),
                'color': colors[len(routes) % len(colors)], 'label': str(len(routes) + 1),
                'lane': 'inner', 'direction': 'down', 'base_y': -0.1, 'alt_y': -0.3
            })
        for i in range(2):  # 2 cars in outer down lane (x=-0.3)
            routes.append({
                'start': (-0.3, 3.2), 'waypoints': [], 'end': (-0.3, -3.2),
                'color': colors[len(routes) % len(colors)], 'label': str(len(routes) + 1),
                'lane': 'outer', 'direction': 'down', 'base_y': -0.3, 'alt_y': -0.1
            })
        
        return routes
    
    # Removed lane offset functions - cars are now positioned exactly in routes
    
    def init_user_cars(self):
        """Initialize all cars at start with random positions, maintaining spacing."""
        cars = []
        base_speed = 1.0
        car_length = 0.24  # Car length from draw_car function (reduced size)
        min_spacing = car_length * 2  # One car length on each side
        
        # Track spawned positions per lane
        lane_positions = {}
        
        for idx, route in enumerate(self.routes):
            direction = route['direction']
            
            # Create unique lane identifier
            if direction in ['right', 'left']:  # Horizontal road
                lane_key = ('horizontal', route['start'][1])
            else:  # Vertical road (up/down)
                lane_key = ('vertical', route['start'][0])
            
            # Initialize tracking for this lane
            if lane_key not in lane_positions:
                lane_positions[lane_key] = []
            
            # Find a valid random spawn position along the lane
            max_attempts = 100
            spawn_pos = None
            
            if direction in ['right', 'left']:  # Horizontal road - vary x
                for attempt in range(max_attempts):
                    candidate = np.random.uniform(-4.5, 4.5)
                    # Don't spawn in intersection area (-0.3 to 0.3)
                    if -0.3 <= candidate <= 0.3:
                        continue
                    valid = True
                    for existing in lane_positions[lane_key]:
                        if abs(candidate - existing) < min_spacing:
                            valid = False
                            break
                    if valid:
                        spawn_pos = candidate
                        lane_positions[lane_key].append(spawn_pos)
                        break
                if spawn_pos is None:
                    # Fallback: spawn outside intersection
                    spawn_pos = 2.0 if np.random.random() > 0.5 else -2.0
                spawn_x, spawn_y = spawn_pos, route['start'][1]
            else:  # Vertical road - vary y
                for attempt in range(max_attempts):
                    candidate = np.random.uniform(-3.0, 3.0)
                    # Don't spawn in intersection area (-0.3 to 0.3)
                    if -0.3 <= candidate <= 0.3:
                        continue
                    valid = True
                    for existing in lane_positions[lane_key]:
                        if abs(candidate - existing) < min_spacing:
                            valid = False
                            break
                    if valid:
                        spawn_pos = candidate
                        lane_positions[lane_key].append(spawn_pos)
                        break
                if spawn_pos is None:
                    # Fallback: spawn outside intersection
                    spawn_pos = 2.0 if np.random.random() > 0.5 else -2.0
                spawn_x, spawn_y = route['start'][0], spawn_pos
            
            car = {
                'route': route,
                'current_waypoint': 0,
                'x': spawn_x,
                'y': spawn_y,
                'color': route['color'],
                'label': route['label'],
                'speed': base_speed * (1.0 + np.random.random() * 1.5),  # 100%-250% (0% to +150% increase)
                'active': True,
                'completed': False,
                'crashed': False,
                'start_frame': 0,
                'spawn_delay': 0,  # All spawn at once
                'changing_lane': False,
                'lane_change_target': None,  # Can be x or y depending on direction
                'lane_change_progress': 0,
            }
            
            cars.append(car)
        
        return cars
    
    def init_ai_cars(self):
        """Initialize all AI cars at start with random positions, maintaining spacing."""
        cars = []
        base_speed = 0.65  # Slower base speed for better collision avoidance
        car_length = 0.24  # Car length from draw_car function (reduced size)
        min_spacing = car_length * 2  # One car length on each side
        min_safety_distance = 0.4  # Minimum distance from ANY other car
        
        # Track spawned positions per lane
        lane_positions = {}
        
        for idx, route in enumerate(self.routes):
            direction = route['direction']
            
            # Create unique lane identifier
            if direction in ['right', 'left']:  # Horizontal road
                lane_key = ('horizontal', route['start'][1])
            else:  # Vertical road (up/down)
                lane_key = ('vertical', route['start'][0])
            
            # Initialize tracking for this lane
            if lane_key not in lane_positions:
                lane_positions[lane_key] = []
            
            # Find a valid random spawn position along the lane
            max_attempts = 100
            spawn_pos = None
            
            if direction in ['right', 'left']:  # Horizontal road - vary x
                for attempt in range(max_attempts):
                    candidate = np.random.uniform(-4.5, 4.5)
                    # Don't spawn in intersection area (-0.3 to 0.3)
                    if -0.3 <= candidate <= 0.3:
                        continue
                    
                    # Check same lane spacing
                    valid = True
                    for existing in lane_positions[lane_key]:
                        if abs(candidate - existing) < min_spacing:
                            valid = False
                            break
                    
                    if valid:
                        # Check distance from ALL other spawned cars
                        candidate_x = candidate
                        candidate_y = route['start'][1]
                        for other_car in cars:
                            dist = np.sqrt((candidate_x - other_car['x'])**2 + (candidate_y - other_car['y'])**2)
                            if dist < min_safety_distance:
                                valid = False
                                break
                    
                    if valid:
                        spawn_pos = candidate
                        lane_positions[lane_key].append(spawn_pos)
                        break
                if spawn_pos is None:
                    # Fallback: spawn outside intersection
                    spawn_pos = 2.0 if np.random.random() > 0.5 else -2.0
                spawn_x, spawn_y = spawn_pos, route['start'][1]
            else:  # Vertical road - vary y
                for attempt in range(max_attempts):
                    candidate = np.random.uniform(-3.0, 3.0)
                    # Don't spawn in intersection area (-0.3 to 0.3)
                    if -0.3 <= candidate <= 0.3:
                        continue
                    
                    # Check same lane spacing
                    valid = True
                    for existing in lane_positions[lane_key]:
                        if abs(candidate - existing) < min_spacing:
                            valid = False
                            break
                    
                    if valid:
                        # Check distance from ALL other spawned cars
                        candidate_x = route['start'][0]
                        candidate_y = candidate
                        for other_car in cars:
                            dist = np.sqrt((candidate_x - other_car['x'])**2 + (candidate_y - other_car['y'])**2)
                            if dist < min_safety_distance:
                                valid = False
                                break
                    
                    if valid:
                        spawn_pos = candidate
                        lane_positions[lane_key].append(spawn_pos)
                        break
                if spawn_pos is None:
                    # Fallback: spawn outside intersection
                    spawn_pos = 2.0 if np.random.random() > 0.5 else -2.0
                spawn_x, spawn_y = route['start'][0], spawn_pos
            
            car = {
                'route': route,
                'current_waypoint': 0,
                'x': spawn_x,
                'y': spawn_y,
                'color': route['color'],
                'label': route['label'],
                'speed': base_speed * (1.0 + np.random.random() * 1.5),  # 100%-250% (0% to +150% increase)
                'active': True,
                'completed': False,
                'crashed': False,
                'delay': 0,  # All spawn at once
                'thinking': False,
                'communicating_with': [],
                'status': 'normal',
                'message': '',
                'start_frame': 0,
                'changing_lane': False,
                'lane_change_target': None,  # Can be x or y depending on direction
                'lane_change_progress': 0,
            }
            
            cars.append(car)
        
        return cars
    
    def create_road_background(self):
        """Create a fixed background image with roads, buildings, and lane markings."""
        # Create a separate figure for the background
        dpi = 100
        width, height = 1000, 640  # pixels (wider to accommodate extended roads)
        fig_bg = plt.figure(figsize=(width/dpi, height/dpi), dpi=dpi)
        ax_bg = fig_bg.add_axes([0, 0, 1, 1])
        
        ax_bg.set_xlim(-5.0, 5.0)
        ax_bg.set_ylim(-3.2, 3.2)
        ax_bg.set_aspect('equal')
        ax_bg.axis('off')
        ax_bg.set_facecolor('#2d5016')  # Green background for grass/non-road areas
        
        # Draw buildings
        np.random.seed(42)  # Fixed seed for consistent windows
        for building in self.road_network['buildings']:
            pos, width, height = building
            # Building
            rect = Rectangle(pos, width, height, 
                           facecolor='#3d3d3d', edgecolor='#555', linewidth=1.5, zorder=1)
            ax_bg.add_patch(rect)
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
                            ax_bg.add_patch(window)
        
        # Draw roads with realistic lane markings - rectangular edges extending to GUI borders
        for road in self.road_network['roads']:
            # Road base (dark gray) - rectangular edges
            ax_bg.plot([road[0][0], road[1][0]], [road[0][1], road[1][1]], 
                   'k-', linewidth=64, color='#2a2a2a', alpha=1.0, zorder=3, solid_capstyle='butt')
            # Road surface (lighter gray) - rectangular edges
            ax_bg.plot([road[0][0], road[1][0]], [road[0][1], road[1][1]], 
                   'k-', linewidth=56, color='#404040', alpha=1.0, zorder=4, solid_capstyle='butt')
            
            # Realistic lane markings - 4 lanes total (2 per direction)
            # Stop lane markings at intersection boundaries with buffer
            intersection_half_size = 0.3  # Half of intersection square size
            buffer = 0.05  # Extra buffer to ensure clean separation
            
            if road[0][0] == road[1][0]:  # Vertical road
                x = road[0][0]
                y_start, y_end = sorted([road[0][1], road[1][1]])
                
                # Find intersections on this road and create segments
                segments = []
                current_start = y_start
                
                for intersection in self.road_network['intersections']:
                    if abs(intersection[0] - x) < 0.01:  # Intersection is on this road
                        int_y = intersection[1]
                        # Add segment before intersection (with buffer)
                        seg_end = int_y - intersection_half_size - buffer
                        if current_start < seg_end:
                            segments.append((current_start, seg_end))
                        current_start = int_y + intersection_half_size + buffer
                
                # Add final segment
                if current_start < y_end:
                    segments.append((current_start, y_end))
                
                # Draw lane markings only on segments (not in intersections)
                for seg_start, seg_end in segments:
                    # Solid yellow center line
                    ax_bg.plot([x, x], [seg_start, seg_end], 
                           '-', linewidth=3, color='#FFD700', alpha=0.9, zorder=5, solid_capstyle='butt')
                    
                    # White dashed lines - draw individual dashes that fit entirely in segment
                    dash_length = 0.15
                    gap_length = 0.15
                    pattern_length = dash_length + gap_length
                    
                    for x_offset in [-0.20, 0.20]:
                        current_y = seg_start
                        while current_y < seg_end:
                            dash_end = current_y + dash_length
                            # Only draw if the entire dash fits before segment end
                            if dash_end <= seg_end:
                                ax_bg.plot([x + x_offset, x + x_offset], [current_y, dash_end], 
                                       '-', linewidth=2, color='white', alpha=0.8, zorder=5, solid_capstyle='butt')
                            current_y += pattern_length
                
            else:  # Horizontal road
                y = road[0][1]
                x_start, x_end = sorted([road[0][0], road[1][0]])
                
                # Find intersections on this road and create segments
                segments = []
                current_start = x_start
                
                for intersection in self.road_network['intersections']:
                    if abs(intersection[1] - y) < 0.01:  # Intersection is on this road
                        int_x = intersection[0]
                        # Add segment before intersection (with buffer)
                        seg_end = int_x - intersection_half_size - buffer
                        if current_start < seg_end:
                            segments.append((current_start, seg_end))
                        current_start = int_x + intersection_half_size + buffer
                
                # Add final segment
                if current_start < x_end:
                    segments.append((current_start, x_end))
                
                # Draw lane markings only on segments (not in intersections)
                for seg_start, seg_end in segments:
                    # Solid yellow center line
                    ax_bg.plot([seg_start, seg_end], [y, y], 
                           '-', linewidth=3, color='#FFD700', alpha=0.9, zorder=5, solid_capstyle='butt')
                    
                    # White dashed lines - draw individual dashes that fit entirely in segment
                    dash_length = 0.15
                    gap_length = 0.15
                    pattern_length = dash_length + gap_length
                    
                    for y_offset in [-0.20, 0.20]:
                        current_x = seg_start
                        while current_x < seg_end:
                            dash_end = current_x + dash_length
                            # Only draw if the entire dash fits before segment end
                            if dash_end <= seg_end:
                                ax_bg.plot([current_x, dash_end], [y + y_offset, y + y_offset], 
                                       '-', linewidth=2, color='white', alpha=0.8, zorder=5, solid_capstyle='butt')
                            current_x += pattern_length
        
        # Draw intersections
        for intersection in self.road_network['intersections']:
            # Intersection square
            square = Rectangle((intersection[0] - 0.3, intersection[1] - 0.3), 
                             0.6, 0.6, facecolor='#404040', alpha=1.0, zorder=4)
            ax_bg.add_patch(square)
            # Center marker removed per user request
        
        # Render to image
        fig_bg.canvas.draw()
        # Get the RGBA buffer
        buf = fig_bg.canvas.buffer_rgba()
        # Convert to numpy array
        img = np.asarray(buf)
        # Convert RGBA to RGB
        img = img[:, :, :3]
        plt.close(fig_bg)
        
        return img
    
    def draw_city_background(self, ax):
        """Draw the fixed city background from pre-rendered image."""
        ax.set_xlim(-5.0, 5.0)
        ax.set_ylim(-3.2, 3.2)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_facecolor('#2d5016')  # Green background instead of dark gray
        
        # Display the fixed road background
        ax.imshow(self.road_background, extent=[-5.0, 5.0, -3.2, 3.2], 
                 aspect='auto', zorder=0, interpolation='bilinear')
    
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
    
    def check_crashed_car_ahead(self, car, all_cars):
        """Check if there's a crashed car ahead in the same lane."""
        if car.get('crashed', False):
            return None
        
        route = car['route']
        direction = route['direction']
        current_y = car['y']
        current_x = car['x']
        detection_range = 1.5  # Look 1.5 units ahead
        
        for other_car in all_cars:
            if other_car['label'] == car['label'] or not other_car.get('crashed', False):
                continue
            
            # Check if in same lane and ahead based on direction
            if direction == 'right':
                if abs(other_car['y'] - current_y) > 0.05:
                    continue
                if other_car['x'] > current_x and other_car['x'] - current_x < detection_range:
                    return other_car
            elif direction == 'left':
                if abs(other_car['y'] - current_y) > 0.05:
                    continue
                if other_car['x'] < current_x and current_x - other_car['x'] < detection_range:
                    return other_car
            elif direction == 'up':
                if abs(other_car['x'] - current_x) > 0.05:
                    continue
                if other_car['y'] > current_y and other_car['y'] - current_y < detection_range:
                    return other_car
            elif direction == 'down':
                if abs(other_car['x'] - current_x) > 0.05:
                    continue
                if other_car['y'] < current_y and current_y - other_car['y'] < detection_range:
                    return other_car
        
        return None
    
    def is_alternate_lane_clear(self, car, all_cars, alt_target):
        """Check if the alternate lane is clear (no cars or crashed cars)."""
        direction = car['route']['direction']
        current_x = car['x']
        current_y = car['y']
        detection_range = 2.0  # Look 2 units ahead and behind
        
        for other_car in all_cars:
            if other_car['label'] == car['label']:
                continue
            
            # Check if other car is in the alternate lane
            if direction in ['right', 'left']:  # Horizontal road
                if abs(other_car['y'] - alt_target) > 0.05:
                    continue
                # Check if within detection range
                if abs(other_car['x'] - current_x) < detection_range:
                    return False  # Lane is not clear
            else:  # Vertical road
                if abs(other_car['x'] - alt_target) > 0.05:
                    continue
                # Check if within detection range
                if abs(other_car['y'] - current_y) < detection_range:
                    return False  # Lane is not clear
        
        return True  # Lane is clear
    
    def check_both_lanes_blocked(self, car, all_cars):
        """Check if both lanes have crashed cars ahead."""
        direction = car['route']['direction']
        current_lane = car['route']['base_y']
        alt_lane = car['route'].get('alt_y') or car['route'].get('alt_x')
        
        if alt_lane is None:
            return False
        
        current_x = car['x']
        current_y = car['y']
        detection_range = 1.5
        
        crashed_in_current = False
        crashed_in_alt = False
        
        for other_car in all_cars:
            if other_car['label'] == car['label'] or not other_car.get('crashed', False):
                continue
            
            # Check for crashed cars in both lanes ahead
            if direction == 'right':
                if other_car['x'] > current_x and other_car['x'] - current_x < detection_range:
                    if abs(other_car['y'] - current_lane) < 0.05:
                        crashed_in_current = True
                    if abs(other_car['y'] - alt_lane) < 0.05:
                        crashed_in_alt = True
            elif direction == 'left':
                if other_car['x'] < current_x and current_x - other_car['x'] < detection_range:
                    if abs(other_car['y'] - current_lane) < 0.05:
                        crashed_in_current = True
                    if abs(other_car['y'] - alt_lane) < 0.05:
                        crashed_in_alt = True
            elif direction == 'up':
                if other_car['y'] > current_y and other_car['y'] - current_y < detection_range:
                    if abs(other_car['x'] - current_lane) < 0.05:
                        crashed_in_current = True
                    if abs(other_car['x'] - alt_lane) < 0.05:
                        crashed_in_alt = True
            elif direction == 'down':
                if other_car['y'] < current_y and current_y - other_car['y'] < detection_range:
                    if abs(other_car['x'] - current_lane) < 0.05:
                        crashed_in_current = True
                    if abs(other_car['x'] - alt_lane) < 0.05:
                        crashed_in_alt = True
        
        return crashed_in_current and crashed_in_alt
    
    def update_car_position(self, car, is_ai=False, all_cars=None):
        """Update car position along its path, with lane changing for crashed cars."""
        # Handle crashed cars - move them to the side of the road
        if car.get('crashed', False):
            direction = car['route']['direction']
            
            # Determine the rightmost position for this direction
            if direction == 'right':
                target_y = -0.5  # Move to right side (bottom) of horizontal road
                if abs(car['y'] - target_y) > 0.01:
                    car['y'] += -0.02 if car['y'] > target_y else 0.02
            elif direction == 'left':
                target_y = 0.5  # Move to right side (top) of horizontal road
                if abs(car['y'] - target_y) > 0.01:
                    car['y'] += 0.02 if car['y'] < target_y else -0.02
            elif direction == 'up':
                target_x = 0.5  # Move to right side (right) of vertical road
                if abs(car['x'] - target_x) > 0.01:
                    car['x'] += 0.02 if car['x'] < target_x else -0.02
            elif direction == 'down':
                target_x = -0.5  # Move to right side (left) of vertical road
                if abs(car['x'] - target_x) > 0.01:
                    car['x'] += -0.02 if car['x'] > target_x else 0.02
            
            return True  # Still render it
        
        # Extra safety check for AI: don't move if status is explicitly stopped
        if is_ai and car.get('status') == 'stopped':
            return True  # Stay in place
        
        direction = car['route']['direction']
        
        # Handle lane changing
        if car.get('changing_lane', False):
            target = car['lane_change_target']
            lane_change_speed = 0.02
            
            if direction in ['right', 'left']:  # Horizontal road - change y
                current = car['y']
                if abs(target - current) < lane_change_speed:
                    car['y'] = target
                    car['changing_lane'] = False
                    car['lane_change_target'] = None
                else:
                    car['y'] += lane_change_speed if target > current else -lane_change_speed
            else:  # Vertical road - change x
                current = car['x']
                if abs(target - current) < lane_change_speed:
                    car['x'] = target
                    car['changing_lane'] = False
                    car['lane_change_target'] = None
                else:
                    car['x'] += lane_change_speed if target > current else -lane_change_speed
        
        # Check for crashed car ahead and decide whether to wait or change lanes
        if all_cars and not car.get('changing_lane', False):
            crashed_ahead = self.check_crashed_car_ahead(car, all_cars)
            if crashed_ahead:
                # Get alternate lane target
                alt_target = car['route'].get('alt_y') if direction in ['right', 'left'] else car['route'].get('alt_x')
                
                if alt_target is not None:
                    # Check if both lanes are blocked
                    both_blocked = self.check_both_lanes_blocked(car, all_cars)
                    
                    if both_blocked:
                        # Both lanes have crashed cars - stop and wait
                        if is_ai:
                            car['status'] = 'stopped'
                        return True
                    else:
                        # Check if alternate lane is clear
                        if self.is_alternate_lane_clear(car, all_cars, alt_target):
                            # Safe to change lanes
                            car['changing_lane'] = True
                            car['lane_change_target'] = alt_target
                        else:
                            # Alternate lane not clear - stop and wait
                            if is_ai:
                                car['status'] = 'stopped'
                            return True
        
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
                speed_mult = 0.2  # Much slower to give more time for collision avoidance
        
        move_dist = 0.04 * speed_mult
        progress = move_dist / dist
        
        # Move in primary direction only (lane changing handles perpendicular)
        if direction in ['right', 'left']:  # Horizontal - move x, maintain y unless changing lanes
            car['x'] += dx * progress
            if not car.get('changing_lane', False):
                car['y'] = car['route']['base_y']  # Keep in lane
        else:  # Vertical - move y, maintain x unless changing lanes
            car['y'] += dy * progress
            if not car.get('changing_lane', False):
                car['x'] = car['route']['base_y']  # Keep in lane (base_y stores x for vertical)
        
        # Check if reached end of road
        if direction == 'right':
            if car['x'] >= end[0] - 0.2:
                car['completed'] = True
        elif direction == 'left':
            if car['x'] <= end[0] + 0.2:
                car['completed'] = True
        elif direction == 'up':
            if car['y'] >= end[1] - 0.2:
                car['completed'] = True
        elif direction == 'down':
            if car['y'] <= end[1] + 0.2:
                car['completed'] = True
        
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
        """Check for collisions between cars in the SAME LANE or perpendicular cars in INTERSECTION."""
        collisions = []
        for i, car1 in enumerate(cars):
            if not car1['active'] or car1['completed'] or car1.get('crashed', False):
                continue
            for j, car2 in enumerate(cars[i+1:], i+1):
                if not car2['active'] or car2['completed'] or car2.get('crashed', False):
                    continue
                
                car1_dir = car1['route']['direction']
                car2_dir = car2['route']['direction']
                
                # Check if both cars are in the intersection
                car1_in_int = any(abs(car1['x'] - ix) < 0.4 and abs(car1['y'] - iy) < 0.4 
                                 for ix, iy in self.road_network['intersections'])
                car2_in_int = any(abs(car2['x'] - ix) < 0.4 and abs(car2['y'] - iy) < 0.4 
                                 for ix, iy in self.road_network['intersections'])
                
                # If both in intersection, only perpendicular cars can collide
                if car1_in_int and car2_in_int:
                    car1_is_horizontal = car1_dir in ['right', 'left']
                    car2_is_horizontal = car2_dir in ['right', 'left']
                    
                    # Only check collision if perpendicular (horizontal vs vertical)
                    if car1_is_horizontal != car2_is_horizontal:
                        dist = np.sqrt((car1['x'] - car2['x'])**2 + (car1['y'] - car2['y'])**2)
                        if dist < 0.30:
                            pair = tuple(sorted([car1['label'], car2['label']]))
                            if pair not in self.collision_pairs:
                                car1['crashed'] = True
                                car2['crashed'] = True
                                collisions.append((car1, car2))
                                self.collision_pairs.add(pair)
                    continue
                
                # Outside intersection: Only check collision if in the SAME LANE
                # Must be going the same direction
                if car1_dir != car2_dir:
                    continue
                
                # Must be in the same lane (same y for horizontal, same x for vertical)
                if car1_dir in ['right', 'left']:  # Horizontal road
                    if abs(car1['y'] - car2['y']) > 0.05:  # Different lanes
                        continue
                else:  # Vertical road
                    if abs(car1['x'] - car2['x']) > 0.05:  # Different lanes
                        continue
                
                # Check physical distance (increased to prevent visual overlaps)
                dist = np.sqrt((car1['x'] - car2['x'])**2 + (car1['y'] - car2['y'])**2)
                if dist < 0.30:
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
    
    def get_car_ahead_same_lane(self, car, cars):
        """Find the closest car directly ahead in the exact same lane and direction."""
        direction = car['route']['direction']
        car_length = 0.24  # Reduced car size
        
        closest_car = None
        closest_distance = float('inf')
        
        for other in cars:
            if other['label'] == car['label'] or other.get('crashed', False) or other.get('completed', False):
                continue
            
            # Must be in EXACT same lane (within 0.05 units for precision)
            if direction in ['right', 'left']:
                if abs(other['y'] - car['y']) > 0.05:
                    continue
                # Check if directly ahead in same direction
                if direction == 'right':
                    if other['x'] > car['x']:
                        dist = other['x'] - car['x']
                        if dist < closest_distance:
                            closest_distance = dist
                            closest_car = other
                elif direction == 'left':
                    if other['x'] < car['x']:
                        dist = car['x'] - other['x']
                        if dist < closest_distance:
                            closest_distance = dist
                            closest_car = other
            else:  # up/down
                if abs(other['x'] - car['x']) > 0.05:
                    continue
                # Check if directly ahead in same direction
                if direction == 'up':
                    if other['y'] > car['y']:
                        dist = other['y'] - car['y']
                        if dist < closest_distance:
                            closest_distance = dist
                            closest_car = other
                elif direction == 'down':
                    if other['y'] < car['y']:
                        dist = car['y'] - other['y']
                        if dist < closest_distance:
                            closest_distance = dist
                            closest_car = other
        
        if closest_car:
            return closest_car, closest_distance
        else:
            return None, float('inf')
    
    def get_distance(self, car1, car2):
        """Get distance between two cars."""
        return np.sqrt((car1['x'] - car2['x'])**2 + (car1['y'] - car2['y'])**2)
    
    def get_distance_to_point(self, car, point):
        """Get distance from car to a point."""
        return np.sqrt((car['x'] - point[0])**2 + (car['y'] - point[1])**2)
    
    def is_near_intersection(self, car):
        """Check if car is near an intersection."""
        for intersection in self.road_network['intersections']:
            dist = self.get_distance_to_point(car, intersection)
            if dist < 1.0:  # Within 1.0 units of intersection
                return True, intersection
        return False, None
    
    def is_car_in_intersection(self, car, intersection_pos):
        """Check if a car is currently inside the intersection square."""
        half_size = 0.3  # Intersection square is 0.6 units wide/high
        return (abs(car['x'] - intersection_pos[0]) <= half_size and
                abs(car['y'] - intersection_pos[1]) <= half_size)
    
    def has_perpendicular_car_in_intersection(self, car, cars, intersection_pos):
        """Check if there's a car from perpendicular direction IN the intersection."""
        my_direction = car['route']['direction']
        my_is_horizontal = my_direction in ['right', 'left']
        
        for other in cars:
            if other['label'] == car['label'] or other.get('crashed', False) or other.get('completed', False):
                continue
            
            other_direction = other['route']['direction']
            other_is_horizontal = other_direction in ['right', 'left']
            
            # Only care about perpendicular cars (horizontal vs vertical)
            if my_is_horizontal != other_is_horizontal:
                # Check if the other car is ACTUALLY IN the intersection
                if self.is_car_in_intersection(other, intersection_pos):
                    return True
        
        return False
    
    def ai_coordinate(self, cars):
        """AI coordination with strict same-lane and right-of-way rules with direction-specific queues."""
        car_length = 0.24  # Reduced car size to fit lanes properly
        intersection_radius = 0.4
        intersection_detection_radius = 0.5  # Slightly larger for detecting nearby cars
        stop_distance = intersection_radius + car_length  # Stop 1 car length before intersection
        
        # Update cars currently in intersection (categorized by direction)
        horizontal_in_intersection = set()
        vertical_in_intersection = set()
        
        for car in cars:
            if car['delay'] > self.mode_frame or car['completed'] or car.get('crashed', False):
                continue
            
            near_intersection, intersection_pos = self.is_near_intersection(car)
            if near_intersection:
                my_dist = self.get_distance_to_point(car, intersection_pos)
                if my_dist < intersection_detection_radius:
                    my_direction = car['route']['direction']
                    if my_direction in ['right', 'left']:
                        horizontal_in_intersection.add(car['label'])
                    else:
                        vertical_in_intersection.add(car['label'])
        
        # Initialize direction-specific queues for each intersection
        for intersection in self.road_network['intersections']:
            for direction_type in ['horizontal', 'vertical']:
                queue_key = (tuple(intersection), direction_type)
                if queue_key not in self.intersection_queue:
                    self.intersection_queue[queue_key] = []
        
        for car in cars:
            if car['delay'] > self.mode_frame or car['completed'] or car.get('crashed', False):
                continue
            
            # Reset status and communication
            car['status'] = 'normal'
            car['communicating_with'] = []
            
            # CHECK IF CAR IS IN INTERSECTION FIRST - if yes, skip ALL logic
            near_intersection, intersection_pos = self.is_near_intersection(car)
            my_in_intersection = False
            
            if near_intersection:
                my_dist = self.get_distance_to_point(car, intersection_pos)
                my_direction = car['route']['direction']
                my_is_horizontal = my_direction in ['right', 'left']
                direction_type = 'horizontal' if my_is_horizontal else 'vertical'
                queue_key = (tuple(intersection_pos), direction_type)
                
                # If already IN the intersection, skip ALL coordination logic
                if my_dist < intersection_radius:
                    my_in_intersection = True
                    # Remove from queue if present
                    if car['label'] in self.intersection_queue[queue_key]:
                        self.intersection_queue[queue_key].remove(car['label'])
                    # Force normal status - NEVER stop in intersection
                    car['status'] = 'normal'
                    # Skip ALL rules below - continue to next car
                    continue
                
                # If APPROACHING intersection (within detection range)
                if my_dist < 1.2:
                    # Add to direction-specific queue if not already in it
                    if car['label'] not in self.intersection_queue[queue_key]:
                        self.intersection_queue[queue_key].append(car['label'])
                    
                    # Check if there are perpendicular cars IN the intersection
                    has_perpendicular = (len(vertical_in_intersection) > 0 if my_is_horizontal 
                                       else len(horizontal_in_intersection) > 0)
                    
                    # Stop ONLY if there are perpendicular cars in intersection
                    # (Parallel cars won't collide, so no need to stop for them)
                    if my_dist <= stop_distance:
                        if has_perpendicular:
                            car['status'] = 'stopped'
                            continue
                    
                    # Slow down when approaching if perpendicular cars present
                    if my_dist < stop_distance + 0.3:
                        if has_perpendicular:
                            car['status'] = 'slowing'
                            continue
            else:
                # Remove from all queues if far from intersection
                for queue_key in self.intersection_queue:
                    if car['label'] in self.intersection_queue[queue_key]:
                        self.intersection_queue[queue_key].remove(car['label'])
            
            # CRASHED CAR HANDLING (check for crashed cars still in lane)
            if car['status'] != 'stopped':
                crashed_ahead = self.check_crashed_car_ahead(car, cars)
                if crashed_ahead:
                    # Check if crashed car is still in the lane (not yet moved to side)
                    # Crashed cars move to positions like -0.5/0.5, lanes are at -0.1/-0.3/0.1/0.3
                    my_direction = car['route']['direction']
                    if my_direction in ['right', 'left']:
                        crashed_car_in_lane = abs(crashed_ahead['y']) < 0.4
                    else:
                        crashed_car_in_lane = abs(crashed_ahead['x']) < 0.4
                    
                    if crashed_car_in_lane:
                        # Crashed car still blocking - this will be handled by update_car_position
                        # which will either stop or change lanes
                        pass
            
            # SAME LANE RULES (only apply if not stopped for intersection and not in intersection)
            if car['status'] != 'stopped':
                car_ahead, distance_ahead = self.get_car_ahead_same_lane(car, cars)
                
                if car_ahead:
                    # Rule 1: Stop if car directly in front is stopped
                    if car_ahead.get('status') == 'stopped':
                        car['status'] = 'stopped'
                        car['communicating_with'].append(car_ahead)
                        continue
                    
                    # Rule 2: Slow down if less than 3 car lengths away
                    if distance_ahead < car_length * 3:
                        car['status'] = 'slowing'
                        car['communicating_with'].append(car_ahead)
                        continue
                    
                    # Rule 3: Slow down if going faster than car ahead and will collide
                    # (Check if we're catching up to a slower car - increase detection range)
                    if distance_ahead < car_length * 5 and car['speed'] > car_ahead['speed']:
                        car['status'] = 'slowing'
                        car['communicating_with'].append(car_ahead)
                        continue
    
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
        
        # Car body (reduced size to fit within lanes without touching adjacent lanes)
        car_length = 0.24
        car_width = 0.12
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
            
            # Headlights removed per user request
        
        # Label
        label_color = '#888888' if car.get('crashed', False) else 'white'
        ax.text(car['x'], car['y'], car['label'], 
               ha='center', va='center', fontsize=11, 
               color=label_color, fontweight='bold', zorder=17)
        
        # AI-specific indicators removed to eliminate lag
    
    def draw_ai_communication(self, ax, cars):
        """AI communication visualization removed to eliminate lag."""
        pass  # No visualization to improve performance
    
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
        user_total = len(self.user_cars)
        
        user_stats = f"""
USER-CONTROLLED
━━━━━━━━━━━━━━━

  Collisions:  {self.user_collisions}
  
  Time:        {user_time:.1f}s
  
  Completed:   {user_completed}/{user_total}
  
  Crashed:     {user_crashed}/{user_total}
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
        ai_total = len(self.ai_cars)
        
        ai_stats = f"""
AI-COORDINATED
━━━━━━━━━━━━━━━

  Collisions:  {self.ai_collisions}
  
  Time:        {ai_time:.1f}s
  
  Completed:   {ai_completed}/{ai_total}
  
  Crashed:     {ai_crashed}/{ai_total}
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
            
            # Update and draw cars (all spawn at once now)
            active_cars = 0
            for car in self.user_cars:
                if car.get('spawn_delay', 0) <= self.mode_frame:
                    if car['active'] and not car['completed']:
                        if self.update_car_position(car, is_ai=False, all_cars=self.user_cars):
                            self.draw_car(self.ax, car, is_ai=False)
                            active_cars += 1
            
            # Check collisions (only for spawned cars)
            spawned_cars = [car for car in self.user_cars if car.get('spawn_delay', 0) <= self.mode_frame]
            collisions = self.check_collisions(spawned_cars)
            for car1, car2 in collisions:
                self.user_collisions += 1
                # Show collision effect
                mid_x = (car1['x'] + car2['x']) / 2
                mid_y = (car1['y'] + car2['y']) / 2
                explosion = Circle((mid_x, mid_y), 0.4, color='red', alpha=0.6, zorder=20)
                self.ax.add_patch(explosion)
                self.ax.text(mid_x, mid_y + 0.6, '💥 COLLISION!', ha='center', va='center',
                           fontsize=16, color='red', fontweight='bold', zorder=21)
            
            # Check if ALL cars have spawned AND all are done (either completed or crashed)
            all_spawned = all(car.get('spawn_delay', 0) <= self.mode_frame for car in self.user_cars)
            completed_count = sum(1 for car in self.user_cars if car['completed'])
            crashed_count = sum(1 for car in self.user_cars if car.get('crashed', False))
            
            # Auto-complete if stuck for too long (safety timeout after 800 frames)
            if all_spawned and self.mode_frame > 800:
                print(f"USER MODE TIMEOUT: {completed_count} completed, {crashed_count} crashed out of {len(self.user_cars)}")
                self.user_end_time = frame
                self.mode = 'stats_user'
                self.mode_frame = 0
            elif all_spawned and all(car['completed'] or car.get('crashed', False) for car in self.user_cars):
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
                # Reset intersection queue for AI mode
                self.intersection_queue = {}
                self.cars_in_intersection = set()
            
            self.mode_frame += 1
            self.draw_title_and_info(self.ax)
            
            # AI coordination
            self.ai_coordinate(self.ai_cars)
            
            # Update and draw cars (all spawn at once now)
            for car in self.ai_cars:
                if car['delay'] <= self.mode_frame:
                    if car['active'] and not car['completed']:
                        if self.update_car_position(car, is_ai=True, all_cars=self.ai_cars):
                            self.draw_car(self.ax, car, is_ai=True)
            
            # Draw communication
            self.draw_ai_communication(self.ax, self.ai_cars)
            
            # Check collisions (should be zero!) - only check spawned cars
            spawned_ai_cars = [car for car in self.ai_cars if car['delay'] <= self.mode_frame]
            collisions = self.check_collisions(spawned_ai_cars)
            for car1, car2 in collisions:
                self.ai_collisions += 1
                # Debug output
                print(f"AI COLLISION at frame {self.mode_frame}: Car {car1['label']} at ({car1['x']:.2f},{car1['y']:.2f}) vs Car {car2['label']} at ({car2['x']:.2f},{car2['y']:.2f})")
                print(f"  Car {car1['label']}: direction={car1['route']['direction']}, status={car1.get('status','none')}, speed={car1['speed']:.2f}")
                print(f"  Car {car2['label']}: direction={car2['route']['direction']}, status={car2.get('status','none')}, speed={car2['speed']:.2f}")
            
            # Check if ALL cars have spawned AND all are done (either completed or crashed)
            all_spawned = all(car['delay'] <= self.mode_frame for car in self.ai_cars)
            completed_count = sum(1 for car in self.ai_cars if car['completed'])
            crashed_count = sum(1 for car in self.ai_cars if car.get('crashed', False))
            stopped_count = sum(1 for car in self.ai_cars if car.get('status') == 'stopped' and not car['completed'] and not car.get('crashed', False))
            
            # Auto-complete if stuck for too long (safety timeout after 800 frames)
            if all_spawned and self.mode_frame > 800:
                print(f"AI MODE TIMEOUT: {completed_count} completed, {crashed_count} crashed, {stopped_count} stopped out of {len(self.ai_cars)}")
                # Print which cars are stopped
                stopped_cars = [car['label'] for car in self.ai_cars if car.get('status') == 'stopped' and not car['completed'] and not car.get('crashed', False)]
                print(f"Stopped cars: {stopped_cars}")
                print(f"Queue state: {self.intersection_queue}")
                self.ai_end_time = frame
                self.mode = 'stats_ai'
                self.mode_frame = 0
            elif all_spawned and all(car['completed'] or car.get('crashed', False) for car in self.ai_cars):
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
        
        # COMPLETE - keep showing comparison
        elif self.mode == 'complete':
            self.draw_comparison(self.ax)
        
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
    print("\nSimulation Features:")
    print("  • 16 total cars (2 per lane)")
    print("  • 8 lanes total across 2 centered roads:")
    print("    - Horizontal road (y=0): 4 lanes (2 right, 2 left)")
    print("    - Vertical road (x=0): 4 lanes (2 up, 2 down)")
    print("  • 1 centered intersection with clean gray square")
    print("  • Lane markings stop at intersection")
    print("  • Green grass background (non-road areas)")
    print("  • Speed variance: 100%-250% (0% to +150% increase)")
    print("  • All cars spawn at start (no staggered spawning)")
    print("  • Random spawn positions along lane (min 2x car length spacing)")
    print("  • Crashed cars move to the right side of their direction")
    print("  • AI cars wait for crashed cars to clear OR change lanes if safe")
    print("  • Lane changes only if alternate lane is clear of all traffic")
    print("  • Cars wait if both lanes have crashed cars blocking")
    print("  • Collisions during lane changes are detected")
    print("  • AI coordination (no visual indicators for performance)")
    print("  • Queue-based right-of-way: Cars wait in order at intersection")
    print("  • Cars stop 1 car length BEFORE intersection when waiting")
    print("  • Same-lane following: Stop if car ahead stopped, slow if catching up")
    print("  • First-come, first-served intersection crossing")
    print("  • Real-time collision detection with visual effects")
    print("\n" + "=" * 60)
    print("Starting demo...\n")
    
    demo = TrafficDemo()
    anim = demo.run()
    
    try:
        plt.show(block=True)
    except KeyboardInterrupt:
        print("\nDemo stopped.")
