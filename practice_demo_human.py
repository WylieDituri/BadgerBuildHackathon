"""
Simple Traffic Demo - Human Driving
Cars stop when perpendicular cars are in intersection
Cars stop when another car in their lane is stopped ahead
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.patches import Rectangle, Polygon, FancyBboxPatch, Wedge

class TrafficDemo:
    def __init__(self):
        self.fig, self.ax = plt.subplots(1, 1, figsize=(12, 10))
        self.fig.patch.set_facecolor('#2b2b2b')
        
        # Animation state
        self.frame = 0
        
        # Road parameters - more compact grid
        self.intersection_size = 0.5
        
        # Car parameters
        self.car_length = 0.35
        self.car_width = 0.18
        self.lane_offset = 0.125  # How far from center each lane is (centered in lane)
        
        # Grid dimensions (more compact)
        self.x_min, self.x_max = -4.0, 4.0
        self.y_min, self.y_max = -3.0, 3.0
        
        # Timer tracking
        self.total_frames = 0  # Track total frames elapsed (doesn't reset on animation repeat)
        self.end_frame = None
        self.all_cars_reached_destination = False
        
        # Initialize 12 cars (3 per direction)
        self.init_cars()
    
    def init_cars(self):
        """Initialize 12 cars, 3 per direction."""
        self.cars = []
        
        # Calculate speeds based on time to cross
        # Animation runs at 20 fps (interval=50ms)
        fps = 20
        horizontal_distance = self.x_max - self.x_min  # 8.0 units
        vertical_distance = self.y_max - self.y_min    # 6.0 units
        
        # Define road positions (matching draw_roads)
        horizontal_y_positions = [-2.2, 0, 2.2]  # Bottom, center, top
        vertical_x_positions = [-3.0, 0, 3.0]    # Left, center, right
        
        # ALL CARS USE THE SAME SPEED (slowest car speed - left-going cars)
        # This simulates realistic human driving where everyone doesn't know optimal speed
        uniform_speed = (horizontal_distance / (6 * fps)) * 0.95  # Slowest speed, 5% slower
        
        # Cars going RIGHT (one on each horizontal road) - all use uniform speed
        colors_right = ['#FF4444', '#FF6666', '#FF8888']
        for i, y_pos in enumerate(horizontal_y_positions):
            base_speed = uniform_speed
            car_data = {
                'x': self.x_min,
                'y': y_pos - self.lane_offset,
                'angle': 0,
                'vx': base_speed,
                'vy': 0,
                'color': colors_right[i],
                'label': f'R{i+1}',
                'active': True,
                'turning': False,
                'turn_stage': 0,
                'original_speed': base_speed,
                'turn_speed': base_speed * 0.4,
                'direction': 'horizontal'
            }
            
            # Top road car (R3) will turn RIGHT at intersection 3 (top-right)
            if i == 2:  # Top horizontal road (near intersection 1 -> 3 -> 9)
                car_data['should_turn'] = True
                car_data['turn_x'] = vertical_x_positions[-1]  # x = 3.0
                car_data['turn_y'] = y_pos  # y = 2.2
                car_data['turn_direction'] = 'right'
                car_data['dest_x'] = 3.0
                car_data['dest_y'] = -2.2  # Goes down to bottom edge
            # Middle road car (R2) will turn LEFT at intersection 6 (middle-right)
            elif i == 1:  # Middle horizontal road (intersection 4 -> 6 -> 3)
                car_data['should_turn'] = True
                car_data['turn_x'] = vertical_x_positions[-1]  # x = 3.0
                car_data['turn_y'] = y_pos  # y = 0
                car_data['turn_direction'] = 'left'
                car_data['dest_x'] = 3.0
                car_data['dest_y'] = 2.2  # Goes up to top edge
            # Bottom road car (R1) will turn LEFT at intersection 9 (bottom-right)
            elif i == 0:  # Bottom horizontal road (intersection 7 -> 9 -> 3)
                car_data['should_turn'] = True
                car_data['turn_x'] = vertical_x_positions[-1]  # x = 3.0
                car_data['turn_y'] = y_pos  # y = -2.2
                car_data['turn_direction'] = 'left'
                car_data['dest_x'] = 3.0
                car_data['dest_y'] = 2.2  # Goes up to top edge
            else:
                car_data['should_turn'] = False
                car_data['dest_x'] = self.x_max
                car_data['dest_y'] = y_pos - self.lane_offset
            
            car_data['reached_destination'] = False
            car_data['stopped'] = False  # Human driving: track if car is stopped
            car_data['stop_cooldown'] = 0  # Frames to wait after perpendicular car leaves intersection
            car_data['waiting_for_perpendicular'] = False  # Track if waiting for perpendicular car
            self.cars.append(car_data)
        
        # Cars going LEFT (one on each horizontal road) - all use uniform speed
        colors_left = ['#4444FF', '#6666FF', '#8888FF']
        for i, y_pos in enumerate(horizontal_y_positions):
            base_speed = uniform_speed
            car_data = {
                'x': self.x_max,
                'y': y_pos + self.lane_offset,
                'angle': np.pi,
                'vx': -base_speed,
                'vy': 0,
                'color': colors_left[i],
                'label': f'L{i+1}',
                'active': True,
                'turning': False,
                'turn_stage': 0,
                'original_speed': base_speed,
                'turn_speed': base_speed * 0.4,
                'direction': 'horizontal'
            }
            
            # L1 (bottom road) will turn RIGHT at intersection 8 (bottom-center) to go up to intersection 2
            if i == 0:  # Bottom horizontal road (going left -> turn right at 8 -> go to 2)
                car_data['should_turn'] = True
                car_data['turn_x'] = vertical_x_positions[1]  # x = 0 (middle vertical)
                car_data['turn_y'] = y_pos  # y = -2.2 (bottom row)
                car_data['turn_direction'] = 'right_from_horizontal'
                # Speed up by 87.5% (1.50 * 1.25 = 1.875), then reduce by 5%
                car_data['vx'] = -base_speed * 1.875
                car_data['dest_x'] = 0.0
                car_data['dest_y'] = 2.2  # Goes up to intersection 2
            else:
                car_data['should_turn'] = False
                car_data['dest_x'] = self.x_min
                car_data['dest_y'] = y_pos + self.lane_offset
            
            car_data['reached_destination'] = False
            car_data['stopped'] = False
            car_data['stop_cooldown'] = 0  # Frames to wait after perpendicular car leaves intersection
            car_data['waiting_for_perpendicular'] = False  # Track if waiting for perpendicular car
            self.cars.append(car_data)
        
        # Cars going UP (one on each vertical road) - all use uniform speed
        colors_up = ['#44FF44', '#66FF66', '#88FF88']
        for i, x_pos in enumerate(vertical_x_positions):
            car_data = {
                'x': x_pos + self.lane_offset,
                'y': self.y_min,
                'angle': np.pi/2,
                'vx': 0,
                'vy': uniform_speed,  # Same speed for all cars
                'color': colors_up[i],
                'label': f'U{i+1}',
                'active': True,
                'turning': False,
                'should_turn': False,
                'dest_x': x_pos + self.lane_offset,
                'dest_y': self.y_max,
                'reached_destination': False,
                'stopped': False,
                'stop_cooldown': 0,  # Frames to wait after perpendicular car leaves intersection
                'waiting_for_perpendicular': False,  # Track if waiting for perpendicular car
                'direction': 'vertical'
            }
            self.cars.append(car_data)
        
        # Cars going DOWN (one on each vertical road) - all use uniform speed
        colors_down = ['#FFFF44', '#FFFF66', '#FFFF88']
        for i, x_pos in enumerate(vertical_x_positions):
            car_data = {
                'x': x_pos - self.lane_offset,
                'y': self.y_max,
                'angle': -np.pi/2,
                'vx': 0,
                'vy': -uniform_speed,  # Same speed for all cars (negative for down)
                'color': colors_down[i],
                'label': f'D{i+1}',
                'active': True,
                'turning': False,
                'turn_stage': 0,
                'original_speed': uniform_speed,
                'turn_speed': uniform_speed * 0.4,
                'direction': 'vertical'
            }
            
            # D1 (left vertical road) starts slow, waits for R3 to pass, then speeds up
            if i == 0:  # Left vertical road at top going down
                car_data['waiting_for_r3'] = True
                car_data['normal_speed'] = uniform_speed
                car_data['vy'] = -uniform_speed * 0.4  # Start at 40% speed
                car_data['dest_x'] = x_pos - self.lane_offset
                car_data['dest_y'] = self.y_min
            
            # Middle vertical car (D2) will turn LEFT at intersection 8 (bottom-center)
            if i == 1:  # Middle vertical road (intersection 2 -> 5 -> 8 -> 7)
                car_data['should_turn'] = True
                car_data['turn_x'] = x_pos  # x = 0
                car_data['turn_y'] = horizontal_y_positions[0]  # y = -2.2 (bottom row)
                car_data['turn_direction'] = 'left_from_vertical'
                car_data['dest_x'] = -3.0
                car_data['dest_y'] = -2.2  # Goes to intersection 7
            else:
                car_data['should_turn'] = False
                car_data['dest_x'] = x_pos - self.lane_offset
                car_data['dest_y'] = self.y_min
            
            car_data['reached_destination'] = False
            car_data['stopped'] = False
            car_data['stop_cooldown'] = 0  # Frames to wait after perpendicular car leaves intersection
            car_data['waiting_for_perpendicular'] = False  # Track if waiting for perpendicular car
            self.cars.append(car_data)
        
        print(f"Initialized {len(self.cars)} cars (3 per direction)")
    
    def draw_roads(self, ax):
        """Draw 3x3 grid of roads with intersections."""
        ax.set_xlim(self.x_min - 0.5, self.x_max + 0.5)
        ax.set_ylim(self.y_min - 0.5, self.y_max + 0.5)
        ax.set_facecolor('#1a4d1a')  # Green grass
        ax.axis('off')
        
        road_width = 0.5  # Width for exactly 2 lanes (one each direction)
        
        # Define road positions for 3x3 grid (more compact)
        horizontal_y_positions = [-2.2, 0, 2.2]  # Bottom, center, top horizontal
        vertical_x_positions = [-3.0, 0, 3.0]    # Left, center, right vertical
        
        # Draw all vertical roads
        for x_pos in vertical_x_positions:
            ax.add_patch(Rectangle((x_pos - road_width/2, self.y_min), 
                                  road_width, self.y_max - self.y_min, 
                                  facecolor='#404040', edgecolor='none', zorder=1))
        
        # Draw all horizontal roads
        for y_pos in horizontal_y_positions:
            ax.add_patch(Rectangle((self.x_min, y_pos - road_width/2), 
                                  self.x_max - self.x_min, road_width, 
                                  facecolor='#404040', edgecolor='none', zorder=1))
        
        # Draw intersections at each crossing point
        intersections = []
        for x_pos in vertical_x_positions:
            for y_pos in horizontal_y_positions:
                intersections.append((x_pos, y_pos))
        
        # Draw each intersection with rounded corners
        half_size = self.intersection_size / 2
        road_half = road_width / 2
        intersection_radius = 0.15
        
        for int_x, int_y in intersections:
            # Main intersection square
            ax.add_patch(Rectangle((int_x - half_size, int_y - half_size), 
                                  self.intersection_size, self.intersection_size,
                                  facecolor='#404040', edgecolor='none', zorder=2))
            
            # Draw rounded corner wedges
            corners = [
                (-road_half, -road_half, 180, 270),  # Bottom-left
                (road_half, -road_half, 270, 360),   # Bottom-right
                (road_half, road_half, 0, 90),       # Top-right
                (-road_half, road_half, 90, 180),    # Top-left
            ]
            
            for cx_offset, cy_offset, start_angle, end_angle in corners:
                wedge = Wedge((int_x + cx_offset, int_y + cy_offset), 
                             intersection_radius, start_angle, end_angle,
                             facecolor='#404040', edgecolor='none', zorder=3)
                ax.add_patch(wedge)
        
        # Draw yellow center lines (stop at intersection edges)
        # Horizontal center lines
        for y_pos in horizontal_y_positions:
            # From left edge to first intersection
            ax.plot([self.x_min, vertical_x_positions[0] - half_size], [y_pos, y_pos], 
                   'y-', linewidth=2, zorder=4)
            
            # Between intersections
            for i in range(len(vertical_x_positions) - 1):
                x1 = vertical_x_positions[i] + half_size
                x2 = vertical_x_positions[i + 1] - half_size
                ax.plot([x1, x2], [y_pos, y_pos], 
                       'y-', linewidth=2, zorder=4)
            
            # From last intersection to right edge
            ax.plot([vertical_x_positions[-1] + half_size, self.x_max], [y_pos, y_pos], 
                   'y-', linewidth=2, zorder=4)
        
        # Vertical center lines
        for x_pos in vertical_x_positions:
            # From bottom edge to first intersection
            ax.plot([x_pos, x_pos], [self.y_min, horizontal_y_positions[0] - half_size], 
                   'y-', linewidth=2, zorder=4)
            
            # Between intersections
            for i in range(len(horizontal_y_positions) - 1):
                y1 = horizontal_y_positions[i] + half_size
                y2 = horizontal_y_positions[i + 1] - half_size
                ax.plot([x_pos, x_pos], [y1, y2], 
                       'y-', linewidth=2, zorder=4)
            
            # From last intersection to top edge
            ax.plot([x_pos, x_pos], [horizontal_y_positions[-1] + half_size, self.y_max], 
                   'y-', linewidth=2, zorder=4)
    
    def check_destination_reached(self, car):
        """Check if a car has reached its destination."""
        if car.get('reached_destination', False):
            return True
        
        dest_x = car.get('dest_x', None)
        dest_y = car.get('dest_y', None)
        
        if dest_x is not None and dest_y is not None:
            # Check if car is within 0.3 units of destination
            distance = np.sqrt((car['x'] - dest_x)**2 + (car['y'] - dest_y)**2)
            if distance < 0.3:
                car['reached_destination'] = True
                car['active'] = False
                return True
        
        return False
    
    def check_all_destinations(self):
        """Check if all cars have reached their destinations."""
        return all(car.get('reached_destination', False) for car in self.cars)
    
    def is_in_intersection(self, car):
        """Check if a car is currently inside any intersection."""
        # Define road positions
        horizontal_y_positions = [-2.2, 0, 2.2]
        vertical_x_positions = [-3.0, 0, 3.0]
        
        half_size = self.intersection_size / 2
        
        for x_pos in vertical_x_positions:
            for y_pos in horizontal_y_positions:
                if (abs(car['x'] - x_pos) < half_size and 
                    abs(car['y'] - y_pos) < half_size):
                    return True, (x_pos, y_pos)
        return False, None
    
    def is_intersection_ahead(self, car, int_x, int_y):
        """Check if an intersection is ahead of the car based on its direction of travel."""
        if car['direction'] == 'horizontal':
            if car['vx'] > 0:  # Going right
                return int_x > car['x']
            else:  # Going left
                return int_x < car['x']
        else:  # vertical
            if car['vy'] > 0:  # Going up
                return int_y > car['y']
            else:  # Going down
                return int_y < car['y']
    
    def check_perpendicular_car_in_intersection(self, car, intersection_pos):
        """Check if there's a perpendicular car in the intersection."""
        my_direction = car['direction']
        
        for other_car in self.cars:
            if other_car['label'] == car['label'] or not other_car['active']:
                continue
            
            # Check if other car is perpendicular direction
            if my_direction != other_car['direction']:
                # Check if other car is in the same intersection
                other_in_int, other_int_pos = self.is_in_intersection(other_car)
                if other_in_int and other_int_pos == intersection_pos:
                    return True
        
        return False
    
    def check_car_stopped_ahead_in_lane(self, car):
        """Check if there's a stopped car ahead in the same lane."""
        my_dir = car['direction']
        
        for other_car in self.cars:
            if other_car['label'] == car['label'] or not other_car['active']:
                continue
            
            # Must be same direction type (horizontal or vertical)
            if other_car['direction'] != my_dir:
                continue
            
            # Check if other car is stopped
            if not other_car.get('stopped', False):
                continue
            
            # Check if in same lane and ahead
            if my_dir == 'horizontal':
                # Same lane if same y position
                if abs(car['y'] - other_car['y']) > 0.05:
                    continue
                
                # Check if ahead
                if car['vx'] > 0:  # Going right
                    if other_car['x'] > car['x'] and other_car['x'] - car['x'] < 1.0:
                        return True
                else:  # Going left
                    if other_car['x'] < car['x'] and car['x'] - other_car['x'] < 1.0:
                        return True
            
            else:  # vertical
                # Same lane if same x position
                if abs(car['x'] - other_car['x']) > 0.05:
                    continue
                
                # Check if ahead
                if car['vy'] > 0:  # Going up
                    if other_car['y'] > car['y'] and other_car['y'] - car['y'] < 1.0:
                        return True
                else:  # Going down
                    if other_car['y'] < car['y'] and car['y'] - other_car['y'] < 1.0:
                        return True
        
        return False
    
    def update_cars(self):
        """Update car positions with human driving rules."""
        # Check if D1 should speed up after R3 passes
        d1_car = next((c for c in self.cars if c['label'] == 'D1'), None)
        r3_car = next((c for c in self.cars if c['label'] == 'R3'), None)
        
        if d1_car and r3_car and d1_car.get('waiting_for_r3', False):
            # R3 has passed D1 when R3's x position is past the intersection (x > -3.0 + 0.5)
            if r3_car['x'] > -2.5:  # R3 has cleared the intersection
                d1_car['vy'] = -d1_car['normal_speed']  # Speed up to normal
                d1_car['waiting_for_r3'] = False  # No longer waiting
        
        for car in self.cars:
            if not car['active']:
                continue
            
            # First check: Is this car already IN an intersection?
            # If yes, it MUST keep moving to clear the intersection (no stopping allowed)
            in_intersection, int_pos = self.is_in_intersection(car)
            
            if in_intersection:
                # Car is in intersection - must keep moving, don't stop for anything
                car['stopped'] = False
                car['stop_cooldown'] = 0  # Reset cooldown when moving
                car['waiting_for_perpendicular'] = False  # Reset waiting flag
            else:
                # Car is NOT in intersection - check if it should stop
                
                # Human driving rule 1: Stop if perpendicular car is in intersection AHEAD
                perpendicular_car_in_intersection = False
                horizontal_y_positions = [-2.2, 0, 2.2]
                vertical_x_positions = [-3.0, 0, 3.0]
                
                # Check if approaching an intersection (within detection range)
                for x_pos in vertical_x_positions:
                    for y_pos in horizontal_y_positions:
                        # Only check intersections that are AHEAD of the car
                        if not self.is_intersection_ahead(car, x_pos, y_pos):
                            continue
                        
                        dist = np.sqrt((car['x'] - x_pos)**2 + (car['y'] - y_pos)**2)
                        if 0.3 < dist < 0.8:  # Approaching but not yet inside (0.3 to 0.8 units away)
                            # Check if perpendicular car is in this intersection
                            if self.check_perpendicular_car_in_intersection(car, (x_pos, y_pos)):
                                perpendicular_car_in_intersection = True
                                car['waiting_for_perpendicular'] = True  # Mark that we're waiting
                                break
                    if perpendicular_car_in_intersection:
                        break
                
                # If we were waiting for perpendicular car but it's now gone, start cooldown
                if car.get('waiting_for_perpendicular', False) and not perpendicular_car_in_intersection:
                    # Perpendicular car has left - start 0.75 second delay (15 frames at 20 fps)
                    if car['stop_cooldown'] == 0:
                        car['stop_cooldown'] = 15  # 0.75 seconds
                    car['waiting_for_perpendicular'] = False  # No longer waiting for car
                
                # Human driving rule 2: Stop if car ahead in same lane is stopped
                should_stop_for_car_ahead = self.check_car_stopped_ahead_in_lane(car)
                
                # Determine if car should stop
                if perpendicular_car_in_intersection or should_stop_for_car_ahead:
                    car['stopped'] = True
                    continue  # Don't move this car
                else:
                    # Obstacle is clear, but check cooldown
                    if car['stop_cooldown'] > 0:
                        # Still in cooldown period - keep stopped
                        car['stopped'] = True
                        car['stop_cooldown'] -= 1
                        continue  # Don't move yet
                    else:
                        # Cooldown expired and no obstacles - can move
                        car['stopped'] = False
                        car['waiting_for_perpendicular'] = False  # Reset waiting flag
            
            # Check if car should start turning
            if car.get('should_turn', False) and not car['turning']:
                turn_direction = car.get('turn_direction')
                
                # Check if car has reached the turn intersection
                should_start_turn = False
                if turn_direction in ['right', 'left']:
                    # Horizontal car going RIGHT turning
                    should_start_turn = car['x'] >= car['turn_x'] - 0.1
                elif turn_direction == 'right_from_horizontal':
                    # Horizontal car going LEFT turning
                    should_start_turn = car['x'] <= car['turn_x'] + 0.1
                elif turn_direction == 'left_from_vertical':
                    # Vertical car turning
                    should_start_turn = car['y'] <= car['turn_y'] + 0.1
                
                if should_start_turn:
                    car['turning'] = True
                    car['turn_stage'] = 0
                    car['turn_center_x'] = car['turn_x']
                    car['turn_center_y'] = car['turn_y']
                    
                    # Set target position based on turn direction
                    if turn_direction == 'right':
                        # Right turn from horizontal: end up in left lane of vertical road going down
                        car['target_x'] = car['turn_x'] - self.lane_offset
                    elif turn_direction == 'left':
                        # Left turn from horizontal: end up in right lane of vertical road going up
                        car['target_x'] = car['turn_x'] + self.lane_offset
                    elif turn_direction == 'right_from_horizontal':
                        # Right turn from horizontal going LEFT: end up in right lane of vertical road going up
                        car['target_x'] = car['turn_x'] + self.lane_offset
                    elif turn_direction == 'left_from_vertical':
                        # Left turn from vertical: end up in top lane of horizontal road going left
                        car['target_y'] = car['turn_y'] + self.lane_offset
                    
                    # Slow down for turn
                    if turn_direction in ['right', 'left', 'right_from_horizontal']:
                        car['vx'] = car['turn_speed'] if car['vx'] > 0 else -car['turn_speed']
                    elif turn_direction == 'left_from_vertical':
                        car['vy'] = -car['turn_speed']
            
            # Handle turning animation
            if car.get('turning', False):
                turn_stage = car['turn_stage']
                turn_direction = car.get('turn_direction', 'right')
                
                if turn_stage < 3:
                    car['turn_stage'] += 1
                    
                    if turn_direction == 'right':
                        # RIGHT TURN: Rotate clockwise (positive angles)
                        car['angle'] = (turn_stage + 1) * np.pi / 6  # 30, 60, 90 degrees
                        
                        # Move slowly during turn, curving to the left lane
                        if turn_stage == 0:
                            # First stage: moving right, starting to curve left and down
                            car['x'] += car['turn_speed'] * 0.8
                            car['y'] -= car['turn_speed'] * 0.3
                        elif turn_stage == 1:
                            # Second stage: curving more, moving left to get to correct lane
                            car['x'] += car['turn_speed'] * 0.1
                            car['y'] -= car['turn_speed'] * 0.7
                        elif turn_stage == 2:
                            # Third stage: mostly down, finalizing position in left lane
                            car['x'] -= car['turn_speed'] * 0.3  # Move left to correct lane
                            car['y'] -= car['turn_speed']
                    
                    elif turn_direction == 'left':
                        # LEFT TURN from horizontal: Rotate counter-clockwise (negative angles)
                        car['angle'] = -(turn_stage + 1) * np.pi / 6  # -30, -60, -90 degrees
                        
                        # Move slowly during turn, curving to the right lane
                        if turn_stage == 0:
                            # First stage: moving right, starting to curve right and up
                            car['x'] += car['turn_speed'] * 0.8
                            car['y'] += car['turn_speed'] * 0.3
                        elif turn_stage == 1:
                            # Second stage: curving more, moving right to get to correct lane
                            car['x'] += car['turn_speed'] * 0.1
                            car['y'] += car['turn_speed'] * 0.7
                        elif turn_stage == 2:
                            # Third stage: mostly up, finalizing position in right lane
                            car['x'] += car['turn_speed'] * 0.3  # Move right to correct lane
                            car['y'] += car['turn_speed']
                    
                    elif turn_direction == 'right_from_horizontal':
                        # RIGHT TURN from horizontal going LEFT: Rotate from π to π/2
                        car['angle'] = np.pi - (turn_stage + 1) * np.pi / 6  # 5π/6, 2π/3, π/2
                        
                        # Move slowly during turn, curving to the right lane going up
                        if turn_stage == 0:
                            # First stage: moving left, starting to curve up and right
                            car['x'] -= car['turn_speed'] * 0.8
                            car['y'] += car['turn_speed'] * 0.3
                        elif turn_stage == 1:
                            # Second stage: curving more, moving right to get to correct lane
                            car['x'] -= car['turn_speed'] * 0.1
                            car['y'] += car['turn_speed'] * 0.7
                        elif turn_stage == 2:
                            # Third stage: mostly up, finalizing position in right lane
                            car['x'] += car['turn_speed'] * 0.3  # Move right to correct lane
                            car['y'] += car['turn_speed']
                    
                    elif turn_direction == 'left_from_vertical':
                        # LEFT TURN from vertical: Going down, turning to face left
                        # Start at -π/2, rotate counter-clockwise to -π (or π)
                        car['angle'] = -np.pi/2 - (turn_stage + 1) * np.pi / 6  # -2π/3, -5π/6, -π
                        
                        # Move slowly during turn, curving to the top lane (going left)
                        if turn_stage == 0:
                            # First stage: mostly down, starting to curve left
                            car['x'] -= car['turn_speed'] * 0.3
                            car['y'] -= car['turn_speed'] * 0.8
                        elif turn_stage == 1:
                            # Second stage: equal down and left
                            car['x'] -= car['turn_speed'] * 0.7
                            car['y'] -= car['turn_speed'] * 0.5
                        elif turn_stage == 2:
                            # Third stage: mostly left, finalizing position in top lane
                            car['x'] -= car['turn_speed']
                            car['y'] += car['turn_speed'] * 0.3  # Move up slightly to correct lane
                else:
                    # Turn complete - straighten out and speed up
                    car['turning'] = False
                    
                    # Set final angle and velocity based on turn direction
                    # Use uniform speed for consistency
                    fps = 20
                    horizontal_distance = self.x_max - self.x_min
                    uniform_speed = (horizontal_distance / (6 * fps)) * 0.95
                    
                    if turn_direction == 'right':
                        car['angle'] = -np.pi / 2  # Facing down
                        car['vx'] = 0
                        car['vy'] = -uniform_speed  # Going down, uniform speed
                        # Ensure car is in correct lane
                        car['x'] = car['target_x']
                        car['direction'] = 'vertical'
                    elif turn_direction == 'left':
                        car['angle'] = np.pi / 2  # Facing up
                        car['vx'] = 0
                        car['vy'] = uniform_speed  # Going up, uniform speed
                        # Ensure car is in correct lane
                        car['x'] = car['target_x']
                        car['direction'] = 'vertical'
                    elif turn_direction == 'right_from_horizontal':
                        car['angle'] = np.pi / 2  # Facing up
                        car['vx'] = 0
                        car['vy'] = uniform_speed  # Going up, uniform speed
                        # Ensure car is in correct lane
                        car['x'] = car['target_x']
                        car['direction'] = 'vertical'
                    elif turn_direction == 'left_from_vertical':
                        car['angle'] = np.pi  # Facing left
                        car['vy'] = 0
                        car['vx'] = -uniform_speed  # Going left, uniform speed
                        # Ensure car is in correct lane
                        car['y'] = car['target_y']
                        car['direction'] = 'horizontal'
                    
                    car['should_turn'] = False  # Don't turn again
            else:
                # Normal movement
                car['x'] += car['vx']
                car['y'] += car['vy']
            
            # Check if car has reached its destination
            self.check_destination_reached(car)
            
            # Deactivate cars that go off screen
            if (car['x'] < self.x_min - 0.5 or car['x'] > self.x_max + 0.5 or 
                car['y'] < self.y_min - 0.5 or car['y'] > self.y_max + 0.5):
                car['active'] = False
    
    def draw_car(self, ax, car):
        """Draw a single car."""
        if not car['active']:
            return
            
        # Car body corners (rectangle)
        corners = np.array([
            [-self.car_length/2, -self.car_width/2],
            [self.car_length/2, -self.car_width/2],
            [self.car_length/2, self.car_width/2],
            [-self.car_length/2, self.car_width/2]
        ])
        
        # Rotate based on direction
        angle = car['angle']
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        rotation = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        corners_rotated = corners @ rotation.T
        
        # Translate to car position
        corners_rotated[:, 0] += car['x']
        corners_rotated[:, 1] += car['y']
        
        # Draw car with different color if stopped
        edge_color = 'red' if car.get('stopped', False) else 'white'
        car_poly = Polygon(corners_rotated, facecolor=car['color'], 
                         edgecolor=edge_color, linewidth=2, zorder=15)
        ax.add_patch(car_poly)
        
        # Draw label
        ax.text(car['x'], car['y'], car['label'], 
               ha='center', va='center', fontsize=12, 
               color='white', fontweight='bold', zorder=17)
        
        # Draw STOP indicator if stopped
        if car.get('stopped', False):
            cooldown = car.get('stop_cooldown', 0)
            if cooldown > 0:
                # Show countdown during cooldown (looking around)
                # 15 frames = 0.75 seconds, show in quarter seconds (5 frames per quarter second)
                stop_text = f'WAIT {cooldown//5}'  # Show in quarter seconds
                color = 'orange'
            else:
                # Stopped for obstacle
                stop_text = 'STOP'
                color = 'red'
            
            ax.text(car['x'], car['y'] - 0.35, stop_text, 
                   ha='center', va='center', fontsize=8, 
                   color=color, fontweight='bold', zorder=18,
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9))
    
    def animate(self, frame):
        """Main animation function."""
        self.frame = frame
        
        # Increment total frame counter (doesn't reset on animation repeat)
        self.total_frames += 1
        
        # Update car positions
        self.update_cars()
        
        # Check if all cars reached destination
        if not self.all_cars_reached_destination and self.check_all_destinations():
            self.end_frame = self.total_frames
            self.all_cars_reached_destination = True
        
        # Draw everything
        self.ax.clear()
        self.draw_roads(self.ax)
        
        # Draw all cars
        for car in self.cars:
            self.draw_car(self.ax, car)
        
        # Draw title
        self.ax.text(0, 2.8, 'HUMAN DRIVING MODE', 
                    ha='center', va='center', fontsize=20, 
                    color='#FFAA44', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.8))
        
        # Draw timer (use total_frames to handle animation repeats correctly)
        fps = 20
        if self.all_cars_reached_destination:
            elapsed = self.end_frame / fps
            timer_text = f"✓ All cars reached destination in {elapsed:.2f} seconds"
            self.ax.text(1.5, -1.1, timer_text, fontsize=14, color='#00FF00', 
                        ha='center', weight='bold', bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        else:
            elapsed = self.total_frames / fps
            timer_text = f"Time: {elapsed:.2f} seconds"
            self.ax.text(1.5, -1.1, timer_text, fontsize=14, color='white', 
                        ha='center', weight='bold', bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        return []
    
    def run(self):
        """Run the animation."""
        anim = animation.FuncAnimation(self.fig, self.animate, frames=200, 
                                      interval=50, blit=False, repeat=True)
        plt.tight_layout()
        plt.show()
        return anim

if __name__ == '__main__':
    print("🚗 Traffic Demo - Human Driving")
    print("=" * 60)
    print("Human Driving Rules:")
    print("  1. Cars STOP when perpendicular cars are in intersection AHEAD")
    print("  2. Cars STOP when car ahead in same lane is stopped")
    print("  3. Cars IN intersection MUST keep moving (can't stop)")
    print("  4. After perpendicular car leaves intersection:")
    print("     - Wait for perpendicular car to fully clear")
    print("     - Then wait additional 0.75 seconds")
    print("     (simulates looking left/right to check for safety)")
    print("  5. ALL cars travel at the SAME SPEED (slowest speed)")
    print("     (realistic: humans don't know optimal speed)")
    print("")
    print("Visual Indicators:")
    print("  • Red edge = car is stopped for obstacle")
    print("  • White edge = car is moving")
    print("  • STOP (red) = stopped for obstacle")
    print("  • WAIT # (orange) = waiting after perpendicular car cleared")
    print("=" * 60)
    
    demo = TrafficDemo()
    demo.run()

