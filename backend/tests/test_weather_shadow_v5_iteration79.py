"""
TEST WEATHER SHADOW — BIONIC V5 ULTIME 300%
============================================

Weather Shadow Integration Tests — Open-Meteo (Free API, no key required)
Tests: status, fetch, analyze (cache), cache list, invalid species, non-regression

Territories:
  - Laurentides: {north:46.95, south:46.85, east:-74.00, west:-74.15}
  - Charlevoix: {north:47.60, south:47.50, east:-70.50, west:-70.65}

Resolution: 30
Cache TTL: 6 hours

Author: Testing Agent T1
Iteration: 79
"""

import pytest
import requests
import time
import os

# API Base URL from environment
BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test data
LAURENTIDES_BOUNDS = {"north": 46.95, "south": 46.85, "east": -74.00, "west": -74.15}
CHARLEVOIX_BOUNDS = {"north": 47.60, "south": 47.50, "east": -70.50, "west": -70.65}
RESOLUTION = 30
TIMEOUT = 30


class TestWeatherShadowStatus:
    """Weather Shadow status endpoint tests"""

    def test_status_endpoint_200(self):
        """GET /api/v1/bionic/weather-shadow/status returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/weather-shadow/status", timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ Status endpoint returns 200")

    def test_status_active(self):
        """Status is active"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/weather-shadow/status", timeout=TIMEOUT)
        data = response.json()
        assert data.get("status") == "active", f"Expected status=active, got {data.get('status')}"
        print(f"✓ Status = active")

    def test_status_api_key_not_required(self):
        """API key is not required (Open-Meteo is free)"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/weather-shadow/status", timeout=TIMEOUT)
        data = response.json()
        assert data.get("api_key_required") is False, f"Expected api_key_required=false, got {data.get('api_key_required')}"
        print(f"✓ api_key_required = false")

    def test_status_provider_open_meteo(self):
        """Provider is Open-Meteo"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/weather-shadow/status", timeout=TIMEOUT)
        data = response.json()
        provider = data.get("provider", "")
        assert "Open-Meteo" in provider, f"Expected provider to contain 'Open-Meteo', got {provider}"
        print(f"✓ Provider = {provider}")

    def test_status_outputs_weather_fields(self):
        """Status lists expected outputs"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/weather-shadow/status", timeout=TIMEOUT)
        data = response.json()
        outputs = data.get("outputs", [])
        expected = ["temperature", "wind_speed", "humidity", "precipitation", "cloud_cover", "surface_pressure"]
        for exp in expected:
            assert exp in outputs, f"Expected '{exp}' in outputs, got {outputs}"
        print(f"✓ Outputs include all weather fields: {outputs}")


class TestWeatherShadowFetch:
    """Weather Shadow fetch endpoint tests — Laurentides"""

    def test_fetch_laurentides_200(self):
        """POST /api/v1/bionic/weather-shadow/fetch Laurentides returns 200"""
        payload = {"bounds": LAURENTIDES_BOUNDS, "species": "moose", "resolution": RESOLUTION}
        response = requests.post(f"{BASE_URL}/api/v1/bionic/weather-shadow/fetch", json=payload, timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Fetch Laurentides returns 200")

    def test_fetch_returns_real_stats(self):
        """Fetch returns real weather stats (temperature, wind, humidity, precipitation, cloud, pressure)"""
        payload = {"bounds": LAURENTIDES_BOUNDS, "species": "moose", "resolution": RESOLUTION}
        response = requests.post(f"{BASE_URL}/api/v1/bionic/weather-shadow/fetch", json=payload, timeout=TIMEOUT)
        data = response.json()
        stats = data.get("stats", {})

        # Verify all weather fields are present
        required_keys = ["temperature", "humidity", "wind_speed_kmh", "precipitation_mm", "cloud_cover_pct", "surface_pressure_hpa"]
        for key in required_keys:
            assert key in stats, f"Missing stats key: {key}"
            assert isinstance(stats[key], dict), f"Expected {key} to be dict, got {type(stats[key])}"

        # Validate temperature range (sanity check: -60 to +60 Celsius is reasonable)
        temp_mean = stats["temperature"]["mean"]
        assert -60 <= temp_mean <= 60, f"Temperature mean {temp_mean} out of reasonable range"
        
        print(f"✓ Fetch returns real stats: temp={temp_mean}°C, humidity={stats['humidity']['mean']}%, wind={stats['wind_speed_kmh']['mean']}km/h")

    def test_fetch_returns_source_id(self):
        """Fetch returns correct source_id"""
        payload = {"bounds": LAURENTIDES_BOUNDS, "species": "moose", "resolution": RESOLUTION}
        response = requests.post(f"{BASE_URL}/api/v1/bionic/weather-shadow/fetch", json=payload, timeout=TIMEOUT)
        data = response.json()
        assert data.get("source_id") == "WEATHER_MOOSE", f"Expected source_id=WEATHER_MOOSE, got {data.get('source_id')}"
        print(f"✓ source_id = WEATHER_MOOSE")

    def test_fetch_returns_validation(self):
        """Fetch returns validation with data_real=true"""
        payload = {"bounds": LAURENTIDES_BOUNDS, "species": "moose", "resolution": RESOLUTION}
        response = requests.post(f"{BASE_URL}/api/v1/bionic/weather-shadow/fetch", json=payload, timeout=TIMEOUT)
        data = response.json()
        validation = data.get("validation", {})
        assert validation.get("data_real") is True, f"Expected data_real=true, got {validation}"
        assert validation.get("source") == "Open-Meteo", f"Expected source=Open-Meteo, got {validation.get('source')}"
        print(f"✓ Validation: data_real=true, source=Open-Meteo")


class TestWeatherShadowAnalyze:
    """Weather Shadow analyze endpoint tests — Cache behavior"""

    def test_analyze_laurentides_first_call(self):
        """POST /api/v1/bionic/weather-shadow/analyze Laurentides moose — 1st call cache_status=stored or hit"""
        payload = {"bounds": LAURENTIDES_BOUNDS, "species": "moose", "resolution": RESOLUTION}
        response = requests.post(f"{BASE_URL}/api/v1/bionic/weather-shadow/analyze", json=payload, timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        cache_status = data.get("cache_status")
        assert cache_status in ["stored", "hit"], f"Expected cache_status in [stored, hit], got {cache_status}"
        print(f"✓ Analyze Laurentides moose: cache_status={cache_status}")
        return data

    def test_analyze_laurentides_cache_hit_fast(self):
        """POST /api/v1/bionic/weather-shadow/analyze — 2nd call = cache hit, time < 50ms"""
        payload = {"bounds": LAURENTIDES_BOUNDS, "species": "moose", "resolution": RESOLUTION}
        
        # First call to ensure cache is populated
        requests.post(f"{BASE_URL}/api/v1/bionic/weather-shadow/analyze", json=payload, timeout=TIMEOUT)
        
        # Second call should be cache hit
        start = time.time()
        response = requests.post(f"{BASE_URL}/api/v1/bionic/weather-shadow/analyze", json=payload, timeout=TIMEOUT)
        elapsed_network = (time.time() - start) * 1000
        
        assert response.status_code == 200
        data = response.json()
        
        cache_status = data.get("cache_status")
        computation_time = data.get("computation_time_ms", 9999)
        
        assert cache_status == "hit", f"Expected cache_status=hit on 2nd call, got {cache_status}"
        assert computation_time < 50, f"Expected cache hit time < 50ms, got {computation_time}ms"
        
        print(f"✓ Cache hit: computation_time={computation_time}ms (network RTT: {elapsed_network:.1f}ms)")

    def test_analyze_charlevoix_different_data(self):
        """POST /api/v1/bionic/weather-shadow/analyze Charlevoix bear — different data from Laurentides"""
        payload_laurentides = {"bounds": LAURENTIDES_BOUNDS, "species": "moose", "resolution": RESOLUTION}
        payload_charlevoix = {"bounds": CHARLEVOIX_BOUNDS, "species": "bear", "resolution": RESOLUTION}
        
        resp_l = requests.post(f"{BASE_URL}/api/v1/bionic/weather-shadow/analyze", json=payload_laurentides, timeout=TIMEOUT)
        resp_c = requests.post(f"{BASE_URL}/api/v1/bionic/weather-shadow/analyze", json=payload_charlevoix, timeout=TIMEOUT)
        
        assert resp_l.status_code == 200 and resp_c.status_code == 200
        
        data_l = resp_l.json()
        data_c = resp_c.json()
        
        # Bounds should be different
        bounds_l = data_l.get("bounds", {})
        bounds_c = data_c.get("bounds", {})
        assert bounds_l != bounds_c, "Bounds should be different"
        
        # Species should be different
        assert data_l.get("species") == "moose"
        assert data_c.get("species") == "bear"
        
        print(f"✓ Charlevoix bear has different data from Laurentides moose")
        print(f"  Laurentides: bounds.north={bounds_l.get('north')}")
        print(f"  Charlevoix: bounds.north={bounds_c.get('north')}")


class TestWeatherShadowCache:
    """Weather Shadow cache list endpoint tests"""

    def test_cache_endpoint_200(self):
        """GET /api/v1/bionic/weather-shadow/cache returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/weather-shadow/cache", timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ Cache endpoint returns 200")

    def test_cache_has_entries(self):
        """Cache has at least 2 active entries"""
        # First ensure cache is populated with 2 territories
        payload_l = {"bounds": LAURENTIDES_BOUNDS, "species": "moose", "resolution": RESOLUTION}
        payload_c = {"bounds": CHARLEVOIX_BOUNDS, "species": "bear", "resolution": RESOLUTION}
        requests.post(f"{BASE_URL}/api/v1/bionic/weather-shadow/analyze", json=payload_l, timeout=TIMEOUT)
        requests.post(f"{BASE_URL}/api/v1/bionic/weather-shadow/analyze", json=payload_c, timeout=TIMEOUT)
        
        # Now check cache
        response = requests.get(f"{BASE_URL}/api/v1/bionic/weather-shadow/cache", timeout=TIMEOUT)
        data = response.json()
        
        active = data.get("active", 0)
        total = data.get("total_entries", 0)
        entries = data.get("entries", [])
        
        assert total >= 2, f"Expected at least 2 cache entries, got {total}"
        assert active >= 2, f"Expected at least 2 active entries, got {active}"
        
        # Count active entries
        active_count = sum(1 for e in entries if e.get("status") == "active")
        assert active_count >= 2, f"Expected at least 2 active entries, got {active_count}"
        
        print(f"✓ Cache has {total} entries, {active} active")
        for entry in entries[:3]:  # Show first 3
            print(f"  - {entry.get('cache_key', 'N/A')[:12]}... species={entry.get('species')} status={entry.get('status')}")


