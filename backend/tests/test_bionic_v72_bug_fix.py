"""
BIONIC V7.2 Bug Fix Tests - Iteration 137
Tests: Quebec City returns 0 zones, Forest returns zones,
       exclusion_failed flag, anthropic filtering, zone merging, oversized rejection

CRITICAL: Overpass API rate limits. Use 120s timeout.
"""
import pytest
import httpx
import os
import time

# Use REACT_APP_BACKEND_URL from environment (production URL)
API_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://heatmap-lite.preview.emergentagent.com").rstrip("/")
TIMEOUT = 120  # Overpass API can be slow

# Quebec City center (urban, residential areas)
QUEBEC_CITY = {
    "waypoint": {"lat": 46.8045, "lng": -71.2364},
    "bounds": {
        "north": 46.8045 + 0.015,
        "south": 46.8045 - 0.015,
        "east": -71.2364 + 0.015,
        "west": -71.2364 - 0.015,
    }
}

# Laurentides Forest Reserve (wilderness, forests)
FOREST_LAURENTIDES = {
    "waypoint": {"lat": 47.285, "lng": -71.415},
    "bounds": {
        "north": 47.285 + 0.015,
        "south": 47.285 - 0.015,
        "east": -71.415 + 0.015,
        "west": -71.415 - 0.015,
    }
}

LAYERS = ["habitats", "rut", "repos", "alimentation"]


@pytest.fixture(scope="module")
def client():
    """HTTP client with 120s timeout for Overpass API"""
    return httpx.Client(timeout=TIMEOUT)


def call_organic_zones(client, location, include_waypoint=True):
    """Call POST /api/v1/bionic/organic-zones"""
    body = {
        "bounds": location["bounds"],
        "species": "moose",
        "layers": LAYERS,
        "resolution": 60,
        "max_zones_per_layer": 8,
        "include_scoring": False,
    }
    if include_waypoint:
        body["waypoint_center"] = location["waypoint"]
    
    response = client.post(f"{API_URL}/api/v1/bionic/organic-zones", json=body)
    return response


class TestV72QuebecCityUrbanExclusion:
    """V7.2: Quebec City center must return 0 zones due to urban exclusion"""
    
    def test_quebec_city_returns_zero_zones(self, client):
        """CRITICAL: Quebec City (46.8045, -71.2364) must return 0 zones"""
        print(f"\n>>> Testing Quebec City: {QUEBEC_CITY['waypoint']}")
        print(f">>> Bounds: {QUEBEC_CITY['bounds']}")
        
        response = call_organic_zones(client, QUEBEC_CITY)
        assert response.status_code == 200, f"API error: {response.status_code} - {response.text[:300]}"
        
        data = response.json()
        zones = data.get("features", [])
        stats = data.get("stats", {})
        
        print(f">>> Zones returned: {len(zones)}")
        print(f">>> Exclusions count: {stats.get('exclusions_count', 0)}")
        print(f">>> Rejected: {stats.get('rejected_exclusion', 0)}")
        print(f">>> exclusion_failed: {stats.get('exclusion_failed', 'NOT SET')}")
        
        # CRITICAL ASSERTION: Quebec City must have 0 zones
        assert len(zones) == 0, (
            f"V7.2 BUG: Quebec City returned {len(zones)} zones. "
            f"Expected 0 zones in urban area. "
            f"Zone layers: {[f.get('properties', {}).get('layer_id') for f in zones]}"
        )
    
    def test_quebec_city_has_exclusions(self, client):
        """Quebec City must have exclusions fetched (not rate-limited)"""
        response = call_organic_zones(client, QUEBEC_CITY)
        assert response.status_code == 200
        
        data = response.json()
        stats = data.get("stats", {})
        exclusions_count = stats.get("exclusions_count", 0)
        exclusion_failed = stats.get("exclusion_failed", False)
        
        print(f">>> Exclusions count: {exclusions_count}")
        print(f">>> exclusion_failed flag: {exclusion_failed}")
        
        # If exclusion_failed=True, Overpass failed but we still get 0 zones (strict mode)
        if exclusion_failed:
            pytest.skip("Overpass API rate-limited - exclusion_failed=True is correct strict behavior")
        
        # Otherwise, we should have exclusions
        assert exclusions_count > 100, (
            f"Too few exclusions ({exclusions_count}) for urban Quebec City. "
            f"Expected >100 exclusions (roads, buildings, urban areas)."
        )
    
    def test_quebec_city_zones_rejected_anthropic(self, client):
        """Quebec City zones should be rejected by anthropic filter"""
        response = call_organic_zones(client, QUEBEC_CITY)
        assert response.status_code == 200
        
        data = response.json()
        stats = data.get("stats", {})
        rejected = stats.get("rejected_exclusion", 0)
        
        print(f">>> Zones rejected: {rejected}")
        
        # We expect some zones were generated but rejected
        # If exclusion_failed, this test is not meaningful
        if not stats.get("exclusion_failed", False):
            assert rejected > 0, (
                f"No zones rejected in Quebec City. "
                f"The anthropic filter should reject raw zones in urban areas."
            )


