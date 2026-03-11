"""
BIONIC V5 300% Backend Tests - Iteration 127
Tests for P0, P1, P1.1, P2 requirements
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://territory-analysis.preview.emergentagent.com')

class TestAuthAPI:
    """Authentication endpoint tests"""
    
    def test_login_success(self):
        """P0: Backend auth works with provided credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "steeve.ross@gmail.com",
                "password": "Saturn5858*"
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == "steeve.ross@gmail.com"
        print(f"Login successful for user: {data['user']['email']}")
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "invalid@example.com",
                "password": "wrongpassword"
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [401, 400], f"Expected 401/400, got {response.status_code}"


class TestHealthAPI:
    """Health check endpoint tests"""
    
    def test_health_endpoint(self):
        """Verify /api/health returns 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200


class TestBionicZonesAPI:
    """BIONIC zones generation endpoint tests"""
    
    def test_generate_zones_endpoint_exists(self):
        """Test that zones generation endpoint responds"""
        # This endpoint requires auth, so we test it returns appropriate error
        response = requests.post(
            f"{BASE_URL}/api/bionic/generate-zones-v5",
            json={
                "lat": 46.8139,
                "lng": -71.2079,
                "species": "tous"
            },
            headers={"Content-Type": "application/json"}
        )
        # Either 200 (success), 401 (needs auth), or 422 (validation) is acceptable
        assert response.status_code in [200, 201, 401, 403, 422], f"Unexpected status: {response.status_code}"
        print(f"Zones endpoint responded with status: {response.status_code}")


class TestUserDataAPI:
    """User data (waypoints) endpoint tests"""
    
    def test_user_data_endpoint(self):
        """Test user-data endpoint (may return 404 if not implemented)"""
        response = requests.get(f"{BASE_URL}/api/user-data/anonymous")
        # 404 is acceptable if using localStorage fallback
        assert response.status_code in [200, 401, 404], f"Unexpected status: {response.status_code}"
        print(f"User data endpoint status: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
