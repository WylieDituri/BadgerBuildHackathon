"""
Collision predictor - predicts and prevents potential collisions
using trajectory analysis and closest point of approach (CPA).
"""

import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from app.models.car import Car
from app.intelligence.car_tracker import CarTracker


@dataclass
class CollisionPrediction:
    """Represents a predicted collision."""
    car1_id: str
    car2_id: str
    time_to_collision_seconds: float
    collision_point: Tuple[float, float]  # (lat, lon)
    closest_distance_meters: float
    confidence: float  # 0.0 to 1.0
    severity: str  # 'low', 'medium', 'high', 'critical'
    recommended_action: str
    
    def to_dict(self):
        return {
            'car1_id': self.car1_id,
            'car2_id': self.car2_id,
            'time_to_collision_seconds': round(self.time_to_collision_seconds, 2),
            'collision_point': {
                'lat': self.collision_point[0],
                'lon': self.collision_point[1]
            },
            'closest_distance_meters': round(self.closest_distance_meters, 2),
            'confidence': round(self.confidence, 2),
            'severity': self.severity,
            'recommended_action': self.recommended_action
        }


class CollisionPredictor:
    """Predicts potential collisions between cars."""
    
    # Safety thresholds
    COLLISION_DISTANCE_THRESHOLD = 10  # meters
    WARNING_DISTANCE_THRESHOLD = 25    # meters
    TIME_HORIZON = 15.0                # seconds
    MIN_CONFIDENCE = 0.3               # minimum to report
    
    def __init__(self, car_tracker: CarTracker):
        self.tracker = car_tracker
        self.recent_predictions: Dict[str, CollisionPrediction] = {}
    
    def predict_all_collisions(self) -> List[CollisionPrediction]:
        """
        Analyze all active cars and predict potential collisions.
        
        Returns: List of collision predictions sorted by urgency
        """
        predictions = []
        active_cars = self.tracker.get_active_cars()
        
        # Check each pair of cars
        for i, car1 in enumerate(active_cars):
            for car2 in active_cars[i+1:]:
                prediction = self._analyze_car_pair(car1, car2)
                if prediction and prediction.confidence >= self.MIN_CONFIDENCE:
                    predictions.append(prediction)
        
        # Sort by urgency (time to collision)
        predictions.sort(key=lambda p: p.time_to_collision_seconds)
        
        # Cache predictions
        for pred in predictions:
            key = self._get_pair_key(pred.car1_id, pred.car2_id)
            self.recent_predictions[key] = pred
        
        return predictions
    
    def check_car(self, car_id: str) -> List[CollisionPrediction]:
        """
        Check a specific car for potential collisions with nearby cars.
        """
        car = self.tracker.get_car(car_id)
        if not car or not car.current_position:
            return []
        
        predictions = []
        
        # Get nearby cars (within 500m)
        nearby = self.tracker.get_cars_in_area(
            car.current_position.lat,
            car.current_position.lon,
            0.5  # 500m radius
        )
        
        for other_car in nearby:
            if other_car.car_id != car_id:
                prediction = self._analyze_car_pair(car, other_car)
                if prediction and prediction.confidence >= self.MIN_CONFIDENCE:
                    predictions.append(prediction)
        
        return predictions
    
    def _analyze_car_pair(
        self,
        car1: Car,
        car2: Car
    ) -> Optional[CollisionPrediction]:
        """
        Analyze trajectory intersection between two cars.
        
        Uses Closest Point of Approach (CPA) algorithm.
        """
        # Check if both have valid positions
        if not car1.current_position or not car2.current_position:
            return None
        
        pos1 = car1.current_position
        pos2 = car2.current_position
        
        # Convert to meters for easier calculation
        x1, y1 = self._latlon_to_meters(pos1.lat, pos1.lon)
        x2, y2 = self._latlon_to_meters(pos2.lat, pos2.lon)
        
        # Get velocity vectors (m/s)
        vel1 = car1.get_velocity_vector()
        vel2 = car2.get_velocity_vector()
        
        if not vel1 or not vel2:
            return None
        
        vx1, vy1 = vel1
        vx2, vy2 = vel2
        
        # Relative position and velocity
        dx = x2 - x1
        dy = y2 - y1
        dvx = vx2 - vx1
        dvy = vy2 - vy1
        
        # Current distance
        current_distance = math.sqrt(dx**2 + dy**2)
        
        # If cars are stationary or moving apart, no collision
        if abs(dvx) < 0.1 and abs(dvy) < 0.1:
            return None
        
        # Calculate time to CPA (Closest Point of Approach)
        # t_cpa = -(dx*dvx + dy*dvy) / (dvx^2 + dvy^2)
        numerator = -(dx * dvx + dy * dvy)
        denominator = dvx**2 + dvy**2
        
        if denominator < 0.01:  # Nearly parallel, moving together
            return None
        
        t_cpa = numerator / denominator
        
        # If CPA is in the past or too far future, ignore
        if t_cpa < 0 or t_cpa > self.TIME_HORIZON:
            return None
        
        # Calculate distance at CPA
        x1_cpa = x1 + vx1 * t_cpa
        y1_cpa = y1 + vy1 * t_cpa
        x2_cpa = x2 + vx2 * t_cpa
        y2_cpa = y2 + vy2 * t_cpa
        
        distance_at_cpa = math.sqrt(
            (x2_cpa - x1_cpa)**2 + (y2_cpa - y1_cpa)**2
        )
        
        # If distance at CPA is safe, no collision
        if distance_at_cpa > self.WARNING_DISTANCE_THRESHOLD:
            return None
        
        # Calculate collision point (midpoint at CPA)
        collision_x = (x1_cpa + x2_cpa) / 2
        collision_y = (y1_cpa + y2_cpa) / 2
        collision_lat, collision_lon = self._meters_to_latlon(collision_x, collision_y)
        
        # Calculate confidence based on:
        # - Distance at CPA (closer = higher confidence)
        # - Trajectory certainty (consistent speed/heading)
        # - Time to CPA (sooner = higher confidence)
        
        distance_factor = 1.0 - (distance_at_cpa / self.WARNING_DISTANCE_THRESHOLD)
        time_factor = 1.0 - (t_cpa / self.TIME_HORIZON)
        
        # Check trajectory consistency (using last few positions)
        consistency1 = self._calculate_trajectory_consistency(car1)
        consistency2 = self._calculate_trajectory_consistency(car2)
        consistency_factor = (consistency1 + consistency2) / 2
        
        confidence = (distance_factor * 0.5 + time_factor * 0.3 + consistency_factor * 0.2)
        confidence = max(0.0, min(1.0, confidence))
        
        # Determine severity
        if distance_at_cpa < self.COLLISION_DISTANCE_THRESHOLD:
            if t_cpa < 3:
                severity = 'critical'
            elif t_cpa < 7:
                severity = 'high'
            else:
                severity = 'medium'
        else:
            severity = 'low'
        
        # Recommend action
        recommended_action = self._recommend_action(
            t_cpa,
            distance_at_cpa,
            severity,
            car1,
            car2
        )
        
        return CollisionPrediction(
            car1_id=car1.car_id,
            car2_id=car2.car_id,
            time_to_collision_seconds=t_cpa,
            collision_point=(collision_lat, collision_lon),
            closest_distance_meters=distance_at_cpa,
            confidence=confidence,
            severity=severity,
            recommended_action=recommended_action
        )
    
    def _recommend_action(
        self,
        time_to_collision: float,
        distance_at_cpa: float,
        severity: str,
        car1: Car,
        car2: Car
    ) -> str:
        """Recommend action to prevent collision."""
        # Emergency vehicles always have priority
        if car1.is_emergency:
            return f"CAR_{car2.car_id}_STOP"
        elif car2.is_emergency:
            return f"CAR_{car1.car_id}_STOP"
        
        # Critical situations
        if severity == 'critical':
            return "BOTH_EMERGENCY_BRAKE"
        
        # High priority
        if severity == 'high':
            if time_to_collision < 5:
                return "BOTH_BRAKE"
            else:
                # Car with higher ID yields (arbitrary but consistent)
                if car1.car_id > car2.car_id:
                    return f"CAR_{car1.car_id}_SLOW"
                else:
                    return f"CAR_{car2.car_id}_SLOW"
        
        # Medium priority
        if severity == 'medium':
            # Suggest rerouting to the car that's further from destination
            return "CONSIDER_REROUTE"
        
        # Low priority
        return "MONITOR"
    
    def _calculate_trajectory_consistency(self, car: Car) -> float:
        """
        Calculate how consistent the car's trajectory has been.
        Returns 0.0 (erratic) to 1.0 (very consistent).
        """
        if len(car.trajectory) < 3:
            return 0.5  # Default for insufficient data
        
        # Check speed consistency
        speeds = [p.speed_mps for p in car.trajectory[-10:]]
        if len(speeds) < 2:
            return 0.5
        
        avg_speed = sum(speeds) / len(speeds)
        if avg_speed < 0.1:
            return 0.5  # Car is stopped
        
        speed_variance = sum((s - avg_speed)**2 for s in speeds) / len(speeds)
        speed_consistency = 1.0 / (1.0 + speed_variance)
        
        # Check heading consistency
        headings = [p.heading for p in car.trajectory[-10:]]
        if len(headings) < 2:
            return 0.5
        
        # Calculate heading variance (accounting for 360° wrap)
        heading_diffs = []
        for i in range(len(headings) - 1):
            diff = abs(headings[i+1] - headings[i])
            if diff > 180:
                diff = 360 - diff
            heading_diffs.append(diff)
        
        avg_heading_change = sum(heading_diffs) / len(heading_diffs) if heading_diffs else 0
        heading_consistency = 1.0 / (1.0 + avg_heading_change / 10.0)
        
        # Combined consistency
        return (speed_consistency + heading_consistency) / 2
    
    @staticmethod
    def _latlon_to_meters(lat: float, lon: float) -> Tuple[float, float]:
        """
        Convert lat/lon to approximate meters (for local calculations).
        Uses simple equirectangular projection (good for small areas).
        """
        # At equator: 1° lat ≈ 111km, 1° lon ≈ 111km * cos(lat)
        x = lon * 111000 * math.cos(math.radians(lat))
        y = lat * 111000
        return (x, y)
    
    @staticmethod
    def _meters_to_latlon(x: float, y: float, ref_lat: float = 43.0) -> Tuple[float, float]:
        """Convert meters back to lat/lon (approximate)."""
        lat = y / 111000
        lon = x / (111000 * math.cos(math.radians(ref_lat)))
        return (lat, lon)
    
    @staticmethod
    def _get_pair_key(car_id1: str, car_id2: str) -> str:
        """Get consistent key for car pair."""
        return "_".join(sorted([car_id1, car_id2]))


