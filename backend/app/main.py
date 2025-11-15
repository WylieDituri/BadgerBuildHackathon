from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import endpoints, websockets
from app.core.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Centralized Car Intelligence API",
    description="Backend API for multi-car path planning and coordination",
    version="0.1.0",
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
app.include_router(endpoints.router, prefix="/api/v1", tags=["planning"])
app.include_router(websockets.router, prefix="/api/v1", tags=["websockets"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("🚗 Initializing Centralized Car Intelligence Backend...")
    print("📦 Using in-memory storage (no Firebase needed!)")
    print(f"✅ Backend ready on port {settings.backend_port}")
    print(f"🔌 WebSocket endpoint: ws://localhost:{settings.backend_port}/api/v1/ws")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Centralized Car Intelligence API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }
