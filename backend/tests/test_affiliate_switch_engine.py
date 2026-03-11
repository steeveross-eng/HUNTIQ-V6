"""
Test Affiliate Switch Engine - Phase 6+
========================================

Tests for:
- Affiliate Switch Engine APIs (20+ endpoints)
- SEO Suppliers APIs
- Toggle switch functionality
- Validation process
- Dashboard and stats

Architecture LEGO V5-ULTIME
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestAffiliateSwitchModuleInfo:
    """Test module info endpoint"""
    
    def test_get_module_info(self):
        """GET /api/v1/affiliate-switch/ - Module info"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-switch/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["module"] == "affiliate_switch_engine"
        assert data["version"] == "1.0.0"
        assert "features" in data
        assert len(data["features"]) >= 5
        assert "statuses" in data
        assert set(data["statuses"]) == {"pending", "active", "inactive", "revoked"}
        assert "validation_steps" in data
        assert len(data["validation_steps"]) == 4


class TestAffiliateSwitchDashboard:
    """Test dashboard endpoint"""
    
    def test_get_dashboard(self):
        """GET /api/v1/affiliate-switch/dashboard - Dashboard stats"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-switch/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "dashboard" in data
        
        dashboard = data["dashboard"]
        assert "totals" in dashboard
        assert "switches" in dashboard
        assert "validation" in dashboard
        assert "by_category" in dashboard
        
        # Verify 103 affiliates as per context
        assert dashboard["totals"]["total_affiliates"] >= 100
        
        # Verify status breakdown
        assert "by_status" in dashboard["totals"]
        assert "pending" in dashboard["totals"]["by_status"]
        
        # Verify switches stats
        assert "on" in dashboard["switches"]
        assert "off" in dashboard["switches"]
        assert "activation_rate" in dashboard["switches"]


class TestAffiliateSwitchAffiliatesList:
    """Test affiliates list endpoint"""
    
    def test_get_affiliates_list(self):
        """GET /api/v1/affiliate-switch/affiliates - List affiliates"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-switch/affiliates?page=1&limit=20")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "affiliates" in data
        assert "pagination" in data
        
        # Verify pagination
        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["limit"] == 20
        assert pagination["total"] >= 100
        
        # Verify affiliate structure
        if len(data["affiliates"]) > 0:
            affiliate = data["affiliates"][0]
            assert "affiliate_id" in affiliate
            assert "company_name" in affiliate
            assert "status" in affiliate
            assert "switch_active" in affiliate
            assert "validation" in affiliate
    
    def test_get_affiliates_with_status_filter(self):
        """GET /api/v1/affiliate-switch/affiliates?status=pending - Filter by status"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-switch/affiliates?status=pending&limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        # All returned affiliates should be pending
        for affiliate in data["affiliates"]:
            assert affiliate["status"] == "pending"
    
    def test_get_affiliates_pagination(self):
        """Test pagination works correctly"""
        # Get page 1
        response1 = requests.get(f"{BASE_URL}/api/v1/affiliate-switch/affiliates?page=1&limit=5")
        data1 = response1.json()
        
        # Get page 2
        response2 = requests.get(f"{BASE_URL}/api/v1/affiliate-switch/affiliates?page=2&limit=5")
        data2 = response2.json()
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify different affiliates on different pages
        if len(data1["affiliates"]) > 0 and len(data2["affiliates"]) > 0:
            ids_page1 = {a["affiliate_id"] for a in data1["affiliates"]}
            ids_page2 = {a["affiliate_id"] for a in data2["affiliates"]}
            assert ids_page1.isdisjoint(ids_page2), "Pages should have different affiliates"


class TestAffiliateSwitchToggle:
    """Test toggle switch functionality"""
    
    @pytest.fixture
    def test_affiliate_id(self):
        """Get a test affiliate ID"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-switch/affiliates?page=1&limit=1")
        data = response.json()
        if data["affiliates"]:
            return data["affiliates"][0]["affiliate_id"]
        pytest.skip("No affiliates available for testing")
    
    def test_toggle_switch_on(self, test_affiliate_id):
        """POST /api/v1/affiliate-switch/affiliates/{id}/toggle - Activate switch"""
        response = requests.post(
            f"{BASE_URL}/api/v1/affiliate-switch/affiliates/{test_affiliate_id}/toggle",
            json={
                "is_active": True,
                "reason": "Test activation",
                "admin_user": "test_admin"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["affiliate_id"] == test_affiliate_id
        assert data["switch_active"] is True
        assert data["status"] == "active"
        assert "message" in data
    
    def test_toggle_switch_off(self, test_affiliate_id):
        """POST /api/v1/affiliate-switch/affiliates/{id}/toggle - Deactivate switch"""
        response = requests.post(
            f"{BASE_URL}/api/v1/affiliate-switch/affiliates/{test_affiliate_id}/toggle",
            json={
                "is_active": False,
                "reason": "Test deactivation",
                "admin_user": "test_admin"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["switch_active"] is False
        assert data["status"] == "inactive"
    
    def test_toggle_nonexistent_affiliate(self):
        """POST /api/v1/affiliate-switch/affiliates/{id}/toggle - 404 for invalid ID"""
        fake_id = str(uuid.uuid4())
        response = requests.post(
            f"{BASE_URL}/api/v1/affiliate-switch/affiliates/{fake_id}/toggle",
            json={"is_active": True}
        )
        assert response.status_code == 404


class TestAffiliateSwitchValidation:
    """Test validation status endpoint"""
    
    @pytest.fixture
    def test_affiliate_id(self):
        """Get a test affiliate ID"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-switch/affiliates?page=1&limit=1")
        data = response.json()
        if data["affiliates"]:
            return data["affiliates"][0]["affiliate_id"]
        pytest.skip("No affiliates available for testing")
    
    def test_get_validation_status(self, test_affiliate_id):
        """GET /api/v1/affiliate-switch/affiliates/{id}/validation-status"""
        response = requests.get(
            f"{BASE_URL}/api/v1/affiliate-switch/affiliates/{test_affiliate_id}/validation-status"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["affiliate_id"] == test_affiliate_id
        assert "company_name" in data
        assert "validation_steps" in data
        assert len(data["validation_steps"]) == 4
        assert "progress" in data
        assert "all_validated" in data
        assert "ready_for_activation" in data
        
        # Verify validation steps structure
        for step in data["validation_steps"]:
            assert "step" in step
            assert "name" in step
            assert "passed" in step
    
    def test_validation_status_nonexistent(self):
        """GET /api/v1/affiliate-switch/affiliates/{id}/validation-status - 404"""
        fake_id = str(uuid.uuid4())
        response = requests.get(
            f"{BASE_URL}/api/v1/affiliate-switch/affiliates/{fake_id}/validation-status"
        )
        assert response.status_code == 404


class TestAffiliateSwitchAffiliateDetail:
    """Test affiliate detail endpoint"""
    
    @pytest.fixture
    def test_affiliate_id(self):
        """Get a test affiliate ID"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-switch/affiliates?page=1&limit=1")
        data = response.json()
        if data["affiliates"]:
            return data["affiliates"][0]["affiliate_id"]
        pytest.skip("No affiliates available for testing")
    
    def test_get_affiliate_detail(self, test_affiliate_id):
        """GET /api/v1/affiliate-switch/affiliates/{id} - Get affiliate detail"""
        response = requests.get(
            f"{BASE_URL}/api/v1/affiliate-switch/affiliates/{test_affiliate_id}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "affiliate" in data
        assert "logs" in data
        
        affiliate = data["affiliate"]
        assert affiliate["affiliate_id"] == test_affiliate_id
        assert "company_name" in affiliate
        assert "validation" in affiliate
        assert "agreement" in affiliate
        assert "seo_integration" in affiliate
        assert "engine_sync" in affiliate
    
    def test_get_affiliate_detail_nonexistent(self):
        """GET /api/v1/affiliate-switch/affiliates/{id} - 404 for invalid ID"""
        fake_id = str(uuid.uuid4())
        response = requests.get(
            f"{BASE_URL}/api/v1/affiliate-switch/affiliates/{fake_id}"
        )
        assert response.status_code == 404


class TestAffiliateSwitchStats:
    """Test stats endpoint"""
    
    def test_get_stats(self):
        """GET /api/v1/affiliate-switch/stats - Get detailed stats"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-switch/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "stats" in data
        
        stats = data["stats"]
        assert "engine_sync" in stats
        assert "seo_integration" in stats
        assert "agreements" in stats


class TestSEOSuppliersStats:
    """Test SEO Suppliers stats endpoint"""
    
    def test_get_suppliers_stats(self):
        """GET /api/v1/bionic/seo/suppliers/stats - 104 fournisseurs"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/suppliers/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "stats" in data
        
        stats = data["stats"]
        assert stats["total_suppliers"] == 104
        assert stats["categories_count"] == 13
        assert "by_category" in stats
        assert "by_country" in stats
        assert "by_priority" in stats


class TestSEOSuppliersCategories:
    """Test SEO Suppliers categories endpoint"""
    
    def test_get_categories(self):
        """GET /api/v1/bionic/seo/suppliers/categories - 13 catégories"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/suppliers/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "categories" in data
        assert data["total_categories"] == 13
        assert data["total_suppliers"] == 104
        
        # Verify category structure
        for cat in data["categories"]:
            assert "id" in cat
            assert "name" in cat
            assert "count" in cat


class TestSEOSuppliersList:
    """Test SEO Suppliers list endpoint"""
    
    def test_get_suppliers_list(self):
        """GET /api/v1/bionic/seo/suppliers/ - List suppliers"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/suppliers/?page=1&limit=20")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "suppliers" in data
        assert "pagination" in data
        
        # Verify supplier structure
        if len(data["suppliers"]) > 0:
            supplier = data["suppliers"][0]
            assert "company" in supplier
            assert "category" in supplier
            assert "country" in supplier
    
    def test_get_suppliers_by_category(self):
        """GET /api/v1/bionic/seo/suppliers/?category=cameras - Filter by category"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/suppliers/?category=cameras&limit=20")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        # All returned suppliers should be in cameras category
        for supplier in data["suppliers"]:
            assert supplier["category"] == "cameras"


class TestSEOSuppliersExport:
    """Test SEO Suppliers export endpoint"""
    
    def test_export_csv_ready(self):
        """GET /api/v1/bionic/seo/suppliers/export?format=csv_ready"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seo/suppliers/export?format=csv_ready")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "columns" in data
        assert "data" in data
        assert len(data["data"]) == 104


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
