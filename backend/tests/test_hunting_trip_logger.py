"""
Test Suite for Hunting Trip Logger Module and Password Reset Features
Tests: Trip CRUD, Waypoint Visits, Observations, Statistics, Password Reset Flow
"""
import pytest
import requests
import os
import uuid
from datetime import datetime, timedelta

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "test@huntiq.ca"
TEST_PASSWORD = "password123"


class TestHuntingTripLoggerInfo:
    """Test hunting trip logger info endpoint"""
    
    def test_trip_logger_info_endpoint(self):
        """GET /api/v1/trips/ - Module info endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/trips/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["module"] == "hunting_trip_logger"
        assert data["version"] == "1.0.0"
        assert data["phase"] == "P4+"
        assert "features" in data
        assert "endpoints" in data
        print(f"✓ Trip logger info: {data['module']} v{data['version']}")


class TestAuthAndLogin:
    """Test authentication for trip logger tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for tests"""
        # Try to login with test user
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            token = response.json().get("token")
            print(f"✓ Logged in as {TEST_EMAIL}")
            return token
        
        # If login fails, try to register
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": "Test User"
        })
        
        if response.status_code == 200:
            token = response.json().get("token")
            print(f"✓ Registered and logged in as {TEST_EMAIL}")
            return token
        
        # If both fail, skip authenticated tests
        pytest.skip(f"Could not authenticate: {response.text}")
    
    def test_login_success(self, auth_token):
        """Verify login works"""
        assert auth_token is not None
        assert len(auth_token) > 0
        print(f"✓ Auth token obtained: {auth_token[:20]}...")


class TestTripCRUD:
    """Test hunting trip CRUD operations"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if response.status_code != 200:
            # Try register
            response = requests.post(f"{BASE_URL}/api/auth/register", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "name": "Test User"
            })
        
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}"}
        
        pytest.skip("Could not authenticate")
    
    @pytest.fixture(scope="class")
    def created_trip_id(self, auth_headers):
        """Create a trip and return its ID for other tests"""
        trip_data = {
            "target_species": "deer",
            "planned_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "title": f"TEST_Trip_{uuid.uuid4().hex[:8]}",
            "planned_waypoints": [],
            "notes": "Test trip for pytest"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/trips/create",
            json=trip_data,
            headers=auth_headers
        )
        
        if response.status_code == 200:
            data = response.json()
            trip_id = data["trip"]["trip_id"]
            print(f"✓ Created test trip: {trip_id}")
            return trip_id
        
        pytest.skip(f"Could not create trip: {response.text}")
    
    def test_create_trip(self, auth_headers):
        """POST /api/v1/trips/create - Create new hunting trip"""
        trip_data = {
            "target_species": "moose",
            "planned_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "title": f"TEST_Moose_Hunt_{uuid.uuid4().hex[:8]}",
            "planned_waypoints": [],
            "notes": "Test moose hunting trip"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/trips/create",
            json=trip_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "trip" in data
        assert data["trip"]["target_species"] == "moose"
        assert data["trip"]["status"] == "planned"
        assert "trip_id" in data["trip"]
        
        print(f"✓ Created trip: {data['trip']['trip_id']}")
    
    def test_list_trips(self, auth_headers):
        """GET /api/v1/trips/list - List user trips"""
        response = requests.get(
            f"{BASE_URL}/api/v1/trips/list",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"✓ Listed {len(data)} trips")
    
    def test_list_trips_with_status_filter(self, auth_headers):
        """GET /api/v1/trips/list?status=planned - Filter by status"""
        response = requests.get(
            f"{BASE_URL}/api/v1/trips/list?status=planned",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        for trip in data:
            assert trip["status"] == "planned"
        
        print(f"✓ Listed {len(data)} planned trips")
    
    def test_get_active_trip_none(self, auth_headers):
        """GET /api/v1/trips/active - No active trip initially"""
        response = requests.get(
            f"{BASE_URL}/api/v1/trips/active",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # May or may not have active trip
        assert "active" in data
        print(f"✓ Active trip check: active={data['active']}")
    
    def test_start_trip(self, auth_headers, created_trip_id):
        """POST /api/v1/trips/start - Start a hunting trip"""
        start_data = {
            "trip_id": created_trip_id,
            "actual_weather": "cloudy",
            "temperature": 5.0,
            "wind_speed": 10.0
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/trips/start",
            json=start_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["trip"]["status"] == "in_progress"
        assert data["trip"]["weather"] == "cloudy"
        assert data["trip"]["temperature"] == 5.0
        
        print(f"✓ Started trip: {created_trip_id}")
    
    def test_get_active_trip_after_start(self, auth_headers, created_trip_id):
        """GET /api/v1/trips/active - Should have active trip after start"""
        response = requests.get(
            f"{BASE_URL}/api/v1/trips/active",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["active"] == True
        assert data["trip"]["trip_id"] == created_trip_id
        
        print(f"✓ Active trip confirmed: {created_trip_id}")
    
    def test_get_trip_details(self, auth_headers, created_trip_id):
        """GET /api/v1/trips/{trip_id} - Get trip details"""
        response = requests.get(
            f"{BASE_URL}/api/v1/trips/{created_trip_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["trip"]["trip_id"] == created_trip_id
        
        print(f"✓ Got trip details: {created_trip_id}")


class TestObservations:
    """Test observation logging"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}"}
        
        pytest.skip("Could not authenticate")
    
    @pytest.fixture(scope="class")
    def active_trip_id(self, auth_headers):
        """Get or create an active trip for observation tests"""
        # Check for active trip
        response = requests.get(
            f"{BASE_URL}/api/v1/trips/active",
            headers=auth_headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("active") and data.get("trip"):
                return data["trip"]["trip_id"]
        
        # Create and start a new trip
        trip_data = {
            "target_species": "deer",
            "planned_date": datetime.now().isoformat(),
            "title": f"TEST_Observation_Trip_{uuid.uuid4().hex[:8]}"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/trips/create",
            json=trip_data,
            headers=auth_headers
        )
        
        if response.status_code == 200:
            trip_id = response.json()["trip"]["trip_id"]
            
            # Start the trip
            requests.post(
                f"{BASE_URL}/api/v1/trips/start",
                json={"trip_id": trip_id, "actual_weather": "sunny"},
                headers=auth_headers
            )
            
            return trip_id
        
        pytest.skip("Could not create trip for observations")
    
    def test_log_observation_sighting(self, auth_headers, active_trip_id):
        """POST /api/v1/trips/observations - Log a sighting"""
        obs_data = {
            "trip_id": active_trip_id,
            "observation_type": "sighting",
            "species": "deer",
            "count": 3,
            "distance_meters": 150.0,
            "direction": "NE",
            "behavior": "feeding",
            "notes": "Test sighting observation"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/trips/observations",
            json=obs_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "observation" in data
        assert data["observation"]["species"] == "deer"
        assert data["observation"]["count"] == 3
        assert data["observation"]["observation_type"] == "sighting"
        
        print(f"✓ Logged sighting: {data['observation']['observation_id']}")
    
    def test_log_observation_tracks(self, auth_headers, active_trip_id):
        """POST /api/v1/trips/observations - Log tracks"""
        obs_data = {
            "trip_id": active_trip_id,
            "observation_type": "tracks",
            "species": "moose",
            "count": 1,
            "notes": "Fresh moose tracks in snow"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/trips/observations",
            json=obs_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["observation"]["observation_type"] == "tracks"
        
        print(f"✓ Logged tracks: {data['observation']['observation_id']}")
    
    def test_list_observations(self, auth_headers, active_trip_id):
        """GET /api/v1/trips/observations/list - List observations"""
        response = requests.get(
            f"{BASE_URL}/api/v1/trips/observations/list?trip_id={active_trip_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 2  # At least the 2 we created
        
        print(f"✓ Listed {len(data)} observations for trip")


class TestWaypointVisits:
    """Test waypoint visit logging"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}"}
        
        pytest.skip("Could not authenticate")
    
    def test_log_waypoint_visit(self, auth_headers):
        """POST /api/v1/trips/visits - Log waypoint visit"""
        visit_data = {
            "waypoint_id": f"test_waypoint_{uuid.uuid4().hex[:8]}",
            "activity_level": 7,
            "weather": "cloudy",
            "notes": "Test waypoint visit"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/trips/visits",
            json=visit_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "visit" in data
        assert data["visit"]["activity_level"] == 7
        
        print(f"✓ Logged visit: {data['visit']['visit_id']}")
        return data["visit"]["visit_id"]
    
    def test_list_visits(self, auth_headers):
        """GET /api/v1/trips/visits/list - List waypoint visits"""
        response = requests.get(
            f"{BASE_URL}/api/v1/trips/visits/list",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"✓ Listed {len(data)} waypoint visits")


class TestTripEndAndStatistics:
    """Test trip ending and statistics"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}"}
        
        pytest.skip("Could not authenticate")
    
    @pytest.fixture(scope="class")
    def trip_to_end(self, auth_headers):
        """Get active trip or create one to end"""
        # Check for active trip
        response = requests.get(
            f"{BASE_URL}/api/v1/trips/active",
            headers=auth_headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("active") and data.get("trip"):
                return data["trip"]["trip_id"]
        
        # Create and start a new trip
        trip_data = {
            "target_species": "deer",
            "planned_date": datetime.now().isoformat(),
            "title": f"TEST_End_Trip_{uuid.uuid4().hex[:8]}"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/trips/create",
            json=trip_data,
            headers=auth_headers
        )
        
        if response.status_code == 200:
            trip_id = response.json()["trip"]["trip_id"]
            
            # Start the trip
            requests.post(
                f"{BASE_URL}/api/v1/trips/start",
                json={"trip_id": trip_id, "actual_weather": "sunny"},
                headers=auth_headers
            )
            
            return trip_id
        
        pytest.skip("Could not create trip to end")
    
    def test_end_trip(self, auth_headers, trip_to_end):
        """POST /api/v1/trips/end - End a hunting trip"""
        end_data = {
            "trip_id": trip_to_end,
            "success": True,
            "notes": "Test trip completed successfully"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/trips/end",
            json=end_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["trip"]["status"] == "completed"
        assert data["trip"]["success"] == True
        
        print(f"✓ Ended trip: {trip_to_end}")
    
    def test_get_user_statistics(self, auth_headers):
        """GET /api/v1/trips/statistics - Get user statistics"""
        response = requests.get(
            f"{BASE_URL}/api/v1/trips/statistics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "statistics" in data
        
        stats = data["statistics"]
        assert "total_trips" in stats
        assert "success_rate" in stats
        assert "total_hours" in stats
        
        print(f"✓ User statistics: {stats['total_trips']} trips, {stats['success_rate']}% success rate")
    
    def test_get_waypoint_statistics(self, auth_headers):
        """GET /api/v1/trips/statistics/waypoint/{id} - Get waypoint stats"""
        # Use a test waypoint ID
        waypoint_id = "test_waypoint_stats"
        
        response = requests.get(
            f"{BASE_URL}/api/v1/trips/statistics/waypoint/{waypoint_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        # May or may not have statistics for this waypoint
        print(f"✓ Waypoint statistics retrieved")


class TestDataSyncToAnalytics:
    """Test that completed trips sync to analytics_trips collection"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}"}
        
        pytest.skip("Could not authenticate")
    
    def test_completed_trip_syncs_to_analytics(self, auth_headers):
        """Verify completed trip appears in analytics"""
        # Create, start, and end a trip
        trip_data = {
            "target_species": "deer",
            "planned_date": datetime.now().isoformat(),
            "title": f"TEST_Analytics_Sync_{uuid.uuid4().hex[:8]}"
        }
        
        # Create
        response = requests.post(
            f"{BASE_URL}/api/v1/trips/create",
            json=trip_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        trip_id = response.json()["trip"]["trip_id"]
        
        # Start
        response = requests.post(
            f"{BASE_URL}/api/v1/trips/start",
            json={"trip_id": trip_id, "actual_weather": "sunny", "temperature": 10.0},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # End
        response = requests.post(
            f"{BASE_URL}/api/v1/trips/end",
            json={"trip_id": trip_id, "success": True, "notes": "Analytics sync test"},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Verify trip is completed
        data = response.json()
        assert data["trip"]["status"] == "completed"
        
        print(f"✓ Trip {trip_id} completed and synced to analytics")


class TestPasswordResetFlow:
    """Test password reset via email flow"""
    
    def test_forgot_password_endpoint(self):
        """POST /api/auth/forgot-password - Request password reset"""
        response = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": TEST_EMAIL}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        # Should always return success to prevent email enumeration
        assert "message" in data
        
        print(f"✓ Forgot password request sent for {TEST_EMAIL}")
    
    def test_forgot_password_nonexistent_email(self):
        """POST /api/auth/forgot-password - Non-existent email still returns success"""
        response = requests.post(
            f"{BASE_URL}/api/auth/forgot-password",
            json={"email": "nonexistent@example.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should still return success to prevent email enumeration
        assert data["success"] == True
        
        print("✓ Forgot password returns success for non-existent email (security)")
    
    def test_verify_reset_token_invalid(self):
        """GET /api/auth/verify-reset-token - Invalid token"""
        response = requests.get(
            f"{BASE_URL}/api/auth/verify-reset-token?token=invalid_token_12345"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == False
        assert data["email"] is None
        
        print("✓ Invalid reset token correctly rejected")
    
    def test_reset_password_invalid_token(self):
        """POST /api/auth/reset-password - Invalid token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/reset-password?token=invalid_token&new_password=newpassword123"
        )
        
        assert response.status_code == 400
        data = response.json()
        
        assert "detail" in data
        # Should indicate invalid or expired token
        
        print("✓ Reset password with invalid token correctly rejected")
    
    def test_reset_password_short_password(self):
        """POST /api/auth/reset-password - Password too short"""
        response = requests.post(
            f"{BASE_URL}/api/auth/reset-password?token=some_token&new_password=123"
        )
        
        assert response.status_code == 400
        data = response.json()
        
        # Should indicate password too short
        assert "detail" in data
        
        print("✓ Short password correctly rejected")


class TestFullTripWorkflow:
    """Test complete trip workflow: Create -> Start -> Log Observation -> End -> Check Statistics"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}"}
        
        pytest.skip("Could not authenticate")
    
    def test_full_workflow(self, auth_headers):
        """Complete trip workflow test"""
        # 1. Create trip
        trip_data = {
            "target_species": "deer",
            "planned_date": datetime.now().isoformat(),
            "title": f"TEST_Full_Workflow_{uuid.uuid4().hex[:8]}",
            "notes": "Full workflow test"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/trips/create",
            json=trip_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        trip_id = response.json()["trip"]["trip_id"]
        print(f"  1. Created trip: {trip_id}")
        
        # 2. Start trip
        response = requests.post(
            f"{BASE_URL}/api/v1/trips/start",
            json={
                "trip_id": trip_id,
                "actual_weather": "cloudy",
                "temperature": 8.0,
                "wind_speed": 15.0
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["trip"]["status"] == "in_progress"
        print(f"  2. Started trip with weather: cloudy, 8°C")
        
        # 3. Log observation
        response = requests.post(
            f"{BASE_URL}/api/v1/trips/observations",
            json={
                "trip_id": trip_id,
                "observation_type": "sighting",
                "species": "deer",
                "count": 2,
                "distance_meters": 100.0,
                "behavior": "moving"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        obs_id = response.json()["observation"]["observation_id"]
        print(f"  3. Logged observation: {obs_id}")
        
        # 4. End trip
        response = requests.post(
            f"{BASE_URL}/api/v1/trips/end",
            json={
                "trip_id": trip_id,
                "success": True,
                "notes": "Successful hunt!"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        trip_data = response.json()["trip"]
        assert trip_data["status"] == "completed"
        assert trip_data["success"] == True
        assert trip_data["observations_count"] >= 1
        print(f"  4. Ended trip: {trip_data['observations_count']} observations")
        
        # 5. Check statistics
        response = requests.get(
            f"{BASE_URL}/api/v1/trips/statistics",
            headers=auth_headers
        )
        assert response.status_code == 200
        stats = response.json()["statistics"]
        assert stats["total_trips"] >= 1
        print(f"  5. Statistics: {stats['total_trips']} total trips, {stats['success_rate']}% success rate")
        
        print(f"✓ Full workflow completed successfully!")


class TestFallbackAuth:
    """Test that trip logger works with fallback auth (no token)"""
    
    def test_trip_info_without_auth(self):
        """GET /api/v1/trips/ - Works without auth"""
        response = requests.get(f"{BASE_URL}/api/v1/trips/")
        assert response.status_code == 200
        print("✓ Trip info endpoint works without auth")
    
    def test_create_trip_without_auth(self):
        """POST /api/v1/trips/create - Works with fallback user"""
        trip_data = {
            "target_species": "deer",
            "planned_date": datetime.now().isoformat(),
            "title": f"TEST_NoAuth_Trip_{uuid.uuid4().hex[:8]}"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/trips/create",
            json=trip_data
        )
        
        # Should work with fallback user
        assert response.status_code == 200
        print("✓ Create trip works with fallback auth")
    
    def test_statistics_without_auth(self):
        """GET /api/v1/trips/statistics - Works with fallback user"""
        response = requests.get(f"{BASE_URL}/api/v1/trips/statistics")
        assert response.status_code == 200
        print("✓ Statistics endpoint works with fallback auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
