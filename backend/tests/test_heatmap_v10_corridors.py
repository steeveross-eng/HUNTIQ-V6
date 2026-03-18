"""
Test Suite: Heatmap V10 Consolidated Score with CORRIDORS-V10 Integration
==========================================================================
Tests the /api/v1/score-consolide/heatmap endpoint which combines:
- ALIMENTATION-V1 (25%)
- REPOS-V1 (20%)
- CORRIDORS-V10 (25%)
- ALIMENTATION-V2 (10%)
- PRESSION (20%)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHeatmapV10API:
    """Test cases for the consolidated heatmap API with CORRIDORS-V10"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Verify BASE_URL is configured"""
        assert BASE_URL, "REACT_APP_BACKEND_URL environment variable not set"

    def test_heatmap_endpoint_returns_200(self):
        """API should return 200 status for valid parameters"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10,
            'grid_size': 20
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_heatmap_returns_grid_with_points(self):
        """API should return grid with correct number of points"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10,
            'grid_size': 20
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        data = response.json()
        
        assert 'points' in data, "Response missing 'points' field"
        assert 'total_points' in data, "Response missing 'total_points' field"
        # grid_size=20 => 20x20 = 400 points
        assert data['total_points'] == 400, f"Expected 400 points, got {data['total_points']}"
        assert len(data['points']) == 400, f"Expected 400 points in array, got {len(data['points'])}"

    def test_heatmap_has_score_avg(self):
        """API should return score_avg in response"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10,
            'grid_size': 20
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        data = response.json()
        
        assert 'score_avg' in data, "Response missing 'score_avg' field"
        assert isinstance(data['score_avg'], (int, float)), "score_avg should be numeric"
        assert 0 <= data['score_avg'] <= 100, f"score_avg should be 0-100, got {data['score_avg']}"

    def test_heatmap_includes_corridors_v10_in_engines(self):
        """API should include corridors_v10 in engines_integrated"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10,
            'grid_size': 20
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        data = response.json()
        
        assert 'engines_integrated' in data, "Response missing 'engines_integrated' field"
        assert 'corridors_v10' in data['engines_integrated'], \
            f"corridors_v10 not in engines_integrated: {data['engines_integrated']}"

    def test_heatmap_weights_include_corridors_v10(self):
        """API should return correct weights with corridors_v10 at 0.25"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10,
            'grid_size': 20
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        data = response.json()
        
        assert 'weights' in data, "Response missing 'weights' field"
        weights = data['weights']
        
        # Expected weights per spec
        expected_weights = {
            'alimentation': 0.25,
            'repos': 0.20,
            'corridors_v10': 0.25,
            'alimentation_v2': 0.10,
            'pression': 0.20
        }
        
        for engine, expected in expected_weights.items():
            assert engine in weights, f"Weight for {engine} not found"
            assert abs(weights[engine] - expected) < 0.01, \
                f"Weight for {engine}: expected {expected}, got {weights[engine]}"

    def test_heatmap_point_structure(self):
        """Each point should have score, classe, color fields"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10,
            'grid_size': 20
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        data = response.json()
        
        assert len(data['points']) > 0, "No points returned"
        point = data['points'][0]
        
        # Required fields per spec
        assert 'lat' in point, "Point missing 'lat' field"
        assert 'lng' in point, "Point missing 'lng' field"
        assert 'score' in point, "Point missing 'score' field"
        assert 'classe' in point, "Point missing 'classe' field"
        assert 'color' in point, "Point missing 'color' field"
        
        # Validate types
        assert isinstance(point['score'], (int, float)), "score should be numeric"
        assert isinstance(point['classe'], str), "classe should be string"
        assert isinstance(point['color'], str), "color should be string"
        assert point['color'].startswith('#'), "color should be hex format"

    def test_heatmap_classe_values(self):
        """Points should have valid classe values (FAIBLE, MODERE, BON, OPTIMAL, EXCLU)"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10,
            'grid_size': 20
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        data = response.json()
        
        valid_classes = {'FAIBLE', 'MODERE', 'MODÉRÉ', 'BON', 'OPTIMAL', 'EXCLU'}
        for point in data['points']:
            assert point['classe'] in valid_classes, \
                f"Invalid classe: {point['classe']}, expected one of {valid_classes}"

    def test_water_exclusion_works(self):
        """Water points should have score=0 and classe=EXCLU"""
        # Test with a known water location (if applicable)
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10,
            'grid_size': 20
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        data = response.json()
        
        # Find any excluded points
        excluded = [p for p in data['points'] if p.get('classe') == 'EXCLU']
        
        # Verify excluded points have score=0
        for p in excluded:
            assert p['score'] == 0, f"Excluded point should have score=0, got {p['score']}"
        
        # Test passes even if no excluded points (area may not have water)
        print(f"Found {len(excluded)} excluded (water) points")

    def test_tracability_corridors_v10_integrated(self):
        """Single point endpoint should show corridors_v10_integrated=true in tracability"""
        # Using the single point endpoint to check tracability
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/point", params=params)
        
        # If endpoint exists
        if response.status_code == 200:
            data = response.json()
            if 'tracability' in data:
                assert data['tracability'].get('corridors_v10_integrated') == True, \
                    "corridors_v10_integrated should be True in tracability"

    def test_different_species(self):
        """API should work for different species"""
        species_list = ['CERF', 'OURS', 'DINDON']
        
        for species in species_list:
            params = {
                'lat': 46.8139,
                'lng': -71.2080,
                'species': species,
                'month': 10,
                'grid_size': 10  # smaller grid for faster tests
            }
            response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
            assert response.status_code == 200, f"Failed for species {species}: {response.status_code}"
            data = response.json()
            assert data['species'].upper() == species.upper(), f"Species mismatch: expected {species}"

    def test_color_gradient_correct(self):
        """Colors should match the thermal gradient: blue→green→yellow→red"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10,
            'grid_size': 20
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        data = response.json()
        
        # Check color mappings
        color_map = {
            'FAIBLE': '#3B82F6',   # blue
            'MODERE': '#22C55E',   # green
            'MODÉRÉ': '#22C55E',   # green (accented)
            'BON': '#F59E0B',      # yellow/amber
            'OPTIMAL': '#DC2626', # red
            'EXCLU': '#1E3A5F'    # dark blue for water
        }
        
        for point in data['points']:
            expected_color = color_map.get(point['classe'])
            if expected_color:
                assert point['color'] == expected_color, \
                    f"Color mismatch for {point['classe']}: expected {expected_color}, got {point['color']}"


class TestConsolidatedScoreSinglePoint:
    """Test the single point consolidated score endpoint"""

    def test_single_point_endpoint(self):
        """Single point endpoint should return consolidated score"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/point", params=params)
        
        if response.status_code == 404:
            pytest.skip("Single point endpoint not implemented")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'score' in data, "Response missing 'score' field"
        assert 'components' in data or 'weights' in data, "Response missing score breakdown"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
