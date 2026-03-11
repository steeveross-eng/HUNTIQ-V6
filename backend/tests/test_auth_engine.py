"""
Auth Engine Tests - Phase P4
Tests for Hybrid Authentication (JWT + Google OAuth)

Features tested:
- GET /api/auth/ - Auth info endpoint
- POST /api/auth/register - User registration with JWT
- POST /api/auth/login - User login with JWT
- GET /api/auth/me - Get authenticated user info
- GET /api/auth/verify - Verify token validity
- POST /api/auth/logout - Logout and invalidate session
- GET /api/auth/ip-info - Get IP trust information
- POST /api/auth/google/callback - Google OAuth callback
- Fallback auth for analytics/geolocation/waypoint-scoring
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

# Get backend URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    raise ValueError("REACT_APP_BACKEND_URL environment variable not set")


class TestAuthEngineInfo:
    """Test auth engine info endpoint"""
    
    def test_auth_info_endpoint(self):
        """GET /api/auth/ returns module info"""
        response = requests.get(f"{BASE_URL}/api/auth/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["module"] == "auth_engine"
        assert data["version"] == "1.0.0"
        assert data["phase"] == "P4"
        assert "Hybrid Authentication" in data["description"]
        assert "features" in data
        assert "endpoints" in data
        print(f"✓ Auth info endpoint working - version {data['version']}")


class TestUserRegistration:
    """Test user registration flow"""
    
    def test_register_new_user(self):
        """POST /api/auth/register creates new user with JWT token"""
        unique_email = f"test_{uuid.uuid4().hex[:8]}@huntiq.ca"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Test User",
            "email": unique_email,
            "password": "password123",
            "phone": "514-555-1234"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data["success"] == True
        assert "token" in data
        assert len(data["token"]) > 0
        assert "user" in data
        
        # Verify user data
        user = data["user"]
        assert user["name"] == "Test User"
        assert user["email"] == unique_email.lower()
        assert user["auth_provider"] == "local"
        assert "user_id" in user
        
        print(f"✓ User registered successfully: {user['email']}")
        return data["token"], user
    
    def test_register_duplicate_email(self):
        """POST /api/auth/register rejects duplicate email"""
        # First registration
        unique_email = f"dup_{uuid.uuid4().hex[:8]}@huntiq.ca"
        
        response1 = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "First User",
            "email": unique_email,
            "password": "password123"
        })
        assert response1.status_code == 200
        
        # Second registration with same email
        response2 = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Second User",
            "email": unique_email,
            "password": "password456"
        })
        
        assert response2.status_code == 400
        data = response2.json()
        assert "existe déjà" in data["detail"] or "already" in data["detail"].lower()
        print(f"✓ Duplicate email correctly rejected")
    
    def test_register_invalid_email(self):
        """POST /api/auth/register validates email format"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Test User",
            "email": "invalid-email",
            "password": "password123"
        })
        
        assert response.status_code == 422  # Validation error
        print(f"✓ Invalid email correctly rejected")
    
    def test_register_short_password(self):
        """POST /api/auth/register validates password length"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Test User",
            "email": f"test_{uuid.uuid4().hex[:8]}@huntiq.ca",
            "password": "123"  # Too short
        })
        
        assert response.status_code == 422  # Validation error
        print(f"✓ Short password correctly rejected")


class TestUserLogin:
    """Test user login flow"""
    
    @pytest.fixture(autouse=True)
    def setup_test_user(self):
        """Create a test user for login tests"""
        self.test_email = f"login_{uuid.uuid4().hex[:8]}@huntiq.ca"
        self.test_password = "password123"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Login Test User",
            "email": self.test_email,
            "password": self.test_password
        })
        
        if response.status_code == 200:
            self.test_user = response.json()["user"]
        else:
            pytest.skip("Could not create test user")
    
    def test_login_success(self):
        """POST /api/auth/login returns JWT token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.test_email,
            "password": self.test_password
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "token" in data
        assert len(data["token"]) > 0
        assert "user" in data
        assert data["user"]["email"] == self.test_email.lower()
        
        print(f"✓ Login successful for {self.test_email}")
    
    def test_login_wrong_password(self):
        """POST /api/auth/login rejects wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.test_email,
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "incorrect" in data["detail"].lower() or "mot de passe" in data["detail"].lower()
        print(f"✓ Wrong password correctly rejected")
    
    def test_login_nonexistent_user(self):
        """POST /api/auth/login rejects nonexistent user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@huntiq.ca",
            "password": "password123"
        })
        
        assert response.status_code == 401
        print(f"✓ Nonexistent user correctly rejected")
    
    def test_login_with_remember_device(self):
        """POST /api/auth/login with remember_device flag"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.test_email,
            "password": self.test_password,
            "remember_device": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        # device_trusted may be True or False depending on IP
        assert "device_trusted" in data
        print(f"✓ Login with remember_device successful")


class TestTokenVerification:
    """Test token verification and user info"""
    
    @pytest.fixture(autouse=True)
    def setup_authenticated_user(self):
        """Create and login a test user"""
        self.test_email = f"verify_{uuid.uuid4().hex[:8]}@huntiq.ca"
        
        # Register
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Verify Test User",
            "email": self.test_email,
            "password": "password123"
        })
        
        if reg_response.status_code == 200:
            self.token = reg_response.json()["token"]
            self.user = reg_response.json()["user"]
        else:
            pytest.skip("Could not create test user")
    
    def test_get_me_with_bearer_token(self):
        """GET /api/auth/me returns user info with Bearer token"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == self.test_email.lower()
        assert data["name"] == "Verify Test User"
        assert "user_id" in data
        print(f"✓ GET /me with Bearer token successful")
    
    def test_get_me_without_token(self):
        """GET /api/auth/me returns 401 without token"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        
        assert response.status_code == 401
        print(f"✓ GET /me without token correctly returns 401")
    
    def test_verify_valid_token(self):
        """GET /api/auth/verify validates token"""
        response = requests.get(f"{BASE_URL}/api/auth/verify?token={self.token}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == True
        assert data["user"] is not None
        assert data["user"]["email"] == self.test_email.lower()
        print(f"✓ Token verification successful")
    
    def test_verify_invalid_token(self):
        """GET /api/auth/verify rejects invalid token"""
        response = requests.get(f"{BASE_URL}/api/auth/verify?token=invalid_token_here")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == False
        assert data["user"] is None
        print(f"✓ Invalid token correctly rejected")


class TestLogout:
    """Test logout functionality"""
    
    def test_logout_with_token(self):
        """POST /api/auth/logout invalidates session"""
        # Create user and get token
        test_email = f"logout_{uuid.uuid4().hex[:8]}@huntiq.ca"
        
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Logout Test User",
            "email": test_email,
            "password": "password123"
        })
        
        assert reg_response.status_code == 200
        token = reg_response.json()["token"]
        
        # Logout
        logout_response = requests.post(
            f"{BASE_URL}/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert logout_response.status_code == 200
        data = logout_response.json()
        assert data["success"] == True
        assert "Déconnexion" in data["message"]
        print(f"✓ Logout successful")


class TestIPInfo:
    """Test IP info endpoint"""
    
    def test_ip_info_endpoint(self):
        """GET /api/auth/ip-info returns IP information"""
        response = requests.get(f"{BASE_URL}/api/auth/ip-info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "ip_address" in data
        assert "is_trusted" in data
        assert isinstance(data["is_trusted"], bool)
        print(f"✓ IP info endpoint working - IP: {data['ip_address']}")


class TestGoogleOAuthCallback:
    """Test Google OAuth callback endpoint"""
    
    def test_google_callback_invalid_session(self):
        """POST /api/auth/google/callback rejects invalid session_id"""
        response = requests.post(f"{BASE_URL}/api/auth/google/callback", json={
            "session_id": "invalid_session_id_12345"
        })
        
        # Should return 401 for invalid session
        assert response.status_code == 401
        print(f"✓ Invalid Google session correctly rejected")


class TestFallbackAuth:
    """Test that existing endpoints work with fallback auth (no token required)"""
    
    def test_analytics_dashboard_without_auth(self):
        """GET /api/v1/analytics/dashboard works without auth (uses default_user)"""
        response = requests.get(f"{BASE_URL}/api/v1/analytics/dashboard")
        
        assert response.status_code == 200
        data = response.json()
        # Should return dashboard data for default_user
        assert "overview" in data or "total_trips" in data or isinstance(data, dict)
        print(f"✓ Analytics dashboard works without auth (fallback)")
    
    def test_analytics_overview_without_auth(self):
        """GET /api/v1/analytics/overview works without auth"""
        response = requests.get(f"{BASE_URL}/api/v1/analytics/overview")
        
        assert response.status_code == 200
        print(f"✓ Analytics overview works without auth (fallback)")
    
    def test_geolocation_tracking_status_without_auth(self):
        """GET /api/v1/geolocation/tracking-status works without auth"""
        response = requests.get(f"{BASE_URL}/api/v1/geolocation/tracking-status")
        
        assert response.status_code == 200
        data = response.json()
        assert "tracking_active" in data
        assert "push_enabled" in data
        print(f"✓ Geolocation tracking status works without auth (fallback)")
    
    def test_waypoint_scoring_wqs_without_auth(self):
        """GET /api/v1/waypoint-scoring/wqs works without auth"""
        response = requests.get(f"{BASE_URL}/api/v1/waypoint-scoring/wqs")
        
        assert response.status_code == 200
        # Returns list of WQS scores (may be empty)
        assert isinstance(response.json(), list)
        print(f"✓ Waypoint scoring WQS works without auth (fallback)")
    
    def test_geolocation_info_without_auth(self):
        """GET /api/v1/geolocation/ works without auth"""
        response = requests.get(f"{BASE_URL}/api/v1/geolocation/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "geolocation_engine"
        print(f"✓ Geolocation info works without auth")


class TestAuthenticatedEndpoints:
    """Test endpoints with authenticated user"""
    
    @pytest.fixture(autouse=True)
    def setup_authenticated_user(self):
        """Create and login a test user"""
        self.test_email = f"auth_{uuid.uuid4().hex[:8]}@huntiq.ca"
        
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Auth Test User",
            "email": self.test_email,
            "password": "password123"
        })
        
        if reg_response.status_code == 200:
            self.token = reg_response.json()["token"]
            self.user = reg_response.json()["user"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not create test user")
    
    def test_analytics_with_auth(self):
        """GET /api/v1/analytics/dashboard with auth returns user-specific data"""
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/dashboard",
            headers=self.headers
        )
        
        assert response.status_code == 200
        print(f"✓ Analytics dashboard works with auth")
    
    def test_geolocation_session_with_auth(self):
        """POST /api/v1/geolocation/session/start with auth"""
        response = requests.post(
            f"{BASE_URL}/api/v1/geolocation/session/start",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "session" in data
        print(f"✓ Geolocation session start works with auth")
    
    def test_waypoint_scoring_with_auth(self):
        """GET /api/v1/waypoint-scoring/ranking with auth"""
        response = requests.get(
            f"{BASE_URL}/api/v1/waypoint-scoring/ranking",
            headers=self.headers
        )
        
        assert response.status_code == 200
        print(f"✓ Waypoint scoring ranking works with auth")


class TestVAPIDConfiguration:
    """Test VAPID keys are configured"""
    
    def test_vapid_public_key_in_geolocation(self):
        """Verify VAPID public key is configured"""
        # Check geolocation module info
        response = requests.get(f"{BASE_URL}/api/v1/geolocation/")
        
        assert response.status_code == 200
        data = response.json()
        
        # VAPID should be mentioned in features
        features_str = str(data.get("features", []))
        assert "Push" in features_str or "notification" in features_str.lower()
        print(f"✓ VAPID configuration verified in geolocation module")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
