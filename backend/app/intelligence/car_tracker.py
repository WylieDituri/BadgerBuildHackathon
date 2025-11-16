"""
Car tracker - manages all active cars and their positions.
Provides trajectory prediction for collision detection.
"""

import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from app.models.car import Car, Position


class CarTracker:
    """Tracks all active cars in the system."""
    
    def __init__(self):
        self.cars: Dict[str, Car] = {}
        self.position_history: Dict[str, List[Position]] = {}
    
    def register_car(self, car: Car):
        """Register a new car in the system."""
        self.cars[car.car_id] = car
        if car.car_id not in self.position_history:
            self.position_history[car.car_id] = []
        print(f"✓ Registered car: {car.car_id} ({car.vehicle_type.value})")
    
    def update_position(
        self,
        car_id: str,
        lat: float,
        lon: float,
        heading: float,
        speed_mps: float
    ) -> Position:
        """Update a car's position."""
        position = Position(
            lat=lat,
            lon=lon,
            heading=heading,
            speed_mps=speed_mps,
            timestamp=datetime.now()
        )
        
        if car_id in self.cars:
            self.cars[car_id].update_position(position)
            self.position_history[car_id].append(position)
            
            # Keep last 60 seconds of history
            cutoff_time = datetime.now() - timedelta(seconds=60)
            self.position_history[car_id] = [
                p for p in self.position_history[car_id]
                if p.timestamp > cutoff_time
            ]
        
        return position
    
    def get_car(self, car_id: str) -> Optional[Car]:
        """Get a car by ID."""
        return self.cars.get(car_id)
    
    def get_all_cars(self) -> List[Car]:
        """Get all registered cars."""
        return list(self.cars.values())
    
    def get_active_cars(self) -> List[Car]:
        """Get cars that have recent position updates."""
        active = []
        cutoff_time = datetime.now() - timedelta(seconds=30)
        
        for car in self.cars.values():
            if car.current_position and car.current_position.timestamp > cutoff_time:
                active.append(car)
        
        return active
    
    def remove_car(self, car_id: str):
        """Remove a car from tracking."""
        if car_id in self.cars:
            del self.cars[car_id]
        if car_id in self.position_history:
            del self.position_history[car_id]
    
    def get_cars_in_area(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float
    ) -> List[Car]:
        """Find all cars within a radius of a point."""
        cars_in_area = []
        
        for car in self.get_active_cars():
            if car.current_position:
                distance = self._haversine_distance(
                    center_lat, center_lon,
                    car.current_position.lat, car.current_position.lon
                )
                if distance <= radius_km:
                    cars_in_area.append(car)
        
        return cars_in_area
    
    def predict_position(
        self,
        car_id: str,
        seconds_ahead: float
    ) -> Optional[Tuple[float, float]]:
        """
        Predict where a car will be in N seconds.
        
        Uses simple linear extrapolation based on current position,
        heading, and speed.
        
        Returns: (predicted_lat, predicted_lon) or None
        """
        car = self.get_car(car_id)
        if not car or not car.current_position:
            return None
        
        pos = car.current_position
        
        # Convert heading to radians (0° = North)
        heading_rad = math.radians(pos.heading)
        
        # Calculate displacement in meters
        distance_m = pos.speed_mps * seconds_ahead
        
        # Earth radius in meters
        R = 6371000
        
        # Calculate new position using haversine formula
        lat1 = math.radians(pos.lat)
        lon1 = math.radians(pos.lon)
        
        # Angular distance
        angular_distance = distance_m / R
        
        # New latitude
        lat2 = math.asin(
            math.sin(lat1) * math.cos(angular_distance) +
            math.cos(lat1) * math.sin(angular_distance) * math.cos(heading_rad)
        )
        
        # New longitude
        lon2 = lon1 + math.atan2(
            math.sin(heading_rad) * math.sin(angular_distance) * math.cos(lat1),
            math.cos(angular_distance) - math.sin(lat1) * math.sin(lat2)
        )
        
        predicted_lat = math.degrees(lat2)
        predicted_lon = math.degrees(lon2)
        
        return (predicted_lat, predicted_lon)
    
    def predict_trajectory(
        self,
        car_id: str,
        time_horizon_seconds: float,
        time_step: float = 1.0
    ) -> List[Tuple[float, float, float]]:
        """
        Predict full trajectory over time horizon.
        
        Returns: List of (lat, lon, time) tuples
        """
        trajectory = []
        car = self.get_car(car_id)
        
        if not car or not car.current_position:
            return trajectory
        
        # Start with current position
        current_time = 0
        trajectory.append((
            car.current_position.lat,
            car.current_position.lon,
            current_time
        ))
        
        # Predict at each time step
        while current_time < time_horizon_seconds:
            current_time += time_step
            predicted = self.predict_position(car_id, current_time)
            if predicted:
                trajectory.append((predicted[0], predicted[1], current_time))
        
        return trajectory
    
    def get_distance_between_cars(
        self,
        car_id1: str,
        car_id2: str
    ) -> Optional[float]:
        """
        Calculate distance between two cars in km.
        Returns None if either car doesn't have a position.
        """
        car1 = self.get_car(car_id1)
        car2 = self.get_car(car_id2)
        
        if not car1 or not car2:
            return None
        if not car1.current_position or not car2.current_position:
            return None
        
        return self._haversine_distance(
            car1.current_position.lat,
            car1.current_position.lon,
            car2.current_position.lat,
            car2.current_position.lon
        )
    
    @staticmethod
    def _haversine_distance(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two lat/lon points in km.
        Uses the Haversine formula.
        """
        R = 6371  # Earth radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(dlat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def get_average_speed(self, car_id: str, window_seconds: int = 10) -> Optional[float]:
        """Get average speed over last N seconds."""
        if car_id not in self.position_history:
            return None
        
        cutoff_time = datetime.now() - timedelta(seconds=window_seconds)
        recent_positions = [
            p for p in self.position_history[car_id]
            if p.timestamp > cutoff_time
        ]
        
        if not recent_positions:
            return None
        
        speeds = [p.speed_mps for p in recent_positions]
        return sum(speeds) / len(speeds)
    
    def is_car_moving(self, car_id: str, threshold_mps: float = 0.5) -> bool:
        """Check if car is moving (speed > threshold)."""
        car = self.get_car(car_id)
        if not car or not car.current_position:
            return False
        return car.current_position.speed_mps > threshold_mps


# Global instance
car_tracker = CarTracker()