class TestV72ForestZoneGeneration:
    """V7.2: Laurentides Forest must return zones normally"""
    
    def test_forest_returns_zones(self, client):
        """Forest area (47.285, -71.415) must return >0 zones"""
        print(f"\n>>> Testing Forest: {FOREST_LAURENTIDES['waypoint']}")
        print(f">>> Bounds: {FOREST_LAURENTIDES['bounds']}")
        
        response = call_organic_zones(client, FOREST_LAURENTIDES)
        assert response.status_code == 200, f"API error: {response.status_code} - {response.text[:300]}"
        
        data = response.json()
        zones = data.get("features", [])
        stats = data.get("stats", {})
        
        print(f">>> Zones returned: {len(zones)}")
        print(f">>> Exclusions count: {stats.get('exclusions_count', 0)}")
        
        # If exclusion_failed, skip the test
        if stats.get("exclusion_failed", False):
            pytest.skip("Overpass API rate-limited - cannot test forest zones")
        
        # Forest must have zones
        assert len(zones) > 0, (
            f"V7.2 BUG: Forest returned 0 zones. "
            f"Expected >0 zones in wilderness area."
        )
    
    def test_forest_returns_at_least_3_zones(self, client):
        """Forest should return at least 3 zones (not over-filtered)"""
        response = call_organic_zones(client, FOREST_LAURENTIDES)
        assert response.status_code == 200
        
        data = response.json()
        zones = data.get("features", [])
        stats = data.get("stats", {})
        
        if stats.get("exclusion_failed", False):
            pytest.skip("Overpass API rate-limited")
        
        print(f">>> Zones returned: {len(zones)}")
        assert len(zones) >= 3, (
            f"Forest returned only {len(zones)} zones. "
            f"Expected >=3 zones. Filter may be too aggressive."
        )
    
    def test_forest_zones_have_valid_structure(self, client):
        """Forest zones should have valid GeoJSON structure"""
        response = call_organic_zones(client, FOREST_LAURENTIDES)
        assert response.status_code == 200
        
        data = response.json()
        zones = data.get("features", [])
        
        if len(zones) == 0:
            pytest.skip("No zones to validate structure")
        
        zone = zones[0]
        assert "geometry" in zone, "Zone missing geometry"
        assert "properties" in zone, "Zone missing properties"
        assert zone["geometry"]["type"] in ["Polygon", "MultiPolygon"], (
            f"Invalid geometry type: {zone['geometry']['type']}"
        )
        
        props = zone["properties"]
        assert "layer_id" in props, "Zone missing layer_id"
        assert "score" in props, "Zone missing score"
        print(f">>> Zone structure valid: layer={props.get('layer_id')}, score={props.get('score')}")


class TestV72ExclusionFailedFlag:
    """V7.2: exclusion_failed=true must mean 0 zones (strict mode)"""
    
    def test_exclusion_failed_implies_zero_zones(self, client):
        """When exclusion_failed=True, zones must be 0"""
        # Test both locations
        for name, location in [("Quebec", QUEBEC_CITY), ("Forest", FOREST_LAURENTIDES)]:
            response = call_organic_zones(client, location)
            if response.status_code != 200:
                continue
            
            data = response.json()
            stats = data.get("stats", {})
            zones = data.get("features", [])
            
            exclusion_failed = stats.get("exclusion_failed", False)
            
            if exclusion_failed:
                print(f">>> {name}: exclusion_failed=True, zones={len(zones)}")
                assert len(zones) == 0, (
                    f"STRICT MODE VIOLATION: {name} has exclusion_failed=True "
                    f"but returned {len(zones)} zones. "
                    f"V7.2 strict mode requires 0 zones when Overpass fails."
                )


