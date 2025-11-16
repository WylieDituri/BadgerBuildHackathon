"""
Traffic monitor - integrates with external traffic APIs and maintains
real-time traffic conditions for routing decisions.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class CongestionLevel(str, Enum):
    """Traffic congestion levels."""
    FREE_FLOW = "free_flow"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    SEVERE = "severe"


@dataclass
class RoadSegmentTraffic:
    """Traffic data for a road segment."""
    segment_id: str
    congestion_level: CongestionLevel
    congestion_factor: float  # 0.0 (free) to 1.0 (gridlock)
    current_speed_kmh: float
    free_flow_speed_kmh: float
    last_updated: datetime
    
    def get_travel_time_multiplier(self) -> float:
        """
        Calculate how much longer this segment takes vs free flow.
        Returns: 1.0 (normal) to 5.0 (very slow)
        """
        if self.current_speed_kmh < 1:
            return 5.0  # Gridlock
        
        return self.free_flow_speed_kmh / self.current_speed_kmh
    
    def to_dict(self):
        return {
            'segment_id': self.segment_id,
            'congestion_level': self.congestion_level.value,
            'congestion_factor': round(self.congestion_factor, 2),
            'current_speed_kmh': round(self.current_speed_kmh, 1),
            'free_flow_speed_kmh': round(self.free_flow_speed_kmh, 1),
            'last_updated': self.last_updated.isoformat()
        }


class TrafficMonitor:
    """Monitors real-time traffic conditions."""
    
    def __init__(self, google_maps_api_key: Optional[str] = None):
        self.api_key = google_maps_api_key
        
        # Cache traffic data
        self.traffic_data: Dict[str, RoadSegmentTraffic] = {}
        
        # Track incidents
        self.active_incidents: Dict[str, dict] = {}
        
        # Monitoring state
        self.is_monitoring = False
        self.update_interval = 60  # seconds
        self.last_update = None
    
    async def start_monitoring(self, bounding_box: Optional[Tuple] = None):
        """
        Start monitoring traffic in a bounding box.
        
        Args:
            bounding_box: (min_lat, min_lon, max_lat, max_lon)
        """
        print("🚦 Starting traffic monitoring...")
        self.is_monitoring = True
        
        while self.is_monitoring:
            try:
                await self.fetch_traffic_data(bounding_box)
                self.last_update = datetime.now()
                print(f"✓ Traffic data updated: {len(self.traffic_data)} segments")
                
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                print(f"❌ Error fetching traffic data: {e}")
                await asyncio.sleep(self.update_interval)
    
    def stop_monitoring(self):
        """Stop traffic monitoring."""
        self.is_monitoring = False
        print("🛑 Traffic monitoring stopped")
    
    async def fetch_traffic_data(self, bounding_box: Optional[Tuple] = None):
        """
        Fetch traffic data from external API.
        
        For now, this is a placeholder. In production, you would:
        1. Call Google Maps Traffic API
        2. Call TomTom Traffic Flow API
        3. Parse Waze data
        """
        if self.api_key:
            await self._fetch_google_traffic(bounding_box)
        else:
            # Simulate traffic data for testing
            await self._simulate_traffic_data()
    
    async def _fetch_google_traffic(self, bounding_box: Optional[Tuple]):
        """
        Fetch traffic from Google Maps API.
        
        API: https://developers.google.com/maps/documentation/roads
        """
        if not bounding_box:
            return
        
        # Example API call (you need to implement based on Google's API)
        url = "https://roads.googleapis.com/v1/speedLimits"
        params = {
            'key': self.api_key,
            # Add path or place parameters
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._process_google_traffic_data(data)
                    else:
                        print(f"Google API error: {response.status}")
            except Exception as e:
                print(f"Error calling Google API: {e}")
    
    async def _simulate_traffic_data(self):
        """
        Simulate traffic data for testing/demo.
        
        In production, remove this and use real APIs.
        """
        import random
        
        # Simulate some road segments with varying traffic
        segments = [
            f"segment_{i:03d}" for i in range(1, 51)  # 50 segments
        ]
        
        for segment_id in segments:
            # Random traffic conditions
            congestion_factor = random.random()
            
            if congestion_factor < 0.2:
                level = CongestionLevel.FREE_FLOW
                speed_ratio = 0.95
            elif congestion_factor < 0.4:
                level = CongestionLevel.LIGHT
                speed_ratio = 0.80
            elif congestion_factor < 0.6:
                level = CongestionLevel.MODERATE
                speed_ratio = 0.60
            elif congestion_factor < 0.8:
                level = CongestionLevel.HEAVY
                speed_ratio = 0.35
            else:
                level = CongestionLevel.SEVERE
                speed_ratio = 0.15
            
            free_flow_speed = 50  # km/h
            current_speed = free_flow_speed * speed_ratio
            
            traffic_data = RoadSegmentTraffic(
                segment_id=segment_id,
                congestion_level=level,
                congestion_factor=congestion_factor,
                current_speed_kmh=current_speed,
                free_flow_speed_kmh=free_flow_speed,
                last_updated=datetime.now()
            )
            
            self.traffic_data[segment_id] = traffic_data
    
    def _process_google_traffic_data(self, data: dict):
        """Process traffic data from Google API response."""
        # Implement based on Google's response format
        pass
    
    def get_segment_traffic(self, segment_id: str) -> Optional[RoadSegmentTraffic]:
        """Get traffic data for a specific road segment."""
        return self.traffic_data.get(segment_id)
    
    def get_all_traffic(self) -> List[RoadSegmentTraffic]:
        """Get all traffic data."""
        return list(self.traffic_data.values())
    
    def get_congested_segments(
        self,
        min_congestion: float = 0.6
    ) -> List[RoadSegmentTraffic]:
        """Get segments with congestion above threshold."""
        return [
            traffic for traffic in self.traffic_data.values()
            if traffic.congestion_factor >= min_congestion
        ]
    
    def calculate_route_congestion(self, segment_ids: List[str]) -> float:
        """
        Calculate average congestion along a route.
        
        Returns: 0.0 (clear) to 1.0 (gridlock)
        """
        if not segment_ids:
            return 0.0
        
        total_congestion = 0
        count = 0
        
        for segment_id in segment_ids:
            traffic = self.get_segment_traffic(segment_id)
            if traffic:
                total_congestion += traffic.congestion_factor
                count += 1
        
        if count == 0:
            return 0.0
        
        return total_congestion / count
    
    def calculate_route_travel_time(
        self,
        segment_ids: List[str],
        base_time_minutes: float
    ) -> float:
        """
        Calculate actual travel time considering current traffic.
        
        Args:
            segment_ids: List of road segments in route
            base_time_minutes: Free-flow travel time
        
        Returns: Adjusted travel time in minutes
        """
        if not segment_ids:
            return base_time_minutes
        
        # Calculate average multiplier
        multipliers = []
        for segment_id in segment_ids:
            traffic = self.get_segment_traffic(segment_id)
            if traffic:
                multipliers.append(traffic.get_travel_time_multiplier())
        
        if not multipliers:
            return base_time_minutes
        
        avg_multiplier = sum(multipliers) / len(multipliers)
        return base_time_minutes * avg_multiplier
    
    def report_incident(
        self,
        incident_id: str,
        lat: float,
        lon: float,
        incident_type: str,
        severity: str,
        description: str
    ):
        """Report a traffic incident."""
        self.active_incidents[incident_id] = {
            'incident_id': incident_id,
            'lat': lat,
            'lon': lon,
            'type': incident_type,
            'severity': severity,
            'description': description,
            'reported_at': datetime.now().isoformat(),
            'active': True
        }
        
        print(f"🚨 Incident reported: {incident_type} at ({lat:.4f}, {lon:.4f})")
    
    def clear_incident(self, incident_id: str):
        """Mark incident as cleared."""
        if incident_id in self.active_incidents:
            self.active_incidents[incident_id]['active'] = False
            self.active_incidents[incident_id]['cleared_at'] = datetime.now().isoformat()
            print(f"✓ Incident cleared: {incident_id}")
    
    def get_incidents_in_area(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float
    ) -> List[dict]:
        """Get active incidents within radius of a point."""
        import math
        
        incidents = []
        for incident in self.active_incidents.values():
            if not incident.get('active', False):
                continue
            
            # Simple distance calculation
            dlat = incident['lat'] - center_lat
            dlon = incident['lon'] - center_lon
            distance = math.sqrt(dlat**2 + dlon**2) * 111  # Rough km
            
            if distance <= radius_km:
                incidents.append(incident)
        
        return incidents
    
    def should_reroute(
        self,
        route_segments: List[str],
        congestion_threshold: float = 0.7
    ) -> bool:
        """
        Determine if a route should be recalculated due to traffic.
        
        Returns: True if rerouting recommended
        """
        avg_congestion = self.calculate_route_congestion(route_segments)
        return avg_congestion >= congestion_threshold
    
    def get_traffic_summary(self) -> Dict:
        """Get summary of current traffic conditions."""
        if not self.traffic_data:
            return {
                'total_segments': 0,
                'average_congestion': 0.0,
                'congestion_distribution': {},
                'active_incidents': 0
            }
        
        # Count by congestion level
        distribution = {
            'free_flow': 0,
            'light': 0,
            'moderate': 0,
            'heavy': 0,
            'severe': 0
        }
        
        total_congestion = 0
        for traffic in self.traffic_data.values():
            distribution[traffic.congestion_level.value] += 1
            total_congestion += traffic.congestion_factor
        
        return {
            'total_segments': len(self.traffic_data),
            'average_congestion': total_congestion / len(self.traffic_data),
            'congestion_distribution': distribution,
            'active_incidents': len([
                i for i in self.active_incidents.values()
                if i.get('active', False)
            ]),
            'last_update': self.last_update.isoformat() if self.last_update else None
        }


# Global instance
traffic_monitor = TrafficMonitor()


# Example usage
if __name__ == "__main__":
    async def test_monitor():
        monitor = TrafficMonitor()
        
        # Simulate one update
        await monitor.fetch_traffic_data()
        
        print("\n📊 Traffic Summary:")
        summary = monitor.get_traffic_summary()
        print(f"  Total segments: {summary['total_segments']}")
        print(f"  Avg congestion: {summary['average_congestion']:.1%}")
        print(f"  Distribution: {summary['congestion_distribution']}")
        
        print("\n🚨 Congested Segments:")
        congested = monitor.get_congested_segments(min_congestion=0.7)
        for traffic in congested[:5]:  # Show first 5
            print(f"  {traffic.segment_id}: {traffic.congestion_level.value} "
                  f"({traffic.current_speed_kmh:.0f} km/h)")
        
        # Test route congestion
        test_route = [f"segment_{i:03d}" for i in range(1, 11)]
        route_congestion = monitor.calculate_route_congestion(test_route)
        print(f"\n🛣️  Test route congestion: {route_congestion:.0%}")
        
        base_time = 15  # minutes
        actual_time = monitor.calculate_route_travel_time(test_route, base_time)
        print(f"  Base time: {base_time:.1f} min")
        print(f"  Actual time: {actual_time:.1f} min")
        print(f"  Delay: {actual_time - base_time:.1f} min")
    
    # Run test
    asyncio.run(test_monitor())

