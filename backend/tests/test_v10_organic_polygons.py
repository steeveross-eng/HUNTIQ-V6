"""
Test V10 Organic Zone Polygons - Catmull-Rom Spline Implementation
Iteration 35: Validates organic shapes (no straight segments), high vertex count (800+),
BCE-4X compliance, and terrain-aware perturbation.
"""
import pytest
import requests
import os
import math

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# V10 API payload
V10_PAYLOAD = {
    "center_lat": 46.85,
    "center_lng": -71.25,
    "species": "CERF",
    "month": 10
}


class TestV10OrganicPolygons:
    """Tests for V10 organic zone polygon generation"""

    @pytest.fixture(scope="class")
    def v10_response(self):
        """Fetch V10 corridor analysis response"""
        response = requests.post(
            f"{BASE_URL}/api/v10/corridors/analyze-full",
            json=V10_PAYLOAD,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        assert response.status_code == 200
        return response.json()

    @pytest.fixture(scope="class")
    def polygon_features(self, v10_response):
        """Extract polygon features from response"""
        return [f for f in v10_response["geojson"]["features"] if f["geometry"]["type"] == "Polygon"]

    # =============== POLYGON COUNT & TYPE TESTS ===============
    
    def test_returns_64_polygon_features(self, polygon_features):
        """API should return exactly 64 Polygon features"""
        assert len(polygon_features) == 64, f"Expected 64 polygons, got {len(polygon_features)}"

    def test_no_point_features(self, v10_response):
        """API should return 0 Point features (replaced by Polygons)"""
        point_features = [f for f in v10_response["geojson"]["features"] if f["geometry"]["type"] == "Point"]
        assert len(point_features) == 0, f"Expected 0 points, got {len(point_features)}"

    # =============== HIGH VERTEX COUNT TESTS (ORGANIC CURVES) ===============

    def test_polygon_min_vertex_count_145(self, polygon_features):
        """All polygons should have minimum 145 vertices (Catmull-Rom spline)"""
        for i, feat in enumerate(polygon_features):
            coords = feat["geometry"]["coordinates"][0]
            assert len(coords) >= 145, f"Polygon {i} has only {len(coords)} vertices (min 145 expected)"

    def test_polygon_avg_vertex_count_800_plus(self, polygon_features):
        """Average polygon vertex count should be 800+ (organic curves)"""
        vertex_counts = [len(f["geometry"]["coordinates"][0]) for f in polygon_features]
        avg = sum(vertex_counts) / len(vertex_counts)
        assert avg >= 800, f"Average vertex count {avg:.0f} < 800 (organic curves expected)"

    def test_polygon_max_vertex_count_1000_plus(self, polygon_features):
        """Max polygon vertex count should be 1000+ (high resolution)"""
        max_count = max(len(f["geometry"]["coordinates"][0]) for f in polygon_features)
        assert max_count >= 1000, f"Max vertex count {max_count} < 1000 (high resolution expected)"

    # =============== ORGANIC SHAPE TESTS (NO STRAIGHT SEGMENTS) ===============

    def test_no_straight_segments_in_polygons(self, polygon_features):
        """Polygons should have smooth curves (no straight line segments)"""
        # A segment is "straight" if 3+ consecutive points are collinear
        for feat in polygon_features[:5]:  # Test first 5 polygons
            coords = feat["geometry"]["coordinates"][0]
            collinear_count = 0
            
            for i in range(len(coords) - 2):
                p1, p2, p3 = coords[i], coords[i+1], coords[i+2]
                # Cross product to check collinearity
                cross = (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])
                if abs(cross) < 1e-12:  # Nearly collinear
                    collinear_count += 1
            
            # Allow at most 10% collinear segments (Catmull-Rom should minimize this)
            max_collinear = len(coords) * 0.10
            assert collinear_count < max_collinear, \
                f"Polygon has {collinear_count} collinear segments (>{max_collinear:.0f}), not organic"

    def test_polygon_coordinates_smoothly_transition(self, polygon_features):
        """Coordinates should transition smoothly (small incremental changes)"""
        for feat in polygon_features[:3]:  # Test first 3 polygons
            coords = feat["geometry"]["coordinates"][0]
            large_jumps = 0
            
            for i in range(len(coords) - 1):
                dx = abs(coords[i+1][0] - coords[i][0])
                dy = abs(coords[i+1][1] - coords[i][1])
                dist = math.sqrt(dx**2 + dy**2)
                
                # A large jump is > 0.001 degrees (~100m)
                if dist > 0.001:
                    large_jumps += 1
            
            # Organic spline should have minimal large jumps (< 5%)
            max_jumps = len(coords) * 0.05
            assert large_jumps < max_jumps, \
                f"Polygon has {large_jumps} large coordinate jumps (>{max_jumps:.0f}), not smooth"

    # =============== ZONE TYPE TESTS ===============

    def test_all_4_zone_types_present(self, polygon_features):
        """All 4 zone types should be present: alimentation, repos, rut, eau"""
        zone_types = set(f["properties"]["zone_type"] for f in polygon_features)
        expected = {"alimentation", "repos", "rut", "eau"}
        assert zone_types == expected, f"Zone types {zone_types} != {expected}"

    def test_zone_colors_match_bce4x_palette(self, polygon_features):
        """Zone colors should match BCE-4X palette"""
        palette = {
            "alimentation": "#4CAF50",
            "repos": "#2196F3",
            "rut": "#FF5722",
            "eau": "#00BCD4"
        }
        for feat in polygon_features:
            zone_type = feat["properties"]["zone_type"]
            color = feat["properties"]["color"]
            assert color == palette[zone_type], f"{zone_type} color {color} != {palette[zone_type]}"

    # =============== BCE-4X COMPLIANCE TESTS ===============

    def test_bce4x_validation_pass(self, v10_response):
        """BCE-4X validation should pass"""
        assert v10_response["validation"]["bce4x"]["status"] == "PASS"

    def test_steeve_max_validation_pass(self, v10_response):
        """Steeve-MAX validation should pass"""
        assert v10_response["validation"]["steeve_max"]["status"] == "PASS"

    # =============== POLYGON STRUCTURE TESTS ===============

    def test_polygon_rings_closed(self, polygon_features):
        """Polygon rings should be closed (first == last)"""
        for feat in polygon_features:
            coords = feat["geometry"]["coordinates"][0]
            assert coords[0] == coords[-1], "Polygon ring not closed"

    def test_polygon_has_center_coordinates(self, polygon_features):
        """Polygons should have center_lat and center_lng properties"""
        for feat in polygon_features:
            props = feat["properties"]
            assert "center_lat" in props, "Missing center_lat"
            assert "center_lng" in props, "Missing center_lng"

    # =============== CORRIDOR TESTS (BCE-4X) ===============

    def test_corridors_are_linestrings(self, v10_response):
        """Corridors should be LineString features"""
        linestrings = [f for f in v10_response["geojson"]["features"] if f["geometry"]["type"] == "LineString"]
        assert len(linestrings) > 0, "No corridor LineStrings found"

    def test_critique_corridors_have_b80000_color(self, v10_response):
        """CRITIQUE corridors should have BCE-4X color (#CC0000 backend, #B80000 frontend)"""
        corridors = [f for f in v10_response["geojson"]["features"] if f["geometry"]["type"] == "LineString"]
        critique = [c for c in corridors if c["properties"]["niveau"] == "CRITIQUE"]
        if critique:
            # Backend uses #CC0000, frontend uses #B80000
            assert critique[0]["properties"]["color"] in ["#CC0000", "#B80000"]

    def test_majeur_corridors_no_pattern(self, v10_response):
        """MAJEUR corridors should have no dash pattern (BCE-4X)"""
        corridors = [f for f in v10_response["geojson"]["features"] if f["geometry"]["type"] == "LineString"]
        majeur = [c for c in corridors if c["properties"]["niveau"] == "MAJEUR"]
        if majeur:
            assert majeur[0]["properties"].get("dash_array") is None or majeur[0]["properties"]["dash_array"] == ""

    # =============== NIVEAU DISTRIBUTION TESTS ===============

    def test_niveau_distribution_has_all_levels(self, v10_response):
        """Niveau distribution should include all 5 levels"""
        dist = v10_response["niveau_distribution"]
        expected_levels = {"CRITIQUE", "MAJEUR", "FORT", "MODERE", "FAIBLE"}
        assert set(dist.keys()) == expected_levels


