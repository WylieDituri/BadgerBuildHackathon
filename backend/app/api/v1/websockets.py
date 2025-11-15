from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Set
import json

router = APIRouter()

# Active WebSocket connections
active_connections: Set[WebSocket] = set()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.
    
    Clients connect to receive live updates about car movements.
    Perfect for handling many concurrent users!
    """
    await websocket.accept()
    active_connections.add(websocket)
    
    try:
        # Send initial state
        from app.services.memory_store import memory_store
        cars = memory_store.get_all_cars()
        await websocket.send_json({
            "type": "initial_state",
            "cars": cars,
            "count": len(cars)
        })
        
        # Keep connection alive and listen for pings
        while True:
            data = await websocket.receive_text()
            # Handle ping/pong for keepalive
            if data == "ping":
                await websocket.send_text("pong")
            
    except WebSocketDisconnect:
        active_connections.discard(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        active_connections.discard(websocket)


async def broadcast_cars_update():
    """Broadcast car updates to all connected WebSocket clients."""
    from app.services.memory_store import memory_store
    cars = memory_store.get_all_cars()
    
    message = json.dumps({
        "type": "cars_update",
        "cars": cars,
        "count": len(cars)
    })
    
    # Broadcast to all connections
    disconnected = set()
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception:
            disconnected.add(connection)
    
    # Clean up dead connections
    for conn in disconnected:
        active_connections.discard(conn)
