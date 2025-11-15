from fastapi import APIRouter, HTTPException
from app.models.schemas import PlanRequest, PlanResponse
from app.services.agent import planning_agent
from app.services.firebase_admin import get_db
from app.core.config import settings

router = APIRouter()


@router.post("/run-plan", response_model=PlanResponse)
async def run_plan(request: PlanRequest) -> PlanResponse:
    """
    Run the centralized planner to develop safe paths for all cars.
    
    This endpoint:
    1. Receives a list of cars with their start/end nodes and current positions
    2. Calls the PlanningAgent to compute conflict-free paths
    3. Optionally updates Firestore with the new paths
    4. Returns the planned paths
    """
    try:
        # Call the planning agent
        plan_response = planning_agent.develop_safe_paths(request.cars)
        
        # Optional: Update Firestore with the new paths
        try:
            db = get_db()
            if db:
                for path_result in plan_response.paths:
                    # Path: artifacts/{appId}/data/public/cars/{carId}
                    car_ref = db.collection("artifacts").document(settings.app_id).collection("data").document("public").collection("cars").document(path_result.car_id)
                    car_ref.update({
                        "path": [{"x": x, "y": y} for x, y in path_result.path],
                        "plan_id": plan_response.plan_id,
                        "status": path_result.status,
                    })
        except Exception as e:
            print(f"Warning: Could not update Firestore: {e}")
        
        return plan_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "car-intelligence-backend"}
