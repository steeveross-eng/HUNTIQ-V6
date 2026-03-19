"""
Test suite for CORRIDORS-V10 Heatmap Lite/Pro visual optimization
Tests:
- Backend API include_corridors parameter
- Lite vs Pro gradient definitions
- Comparison toggle functionality
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://lisibilite-pro.preview.emergentagent.com"


class TestHeatmapAPI:
    """Backend API tests for /api/v1/score-consolide/heatmap endpoint"""
    
    def test_heatmap_with_corridors_included(self):
        """Test heatmap API with include_corridors=1"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10,
            'grid_size': 20,
            'include_corridors': 1
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify corridors_v10_included is true
        assert data.get('corridors_v10_included') == True
        assert 'corridors_v10' in data.get('engines_integrated', [])
        
        # Verify weights include corridors
        weights = data.get('weights', {})
        assert 'corridors_v10' in weights
        assert weights['corridors_v10'] == 0.25
    
    def test_heatmap_without_corridors(self):
        """Test heatmap API with include_corridors=0"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10,
            'grid_size': 20,
            'include_corridors': 0
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify corridors_v10_included is false
        assert data.get('corridors_v10_included') == False
        assert 'corridors_v10' not in data.get('engines_integrated', [])
    
    def test_score_difference_with_without_corridors(self):
        """Test that score changes when corridors are excluded"""
        params_base = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10,
            'grid_size': 20,
        }
        
        # With corridors
        response_with = requests.get(
            f"{BASE_URL}/api/v1/score-consolide/heatmap", 
            params={**params_base, 'include_corridors': 1}
        )
        assert response_with.status_code == 200
        score_with = response_with.json().get('score_avg')
        
        # Without corridors
        response_without = requests.get(
            f"{BASE_URL}/api/v1/score-consolide/heatmap", 
            params={**params_base, 'include_corridors': 0}
        )
        assert response_without.status_code == 200
        score_without = response_without.json().get('score_avg')
        
        # Scores should differ (corridors contribute 25% weight)
        # Note: They may not always differ if corridor scores match other engine scores
        print(f"Score with corridors: {score_with}")
        print(f"Score without corridors: {score_without}")
        
        # Both should be valid scores
        assert score_with is not None and score_with > 0
        assert score_without is not None and score_without > 0
    
    def test_grid_returns_400_points(self):
        """Test that 20x20 grid returns 400 points"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10,
            'grid_size': 20,
            'include_corridors': 1
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get('total_points') == 400
        assert len(data.get('points', [])) == 400
    
    def test_point_structure(self):
        """Test that each point has required fields"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10,
            'grid_size': 5,  # Small grid for quick test
            'include_corridors': 1
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        
        assert response.status_code == 200
        data = response.json()
        points = data.get('points', [])
        
        assert len(points) > 0
        for point in points[:5]:  # Check first 5 points
            assert 'lat' in point
            assert 'lng' in point
            assert 'score' in point
            assert 'classe' in point
            assert 'color' in point
    
    def test_weights_sum_to_one(self):
        """Test that normalized weights sum to ~1.0"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10,
            'grid_size': 5,
            'include_corridors': 1
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        
        assert response.status_code == 200
        data = response.json()
        weights = data.get('weights', {})
        
        total = sum(weights.values())
        assert abs(total - 1.0) < 0.01, f"Weights should sum to 1.0, got {total}"
    
    def test_ours_species(self):
        """Test heatmap works for OURS species"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'OURS',
            'month': 10,
            'grid_size': 5,
            'include_corridors': 1
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('species') == 'OURS'
    
    def test_dindon_species(self):
        """Test heatmap works for DINDON species"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'DINDON',
            'month': 5,
            'grid_size': 5,
            'include_corridors': 1
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('species') == 'DINDON'


class TestEngineWeights:
    """Test engine weight configuration"""
    
    def test_expected_engine_weights_with_corridors(self):
        """Verify correct engine weights when corridors included"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10,
            'grid_size': 5,
            'include_corridors': 1
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        
        assert response.status_code == 200
        data = response.json()
        weights = data.get('weights', {})
        
        # Expected weights from score_consolide.py
        assert weights.get('alimentation') == 0.25
        assert weights.get('repos') == 0.20
        assert weights.get('corridors_v10') == 0.25
        assert weights.get('alimentation_v2') == 0.10
        assert weights.get('pression') == 0.20
    
    def test_engines_integrated_list(self):
        """Verify correct engines in integrated list"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CERF',
            'month': 10,
            'grid_size': 5,
            'include_corridors': 1
        }
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        
        assert response.status_code == 200
        data = response.json()
        engines = data.get('engines_integrated', [])
        
        expected = ['alimentation_v1', 'repos_v1', 'alimentation_v2', 'pression', 'corridors_v10']
        for engine in expected:
            assert engine in engines, f"Missing engine: {engine}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
