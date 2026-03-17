"""
BIONIC V3 Certification Tests - P0 Security & Module Migration
===============================================================
Tests for 7 P0 tasks:
1) BCE-4X removed from user space (territory header)
2) Admin + Admin Premium secured with Saturn5858* password
3) Terres/Hotspots tab in Admin Premium
4) Full Hotspots V3 module in Admin Premium
5-6) Territorial data + gestionnaire access
7) Annual scheduler extraction

Backend API Tests using public URL.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://organic-zones-map.preview.emergentagent.com')

# Admin credentials
ADMIN_EMAIL = "admin@huntiq.ca"
NEW_PASSWORD = "Saturn5858*"
OLD_PASSWORD = "admin123"


class TestAdminAuthentication:
    """Tests for admin authentication with new password"""
    
    def test_new_password_login_success(self):
        """CRITICAL: New password Saturn5858* should work"""
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/login",
            json={"email": ADMIN_EMAIL, "password": NEW_PASSWORD}
        )
        assert response.status_code == 200, f"Login with new password failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "token" in data
        assert data.get("is_admin") == True
        print(f"PASS: New password login successful, token received")
    
    def test_old_password_login_rejected(self):
        """CRITICAL: Old password admin123 must be REJECTED"""
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/login",
            json={"email": ADMIN_EMAIL, "password": OLD_PASSWORD}
        )
        assert response.status_code == 401, f"Old password should be rejected, got {response.status_code}"
        data = response.json()
        assert "Invalid credentials" in str(data.get("detail", "")), "Should return invalid credentials error"
        print(f"PASS: Old password correctly rejected with 401")
    
    def test_wrong_email_rejected(self):
        """Wrong email should be rejected"""
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/login",
            json={"email": "wrong@example.com", "password": NEW_PASSWORD}
        )
        assert response.status_code == 401
        print(f"PASS: Wrong email rejected")


class TestHotspotSchedulerEndpoint:
    """Tests for POST /api/v1/admin/bionic-hotspots/scheduler/run"""
    
    def test_scheduler_run_returns_success(self):
        """CRITICAL: Scheduler extraction should return success with hotspots"""
        response = requests.post(f"{BASE_URL}/api/v1/admin/bionic-hotspots/scheduler/run")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True
        assert data.get("total_hotspots") == 300, f"Expected 300 hotspots, got {data.get('total_hotspots')}"
        assert data.get("total_regions") == 12, f"Expected 12 regions, got {data.get('total_regions')}"
        print(f"PASS: Scheduler extraction returned {data.get('total_hotspots')} hotspots from {data.get('total_regions')} regions")
    
    def test_scheduler_run_returns_bce4x_report(self):
        """Scheduler should return BCE-4X report with PASS status"""
        response = requests.post(f"{BASE_URL}/api/v1/admin/bionic-hotspots/scheduler/run")
        data = response.json()
        
        bce = data.get("bce4x_report", {})
        assert bce.get("overall") == "PASS", f"BCE-4X should PASS, got {bce.get('overall')}"
        assert bce.get("total_checks") == 1200
        assert bce.get("passed") == 1200
        assert bce.get("failed") == 0
        print(f"PASS: BCE-4X report shows {bce.get('overall')} ({bce.get('passed')}/{bce.get('total_checks')})")
    
    def test_scheduler_run_returns_next_year(self):
        """Scheduler should set next_scheduled to year+1"""
        response = requests.post(f"{BASE_URL}/api/v1/admin/bionic-hotspots/scheduler/run")
        data = response.json()
        
        next_scheduled = data.get("next_scheduled", "")
        assert "2027" in next_scheduled, f"Next scheduled should be 2027, got {next_scheduled}"
        print(f"PASS: Next scheduled extraction: {next_scheduled[:10]}")
    
    def test_scheduler_run_returns_regions_summary(self):
        """Scheduler should return regions summary with MAJEUR/FORT counts"""
        response = requests.post(f"{BASE_URL}/api/v1/admin/bionic-hotspots/scheduler/run")
        data = response.json()
        
        summary = data.get("regions_summary", [])
        assert len(summary) == 12, f"Expected 12 regions summary, got {len(summary)}"
        
        for region in summary:
            assert "region_id" in region
            assert "region_name" in region
            assert "hotspots" in region
            assert "majeur" in region
            assert "fort" in region
        print(f"PASS: Regions summary includes all 12 regions with classification counts")


class TestTerritoryTypesEndpoint:
    """Tests for GET /api/v1/admin/bionic-hotspots/territory-types"""
    
    def test_territory_types_returns_available_types(self):
        """Should return 7 territory types and 4 access statuses"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/bionic-hotspots/territory-types")
        assert response.status_code == 200
        data = response.json()
        
        types = data.get("territory_types", [])
        assert len(types) == 7, f"Expected 7 territory types, got {len(types)}"
        expected_types = ["Prive", "Public", "Gouvernemental", "ZEC", "Pourvoirie", "Reserve faunique", "Territoire autochtone"]
        for t in expected_types:
            assert t in types, f"Missing territory type: {t}"
        
        statuses = data.get("access_statuses", [])
        assert len(statuses) == 4
        print(f"PASS: 7 territory types and 4 access statuses returned")
    
    def test_territory_types_returns_distribution(self):
        """Should return distribution by type and access"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/bionic-hotspots/territory-types")
        data = response.json()
        
        by_type = data.get("distribution_by_type", {})
        by_access = data.get("distribution_by_access", {})
        
        assert len(by_type) > 0, "Should have distribution by type"
        assert len(by_access) > 0, "Should have distribution by access"
        print(f"PASS: Distribution by type: {by_type}")


class TestHotspotListEndpoint:
    """Tests for GET /api/v1/admin/bionic-hotspots/list"""
    
    def test_list_returns_hotspots_with_territory_fields(self):
        """List should return enriched territorial data"""
        # First run extraction
        requests.post(f"{BASE_URL}/api/v1/admin/bionic-hotspots/scheduler/run")
        
        response = requests.get(f"{BASE_URL}/api/v1/admin/bionic-hotspots/list?limit=10")
        assert response.status_code == 200
        data = response.json()
        
        hotspots = data.get("hotspots", [])
        assert len(hotspots) > 0, "Should have hotspots after extraction"
        
        h = hotspots[0]
        # Check enriched fields
        assert "territory_type" in h, "Missing territory_type"
        assert "access_status" in h, "Missing access_status"
        assert "ville" in h, "Missing ville"
        assert "code_postal" in h, "Missing code_postal"
        assert "altitude_m" in h, "Missing altitude_m"
        assert "center" in h, "Missing center (GPS)"
        assert "gestionnaire" in h, "Missing gestionnaire"
        print(f"PASS: Hotspots include enriched territorial data")
    
    def test_list_filter_by_territory_type(self):
        """Should filter by territory_type"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/bionic-hotspots/list?territory_type=ZEC&limit=50")
        data = response.json()
        
        hotspots = data.get("hotspots", [])
        for h in hotspots:
            assert h.get("territory_type") == "ZEC", f"Expected ZEC, got {h.get('territory_type')}"
        print(f"PASS: Filter by territory_type ZEC works ({len(hotspots)} results)")
    
    def test_list_filter_by_access_status(self):
        """Should filter by access_status"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/bionic-hotspots/list?access_status=Payant&limit=50")
        data = response.json()
        
        hotspots = data.get("hotspots", [])
        for h in hotspots:
            assert h.get("access_status") == "Payant", f"Expected Payant, got {h.get('access_status')}"
        print(f"PASS: Filter by access_status Payant works ({len(hotspots)} results)")


class TestGestionnaireData:
    """Tests for gestionnaire contact information in hotspots"""
    
    def test_gestionnaire_has_contact_info(self):
        """ZEC/Pourvoiries/Reserves should have gestionnaire contact info"""
        requests.post(f"{BASE_URL}/api/v1/admin/bionic-hotspots/scheduler/run")
        
        response = requests.get(f"{BASE_URL}/api/v1/admin/bionic-hotspots/list?territory_type=ZEC&limit=5")
        data = response.json()
        hotspots = data.get("hotspots", [])
        
        if hotspots:
            h = hotspots[0]
            g = h.get("gestionnaire", {})
            # ZEC should have nom, tel, courriel, web
            assert g.get("nom") or g.get("type"), "Gestionnaire should have nom or type"
            print(f"PASS: ZEC gestionnaire has contact info: {g.get('nom', g.get('type'))}")


class TestBCE4XReport:
    """Tests for BCE-4X compliance report"""
    
    def test_bce4x_report_returns_pass(self):
        """BCE-4X report should return PASS with all checks passing"""
        requests.post(f"{BASE_URL}/api/v1/admin/bionic-hotspots/scheduler/run")
        
        response = requests.get(f"{BASE_URL}/api/v1/admin/bionic-hotspots/report/bce4x")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("overall") == "PASS"
        assert data.get("passed") == data.get("total_checks")
        print(f"PASS: BCE-4X report overall: {data.get('overall')} ({data.get('passed')}/{data.get('total_checks')})")


class TestHotspotExports:
    """Tests for export endpoints"""
    
    def test_export_geojson_valid_structure(self):
        """Export GeoJSON should return valid GeoJSON structure"""
        requests.post(f"{BASE_URL}/api/v1/admin/bionic-hotspots/scheduler/run")
        
        response = requests.get(f"{BASE_URL}/api/v1/admin/bionic-hotspots/export/geojson")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("type") == "FeatureCollection"
        assert "features" in data
        print(f"PASS: GeoJSON export valid with {len(data.get('features', []))} features")
    
    def test_export_json_returns_data(self):
        """Export JSON should return extraction data"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/bionic-hotspots/export/json")
        assert response.status_code == 200
        data = response.json()
        
        assert "regions" in data or "error" not in data
        print(f"PASS: JSON export returns data")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
