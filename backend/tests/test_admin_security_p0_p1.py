"""
Test Admin Security (P0) and Legacy Route Removal (P1)
=======================================================
P0: All /api/admin/geo/* endpoints must be protected with @require_admin
P1: Legacy /api/user-data/waypoints and /api/user/waypoints must return 404

Test Credentials:
- Admin: steeve.ross@gmail.com / Saturn5858*
- Hunter (non-admin): hunter.test@huntiq.ca / Test1234!
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin endpoints to test
ADMIN_GEO_ENDPOINTS = [
    ("GET", "/api/admin/geo/all"),
    ("GET", "/api/admin/geo/hotspots"),
    ("GET", "/api/admin/geo/corridors"),
    ("GET", "/api/admin/geo/analytics/overview"),
    ("GET", "/api/admin/geo/analytics/heatmap"),
    ("GET", "/api/admin/geo/monetization/available-hotspots"),
    ("GET", "/api/admin/geo/export/geojson"),
    ("GET", "/api/admin/geo/"),  # Module info
]

# Legacy routes that should return 404
LEGACY_ROUTES = [
    ("GET", "/api/user-data/waypoints"),
    ("GET", "/api/user/waypoints"),
    ("POST", "/api/user-data/waypoints"),
    ("POST", "/api/user/waypoints"),
]


class TestAdminSecurityP0:
    """P0: Test that all admin endpoints require authentication and admin role"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "steeve.ross@gmail.com",
                "password": "Saturn5858*"
            }
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("token") or data.get("access_token")
        pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")
    
    @pytest.fixture(scope="class")
    def hunter_token(self):
        """Get hunter (non-admin) authentication token"""
        # First try to register the hunter user
        requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": "hunter.test@huntiq.ca",
                "password": "Test1234!",
                "name": "Test Hunter"
            }
        )
        
        # Then login
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "hunter.test@huntiq.ca",
                "password": "Test1234!"
            }
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("token") or data.get("access_token")
        pytest.skip(f"Hunter login failed: {response.status_code} - {response.text}")
    
    # ============================================
    # Test 401 Unauthorized (No Authentication)
    # ============================================
    
    @pytest.mark.parametrize("method,endpoint", ADMIN_GEO_ENDPOINTS)
    def test_admin_endpoint_returns_401_without_auth(self, method, endpoint):
        """All admin endpoints should return 401 without authentication"""
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json={})
        
        assert response.status_code == 401, \
            f"{method} {endpoint} should return 401 without auth, got {response.status_code}"
        print(f"✓ {method} {endpoint} returns 401 without auth")
    
    # ============================================
    # Test 403 Forbidden (Non-Admin User)
    # ============================================
    
    @pytest.mark.parametrize("method,endpoint", ADMIN_GEO_ENDPOINTS)
    def test_admin_endpoint_returns_403_for_hunter(self, method, endpoint, hunter_token):
        """All admin endpoints should return 403 for non-admin users"""
        url = f"{BASE_URL}{endpoint}"
        headers = {"Authorization": f"Bearer {hunter_token}"}
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json={}, headers=headers)
        
        assert response.status_code == 403, \
            f"{method} {endpoint} should return 403 for hunter, got {response.status_code}"
        print(f"✓ {method} {endpoint} returns 403 for non-admin user")
    
    # ============================================
    # Test 200 OK (Admin User)
    # ============================================
    
    def test_admin_geo_all_works_for_admin(self, admin_token):
        """GET /api/admin/geo/all should work for admin"""
        response = requests.get(
            f"{BASE_URL}/api/admin/geo/all?limit=2",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ GET /api/admin/geo/all returns 200 for admin with {len(data)} entities")
    
    def test_admin_geo_hotspots_works_for_admin(self, admin_token):
        """GET /api/admin/geo/hotspots should work for admin"""
        response = requests.get(
            f"{BASE_URL}/api/admin/geo/hotspots?limit=3",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "hotspots" in data, "Response should contain 'hotspots' key"
        assert "by_category" in data, "Response should contain 'by_category' key"
        print(f"✓ GET /api/admin/geo/hotspots returns 200 for admin with {data.get('total', 0)} hotspots")
    
    def test_admin_geo_analytics_overview_works_for_admin(self, admin_token):
        """GET /api/admin/geo/analytics/overview should work for admin"""
        response = requests.get(
            f"{BASE_URL}/api/admin/geo/analytics/overview",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "total_entities" in data, "Response should contain 'total_entities'"
        assert "by_type" in data, "Response should contain 'by_type'"
        print(f"✓ GET /api/admin/geo/analytics/overview returns 200 for admin with {data.get('total_entities', 0)} entities")
    
    def test_admin_geo_corridors_works_for_admin(self, admin_token):
        """GET /api/admin/geo/corridors should work for admin"""
        response = requests.get(
            f"{BASE_URL}/api/admin/geo/corridors?limit=2",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "corridors" in data, "Response should contain 'corridors' key"
        print(f"✓ GET /api/admin/geo/corridors returns 200 for admin")
    
    def test_admin_geo_module_info_works_for_admin(self, admin_token):
        """GET /api/admin/geo/ should work for admin"""
        response = requests.get(
            f"{BASE_URL}/api/admin/geo/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "module" in data, "Response should contain 'module' key"
        assert data.get("module") == "admin_geo_engine", "Module should be admin_geo_engine"
        print(f"✓ GET /api/admin/geo/ returns 200 for admin")


class TestLegacyRouteRemovalP1:
    """P1: Test that legacy user_waypoints routes return 404"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "steeve.ross@gmail.com",
                "password": "Saturn5858*"
            }
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("token") or data.get("access_token")
        pytest.skip(f"Admin login failed: {response.status_code}")
    
    @pytest.mark.parametrize("method,endpoint", LEGACY_ROUTES)
    def test_legacy_route_returns_404(self, method, endpoint, admin_token):
        """Legacy user_waypoints routes should return 404"""
        url = f"{BASE_URL}{endpoint}"
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json={"test": "data"}, headers=headers)
        
        assert response.status_code == 404, \
            f"{method} {endpoint} should return 404, got {response.status_code}"
        print(f"✓ {method} {endpoint} returns 404 (legacy route removed)")


class TestBackendStartup:
    """Test that backend starts without errors"""
    
    def test_api_root_health(self):
        """API root should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "operational", "API should be operational"
        print(f"✓ API root returns operational status")
    
    def test_modules_status(self):
        """Modules status should return loaded modules"""
        response = requests.get(f"{BASE_URL}/api/modules/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "total_modules" in data, "Response should contain total_modules"
        assert data.get("total_modules", 0) > 0, "Should have loaded modules"
        print(f"✓ Modules status shows {data.get('total_modules')} modules loaded")


class TestAdminHotspotsTab:
    """Test the Hotspots tab functionality in /admin"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "steeve.ross@gmail.com",
                "password": "Saturn5858*"
            }
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("token") or data.get("access_token")
        pytest.skip(f"Admin login failed: {response.status_code}")
    
    def test_hotspots_endpoint_returns_all_categories(self, admin_token):
        """Hotspots endpoint should return hotspots with category breakdown"""
        response = requests.get(
            f"{BASE_URL}/api/admin/geo/hotspots",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "hotspots" in data
        assert "by_category" in data
        assert "total" in data
        
        # Verify categories exist
        categories = data.get("by_category", {})
        expected_categories = ["standard", "premium", "land_rental", "chalet", "environmental", "user_personal", "inactive"]
        for cat in expected_categories:
            assert cat in categories, f"Category '{cat}' should be in by_category"
        
        print(f"✓ Hotspots endpoint returns {data.get('total')} hotspots with category breakdown")
        print(f"  Categories: {categories}")
    
    def test_hotspots_filter_by_category(self, admin_token):
        """Hotspots endpoint should support category filtering"""
        categories_to_test = ["premium", "environmental", "user_personal"]
        
        for category in categories_to_test:
            response = requests.get(
                f"{BASE_URL}/api/admin/geo/hotspots?category={category}",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 200, f"Filter by {category} should work"
            print(f"✓ Hotspots filter by category={category} works")
    
    def test_hotspots_filter_by_user(self, admin_token):
        """Hotspots endpoint should support user_id filtering"""
        response = requests.get(
            f"{BASE_URL}/api/admin/geo/hotspots?user_id=system",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        print(f"✓ Hotspots filter by user_id works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
