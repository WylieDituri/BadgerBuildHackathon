#!/usr/bin/env python3
"""
Test script for the intelligence layer.
Demonstrates collision prediction, intersection coordination, and traffic monitoring.
"""

import asyncio
import time
from app.models.car import Car, Position, VehicleType
from app.intelligence.car_tracker import CarTracker
from app.intelligence.collision_predictor import CollisionPredictor
from app.intelligence.intersection_manager import IntersectionManager
from app.intelligence.traffic_monitor import TrafficMonitor


async def demo_collision_prediction():
    """Demo: Collision prediction between two cars."""
    print("\n" + "="*60)
    print("🔮 DEMO 1: Collision Prediction")
    print("="*60)
    
    tracker = CarTracker()
    predictor = CollisionPredictor(tracker)
    
    # Create two cars on collision course
    print("\n📍 Setting up scenario: Two cars approaching intersection...")
    
    car1 = Car(
        car_id="car_001",
        vehicle_type=VehicleType.SEDAN,
        current_position=Position(
            lat=43.0750,
            lon=-89.3900,
            heading=90,  # Going East
            speed_mps=13.4  # ~30 mph
        )
    )
    
    car2 = Car(
        car_id="car_002",
        vehicle_type=VehicleType.SUV,
        current_position=Position(
            lat=43.0750,
            lon=-89.3880,  # 150m East
            heading=270,  # Going West (head-on!)
            speed_mps=15.6  # ~35 mph
        )
    )
    
    tracker.register_car(car1)
    tracker.register_car(car2)
    
    print(f"  Car 1: {car1.car_id} at ({car1.current_position.lat:.4f}, {car1.current_position.lon:.4f})")
    print(f"         Heading {car1.current_position.heading}° @ {car1.current_position.speed_mps:.1f} m/s")
    print(f"  Car 2: {car2.car_id} at ({car2.current_position.lat:.4f}, {car2.current_position.lon:.4f})")
    print(f"         Heading {car2.current_position.heading}° @ {car2.current_position.speed_mps:.1f} m/s")
    
    # Predict collision
    print("\n🔍 Running collision prediction...")
    predictions = predictor.predict_all_collisions()
    
    if predictions:
        pred = predictions[0]
        print(f"\n⚠️  COLLISION PREDICTED!")
        print(f"  Cars: {pred.car1_id} ↔ {pred.car2_id}")
        print(f"  Time to collision: {pred.time_to_collision_seconds:.1f} seconds")
        print(f"  Collision point: ({pred.collision_point[0]:.4f}, {pred.collision_point[1]:.4f})")
        print(f"  Closest distance: {pred.closest_distance_meters:.1f} meters")
        print(f"  Severity: {pred.severity.upper()}")
        print(f"  Confidence: {pred.confidence:.0%}")
        print(f"  Recommended action: {pred.recommended_action}")
    else:
        print("✓ No collision predicted")


