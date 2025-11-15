"""
Simple in-memory storage for hackathon demo.
No Firebase needed - data lives in memory during runtime.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


class MemoryStore:
    """In-memory data store. Perfect for hackathon demos!"""
    
    def __init__(self):
        self.cars: Dict[str, Dict[str, Any]] = {}
        self.plans: Dict[str, Dict[str, Any]] = {}
        self.requests: List[Dict[str, Any]] = []
    
    def add_car(self, car_id: str, data: Dict[str, Any]) -> None:
        """Add or update a car."""
        self.cars[car_id] = {
            **data,
            "updated_at": datetime.utcnow().isoformat(),
        }
    
    def get_car(self, car_id: str) -> Optional[Dict[str, Any]]:
        """Get a car by ID."""
        return self.cars.get(car_id)
    
    def get_all_cars(self) -> Dict[str, Dict[str, Any]]:
        """Get all cars."""
        return self.cars.copy()
    
    def update_car_path(self, car_id: str, path: List[tuple], plan_id: str, status: str) -> None:
        """Update a car's path."""
        if car_id not in self.cars:
            self.cars[car_id] = {}
        self.cars[car_id].update({
            "path": [{"x": x, "y": y} for x, y in path],
            "plan_id": plan_id,
            "status": status,
            "updated_at": datetime.utcnow().isoformat(),
        })
    
    def add_plan(self, plan_id: str, data: Dict[str, Any]) -> None:
        """Add a plan."""
        self.plans[plan_id] = {
            **data,
            "created_at": datetime.utcnow().isoformat(),
        }
    
    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get a plan by ID."""
        return self.plans.get(plan_id)
    
    def add_request(self, request_data: Dict[str, Any]) -> str:
        """Add a request and return its ID."""
        request_id = str(uuid.uuid4())
        self.requests.append({
            "id": request_id,
            **request_data,
            "created_at": datetime.utcnow().isoformat(),
        })
        return request_id
    
    def clear_all(self) -> None:
        """Clear all data (useful for testing)."""
        self.cars.clear()
        self.plans.clear()
        self.requests.clear()


# Global singleton instance
memory_store = MemoryStore()

