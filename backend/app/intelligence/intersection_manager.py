"""
Intersection manager - coordinates cars at intersections to prevent collisions.
Uses reservation-based system with priority queues.
"""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from app.models.car import Car
from app.intelligence.car_tracker import CarTracker


@dataclass
class IntersectionReservation:
    """Represents a reservation to cross an intersection."""
    car_id: str
    intersection_id: str
    start_time: float  # Unix timestamp
    end_time: float    # Unix timestamp
    priority: int      # Higher = more important
    created_at: datetime = field(default_factory=datetime.now)
    
    def is_active(self, current_time: float) -> bool:
        """Check if reservation is currently active."""
        return self.start_time <= current_time <= self.end_time
    
    def conflicts_with(self, other: 'IntersectionReservation') -> bool:
        """Check if this reservation conflicts with another."""
        return not (self.end_time < other.start_time or self.start_time > other.end_time)


@dataclass
class CrossingDecision:
    """Response to a crossing request."""
    approved: bool
    wait_time_seconds: float
    crossing_window: Optional[Tuple[float, float]]  # (start, end) timestamps
    speed_recommendation: str  # 'maintain', 'slow', 'stop'
    reason: str
    priority: int
    
    def to_dict(self):
        return {
            'approved': self.approved,
            'wait_time_seconds': round(self.wait_time_seconds, 2),
            'crossing_window': {
                'start': self.crossing_window[0],
                'end': self.crossing_window[1]
            } if self.crossing_window else None,
            'speed_recommendation': self.speed_recommendation,
            'reason': self.reason,
            'priority': self.priority
        }


