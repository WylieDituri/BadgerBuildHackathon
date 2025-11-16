"""
Data models for cars, positions, and routes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Tuple
from enum import Enum


class VehicleType(str, Enum):
    """Types of vehicles in the system."""
    SEDAN = "sedan"
    SUV = "suv"
    TRUCK = "truck"
    EMERGENCY = "emergency"
    AUTONOMOUS = "autonomous"


class RouteStatus(str, Enum):
    """Status of a route."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REROUTING = "rerouting"


@dataclass
class Position:
    """Represents a geographic position with velocity."""
    lat: float
    lon: float
    heading: float  # degrees, 0=North, 90=East, 180=South, 270=West
    speed_mps: float  # meters per second
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            'lat': self.lat,
            'lon': self.lon,
            'heading': self.heading,
            'speed_mps': self.speed_mps,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class Waypoint:
    """A point along a route."""
    lat: float
    lon: float
    instruction: Optional[str] = None  # e.g., "Turn left on Main St"
    
    def to_tuple(self) -> Tuple[float, float]:
        return (self.lat, self.lon)
    
    def to_dict(self):
        return {
            'lat': self.lat,
            'lon': self.lon,
            'instruction': self.instruction
        }


@dataclass
class Route:
    """Represents a planned route from A to B."""
    route_id: str
    car_id: str
    start: Waypoint
    end: Waypoint
    waypoints: List[Waypoint]
    distance_km: float
    estimated_time_minutes: float
    status: RouteStatus = RouteStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    traffic_incidents: List[dict] = field(default_factory=list)
    
    def to_dict(self):
        return {
            'route_id': self.route_id,
            'car_id': self.car_id,
            'start': self.start.to_dict(),
            'end': self.end.to_dict(),
            'waypoints': [wp.to_dict() for wp in self.waypoints],
            'distance_km': self.distance_km,
            'estimated_time_minutes': self.estimated_time_minutes,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'traffic_incidents': self.traffic_incidents
        }


@dataclass
class Car:
    """Represents a vehicle in the system."""
    car_id: str
    vehicle_type: VehicleType
    owner_id: Optional[str] = None
    current_position: Optional[Position] = None
    current_route: Optional[Route] = None
    destination: Optional[Tuple[float, float]] = None
    trajectory: List[Position] = field(default_factory=list)  # Recent positions
    is_emergency: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    def update_position(self, position: Position):
        """Update car's current position and maintain trajectory history."""
        self.current_position = position
        self.trajectory.append(position)
        
        # Keep only last 30 seconds of trajectory (assuming 1 update/sec)
        if len(self.trajectory) > 30:
            self.trajectory = self.trajectory[-30:]
    
    def get_velocity_vector(self) -> Optional[Tuple[float, float]]:
        """
        Get current velocity as a vector (vx, vy) in m/s.
        Returns None if position/heading unknown.
        """
        if not self.current_position:
            return None
        
        import math
        heading_rad = math.radians(self.current_position.heading)
        vx = self.current_position.speed_mps * math.sin(heading_rad)
        vy = self.current_position.speed_mps * math.cos(heading_rad)
        return (vx, vy)
    
    def to_dict(self):
        return {
            'car_id': self.car_id,
            'vehicle_type': self.vehicle_type.value,
            'owner_id': self.owner_id,
            'current_position': self.current_position.to_dict() if self.current_position else None,
            'current_route': self.current_route.to_dict() if self.current_route else None,
            'destination': self.destination,
            'is_emergency': self.is_emergency,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class TrafficIncident:
    """Represents a traffic incident (accident, construction, etc.)"""
    incident_id: str
    type: str  # 'accident', 'construction', 'weather', 'event'
    lat: float
    lon: float
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    lanes_blocked: int = 0
    estimated_clearance_minutes: Optional[int] = None
    reported_at: datetime = field(default_factory=datetime.now)
    cleared_at: Optional[datetime] = None
    
    def is_active(self) -> bool:
        """Check if incident is still active."""
        return self.cleared_at is None
    
    def to_dict(self):
        return {
            'incident_id': self.incident_id,
            'type': self.type,
            'lat': self.lat,
            'lon': self.lon,
            'severity': self.severity,
            'description': self.description,
            'lanes_blocked': self.lanes_blocked,
            'estimated_clearance_minutes': self.estimated_clearance_minutes,
            'reported_at': self.reported_at.isoformat(),
            'cleared_at': self.cleared_at.isoformat() if self.cleared_at else None,
            'is_active': self.is_active()
        }