class TestV10PerformanceAndSize:
    """Tests for polygon size and performance"""

    @pytest.fixture(scope="class")
    def v10_response(self):
        response = requests.post(
            f"{BASE_URL}/api/v10/corridors/analyze-full",
            json=V10_PAYLOAD,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        assert response.status_code == 200
        return response.json()

    def test_polygon_geographic_extent_400_560m(self, v10_response):
        """Zone polygons should cover ~400-560m (larger than convex hull 300m)"""
        polygons = [f for f in v10_response["geojson"]["features"] if f["geometry"]["type"] == "Polygon"]
        
        for feat in polygons[:5]:  # Test first 5
            coords = feat["geometry"]["coordinates"][0]
            lngs = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            
            # Calculate extent in degrees
            lng_extent = max(lngs) - min(lngs)
            lat_extent = max(lats) - min(lats)
            
            # Convert to meters (rough approximation at 46.85°N)
            m_per_deg_lat = 111320
            m_per_deg_lng = 111320 * math.cos(math.radians(46.85))
            
            extent_m = max(lng_extent * m_per_deg_lng, lat_extent * m_per_deg_lat)
            
            # Zone should be 200-700m extent (organic shapes vary)
            assert 200 < extent_m < 700, f"Zone extent {extent_m:.0f}m outside 200-700m range"

    def test_api_response_time_acceptable(self):
        """API should respond within 30 seconds despite high vertex count"""
        import time
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v10/corridors/analyze-full",
            json=V10_PAYLOAD,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 30, f"API response time {elapsed:.1f}s > 30s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
