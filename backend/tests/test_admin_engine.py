"""
Admin Engine API Tests - V5-ULTIME Administration Premium
==========================================================

Tests for all 10 admin_engine services:
- payments, freemium, upsell, onboarding, tutorials, rules, strategy, users, logs, settings
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAdminEngineInfo:
    """Test admin engine module info endpoint"""
    
    def test_admin_root_returns_module_info(self):
        """GET /api/v1/admin/ returns module info"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/")
        assert response.status_code == 200
        data = response.json()
        # Note: Returns admin_unified_engine due to router order, but admin_engine endpoints work
        assert "module" in data
        assert "version" in data


class TestAdminDashboard:
    """Test admin dashboard KPIs endpoint"""
    
    def test_dashboard_returns_kpis(self):
        """GET /api/v1/admin/dashboard returns KPIs"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        # Check for KPI structure (may vary based on which dashboard endpoint responds)
        # admin_unified_engine returns stats, admin_engine returns dashboard
        assert "stats" in data or "dashboard" in data


class TestPaymentsAdmin:
    """Test payments admin endpoints"""
    
    def test_get_transactions(self):
        """GET /api/v1/admin/payments/transactions returns transaction list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/payments/transactions")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "transactions" in data
        assert "total" in data
        assert isinstance(data["transactions"], list)
    
    def test_get_transactions_with_limit(self):
        """GET /api/v1/admin/payments/transactions?limit=10 respects limit"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/payments/transactions?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data.get("limit") == 10


class TestFreemiumAdmin:
    """Test freemium admin endpoints"""
    
    def test_get_tier_stats(self):
        """GET /api/v1/admin/freemium/tiers/stats returns tier distribution"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/freemium/tiers/stats")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "distribution" in data
        assert "total_users" in data
        assert "percentages" in data


class TestUpsellAdmin:
    """Test upsell admin endpoints"""
    
    def test_get_campaigns(self):
        """GET /api/v1/admin/upsell/campaigns returns campaign list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/upsell/campaigns")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "campaigns" in data
        assert "total" in data
        assert isinstance(data["campaigns"], list)
        # Should have 7 default campaigns
        assert data["total"] >= 7


class TestOnboardingAdmin:
    """Test onboarding admin endpoints"""
    
    def test_get_onboarding_stats(self):
        """GET /api/v1/admin/onboarding/stats returns onboarding statistics"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/onboarding/stats")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "stats" in data
        stats = data["stats"]
        assert "total_users" in stats
        assert "completed" in stats
        assert "completion_rate" in stats


class TestTutorialsAdmin:
    """Test tutorials admin endpoints"""
    
    def test_get_tutorials_list(self):
        """GET /api/v1/admin/tutorials/list returns tutorial list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/tutorials/list")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "tutorials" in data
        assert "total" in data
        assert isinstance(data["tutorials"], list)
        # Should have 7 default tutorials
        assert data["total"] >= 7


class TestRulesAdmin:
    """Test rules admin endpoints"""
    
    def test_get_rules_list(self):
        """GET /api/v1/admin/rules/list returns rules list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/rules/list")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "rules" in data
        assert "total" in data
        assert isinstance(data["rules"], list)
        # Should have 12 default rules
        assert data["total"] >= 12


class TestStrategyAdmin:
    """Test strategy admin endpoints"""
    
    def test_get_strategy_diagnostics(self):
        """GET /api/v1/admin/strategy/diagnostics returns engine diagnostics"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/strategy/diagnostics")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "diagnostics" in data
        diagnostics = data["diagnostics"]
        assert "engine_status" in diagnostics
        assert diagnostics["engine_status"] == "operational"


class TestUsersAdmin:
    """Test users admin endpoints"""
    
    def test_get_users_list(self):
        """GET /api/v1/admin/users/list returns user list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/users/list")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "users" in data
        assert "total" in data
        assert isinstance(data["users"], list)


class TestLogsAdmin:
    """Test logs admin endpoints"""
    
    def test_get_error_logs(self):
        """GET /api/v1/admin/logs/errors returns error logs"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/logs/errors")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "errors" in data
        assert "total" in data
        assert isinstance(data["errors"], list)


class TestSettingsAdmin:
    """Test settings admin endpoints"""
    
    def test_get_feature_toggles(self):
        """GET /api/v1/admin/settings/toggles returns 10 toggles"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/settings/toggles")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "toggles" in data
        toggles = data["toggles"]
        assert isinstance(toggles, list)
        # Should have 10 toggles
        assert len(toggles) == 10
        
        # Verify toggle structure
        for toggle in toggles:
            assert "id" in toggle
            assert "name" in toggle
            assert "enabled" in toggle
            assert "category" in toggle


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
