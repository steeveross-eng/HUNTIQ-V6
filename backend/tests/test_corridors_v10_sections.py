"""
CORRIDORS-V10 STEEVE-MAX + BCE-4X Sections 2-6 Backend Tests
=============================================================
Tests for:
- S5: weather_official field in guide-pro API
- API endpoint health checks
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestGuideProAPI:
    """Section 5: Backend /api/v3/intelligence/guide-pro weather_official tests"""
    
    def test_guide_pro_returns_weather_official(self):
        """S5: Verify guide-pro returns weather_official field"""
        params = {
            'lat': 46.8139,
            'lng': -71.2080,
            'species': 'CHEVREUIL',
            'month': 1
        }
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/guide-pro", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'weather_official' in data, "weather_official field missing from response"
        
        wo = data['weather_official']
        assert 'temperature' in wo, "temperature missing from weather_official"
        assert 'wind_direction_deg' in wo, "wind_direction_deg missing from weather_official"
        assert 'wind_speed_kmh' in wo, "wind_speed_kmh missing from weather_official"
        assert 'wind_force' in wo, "wind_force missing from weather_official"
        
    def test_weather_official_temperature_is_numeric(self):
        """S5: Temperature should be a numeric value"""
        params = {'lat': 46.8139, 'lng': -71.2080, 'species': 'CHEVREUIL', 'month': 1}
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/guide-pro", params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        temp = data['weather_official']['temperature']
        assert isinstance(temp, (int, float)), f"Temperature should be numeric, got {type(temp)}"
        # Temperature should be reasonable for Quebec in January (-40 to 10)
        assert -50 <= temp <= 20, f"Temperature {temp} seems unreasonable for Quebec January"
        
    def test_weather_official_wind_data(self):
        """S5: Wind data should be valid"""
        params = {'lat': 46.8139, 'lng': -71.2080, 'species': 'CHEVREUIL', 'month': 6}
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/guide-pro", params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        wo = data['weather_official']
        assert 0 <= wo['wind_direction_deg'] <= 360, "Wind direction should be 0-360 degrees"
        assert wo['wind_speed_kmh'] >= 0, "Wind speed should be non-negative"
        assert wo['wind_force'] in ['faible', 'modere', 'fort'], f"Unexpected wind force: {wo['wind_force']}"
        
    def test_guide_pro_terrain_score(self):
        """S4: Terrain consolidated score present"""
        params = {'lat': 46.8139, 'lng': -71.2080, 'species': 'CHEVREUIL', 'month': 10}
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/guide-pro", params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'terrain' in data, "terrain field missing"
        terrain = data['terrain']
        assert 'consolidated_score' in terrain, "consolidated_score missing from terrain"
        assert 0 <= terrain['consolidated_score'] <= 100, "Score should be 0-100"
        
    def test_guide_pro_hunting_windows(self):
        """S6: hunting_windows for HEURES HOT"""
        params = {'lat': 46.8139, 'lng': -71.2080, 'species': 'CHEVREUIL', 'month': 10}
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/guide-pro", params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'hunting_windows' in data, "hunting_windows missing"
        # Should have at least some windows
        hw = data['hunting_windows']
        assert isinstance(hw, list), "hunting_windows should be a list"
        
        if len(hw) > 0:
            window = hw[0]
            assert 'start' in window, "start missing from hunting window"
            assert 'end' in window, "end missing from hunting window"
            assert 'intensity' in window, "intensity missing from hunting window"
            assert 'duration_min' in window, "duration_min missing"
            assert 'source' in window, "source missing"


class TestIntelligenceSummaryAPI:
    """Intelligence summary API tests"""
    
    def test_summary_endpoint(self):
        """Test summary endpoint returns consolidated score"""
        params = {'lat': 46.8139, 'lng': -71.2080, 'species': 'CHEVREUIL', 'month': 10}
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/summary", params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'consolidated' in data
        assert 'score' in data['consolidated']
        assert 'classe' in data['consolidated']


class TestSolunarAPI:
    """Solunar endpoint tests"""
    
    def test_solunar_returns_curve(self):
        """Solunar should return 24h curve for chart"""
        params = {'lat': 46.8139, 'lng': -71.2080}
        response = requests.get(f"{BASE_URL}/api/v3/intelligence/solunar", params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'curve_24h' in data, "curve_24h missing"
        assert 'hunting_windows' in data, "hunting_windows missing"
        assert 'solunar_score' in data, "solunar_score missing"


class TestEngineRegistry:
    """Engine registry tests"""
    
    def test_registry_endpoint(self):
        """Registry should return manifest"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/registry")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'engines' in data
        assert isinstance(data['engines'], list)
        assert len(data['engines']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
