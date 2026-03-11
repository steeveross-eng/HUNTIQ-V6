"""
Test Suite: Affiliate Ad Automation Engine - COMMANDE 3
========================================================

Tests for the 100% automated ad sales cycle:
1. Trigger automatique à l'activation affilié
2. Email automatique offre publicitaire
3. Portail Checkout
4. Déploiement automatisé
5. Tracking performance
6. Renouvellement

Plus validation en lot des 102 affiliés.
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAffiliateAdsModuleInfo:
    """Test module info endpoint"""
    
    def test_module_info_returns_200(self):
        """GET /api/v1/affiliate-ads/ - Module info"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["module"] == "affiliate_ad_automation_engine"
        assert data["version"] == "1.0.0"
        assert "packages" in data
        assert "placements" in data
        assert "statuses" in data
        
        # Verify packages
        expected_packages = ["1_month", "3_months", "6_months", "12_months"]
        assert data["packages"] == expected_packages
        
        # Verify placements
        expected_placements = [
            "homepage_banner", "sidebar_right", "category_page",
            "article_inline", "footer_banner", "search_results", "map_overlay"
        ]
        assert data["placements"] == expected_placements


class TestBionicDashboard:
    """Test BIONIC revenue dashboard"""
    
    def test_bionic_dashboard_returns_249_revenue(self):
        """GET /api/v1/affiliate-ads/dashboard/bionic - Dashboard revenus (249$ attendus)"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/dashboard/bionic")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "dashboard" in data
        
        dashboard = data["dashboard"]
        assert "totals" in dashboard
        assert "by_status" in dashboard
        assert "by_placement" in dashboard
        
        # Verify revenue is 249$ (from Engel Coolers 3_months package)
        assert dashboard["totals"]["total_revenue"] == 249.0
        assert dashboard["totals"]["total_opportunities"] == 5
        assert dashboard["active_ads_count"] == 1
        
    def test_bionic_dashboard_has_active_status(self):
        """Verify dashboard shows 1 active and 4 pending opportunities"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/dashboard/bionic")
        data = response.json()
        
        by_status = data["dashboard"]["by_status"]
        assert by_status.get("active", 0) == 1
        assert by_status.get("pending", 0) == 4


class TestOpportunities:
    """Test ad opportunities endpoints"""
    
    def test_get_all_opportunities(self):
        """GET /api/v1/affiliate-ads/opportunities - 5 opportunités"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/opportunities")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "opportunities" in data
        assert "pagination" in data
        
        # Verify 5 opportunities exist
        assert data["pagination"]["total"] == 5
        assert len(data["opportunities"]) == 5
        
    def test_opportunities_have_required_fields(self):
        """Verify opportunities have all required fields"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/opportunities")
        data = response.json()
        
        for opp in data["opportunities"]:
            assert "opportunity_id" in opp
            assert "affiliate_id" in opp
            assert "company_name" in opp
            assert "status" in opp
            assert "checkout_token" in opp
            assert "checkout_url" in opp
            
    def test_filter_opportunities_by_status(self):
        """GET /api/v1/affiliate-ads/opportunities?status=active"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/opportunities?status=active")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        # All returned opportunities should be active
        for opp in data["opportunities"]:
            assert opp["status"] == "active"
            
    def test_get_active_opportunity_engel_coolers(self):
        """Verify Engel Coolers opportunity is ACTIVE with 249$ and 3 months"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/opportunities?status=active")
        data = response.json()
        
        active_opps = data["opportunities"]
        assert len(active_opps) == 1
        
        engel = active_opps[0]
        assert engel["company_name"] == "Engel Coolers"
        assert engel["selected_package"] == "3_months"
        assert engel["selected_placement"] == "sidebar_right"
        assert engel["final_price"] == 249.0
        assert engel["duration_days"] == 90
        assert engel["payment_status"] == "completed"


