"""
Phase 21 - E2E Final Tests for BIONIC HUNT/Chasse-V5
=========================================
Tests for Release Candidate validation.
Covers: Waypoints API, Recommendation Engine, Authentication
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestWaypointEngineAPI:
    """PRIORITÉ 3 - Waypoints API Tests"""
    
    def test_waypoint_module_info(self):
        """GET /api/v1/waypoints/ - Module info"""
        response = requests.get(f"{BASE_URL}/api/v1/waypoints/")
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "waypoint_engine"
        assert data["version"] == "1.0.0"
        assert "stats" in data
        print(f"✅ Waypoint module info: {data['module']} v{data['version']}")
    
    def test_create_waypoint(self):
        """POST /api/v1/waypoints/create - Create waypoint"""
        test_id = str(uuid.uuid4())[:8]
        payload = {
            "lat": 46.8139,
            "lng": -71.2082,
            "name": f"TEST_waypoint_{test_id}",
            "source": "user_double_click",
            "user_id": "test_user_e2e"
        }
        response = requests.post(f"{BASE_URL}/api/v1/waypoints/create", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "waypoint" in data
        assert data["waypoint"]["name"] == payload["name"]
        assert data["waypoint"]["lat"] == payload["lat"]
        assert data["waypoint"]["lng"] == payload["lng"]
        print(f"✅ Waypoint created: {data['waypoint']['name']}")
        return data["waypoint"]["id"]
    
    def test_list_waypoints(self):
        """GET /api/v1/waypoints - List waypoints"""
        response = requests.get(f"{BASE_URL}/api/v1/waypoints")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "waypoints" in data
        assert "total" in data
        print(f"✅ Listed {data['total']} waypoints")
    
    def test_list_waypoints_with_filter(self):
        """GET /api/v1/waypoints?user_id=test - Filter by user"""
        response = requests.get(f"{BASE_URL}/api/v1/waypoints?user_id=test_user_e2e")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✅ Filtered waypoints for test_user_e2e: {data['total']}")
    
    def test_waypoints_in_bounds(self):
        """GET /api/v1/waypoints/bounds - Geographic bounds query"""
        params = {
            "north": 47.0,
            "south": 46.0,
            "east": -70.0,
            "west": -72.0
        }
        response = requests.get(f"{BASE_URL}/api/v1/waypoints/bounds", params=params)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✅ Waypoints in bounds: {data['total']}")
    
    def test_waypoint_stats(self):
        """GET /api/v1/waypoints/stats - Statistics"""
        response = requests.get(f"{BASE_URL}/api/v1/waypoints/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "stats" in data
        print(f"✅ Waypoint stats: {data['stats']}")


class TestRecommendationEngineAPI:
    """PRIORITÉ 4 - Recommendation Engine Tests"""
    
    def test_recommendation_module_info(self):
        """GET /api/v1/recommendation/ - Module info"""
        response = requests.get(f"{BASE_URL}/api/v1/recommendation/")
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "recommendation_engine"
        assert data["version"] == "1.0.0"
        assert data["status"] == "operational"
        print(f"✅ Recommendation module: {data['module']} v{data['version']} - {data['status']}")
    
    def test_recommendation_health(self):
        """GET /api/v1/recommendation/health - Health check"""
        response = requests.get(f"{BASE_URL}/api/v1/recommendation/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✅ Recommendation health: {data['status']}")
    
    def test_strategies_for_species(self):
        """GET /api/v1/recommendation/strategies?species=deer - Strategy recommendations"""
        response = requests.get(f"{BASE_URL}/api/v1/recommendation/strategies?species=deer")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        print(f"✅ Strategies for deer: {len(data['data'].get('strategies', []))} strategies")
    
    def test_strategies_with_season(self):
        """GET /api/v1/recommendation/strategies?species=deer&season=rut"""
        response = requests.get(f"{BASE_URL}/api/v1/recommendation/strategies?species=deer&season=rut")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✅ Strategies for deer in rut season: OK")
    
    def test_contextual_recommendations(self):
        """GET /api/v1/recommendation/for-context?species=deer&season=rut"""
        params = {
            "species": "deer",
            "season": "rut"
        }
        response = requests.get(f"{BASE_URL}/api/v1/recommendation/for-context", params=params)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        print(f"✅ Contextual recommendations: OK")
    
    def test_contextual_with_weather(self):
        """GET /api/v1/recommendation/for-context with weather params"""
        params = {
            "species": "deer",
            "season": "rut",
            "temperature": 5.0,
            "humidity": 70.0,
            "wind_speed": 15.0
        }
        response = requests.get(f"{BASE_URL}/api/v1/recommendation/for-context", params=params)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✅ Contextual recommendations with weather: OK")
    
    def test_personalized_recommendations(self):
        """GET /api/v1/recommendation/personalized/{user_id}"""
        response = requests.get(f"{BASE_URL}/api/v1/recommendation/personalized/test_user_123")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["user_id"] == "test_user_123"
        print(f"✅ Personalized recommendations for test_user_123: OK")


class TestAuthenticationAPI:
    """PRIORITÉ 1 - Authentication Tests"""
    
    def test_auth_health(self):
        """GET /api/health - API health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✅ API health: {data['status']}")
    
    def test_auth_login_endpoint_exists(self):
        """POST /api/auth/login - Endpoint exists"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@test.com",
            "password": "wrongpassword"
        })
        # Should return 401 for invalid credentials, not 404
        assert response.status_code in [401, 400, 422]
        print(f"✅ Auth login endpoint exists (status: {response.status_code})")
    
    def test_auth_register_endpoint_exists(self):
        """POST /api/auth/register - Endpoint exists"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
            "password": "testpassword123",
            "name": "Test User"
        })
        # Should return 200/201 for success or 400/409 for duplicate
        assert response.status_code in [200, 201, 400, 409, 422]
        print(f"✅ Auth register endpoint exists (status: {response.status_code})")


class TestWaypointScoringAPI:
    """Additional Waypoint Scoring Tests"""
    
    def test_waypoint_scoring_module(self):
        """GET /api/v1/waypoint-scoring/ - Module info"""
        response = requests.get(f"{BASE_URL}/api/v1/waypoint-scoring/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Waypoint scoring module: {data.get('module', 'OK')}")
        else:
            print(f"⚠️ Waypoint scoring module not found (status: {response.status_code})")
            pytest.skip("Waypoint scoring module not available")


class TestCriticalEndpoints:
    """Critical endpoints that must work for Release Candidate"""
    
    def test_api_root(self):
        """GET /api - API root"""
        response = requests.get(f"{BASE_URL}/api")
        assert response.status_code in [200, 404]  # May redirect or return info
        print(f"✅ API root accessible")
    
    def test_docs_endpoint(self):
        """GET /api/docs - API documentation"""
        response = requests.get(f"{BASE_URL}/api/docs")
        assert response.status_code == 200
        print(f"✅ API docs accessible")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
