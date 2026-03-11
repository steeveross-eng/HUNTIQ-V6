"""
BIONIC V5 300% — API Integration Tests: Spatial Clipping & Snapshot
=====================================================================
Tests the /api/v1/bionic/clipped-zones and /api/v1/bionic/snapshot endpoints.
"""

import pytest
import requests
import os
import math

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://territory-analysis.preview.emergentagent.com')

# Test coordinates (Quebec City area)
TEST_LAT = 46.8
TEST_LNG = -71.2


class TestClippedZonesEndpoint:
    """Tests for POST /api/v1/bionic/clipped-zones"""
    
    def test_clipped_zones_returns_200(self):
        """Endpoint returns 200 with valid payload"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/clipped-zones",
            json={"lat": TEST_LAT, "lng": TEST_LNG, "species": "moose"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_clipped_zones_has_required_fields(self):
        """Response contains required fields: clipped_zones, analysis_bbox, stats"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/clipped-zones",
            json={"lat": TEST_LAT, "lng": TEST_LNG, "species": "moose"},
            timeout=30
        )
        data = response.json()
        
        assert "clipped_zones" in data, "Missing 'clipped_zones'"
        assert "analysis_bbox" in data, "Missing 'analysis_bbox'"
        assert "stats" in data, "Missing 'stats'"
        assert "metadata" in data, "Missing 'metadata'"
    
    def test_analysis_bbox_dimensions_1km(self):
        """INVARIANT: analysis_bbox must be exactly 1km × 1km"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/clipped-zones",
            json={"lat": TEST_LAT, "lng": TEST_LNG, "species": "moose"},
            timeout=30
        )
        bbox = response.json()["analysis_bbox"]
        
        # Check lat delta (~0.009° for 1km)
        lat_delta = bbox["north"] - bbox["south"]
        height_m = lat_delta * 111320
        assert 999 < height_m < 1001, f"Height {height_m}m not 1000m"
        
        # Check lng delta (compensated for latitude)
        lng_delta = bbox["east"] - bbox["west"]
        width_m = lng_delta * 111320 * math.cos(math.radians(TEST_LAT))
        assert 999 < width_m < 1001, f"Width {width_m}m not 1000m"
    
    def test_analysis_bbox_centered(self):
        """INVARIANT: bbox must be centered on the input coordinates"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/clipped-zones",
            json={"lat": TEST_LAT, "lng": TEST_LNG, "species": "moose"},
            timeout=30
        )
        bbox = response.json()["analysis_bbox"]
        
        center_lat = (bbox["north"] + bbox["south"]) / 2
        center_lng = (bbox["east"] + bbox["west"]) / 2
        
        assert abs(center_lat - TEST_LAT) < 1e-8, f"Center lat {center_lat} != {TEST_LAT}"
        assert abs(center_lng - TEST_LNG) < 1e-8, f"Center lng {center_lng} != {TEST_LNG}"
    
    def test_stats_overflow_count_always_zero(self):
        """INVARIANT: overflow_count must always be 0"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/clipped-zones",
            json={"lat": TEST_LAT, "lng": TEST_LNG, "species": "moose"},
            timeout=30
        )
        stats = response.json()["stats"]
        
        assert stats.get("overflow_count") == 0, f"overflow_count={stats.get('overflow_count')}, expected 0"
    
    def test_metadata_contains_invariant_marker(self):
        """Metadata must contain BIONIC_V5_300_STRICT marker"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/clipped-zones",
            json={"lat": TEST_LAT, "lng": TEST_LNG, "species": "moose"},
            timeout=30
        )
        metadata = response.json()["metadata"]
        
        assert metadata.get("clipping_invariant") == "BIONIC_V5_300_STRICT"


class TestSnapshotEndpoint:
    """Tests for POST /api/v1/bionic/snapshot"""
    
    def test_snapshot_returns_200(self):
        """Endpoint returns 200 with valid payload"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/snapshot",
            json={
                "lat": TEST_LAT,
                "lng": TEST_LNG,
                "species": "moose",
                "waypoint_name": "Test Waypoint"
            },
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_snapshot_has_required_fields(self):
        """Response contains all required snapshot fields"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/snapshot",
            json={
                "lat": TEST_LAT,
                "lng": TEST_LNG,
                "species": "moose",
                "waypoint_name": "Test Waypoint"
            },
            timeout=30
        )
        data = response.json()
        
        required_fields = [
            "snapshot_id", "timestamp", "version", "waypoint",
            "analysis_bbox", "species", "season", "structural_zones",
            "clipping_stats", "zone_summary"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_snapshot_id_format(self):
        """snapshot_id follows expected format"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/snapshot",
            json={
                "lat": TEST_LAT,
                "lng": TEST_LNG,
                "species": "moose",
                "waypoint_name": "Test Waypoint"
            },
            timeout=30
        )
        snapshot_id = response.json()["snapshot_id"]
        
        assert snapshot_id.startswith("snap_"), f"snapshot_id should start with 'snap_': {snapshot_id}"
        assert "moose" in snapshot_id, f"snapshot_id should contain species: {snapshot_id}"
    
    def test_snapshot_waypoint_data(self):
        """Waypoint data is correctly included"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/snapshot",
            json={
                "lat": TEST_LAT,
                "lng": TEST_LNG,
                "species": "moose",
                "waypoint_name": "Test Quebec"
            },
            timeout=30
        )
        waypoint = response.json()["waypoint"]
        
        assert waypoint["name"] == "Test Quebec"
        assert abs(waypoint["lat"] - TEST_LAT) < 1e-6
        assert abs(waypoint["lng"] - TEST_LNG) < 1e-6
    
    def test_snapshot_version_marker(self):
        """Version must be BIONIC_V5_300_STRICT"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/snapshot",
            json={
                "lat": TEST_LAT,
                "lng": TEST_LNG,
                "species": "moose"
            },
            timeout=30
        )
        
        assert response.json()["version"] == "BIONIC_V5_300_STRICT"
    
    def test_snapshot_has_zone_summary(self):
        """zone_summary is present (may be empty dict if no zones)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/snapshot",
            json={
                "lat": TEST_LAT,
                "lng": TEST_LNG,
                "species": "moose"
            },
            timeout=30
        )
        
        zone_summary = response.json()["zone_summary"]
        assert isinstance(zone_summary, dict), f"zone_summary should be dict: {type(zone_summary)}"


class TestEdgeCases:
    """Edge case tests for spatial clipping endpoints"""
    
    def test_clipped_zones_invalid_lat(self):
        """Should reject invalid latitude"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/clipped-zones",
            json={"lat": 200, "lng": TEST_LNG, "species": "moose"},
            timeout=30
        )
        assert response.status_code == 422, f"Expected 422 for invalid lat, got {response.status_code}"
    
    def test_clipped_zones_invalid_lng(self):
        """Should reject invalid longitude"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/clipped-zones",
            json={"lat": TEST_LAT, "lng": -200, "species": "moose"},
            timeout=30
        )
        assert response.status_code == 422, f"Expected 422 for invalid lng, got {response.status_code}"
    
    def test_clipped_zones_missing_lat(self):
        """Should require lat field"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/clipped-zones",
            json={"lng": TEST_LNG, "species": "moose"},
            timeout=30
        )
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
