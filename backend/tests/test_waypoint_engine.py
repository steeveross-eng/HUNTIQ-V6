"""
Waypoint Engine V1 - Backend API Tests
=======================================
Tests for the MapInteractionLayer waypoint creation API.
Module: P1 - Module d'Interaction Cartographique Universel
"""
import pytest
import requests
import os
import uuid

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://bionic-toolbar-slim.preview.emergentagent.com')

class TestWaypointEngineAPI:
    """Tests for /api/v1/waypoints endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        self.test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        self.created_waypoint_ids = []
        yield
        # Cleanup: Delete created waypoints
        for wp_id in self.created_waypoint_ids:
            try:
                requests.delete(f"{BASE_URL}/api/v1/waypoints/{wp_id}")
            except:
                pass
    
    def test_module_info(self):
        """Test GET /api/v1/waypoints/ - Module info endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/waypoints/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify module info structure
        assert data["module"] == "waypoint_engine"
        assert data["version"] == "1.0.0"
        assert "features" in data
        assert "stats" in data
        print(f"✓ Module info: {data['module']} v{data['version']}")
    
    def test_create_waypoint_success(self):
        """Test POST /api/v1/waypoints/create - Create waypoint from double-click"""
        payload = {
            "lat": 46.8139,
            "lng": -71.2080,
            "name": "Test Waypoint Double-Click",
            "timestamp": "2026-02-17T20:00:00Z",
            "source": "user_double_click",
            "user_id": self.test_user_id
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/waypoints/create",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data["success"] == True
        assert "waypoint" in data
        
        waypoint = data["waypoint"]
        assert waypoint["lat"] == payload["lat"]
        assert waypoint["lng"] == payload["lng"]
        assert waypoint["name"] == payload["name"]
        assert waypoint["source"] == "user_double_click"
        assert waypoint["user_id"] == self.test_user_id
        assert "id" in waypoint
        
        self.created_waypoint_ids.append(waypoint["id"])
        print(f"✓ Waypoint created: {waypoint['id']}")
    
    def test_create_waypoint_minimal(self):
        """Test POST /api/v1/waypoints/create - Create with minimal data"""
        payload = {
            "lat": 45.5017,
            "lng": -73.5673,
            "name": "Minimal Waypoint"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/waypoints/create",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        
        waypoint = data["waypoint"]
        assert waypoint["lat"] == payload["lat"]
        assert waypoint["lng"] == payload["lng"]
        
        self.created_waypoint_ids.append(waypoint["id"])
        print(f"✓ Minimal waypoint created: {waypoint['id']}")
    
    def test_list_waypoints(self):
        """Test GET /api/v1/waypoints - List waypoints"""
        # First create a waypoint
        create_response = requests.post(
            f"{BASE_URL}/api/v1/waypoints/create",
            json={
                "lat": 46.0,
                "lng": -71.0,
                "name": "List Test Waypoint",
                "user_id": self.test_user_id
            }
        )
        assert create_response.status_code == 200
        created_wp = create_response.json()["waypoint"]
        self.created_waypoint_ids.append(created_wp["id"])
        
        # List waypoints for user
        response = requests.get(
            f"{BASE_URL}/api/v1/waypoints",
            params={"user_id": self.test_user_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "waypoints" in data
        assert "total" in data
        assert data["total"] >= 1
        
        # Verify our waypoint is in the list
        waypoint_ids = [wp["id"] for wp in data["waypoints"]]
        assert created_wp["id"] in waypoint_ids
        print(f"✓ Listed {data['total']} waypoints for user {self.test_user_id}")
    
    def test_list_waypoints_by_source(self):
        """Test GET /api/v1/waypoints - Filter by source"""
        # Create waypoint with specific source
        create_response = requests.post(
            f"{BASE_URL}/api/v1/waypoints/create",
            json={
                "lat": 46.1,
                "lng": -71.1,
                "name": "Source Filter Test",
                "source": "user_double_click",
                "user_id": self.test_user_id
            }
        )
        assert create_response.status_code == 200
        self.created_waypoint_ids.append(create_response.json()["waypoint"]["id"])
        
        # Filter by source
        response = requests.get(
            f"{BASE_URL}/api/v1/waypoints",
            params={"source": "user_double_click"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned waypoints should have the specified source
        for wp in data["waypoints"]:
            assert wp["source"] == "user_double_click"
        print(f"✓ Filtered waypoints by source: {data['total']} results")
    
    def test_get_waypoint_by_id(self):
        """Test GET /api/v1/waypoints/{id} - Get single waypoint"""
        # Create waypoint
        create_response = requests.post(
            f"{BASE_URL}/api/v1/waypoints/create",
            json={
                "lat": 46.2,
                "lng": -71.2,
                "name": "Get By ID Test",
                "user_id": self.test_user_id
            }
        )
        assert create_response.status_code == 200
        created_wp = create_response.json()["waypoint"]
        self.created_waypoint_ids.append(created_wp["id"])
        
        # Get by ID
        response = requests.get(f"{BASE_URL}/api/v1/waypoints/{created_wp['id']}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["waypoint"]["id"] == created_wp["id"]
        assert data["waypoint"]["name"] == "Get By ID Test"
        print(f"✓ Retrieved waypoint by ID: {created_wp['id']}")
    
    def test_get_waypoint_not_found(self):
        """Test GET /api/v1/waypoints/{id} - Non-existent waypoint"""
        fake_id = "non-existent-id-12345"
        response = requests.get(f"{BASE_URL}/api/v1/waypoints/{fake_id}")
        
        assert response.status_code == 404
        print("✓ Correctly returned 404 for non-existent waypoint")
    
    def test_update_waypoint(self):
        """Test PUT /api/v1/waypoints/{id} - Update waypoint"""
        # Create waypoint
        create_response = requests.post(
            f"{BASE_URL}/api/v1/waypoints/create",
            json={
                "lat": 46.3,
                "lng": -71.3,
                "name": "Original Name",
                "user_id": self.test_user_id
            }
        )
        assert create_response.status_code == 200
        created_wp = create_response.json()["waypoint"]
        self.created_waypoint_ids.append(created_wp["id"])
        
        # Update waypoint
        update_response = requests.put(
            f"{BASE_URL}/api/v1/waypoints/{created_wp['id']}",
            json={"name": "Updated Name", "description": "Added description"}
        )
        
        assert update_response.status_code == 200
        data = update_response.json()
        
        assert data["success"] == True
        assert data["waypoint"]["name"] == "Updated Name"
        
        # Verify update persisted
        get_response = requests.get(f"{BASE_URL}/api/v1/waypoints/{created_wp['id']}")
        assert get_response.json()["waypoint"]["name"] == "Updated Name"
        print(f"✓ Updated waypoint: {created_wp['id']}")
    
    def test_delete_waypoint(self):
        """Test DELETE /api/v1/waypoints/{id} - Delete waypoint"""
        # Create waypoint
        create_response = requests.post(
            f"{BASE_URL}/api/v1/waypoints/create",
            json={
                "lat": 46.4,
                "lng": -71.4,
                "name": "To Be Deleted",
                "user_id": self.test_user_id
            }
        )
        assert create_response.status_code == 200
        created_wp = create_response.json()["waypoint"]
        
        # Delete waypoint
        delete_response = requests.delete(f"{BASE_URL}/api/v1/waypoints/{created_wp['id']}")
        
        assert delete_response.status_code == 200
        data = delete_response.json()
        assert data["success"] == True
        assert data["deleted"] == True
        
        # Verify deletion
        get_response = requests.get(f"{BASE_URL}/api/v1/waypoints/{created_wp['id']}")
        assert get_response.status_code == 404
        print(f"✓ Deleted waypoint: {created_wp['id']}")
    
    def test_get_waypoints_in_bounds(self):
        """Test GET /api/v1/waypoints/bounds - Geographic bounds query"""
        # Create waypoint in specific location
        create_response = requests.post(
            f"{BASE_URL}/api/v1/waypoints/create",
            json={
                "lat": 46.8,
                "lng": -71.2,
                "name": "Bounds Test Waypoint",
                "user_id": self.test_user_id
            }
        )
        assert create_response.status_code == 200
        self.created_waypoint_ids.append(create_response.json()["waypoint"]["id"])
        
        # Query by bounds
        response = requests.get(
            f"{BASE_URL}/api/v1/waypoints/bounds",
            params={
                "north": 47.0,
                "south": 46.5,
                "east": -71.0,
                "west": -71.5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "waypoints" in data
        print(f"✓ Bounds query returned {data['total']} waypoints")
    
    def test_get_stats(self):
        """Test GET /api/v1/waypoints/stats - Get statistics"""
        response = requests.get(f"{BASE_URL}/api/v1/waypoints/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "stats" in data
        assert "total" in data["stats"]
        print(f"✓ Stats: {data['stats']}")


class TestWaypointValidation:
    """Tests for waypoint input validation"""
    
    def test_create_waypoint_invalid_lat(self):
        """Test validation for invalid latitude"""
        payload = {
            "lat": 100.0,  # Invalid: > 90
            "lng": -71.0,
            "name": "Invalid Lat"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/waypoints/create",
            json=payload
        )
        
        # Should return 422 for validation error
        assert response.status_code == 422
        print("✓ Correctly rejected invalid latitude")
    
    def test_create_waypoint_invalid_lng(self):
        """Test validation for invalid longitude"""
        payload = {
            "lat": 46.0,
            "lng": -200.0,  # Invalid: < -180
            "name": "Invalid Lng"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/waypoints/create",
            json=payload
        )
        
        # Should return 422 for validation error
        assert response.status_code == 422
        print("✓ Correctly rejected invalid longitude")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