class IntersectionManager:
    """Manages car coordination at intersections."""
    
    # Time each car needs to cross an intersection (seconds)
    DEFAULT_CROSSING_TIME = 3.0
    EMERGENCY_CROSSING_TIME = 2.0
    
    # Safety buffer between cars (seconds)
    SAFETY_BUFFER = 1.0
    
    def __init__(self, car_tracker: CarTracker):
        self.tracker = car_tracker
        
        # intersection_id -> list of reservations
        self.reservations: Dict[str, List[IntersectionReservation]] = defaultdict(list)
        
        # Track cars waiting at each intersection
        self.waiting_cars: Dict[str, List[str]] = defaultdict(list)
        
        # Performance metrics
        self.total_requests = 0
        self.approved_requests = 0
        self.average_wait_time = 0.0
    
    def request_crossing(
        self,
        car_id: str,
        intersection_id: str,
        eta_seconds: float
    ) -> CrossingDecision:
        """
        Car requests permission to cross an intersection.
        
        Args:
            car_id: ID of requesting car
            intersection_id: ID of intersection
            eta_seconds: Estimated time to arrival (seconds from now)
        
        Returns:
            CrossingDecision with approval status and timing
        """
        self.total_requests += 1
        
        car = self.tracker.get_car(car_id)
        if not car:
            return CrossingDecision(
                approved=False,
                wait_time_seconds=0,
                crossing_window=None,
                speed_recommendation='stop',
                reason='Car not found in system',
                priority=0
            )
        
        # Calculate priority
        priority = self._calculate_priority(car, eta_seconds)
        
        # Get current time
        current_time = time.time()
        requested_start_time = current_time + eta_seconds
        
        # Determine crossing duration
        crossing_duration = (
            self.EMERGENCY_CROSSING_TIME if car.is_emergency
            else self.DEFAULT_CROSSING_TIME
        )
        requested_end_time = requested_start_time + crossing_duration
        
        # Clean up old reservations
        self._cleanup_old_reservations(intersection_id, current_time)
        
        # Check if requested time slot is available
        if self._is_slot_available(
            intersection_id,
            requested_start_time,
            requested_end_time,
            priority
        ):
            # Approve immediately
            reservation = IntersectionReservation(
                car_id=car_id,
                intersection_id=intersection_id,
                start_time=requested_start_time,
                end_time=requested_end_time,
                priority=priority
            )
            self.reservations[intersection_id].append(reservation)
            self.approved_requests += 1
            
            return CrossingDecision(
                approved=True,
                wait_time_seconds=0,
                crossing_window=(requested_start_time, requested_end_time),
                speed_recommendation='maintain',
                reason='Slot available',
                priority=priority
            )
        
        # Find next available slot
        next_slot = self._find_next_available_slot(
            intersection_id,
            requested_start_time,
            crossing_duration,
            priority
        )
        
        if next_slot:
            start_time, end_time = next_slot
            delay = start_time - requested_start_time
            
            # Create reservation
            reservation = IntersectionReservation(
                car_id=car_id,
                intersection_id=intersection_id,
                start_time=start_time,
                end_time=end_time,
                priority=priority
            )
            self.reservations[intersection_id].append(reservation)
            self.approved_requests += 1
            
            # Track waiting
            if car_id not in self.waiting_cars[intersection_id]:
                self.waiting_cars[intersection_id].append(car_id)
            
            # Update metrics
            self.average_wait_time = (
                (self.average_wait_time * (self.approved_requests - 1) + delay) /
                self.approved_requests
            )
            
            # Recommend speed adjustment
            if delay < 2:
                speed_rec = 'maintain'
                reason = 'Short delay, maintain speed'
            elif delay < 5:
                speed_rec = 'slow'
                reason = 'Moderate delay, reduce speed'
            else:
                speed_rec = 'stop'
                reason = 'Long delay, stop and wait'
            
            return CrossingDecision(
                approved=True,
                wait_time_seconds=delay,
                crossing_window=(start_time, end_time),
                speed_recommendation=speed_rec,
                reason=reason,
                priority=priority
            )
        
        # No slot available in reasonable time
        return CrossingDecision(
            approved=False,
            wait_time_seconds=999,
            crossing_window=None,
            speed_recommendation='stop',
            reason='Intersection too congested, consider reroute',
            priority=priority
        )
    
    def release_intersection(self, car_id: str, intersection_id: str):
        """Car reports it has cleared the intersection."""
        # Remove from waiting list
        if car_id in self.waiting_cars[intersection_id]:
            self.waiting_cars[intersection_id].remove(car_id)
        
        # Remove reservation
        self.reservations[intersection_id] = [
            r for r in self.reservations[intersection_id]
            if r.car_id != car_id
        ]
    
    def get_intersection_status(self, intersection_id: str) -> Dict:
        """Get current status of an intersection."""
        current_time = time.time()
        self._cleanup_old_reservations(intersection_id, current_time)
        
        active_reservations = [
            r for r in self.reservations[intersection_id]
            if r.is_active(current_time)
        ]
        
        upcoming_reservations = [
            r for r in self.reservations[intersection_id]
            if r.start_time > current_time
        ][:5]  # Next 5
        
        return {
            'intersection_id': intersection_id,
            'current_time': current_time,
            'active_cars': [r.car_id for r in active_reservations],
            'waiting_cars': self.waiting_cars[intersection_id],
            'upcoming_reservations': [
                {
                    'car_id': r.car_id,
                    'start_time': r.start_time,
                    'priority': r.priority
                }
                for r in upcoming_reservations
            ],
            'congestion_level': self._calculate_congestion(intersection_id)
        }
    
    def _calculate_priority(self, car: Car, eta_seconds: float) -> int:
        """
        Calculate crossing priority for a car.
        
        Higher priority = crosses first.
        
        Factors:
        - Emergency vehicle: +1000
        - Waiting time: +2 per second
        - Distance/ETA: closer = higher
        """
        priority = 0
        
        # Emergency vehicles always have highest priority
        if car.is_emergency:
            priority += 1000
        
        # Waiting cars get priority boost
        # (This is calculated elsewhere if car has been waiting)
        
        # Closer cars get slight priority
        # (Inverse of ETA, capped at 100)
        if eta_seconds > 0:
            priority += int(min(100, 100 / eta_seconds))
        
        return priority
    
    def _is_slot_available(
        self,
        intersection_id: str,
        start_time: float,
        end_time: float,
        priority: int
    ) -> bool:
        """Check if a time slot is available."""
        proposed = IntersectionReservation(
            car_id="temp",
            intersection_id=intersection_id,
            start_time=start_time,
            end_time=end_time + self.SAFETY_BUFFER,
            priority=priority
        )
        
        for existing in self.reservations[intersection_id]:
            # If proposed conflicts with existing
            if proposed.conflicts_with(existing):
                # Only allow if proposed has much higher priority
                if priority <= existing.priority + 500:  # Emergency override threshold
                    return False
        
        return True
    
    def _find_next_available_slot(
        self,
        intersection_id: str,
        preferred_start: float,
        duration: float,
        priority: int
    ) -> Optional[Tuple[float, float]]:
        """
        Find next available time slot at intersection.
        
        Returns: (start_time, end_time) or None
        """
        # Sort existing reservations by start time
        sorted_reservations = sorted(
            self.reservations[intersection_id],
            key=lambda r: r.start_time
        )
        
        # Try to find gap in reservations
        search_start = preferred_start
        max_search_time = preferred_start + 30  # Don't search more than 30s ahead
        
        while search_start < max_search_time:
            search_end = search_start + duration + self.SAFETY_BUFFER
            
            # Check if this slot conflicts
            conflicts = False
            for existing in sorted_reservations:
                # Skip reservations that end before our search window
                if existing.end_time < search_start:
                    continue
                
                # If existing starts after our window, we found a gap
                if existing.start_time >= search_end:
                    break
                
                # There's a conflict, move search_start to after this reservation
                if existing.start_time <= search_start < existing.end_time:
                    search_start = existing.end_time + self.SAFETY_BUFFER
                    conflicts = True
                    break
            
            if not conflicts:
                return (search_start, search_end - self.SAFETY_BUFFER)
        
        return None
    
    def _cleanup_old_reservations(self, intersection_id: str, current_time: float):
        """Remove reservations that have expired."""
        self.reservations[intersection_id] = [
            r for r in self.reservations[intersection_id]
            if r.end_time > current_time - 5  # Keep for 5s after end for debugging
        ]
    
    def _calculate_congestion(self, intersection_id: str) -> float:
        """
        Calculate congestion level at intersection.
        
        Returns: 0.0 (free) to 1.0 (gridlock)
        """
        # Count reservations in next 30 seconds
        current_time = time.time()
        near_future = current_time + 30
        
        upcoming = [
            r for r in self.reservations[intersection_id]
            if current_time <= r.start_time <= near_future
        ]
        
        # Max ~10 cars can pass through in 30 seconds
        # (3s crossing + 1s buffer = 4s per car = 7.5 cars/30s)
        max_throughput = 7.5
        congestion = len(upcoming) / max_throughput
        
        return min(1.0, congestion)
    
    def get_performance_metrics(self) -> Dict:
        """Get system performance metrics."""
        approval_rate = (
            self.approved_requests / self.total_requests
            if self.total_requests > 0
            else 0
        )
        
        return {
            'total_requests': self.total_requests,
            'approved_requests': self.approved_requests,
            'approval_rate': approval_rate,
            'average_wait_time_seconds': round(self.average_wait_time, 2),
            'active_intersections': len([
                i for i, reservations in self.reservations.items()
                if reservations
            ])
        }