async def demo_intersection_coordination():
    """Demo: Intersection coordination with multiple cars."""
    print("\n" + "="*60)
    print("🚦 DEMO 2: Intersection Coordination")
    print("="*60)
    
    tracker = CarTracker()
    manager = IntersectionManager(tracker)
    
    # Create multiple cars
    print("\n📍 Setting up scenario: 4 cars approaching same intersection...")
    
    cars = [
        Car(car_id="sedan_001", vehicle_type=VehicleType.SEDAN),
        Car(car_id="suv_001", vehicle_type=VehicleType.SUV),
        Car(car_id="truck_001", vehicle_type=VehicleType.TRUCK),
        Car(car_id="ambulance_001", vehicle_type=VehicleType.EMERGENCY, is_emergency=True),
    ]
    
    for car in cars:
        tracker.register_car(car)
    
    # Cars request crossing with different ETAs
    requests = [
        ("sedan_001", 5.0),
        ("suv_001", 6.0),
        ("truck_001", 7.0),
        ("ambulance_001", 8.0),  # Emergency arrives last but should get priority!
    ]
    
    print("\n🚗 Cars requesting intersection crossing:")
    
    for car_id, eta in requests:
        car = tracker.get_car(car_id)
        decision = manager.request_crossing(car_id, "intersection_main", eta)
        
        status_icon = "✓" if decision.approved else "✗"
        emergency_tag = " 🚨" if car.is_emergency else ""
        
        print(f"\n  {status_icon} {car_id}{emergency_tag}")
        print(f"    ETA: {eta:.1f}s")
        print(f"    Decision: {decision.speed_recommendation.upper()}")
        print(f"    Wait time: {decision.wait_time_seconds:.1f}s")
        print(f"    Reason: {decision.reason}")
        print(f"    Priority: {decision.priority}")
    
    # Show intersection status
    print("\n📊 Intersection Status:")
    status = manager.get_intersection_status("intersection_main")
    print(f"  Active cars: {len(status['active_cars'])}")
    print(f"  Waiting cars: {len(status['waiting_cars'])}")
    print(f"  Congestion level: {status['congestion_level']:.0%}")
    print(f"  Upcoming reservations: {len(status['upcoming_reservations'])}")
    
    # Performance metrics
    print("\n📈 System Metrics:")
    metrics = manager.get_performance_metrics()
    print(f"  Total requests: {metrics['total_requests']}")
    print(f"  Approval rate: {metrics['approval_rate']:.0%}")
    print(f"  Avg wait time: {metrics['average_wait_time_seconds']:.1f}s")


async def demo_traffic_monitoring():
    """Demo: Traffic monitoring and congestion detection."""
    print("\n" + "="*60)
    print("🚥 DEMO 3: Traffic Monitoring")
    print("="*60)
    
    monitor = TrafficMonitor()
    
    print("\n📡 Fetching traffic data (simulated)...")
    await monitor.fetch_traffic_data()
    
    # Traffic summary
    summary = monitor.get_traffic_summary()
    print(f"\n📊 Traffic Summary:")
    print(f"  Monitored segments: {summary['total_segments']}")
    print(f"  Average congestion: {summary['average_congestion']:.0%}")
    print(f"  Active incidents: {summary['active_incidents']}")
    
    dist = summary['congestion_distribution']
    print(f"\n  Distribution:")
    print(f"    🟢 Free flow: {dist['free_flow']} segments")
    print(f"    🟡 Light: {dist['light']} segments")
    print(f"    🟠 Moderate: {dist['moderate']} segments")
    print(f"    🔴 Heavy: {dist['heavy']} segments")
    print(f"    🔴 Severe: {dist['severe']} segments")
    
    # Show most congested
    print("\n🚨 Most Congested Segments:")
    congested = monitor.get_congested_segments(min_congestion=0.7)
    for traffic in congested[:5]:
        print(f"  {traffic.segment_id}: {traffic.congestion_level.value}")
        print(f"    Current speed: {traffic.current_speed_kmh:.0f} km/h")
        print(f"    Congestion: {traffic.congestion_factor:.0%}")
    
    # Test route analysis
    print("\n🛣️  Route Analysis:")
    test_route = [f"segment_{i:03d}" for i in range(1, 11)]
    route_congestion = monitor.calculate_route_congestion(test_route)
    base_time = 15  # minutes
    actual_time = monitor.calculate_route_travel_time(test_route, base_time)
    
    print(f"  Route: {test_route[0]} → {test_route[-1]}")
    print(f"  Segments: {len(test_route)}")
    print(f"  Congestion: {route_congestion:.0%}")
    print(f"  Base travel time: {base_time:.1f} min")
    print(f"  Actual travel time: {actual_time:.1f} min")
    print(f"  Delay: {actual_time - base_time:.1f} min ({(actual_time/base_time - 1):.0%} slower)")
    
    if monitor.should_reroute(test_route):
        print(f"  ⚠️  Rerouting recommended!")
    else:
        print(f"  ✓ Route is acceptable")


