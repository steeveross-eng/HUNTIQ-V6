"""
BIONIC V8.3.A — Compare Waypoints API Tests
Tests for POST /api/v1/compare/waypoints endpoint.
Verifies: Multi-waypoint comparison, scores, zones, corridors, weather, anthropic pressure.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestCompareWaypointsAPI:
    """Tests for the compare waypoints endpoint."""

    def test_compare_two_waypoints_success(self):
        """POST /api/v1/compare/waypoints with 2 waypoints returns valid comparison."""
        payload = {
            "waypoints": [
                {"id": "wp1", "name": "Test Rural WP V821", "lat": 47.0005, "lng": -72.2800},
                {"id": "wp2", "name": "Test Backend WP", "lat": 46.8190, "lng": -71.2390}
            ]
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/compare/waypoints",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # Long timeout for zone generation
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "comparison" in data, "Response should contain 'comparison' array"
        assert "waypoint_count" in data, "Response should contain 'waypoint_count'"
        assert "total_computation_ms" in data, "Response should contain 'total_computation_ms'"
        
        # Verify comparison array has 2 items
        assert len(data["comparison"]) == 2, f"Expected 2 comparison items, got {len(data['comparison'])}"
        
        # Verify each comparison item structure
        for item in data["comparison"]:
            assert "waypoint" in item, "Each comparison item should have 'waypoint'"
            if "error" not in item:  # Success case
                assert "scores" in item, "Comparison item should have 'scores'"
                assert "zones" in item, "Comparison item should have 'zones'"
                assert "corridors" in item, "Comparison item should have 'corridors'"
                assert "weather" in item, "Comparison item should have 'weather'"
                assert "anthropic_pressure" in item, "Comparison item should have 'anthropic_pressure'"
        
        print(f"✓ Compare 2 waypoints: {data['waypoint_count']} WPs compared in {data['total_computation_ms']}ms")

    def test_compare_three_waypoints_success(self):
        """POST /api/v1/compare/waypoints with 3 waypoints returns valid comparison."""
        payload = {
            "waypoints": [
                {"id": "wp1", "name": "WP North", "lat": 47.1, "lng": -72.5},
                {"id": "wp2", "name": "WP Central", "lat": 46.9, "lng": -72.3},
                {"id": "wp3", "name": "WP South", "lat": 46.7, "lng": -72.1}
            ]
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/compare/waypoints",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=180  # Even longer timeout for 3 waypoints
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert len(data["comparison"]) == 3, f"Expected 3 comparison items, got {len(data['comparison'])}"
        
        print(f"✓ Compare 3 waypoints: {data['waypoint_count']} WPs compared in {data['total_computation_ms']}ms")

    def test_compare_validates_min_waypoints(self):
        """POST /api/v1/compare/waypoints with 1 waypoint should fail validation."""
        payload = {
            "waypoints": [
                {"id": "wp1", "name": "Single WP", "lat": 47.0, "lng": -72.0}
            ]
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/compare/waypoints",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        # Should return 422 (validation error) since min_length=2
        assert response.status_code == 422, f"Expected 422 for 1 waypoint, got {response.status_code}"
        print("✓ Validation: Rejects single waypoint request")

    def test_compare_validates_max_waypoints(self):
        """POST /api/v1/compare/waypoints with 4+ waypoints should fail validation."""
        payload = {
            "waypoints": [
                {"id": "wp1", "name": "WP1", "lat": 47.0, "lng": -72.0},
                {"id": "wp2", "name": "WP2", "lat": 47.1, "lng": -72.1},
                {"id": "wp3", "name": "WP3", "lat": 47.2, "lng": -72.2},
                {"id": "wp4", "name": "WP4", "lat": 47.3, "lng": -72.3}
            ]
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/compare/waypoints",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        # Should return 422 (validation error) since max_length=3
        assert response.status_code == 422, f"Expected 422 for 4 waypoints, got {response.status_code}"
        print("✓ Validation: Rejects 4+ waypoints request")

    def test_compare_returns_score_structure(self):
        """Verify comparison returns proper score structure with global and by_category."""
        payload = {
            "waypoints": [
                {"id": "wp1", "name": "Score Test WP1", "lat": 47.0005, "lng": -72.2800},
                {"id": "wp2", "name": "Score Test WP2", "lat": 46.8190, "lng": -71.2390}
            ]
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/compare/waypoints",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for item in data["comparison"]:
            if "error" not in item:
                scores = item.get("scores", {})
                assert "global" in scores, "Scores should have 'global'"
                assert "by_category" in scores, "Scores should have 'by_category'"
                assert isinstance(scores["global"], (int, float)), "Global score should be numeric"
                assert isinstance(scores["by_category"], dict), "by_category should be dict"
                
                # Global score should be 0-100
                assert 0 <= scores["global"] <= 100, f"Global score {scores['global']} out of range"
        
        print("✓ Score structure: global + by_category verified")

    def test_compare_returns_weather_data(self):
        """Verify comparison includes weather data for each waypoint."""
        payload = {
            "waypoints": [
                {"id": "wp1", "name": "Weather Test WP1", "lat": 47.0, "lng": -72.28},
                {"id": "wp2", "name": "Weather Test WP2", "lat": 46.82, "lng": -71.24}
            ]
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/compare/waypoints",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for item in data["comparison"]:
            if "error" not in item:
                weather = item.get("weather", {})
                # Weather should have temperature_c field (may be null if API failed)
                assert "temperature_c" in weather, "Weather should have 'temperature_c'"
                assert "wind_speed_kmh" in weather, "Weather should have 'wind_speed_kmh'"
                assert "condition" in weather, "Weather should have 'condition'"
        
        print("✓ Weather data: Verified weather structure in comparison")

    def test_compare_returns_anthropic_pressure(self):
        """Verify comparison includes anthropic pressure analysis."""
        payload = {
            "waypoints": [
                {"id": "wp1", "name": "Pressure Test WP1", "lat": 47.0, "lng": -72.28},
                {"id": "wp2", "name": "Pressure Test WP2", "lat": 46.82, "lng": -71.24}
            ]
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/compare/waypoints",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for item in data["comparison"]:
            if "error" not in item:
                pressure = item.get("anthropic_pressure", {})
                assert "rejections" in pressure, "Pressure should have 'rejections'"
                assert "level" in pressure, "Pressure should have 'level'"
                # Level should be one of: faible, modérée, élevée
                assert pressure["level"] in ["faible", "modérée", "élevée"], f"Unexpected level: {pressure['level']}"
        
        print("✓ Anthropic pressure: Verified pressure structure")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
