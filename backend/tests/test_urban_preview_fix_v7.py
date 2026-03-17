"""
Test BIONIC V7.1 — Urban Preview Fix Verification
Tests the bug fix for zones appearing in dense urban areas (Quebec City center).

ROOT CAUSE: Frontend useZoneOrchestrator.js had a 'preview preservation' bug.
When backend correctly returned 0 zones, client-side preview zones were KEPT on screen.

FIX VERIFIED:
1. Backend: anthropic_pressure_v7 filter rejects zones where urban<0.60 AND roads<0.65
2. Backend: urban threshold lowered to 0.10
3. Frontend: useZoneOrchestrator.js now ALWAYS replaces preview with backend result (even if 0 zones)
4. Frontend: backendVerified flag in cache prevents re-generating preview for known-empty areas
"""
import pytest
import httpx
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://species-network.preview.emergentagent.com")
TIMEOUT = 120  # API calls can take 30-60s due to Overpass API

# Test coordinates per requirements
URBAN_WAYPOINT = {"lat": 46.8045, "lng": -71.2364}  # Quebec City center (Montcalm/Saint-Sauveur)
URBAN_BOUNDS = {"north": 46.8195, "south": 46.7895, "east": -71.2214, "west": -71.2514}

FOREST_WAYPOINT = {"lat": 47.285, "lng": -71.415}  # Reserve des Laurentides
FOREST_BOUNDS = {"north": 47.30, "south": 47.27, "east": -71.40, "west": -71.43}

LAYERS = ["habitats", "rut", "repos", "alimentation"]


@pytest.fixture(scope="module")
def client():
    return httpx.Client(base_url=BASE_URL.rstrip('/'), timeout=TIMEOUT)


def _call_organic_zones(client, bounds, waypoint_center=None):
    """Helper to call the organic-zones endpoint"""
    body = {
        "bounds": bounds,
        "species": "moose",
        "layers": LAYERS,
        "resolution": 60,
        "max_zones_per_layer": 8,
        "include_scoring": False,
    }
    if waypoint_center:
        body["waypoint_center"] = waypoint_center
    resp = client.post("/api/v1/bionic/organic-zones", json=body)
    assert resp.status_code == 200, f"API error: {resp.status_code} {resp.text[:200]}"
    return resp.json()


class TestUrbanPreviewFixV71:
    """Tests for the urban preview preservation bug fix"""
    
    def test_urban_quebec_center_returns_zero_zones(self, client):
        """
        CRITICAL TEST: Waypoint 46.8045, -71.2364 (Quebec center) MUST return 0 zones.
        This was the bug location - preview zones were incorrectly showing.
        """
        data = _call_organic_zones(client, URBAN_BOUNDS, URBAN_WAYPOINT)
        zones = data.get("features", [])
        
        assert len(zones) == 0, (
            f"BUG REGRESSION: {len(zones)} zones returned for Quebec City center! "
            f"Backend should exclude ALL zones in urban area. "
            f"Zone layers: {[f.get('properties', {}).get('layer_id') for f in zones[:5]]}"
        )
        print(f"PASS: Urban Quebec City returned 0 zones (exclusions applied)")
    
    def test_forest_waypoint_returns_zones(self, client):
        """
        Forest area (47.285, -71.415) MUST return zones (>0).
        Anti-regression: ensure filter isn't too aggressive.
        """
        data = _call_organic_zones(client, FOREST_BOUNDS, FOREST_WAYPOINT)
        zones = data.get("features", [])
        
        assert len(zones) > 0, (
            f"BUG: Forest area returned 0 zones! "
            f"Filter may be too aggressive. Stats: {data.get('stats', {})}"
        )
        print(f"PASS: Forest area returned {len(zones)} zones")
    
    def test_urban_has_exclusion_data(self, client):
        """Verify the backend fetched and applied exclusion data"""
        data = _call_organic_zones(client, URBAN_BOUNDS, URBAN_WAYPOINT)
        stats = data.get("stats", {})
        exclusions_count = stats.get("exclusions_count", 0)
        
        assert exclusions_count > 100, (
            f"Too few exclusions for urban area: {exclusions_count}. "
            f"Overpass API may have failed."
        )
        print(f"PASS: Urban area has {exclusions_count} exclusion features")
    
    def test_anthropic_pressure_filter_rejects_zones(self, client):
        """Verify the anthropic_pressure_v7 filter is active and rejecting zones"""
        data = _call_organic_zones(client, URBAN_BOUNDS, URBAN_WAYPOINT)
        stats = data.get("stats", {})
        rejected = stats.get("rejected_exclusion", 0)
        
        assert rejected > 0, (
            f"No zones rejected by exclusion filter in urban area. "
            f"The anthropic_pressure_v7 filter may not be working."
        )
        print(f"PASS: {rejected} zones rejected by exclusion filters")
    
    def test_forest_not_over_filtered(self, client):
        """Forest should have >= 3 zones (not over-filtered)"""
        data = _call_organic_zones(client, FOREST_BOUNDS, FOREST_WAYPOINT)
        zones = data.get("features", [])
        
        assert len(zones) >= 3, (
            f"Only {len(zones)} zones in forest area - filter too aggressive"
        )
        print(f"PASS: Forest has {len(zones)} zones (not over-filtered)")
    
    def test_response_is_geojson_featurecollection(self, client):
        """Verify response format is valid GeoJSON"""
        data = _call_organic_zones(client, FOREST_BOUNDS, FOREST_WAYPOINT)
        
        assert data.get("type") == "FeatureCollection", "Response not a FeatureCollection"
        assert "features" in data, "Response missing features array"
        assert "stats" in data, "Response missing stats object"
        print("PASS: Response is valid GeoJSON FeatureCollection with stats")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
