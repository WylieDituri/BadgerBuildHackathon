#!/usr/bin/env python3
"""
Traffic simulator - generates simulated traffic for testing the visualization.
Continuously creates cars, updates their positions, and simulates various scenarios.
"""

import requests
import time
import random
import math
from threading import Thread


API_BASE = "http://localhost:8000/api/v2/intelligence"


class TrafficSimulator:
    """Simulates realistic traffic for testing."""
    
    def __init__(self):
        self.active_cars = {}
        self.car_counter = 0
        self.running = False
    
    def start(self):
        """Start the simulator."""
        print("🚗 Starting Traffic Simulator...")
        print(f"📡 Connected to: {API_BASE}")
        print("🔄 Generating traffic...\n")
        
        self.running = True
        
        # Start threads for different simulation tasks
        Thread(target=self._spawn_cars, daemon=True).start()
        Thread(target=self._update_positions, daemon=True).start()
        Thread(target=self._create_scenarios, daemon=True).start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping simulator...")
            self.running = False
    
    def _spawn_cars(self):
        """Periodically spawn new cars."""
        while self.running:
            # Spawn 1-2 cars every 5 seconds
            for _ in range(random.randint(1, 2)):
                self._create_car()
            
            time.sleep(5)
    
    def _create_car(self):
        """Create a new car."""
        self.car_counter += 1
        car_id = f"car_{self.car_counter:03d}"
        
        # Random vehicle type
        vehicle_types = ["sedan", "suv", "truck"]
        is_emergency = random.random() < 0.1  # 10% chance of emergency
        
        if is_emergency:
            vehicle_type = "emergency"
        else:
            vehicle_type = random.choice(vehicle_types)
        
        # Register car
        try:
            response = requests.post(f"{API_BASE}/cars/register", json={
                "car_id": car_id,
                "vehicle_type": vehicle_type,
                "is_emergency": is_emergency
            }, timeout=2)
            
            if response.status_code == 200:
                # Map coordinate conversion: x = (lon + 89.39) * 100 - 3, y = (lat - 43.075) * 100 - 3
                # Map bounds: x from -4 to 4, y from -3.5 to 3.5
                # Roads at: x = -3, 0, 3 and y = -3, 0, 3
                
                # Define spawn zones at the FAR edges of the road network
                # These spawn positions ensure cars start outside the map and drive in
                spawn_zones = [
                    # NORTH EDGE - Top of map (y=3.5), along top road
                    {"lat": 43.140, "lon": -89.39 + random.uniform(-0.04, 0.04), "heading": 180, "name": "North →S"},
                    {"lat": 43.138, "lon": -89.365 + random.uniform(-0.01, 0.01), "heading": 180, "name": "North-E →S"},
                    {"lat": 43.138, "lon": -89.415 + random.uniform(-0.01, 0.01), "heading": 180, "name": "North-W →S"},
                    
                    # SOUTH EDGE - Bottom of map (y=-3.5), along bottom road
                    {"lat": 43.070, "lon": -89.39 + random.uniform(-0.04, 0.04), "heading": 0, "name": "South →N"},
                    {"lat": 43.072, "lon": -89.365 + random.uniform(-0.01, 0.01), "heading": 0, "name": "South-E →N"},
                    {"lat": 43.072, "lon": -89.415 + random.uniform(-0.01, 0.01), "heading": 0, "name": "South-W →N"},
                    
                    # EAST EDGE - Right side of map (x=4), along right road
                    {"lat": 43.105 + random.uniform(-0.02, 0.02), "lon": -89.32, "heading": 270, "name": "East →W"},
                    {"lat": 43.120 + random.uniform(-0.005, 0.005), "lon": -89.325, "heading": 270, "name": "East-N →W"},
                    {"lat": 43.090 + random.uniform(-0.005, 0.005), "lon": -89.325, "heading": 270, "name": "East-S →W"},
                    
                    # WEST EDGE - Left side of map (x=-4), along left road
                    {"lat": 43.105 + random.uniform(-0.02, 0.02), "lon": -89.46, "heading": 90, "name": "West →E"},
                    {"lat": 43.120 + random.uniform(-0.005, 0.005), "lon": -89.455, "heading": 90, "name": "West-N →E"},
                    {"lat": 43.090 + random.uniform(-0.005, 0.005), "lon": -89.455, "heading": 90, "name": "West-S →E"},
                ]
                
                # Pick random spawn zone
                spawn = random.choice(spawn_zones)
                lat = spawn["lat"]
                lon = spawn["lon"]
                heading = spawn["heading"]
                speed = random.uniform(8, 15) if not is_emergency else random.uniform(15, 20)
                
                self.active_cars[car_id] = {
                    'lat': lat,
                    'lon': lon,
                    'heading': heading,
                    'speed': speed,
                    'is_emergency': is_emergency,
                    'lifetime': 0
                }
                
                # Send initial position
                self._update_car_position(car_id)
                
                emoji = "🚨" if is_emergency else "🚗"
                zone_name = spawn.get("name", "Unknown")
                print(f"{emoji} Spawned: {car_id} ({vehicle_type}) at {zone_name}")
        except Exception as e:
            print(f"Error creating car {car_id}: {e}")
    
    def _update_positions(self):
        """Update positions of all active cars."""
        while self.running:
            cars_to_remove = []
            
            for car_id, car_data in list(self.active_cars.items()):
                # Move car
                car_data['lifetime'] += 1
                
                # Simple movement: move in current heading direction
                heading_rad = math.radians(car_data['heading'])
                
                # Speed in degrees/second (approximate)
                speed_deg = car_data['speed'] / 111000  # Convert m/s to deg/s
                
                car_data['lat'] += speed_deg * math.cos(heading_rad)
                car_data['lon'] += speed_deg * math.sin(heading_rad)
                
                # Randomly change direction at intersections
                if random.random() < 0.1:  # 10% chance per second
                    car_data['heading'] = random.choice([0, 90, 180, 270])
                
                # Update position via API
                self._update_car_position(car_id)
                
                # Remove cars after 60 seconds or if out of bounds
                if car_data['lifetime'] > 60 or self._is_out_of_bounds(car_data):
                    cars_to_remove.append(car_id)
            
            # Remove expired cars
            for car_id in cars_to_remove:
                del self.active_cars[car_id]
                print(f"♻️  Removed: {car_id}")
            
            time.sleep(1)
    
    def _update_car_position(self, car_id):
        """Send position update to API."""
        car_data = self.active_cars.get(car_id)
        if not car_data:
            return
        
        try:
            requests.post(f"{API_BASE}/cars/location", json={
                "car_id": car_id,
                "lat": car_data['lat'],
                "lon": car_data['lon'],
                "heading": car_data['heading'],
                "speed_mps": car_data['speed']
            }, timeout=2)
        except Exception as e:
            pass  # Silently fail to avoid spam
    
    def _is_out_of_bounds(self, car_data):
        """Check if car is too far from center."""
        dlat = abs(car_data['lat'] - 43.075)
        dlon = abs(car_data['lon'] + 89.390)
        return dlat > 0.005 or dlon > 0.005
    
    def _create_scenarios(self):
        """Create interesting scenarios (collisions, congestion, etc.)."""
        while self.running:
            time.sleep(15)  # Every 15 seconds
            
            scenario = random.choice([
                'collision_course',
                'intersection_rush',
                'emergency_vehicle',
                'nothing'
            ])
            
            if scenario == 'collision_course' and len(self.active_cars) >= 2:
                self._create_collision_scenario()
            elif scenario == 'intersection_rush':
                self._create_intersection_rush()
            elif scenario == 'emergency_vehicle':
                self._create_emergency_scenario()
    
    def _create_collision_scenario(self):
        """Create two cars on collision course."""
        print("\n⚠️  Creating collision scenario...")
        
        # Create two cars heading towards each other
        lat_base = 43.075
        lon_base = -89.390
        
        car1_id = f"car_{self.car_counter + 1:03d}"
        car2_id = f"car_{self.car_counter + 2:03d}"
        self.car_counter += 2
        
        for car_id, heading, offset in [(car1_id, 90, -0.001), (car2_id, 270, 0.001)]:
            try:
                requests.post(f"{API_BASE}/cars/register", json={
                    "car_id": car_id,
                    "vehicle_type": "sedan"
                }, timeout=2)
                
                self.active_cars[car_id] = {
                    'lat': lat_base,
                    'lon': lon_base + offset,
                    'heading': heading,
                    'speed': 15.0,
                    'is_emergency': False,
                    'lifetime': 0
                }
                
                self._update_car_position(car_id)
            except:
                pass
    
    def _create_intersection_rush(self):
        """Create multiple cars approaching same intersection."""
        print("\n🚦 Creating intersection rush...")
        
        lat_center = 43.075
        lon_center = -89.390
        
        # 4 cars from different directions
        directions = [
            (0, -0.001, 0),      # From South, heading North
            (90, 0, -0.001),     # From West, heading East
            (180, 0.001, 0),     # From North, heading South
            (270, 0, 0.001),     # From East, heading West
        ]
        
        for heading, dlat, dlon in directions:
            car_id = f"car_{self.car_counter + 1:03d}"
            self.car_counter += 1
            
            try:
                requests.post(f"{API_BASE}/cars/register", json={
                    "car_id": car_id,
                    "vehicle_type": random.choice(["sedan", "suv"])
                }, timeout=2)
                
                self.active_cars[car_id] = {
                    'lat': lat_center + dlat,
                    'lon': lon_center + dlon,
                    'heading': heading,
                    'speed': 12.0,
                    'is_emergency': False,
                    'lifetime': 0
                }
                
                self._update_car_position(car_id)
            except:
                pass
    
    def _create_emergency_scenario(self):
        """Create an emergency vehicle scenario."""
        print("\n🚨 Creating emergency vehicle scenario...")
        
        car_id = f"ambulance_{self.car_counter + 1:03d}"
        self.car_counter += 1
        
        try:
            requests.post(f"{API_BASE}/cars/register", json={
                "car_id": car_id,
                "vehicle_type": "emergency",
                "is_emergency": True
            }, timeout=2)
            
            self.active_cars[car_id] = {
                'lat': 43.073,
                'lon': -89.392,
                'heading': random.choice([0, 90, 180, 270]),
                'speed': 20.0,
                'is_emergency': True,
                'lifetime': 0
            }
            
            self._update_car_position(car_id)
        except:
            pass


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  🚗 TRAFFIC SIMULATOR")
    print("="*60)
    print("\nThis simulator generates realistic traffic for testing.")
    print("\nFeatures:")
    print("  • Spawns cars every 5 seconds")
    print("  • Updates positions in real-time")
    print("  • Creates collision scenarios")
    print("  • Simulates intersection rushes")
    print("  • Emergency vehicle responses")
    print("\n⚠️  Make sure the backend is running first:")
    print("   cd backend && uvicorn app.main:app --reload")
    print("\n📊 Then run the visualizer in another terminal:")
    print("   python visualizer/live_dashboard.py")
    print("\n" + "="*60 + "\n")
    
    input("Press ENTER to start the simulator...")
    
    simulator = TrafficSimulator()
    simulator.start()

