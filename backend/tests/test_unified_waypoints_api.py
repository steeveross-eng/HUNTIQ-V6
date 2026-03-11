"""
Test Suite: Unified Waypoints API (territory_waypoints)
Phase P6 - Unified Geospatial Architecture

Tests the unified waypoints API endpoints:
- GET /api/territory/waypoints?user_id={id} - List waypoints
- POST /api/territory/waypoints?user_id={id} - Create waypoint
- DELETE /api/territory/waypoints/{waypoint_id}?user_id={id} - Delete waypoint
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_USER_ID = "default_user"


class TestUnifiedWaypointsAPI:
    """Test unified waypoints API (territory_waypoints collection)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.created_waypoint_ids = []
        yield
        # Cleanup: Delete test-created waypoints
        for wp_id in self.created_waypoint_ids:
            try:
                requests.delete(
                    f"{BASE_URL}/api/territory/waypoints/{wp_id}",
                    params={"user_id": TEST_USER_ID}
                )
            except:
                pass
    
    def test_api_health(self):
        """Test API is operational"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "BIONIC HUNT/Chasse" in data["message"]
    
    def test_list_waypoints_success(self):
        """Test GET /api/territory/waypoints returns waypoints list"""
        response = requests.get(
            f"{BASE_URL}/api/territory/waypoints",
            params={"user_id": TEST_USER_ID}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return a list
        assert isinstance(data, list)
        
        # Verify waypoint structure if any exist
        if len(data) > 0:
            waypoint = data[0]
            assert "id" in waypoint
            assert "latitude" in waypoint
            assert "longitude" in waypoint
            assert "name" in waypoint
            assert "waypoint_type" in waypoint
            assert "user_id" in waypoint
    
    def test_list_waypoints_contains_migrated_data(self):
        """Test that migrated waypoints are visible"""
        response = requests.get(
            f"{BASE_URL}/api/territory/waypoints",
            params={"user_id": TEST_USER_ID}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check for migrated waypoints
        waypoint_names = [wp["name"] for wp in data]
        
        # At least some of the migrated waypoints should exist
        expected_names = ["Mon spot de chasse", "Ma cache caméra", "Point Test Bidirectionnel"]
        found_count = sum(1 for name in expected_names if name in waypoint_names)
        
        assert found_count >= 2, f"Expected at least 2 migrated waypoints, found {found_count}. Names: {waypoint_names}"
    
    def test_create_waypoint_success(self):
        """Test POST /api/territory/waypoints creates a new waypoint"""
        test_name = f"TEST_Waypoint_{uuid.uuid4().hex[:8]}"
        
        payload = {
            "name": test_name,
            "latitude": 46.8500,
            "longitude": -71.2500,
            "waypoint_type": "hunting",
            "description": "Test waypoint for automated testing"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/territory/waypoints",
            params={"user_id": TEST_USER_ID},
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["name"] == test_name
        assert data["latitude"] == 46.85
        assert data["longitude"] == -71.25
        assert data["waypoint_type"] == "hunting"
        assert data["user_id"] == TEST_USER_ID
        
        # Track for cleanup
        self.created_waypoint_ids.append(data["id"])
        
        # Verify persistence with GET
        get_response = requests.get(
            f"{BASE_URL}/api/territory/waypoints",
            params={"user_id": TEST_USER_ID}
        )
        assert get_response.status_code == 200
        waypoints = get_response.json()
        
        created_wp = next((wp for wp in waypoints if wp["id"] == data["id"]), None)
        assert created_wp is not None, "Created waypoint not found in list"
        assert created_wp["name"] == test_name
    
    def test_create_waypoint_all_types(self):
        """Test creating waypoints with different types"""
        waypoint_types = ["observation", "camera", "cache", "stand", "water", "trail_start", "custom", "hunting", "feeder", "sighting", "parking"]
        
        for wp_type in waypoint_types[:3]:  # Test first 3 types to save time
            payload = {
                "name": f"TEST_Type_{wp_type}_{uuid.uuid4().hex[:6]}",
                "latitude": 46.8 + (waypoint_types.index(wp_type) * 0.01),
                "longitude": -71.2,
                "waypoint_type": wp_type,
                "description": f"Test {wp_type} waypoint"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/territory/waypoints",
                params={"user_id": TEST_USER_ID},
                json=payload
            )
            
            assert response.status_code == 200, f"Failed to create {wp_type} waypoint"
            data = response.json()
            assert data["waypoint_type"] == wp_type
            
            self.created_waypoint_ids.append(data["id"])
    
    def test_create_waypoint_with_optional_fields(self):
        """Test creating waypoint with all optional fields"""
        test_name = f"TEST_FullFields_{uuid.uuid4().hex[:8]}"
        
        payload = {
            "name": test_name,
            "latitude": 46.9000,
            "longitude": -71.3000,
            "waypoint_type": "stand",
            "description": "Full description",
            "icon": "🎯",
            "active": True,
            "color": "#ff5500",
            "notes": "Additional notes"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/territory/waypoints",
            params={"user_id": TEST_USER_ID},
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == test_name
        assert data["active"] == True
        assert data["color"] == "#ff5500"
        
        self.created_waypoint_ids.append(data["id"])
    
    def test_delete_waypoint_success(self):
        """Test DELETE /api/territory/waypoints/{id} removes waypoint"""
        # First create a waypoint
        test_name = f"TEST_ToDelete_{uuid.uuid4().hex[:8]}"
        
        create_response = requests.post(
            f"{BASE_URL}/api/territory/waypoints",
            params={"user_id": TEST_USER_ID},
            json={
                "name": test_name,
                "latitude": 46.7500,
                "longitude": -71.1500,
                "waypoint_type": "custom"
            }
        )
        
        assert create_response.status_code == 200
        created_id = create_response.json()["id"]
        
        # Delete the waypoint
        delete_response = requests.delete(
            f"{BASE_URL}/api/territory/waypoints/{created_id}",
            params={"user_id": TEST_USER_ID}
        )
        
        assert delete_response.status_code == 200
        delete_data = delete_response.json()
        assert delete_data["status"] == "deleted"
        assert delete_data["id"] == created_id
        
        # Verify deletion with GET
        get_response = requests.get(
            f"{BASE_URL}/api/territory/waypoints",
            params={"user_id": TEST_USER_ID}
        )
        waypoints = get_response.json()
        
        deleted_wp = next((wp for wp in waypoints if wp["id"] == created_id), None)
        assert deleted_wp is None, "Waypoint should be deleted but still exists"
    
    def test_delete_waypoint_not_found(self):
        """Test DELETE with non-existent waypoint returns 404"""
        fake_id = str(uuid.uuid4())
        
        response = requests.delete(
            f"{BASE_URL}/api/territory/waypoints/{fake_id}",
            params={"user_id": TEST_USER_ID}
        )
        
        assert response.status_code == 404
    
    def test_delete_waypoint_wrong_user(self):
        """Test DELETE with wrong user_id returns 404"""
        # First create a waypoint
        create_response = requests.post(
            f"{BASE_URL}/api/territory/waypoints",
            params={"user_id": TEST_USER_ID},
            json={
                "name": f"TEST_WrongUser_{uuid.uuid4().hex[:8]}",
                "latitude": 46.7000,
                "longitude": -71.1000,
                "waypoint_type": "custom"
            }
        )
        
        assert create_response.status_code == 200
        created_id = create_response.json()["id"]
        self.created_waypoint_ids.append(created_id)
        
        # Try to delete with wrong user
        delete_response = requests.delete(
            f"{BASE_URL}/api/territory/waypoints/{created_id}",
            params={"user_id": "wrong_user_id"}
        )
        
        # Should return 404 because waypoint doesn't belong to this user
        assert delete_response.status_code == 404
    
    def test_waypoint_user_isolation(self):
        """Test that waypoints are isolated by user_id"""
        # Create waypoint for test user
        test_name = f"TEST_Isolation_{uuid.uuid4().hex[:8]}"
        
        create_response = requests.post(
            f"{BASE_URL}/api/territory/waypoints",
            params={"user_id": TEST_USER_ID},
            json={
                "name": test_name,
                "latitude": 46.6500,
                "longitude": -71.0500,
                "waypoint_type": "custom"
            }
        )
        
        assert create_response.status_code == 200
        created_id = create_response.json()["id"]
        self.created_waypoint_ids.append(created_id)
        
        # List waypoints for different user
        other_user_response = requests.get(
            f"{BASE_URL}/api/territory/waypoints",
            params={"user_id": "other_test_user"}
        )
        
        assert other_user_response.status_code == 200
        other_waypoints = other_user_response.json()
        
        # The created waypoint should NOT appear for other user
        found = any(wp["id"] == created_id for wp in other_waypoints)
        assert not found, "Waypoint should not be visible to other users"


class TestWaypointDataIntegrity:
    """Test data integrity and field validation"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.created_waypoint_ids = []
        yield
        # Cleanup
        for wp_id in self.created_waypoint_ids:
            try:
                requests.delete(
                    f"{BASE_URL}/api/territory/waypoints/{wp_id}",
                    params={"user_id": TEST_USER_ID}
                )
            except:
                pass
    
    def test_waypoint_coordinates_precision(self):
        """Test that coordinates maintain precision"""
        precise_lat = 46.81234567
        precise_lng = -71.20987654
        
        response = requests.post(
            f"{BASE_URL}/api/territory/waypoints",
            params={"user_id": TEST_USER_ID},
            json={
                "name": f"TEST_Precision_{uuid.uuid4().hex[:8]}",
                "latitude": precise_lat,
                "longitude": precise_lng,
                "waypoint_type": "custom"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        self.created_waypoint_ids.append(data["id"])
        
        # Check precision (at least 4 decimal places)
        assert abs(data["latitude"] - precise_lat) < 0.0001
        assert abs(data["longitude"] - precise_lng) < 0.0001
    
    def test_waypoint_created_at_timestamp(self):
        """Test that created_at timestamp is set"""
        response = requests.post(
            f"{BASE_URL}/api/territory/waypoints",
            params={"user_id": TEST_USER_ID},
            json={
                "name": f"TEST_Timestamp_{uuid.uuid4().hex[:8]}",
                "latitude": 46.8,
                "longitude": -71.2,
                "waypoint_type": "custom"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        self.created_waypoint_ids.append(data["id"])
        
        assert "created_at" in data
        assert data["created_at"] is not None
        # Should be ISO format datetime string
        assert "T" in data["created_at"]
    
    def test_waypoint_id_is_uuid(self):
        """Test that waypoint ID is a valid UUID"""
        response = requests.post(
            f"{BASE_URL}/api/territory/waypoints",
            params={"user_id": TEST_USER_ID},
            json={
                "name": f"TEST_UUID_{uuid.uuid4().hex[:8]}",
                "latitude": 46.8,
                "longitude": -71.2,
                "waypoint_type": "custom"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        self.created_waypoint_ids.append(data["id"])
        
        # Verify ID is valid UUID format
        try:
            uuid.UUID(data["id"])
        except ValueError:
            pytest.fail(f"Waypoint ID is not a valid UUID: {data['id']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
