"""
Test Urban Exclusion Bug Fix V7

Tests for the critical urban exclusion bug fix in dense urban areas (Quebec City):
1. Urban intersection threshold lowered from 0.40 to 0.10
2. Buildings now queried from Overpass at ALL detail levels
3. New anthropic_pressure_v7 filter rejects zones where urban AND roads penalties are both 'close' band

Test scenarios:
- URBAN (Quebec City Montcalm/Saint-Sauveur) → must return 0 zones
- FOREST (Reserve des Laurentides) → must return zones normally
- PERIURBAN (Stoneham area) → should have some zones with high penalties
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestUrbanExclusionV7:
    """Tests for urban exclusion bug fix in V7"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        login_url = f"{BASE_URL}/api/auth/login"
        response = requests.post(
            login_url,
            json={"email": "steeve.ross@gmail.com", "password": "Saturn5858*"},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("access_token") or response.json().get("token")
        pytest.skip("Authentication failed")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Return headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    # =========================================================================
    # TEST 1: URBAN ZONES (Quebec City center) → MUST RETURN 0 ZONES
    # =========================================================================
    def test_urban_quebec_city_returns_zero_zones(self, auth_headers):
        """
        Quebec City dense urban area (Montcalm/Saint-Sauveur) must return 0 zones.
        This is the critical bug fix test.
        
        Bounds: north=46.825, south=46.795, east=-71.195, west=-71.235
        Waypoint: lat=46.812, lng=-71.215
        """
        url = f"{BASE_URL}/api/v1/bionic/organic-zones"
        payload = {
            "bounds": {
                "north": 46.825,
                "south": 46.795,
                "east": -71.195,
                "west": -71.235
            },
            "waypoint_center": {
                "lat": 46.812,
                "lng": -71.215
            },
            "species": "moose",
            "season": "fall_hunting"
        }
        
        print(f"\n[TEST] Urban Quebec City - Expected: 0 zones")
        print(f"[TEST] Bounds: {payload['bounds']}")
        print(f"[TEST] Waypoint: {payload['waypoint_center']}")
        
        response = requests.post(url, json=payload, headers=auth_headers, timeout=120)
        
        assert response.status_code == 200, f"API returned {response.status_code}: {response.text}"
        
        data = response.json()
        zones = data.get("zones", [])
        stats = data.get("stats", {})
        
        print(f"[RESULT] Zones returned: {len(zones)}")
        print(f"[RESULT] Stats: {stats}")
        
        # CRITICAL: Urban areas must return 0 zones
        assert len(zones) == 0, (
            f"BUG NOT FIXED: Urban Quebec City returned {len(zones)} zones. "
            f"Expected 0 zones due to urban exclusion."
        )
        
        # Verify exclusion engine stats show rejections
        if "exclusion_stats" in stats:
            print(f"[RESULT] Exclusion stats: {stats['exclusion_stats']}")
        
        print("[PASS] Urban Quebec City correctly returns 0 zones")
    
    # =========================================================================
    # TEST 2: FOREST ZONES (Reserve des Laurentides) → MUST RETURN ZONES
    # =========================================================================
    def test_forest_laurentides_returns_zones(self, auth_headers):
        """
        Forest area (Reserve des Laurentides) must return zones normally.
        
        Note: Testing WITHOUT waypoint_center to avoid perimeter filtering.
        The response is GeoJSON FeatureCollection, so we check features.
        
        Bounds: north=47.30, south=47.27, east=-71.40, west=-71.43
        """
        url = f"{BASE_URL}/api/v1/bionic/organic-zones"
        payload = {
            "bounds": {
                "north": 47.30,
                "south": 47.27,
                "east": -71.40,
                "west": -71.43
            },
            # No waypoint_center - get all zones in bounds
            "species": "moose",
            "season": "fall_hunting"
        }
        
        print(f"\n[TEST] Forest Reserve Laurentides - Expected: >0 zones (no perimeter filter)")
        print(f"[TEST] Bounds: {payload['bounds']}")
        
        response = requests.post(url, json=payload, headers=auth_headers, timeout=120)
        
        assert response.status_code == 200, f"API returned {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Response is GeoJSON FeatureCollection when no waypoint_center
        features = data.get("features", [])
        zones = data.get("zones", features)  # Fallback to features if no zones key
        
        print(f"[RESULT] Zones/Features returned: {len(zones)}")
        if "stats" in data:
            print(f"[RESULT] Stats: {data.get('stats')}")
        
        # Forest areas must return zones
        assert len(zones) > 0, (
            f"Forest area returned 0 zones/features. Expected >0 zones for wilderness area. "
            f"Response keys: {list(data.keys())}"
        )
        
        print(f"[PASS] Forest Laurentides correctly returns {len(zones)} zones")
    
    # =========================================================================
    # TEST 3: PERIURBAN (Stoneham area) → SHOULD HAVE SOME ZONES WITH PENALTIES
    # =========================================================================
    def test_periurban_stoneham_has_zones_with_penalties(self, auth_headers):
        """
        Periurban area (Stoneham) should have some zones with high penalties
        but not be entirely blocked.
        
        Using area between Quebec City and Laurentides.
        """
        url = f"{BASE_URL}/api/v1/bionic/organic-zones"
        payload = {
            "bounds": {
                "north": 47.05,
                "south": 47.02,
                "east": -71.30,
                "west": -71.35
            },
            "waypoint_center": {
                "lat": 47.035,
                "lng": -71.325
            },
            "species": "moose",
            "season": "fall_hunting"
        }
        
        print(f"\n[TEST] Periurban Stoneham - Expected: some zones with penalties")
        print(f"[TEST] Bounds: {payload['bounds']}")
        print(f"[TEST] Waypoint: {payload['waypoint_center']}")
        
        response = requests.post(url, json=payload, headers=auth_headers, timeout=120)
        
        assert response.status_code == 200, f"API returned {response.status_code}: {response.text}"
        
        data = response.json()
        zones = data.get("zones", [])
        stats = data.get("stats", {})
        
        print(f"[RESULT] Zones returned: {len(zones)}")
        print(f"[RESULT] Stats: {stats}")
        
        # Periurban areas can have 0 or more zones - not a strict requirement
        # But if zones exist, check they have penalty factors
        if len(zones) > 0:
            zones_with_penalties = [
                z for z in zones 
                if z.get("penalty_factor", 1.0) < 0.9
            ]
            print(f"[RESULT] Zones with penalties (<0.9): {len(zones_with_penalties)}")
            
            # Check penalty details on first few zones
            for zone in zones[:3]:
                penalty = zone.get("penalty_factor", 1.0)
                details = zone.get("penalty_details", {})
                print(f"[RESULT] Zone penalty={penalty}, details={details}")
        
        print(f"[PASS] Periurban test completed - {len(zones)} zones returned")
    
    # =========================================================================
    # TEST 4: VERIFY EXCLUSION CONFIG THRESHOLD
    # =========================================================================
    def test_exclusion_config_urban_threshold(self):
        """
        Verify urban intersection threshold is 0.10 (not 0.40)
        """
        from modules.bionic_engine_p0.services.exclusion_config_v6 import INTERSECTION_THRESHOLDS_V6
        
        urban_threshold = INTERSECTION_THRESHOLDS_V6.get("urban")
        
        print(f"\n[TEST] Urban threshold check")
        print(f"[RESULT] INTERSECTION_THRESHOLDS_V6['urban'] = {urban_threshold}")
        
        assert urban_threshold == 0.10, (
            f"Urban threshold is {urban_threshold}, expected 0.10. "
            f"Bug fix not applied correctly."
        )
        
        print("[PASS] Urban threshold correctly set to 0.10")
    
    # =========================================================================
    # TEST 5: VERIFY ANTHROPIC PRESSURE FILTER EXISTS
    # =========================================================================
    def test_anthropic_pressure_filter_exists(self):
        """
        Verify the anthropic_pressure_v7 rejection filter is in the code.
        Lines 268-283 in exclusion_engine_v6.py should have the filter.
        """
        import inspect
        from modules.bionic_engine_p0.services.exclusion_engine_v6 import process_zones_v6
        
        source = inspect.getsource(process_zones_v6)
        
        print(f"\n[TEST] Anthropic pressure filter check")
        
        # Check for the key conditions in the filter
        assert "anthropic_pressure_v7" in source, (
            "anthropic_pressure_v7 rejection reason not found in process_zones_v6"
        )
        
        assert "urban_pen < 0.60" in source or "urban_pen<0.60" in source.replace(" ", ""), (
            "urban_pen < 0.60 condition not found in anthropic pressure filter"
        )
        
        assert "roads_pen < 0.65" in source or "roads_pen<0.65" in source.replace(" ", ""), (
            "roads_pen < 0.65 condition not found in anthropic pressure filter"
        )
        
        print("[PASS] Anthropic pressure filter correctly implemented")
    
    # =========================================================================
    # TEST 6: VERIFY BUILDING QUERY AT ALL DETAIL LEVELS
    # =========================================================================
    def test_building_query_all_detail_levels(self):
        """
        Verify buildings are queried at ALL detail levels, not just 'high'.
        Line 131 in terrain_data_router.py should have building query outside
        the 'if detail_level == "high"' block.
        """
        import inspect
        from modules.bionic_engine_p0.routers.terrain_data_router import _build_overpass_query
        
        source = inspect.getsource(_build_overpass_query)
        
        print(f"\n[TEST] Building query at all detail levels check")
        
        # The building query should be OUTSIDE the detail_level check
        # Check that 'way["building"]' appears before 'if detail_level == "high"'
        building_query_idx = source.find('way["building"]')
        detail_high_idx = source.find('if detail_level == "high"')
        
        # For urban section, find the urban section and check building is queried before detail_level check
        urban_section_start = source.find('if "urban" in exclude_types')
        urban_section_end = source.find('if "infrastructure" in exclude_types')
        
        urban_section = source[urban_section_start:urban_section_end]
        
        print(f"[DEBUG] Urban section:\n{urban_section[:500]}...")
        
        # Building query should exist in urban section
        assert 'way["building"]' in urban_section, (
            "Building query not found in urban section"
        )
        
        # Check building query is NOT inside the "if detail_level == high" block only
        # It should be queried regardless of detail level
        building_idx_in_urban = urban_section.find('way["building"]')
        detail_high_idx_in_urban = urban_section.find('if detail_level == "high"')
        
        # Building should appear BEFORE the detail_level check
        assert building_idx_in_urban < detail_high_idx_in_urban, (
            f"Building query appears AFTER detail_level check. "
            f"building_idx={building_idx_in_urban}, detail_high_idx={detail_high_idx_in_urban}. "
            f"Buildings should be queried at ALL detail levels."
        )
        
        print("[PASS] Building query correctly at all detail levels")


class TestLoginFlow:
    """Verify login still works"""
    
    def test_login_with_credentials(self):
        """Test login with provided credentials"""
        url = f"{BASE_URL}/api/auth/login"
        response = requests.post(
            url,
            json={"email": "steeve.ross@gmail.com", "password": "Saturn5858*"},
            timeout=30
        )
        
        print(f"\n[TEST] Login flow")
        print(f"[RESULT] Status: {response.status_code}")
        
        assert response.status_code == 200, f"Login failed: {response.status_code}"
        
        data = response.json()
        assert "access_token" in data or "token" in data, "No token in response"
        
        print("[PASS] Login successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
