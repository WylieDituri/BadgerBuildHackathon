from fastapi import APIRouter, HTTPException
from app.models.schemas import PlanRequest, PlanResponse
from app.services.agent import planning_agent
from app.services.memory_store import memory_store
from app.api.v1.websockets import broadcast_cars_update

router = APIRouter()


@router.post("/run-plan", response_model=PlanResponse)
async def run_plan(request: PlanRequest) -> PlanResponse:
    """
    Run the centralized planner to develop safe paths for all cars.
    
    This endpoint:
    1. Receives a list of cars with their start/end nodes and current positions
    2. Calls the PlanningAgent to compute conflict-free paths
    3. Stores paths in memory (no Firebase needed!)
    4. Broadcasts updates to all WebSocket clients
    5. Returns the planned paths
    """
    try:
        # Call the planning agent
        plan_response = planning_agent.develop_safe_paths(request.cars)
        
        # Store paths in memory (simple and fast for hackathon!)
        for path_result in plan_response.paths:
            memory_store.update_car_path(
                car_id=path_result.car_id,
                path=path_result.path,
                plan_id=plan_response.plan_id,
                status=path_result.status,
            )
        
        # Store the plan itself
        memory_store.add_plan(plan_response.plan_id, {
            "paths": [p.dict() for p in plan_response.paths],
        })
        
        # Broadcast update to all WebSocket clients (real-time!)
        await broadcast_cars_update()
        
        return plan_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(e)}")


@router.post("/cars")
async def add_car(car_data: dict):
    """Add or update a car. Broadcasts update to all WebSocket clients."""
    car_id = car_data.get("id") or car_data.get("car_id")
    if not car_id:
        raise HTTPException(status_code=400, detail="Car ID required")
    
    memory_store.add_car(car_id, car_data)
    
    # Broadcast to all connected clients
    await broadcast_cars_update()
    
    return {"status": "ok", "car_id": car_id}


@router.get("/cars")
async def get_cars():
    """Get all cars from memory store."""
    cars = memory_store.get_all_cars()
    return {"cars": cars, "count": len(cars)}


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    from app.api.v1.websockets import active_connections
    return {
        "status": "healthy",
        "service": "car-intelligence-backend",
        "storage": "memory",
        "active_websocket_connections": len(active_connections)
    }