async def demo_integrated_scenario():
    """Demo: Complete integrated scenario with all systems."""
    print("\n" + "="*60)
    print("🌟 DEMO 4: Integrated Intelligence System")
    print("="*60)
    
    tracker = CarTracker()
    predictor = CollisionPredictor(tracker)
    intersection_mgr = IntersectionManager(tracker)
    traffic_mon = TrafficMonitor()
    
    # Initialize traffic
    await traffic_mon.fetch_traffic_data()
    
    print("\n📍 Scenario: Rush hour with multiple cars...")
    
    # Create 5 cars in various locations
    cars_data = [
        ("car_a", 43.0750, -89.3900, 90, 12.0, False),
        ("car_b", 43.0750, -89.3880, 270, 14.0, False),
        ("car_c", 43.0760, -89.3890, 180, 10.0, False),
        ("car_d", 43.0740, -89.3890, 0, 13.0, False),
        ("ambulance", 43.0755, -89.3895, 45, 18.0, True),
    ]
    
    for car_id, lat, lon, heading, speed, is_emergency in cars_data:
        vehicle_type = VehicleType.EMERGENCY if is_emergency else VehicleType.SEDAN
        car = Car(
            car_id=car_id,
            vehicle_type=vehicle_type,
            is_emergency=is_emergency,
            current_position=Position(lat=lat, lon=lon, heading=heading, speed_mps=speed)
        )
        tracker.register_car(car)
    
    print(f"  Registered {len(cars_data)} cars")
    
    # Check collisions
    print("\n🔍 Checking for collision risks...")
    predictions = predictor.predict_all_collisions()
    
    if predictions:
        print(f"  ⚠️  {len(predictions)} collision risk(s) detected!")
        for pred in predictions:
            print(f"    • {pred.car1_id} ↔ {pred.car2_id}: {pred.time_to_collision_seconds:.1f}s ({pred.severity})")
    else:
        print(f"  ✓ No immediate collision risks")
    
    # Intersection requests
    print("\n🚦 Processing intersection requests...")
    for car_id, _, _, _, _, _ in cars_data:
        eta = 5.0 + (hash(car_id) % 5)  # Random but consistent ETA
        decision = intersection_mgr.request_crossing(car_id, "main_intersection", eta)
        
        icon = "🚨" if tracker.get_car(car_id).is_emergency else "🚗"
        print(f"  {icon} {car_id}: {decision.speed_recommendation}")
    
    # System status
    print("\n📊 System Status:")
    active_cars = tracker.get_active_cars()
    print(f"  Active cars: {len(active_cars)}")
    print(f"  Emergency vehicles: {len([c for c in active_cars if c.is_emergency])}")
    print(f"  Collision predictions: {len(predictions)}")
    print(f"  Traffic segments monitored: {len(traffic_mon.traffic_data)}")
    print(f"  Average congestion: {traffic_mon.get_traffic_summary()['average_congestion']:.0%}")


async def main():
    """Run all demos."""
    print("\n" + "🚗"*30)
    print("   TRAFFIC INTELLIGENCE SYSTEM DEMO")
    print("🚗"*30)
    
    await demo_collision_prediction()
    await asyncio.sleep(1)
    
    await demo_intersection_coordination()
    await asyncio.sleep(1)
    
    await demo_traffic_monitoring()
    await asyncio.sleep(1)
    
    await demo_integrated_scenario()
    
    print("\n" + "="*60)
    print("✅ All demos completed!")
    print("="*60)
    print("\n💡 Next steps:")
    print("  1. Start the API: uvicorn app.main:app --reload")
    print("  2. Test endpoints: curl http://localhost:8000/api/v2/intelligence/analytics/system-status")
    print("  3. View docs: http://localhost:8000/docs")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())

