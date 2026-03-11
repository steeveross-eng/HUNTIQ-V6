"""
Test Ad Spaces Engine - COMMANDE 4
==================================
Tests for:
- Ad Spaces Catalog (18 spaces, 6 categories)
- Ad Slot Manager
- Ad Render Engine (PRE-PRODUCTION mode)
- Master Switch integration
- Affiliate Ads system status
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAdSpacesModule:
    """Test Ad Spaces Engine module info"""
    
    def test_module_info(self):
        """GET /api/v1/ad-spaces/ - Module info"""
        response = requests.get(f"{BASE_URL}/api/v1/ad-spaces/")
        assert response.status_code == 200
        data = response.json()
        
        assert data["module"] == "ad_spaces_engine"
        assert data["version"] == "1.0.0"
        assert data["total_spaces"] == 18
        assert len(data["categories"]) == 6
        assert "banner" in data["categories"]
        assert "sidebar" in data["categories"]
        assert "native" in data["categories"]
        assert "carousel" in data["categories"]
        assert "featured" in data["categories"]
        assert "inline" in data["categories"]
        print(f"✓ Module info: {data['total_spaces']} spaces, {len(data['categories'])} categories")


class TestAdSpacesCatalog:
    """Test Ad Spaces Catalog endpoints"""
    
    def test_catalog_full(self):
        """GET /api/v1/ad-spaces/catalog - Full catalog"""
        response = requests.get(f"{BASE_URL}/api/v1/ad-spaces/catalog")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["total"] == 18
        assert len(data["catalog"]) == 18
        
        # Verify category counts
        categories = data["categories"]
        assert categories["banner"] == 3
        assert categories["sidebar"] == 3
        assert categories["native"] == 3
        assert categories["carousel"] == 2
        assert categories["featured"] == 5
        assert categories["inline"] == 2
        print(f"✓ Catalog: {data['total']} spaces with correct category distribution")
    
    def test_catalog_by_category_banner(self):
        """GET /api/v1/ad-spaces/catalog/by-category/banner"""
        response = requests.get(f"{BASE_URL}/api/v1/ad-spaces/catalog/by-category/banner")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["category"] == "banner"
        assert data["count"] == 3
        
        space_names = [s["name"] for s in data["spaces"]]
        assert "Header Banner Principal" in space_names
        assert "Header Banner Catégorie" in space_names
        assert "Footer Banner Principal" in space_names
        print(f"✓ Banner category: {data['count']} spaces")
    
    def test_catalog_by_category_sidebar(self):
        """GET /api/v1/ad-spaces/catalog/by-category/sidebar"""
        response = requests.get(f"{BASE_URL}/api/v1/ad-spaces/catalog/by-category/sidebar")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["count"] == 3
        print(f"✓ Sidebar category: {data['count']} spaces")
    
    def test_catalog_by_category_featured(self):
        """GET /api/v1/ad-spaces/catalog/by-category/featured"""
        response = requests.get(f"{BASE_URL}/api/v1/ad-spaces/catalog/by-category/featured")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["count"] == 5
        print(f"✓ Featured category: {data['count']} spaces")
    
    def test_catalog_by_page_homepage(self):
        """GET /api/v1/ad-spaces/catalog/by-page/homepage"""
        response = requests.get(f"{BASE_URL}/api/v1/ad-spaces/catalog/by-page/homepage")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["page"] == "homepage"
        # Homepage should have spaces with "homepage" or "all" in pages
        assert data["count"] >= 5  # At least 5 spaces for homepage
        print(f"✓ Homepage spaces: {data['count']} available")
    
    def test_catalog_space_details(self):
        """GET /api/v1/ad-spaces/catalog/header_banner_main"""
        response = requests.get(f"{BASE_URL}/api/v1/ad-spaces/catalog/header_banner_main")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        space = data["space"]
        assert space["space_id"] == "header_banner_main"
        assert space["name"] == "Header Banner Principal"
        assert space["category"] == "banner"
        assert space["priority"] == "premium"
        assert space["base_price_multiplier"] == 2.5
        print(f"✓ Space details: {space['name']} (multiplier: {space['base_price_multiplier']}x)")
    
    def test_catalog_space_not_found(self):
        """GET /api/v1/ad-spaces/catalog/invalid_space - 404"""
        response = requests.get(f"{BASE_URL}/api/v1/ad-spaces/catalog/invalid_space")
        assert response.status_code == 404
        print("✓ Invalid space returns 404")


class TestAdSpacesDashboard:
    """Test Ad Spaces Dashboard"""
    
    def test_dashboard(self):
        """GET /api/v1/ad-spaces/dashboard"""
        response = requests.get(f"{BASE_URL}/api/v1/ad-spaces/dashboard")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        dashboard = data["dashboard"]
        
        # Master switch should be OFF (PRE-PRODUCTION)
        assert dashboard["master_switch"]["is_active"] == False
        assert dashboard["master_switch"]["mode"] == "PRE_PRODUCTION"
        
        # Catalog info
        assert dashboard["catalog"]["total_spaces"] == 18
        
        print(f"✓ Dashboard: Mode {dashboard['master_switch']['mode']}, {dashboard['catalog']['total_spaces']} spaces")


class TestAdSlotsManager:
    """Test Ad Slot Manager"""
    
    def test_active_slots_preproduction(self):
        """GET /api/v1/ad-spaces/slots/active - PRE-PRODUCTION mode"""
        response = requests.get(f"{BASE_URL}/api/v1/ad-spaces/slots/active")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["mode"] == "PRE_PRODUCTION"
        assert data["ads_will_render"] == False
        # In pre-production, active slots should be 0 (all paused)
        assert data["count"] == 0
        print(f"✓ Active slots: {data['count']} (PRE-PRODUCTION mode)")
    
    def test_slot_conflicts(self):
        """GET /api/v1/ad-spaces/slots/conflicts"""
        response = requests.get(f"{BASE_URL}/api/v1/ad-spaces/slots/conflicts")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "has_conflicts" in data
        print(f"✓ Slot conflicts check: has_conflicts={data['has_conflicts']}")


class TestAdRenderEngine:
    """Test Ad Render Engine - PRE-PRODUCTION mode"""
    
    def test_render_sidebar_mid_preproduction(self):
        """GET /api/v1/ad-spaces/render/sidebar_mid - No render in PRE-PRODUCTION"""
        response = requests.get(f"{BASE_URL}/api/v1/ad-spaces/render/sidebar_mid")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["render"] == False
        assert data["reason"] == "System in pre-production mode"
        assert data["ad"] is None
        print(f"✓ Render sidebar_mid: render={data['render']} (reason: {data['reason']})")
    
    def test_render_header_banner_preproduction(self):
        """GET /api/v1/ad-spaces/render/header_banner_main - No render in PRE-PRODUCTION"""
        response = requests.get(f"{BASE_URL}/api/v1/ad-spaces/render/header_banner_main")
        assert response.status_code == 200
        data = response.json()
        
        assert data["render"] == False
        print(f"✓ Render header_banner_main: render={data['render']}")
    
    def test_render_page_homepage_preproduction(self):
        """GET /api/v1/ad-spaces/render/page/homepage - No ads in PRE-PRODUCTION"""
        response = requests.get(f"{BASE_URL}/api/v1/ad-spaces/render/page/homepage")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["mode"] == "PRE_PRODUCTION"
        assert data["render"] == False
        assert len(data["ads"]) == 0
        print(f"✓ Render page homepage: {len(data['ads'])} ads (PRE-PRODUCTION)")
    
    def test_render_invalid_space(self):
        """GET /api/v1/ad-spaces/render/invalid_space - Returns render=false in PRE-PRODUCTION"""
        response = requests.get(f"{BASE_URL}/api/v1/ad-spaces/render/invalid_space")
        # In PRE-PRODUCTION mode, master switch check happens first, so returns 200 with render=false
        # In PRODUCTION mode, this would return 404 for invalid space
        assert response.status_code == 200
        data = response.json()
        assert data["render"] == False
        assert data["reason"] == "System in pre-production mode"
        print("✓ Render invalid space: returns render=false in PRE-PRODUCTION mode")


class TestMasterSwitch:
    """Test Master Switch Publicitaire"""
    
    def test_master_switch_status(self):
        """GET /api/v1/affiliate-ads/master-switch"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/master-switch")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        switch = data["master_switch"]
        assert switch["switch_id"] == "global"
        assert switch["is_active"] == False  # PRE-PRODUCTION
        assert switch["auto_deploy_enabled"] == False
        assert "pré-production" in switch["reason"].lower() or "pre-production" in switch["reason"].lower()
        print(f"✓ Master Switch: is_active={switch['is_active']}, reason={switch['reason']}")


