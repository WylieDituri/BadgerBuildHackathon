"""
Race Management Service
Handles race creation, player registration, crash detection, and timing.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime
from enum import Enum
import math


class RaceStatus(str, Enum):
    WAITING = "waiting"  # Waiting for admin to start
    COUNTDOWN = "countdown"  # 3, 2, 1, GO!
    ACTIVE = "active"  # Race in progress
    FINISHED = "finished"  # Race completed


class PlayerStatus(str, Enum):
    REGISTERED = "registered"  # Signed up but not started
    RACING = "racing"  # Currently racing
    CRASHED = "crashed"  # Eliminated
    FINISHED = "finished"  # Completed the race


@dataclass
class RaceCheckpoint:
    """A checkpoint or destination in the race"""
    name: str
    lat: float
    lon: float
    radius_meters: float = 20.0  # How close player needs to be


@dataclass
class Player:
    """A player in the race"""
    player_id: str
    username: str
    car_id: str
    start_point: RaceCheckpoint
    destination: Optional[RaceCheckpoint] = None  # Personal destination (opposite corner)
    status: PlayerStatus = PlayerStatus.REGISTERED
    start_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None
    crash_time: Optional[datetime] = None
    total_time_seconds: Optional[float] = None
    current_lat: float = 0.0
    current_lon: float = 0.0
    current_speed: float = 0.0
    distance_traveled: float = 0.0  # meters
    last_update_time: datetime = field(default_factory=datetime.now)
    
    def get_race_time_seconds(self) -> Optional[float]:
        """Calculate current or final race time"""
        if not self.start_time:
            return None
        
        end_time = self.finish_time or self.crash_time or datetime.now()
        return (end_time - self.start_time).total_seconds()
    
    def is_afk(self, threshold_seconds: float = 10.0) -> bool:
        """Check if player has been inactive"""
        if self.status != PlayerStatus.RACING:
            return False
        return (datetime.now() - self.last_update_time).total_seconds() > threshold_seconds
    
    def calculate_opposite_corner_destination(self) -> RaceCheckpoint:
        """Calculate opposite corner from start position"""
        # Convert to map coordinates
        start_x = (self.start_point.lon + 89.401) * 1000
        start_y = (self.start_point.lat - 43.073) * 1000
        
        # Calculate opposite corner
        dest_x = -start_x
        dest_y = -start_y
        
        # Convert back to GPS
        dest_lat = dest_y / 1000 + 43.073
        dest_lon = dest_x / 1000 - 89.401
        
        return RaceCheckpoint(
            name=f"Opposite of {self.start_point.name}",
            lat=dest_lat,
            lon=dest_lon,
            radius_meters=25.0
        )


@dataclass
class Race:
    """A race session"""
    race_id: str
    name: str
    destination: RaceCheckpoint
    status: RaceStatus = RaceStatus.WAITING
    players: Dict[str, Player] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    countdown_start: Optional[datetime] = None
    max_players: int = 20
    crash_detection_enabled: bool = True
    collision_radius_meters: float = 8.0  # Distance considered a crash (matches frontend car size)
    
    def add_player(self, player: Player) -> bool:
        """Add a player to the race"""
        if len(self.players) >= self.max_players:
            return False
        # Allow joining if waiting or during active race (for lobby)
        if self.status not in [RaceStatus.WAITING, RaceStatus.ACTIVE]:
            return False
        
        self.players[player.player_id] = player
        return True
    
    def get_active_players(self) -> List[Player]:
        """Get players currently racing"""
        return [p for p in self.players.values() if p.status == PlayerStatus.RACING]
    
    def get_finished_players(self) -> List[Player]:
        """Get players who finished, sorted by time"""
        finished = [p for p in self.players.values() if p.status == PlayerStatus.FINISHED]
        return sorted(finished, key=lambda p: p.total_time_seconds or float('inf'))
    
    def get_crashed_players(self) -> List[Player]:
        """Get players who crashed"""
        return [p for p in self.players.values() if p.status == PlayerStatus.CRASHED]
    
    def should_auto_end(self) -> bool:
        """Check if race should automatically end"""
        if self.status != RaceStatus.ACTIVE:
            return False
        
        if len(self.players) == 0:
            return False
        
        # Check if all players are done (finished, crashed, or AFK)
        for player in self.players.values():
            if player.status == PlayerStatus.RACING:
                if not player.is_afk(10.0):  # 10 second AFK threshold
                    return False  # At least one active player
        
        return True  # All players done
    
    def get_leaderboard(self) -> List[dict]:
        """Get race leaderboard"""
        leaderboard = []
        
        # Add finished players first
        for rank, player in enumerate(self.get_finished_players(), 1):
            leaderboard.append({
                'rank': rank,
                'player_id': player.player_id,
                'username': player.username,
                'status': 'finished',
                'time': player.total_time_seconds,
                'distance': player.distance_traveled
            })
        
        # Add currently racing players
        racing = self.get_active_players()
        racing.sort(key=lambda p: self._distance_to_destination(p))
        
        for player in racing:
            leaderboard.append({
                'rank': None,
                'player_id': player.player_id,
                'username': player.username,
                'status': 'racing',
                'time': player.get_race_time_seconds(),
                'distance': player.distance_traveled,
                'distance_to_finish': self._distance_to_destination(player)
            })
        
        # Add crashed players
        for player in self.get_crashed_players():
            leaderboard.append({
                'rank': None,
                'player_id': player.player_id,
                'username': player.username,
                'status': 'crashed',
                'time': player.get_race_time_seconds(),
                'distance': player.distance_traveled
            })
        
        return leaderboard
    
    def _distance_to_destination(self, player: Player) -> float:
        """Calculate distance from player to destination in meters"""
        return self._haversine_distance(
            player.current_lat, player.current_lon,
            self.destination.lat, self.destination.lon
        )
    
    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in meters"""
        R = 6371000  # Earth radius in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi / 2) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c


