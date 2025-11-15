from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter()

# Active WebSocket connections
active_connections: List[WebSocket] = []


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.
    
    Clients can connect to receive live updates about car movements,
    planning results, or other system events.
    """
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            
            # Echo back for now (implement custom logic as needed)
            await websocket.send_text(f"Echo: {data}")
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)


async def broadcast_message(message: str):
    """Broadcast a message to all connected WebSocket clients."""
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except:
            # Remove dead connections
            if connection in active_connections:
                active_connections.remove(connection)