# Example usage
if __name__ == "__main__":
    # Test collision prediction
    from app.models.car import Car, Position, VehicleType
    
    tracker = CarTracker()
    predictor = CollisionPredictor(tracker)
    
    # Create two cars on collision course
    car1 = Car(
        car_id="car_001",
        vehicle_type=VehicleType.SEDAN,
        current_position=Position(
            lat=43.0750,
            lon=-89.3900,
            heading=90,  # Going East
            speed_mps=15  # ~33 mph
        )
    )
    
    car2 = Car(
        car_id="car_002",
        vehicle_type=VehicleType.SUV,
        current_position=Position(
            lat=43.0750,
            lon=-89.3890,  # 100m East
            heading=270,  # Going West (head-on!)
            speed_mps=15
        )
    )
    
    tracker.register_car(car1)
    tracker.register_car(car2)
    
    predictions = predictor.predict_all_collisions()
    
    for pred in predictions:
        print(f"\n⚠️  COLLISION PREDICTED!")
        print(f"  Cars: {pred.car1_id} vs {pred.car2_id}")
        print(f"  Time: {pred.time_to_collision_seconds:.1f}s")
        print(f"  Distance: {pred.closest_distance_meters:.1f}m")
        print(f"  Severity: {pred.severity}")
        print(f"  Confidence: {pred.confidence:.0%}")
        print(f"  Action: {pred.recommended_action}")

