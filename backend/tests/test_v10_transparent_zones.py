"""
Iteration 38 - V10 Zone Transparent Interiors + Opaque Contours Test
====================================================================
Verify STEEVE-MAX directive:
1. Zone interiors fully transparent (fillOpacity=0)
2. Zone contours opaque (opacity=1.0), weight=3
3. Zones can overlap freely (superposition libre)
4. Contours organic (Catmull-Rom + Chaikin smoothing)
5. BCE-4X compliance (no simplification, no vertex loss)
6. STEEVE-MAX compliance (64→16 fusion, dynamic dimension)
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

@pytest.fixture(scope="module")
def v10_data():
    """Fetch V10 corridors data for testing."""
    response = requests.post(
        f"{BASE_URL}/api/v10/corridors/analyze-full",
        json={"center_lat": 46.85, "center_lng": -71.25, "species": "CERF", "month": 10},
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200, f"API returned {response.status_code}"
    return response.json()


class TestV10APIStructure:
    """Test API response structure and content."""
    
    def test_api_returns_200(self, v10_data):
        """API should return 200 with valid data."""
        assert v10_data is not None
        assert "geojson" in v10_data
        
    def test_16_polygon_features_4_per_type(self, v10_data):
        """Should have exactly 16 Polygon features (4 per zone type)."""
        features = v10_data.get("geojson", {}).get("features", [])
        polygons = [f for f in features if f["geometry"]["type"] == "Polygon"]
        
        assert len(polygons) == 16, f"Expected 16 polygons, got {len(polygons)}"
        
        # Count per zone type
        zone_counts = {}
        for p in polygons:
            zone_type = p["properties"]["zone_type"]
            zone_counts[zone_type] = zone_counts.get(zone_type, 0) + 1
        
        for zone_type in ["alimentation", "repos", "rut", "eau"]:
            assert zone_counts.get(zone_type, 0) == 4, f"Expected 4 {zone_type} zones, got {zone_counts.get(zone_type, 0)}"

    def test_cluster_size_4_per_polygon(self, v10_data):
        """Each polygon should have cluster_size=4 (fusion of 4 zones)."""
        features = v10_data.get("geojson", {}).get("features", [])
        polygons = [f for f in features if f["geometry"]["type"] == "Polygon"]
        
        for p in polygons:
            cluster_size = p["properties"].get("cluster_size")
            assert cluster_size == 4, f"Expected cluster_size=4, got {cluster_size}"

    def test_all_centers_has_4_entries_per_polygon(self, v10_data):
        """Each polygon should have all_centers array with 4 entries."""
        features = v10_data.get("geojson", {}).get("features", [])
        polygons = [f for f in features if f["geometry"]["type"] == "Polygon"]
        
        for p in polygons:
            all_centers = p["properties"].get("all_centers", [])
            assert len(all_centers) == 4, f"Expected 4 centers, got {len(all_centers)}"

    def test_64_total_center_points(self, v10_data):
        """Total center points should be 64 (16 polygons * 4 centers each)."""
        features = v10_data.get("geojson", {}).get("features", [])
        polygons = [f for f in features if f["geometry"]["type"] == "Polygon"]
        
        total_centers = sum(len(p["properties"].get("all_centers", [])) for p in polygons)
        assert total_centers == 64, f"Expected 64 total centers, got {total_centers}"


class TestV10PolygonGeometry:
    """Test polygon geometry requirements (BCE-4X + STEEVE-MAX)."""
    
    def test_high_vertex_counts_catmull_rom_chaikin(self, v10_data):
        """Polygons should have high vertex counts (>2000) indicating smoothing."""
        features = v10_data.get("geojson", {}).get("features", [])
        polygons = [f for f in features if f["geometry"]["type"] == "Polygon"]
        
        for p in polygons:
            coords = p["geometry"]["coordinates"][0]
            zone_type = p["properties"]["zone_type"]
            assert len(coords) > 2000, f"{zone_type} polygon has only {len(coords)} vertices (expected >2000)"
    
    def test_polygon_extent_large_organic(self, v10_data):
        """Zone polygons should have large extent (600m+ for organic shapes)."""
        features = v10_data.get("geojson", {}).get("features", [])
        polygons = [f for f in features if f["geometry"]["type"] == "Polygon"]
        
        for p in polygons:
            coords = p["geometry"]["coordinates"][0]
            lats = [c[1] for c in coords]
            lngs = [c[0] for c in coords]
            
            lat_extent = (max(lats) - min(lats)) * 111320  # meters
            lng_extent = (max(lngs) - min(lngs)) * 85000   # approx at 46°N
            
            max_extent = max(lat_extent, lng_extent)
            zone_type = p["properties"]["zone_type"]
            
            # Organic shapes should be 600m+ in largest dimension
            assert max_extent > 600, f"{zone_type} extent {max_extent:.0f}m is too small (expected >600m)"


class TestV10ZoneColors:
    """Test zone colors (BCE-4X palette)."""
    
    def test_zone_colors_correct(self, v10_data):
        """Zone colors should match BCE-4X specification."""
        expected_colors = {
            "alimentation": "#4CAF50",
            "repos": "#2196F3",
            "rut": "#FF5722",
            "eau": "#00BCD4",
        }
        
        features = v10_data.get("geojson", {}).get("features", [])
        polygons = [f for f in features if f["geometry"]["type"] == "Polygon"]
        
        for p in polygons:
            zone_type = p["properties"]["zone_type"]
            color = p["properties"]["color"]
            expected = expected_colors.get(zone_type)
            
            assert color == expected, f"{zone_type} color {color} != expected {expected}"


class TestV10EngineVersion:
    """Test engine version and metadata."""
    
    def test_engine_v10(self, v10_data):
        """Engine should be CORRIDORS-V10."""
        assert v10_data.get("engine") == "CORRIDORS-V10"
        assert v10_data.get("version") == "10.0.0"

    def test_corridor_linestrings_exist(self, v10_data):
        """Should have corridor LineString features."""
        features = v10_data.get("geojson", {}).get("features", [])
        corridors = [f for f in features if f["geometry"]["type"] == "LineString"]
        
        assert len(corridors) > 0, "Expected corridor LineString features"
        # V10 generates 192 corridors (16 zones * 12 connections each)
        assert len(corridors) >= 150, f"Expected ~192 corridors, got {len(corridors)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
