"""
Test Admin Hotspots & Networking APIs - Phase 4 Migration
=========================================================

Tests for:
- Hotspots Admin: Dashboard, Listings, Pricing, Regions, Owners, Renters, Agreements
- Networking Admin: Dashboard, Posts, Groups, Leads, Referrals, Wallets
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestHotspotsAdminDashboard:
    """Hotspots Dashboard API tests"""
    
    def test_hotspots_dashboard_returns_success(self):
        """GET /api/v1/admin/hotspots/dashboard - Returns dashboard stats"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/hotspots/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "stats" in data
        
        # Verify stats structure
        stats = data["stats"]
        assert "listings" in stats
        assert "users" in stats
        assert "agreements" in stats
        assert "revenue" in stats
        assert "activity" in stats
        
        # Verify listings sub-structure
        assert "total" in stats["listings"]
        assert "active" in stats["listings"]
        assert "pending" in stats["listings"]
        assert "featured" in stats["listings"]
        
        # Verify users sub-structure
        assert "owners" in stats["users"]
        assert "renters" in stats["users"]
        assert "premium_renters" in stats["users"]


class TestHotspotsAdminListings:
    """Hotspots Listings API tests"""
    
    def test_hotspots_listings_returns_success(self):
        """GET /api/v1/admin/hotspots/listings - Returns listings list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/hotspots/listings")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "total" in data
        assert "status_counts" in data
        assert "listings" in data
        assert isinstance(data["listings"], list)
        
        # Verify status_counts structure
        status_counts = data["status_counts"]
        expected_statuses = ["draft", "pending", "active", "rented", "expired", "suspended"]
        for status in expected_statuses:
            assert status in status_counts
    
    def test_hotspots_listings_with_status_filter(self):
        """GET /api/v1/admin/hotspots/listings?status=active - Filters by status"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/hotspots/listings?status=active")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
    
    def test_hotspots_listings_with_limit(self):
        """GET /api/v1/admin/hotspots/listings?limit=10 - Limits results"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/hotspots/listings?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True


class TestHotspotsAdminPricing:
    """Hotspots Pricing API tests"""
    
    def test_hotspots_pricing_returns_success(self):
        """GET /api/v1/admin/hotspots/pricing - Returns pricing configuration"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/hotspots/pricing")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "pricing" in data
        
        # Verify pricing structure
        pricing = data["pricing"]
        expected_keys = [
            "listing_basic", "listing_featured_7", "listing_featured_30",
            "boost_24h", "badge_premium", "send_to_hunters", "generate_agreement",
            "ai_analysis", "renter_basic", "renter_pro", "renter_vip"
        ]
        for key in expected_keys:
            assert key in pricing
            assert "price" in pricing[key]
            assert "name" in pricing[key]


class TestHotspotsAdminRegions:
    """Hotspots Regions API tests"""
    
    def test_hotspots_regions_returns_success(self):
        """GET /api/v1/admin/hotspots/regions - Returns regions stats"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/hotspots/regions")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "regions" in data
        assert isinstance(data["regions"], list)


class TestHotspotsAdminOwners:
    """Hotspots Owners API tests"""
    
    def test_hotspots_owners_returns_success(self):
        """GET /api/v1/admin/hotspots/owners - Returns owners list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/hotspots/owners")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "total" in data
        assert "owners" in data
        assert isinstance(data["owners"], list)


class TestHotspotsAdminRenters:
    """Hotspots Renters API tests"""
    
    def test_hotspots_renters_returns_success(self):
        """GET /api/v1/admin/hotspots/renters - Returns renters list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/hotspots/renters")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "total" in data
        assert "tier_counts" in data
        assert "renters" in data
        
        # Verify tier_counts structure
        tier_counts = data["tier_counts"]
        expected_tiers = ["free", "basic", "pro", "vip"]
        for tier in expected_tiers:
            assert tier in tier_counts
    
    def test_hotspots_renters_with_tier_filter(self):
        """GET /api/v1/admin/hotspots/renters?subscription_tier=pro - Filters by tier"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/hotspots/renters?subscription_tier=pro")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True


class TestHotspotsAdminAgreements:
    """Hotspots Agreements API tests"""
    
    def test_hotspots_agreements_returns_success(self):
        """GET /api/v1/admin/hotspots/agreements - Returns agreements list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/hotspots/agreements")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "total" in data
        assert "status_counts" in data
        assert "agreements" in data
        
        # Verify status_counts structure
        status_counts = data["status_counts"]
        expected_statuses = ["draft", "pending_owner", "pending_renter", "signed", "cancelled", "completed", "disputed"]
        for status in expected_statuses:
            assert status in status_counts
    
    def test_hotspots_agreements_with_status_filter(self):
        """GET /api/v1/admin/hotspots/agreements?status=signed - Filters by status"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/hotspots/agreements?status=signed")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True


