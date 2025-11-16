"""
V2 Intelligence API - Production endpoints for real traffic intelligence.
Integrates collision prediction, intersection coordination, and traffic monitoring.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

from app.models.car import Car, Position, VehicleType, RouteStatus
from app.intelligence.car_tracker import car_tracker
from app.intelligence.collision_predictor import CollisionPredictor
from app.intelligence.intersection_manager import IntersectionManager
from app.intelligence.traffic_monitor import traffic_monitor


# Initialize intelligence systems
collision_predictor = CollisionPredictor(car_tracker)
intersection_manager = IntersectionManager(car_tracker)

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class RegisterCarRequest(BaseModel):
    car_id: str = Field(..., description="Unique car identifier")
    vehicle_type: str = Field(default="sedan", description="Type of vehicle")
    owner_id: Optional[str] = None
    is_emergency: bool = False


class LocationUpdateRequest(BaseModel):
    car_id: str
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    heading: float = Field(..., ge=0, lt=360, description="Degrees, 0=North")
    speed_mps: float = Field(..., ge=0, description="Speed in meters/second")


class IntersectionRequest(BaseModel):
    car_id: str
    intersection_id: str
    eta_seconds: float = Field(..., ge=0, description="Estimated time to arrival")


class IncidentReport(BaseModel):
    lat: float
    lon: float
    incident_type: str = Field(..., description="accident, construction, weather, event")
    severity: str = Field(..., description="low, medium, high, critical")
    description: str
    lanes_blocked: int = 0


# ============================================================================
# Car Management Endpoints
# ============================================================================

@router.post("/cars/register")
async def register_car(request: RegisterCarRequest):
    """
    Register a new car in the system.
    
    This must be called before a car can report positions or request services.
    """
    try:
        vehicle_type = VehicleType(request.vehicle_type)
    except ValueError:
        raise HTTPException(400, f"Invalid vehicle_type: {request.vehicle_type}")
    
    car = Car(
        car_id=request.car_id,
        vehicle_type=vehicle_type,
        owner_id=request.owner_id,
        is_emergency=request.is_emergency
    )
    
    car_tracker.register_car(car)
    
    return {
        "status": "registered",
        "car_id": request.car_id,
        "vehicle_type": request.vehicle_type,
        "is_emergency": request.is_emergency,
        "message": "Car successfully registered in intelligence system"
    }


@router.post("/cars/location")
async def update_location(
    request: LocationUpdateRequest,
    background_tasks: BackgroundTasks
):
    """
    Update a car's current location.
    
    This triggers:
    - Position tracking update
    - Collision prediction check
    - Traffic pattern analysis
    """
    # Update position
    position = car_tracker.update_position(
        car_id=request.car_id,
        lat=request.lat,
        lon=request.lon,
        heading=request.heading,
        speed_mps=request.speed_mps
    )
    
    # Background: Check for collisions with this car
    background_tasks.add_task(
        check_collisions_background,
        request.car_id
    )
    
    return {
        "status": "updated",
        "car_id": request.car_id,
        "position": position.to_dict(),
        "timestamp": position.timestamp.isoformat()
    }


@router.get("/cars/{car_id}")
async def get_car_info(car_id: str):
    """Get current information about a car."""
    car = car_tracker.get_car(car_id)
    
    if not car:
        raise HTTPException(404, f"Car {car_id} not found")
    
    return car.to_dict()


@router.get("/cars")
async def list_cars(active_only: bool = False):
    """
    List all cars in the system.
    
    Query params:
    - active_only: If true, only return cars with recent positions
    """
    if active_only:
        cars = car_tracker.get_active_cars()
    else:
        cars = car_tracker.get_all_cars()
    
    return {
        "count": len(cars),
        "cars": [car.to_dict() for car in cars]
    }


# ============================================================================
# Collision Prediction Endpoints
# ============================================================================

@router.get("/collisions/predict")
async def predict_collisions():
    """
    Predict all potential collisions in the system.
    
    Returns list of collision predictions sorted by urgency.
    """
    predictions = collision_predictor.predict_all_collisions()
    
    return {
        "count": len(predictions),
        "predictions": [pred.to_dict() for pred in predictions],
        "timestamp": datetime.now().isoformat()
    }


@router.get("/collisions/check/{car_id}")
async def check_car_collisions(car_id: str):
    """
    Check if a specific car is at risk of collision.
    
    Returns predictions only involving this car.
    """
    car = car_tracker.get_car(car_id)
    if not car:
        raise HTTPException(404, f"Car {car_id} not found")
    
    predictions = collision_predictor.check_car(car_id)
    
    if predictions:
        return {
            "at_risk": True,
            "count": len(predictions),
            "predictions": [pred.to_dict() for pred in predictions],
            "highest_severity": max(p.severity for p in predictions)
        }
    else:
        return {
            "at_risk": False,
            "count": 0,
            "predictions": [],
            "message": "No collision risk detected"
        }


# ============================================================================
# Intersection Coordination Endpoints
# ============================================================================

@router.post("/intersection/request")
async def request_intersection_crossing(request: IntersectionRequest):
    """
    Request permission to cross an intersection.
    
    Returns timing and speed recommendations.
    """
    decision = intersection_manager.request_crossing(
        car_id=request.car_id,
        intersection_id=request.intersection_id,
        eta_seconds=request.eta_seconds
    )
    
    return decision.to_dict()


@router.post("/intersection/release")
async def release_intersection(car_id: str, intersection_id: str):
    """
    Report that car has cleared the intersection.
    
    This frees up the intersection for other cars.
    """
    intersection_manager.release_intersection(car_id, intersection_id)
    
    return {
        "status": "released",
        "car_id": car_id,
        "intersection_id": intersection_id
    }


@router.get("/intersection/{intersection_id}/status")
async def get_intersection_status(intersection_id: str):
    """Get current status and congestion at an intersection."""
    status = intersection_manager.get_intersection_status(intersection_id)
    return status


@router.get("/intersection/metrics")
async def get_intersection_metrics():
    """Get performance metrics for intersection management system."""
    metrics = intersection_manager.get_performance_metrics()
    return metrics


# ============================================================================
# Traffic Monitoring Endpoints
# ============================================================================

@router.get("/traffic/summary")
async def get_traffic_summary():
    """Get summary of current traffic conditions."""
    summary = traffic_monitor.get_traffic_summary()
    return summary


@router.get("/traffic/segment/{segment_id}")
async def get_segment_traffic(segment_id: str):
    """Get traffic data for a specific road segment."""
    traffic = traffic_monitor.get_segment_traffic(segment_id)
    
    if not traffic:
        raise HTTPException(404, f"No traffic data for segment {segment_id}")
    
    return traffic.to_dict()


@router.get("/traffic/congested")
async def get_congested_segments(min_congestion: float = 0.6):
    """
    Get all road segments with high congestion.
    
    Query params:
    - min_congestion: Minimum congestion level (0.0-1.0)
    """
    segments = traffic_monitor.get_congested_segments(min_congestion)
    
    return {
        "count": len(segments),
        "segments": [seg.to_dict() for seg in segments]
    }


@router.post("/traffic/incident/report")
async def report_traffic_incident(incident: IncidentReport):
    """Report a traffic incident (accident, construction, etc.)"""
    import uuid
    
    incident_id = f"incident_{uuid.uuid4().hex[:8]}"
    
    traffic_monitor.report_incident(
        incident_id=incident_id,
        lat=incident.lat,
        lon=incident.lon,
        incident_type=incident.incident_type,
        severity=incident.severity,
        description=incident.description
    )
    
    return {
        "status": "reported",
        "incident_id": incident_id,
        "type": incident.incident_type,
        "severity": incident.severity
    }


@router.post("/traffic/incident/{incident_id}/clear")
async def clear_incident(incident_id: str):
    """Mark a traffic incident as cleared."""
    traffic_monitor.clear_incident(incident_id)
    
    return {
        "status": "cleared",
        "incident_id": incident_id
    }


# ============================================================================
# Analytics & Monitoring Endpoints
# ============================================================================

@router.get("/analytics/system-status")
async def get_system_status():
    """Get overall system status and health."""
    active_cars = car_tracker.get_active_cars()
    all_cars = car_tracker.get_all_cars()
    
    collision_predictions = collision_predictor.predict_all_collisions()
    critical_collisions = [p for p in collision_predictions if p.severity == 'critical']
    
    traffic_summary = traffic_monitor.get_traffic_summary()
    intersection_metrics = intersection_manager.get_performance_metrics()
    
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "cars": {
            "total_registered": len(all_cars),
            "currently_active": len(active_cars),
            "emergency_vehicles": len([c for c in all_cars if c.is_emergency])
        },
        "collisions": {
            "total_predictions": len(collision_predictions),
            "critical_risk": len(critical_collisions),
            "at_risk_cars": len(set(
                p.car1_id for p in collision_predictions
            ).union(p.car2_id for p in collision_predictions))
        },
        "traffic": {
            "monitored_segments": traffic_summary.get('total_segments', 0),
            "average_congestion": traffic_summary.get('average_congestion', 0),
            "active_incidents": traffic_summary.get('active_incidents', 0)
        },
        "intersections": {
            "total_requests": intersection_metrics['total_requests'],
            "approval_rate": intersection_metrics['approval_rate'],
            "average_wait_time": intersection_metrics['average_wait_time_seconds']
        }
    }


@router.get("/analytics/cars-in-area")
async def get_cars_in_area(
    lat: float,
    lon: float,
    radius_km: float = 1.0
):
    """
    Find all cars within a radius of a point.
    
    Useful for area-based queries and visualization.
    """
    cars = car_tracker.get_cars_in_area(lat, lon, radius_km)
    
    return {
        "center": {"lat": lat, "lon": lon},
        "radius_km": radius_km,
        "count": len(cars),
        "cars": [car.to_dict() for car in cars]
    }


# ============================================================================
# Background Tasks
# ============================================================================

async def check_collisions_background(car_id: str):
    """Background task to check collisions for a car."""
    try:
        predictions = collision_predictor.check_car(car_id)
        
        if predictions:
            # Log critical collisions
            for pred in predictions:
                if pred.severity in ['critical', 'high']:
                    print(f"⚠️  COLLISION RISK: {pred.car1_id} vs {pred.car2_id} "
                          f"in {pred.time_to_collision_seconds:.1f}s ({pred.severity})")
    except Exception as e:
        print(f"Error in collision check background task: {e}")

