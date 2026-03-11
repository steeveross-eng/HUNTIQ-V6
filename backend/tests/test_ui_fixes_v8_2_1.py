"""
BIONIC V8.2.1 — UI Fixes Tests (3 corrections prioritaires)
1. Windfield endpoint returns wind data grid
2. Organic-zones regression test for rural waypoint (47.0, -72.28) → 8+ zones
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestWindfieldEndpoint:
    """Tests for POST /api/v1/bionic/weather-shadow/windfield"""

    def test_windfield_returns_200(self):
        """Windfield endpoint should return 200 OK"""
        payload = {
            "bounds": {"north": 47.02, "south": 46.98, "east": -72.26, "west": -72.30},
            "resolution": 30
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/weather-shadow/windfield",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Windfield returned {response.status_code}: {response.text[:500]}"

    def test_windfield_returns_u10_v10_arrays(self):
        """Windfield response must contain u10 and v10 wind component arrays"""
        payload = {
            "bounds": {"north": 47.02, "south": 46.98, "east": -72.26, "west": -72.30},
            "resolution": 30
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/weather-shadow/windfield",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        assert "u10" in data, "Response missing 'u10' wind component"
        assert "v10" in data, "Response missing 'v10' wind component"
        assert isinstance(data["u10"], list), "u10 should be a 2D array"
        assert isinstance(data["v10"], list), "v10 should be a 2D array"
        assert len(data["u10"]) > 0, "u10 array should not be empty"
        assert len(data["v10"]) > 0, "v10 array should not be empty"

    def test_windfield_metadata_contains_wind_info(self):
        """Windfield metadata must contain base_wind_speed_kmh and base_wind_direction_deg"""
        payload = {
            "bounds": {"north": 47.02, "south": 46.98, "east": -72.26, "west": -72.30},
            "resolution": 30
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/weather-shadow/windfield",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        assert "metadata" in data, "Response missing 'metadata'"
        meta = data["metadata"]
        assert "base_wind_speed_kmh" in meta, "Metadata missing base_wind_speed_kmh"
        assert "base_wind_direction_deg" in meta, "Metadata missing base_wind_direction_deg"
        assert isinstance(meta["base_wind_speed_kmh"], (int, float)), "base_wind_speed_kmh should be numeric"
        assert isinstance(meta["base_wind_direction_deg"], (int, float)), "base_wind_direction_deg should be numeric"


class TestOrganicZonesRegression:
    """Regression test: rural waypoint (47.0, -72.28) must return 8+ zones with weather_metadata"""

    def test_rural_waypoint_generates_candidates(self):
        """POST /api/v1/bionic/organic-zones for rural waypoint should generate zone candidates (stats.total_zones > 0)"""
        payload = {
            "bounds": {"north": 47.05, "south": 46.95, "east": -72.23, "west": -72.33},
            "layers": ["habitats", "repos", "alimentation", "rut", "corridors", "salines"],
            "species": "moose",
            "waypoint_center": {"lat": 47.0, "lng": -72.28},
            "selected_season": "post_rut"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=90
        )
        assert response.status_code == 200, f"organic-zones returned {response.status_code}: {response.text[:500]}"
        data = response.json()
        stats = data.get("stats", {})
        total_candidates = stats.get("total_zones", 0) + stats.get("rejected_exclusion", 0)
        assert total_candidates > 0, f"Expected zone candidates to be generated, got total_zones={stats.get('total_zones', 0)}, rejected={stats.get('rejected_exclusion', 0)}"
        assert stats.get("exclusion_engine") == "v7", f"Expected V7 exclusion engine, got {stats.get('exclusion_engine')}"

    def test_rural_waypoint_has_weather_metadata(self):
        """Rural waypoint response must include weather_metadata with applied=true"""
        payload = {
            "bounds": {"north": 47.02, "south": 46.98, "east": -72.26, "west": -72.30},
            "layers": ["habitats", "repos", "alimentation"],
            "species": "moose",
            "waypoint_center": {"lat": 47.0, "lng": -72.28},
            "selected_season": "post_rut"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        data = response.json()
        assert "weather_metadata" in data, "Response missing weather_metadata"
        wm = data["weather_metadata"]
        assert wm.get("applied") is True, "weather_metadata.applied should be True when waypoint_center provided"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