class RaceManager:
    """Manages all race sessions"""
    
    def __init__(self):
        self.races: Dict[str, Race] = {}
        self.active_race_id: Optional[str] = None
        self.player_to_race: Dict[str, str] = {}  # player_id -> race_id
    
    def create_race(self, race_id: str, name: str, destination: RaceCheckpoint) -> Race:
        """Create a new race"""
        race = Race(
            race_id=race_id,
            name=name,
            destination=destination
        )
        self.races[race_id] = race
        self.active_race_id = race_id
        return race
    
    def get_or_create_lobby(self) -> Race:
        """Get or create the permanent lobby race"""
        lobby_id = "permanent_lobby"
        
        if lobby_id in self.races:
            race = self.races[lobby_id]
            # Reset if finished
            if race.status == RaceStatus.FINISHED:
                race.status = RaceStatus.WAITING
                race.players.clear()
                race.started_at = None
                race.finished_at = None
            return race
        
        # Create permanent lobby
        race = Race(
            race_id=lobby_id,
            name="Global Lobby",
            destination=RaceCheckpoint("Center", 43.073, -89.401, 25.0),
            max_players=50
        )
        self.races[lobby_id] = race
        self.active_race_id = lobby_id
        return race
    
    def get_race(self, race_id: str) -> Optional[Race]:
        """Get a race by ID"""
        return self.races.get(race_id)
    
    def get_active_race(self) -> Optional[Race]:
        """Get the currently active race"""
        # Always return the lobby
        return self.get_or_create_lobby()
    
    def register_player(
        self,
        race_id: str,
        player_id: str,
        username: str,
        car_id: str,
        start_point: RaceCheckpoint
    ) -> bool:
        """Register a player for a race"""
        race = self.get_race(race_id)
        if not race:
            return False
        
        player = Player(
            player_id=player_id,
            username=username,
            car_id=car_id,
            start_point=start_point,
            current_lat=start_point.lat,
            current_lon=start_point.lon
        )
        
        # Calculate opposite corner destination
        player.destination = player.calculate_opposite_corner_destination()
        
        success = race.add_player(player)
        if success:
            self.player_to_race[player_id] = race_id
        
        return success
    
    def start_race(self, race_id: str) -> bool:
        """Start a race (after countdown)"""
        race = self.get_race(race_id)
        if not race or race.status != RaceStatus.WAITING:
            return False
        
        race.status = RaceStatus.ACTIVE
        race.started_at = datetime.now()
        
        # Set all players to racing
        for player in race.players.values():
            player.status = PlayerStatus.RACING
            player.start_time = race.started_at
        
        return True
    
    def update_player_position(
        self,
        player_id: str,
        lat: float,
        lon: float,
        speed_mps: float
    ) -> Optional[dict]:
        """Update a player's position and check for finish/crash"""
        race_id = self.player_to_race.get(player_id)
        if not race_id:
            return None
        
        race = self.get_race(race_id)
        if not race:
            return None
        
        player = race.players.get(player_id)
        if not player:
            return None
        
        # Update position (always update, even if waiting)
        old_lat, old_lon = player.current_lat, player.current_lon
        player.current_lat = lat
        player.current_lon = lon
        player.current_speed = speed_mps
        player.last_update_time = datetime.now()  # Track activity
        
        # Only check finish/crash if actually racing
        if race.status != RaceStatus.ACTIVE or player.status != PlayerStatus.RACING:
            return {'event': 'position_updated', 'player_id': player_id}
        
        # Update distance traveled
        if old_lat != 0 and old_lon != 0:
            segment_distance = race._haversine_distance(old_lat, old_lon, lat, lon)
            player.distance_traveled += segment_distance
        
        # Check if reached destination (use personal destination)
        if player.destination:
            dest_lat = player.destination.lat
            dest_lon = player.destination.lon
            dest_radius = player.destination.radius_meters
        else:
            dest_lat = race.destination.lat
            dest_lon = race.destination.lon
            dest_radius = race.destination.radius_meters
        
        distance_to_dest = race._haversine_distance(lat, lon, dest_lat, dest_lon)
        if distance_to_dest <= dest_radius:
            player.status = PlayerStatus.FINISHED
            player.finish_time = datetime.now()
            player.total_time_seconds = player.get_race_time_seconds()
            
            return {
                'event': 'finished',
                'player_id': player_id,
                'time': player.total_time_seconds,
                'rank': len(race.get_finished_players())
            }
        
        # Check for crashes with other players
        if race.crash_detection_enabled:
            for other in race.get_active_players():
                if other.player_id == player_id:
                    continue
                
                distance = race._haversine_distance(
                    lat, lon, other.current_lat, other.current_lon
                )
                
                if distance <= race.collision_radius_meters:
                    # Both players crash
                    player.status = PlayerStatus.CRASHED
                    player.crash_time = datetime.now()
                    
                    other.status = PlayerStatus.CRASHED
                    other.crash_time = datetime.now()
                    
                    return {
                        'event': 'crashed',
                        'player_id': player_id,
                        'crashed_with': other.player_id,
                        'time': player.get_race_time_seconds()
                    }
        
        return {'event': 'position_updated'}
    
    def end_race(self, race_id: str) -> bool:
        """End a race"""
        race = self.get_race(race_id)
        if not race:
            return False
        
        race.status = RaceStatus.FINISHED
        race.finished_at = datetime.now()
        
        # Mark any still-racing players as finished
        for player in race.get_active_players():
            player.status = PlayerStatus.FINISHED
            player.finish_time = datetime.now()
            player.total_time_seconds = player.get_race_time_seconds()
        
        return True
    
    def get_player_stats(self, player_id: str) -> Optional[dict]:
        """Get stats for a specific player"""
        race_id = self.player_to_race.get(player_id)
        if not race_id:
            return None
        
        race = self.get_race(race_id)
        if not race:
            return None
        
        player = race.players.get(player_id)
        if not player:
            return None
        
        stats = {
            'player_id': player_id,
            'username': player.username,
            'status': player.status.value,
            'distance_traveled': round(player.distance_traveled, 2),
            'current_speed_mps': round(player.current_speed, 2),
            'current_speed_mph': round(player.current_speed * 2.237, 2),
        }
        
        if player.status == PlayerStatus.FINISHED:
            stats['time_seconds'] = round(player.total_time_seconds, 2)
            stats['rank'] = len([p for p in race.get_finished_players() 
                                if p.total_time_seconds < player.total_time_seconds]) + 1
            stats['total_finishers'] = len(race.get_finished_players())
        elif player.status == PlayerStatus.CRASHED:
            stats['time_before_crash'] = round(player.get_race_time_seconds(), 2)
        elif player.status == PlayerStatus.RACING:
            stats['current_time'] = round(player.get_race_time_seconds(), 2)
            stats['distance_to_finish'] = round(race._distance_to_destination(player), 2)
        
        return stats


# Global race manager instance
race_manager = RaceManager()

