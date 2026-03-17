"""
V10 Zone Polygons API Tests - Iteration 34
=========================================
Verify that V10 engine generates Polygon geometry for zones instead of Point.
All 64 zones should be Polygon features with correct properties.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestV10ZonePolygons:
    """Test V10 zone polygon generation - BCE-4X / Steeve-MAX"""

    def test_api_returns_polygon_geometry_not_points(self):
        """Verify API returns Polygon geometry for zones, not Point"""
        response = requests.post(
            f"{BASE_URL}/api/v10/corridors/analyze-full",
            json={
                "center_lat": 46.85,
                "center_lng": -71.25,
                "species": "CERF",
                "month": 10
            },
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        assert response.status_code == 200, f"API returned {response.status_code}"
        data = response.json()
        
        features = data.get('geojson', {}).get('features', [])
        assert len(features) > 0, "No features returned"
        
        polygons = [f for f in features if f['geometry']['type'] == 'Polygon']
        points = [f for f in features if f['geometry']['type'] == 'Point']
        
        # Key assertion: 64 Polygons, 0 Points
        assert len(polygons) == 64, f"Expected 64 Polygon features, got {len(polygons)}"
        assert len(points) == 0, f"Expected 0 Point features, got {len(points)}"

    def test_polygon_has_required_properties(self):
        """Verify each Polygon has zone_type, score, color, center_lat, center_lng"""
        response = requests.post(
            f"{BASE_URL}/api/v10/corridors/analyze-full",
            json={"center_lat": 46.85, "center_lng": -71.25, "species": "CERF", "month": 10},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        features = data.get('geojson', {}).get('features', [])
        polygons = [f for f in features if f['geometry']['type'] == 'Polygon']
        
        required_props = ['zone_type', 'score', 'color', 'center_lat', 'center_lng', 'species']
        
        for i, polygon in enumerate(polygons[:10]):  # Check first 10
            props = polygon.get('properties', {})
            for prop in required_props:
                assert prop in props, f"Polygon {i} missing property '{prop}'"
            
            # Verify values are valid
            assert props['zone_type'] in ['alimentation', 'repos', 'rut', 'eau'], f"Invalid zone_type: {props['zone_type']}"
            assert isinstance(props['score'], (int, float)), f"score should be numeric, got {type(props['score'])}"
            assert props['color'].startswith('#'), f"color should be hex, got {props['color']}"
            assert isinstance(props['center_lat'], (int, float)), f"center_lat should be numeric"
            assert isinstance(props['center_lng'], (int, float)), f"center_lng should be numeric"

    def test_polygon_has_valid_coordinates(self):
        """Verify Polygon coordinates form a valid closed ring"""
        response = requests.post(
            f"{BASE_URL}/api/v10/corridors/analyze-full",
            json={"center_lat": 46.85, "center_lng": -71.25, "species": "CERF", "month": 10},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        features = data.get('geojson', {}).get('features', [])
        polygons = [f for f in features if f['geometry']['type'] == 'Polygon']
        
        for i, polygon in enumerate(polygons[:10]):  # Check first 10
            coords = polygon['geometry']['coordinates']
            assert len(coords) >= 1, f"Polygon {i} has no coordinate rings"
            
            ring = coords[0]  # Outer ring
            assert len(ring) >= 4, f"Polygon {i} outer ring has less than 4 points"
            
            # Check ring is closed (first == last)
            first_point = ring[0]
            last_point = ring[-1]
            assert first_point == last_point, f"Polygon {i} ring is not closed"
            
            # Check coordinates are valid lat/lng
            for point in ring:
                assert len(point) == 2, f"Point should have 2 coordinates"
                lng, lat = point
                assert -180 <= lng <= 180, f"Invalid longitude: {lng}"
                assert -90 <= lat <= 90, f"Invalid latitude: {lat}"

    def test_corridors_still_linestrings(self):
        """Verify corridors are still LineString geometry"""
        response = requests.post(
            f"{BASE_URL}/api/v10/corridors/analyze-full",
            json={"center_lat": 46.85, "center_lng": -71.25, "species": "CERF", "month": 10},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        features = data.get('geojson', {}).get('features', [])
        linestrings = [f for f in features if f['geometry']['type'] == 'LineString']
        
        # Should have corridors as LineStrings
        assert len(linestrings) > 0, "No corridor LineStrings found"
        
        # Check corridor has required properties
        corridor = linestrings[0]
        props = corridor.get('properties', {})
        assert 'niveau' in props, "Corridor missing 'niveau' property"
        assert 'color' in props, "Corridor missing 'color' property"
        assert 'largeur_m' in props, "Corridor missing 'largeur_m' property"

    def test_zone_colors_match_bce4x_palette(self):
        """Verify zone colors match BCE-4X normative palette"""
        response = requests.post(
            f"{BASE_URL}/api/v10/corridors/analyze-full",
            json={"center_lat": 46.85, "center_lng": -71.25, "species": "CERF", "month": 10},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # BCE-4X normative zone colors
        expected_colors = {
            'alimentation': '#4CAF50',
            'repos': '#2196F3',
            'rut': '#FF5722',
            'eau': '#00BCD4',
        }
        
        features = data.get('geojson', {}).get('features', [])
        polygons = [f for f in features if f['geometry']['type'] == 'Polygon']
        
        for polygon in polygons[:20]:
            props = polygon.get('properties', {})
            zone_type = props.get('zone_type')
            color = props.get('color')
            
            if zone_type in expected_colors:
                assert color == expected_colors[zone_type], \
                    f"Zone '{zone_type}' color mismatch: expected {expected_colors[zone_type]}, got {color}"

    def test_corridor_levels_bce4x_compliance(self):
        """Verify corridor levels and colors follow backend classifier palette"""
        response = requests.post(
            f"{BASE_URL}/api/v10/corridors/analyze-full",
            json={"center_lat": 46.85, "center_lng": -71.25, "species": "CERF", "month": 10},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Backend classifier.py palette (CORRIDOR_LEVELS)
        # Note: Frontend BionicCorridorsV10Layer uses its own palette for rendering
        corridor_colors = {
            'CRITIQUE': '#CC0000',  # Backend uses #CC0000, frontend renders #B80000
            'MAJEUR': '#FF0000',
            'FORT': '#FF8C00',
            'MODERE': '#FFD700',
            'FAIBLE': '#BFBFBF',
        }
        
        features = data.get('geojson', {}).get('features', [])
        corridors = [f for f in features if f['geometry']['type'] == 'LineString']
        
        niveau_counts = {}
        for corridor in corridors:
            niveau = corridor['properties'].get('niveau')
            color = corridor['properties'].get('color')
            
            # Count levels
            niveau_counts[niveau] = niveau_counts.get(niveau, 0) + 1
            
            # Verify color matches level
            if niveau in corridor_colors:
                assert color == corridor_colors[niveau], \
                    f"Corridor niveau '{niveau}' color mismatch: expected {corridor_colors[niveau]}, got {color}"
        
        print(f"Niveau distribution: {niveau_counts}")
        
        # Should have multiple levels represented
        assert len(niveau_counts) >= 2, f"Expected at least 2 corridor levels, got {niveau_counts}"


class TestV10FrontendIntegration:
    """Test frontend-relevant API data"""

    def test_api_response_structure_for_frontend(self):
        """Verify response has all required fields for frontend rendering"""
        response = requests.post(
            f"{BASE_URL}/api/v10/corridors/analyze-full",
            json={"center_lat": 46.85, "center_lng": -71.25, "species": "CERF", "month": 10},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Required top-level fields
        assert 'geojson' in data, "Missing 'geojson' field"
        assert 'niveau_distribution' in data, "Missing 'niveau_distribution' field"
        assert 'score_corridor' in data, "Missing 'score_corridor' field"
        assert 'continuity' in data, "Missing 'continuity' field"
        
        # GeoJSON structure
        geojson = data['geojson']
        assert geojson['type'] == 'FeatureCollection', "GeoJSON should be FeatureCollection"
        assert 'features' in geojson, "GeoJSON missing features"

    def test_zone_center_coordinates_within_polygon(self):
        """Verify center_lat/center_lng are approximately within polygon bounds"""
        response = requests.post(
            f"{BASE_URL}/api/v10/corridors/analyze-full",
            json={"center_lat": 46.85, "center_lng": -71.25, "species": "CERF", "month": 10},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        features = data.get('geojson', {}).get('features', [])
        polygons = [f for f in features if f['geometry']['type'] == 'Polygon']
        
        for i, polygon in enumerate(polygons[:5]):  # Check first 5
            props = polygon.get('properties', {})
            center_lat = props.get('center_lat')
            center_lng = props.get('center_lng')
            
            # Get polygon bounds
            ring = polygon['geometry']['coordinates'][0]
            lngs = [p[0] for p in ring]
            lats = [p[1] for p in ring]
            
            min_lat, max_lat = min(lats), max(lats)
            min_lng, max_lng = min(lngs), max(lngs)
            
            # Center should be approximately within bounds (with small tolerance for edge cases)
            tolerance = 0.001  # ~100m
            assert min_lat - tolerance <= center_lat <= max_lat + tolerance, \
                f"Polygon {i} center_lat {center_lat} outside bounds [{min_lat}, {max_lat}]"
            assert min_lng - tolerance <= center_lng <= max_lng + tolerance, \
                f"Polygon {i} center_lng {center_lng} outside bounds [{min_lng}, {max_lng}]"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
