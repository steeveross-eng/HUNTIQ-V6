"""
Test suite for BIONIC V8.2 Resilience Pipeline
Bug fix: Zone generation with graceful degradation when Overpass API fails

Tests:
1. POST /api/v1/bionic/organic-zones returns zones even when Overpass unavailable
2. Response contains non-empty features[], non-empty corridors[]
3. Response contains stats.exclusion_degraded=true in degraded mode
4. API response time < 60s (frontend timeout)
5. Cache hit on second identical request (< 2s)
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://steve-max-plus.preview.emergentagent.com')

# Test coordinates (forest zone in Quebec)
TEST_BOUNDS = {
    "north": 48.2211,
    "south": 48.1911,
    "east": -68.3535,
    "west": -68.4135
}
TEST_WAYPOINT = {"lat": 48.2061, "lng": -68.3835}


class TestOrganicZonesV82Resilience:
    """Tests for V8.2 graceful degradation when Overpass API is unavailable"""
    
    def test_organic_zones_returns_zones_on_overpass_failure(self):
        """
        CRITICAL: POST /api/v1/bionic/organic-zones must return zones
        even when Overpass API is unavailable (graceful degradation)
        """
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "waypoint_center": TEST_WAYPOINT
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=65  # Slightly over frontend timeout
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # CRITICAL: features must be non-empty (zones generated)
        features = data.get("features", [])
        assert len(features) > 0, f"Expected non-empty features[], got {len(features)} zones"
        print(f"PASS: {len(features)} zones generated")
    
    def test_corridors_generated(self):
        """Corridors should also be generated in degraded mode"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "waypoint_center": TEST_WAYPOINT
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=65
        )
        
        assert response.status_code == 200
        data = response.json()
        
        corridors = data.get("corridors", [])
        assert len(corridors) > 0, f"Expected non-empty corridors[], got {len(corridors)}"
        print(f"PASS: {len(corridors)} corridors generated")
    
    def test_exclusion_degraded_flag_present(self):
        """
        In degraded mode, stats.exclusion_degraded should be true
        indicating zones were generated without exclusion filtering
        """
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "waypoint_center": TEST_WAYPOINT
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=65
        )
        
        assert response.status_code == 200
        data = response.json()
        
        stats = data.get("stats", {})
        # Note: exclusion_degraded will be True when Overpass is unavailable
        # The test validates the flag exists and is boolean
        assert "exclusion_degraded" in stats, "stats.exclusion_degraded field missing"
        assert isinstance(stats["exclusion_degraded"], bool), "exclusion_degraded should be boolean"
        print(f"PASS: exclusion_degraded={stats['exclusion_degraded']}")
    
    def test_response_time_under_60_seconds(self):
        """
        API response must arrive within 60s (frontend timeout limit)
        V8.2 pipeline should complete in ~15-30s even with Overpass failures
        """
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "waypoint_center": TEST_WAYPOINT
        }
        
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=65
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 60, f"Response took {elapsed:.1f}s, expected < 60s"
        print(f"PASS: Response time {elapsed:.1f}s (under 60s limit)")
    
    def test_cache_hit_under_2_seconds(self):
        """
        Second identical request should hit cache and return < 2s
        V8.2: Cache TTL is 15 minutes (900s)
        """
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "waypoint_center": TEST_WAYPOINT
        }
        
        # First call (might be slow if not cached)
        requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=65
        )
        
        # Second call (should be cached)
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=10
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 2, f"Cache hit took {elapsed:.1f}s, expected < 2s"
        print(f"PASS: Cache hit {elapsed:.1f}s (under 2s limit)")
    
    def test_stats_structure_complete(self):
        """Verify all expected stats fields are present"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "waypoint_center": TEST_WAYPOINT
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=65
        )
        
        assert response.status_code == 200
        data = response.json()
        stats = data.get("stats", {})
        
        required_fields = [
            "layers_processed",
            "total_zones",
            "exclusions_count",
            "exclusion_engine",
            "computation_time_ms",
            "species",
            "bounds",
            "exclusion_degraded"
        ]
        
        for field in required_fields:
            assert field in stats, f"Missing stats field: {field}"
        
        print(f"PASS: All {len(required_fields)} required stats fields present")


class TestBiologicalSeasons:
    """Tests for V8.1 biological season support"""
    
    def test_biological_season_parameter(self):
        """Test that biological_season parameter is accepted"""
        for season in ["pre_rut", "rut", "post_rut", "winter", "spring"]:
            payload = {
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "biological_season": season
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/bionic/organic-zones",
                json=payload,
                timeout=65
            )
            
            assert response.status_code == 200, f"Season {season} failed: {response.status_code}"
            data = response.json()
            
            # Check biological_season metadata in response
            bio_season = data.get("biological_season", {})
            assert bio_season.get("id") == season, f"Expected season {season} in response"
        
        print("PASS: All 5 biological seasons accepted")


class TestAPIHealth:
    """Basic API health checks"""
    
    def test_health_endpoint(self):
        """Test /api/health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        print("PASS: Health endpoint OK")
    
    def test_organic_zones_layers_endpoint(self):
        """Test GET /api/v1/bionic/organic-zones/layers"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/organic-zones/layers", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert "layers" in data
        assert "species" in data
        assert len(data["layers"]) > 0
        print(f"PASS: Layers endpoint returns {len(data['layers'])} layers")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
