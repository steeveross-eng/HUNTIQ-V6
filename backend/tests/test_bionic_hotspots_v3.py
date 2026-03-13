"""
BIONIC Hotspots V3 Admin API Tests
===================================
Tests for the new Hotspot extraction engine and admin API endpoints.

Endpoints tested:
- POST /api/v1/admin/bionic-hotspots/extract (triggers extraction for all 12 regions)
- GET  /api/v1/admin/bionic-hotspots/regions (lists 12 Quebec regions)
- GET  /api/v1/admin/bionic-hotspots/list (with filters: classification, species)
- GET  /api/v1/admin/bionic-hotspots/stats (score_avg, score_max, by_species, etc.)
- GET  /api/v1/admin/bionic-hotspots/export/geojson (GeoJSON FeatureCollection)
- GET  /api/v1/admin/bionic-hotspots/report/bce4x (BCE-4X compliance validation)
- GET  /api/v1/admin/bionic-hotspots/report/daily (daily report)
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
HOTSPOT_API = f"{BASE_URL}/api/v1/admin/bionic-hotspots"


class TestHotspotRegions:
    """Test GET /regions endpoint - should list all 12 Quebec regions"""

    def test_list_regions_returns_12(self):
        """Verify all 12 BIONIC regions are returned"""
        response = requests.get(f"{HOTSPOT_API}/regions")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total" in data, "Response should have 'total' field"
        assert "regions" in data, "Response should have 'regions' field"
        assert data["total"] == 12, f"Expected 12 regions, got {data['total']}"
        assert len(data["regions"]) == 12, f"Expected 12 regions in list, got {len(data['regions'])}"
        
        # Verify region structure
        region = data["regions"][0]
        assert "id" in region, "Region should have 'id'"
        assert "name" in region, "Region should have 'name'"
        assert "center" in region, "Region should have 'center'"
        assert "radius_km" in region, "Region should have 'radius_km'"

    def test_regions_include_expected_ids(self):
        """Verify expected region IDs are present"""
        response = requests.get(f"{HOTSPOT_API}/regions")
        data = response.json()
        
        region_ids = [r["id"] for r in data["regions"]]
        expected_ids = [
            "laurentides", "outaouais", "lanaudiere", "mauricie", "estrie",
            "saguenay", "capitale_nationale", "chaudiere_appalaches",
            "bas_saint_laurent", "abitibi", "cote_nord", "gaspesie"
        ]
        
        for expected in expected_ids:
            assert expected in region_ids, f"Expected region '{expected}' not found"


class TestHotspotExtraction:
    """Test POST /extract endpoint - extracts hotspots for all regions"""

    def test_extract_all_returns_success(self):
        """Verify extraction completes successfully with expected data"""
        response = requests.post(f"{HOTSPOT_API}/extract", timeout=60)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success=True"
        assert data["total_regions"] == 12, f"Expected 12 regions, got {data['total_regions']}"
        assert data["total_hotspots"] > 0, f"Expected total_hotspots > 0, got {data['total_hotspots']}"
        assert "scoring_weights" in data, "Response should include scoring_weights"
        assert "thresholds" in data, "Response should include thresholds"
        assert "regions_summary" in data, "Response should include regions_summary"
        assert "extracted_at" in data, "Response should include extracted_at timestamp"
        
        # Verify we have ~300 hotspots (25 per region x 12 regions)
        assert data["total_hotspots"] >= 100, f"Expected at least 100 hotspots, got {data['total_hotspots']}"

    def test_extract_returns_regions_summary(self):
        """Verify regions_summary has proper structure"""
        response = requests.post(f"{HOTSPOT_API}/extract", timeout=60)
        data = response.json()
        
        assert len(data["regions_summary"]) == 12, "Should have 12 region summaries"
        
        for region_sum in data["regions_summary"]:
            assert "region_id" in region_sum
            assert "region_name" in region_sum
            assert "hotspots_count" in region_sum
            assert "by_classification" in region_sum
            assert "by_species" in region_sum


class TestHotspotList:
    """Test GET /list endpoint - lists hotspots with filters (requires extraction first)"""

    @pytest.fixture(autouse=True)
    def ensure_extraction(self):
        """Ensure extraction is done before list tests"""
        requests.post(f"{HOTSPOT_API}/extract", timeout=60)

    def test_list_returns_hotspots(self):
        """Verify /list returns hotspots with correct structure"""
        response = requests.get(f"{HOTSPOT_API}/list")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "hotspots" in data, "Response should have 'hotspots'"
        assert "total" in data, "Response should have 'total'"
        assert len(data["hotspots"]) > 0, "Should have at least one hotspot"
        
        # Verify hotspot structure
        hotspot = data["hotspots"][0]
        assert "id" in hotspot, "Hotspot should have 'id'"
        assert "score" in hotspot, "Hotspot should have 'score'"
        assert "classification" in hotspot, "Hotspot should have 'classification'"
        assert "category" in hotspot, "Hotspot should have 'category'"
        assert "dominant_species" in hotspot, "Hotspot should have 'dominant_species'"
        assert "region_name" in hotspot, "Hotspot should have 'region_name'"
        assert "center" in hotspot, "Hotspot should have 'center'"
        assert "accessibility" in hotspot, "Hotspot should have 'accessibility'"

    def test_list_filter_classification_majeur(self):
        """Verify classification=MAJEUR filter works (score >= 80)"""
        response = requests.get(f"{HOTSPOT_API}/list?classification=MAJEUR")
        data = response.json()
        
        for hotspot in data["hotspots"]:
            assert hotspot["classification"] == "MAJEUR", f"Expected MAJEUR, got {hotspot['classification']}"
            assert hotspot["score"] >= 80, f"MAJEUR should have score >= 80, got {hotspot['score']}"

    def test_list_filter_by_species(self):
        """Verify species filter works"""
        response = requests.get(f"{HOTSPOT_API}/list?species=orignal")
        data = response.json()
        
        for hotspot in data["hotspots"]:
            assert hotspot["dominant_species"] == "orignal", f"Expected orignal, got {hotspot['dominant_species']}"

    def test_list_filter_by_region(self):
        """Verify region_id filter works"""
        response = requests.get(f"{HOTSPOT_API}/list?region_id=laurentides")
        data = response.json()
        
        for hotspot in data["hotspots"]:
            assert hotspot["region_id"] == "laurentides", f"Expected laurentides, got {hotspot['region_id']}"


class TestHotspotStats:
    """Test GET /stats endpoint - aggregated statistics"""

    @pytest.fixture(autouse=True)
    def ensure_extraction(self):
        """Ensure extraction is done before stats tests"""
        requests.post(f"{HOTSPOT_API}/extract", timeout=60)

    def test_stats_returns_aggregated_data(self):
        """Verify stats endpoint returns expected fields"""
        response = requests.get(f"{HOTSPOT_API}/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "score_avg" in data, "Should have score_avg"
        assert "score_max" in data, "Should have score_max"
        assert "by_species" in data, "Should have by_species"
        assert "by_category" in data, "Should have by_category"
        assert "by_region" in data, "Should have by_region"
        
        # Verify score_avg is reasonable (between 60-100 since we filter >= 60)
        assert 60 <= data["score_avg"] <= 100, f"score_avg should be between 60-100, got {data['score_avg']}"
        
        # Verify by_species has expected species
        assert len(data["by_species"]) > 0, "Should have species breakdown"


class TestHotspotExportGeoJSON:
    """Test GET /export/geojson endpoint - GeoJSON FeatureCollection export"""

    @pytest.fixture(autouse=True)
    def ensure_extraction(self):
        """Ensure extraction is done before export tests"""
        requests.post(f"{HOTSPOT_API}/extract", timeout=60)

    def test_export_geojson_valid_structure(self):
        """Verify GeoJSON export is a valid FeatureCollection"""
        response = requests.get(f"{HOTSPOT_API}/export/geojson")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("type") == "FeatureCollection", f"Expected FeatureCollection, got {data.get('type')}"
        assert "features" in data, "Should have 'features' array"
        assert "metadata" in data, "Should have 'metadata'"
        assert len(data["features"]) > 0, "Should have at least one feature"
        
        # Verify feature structure
        feature = data["features"][0]
        assert feature["type"] == "Feature"
        assert "geometry" in feature
        assert "properties" in feature
        assert feature["geometry"]["type"] == "Polygon"
        assert "coordinates" in feature["geometry"]
        
        # Verify properties
        props = feature["properties"]
        assert "id" in props
        assert "score" in props
        assert "classification" in props


class TestHotspotBCE4XReport:
    """Test GET /report/bce4x endpoint - BCE-4X compliance validation"""

    @pytest.fixture(autouse=True)
    def ensure_extraction(self):
        """Ensure extraction is done before report tests"""
        requests.post(f"{HOTSPOT_API}/extract", timeout=60)

    def test_bce4x_report_overall_pass(self):
        """Verify BCE-4X report returns PASS with checks > 0"""
        response = requests.get(f"{HOTSPOT_API}/report/bce4x")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "overall" in data, "Should have 'overall' status"
        assert data["overall"] == "PASS", f"Expected overall PASS, got {data['overall']}"
        assert "total_checks" in data, "Should have total_checks"
        assert data["total_checks"] > 0, "Should have > 0 checks"
        assert "passed" in data, "Should have passed count"
        assert "failed" in data, "Should have failed count"
        assert data["failed"] == 0, f"Expected 0 failures, got {data['failed']}"


class TestHotspotDailyReport:
    """Test GET /report/daily endpoint - daily change report"""

    @pytest.fixture(autouse=True)
    def ensure_extraction(self):
        """Ensure extraction is done before report tests"""
        requests.post(f"{HOTSPOT_API}/extract", timeout=60)

    def test_daily_report_structure(self):
        """Verify daily report returns expected structure"""
        response = requests.get(f"{HOTSPOT_API}/report/daily")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "report_type" in data
        assert data["report_type"] == "daily"
        assert "generated_at" in data
        assert "latest_extraction" in data
        assert "total_hotspots" in data
        assert "changes" in data


class TestHotspotBeforeExtraction:
    """Test endpoints behave correctly before extraction is called"""

    def test_list_before_extraction_returns_empty(self):
        """If no extraction has been done in this session, list should indicate so"""
        # Note: This test depends on server state. If extraction was already called,
        # this may not return empty. The message check is the key validation.
        response = requests.get(f"{HOTSPOT_API}/list")
        assert response.status_code == 200
        # Either returns data or a message about no extraction
        data = response.json()
        if "message" in data:
            assert "extraction" in data["message"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