class TestCheckoutPortal:
    """Test checkout portal endpoints"""
    
    def test_get_checkout_page_valid_token(self):
        """GET /api/v1/affiliate-ads/checkout/{token} - Page checkout"""
        # First get a valid checkout token from opportunities
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/opportunities")
        data = response.json()
        
        # Find a pending opportunity with checkout token
        pending_opps = [o for o in data["opportunities"] if o["status"] == "pending"]
        if pending_opps:
            checkout_token = pending_opps[0]["checkout_token"]
            
            checkout_response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/checkout/{checkout_token}")
            assert checkout_response.status_code == 200
            
            checkout_data = checkout_response.json()
            assert checkout_data["success"] is True
            assert "checkout" in checkout_data
            assert "packages" in checkout_data
            assert "placements" in checkout_data
            
            # Verify packages pricing
            packages = checkout_data["packages"]
            assert len(packages) == 4
            
            # Find 3_months package and verify price
            three_months = next((p for p in packages if p["id"] == "3_months"), None)
            assert three_months is not None
            assert three_months["price"] == 249.0
            assert three_months["discount"] == 15
            assert three_months["duration_days"] == 90
            
    def test_checkout_invalid_token_returns_404(self):
        """GET /api/v1/affiliate-ads/checkout/{invalid_token} - 404"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/checkout/invalid-token-12345")
        assert response.status_code == 404
        
    def test_submit_checkout(self):
        """POST /api/v1/affiliate-ads/checkout/{token}/submit - Soumettre checkout"""
        # Get a pending opportunity
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/opportunities?status=pending")
        data = response.json()
        
        if data["opportunities"]:
            checkout_token = data["opportunities"][0]["checkout_token"]
            
            # Submit checkout
            checkout_data = {
                "package": "1_month",
                "placement": "footer_banner",
                "auto_renew": False
            }
            
            submit_response = requests.post(
                f"{BASE_URL}/api/v1/affiliate-ads/checkout/{checkout_token}/submit",
                json=checkout_data
            )
            
            # Should succeed or return payment_pending status
            assert submit_response.status_code == 200
            result = submit_response.json()
            assert result["success"] is True
            assert "summary" in result
            assert "payment_url" in result


class TestPaymentProcessing:
    """Test payment processing endpoints"""
    
    def test_payment_endpoint_exists(self):
        """POST /api/v1/affiliate-ads/pay/{id} - Paiement endpoint exists"""
        # Use a non-existent ID to verify endpoint exists
        response = requests.post(
            f"{BASE_URL}/api/v1/affiliate-ads/pay/non-existent-id",
            json={"payment_method": "stripe"}
        )
        # Should return 404 for non-existent opportunity, not 405 or 500
        assert response.status_code == 404
        
    def test_payment_requires_valid_status(self):
        """Verify payment only works for payment_pending status"""
        # Get the active opportunity (already paid)
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/opportunities?status=active")
        data = response.json()
        
        if data["opportunities"]:
            opp_id = data["opportunities"][0]["opportunity_id"]
            
            # Try to pay again - should fail
            pay_response = requests.post(
                f"{BASE_URL}/api/v1/affiliate-ads/pay/{opp_id}",
                json={"payment_method": "stripe"}
            )
            
            assert pay_response.status_code == 200
            result = pay_response.json()
            # Should indicate invalid status
            assert result["success"] is False or "error" in result


class TestDeployedAds:
    """Test deployed ads endpoints"""
    
    def test_get_deployed_ads(self):
        """GET /api/v1/affiliate-ads/deployed - Publicités déployées"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/deployed")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "ads" in data
        assert "count" in data
        
        # Should have 1 deployed ad (Engel Coolers)
        assert data["count"] == 1
        
    def test_deployed_ad_has_correct_data(self):
        """Verify deployed ad has correct company and placement"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/deployed")
        data = response.json()
        
        ads = data["ads"]
        assert len(ads) == 1
        
        ad = ads[0]
        assert ad["company_name"] == "Engel Coolers"
        assert ad["placement"] == "sidebar_right"
        assert ad["is_active"] is True
        assert "campaign_start" in ad
        assert "campaign_end" in ad
        
    def test_get_ads_by_placement(self):
        """GET /api/v1/affiliate-ads/deployed/by-placement/sidebar_right"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/deployed/by-placement/sidebar_right")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["placement"] == "sidebar_right"
        assert data["count"] >= 1


