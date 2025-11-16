"""
Race API Endpoints
Handles race creation, player registration, and race management.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.services.race_manager import (
    race_manager,
    RaceCheckpoint,
    RaceStatus,
    PlayerStatus
)

router = APIRouter()


# Request/Response Models
class CreateRaceRequest(BaseModel):
    race_id: str
    name: str
    destination_name: str
    destination_lat: float
    destination_lon: float
    destination_radius: float = 20.0


class RegisterPlayerRequest(BaseModel):
    player_id: str
    username: str
    start_point_name: str
    start_lat: float
    start_lon: float


class UpdatePositionRequest(BaseModel):
    player_id: str
    lat: float
    lon: float
    speed_mps: float


# Admin Endpoints
@router.post("/admin/race/create")
async def create_race(request: CreateRaceRequest):
    """Create a new race (admin only)"""
    destination = RaceCheckpoint(
        name=request.destination_name,
        lat=request.destination_lat,
        lon=request.destination_lon,
        radius_meters=request.destination_radius
    )
    
    race = race_manager.create_race(
        race_id=request.race_id,
        name=request.name,
        destination=destination
    )
    
    return {
        "status": "created",
        "race_id": race.race_id,
        "name": race.name,
        "destination": {
            "name": destination.name,
            "lat": destination.lat,
            "lon": destination.lon
        }
    }


@router.post("/admin/race/{race_id}/start")
async def start_race(race_id: str):
    """Start a race (admin only) - works for lobby"""
    race = race_manager.get_race(race_id)
    if not race:
        raise HTTPException(404, "Race not found")
    
    # Force start from waiting or re-start from active
    if race.status == RaceStatus.FINISHED:
        race.status = RaceStatus.WAITING
    
    success = race_manager.start_race(race_id)
    
    if not success:
        raise HTTPException(400, "Cannot start race. Check status and players.")
    
    return {
        "status": "started",
        "race_id": race_id,
        "started_at": datetime.now().isoformat()
    }


@router.post("/admin/race/{race_id}/end")
async def end_race(race_id: str):
    """End a race (admin only)"""
    success = race_manager.end_race(race_id)
    
    if not success:
        raise HTTPException(404, "Race not found")
    
    return {
        "status": "ended",
        "race_id": race_id
    }


@router.get("/admin/race/{race_id}/status")
async def get_race_status(race_id: str):
    """Get complete race status (admin only)"""
    race = race_manager.get_race(race_id)
    
    if not race:
        raise HTTPException(404, "Race not found")
    
    # Auto-end race if everyone is done
    should_end = race.should_auto_end()
    if should_end and race.status.value == "active":
        race_manager.end_race(race_id)
    
    return {
        "race_id": race.race_id,
        "name": race.name,
        "status": race.status.value,
        "created_at": race.created_at.isoformat(),
        "started_at": race.started_at.isoformat() if race.started_at else None,
        "destination": {
            "name": race.destination.name,
            "lat": race.destination.lat,
            "lon": race.destination.lon
        },
        "players": {
            "total": len(race.players),
            "racing": len(race.get_active_players()),
            "finished": len(race.get_finished_players()),
            "crashed": len(race.get_crashed_players())
        },
        "leaderboard": race.get_leaderboard(),
        "should_auto_end": should_end
    }


@router.get("/admin/race/active")
async def get_active_race():
    """Get the currently active race (admin only)"""
    race = race_manager.get_active_race()
    
    if not race:
        return {"active_race": None}
    
    return {
        "active_race": {
            "race_id": race.race_id,
            "name": race.name,
            "status": race.status.value,
            "player_count": len(race.players)
        }
    }


@router.get("/admin/race/{race_id}/players")
async def get_all_players(race_id: str):
    """Get all players with positions for admin map"""
    race = race_manager.get_race(race_id)
    
    if not race:
        raise HTTPException(404, "Race not found")
    
    players_data = []
    for player in race.players.values():
        dest = player.destination if player.destination else race.destination
        players_data.append({
            "player_id": player.player_id,
            "username": player.username,
            "status": player.status.value,
            "position": {
                "lat": player.current_lat,
                "lon": player.current_lon
            },
            "destination": {
                "lat": dest.lat,
                "lon": dest.lon
            },
            "speed": player.current_speed
        })
    
    return {
        "race_id": race_id,
        "players": players_data
    }


# Player Endpoints
@router.post("/player/register")
async def register_player(request: RegisterPlayerRequest):
    """Register a player for the permanent lobby"""
    # Get or create the lobby
    race = race_manager.get_or_create_lobby()
    
    start_point = RaceCheckpoint(
        name=request.start_point_name,
        lat=request.start_lat,
        lon=request.start_lon
    )
    
    car_id = f"race_{request.player_id}_lobby"
    
    success = race_manager.register_player(
        race_id=race.race_id,
        player_id=request.player_id,
        username=request.username,
        car_id=car_id,
        start_point=start_point
    )
    
    if not success:
        raise HTTPException(400, "Cannot register. Lobby may be full.")
    
    # Get player to return destination
    player = race.players.get(request.player_id)
    dest = player.destination if player and player.destination else race.destination
    
    return {
        "status": "registered",
        "player_id": request.player_id,
        "race_id": race.race_id,
        "car_id": car_id,
        "destination": {
            "name": dest.name,
            "lat": dest.lat,
            "lon": dest.lon
        }
    }


@router.post("/player/position")
async def update_player_position(request: UpdatePositionRequest):
    """Update player position during race"""
    result = race_manager.update_player_position(
        player_id=request.player_id,
        lat=request.lat,
        lon=request.lon,
        speed_mps=request.speed_mps
    )
    
    if not result:
        raise HTTPException(400, "Player not in active race")
    
    return result


@router.get("/player/{player_id}/stats")
async def get_player_stats(player_id: str):
    """Get stats for a specific player"""
    stats = race_manager.get_player_stats(player_id)
    
    if not stats:
        raise HTTPException(404, "Player not found in any race")
    
    return stats


@router.get("/player/{player_id}/race")
async def get_player_race_info(player_id: str):
    """Get race info for a player (limited view)"""
    race_id = race_manager.player_to_race.get(player_id)
    
    if not race_id:
        raise HTTPException(404, "Player not in any race")
    
    race = race_manager.get_race(race_id)
    if not race:
        raise HTTPException(404, "Race not found")
    
    player = race.players.get(player_id)
    if not player:
        raise HTTPException(404, "Player not found in race")
    
    # Use personal destination if available
    dest = player.destination if player.destination else race.destination
    
    # Calculate distance to personal destination
    distance_to_finish = None
    if player.status == PlayerStatus.RACING and dest:
        distance_to_finish = round(race._haversine_distance(
            player.current_lat, player.current_lon,
            dest.lat, dest.lon
        ), 2)
    
    # Limited view - only show destination and player's own info
    return {
        "race_id": race.race_id,
        "name": race.name,
        "status": race.status.value,
        "destination": {
            "name": dest.name,
            "lat": dest.lat,
            "lon": dest.lon
        },
        "your_position": {
            "lat": player.current_lat,
            "lon": player.current_lon
        },
        "your_status": player.status.value,
        "distance_to_finish": distance_to_finish
    }

