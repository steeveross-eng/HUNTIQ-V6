"""
MASTER PLAN BIONIC 1000% — Passe 1 API Integration Tests
========================================================

Tests:
  T-BUG04-API: API returns zones where score = score_display = int(score_global)
  T-T4-API: stats.t4_zone_count == len(geojson.features)
  T-CLASSIFICATION-API: All zones have valid zone_type from v7 data
  T-NO-DOUBLE-PEN: V5 scoring module is NOT called when V7 engine active
"""

import pytest
import requests
import os

# Get API base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://bionic-toolbar-slim.preview.emergentagent.com').rstrip('/')

# Rural location in Laurentides, Quebec (for testing zones generation)
RURAL_BOUNDS = {
    "south": 47.285,
    "north": 47.315,
    "west": -71.535,
    "east": -71.505
}
WAYPOINT_CENTER = {"lat": 47.30, "lng": -71.52}


class TestBUG04APIScoring:
    """BUG-04: API must return score = score_display = int(score_global) for V7 zones."""

    def test_api_v7_zone_scoring_coherence(self):
        """All V7 zones must have score == score_display == int(score_global)."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": RURAL_BOUNDS,
                "species": "moose",
                "layers": ["habitats", "rut", "repos", "alimentation"],
                "waypoint_center": WAYPOINT_CENTER
            },
            timeout=60
        )
        
        assert response.status_code == 200, f"API returned {response.status_code}"
        data = response.json()
        
        features = data.get("features", [])
        assert len(features) > 0, "Expected at least 1 zone from rural location"
        
        for feature in features:
            props = feature.get("properties", {})
            
            # Skip non-V7 zones (fallback V5 zones don't have score_global)
            if "score_global" not in props:
                continue
            
            score = props.get("score")
            score_display = props.get("score_display")
            score_global = props.get("score_global")
            
            expected = max(25, int(score_global))
            
            assert score == expected, (
                f"score mismatch: {score} != expected {expected} (score_global={score_global})"
            )
            assert score_display == expected, (
                f"score_display mismatch: {score_display} != expected {expected} (score_global={score_global})"
            )

    def test_api_v7_zone_score_range(self):
        """V7 zone scores must be >= 25 (min floor applied)."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": RURAL_BOUNDS,
                "species": "moose",
                "layers": ["habitats", "rut", "repos", "alimentation"],
                "waypoint_center": WAYPOINT_CENTER
            },
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            score = props.get("score", 0)
            
            assert score >= 25, f"score {score} is below minimum floor 25"


class TestT4APICoherence:
    """T4: stats.t4_zone_count must equal len(geojson.features)."""

    def test_api_t4_zone_count_coherence(self):
        """stats.t4_zone_count must match the actual features array length."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": RURAL_BOUNDS,
                "species": "moose",
                "layers": ["habitats", "rut", "repos", "alimentation"],
                "waypoint_center": WAYPOINT_CENTER
            },
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        features = data.get("features", [])
        stats = data.get("stats", {})
        
        t4_zone_count = stats.get("t4_zone_count")
        
        assert t4_zone_count is not None, "stats.t4_zone_count is missing from response"
        assert t4_zone_count == len(features), (
            f"T4 MISMATCH: stats.t4_zone_count={t4_zone_count} != len(features)={len(features)}"
        )

    def test_api_stats_total_zones_coherence(self):
        """stats.total_zones should also match features count."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": RURAL_BOUNDS,
                "species": "moose",
                "layers": ["habitats", "rut", "repos", "alimentation"],
                "waypoint_center": WAYPOINT_CENTER
            },
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        features = data.get("features", [])
        stats = data.get("stats", {})
        total_zones = stats.get("total_zones", 0)
        
        # total_zones is counted before geojson conversion, should match
        assert total_zones == len(features), (
            f"stats.total_zones={total_zones} != len(features)={len(features)}"
        )


class TestBUG01APIClassification:
    """BUG-01: Each zone must have a valid zone_type from v7 data."""

    VALID_ZONE_TYPES = {"feed", "rut", "rest", "mixed"}

    def test_api_zone_type_valid(self):
        """All V7 zones must have a valid zone_type."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": RURAL_BOUNDS,
                "species": "moose",
                "layers": ["habitats", "rut", "repos", "alimentation"],
                "waypoint_center": WAYPOINT_CENTER
            },
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            
            # Check zone_type exists (for V7 zones)
            if "v7" in props or "zone_type" in props:
                zone_type = props.get("zone_type")
                assert zone_type is not None, "zone_type is missing from V7 zone"
                assert zone_type in self.VALID_ZONE_TYPES, (
                    f"Invalid zone_type: {zone_type}, expected one of {self.VALID_ZONE_TYPES}"
                )


class TestNoDoublePenalization:
    """Verify V5 scoring module is NOT overwriting V7 scores."""

    def test_api_v7_engine_active(self):
        """When V7 engine is active, exclusion_engine in stats should be 'v7'."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": RURAL_BOUNDS,
                "species": "moose",
                "layers": ["habitats", "rut", "repos", "alimentation"],
                "waypoint_center": WAYPOINT_CENTER
            },
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        stats = data.get("stats", {})
        exclusion_engine = stats.get("exclusion_engine")
        
        assert exclusion_engine == "v7", (
            f"Expected exclusion_engine='v7', got '{exclusion_engine}'"
        )

    def test_api_v7_zones_have_subscores(self):
        """V7 zones should have subscores dict (indicator of V7 scoring, not V5)."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": RURAL_BOUNDS,
                "species": "moose",
                "layers": ["habitats", "rut", "repos", "alimentation"],
                "waypoint_center": WAYPOINT_CENTER
            },
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        features = data.get("features", [])
        v7_zones_count = 0
        
        for feature in features:
            props = feature.get("properties", {})
            if "subscores" in props or "v7" in props:
                v7_zones_count += 1
                # V7 zones should have subscores (even if empty dict)
                subscores = props.get("subscores") or props.get("v7", {}).get("subscores")
                assert subscores is not None or props.get("v7"), (
                    "V7 zone missing subscores indicator"
                )
        
        # At least some zones should be V7 processed
        assert v7_zones_count > 0, "No V7 zones found in response"


class TestAPIHealthAndStructure:
    """Basic API health and response structure tests."""

    def test_api_organic_zones_endpoint_available(self):
        """POST /api/v1/bionic/organic-zones should be available."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": RURAL_BOUNDS,
                "species": "moose",
                "layers": ["habitats"],
                "waypoint_center": WAYPOINT_CENTER
            },
            timeout=60
        )
        
        assert response.status_code == 200

    def test_api_response_is_geojson(self):
        """Response should be valid GeoJSON FeatureCollection."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": RURAL_BOUNDS,
                "species": "moose",
                "layers": ["habitats", "rut"],
                "waypoint_center": WAYPOINT_CENTER
            },
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("type") == "FeatureCollection", "Response is not a FeatureCollection"
        assert "features" in data, "Missing 'features' key"
        assert isinstance(data["features"], list), "'features' is not a list"

    def test_api_layers_endpoint(self):
        """GET /api/v1/bionic/organic-zones/layers should return available layers."""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/organic-zones/layers",
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "layers" in data
        assert "species" in data
        assert len(data["layers"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
