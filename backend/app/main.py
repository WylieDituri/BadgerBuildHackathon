from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import endpoints, websockets
from app.api.v2 import intelligence
from app.core.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Centralized Car Intelligence API",
    description="Backend API for multi-car path planning and coordination with real-time intelligence",
    version="0.2.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for hackathon demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# V1 API (Demo/Simple)
app.include_router(endpoints.router, prefix="/api/v1", tags=["v1-planning"])
app.include_router(websockets.router, prefix="/api/v1", tags=["v1-websockets"])

# V2 API (Production/Intelligence)
app.include_router(intelligence.router, prefix="/api/v2/intelligence", tags=["v2-intelligence"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("\n" + "="*60)
    print("🚗 Centralized Car Intelligence Backend v0.2.0")
    print("="*60)
    print("📦 Using in-memory storage (no Firebase needed!)")
    print(f"✅ Backend ready on port {settings.backend_port}")
    print(f"🔌 WebSocket endpoint: ws://localhost:{settings.backend_port}/api/v1/ws")
    print("\n🧠 Intelligence Systems:")
    print("   ✓ Collision Predictor (trajectory analysis)")
    print("   ✓ Intersection Manager (coordination)")
    print("   ✓ Traffic Monitor (congestion tracking)")
    print("\n📚 API Documentation:")
    print(f"   http://localhost:{settings.backend_port}/docs")
    print(f"   http://localhost:{settings.backend_port}/")
    print("="*60 + "\n")


@app.get("/")
async def root():
    """API root - shows available endpoints."""
    return {
        "name": "Car Intelligence API",
        "version": "0.2.0",
        "status": "operational",
        "apis": {
            "v1": {
                "description": "Demo API (simple planning)",
                "prefix": "/api/v1",
                "endpoints": ["/run-plan", "/cars", "/health"]
            },
            "v2": {
                "description": "Production API (collision prediction, intersection coordination, traffic)",
                "prefix": "/api/v2/intelligence",
                "endpoints": [
                    "/cars/register",
                    "/cars/location",
                    "/collisions/predict",
                    "/intersection/request",
                    "/traffic/summary",
                    "/analytics/system-status"
                ]
            }
        },
        "documentation": f"http://localhost:{settings.backend_port}/docs",
        "system_status": f"http://localhost:{settings.backend_port}/api/v2/intelligence/analytics/system-status"
    }