class TestNetworkingAdminDashboard:
    """Networking Dashboard API tests"""
    
    def test_networking_dashboard_returns_success(self):
        """GET /api/v1/admin/networking/dashboard - Returns dashboard stats"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/networking/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "stats" in data
        
        # Verify stats structure
        stats = data["stats"]
        assert "posts" in stats
        assert "leads" in stats
        assert "contacts" in stats
        assert "groups" in stats
        assert "referrals" in stats
        assert "wallets" in stats
        
        # Verify posts sub-structure
        assert "total" in stats["posts"]
        assert "this_week" in stats["posts"]
        
        # Verify referrals sub-structure
        assert "total" in stats["referrals"]
        assert "pending" in stats["referrals"]
        assert "rewarded" in stats["referrals"]


class TestNetworkingAdminPosts:
    """Networking Posts API tests"""
    
    def test_networking_posts_returns_success(self):
        """GET /api/v1/admin/networking/posts - Returns posts list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/networking/posts")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "total" in data
        assert "posts" in data
        assert isinstance(data["posts"], list)
    
    def test_networking_posts_with_visibility_filter(self):
        """GET /api/v1/admin/networking/posts?visibility=public - Filters by visibility"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/networking/posts?visibility=public")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True


class TestNetworkingAdminGroups:
    """Networking Groups API tests"""
    
    def test_networking_groups_returns_success(self):
        """GET /api/v1/admin/networking/groups - Returns groups list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/networking/groups")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "total" in data
        assert "type_counts" in data
        assert "groups" in data
        
        # Verify type_counts structure
        type_counts = data["type_counts"]
        expected_types = ["hunting_club", "family", "business", "friends", "custom"]
        for group_type in expected_types:
            assert group_type in type_counts
    
    def test_networking_groups_with_privacy_filter(self):
        """GET /api/v1/admin/networking/groups?privacy=public - Filters by privacy"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/networking/groups?privacy=public")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True


class TestNetworkingAdminLeads:
    """Networking Leads API tests"""
    
    def test_networking_leads_returns_success(self):
        """GET /api/v1/admin/networking/leads - Returns leads list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/networking/leads")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "total" in data
        assert "status_counts" in data
        assert "values" in data
        assert "leads" in data
        
        # Verify status_counts structure
        status_counts = data["status_counts"]
        expected_statuses = ["new", "contacted", "interested", "negotiating", "converted", "lost"]
        for status in expected_statuses:
            assert status in status_counts
        
        # Verify values structure
        values = data["values"]
        assert "total_estimated" in values
        assert "total_actual" in values
    
    def test_networking_leads_with_status_filter(self):
        """GET /api/v1/admin/networking/leads?status=new - Filters by status"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/networking/leads?status=new")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True


class TestNetworkingAdminReferrals:
    """Networking Referrals API tests"""
    
    def test_networking_referrals_returns_success(self):
        """GET /api/v1/admin/networking/referrals - Returns referrals list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/networking/referrals")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "total" in data
        assert "status_counts" in data
        assert "total_rewards_distributed" in data
        assert "referrals" in data
        
        # Verify status_counts structure
        status_counts = data["status_counts"]
        expected_statuses = ["pending", "verified", "rewarded", "expired"]
        for status in expected_statuses:
            assert status in status_counts
    
    def test_networking_referrals_with_status_filter(self):
        """GET /api/v1/admin/networking/referrals?status=pending - Filters by status"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/networking/referrals?status=pending")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
    
    def test_networking_pending_referrals_returns_success(self):
        """GET /api/v1/admin/networking/referrals/pending - Returns pending referrals"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/networking/referrals/pending")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "total" in data
        assert "referrals" in data


class TestNetworkingAdminWallets:
    """Networking Wallets API tests"""
    
    def test_networking_wallets_returns_success(self):
        """GET /api/v1/admin/networking/wallets - Returns wallets list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/networking/wallets")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "total" in data
        assert "total_credits_circulation" in data
        assert "total_earned_all_time" in data
        assert "wallets" in data
        assert isinstance(data["wallets"], list)


class TestNetworkingAdminReferralCodes:
    """Networking Referral Codes API tests"""
    
    def test_networking_referral_codes_returns_success(self):
        """GET /api/v1/admin/networking/referral-codes - Returns referral codes list"""
        response = requests.get(f"{BASE_URL}/api/v1/admin/networking/referral-codes")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "total" in data
        assert "codes" in data
        assert isinstance(data["codes"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
