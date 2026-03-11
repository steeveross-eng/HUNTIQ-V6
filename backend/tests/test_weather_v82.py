"""
BIONIC V8.2 Weather API Tests
Tests for Weather V8.2 feature with OpenWeatherMap integration and cache TTL 30min.

Endpoints tested:
  - GET /api/v1/weather/now?lat=X&lng=Y     — Current weather (cache 30min)
  - GET /api/v1/weather/forecast?lat=X&lng=Y — 5-day/3h forecast (cache 30min)
  - GET /api/v1/weather/influence?lat=X&lng=Y — Weather influence on scoring
  - GET /api/v1/weather/cache-stats          — Cache statistics

Additional tests:
  - Cache hit verification (from_cache=True on second call)
  - Invalid params handling
  - Organic-zones regression (V7 engine still works)
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test coordinates (Quebec region)
TEST_LAT = 47.0
TEST_LNG = -72.28


class TestWeatherNowEndpoint:
    """Tests for GET /api/v1/weather/now"""

    def test_weather_now_returns_valid_snapshot(self):
        """Test that /api/v1/weather/now returns valid weather data"""
        response = requests.get(
            f"{BASE_URL}/api/v1/weather/now",
            params={"lat": TEST_LAT, "lng": TEST_LNG}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Required fields
        assert "temperature_c" in data, "Missing temperature_c"
        assert "wind_speed_kmh" in data, "Missing wind_speed_kmh"
        assert "pressure_hpa" in data, "Missing pressure_hpa"
        assert "from_cache" in data, "Missing from_cache"
        
        # Validate data types
        assert isinstance(data["temperature_c"], (int, float)), "temperature_c should be numeric"
        assert isinstance(data["wind_speed_kmh"], (int, float)), "wind_speed_kmh should be numeric"
        assert isinstance(data["pressure_hpa"], (int, float)), "pressure_hpa should be numeric"
        
        # Validate reasonable ranges
        assert -50 < data["temperature_c"] < 50, f"Temperature out of range: {data['temperature_c']}"
        assert 0 <= data["wind_speed_kmh"] < 200, f"Wind speed out of range: {data['wind_speed_kmh']}"
        assert 900 < data["pressure_hpa"] < 1100, f"Pressure out of range: {data['pressure_hpa']}"
        
        print(f"✓ Weather snapshot: {data['temperature_c']}°C, wind {data['wind_speed_kmh']}km/h, pressure {data['pressure_hpa']}hPa")

    def test_weather_now_cache_hit(self):
        """Test that second call with same coords returns from_cache=True"""
        # First call
        response1 = requests.get(
            f"{BASE_URL}/api/v1/weather/now",
            params={"lat": TEST_LAT, "lng": TEST_LNG}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Second call should hit cache
        response2 = requests.get(
            f"{BASE_URL}/api/v1/weather/now",
            params={"lat": TEST_LAT, "lng": TEST_LNG}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Second call must be from cache
        assert data2.get("from_cache") == True, f"Expected from_cache=True, got {data2.get('from_cache')}"
        
        # Same data (within small tolerance for timestamps)
        assert data1["temperature_c"] == data2["temperature_c"], "Temperature should match from cache"
        
        print(f"✓ Cache hit verified: from_cache={data2['from_cache']}")

    def test_weather_now_invalid_params_lat_out_of_range(self):
        """Test that invalid lat param returns error"""
        response = requests.get(
            f"{BASE_URL}/api/v1/weather/now",
            params={"lat": 999, "lng": TEST_LNG}
        )
        
        # Should return 422 Unprocessable Entity for validation error
        assert response.status_code == 422, f"Expected 422 for invalid lat, got {response.status_code}"
        print(f"✓ Invalid lat correctly rejected with 422")

    def test_weather_now_missing_params(self):
        """Test that missing params returns error"""
        response = requests.get(f"{BASE_URL}/api/v1/weather/now")
        
        assert response.status_code == 422, f"Expected 422 for missing params, got {response.status_code}"
        print(f"✓ Missing params correctly rejected with 422")


class TestWeatherForecastEndpoint:
    """Tests for GET /api/v1/weather/forecast"""

    def test_forecast_returns_multiple_entries(self):
        """Test that /api/v1/weather/forecast returns forecast with multiple entries"""
        response = requests.get(
            f"{BASE_URL}/api/v1/weather/forecast",
            params={"lat": TEST_LAT, "lng": TEST_LNG}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Required fields
        assert "forecasts" in data, "Missing forecasts array"
        assert "forecast_count" in data, "Missing forecast_count"
        assert "from_cache" in data, "Missing from_cache"
        
        # Should have multiple forecast entries (5 days × 8 entries/day = 40 entries)
        forecast_count = data["forecast_count"]
        assert forecast_count >= 8, f"Expected at least 8 forecast entries, got {forecast_count}"
        
        # Validate first forecast entry
        if data["forecasts"]:
            first = data["forecasts"][0]
            assert "temperature_c" in first, "Missing temperature_c in forecast entry"
            assert "wind_speed_kmh" in first, "Missing wind_speed_kmh in forecast entry"
            assert "dt_txt" in first, "Missing dt_txt in forecast entry"
        
        print(f"✓ Forecast returned {forecast_count} entries")


class TestWeatherInfluenceEndpoint:
    """Tests for GET /api/v1/weather/influence"""

    def test_influence_returns_multipliers(self):
        """Test that /api/v1/weather/influence returns influence_multipliers"""
        response = requests.get(
            f"{BASE_URL}/api/v1/weather/influence",
            params={"lat": TEST_LAT, "lng": TEST_LNG}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Required fields
        assert "influence_multipliers" in data, "Missing influence_multipliers"
        assert "weather" in data, "Missing weather summary"
        assert "from_cache" in data, "Missing from_cache"
        
        multipliers = data["influence_multipliers"]
        
        # Check all 5 multiplier categories
        required_categories = ["repos", "alimentation", "corridors", "rut", "habitats"]
        for cat in required_categories:
            assert cat in multipliers, f"Missing multiplier for {cat}"
            # Multipliers should be between 0.7 and 1.3
            assert 0.7 <= multipliers[cat] <= 1.3, f"Multiplier {cat} out of range: {multipliers[cat]}"
        
        print(f"✓ Influence multipliers: repos={multipliers['repos']}, alimentation={multipliers['alimentation']}, corridors={multipliers['corridors']}, rut={multipliers['rut']}, habitats={multipliers['habitats']}")


class TestWeatherCacheStats:
    """Tests for GET /api/v1/weather/cache-stats"""

    def test_cache_stats_returns_ttl_1800(self):
        """Test that /api/v1/weather/cache-stats returns TTL=1800 seconds (30 min)"""
        response = requests.get(f"{BASE_URL}/api/v1/weather/cache-stats")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Required fields
        assert "cache_ttl_seconds" in data, "Missing cache_ttl_seconds"
        assert "cache_ttl_minutes" in data, "Missing cache_ttl_minutes"
        assert "weather_cache_entries" in data, "Missing weather_cache_entries"
        
        # TTL must be 1800 seconds (30 minutes)
        assert data["cache_ttl_seconds"] == 1800, f"Expected TTL=1800, got {data['cache_ttl_seconds']}"
        assert data["cache_ttl_minutes"] == 30, f"Expected TTL=30 min, got {data['cache_ttl_minutes']}"
        
        print(f"✓ Cache stats: TTL={data['cache_ttl_seconds']}s ({data['cache_ttl_minutes']} min), entries={data['weather_cache_entries']}")


class TestOrganicZonesV7Regression:
    """Test that V7 organic-zones engine still works (regression test)"""

    def test_organic_zones_rural_returns_8_plus_zones(self):
        """Test that POST /api/v1/bionic/organic-zones with rural waypoint returns 8+ zones"""
        # Rural bounds (Laurentides forest region - ~5km area)
        center_lat, center_lng = 46.8566, -71.4866
        delta = 0.025  # ~2.5km radius
        
        payload = {
            "bounds": {
                "north": center_lat + delta,
                "south": center_lat - delta,
                "east": center_lng + delta,
                "west": center_lng - delta
            },
            "species": "moose",
            "layers": ["habitats", "repos", "alimentation", "corridors"],
            "max_zones_per_layer": 8,
            "waypoint_center": {
                "lat": center_lat,
                "lng": center_lng
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60  # Zone generation can take time
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Should have features array and stats
        assert "features" in data, "Missing features array"
        assert "stats" in data, "Missing stats"
        
        # Get zone count from stats
        zone_count = data["stats"].get("total_zones", 0)
        
        # V7 engine should be active
        assert data["stats"].get("exclusion_engine") == "v7", f"Expected V7 engine, got {data['stats'].get('exclusion_engine')}"
        
        # V7 engine should generate zones for rural areas (8+ zones expected)
        assert zone_count >= 8, f"Expected at least 8 zones for rural waypoint, got {zone_count}"
        
        print(f"✓ V7 organic-zones working: {zone_count} zones generated, engine={data['stats'].get('exclusion_engine')}")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