class TestAffiliateAdsSystemStatus:
    """Test Affiliate Ads System Status"""
    
    def test_system_status(self):
        """GET /api/v1/affiliate-ads/system/status"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/system/status")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        status = data["system_status"]
        
        # Mode should be PRÉ-PRODUCTION
        assert status["mode"] == "PRÉ-PRODUCTION"
        
        # Master switch should be OFF
        assert status["master_switch"]["is_active"] == False
        
        # Check opportunities by status
        opps = status["opportunities_by_status"]
        # After deactivation: active → paused, pending/checkout → suspended
        assert "paused" in opps or "suspended" in opps
        
        print(f"✓ System status: Mode={status['mode']}, Opportunities={opps}")
    
    def test_opportunities_paused_suspended(self):
        """GET /api/v1/affiliate-ads/opportunities - Check paused/suspended status"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/opportunities")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        opps = data["opportunities"]
        
        # All opportunities should be paused or suspended
        for opp in opps:
            assert opp["status"] in ["paused", "suspended"], f"Unexpected status: {opp['status']}"
        
        # Engel Coolers should be paused (was active)
        engel = next((o for o in opps if o["company_name"] == "Engel Coolers"), None)
        if engel:
            assert engel["status"] == "paused"
            print(f"✓ Engel Coolers: status={engel['status']} (was ACTIVE before deactivation)")
        
        print(f"✓ All {len(opps)} opportunities are paused/suspended")


class TestPriceMultipliers:
    """Test price multipliers for ad spaces"""
    
    def test_premium_multipliers(self):
        """Verify premium spaces have high multipliers"""
        response = requests.get(f"{BASE_URL}/api/v1/ad-spaces/catalog")
        assert response.status_code == 200
        data = response.json()
        
        # Find map_overlay_sponsored (should have 3.5x multiplier)
        map_overlay = next((s for s in data["catalog"] if s["space_id"] == "map_overlay_sponsored"), None)
        assert map_overlay is not None
        assert map_overlay["base_price_multiplier"] == 3.5
        assert map_overlay["priority"] == "premium"
        
        # Find featured_partner_homepage (should have 3.0x multiplier)
        featured_homepage = next((s for s in data["catalog"] if s["space_id"] == "featured_partner_homepage"), None)
        assert featured_homepage is not None
        assert featured_homepage["base_price_multiplier"] == 3.0
        
        print(f"✓ Premium multipliers: map_overlay={map_overlay['base_price_multiplier']}x, featured_homepage={featured_homepage['base_price_multiplier']}x")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
