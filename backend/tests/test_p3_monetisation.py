"""
P3 Monétisation Engines - Backend API Tests
============================================
Tests for 5 monetisation engines:
- payment_engine
- freemium_engine
- upsell_engine
- onboarding_engine
- tutorial_engine
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://alimentation-v2-fix.preview.emergentagent.com')

class TestPaymentEngine:
    """Payment Engine API Tests"""
    
    def test_payment_engine_info(self):
        """GET /api/v1/payments/ - Engine info"""
        response = requests.get(f"{BASE_URL}/api/v1/payments/")
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "payment_engine"
        assert data["version"] == "1.0.0"
        assert data["provider"] == "Stripe"
        assert "packages" in data
        print(f"✓ Payment engine info: {data['module']} v{data['version']}")
    
    def test_get_packages(self):
        """GET /api/v1/payments/packages - List packages"""
        response = requests.get(f"{BASE_URL}/api/v1/payments/packages")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "packages" in data
        packages = data["packages"]
        assert len(packages) == 4  # premium_monthly, premium_yearly, pro_monthly, pro_yearly
        
        # Verify package structure
        for pkg in packages:
            assert "id" in pkg
            assert "name" in pkg
            assert "amount" in pkg
            assert "currency" in pkg
            assert "tier" in pkg
            assert "duration_days" in pkg
        
        # Verify specific packages
        package_ids = [p["id"] for p in packages]
        assert "premium_monthly" in package_ids
        assert "premium_yearly" in package_ids
        assert "pro_monthly" in package_ids
        assert "pro_yearly" in package_ids
        print(f"✓ Packages retrieved: {len(packages)} packages")


class TestFreemiumEngine:
    """Freemium Engine API Tests"""
    
    def test_freemium_engine_info(self):
        """GET /api/v1/freemium/ - Engine info"""
        response = requests.get(f"{BASE_URL}/api/v1/freemium/")
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "freemium_engine"
        assert data["version"] == "1.0.0"
        assert "tiers" in data
        assert "free" in data["tiers"]
        assert "premium" in data["tiers"]
        assert "pro" in data["tiers"]
        print(f"✓ Freemium engine info: {data['module']} v{data['version']}")
    
    def test_get_subscription(self):
        """GET /api/v1/freemium/subscription/{user_id} - Get user subscription"""
        user_id = "test_user_123"
        response = requests.get(f"{BASE_URL}/api/v1/freemium/subscription/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "subscription" in data
        sub = data["subscription"]
        assert sub["user_id"] == user_id
        assert "tier" in sub
        assert "limits" in sub
        print(f"✓ Subscription retrieved for {user_id}: tier={sub['tier']}")
    
    def test_compare_tiers(self):
        """GET /api/v1/freemium/tiers/compare - Compare all tiers"""
        response = requests.get(f"{BASE_URL}/api/v1/freemium/tiers/compare")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "tiers" in data
        assert "features" in data
        
        # Verify tiers
        assert "free" in data["tiers"]
        assert "premium" in data["tiers"]
        assert "pro" in data["tiers"]
        
        # Verify features structure
        features = data["features"]
        assert len(features) > 0
        for feature in features:
            assert "id" in feature
            assert "name" in feature
            assert "tiers" in feature
        print(f"✓ Tier comparison: {len(features)} features compared")
    
    def test_get_pricing(self):
        """GET /api/v1/freemium/pricing - Get pricing info"""
        response = requests.get(f"{BASE_URL}/api/v1/freemium/pricing")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "pricing" in data
        pricing = data["pricing"]
        assert "free" in pricing
        assert "premium" in pricing
        assert "pro" in pricing
        print(f"✓ Pricing info retrieved")


class TestUpsellEngine:
    """Upsell Engine API Tests"""
    
    def test_upsell_engine_info(self):
        """GET /api/v1/upsell/ - Engine info"""
        response = requests.get(f"{BASE_URL}/api/v1/upsell/")
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "upsell_engine"
        assert data["version"] == "1.0.0"
        assert "trigger_types" in data
        assert "upsell_types" in data
        print(f"✓ Upsell engine info: {data['module']} v{data['version']}")
    
    def test_trigger_quota_reached(self):
        """POST /api/v1/upsell/trigger - Trigger quota reached upsell"""
        payload = {
            "user_id": "test_user_123",
            "trigger_type": "quota_reached",
            "context": {"feature": "daily_strategy_generations"}
        }
        response = requests.post(f"{BASE_URL}/api/v1/upsell/trigger", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        # May or may not return upsell depending on rate limiting
        print(f"✓ Upsell trigger tested: upsell={'yes' if data.get('upsell') else 'no (rate limited)'}")
    
    def test_trigger_feature_locked(self):
        """POST /api/v1/upsell/trigger - Trigger feature locked upsell"""
        payload = {
            "user_id": "test_user_456",
            "trigger_type": "feature_locked",
            "context": {"feature": "live_heading"}
        }
        response = requests.post(f"{BASE_URL}/api/v1/upsell/trigger", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✓ Feature locked trigger tested")
    
    def test_list_campaigns(self):
        """GET /api/v1/upsell/campaigns - List all campaigns"""
        response = requests.get(f"{BASE_URL}/api/v1/upsell/campaigns")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "campaigns" in data
        campaigns = data["campaigns"]
        assert len(campaigns) >= 7  # Default campaigns
        print(f"✓ Campaigns retrieved: {len(campaigns)} campaigns")


class TestOnboardingEngine:
    """Onboarding Engine API Tests"""
    
    def test_onboarding_engine_info(self):
        """GET /api/v1/onboarding/ - Engine info"""
        response = requests.get(f"{BASE_URL}/api/v1/onboarding/")
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "onboarding_engine"
        assert data["version"] == "1.0.0"
        assert "steps" in data
        assert data["total_steps"] == 4
        print(f"✓ Onboarding engine info: {data['module']} v{data['version']}")
    
    def test_get_onboarding_status(self):
        """GET /api/v1/onboarding/status/{user_id} - Get user onboarding status"""
        user_id = "test_user_123"
        response = requests.get(f"{BASE_URL}/api/v1/onboarding/status/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "status" in data
        status = data["status"]
        assert status["user_id"] == user_id
        assert "current_step" in status
        assert "completed_steps" in status
        assert "current_step_config" in data
        assert "progress" in data
        print(f"✓ Onboarding status for {user_id}: step={status['current_step']}, progress={data['progress']}%")
    
    def test_get_all_steps(self):
        """GET /api/v1/onboarding/steps - Get all onboarding steps"""
        response = requests.get(f"{BASE_URL}/api/v1/onboarding/steps")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "steps" in data
        steps = data["steps"]
        assert len(steps) == 4
        
        # Verify step order
        step_names = [s["step"] for s in steps]
        assert "profile" in step_names
        assert "territory" in step_names
        assert "objectives" in step_names
        assert "plan_maitre" in step_names
        print(f"✓ Onboarding steps retrieved: {len(steps)} steps")


class TestTutorialEngine:
    """Tutorial Engine API Tests"""
    
    def test_tutorial_engine_info(self):
        """GET /api/v1/tutorials/ - Engine info"""
        response = requests.get(f"{BASE_URL}/api/v1/tutorials/")
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "tutorial_engine"
        assert data["version"] == "1.0.0"
        assert "types" in data
        assert "triggers" in data
        assert data["total_tutorials"] >= 7
        print(f"✓ Tutorial engine info: {data['module']} v{data['version']}")
    
    def test_list_tutorials(self):
        """GET /api/v1/tutorials/list - List all tutorials"""
        response = requests.get(f"{BASE_URL}/api/v1/tutorials/list")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "tutorials" in data
        tutorials = data["tutorials"]
        assert len(tutorials) >= 7
        
        # Verify tutorial structure
        for tut in tutorials:
            assert "id" in tut
            assert "type" in tut
            assert "title" in tut
            assert "accessible" in tut
        print(f"✓ Tutorials retrieved: {len(tutorials)} tutorials")
    
    def test_get_daily_tip(self):
        """GET /api/v1/tutorials/tip/daily - Get daily tip"""
        response = requests.get(f"{BASE_URL}/api/v1/tutorials/tip/daily")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "tip" in data
        tip = data["tip"]
        assert tip["type"] == "tip"
        assert "title" in tip
        assert "content" in tip
        print(f"✓ Daily tip retrieved: {tip['title']}")
    
    def test_list_tutorials_by_type(self):
        """GET /api/v1/tutorials/list?type=feature - Filter by type"""
        response = requests.get(f"{BASE_URL}/api/v1/tutorials/list?type=feature")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        tutorials = data["tutorials"]
        for tut in tutorials:
            assert tut["type"] == "feature"
        print(f"✓ Feature tutorials: {len(tutorials)} tutorials")


class TestModulesIntegration:
    """Integration tests across P3 modules"""
    
    def test_all_engines_registered(self):
        """Verify all 5 P3 engines are registered"""
        engines = [
            ("/api/v1/payments/", "payment_engine"),
            ("/api/v1/freemium/", "freemium_engine"),
            ("/api/v1/upsell/", "upsell_engine"),
            ("/api/v1/onboarding/", "onboarding_engine"),
            ("/api/v1/tutorials/", "tutorial_engine"),
        ]
        
        for endpoint, expected_module in engines:
            response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"Engine {expected_module} not responding"
            data = response.json()
            assert data["module"] == expected_module, f"Wrong module name for {endpoint}"
        
        print(f"✓ All 5 P3 monetisation engines registered and responding")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