# Example usage
if __name__ == "__main__":
    from app.models.car import Car, Position, VehicleType
    from app.intelligence.car_tracker import CarTracker
    
    tracker = CarTracker()
    manager = IntersectionManager(tracker)
    
    # Simulate cars requesting to cross
    car1 = Car(car_id="car_001", vehicle_type=VehicleType.SEDAN)
    car2 = Car(car_id="car_002", vehicle_type=VehicleType.SUV)
    car3 = Car(car_id="ambulance_001", vehicle_type=VehicleType.EMERGENCY, is_emergency=True)
    
    tracker.register_car(car1)
    tracker.register_car(car2)
    tracker.register_car(car3)
    
    print("\n🚦 Intersection Manager Test\n")
    
    # Car 1 requests (arrives in 5s)
    decision1 = manager.request_crossing("car_001", "int_001", 5.0)
    print(f"Car 1: {decision1.speed_recommendation} - {decision1.reason}")
    
    # Car 2 requests (arrives in 6s - conflicts!)
    decision2 = manager.request_crossing("car_002", "int_001", 6.0)
    print(f"Car 2: {decision2.speed_recommendation} - {decision2.reason}")
    print(f"  Wait time: {decision2.wait_time_seconds:.1f}s")
    
    # Emergency vehicle (arrives in 7s - should get priority!)
    decision3 = manager.request_crossing("ambulance_001", "int_001", 7.0)
    print(f"Ambulance: {decision3.speed_recommendation} - {decision3.reason}")
    
    # Status
    status = manager.get_intersection_status("int_001")
    print(f"\n📊 Intersection Status:")
    print(f"  Active cars: {len(status['active_cars'])}")
    print(f"  Waiting cars: {len(status['waiting_cars'])}")
    print(f"  Congestion: {status['congestion_level']:.0%}")
    
    metrics = manager.get_performance_metrics()
    print(f"\n📈 Performance Metrics:")
    print(f"  Approval rate: {metrics['approval_rate']:.0%}")
    print(f"  Avg wait time: {metrics['average_wait_time_seconds']:.1f}s")