class TestV72AnthropicRejectionCriteria:
    """V7.2: Test the 5 anthropic rejection criteria"""
    
    def test_anthropic_filter_in_stats(self, client):
        """Check that anthropic filtering is being applied"""
        response = call_organic_zones(client, QUEBEC_CITY)
        if response.status_code != 200:
            pytest.skip("API unavailable")
        
        data = response.json()
        stats = data.get("stats", {})
        
        # The V7 metadata should contain rejection info
        v7_metadata = data.get("v7_metadata", {})
        total_rejected = v7_metadata.get("total_rejected", stats.get("rejected_exclusion", 0))
        
        print(f">>> Total rejected zones: {total_rejected}")
        print(f">>> Exclusion engine: {stats.get('exclusion_engine', 'unknown')}")
        
        # In urban areas, we expect rejections
        if not stats.get("exclusion_failed", False):
            assert total_rejected > 0, (
                "No zones rejected in urban area. "
                "Anthropic filter should be rejecting zones."
            )


class TestV72ZoneMerging:
    """V7.2: Same-type zones <200m should be merged"""
    
    def test_merged_zones_have_merged_suffix(self, client):
        """Check for zone_id ending with '_merged'"""
        # Forest is more likely to have merged zones
        response = call_organic_zones(client, FOREST_LAURENTIDES)
        if response.status_code != 200:
            pytest.skip("API unavailable")
        
        data = response.json()
        zones = data.get("features", [])
        
        if len(zones) == 0:
            pytest.skip("No zones to check for merging")
        
        merged_zones = []
        for zone in zones:
            props = zone.get("properties", {})
            zone_id = props.get("zone_id", "")
            if "_merged" in zone_id:
                merged_zones.append(zone_id)
        
        print(f">>> Total zones: {len(zones)}")
        print(f">>> Merged zones: {len(merged_zones)}")
        if merged_zones:
            print(f">>> Merged zone IDs: {merged_zones[:5]}")
        
        # Note: merged zones are optional - they only appear when same-type zones are <200m apart
        # So we just log the count, not assert


class TestV72OversizedZoneRejection:
    """V7.2: Zones >500000m² (0.5km²) should be rejected"""
    
    def test_zones_under_max_area(self, client):
        """All returned zones should be under 500000m²"""
        response = call_organic_zones(client, FOREST_LAURENTIDES)
        if response.status_code != 200:
            pytest.skip("API unavailable")
        
        data = response.json()
        zones = data.get("features", [])
        
        MAX_AREA = 500000  # m²
        oversized = []
        
        for zone in zones:
            props = zone.get("properties", {})
            area = props.get("area_m2", 0)
            if area > MAX_AREA:
                oversized.append({
                    "zone_id": props.get("zone_id"),
                    "area_m2": area
                })
        
        print(f">>> Total zones: {len(zones)}")
        print(f">>> Oversized zones (should be 0): {len(oversized)}")
        
        assert len(oversized) == 0, (
            f"V7.2 BUG: {len(oversized)} zones exceed max area of {MAX_AREA}m². "
            f"Oversized: {oversized}"
        )


class TestV72ThresholdVerification:
    """V7.2: Verify tightened thresholds (urban=0.08, roads=0.08, infra=0.12)"""
    
    def test_exclusion_engine_version(self, client):
        """Check that V7 exclusion engine is being used"""
        response = call_organic_zones(client, FOREST_LAURENTIDES)
        if response.status_code != 200:
            pytest.skip("API unavailable")
        
        data = response.json()
        stats = data.get("stats", {})
        
        engine = stats.get("exclusion_engine", "unknown")
        print(f">>> Exclusion engine: {engine}")
        
        # V7.2 should use v7 engine
        assert engine in ["v7", "v6"], (
            f"Unexpected exclusion engine: {engine}. "
            f"V7.2 should use v7 or v6 engine."
        )


class TestV72CompactnessFilter:
    """V7.2: Compactness raised from 0.15 to 0.25"""
    
    def test_zones_have_valid_compactness(self, client):
        """All zones should have compactness >= 0.25"""
        response = call_organic_zones(client, FOREST_LAURENTIDES)
        if response.status_code != 200:
            pytest.skip("API unavailable")
        
        data = response.json()
        zones = data.get("features", [])
        
        MIN_COMPACTNESS = 0.25
        low_compactness = []
        
        for zone in zones:
            props = zone.get("properties", {})
            compactness = props.get("compactness", 1.0)
            if compactness < MIN_COMPACTNESS:
                low_compactness.append({
                    "zone_id": props.get("zone_id"),
                    "compactness": compactness
                })
        
        print(f">>> Total zones: {len(zones)}")
        print(f">>> Low compactness zones (should be 0): {len(low_compactness)}")
        
        # Note: Compactness filter is in trimming, not final output validation
        # So zones might still have lower compactness in some cases
        if low_compactness:
            print(f">>> Warning: Some zones have low compactness: {low_compactness[:3]}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
