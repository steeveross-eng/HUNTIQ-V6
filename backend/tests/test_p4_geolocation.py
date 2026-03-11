"""
Phase P4 - Geolocation Engine API Tests
Tests for background geolocation tracking and proximity alerts
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestGeolocationInfo:
    """Test geolocation info endpoint"""
    
    def test_geolocation_info_endpoint(self):
        """GET /api/v1/geolocation/ - Get module info"""
        response = requests.get(f"{BASE_URL}/api/v1/geolocation/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["module"] == "geolocation_engine"
        assert data["version"] == "1.0.0"
        assert data["phase"] == "P4"
        assert "features" in data
        assert "endpoints" in data
        assert len(data["features"]) >= 5
        print(f"✓ Geolocation info: {data['module']} v{data['version']}")


class TestTrackingStatus:
    """Test tracking status endpoint"""
    
    def test_tracking_status_endpoint(self):
        """GET /api/v1/geolocation/tracking-status - Get tracking status"""
        response = requests.get(f"{BASE_URL}/api/v1/geolocation/tracking-status")
        assert response.status_code == 200
        
        data = response.json()
        assert "tracking_active" in data
        assert "push_enabled" in data
        assert "total_locations" in data
        assert "features" in data
        
        # Verify features structure
        features = data["features"]
        assert features["background_tracking"] == True
        assert features["proximity_alerts"] == True
        assert features["session_tracking"] == True
        print(f"✓ Tracking status: active={data['tracking_active']}, locations={data['total_locations']}")


class TestTrackingSession:
    """Test tracking session endpoints"""
    
    def test_start_tracking_session(self):
        """POST /api/v1/geolocation/session/start - Start tracking session"""
        response = requests.post(f"{BASE_URL}/api/v1/geolocation/session/start")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "session" in data
        assert "id" in data["session"]
        assert data["session"]["active"] == True
        assert "started_at" in data["session"]
        assert data["message"] == "Session de tracking démarrée"
        
        # Store session ID for later tests
        self.__class__.session_id = data["session"]["id"]
        print(f"✓ Session started: {data['session']['id']}")
        return data["session"]["id"]
    
    def test_end_tracking_session(self):
        """POST /api/v1/geolocation/session/{id}/end - End tracking session"""
        # First start a session
        start_response = requests.post(f"{BASE_URL}/api/v1/geolocation/session/start")
        session_id = start_response.json()["session"]["id"]
        
        # End the session
        response = requests.post(f"{BASE_URL}/api/v1/geolocation/session/{session_id}/end")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "session" in data
        assert data["session"]["active"] == False
        assert "ended_at" in data["session"]
        assert "distance_km" in data["session"]
        assert "locations_count" in data["session"]
        print(f"✓ Session ended: {session_id}, distance={data['session']['distance_km']}km")
    
    def test_end_nonexistent_session(self):
        """POST /api/v1/geolocation/session/{id}/end - End non-existent session returns 404"""
        response = requests.post(f"{BASE_URL}/api/v1/geolocation/session/000000000000000000000000/end")
        assert response.status_code == 404
        print("✓ Non-existent session returns 404")


class TestLocationRecording:
    """Test location recording endpoints"""
    
    def test_record_location(self):
        """POST /api/v1/geolocation/location - Record location update"""
        location_data = {
            "latitude": 46.8139,
            "longitude": -71.2080,
            "accuracy": 10.0,
            "altitude": 100.0,
            "speed": 1.5,
            "heading": 45.0
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/geolocation/location",
            json=location_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "location" in data
        assert data["location"]["latitude"] == 46.8139
        assert data["location"]["longitude"] == -71.2080
        assert "id" in data["location"]
        assert "timestamp" in data["location"]
        assert "alerts" in data
        assert "alerts_count" in data
        print(f"✓ Location recorded: {data['location']['id']}")
    
    def test_record_location_minimal(self):
        """POST /api/v1/geolocation/location - Record with minimal data"""
        location_data = {
            "latitude": 46.8200,
            "longitude": -71.2100
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/geolocation/location",
            json=location_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        print("✓ Minimal location recorded")
    
    def test_record_location_invalid_coordinates(self):
        """POST /api/v1/geolocation/location - Invalid coordinates rejected"""
        location_data = {
            "latitude": 200.0,  # Invalid - must be -90 to 90
            "longitude": -71.2080
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/geolocation/location",
            json=location_data
        )
        assert response.status_code == 422  # Validation error
        print("✓ Invalid coordinates rejected with 422")


class TestLocationHistory:
    """Test location history endpoint"""
    
    def test_get_location_history(self):
        """GET /api/v1/geolocation/history - Get location history"""
        response = requests.get(f"{BASE_URL}/api/v1/geolocation/history?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            location = data[0]
            assert "id" in location
            assert "latitude" in location
            assert "longitude" in location
            assert "timestamp" in location
            print(f"✓ Location history: {len(data)} records")
        else:
            print("✓ Location history: empty (no records yet)")
    
    def test_get_location_history_with_limit(self):
        """GET /api/v1/geolocation/history - Test limit parameter"""
        response = requests.get(f"{BASE_URL}/api/v1/geolocation/history?limit=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 2
        print(f"✓ Location history with limit: {len(data)} records")


class TestProximityAlerts:
    """Test proximity alert endpoints"""
    
    def test_check_proximity(self):
        """POST /api/v1/geolocation/check-proximity - Check proximity to waypoints"""
        response = requests.post(
            f"{BASE_URL}/api/v1/geolocation/check-proximity?lat=46.8139&lng=-71.2080"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "position" in data
        assert data["position"]["lat"] == 46.8139
        assert data["position"]["lng"] == -71.2080
        assert "alerts" in data
        assert "alerts_count" in data
        assert "has_alerts" in data
        print(f"✓ Proximity check: {data['alerts_count']} alerts")
    
    def test_check_proximity_far_location(self):
        """POST /api/v1/geolocation/check-proximity - Far location returns no alerts"""
        # Use a location far from any waypoints
        response = requests.post(
            f"{BASE_URL}/api/v1/geolocation/check-proximity?lat=0.0&lng=0.0"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["alerts_count"] == 0
        assert data["has_alerts"] == False
        print("✓ Far location returns no alerts")


class TestNearbyHotspots:
    """Test nearby hotspots endpoint"""
    
    def test_get_nearby_hotspots(self):
        """GET /api/v1/geolocation/nearby-hotspots - Get nearby waypoints"""
        response = requests.get(
            f"{BASE_URL}/api/v1/geolocation/nearby-hotspots?lat=46.8139&lng=-71.2080&radius_km=10"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "center" in data
        assert data["center"]["lat"] == 46.8139
        assert data["center"]["lng"] == -71.2080
        assert "radius_km" in data
        assert data["radius_km"] == 10.0
        assert "hotspots" in data
        assert "count" in data
        
        if data["count"] > 0:
            hotspot = data["hotspots"][0]
            assert "waypoint_id" in hotspot
            assert "name" in hotspot
            assert "lat" in hotspot
            assert "lng" in hotspot
            assert "distance_m" in hotspot
            assert "wqs" in hotspot
            assert "classification" in hotspot
            print(f"✓ Nearby hotspots: {data['count']} found")
        else:
            print("✓ Nearby hotspots: none in range")
    
    def test_get_nearby_hotspots_small_radius(self):
        """GET /api/v1/geolocation/nearby-hotspots - Small radius test"""
        response = requests.get(
            f"{BASE_URL}/api/v1/geolocation/nearby-hotspots?lat=46.8139&lng=-71.2080&radius_km=0.001"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["radius_km"] == 0.001
        print(f"✓ Small radius test: {data['count']} hotspots")


class TestPushSubscription:
    """Test push notification subscription endpoints"""
    
    def test_subscribe_push(self):
        """POST /api/v1/geolocation/subscribe - Subscribe to push notifications"""
        subscription_data = {
            "endpoint": "https://fcm.googleapis.com/fcm/send/test-endpoint",
            "keys": {
                "p256dh": "test-p256dh-key",
                "auth": "test-auth-key"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/geolocation/subscribe",
            json=subscription_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "message" in data
        print("✓ Push subscription created")
    
    def test_unsubscribe_push(self):
        """DELETE /api/v1/geolocation/subscribe - Unsubscribe from push"""
        response = requests.delete(f"{BASE_URL}/api/v1/geolocation/subscribe")
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "message" in data
        print("✓ Push unsubscribe completed")


class TestPushNotification:
    """Test push notification sending endpoint"""
    
    def test_send_notification(self):
        """POST /api/v1/geolocation/notify - Send push notification"""
        # First subscribe
        subscription_data = {
            "endpoint": "https://fcm.googleapis.com/fcm/send/test-endpoint",
            "keys": {
                "p256dh": "test-p256dh-key",
                "auth": "test-auth-key"
            }
        }
        requests.post(f"{BASE_URL}/api/v1/geolocation/subscribe", json=subscription_data)
        
        # Send notification
        notification_data = {
            "title": "Test Notification",
            "body": "This is a test notification from BIONIC HUNT/Chasse",
            "url": "/map"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/geolocation/notify",
            json=notification_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "message" in data
        print(f"✓ Notification sent: success={data['success']}")


class TestIntegrationFlow:
    """Test complete tracking flow"""
    
    def test_complete_tracking_flow(self):
        """Test complete tracking session flow"""
        # 1. Start session
        start_response = requests.post(f"{BASE_URL}/api/v1/geolocation/session/start")
        assert start_response.status_code == 200
        session_id = start_response.json()["session"]["id"]
        print(f"  1. Session started: {session_id}")
        
        # 2. Record multiple locations
        locations = [
            {"latitude": 46.8139, "longitude": -71.2080, "accuracy": 10},
            {"latitude": 46.8145, "longitude": -71.2085, "accuracy": 15},
            {"latitude": 46.8150, "longitude": -71.2090, "accuracy": 12}
        ]
        
        for i, loc in enumerate(locations):
            response = requests.post(
                f"{BASE_URL}/api/v1/geolocation/location?session_id={session_id}",
                json=loc
            )
            assert response.status_code == 200
            print(f"  2.{i+1}. Location recorded")
        
        # 3. Check nearby hotspots
        hotspots_response = requests.get(
            f"{BASE_URL}/api/v1/geolocation/nearby-hotspots?lat=46.8139&lng=-71.2080&radius_km=5"
        )
        assert hotspots_response.status_code == 200
        print(f"  3. Nearby hotspots: {hotspots_response.json()['count']}")
        
        # 4. Check proximity
        proximity_response = requests.post(
            f"{BASE_URL}/api/v1/geolocation/check-proximity?lat=46.8139&lng=-71.2080"
        )
        assert proximity_response.status_code == 200
        print(f"  4. Proximity alerts: {proximity_response.json()['alerts_count']}")
        
        # 5. Get history
        history_response = requests.get(f"{BASE_URL}/api/v1/geolocation/history?limit=10")
        assert history_response.status_code == 200
        print(f"  5. History records: {len(history_response.json())}")
        
        # 6. End session
        end_response = requests.post(f"{BASE_URL}/api/v1/geolocation/session/{session_id}/end")
        assert end_response.status_code == 200
        session_data = end_response.json()["session"]
        print(f"  6. Session ended: distance={session_data['distance_km']}km, locations={session_data['locations_count']}")
        
        print("✓ Complete tracking flow successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