class TestWeatherShadowValidation:
    """Weather Shadow validation tests — invalid inputs"""

    def test_invalid_species_400(self):
        """Invalid species returns 400"""
        payload = {"bounds": LAURENTIDES_BOUNDS, "species": "invalid_species_xyz", "resolution": RESOLUTION}
        response = requests.post(f"{BASE_URL}/api/v1/bionic/weather-shadow/analyze", json=payload, timeout=TIMEOUT)
        assert response.status_code == 400, f"Expected 400 for invalid species, got {response.status_code}"
        print(f"✓ Invalid species returns 400")


class TestNonRegression:
    """Non-regression tests — ensure existing endpoints still work"""

    def test_api_keys_status_weather_configured(self):
        """GET /api/v1/system/api-keys/status — weather_realtime=configured"""
        response = requests.get(f"{BASE_URL}/api/v1/system/api-keys/status", timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Find weather_realtime in key_statuses
        key_statuses = data.get("key_statuses", {})
        weather_key = key_statuses.get("weather_realtime")
        
        assert weather_key is not None, "weather_realtime key not found in key_statuses"
        assert weather_key.get("status") == "configured", f"Expected weather_realtime status=configured, got {weather_key.get('status')}"
        print(f"✓ Non-regression: weather_realtime = configured")

    def test_pipeline_full_analysis_works(self):
        """POST /api/v1/bionic/pipeline/full-analysis — still works (synthetic inchangé)"""
        payload = {
            "bounds": LAURENTIDES_BOUNDS,
            "species": "moose",
            "resolution": RESOLUTION
        }
        response = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/full-analysis", json=payload, timeout=60)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Check pipeline executed with multiple modules
        source_ids = data.get("pipeline_source_ids", [])
        assert len(source_ids) >= 5, f"Expected at least 5 modules, got {len(source_ids)}"
        
        print(f"✓ Non-regression: pipeline/full-analysis works ({len(source_ids)} modules)")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
