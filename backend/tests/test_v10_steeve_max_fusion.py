"""
Test STEEVE-MAX Directive: Dimension dynamique + Fusion ecologique + Chaikin smoothing
Iteration 37 - V10 Corridors API testing

Expected API behavior:
- 16 Polygon features (down from 64) - 4 per zone type (alimentation, repos, rut, eau)
- Each polygon has cluster_size=4 and all_centers with 4 center entries
- Total 64 center points preserved across all zones
- Zone polygons are large and organic (800-1500m extent from merged clusters)
- Smooth contours (Chaikin smoothing, high vertex count ~5000)
- 192 corridor LineString features
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestV10SteeveMaxFusion:
    """Tests for STEEVE-MAX fusion and dimension features"""

    def test_api_returns_16_polygon_features(self):
        """API should return exactly 16 Polygon features (4 per zone type)"""
        response = requests.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json={
            "center_lat": 46.85,
            "center_lng": -71.25,
            "species": "CERF",
            "month": 10
        })
        assert response.status_code == 200
        
        data = response.json()
        features = data.get('geojson', {}).get('features', [])
        polygons = [f for f in features if f['geometry']['type'] == 'Polygon']
        
        assert len(polygons) == 16, f"Expected 16 polygon features, got {len(polygons)}"

    def test_4_polygons_per_zone_type(self):
        """Each zone type (alimentation, repos, rut, eau) should have exactly 4 polygons"""
        response = requests.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json={
            "center_lat": 46.85,
            "center_lng": -71.25,
            "species": "CERF",
            "month": 10
        })
        assert response.status_code == 200
        
        data = response.json()
        features = data.get('geojson', {}).get('features', [])
        polygons = [f for f in features if f['geometry']['type'] == 'Polygon']
        
        by_type = {}
        for p in polygons:
            zt = p['properties'].get('zone_type', 'unknown')
            by_type[zt] = by_type.get(zt, 0) + 1
        
        expected_types = ['alimentation', 'repos', 'rut', 'eau']
        for zone_type in expected_types:
            count = by_type.get(zone_type, 0)
            assert count == 4, f"Expected 4 {zone_type} polygons, got {count}"

    def test_each_polygon_has_cluster_size_4(self):
        """Each polygon should have cluster_size=4 from super-quadrant grouping"""
        response = requests.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json={
            "center_lat": 46.85,
            "center_lng": -71.25,
            "species": "CERF",
            "month": 10
        })
        assert response.status_code == 200
        
        data = response.json()
        features = data.get('geojson', {}).get('features', [])
        polygons = [f for f in features if f['geometry']['type'] == 'Polygon']
        
        for i, p in enumerate(polygons):
            cluster_size = p['properties'].get('cluster_size')
            assert cluster_size == 4, f"Polygon {i} has cluster_size={cluster_size}, expected 4"

    def test_each_polygon_has_4_centers_in_all_centers(self):
        """Each polygon should have all_centers array with 4 center entries"""
        response = requests.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json={
            "center_lat": 46.85,
            "center_lng": -71.25,
            "species": "CERF",
            "month": 10
        })
        assert response.status_code == 200
        
        data = response.json()
        features = data.get('geojson', {}).get('features', [])
        polygons = [f for f in features if f['geometry']['type'] == 'Polygon']
        
        for i, p in enumerate(polygons):
            all_centers = p['properties'].get('all_centers', [])
            assert len(all_centers) == 4, f"Polygon {i} has {len(all_centers)} centers, expected 4"
            
            # Verify each center has lat, lng, score
            for j, center in enumerate(all_centers):
                assert 'lat' in center, f"Center {j} missing 'lat'"
                assert 'lng' in center, f"Center {j} missing 'lng'"
                assert 'score' in center, f"Center {j} missing 'score'"

    def test_total_64_center_points_preserved(self):
        """Total center points across all polygons should be 64 (4 centers x 16 polygons)"""
        response = requests.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json={
            "center_lat": 46.85,
            "center_lng": -71.25,
            "species": "CERF",
            "month": 10
        })
        assert response.status_code == 200
        
        data = response.json()
        features = data.get('geojson', {}).get('features', [])
        polygons = [f for f in features if f['geometry']['type'] == 'Polygon']
        
        total_centers = sum(len(p['properties'].get('all_centers', [])) for p in polygons)
        assert total_centers == 64, f"Total center points: {total_centers}, expected 64"

    def test_polygon_high_vertex_count_chaikin_smoothing(self):
        """Polygons should have high vertex count from Chaikin smoothing (~5000 vertices)"""
        response = requests.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json={
            "center_lat": 46.85,
            "center_lng": -71.25,
            "species": "CERF",
            "month": 10
        })
        assert response.status_code == 200
        
        data = response.json()
        features = data.get('geojson', {}).get('features', [])
        polygons = [f for f in features if f['geometry']['type'] == 'Polygon']
        
        for i, p in enumerate(polygons):
            coords = p['geometry']['coordinates'][0]
            vertex_count = len(coords)
            # Chaikin smoothing with 2 iterations should produce 3000-7000 vertices
            assert vertex_count >= 2000, f"Polygon {i} has only {vertex_count} vertices, expected 2000+ (Chaikin smoothed)"
            assert vertex_count <= 10000, f"Polygon {i} has {vertex_count} vertices, may be too many"

    def test_zone_polygon_colors(self):
        """Zone polygons should have correct BCE-4X colors"""
        response = requests.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json={
            "center_lat": 46.85,
            "center_lng": -71.25,
            "species": "CERF",
            "month": 10
        })
        assert response.status_code == 200
        
        data = response.json()
        features = data.get('geojson', {}).get('features', [])
        polygons = [f for f in features if f['geometry']['type'] == 'Polygon']
        
        expected_colors = {
            'alimentation': '#4CAF50',  # green
            'repos': '#2196F3',         # blue
            'rut': '#FF5722',           # orange
            'eau': '#00BCD4',           # teal
        }
        
        for p in polygons:
            zone_type = p['properties'].get('zone_type')
            color = p['properties'].get('color')
            expected = expected_colors.get(zone_type)
            assert color == expected, f"{zone_type} has color {color}, expected {expected}"

    def test_192_corridor_linestring_features(self):
        """API should return 192 corridor LineString features"""
        response = requests.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json={
            "center_lat": 46.85,
            "center_lng": -71.25,
            "species": "CERF",
            "month": 10
        })
        assert response.status_code == 200
        
        data = response.json()
        features = data.get('geojson', {}).get('features', [])
        corridors = [f for f in features if f['geometry']['type'] == 'LineString']
        
        assert len(corridors) == 192, f"Expected 192 corridors, got {len(corridors)}"

    def test_corridor_score_property_exists(self):
        """All corridors should have score property for frontend filtering"""
        response = requests.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json={
            "center_lat": 46.85,
            "center_lng": -71.25,
            "species": "CERF",
            "month": 10
        })
        assert response.status_code == 200
        
        data = response.json()
        features = data.get('geojson', {}).get('features', [])
        corridors = [f for f in features if f['geometry']['type'] == 'LineString']
        
        for i, c in enumerate(corridors):
            score = c['properties'].get('score')
            assert score is not None, f"Corridor {i} missing score property"
            assert isinstance(score, (int, float)), f"Corridor {i} score should be numeric"

    def test_engine_version_v10(self):
        """API response should indicate CORRIDORS-V10 engine"""
        response = requests.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json={
            "center_lat": 46.85,
            "center_lng": -71.25,
            "species": "CERF",
            "month": 10
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('engine') == 'CORRIDORS-V10', f"Engine should be CORRIDORS-V10, got {data.get('engine')}"
        assert data.get('version') == '10.0.0', f"Version should be 10.0.0, got {data.get('version')}"


class TestV10PolygonExtent:
    """Tests for zone polygon geographic extent (dimension dynamique)"""

    def _haversine(self, lat1, lon1, lat2, lon2):
        """Calculate distance in meters between two lat/lng points"""
        from math import radians, cos, sin, sqrt, atan2
        R = 6371000
        phi1, phi2 = radians(lat1), radians(lat2)
        dphi = radians(lat2 - lat1)
        dlam = radians(lon2 - lon1)
        a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlam/2)**2
        return 2 * R * atan2(sqrt(a), sqrt(1-a))

    def test_polygon_extent_large_organic(self):
        """Zone polygons should be large (800-1500m extent) from merged clusters"""
        response = requests.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json={
            "center_lat": 46.85,
            "center_lng": -71.25,
            "species": "CERF",
            "month": 10
        })
        assert response.status_code == 200
        
        data = response.json()
        features = data.get('geojson', {}).get('features', [])
        polygons = [f for f in features if f['geometry']['type'] == 'Polygon']
        
        extents = []
        for p in polygons:
            coords = p['geometry']['coordinates'][0]
            lats = [c[1] for c in coords]
            lngs = [c[0] for c in coords]
            extent_m = self._haversine(min(lats), min(lngs), max(lats), max(lngs))
            extents.append(extent_m)
            # Large merged clusters should have 800-1800m extent
            assert extent_m >= 600, f"Polygon extent {extent_m}m too small, expected >= 600m"
            assert extent_m <= 2000, f"Polygon extent {extent_m}m too large, expected <= 2000m"
        
        avg_extent = sum(extents) / len(extents)
        print(f"Average polygon extent: {int(avg_extent)}m")
        assert avg_extent >= 1000, f"Average extent {int(avg_extent)}m too small for merged clusters"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