class TestTracking:
    """Test impression and click tracking"""
    
    def test_track_impression(self):
        """POST /api/v1/affiliate-ads/track/impression - Tracking"""
        # Get a deployed ad ID
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/deployed")
        data = response.json()
        
        if data["ads"]:
            ad_id = data["ads"][0]["ad_id"]
            
            track_response = requests.post(
                f"{BASE_URL}/api/v1/affiliate-ads/track/impression",
                json={"ad_id": ad_id}
            )
            
            assert track_response.status_code == 200
            result = track_response.json()
            assert result["success"] is True
            
    def test_track_click(self):
        """POST /api/v1/affiliate-ads/track/click - Tracking clics"""
        # Get a deployed ad ID
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/deployed")
        data = response.json()
        
        if data["ads"]:
            ad_id = data["ads"][0]["ad_id"]
            
            track_response = requests.post(
                f"{BASE_URL}/api/v1/affiliate-ads/track/click",
                json={"ad_id": ad_id}
            )
            
            assert track_response.status_code == 200
            result = track_response.json()
            assert result["success"] is True


class TestRenewals:
    """Test renewal system"""
    
    def test_get_pending_renewals(self):
        """GET /api/v1/affiliate-ads/renewals/pending - Renouvellements"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/renewals/pending")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "pending_renewals" in data
        assert "count" in data
        
        # Currently no renewals pending (campaign just started)
        assert data["count"] == 0


class TestAffiliateSwitchBulkValidate:
    """Test affiliate switch bulk validation"""
    
    def test_affiliate_switch_dashboard_shows_102_active(self):
        """GET /api/v1/affiliate-switch/dashboard - 102 actifs"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-switch/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        dashboard = data["dashboard"]
        totals = dashboard["totals"]
        
        # Verify 102 active affiliates
        assert totals["by_status"]["active"] == 102
        assert dashboard["switches"]["on"] == 102
        
    def test_bulk_validate_endpoint_exists(self):
        """POST /api/v1/affiliate-switch/bulk/validate - Validation lot"""
        # Test with empty config to verify endpoint exists
        response = requests.post(
            f"{BASE_URL}/api/v1/affiliate-switch/bulk/validate",
            json={
                "affiliate_ids": [],
                "steps": ["identity"],
                "auto_activate": False,
                "validator": "test"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "validated_count" in data


class TestPerformanceTracking:
    """Test performance tracking endpoints"""
    
    def test_get_ad_performance(self):
        """GET /api/v1/affiliate-ads/performance/{opportunity_id}"""
        # Get active opportunity
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/opportunities?status=active")
        data = response.json()
        
        if data["opportunities"]:
            opp_id = data["opportunities"][0]["opportunity_id"]
            
            perf_response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/performance/{opp_id}")
            assert perf_response.status_code == 200
            
            perf_data = perf_response.json()
            assert perf_data["success"] is True
            assert "performance" in perf_data
            
            performance = perf_data["performance"]
            assert "impressions" in performance
            assert "clicks" in performance
            assert "ctr" in performance


class TestOpportunityDetails:
    """Test opportunity detail endpoint"""
    
    def test_get_opportunity_details(self):
        """GET /api/v1/affiliate-ads/opportunities/{opportunity_id}"""
        # Get an opportunity
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/opportunities")
        data = response.json()
        
        if data["opportunities"]:
            opp_id = data["opportunities"][0]["opportunity_id"]
            
            detail_response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/opportunities/{opp_id}")
            assert detail_response.status_code == 200
            
            detail_data = detail_response.json()
            assert detail_data["success"] is True
            assert "opportunity" in detail_data
            assert "logs" in detail_data
            
    def test_opportunity_not_found_returns_404(self):
        """GET /api/v1/affiliate-ads/opportunities/{invalid_id} - 404"""
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/opportunities/invalid-id-12345")
        assert response.status_code == 404


class TestPricingStructure:
    """Test pricing structure is correct"""
    
    def test_package_pricing(self):
        """Verify package pricing: 1_month=99$, 3_months=249$, 6_months=449$, 12_months=799$"""
        # Get checkout page to see pricing
        response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/opportunities?status=pending")
        data = response.json()
        
        if data["opportunities"]:
            checkout_token = data["opportunities"][0]["checkout_token"]
            
            checkout_response = requests.get(f"{BASE_URL}/api/v1/affiliate-ads/checkout/{checkout_token}")
            checkout_data = checkout_response.json()
            
            packages = {p["id"]: p for p in checkout_data["packages"]}
            
            assert packages["1_month"]["price"] == 99.0
            assert packages["3_months"]["price"] == 249.0
            assert packages["6_months"]["price"] == 449.0
            assert packages["12_months"]["price"] == 799.0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
