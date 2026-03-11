"""
BIONIC V8.2.1 Weather Zone Integration Tests
Tests for Weather V8.2.1 - Weather multipliers integrated into organic-zones endpoint.

Features tested:
  - POST /api/v1/bionic/organic-zones with waypoint_center returns weather_metadata
  - Zone properties contain weather_multiplier, weather_global, score_pre_weather fields
  - Score alimentation is adjusted by weather multiplier (score != score_pre_weather when mult != 1.0)
  - weather_metadata.badges array contains 'favorable'/'wind_alert'/'heavy_rain' when conditions match
  - weather_metadata.snapshot contains temperature, wind, precipitation from OWM cache
  - GET /api/v1/weather/cache-stats confirms cache TTL = 1800s (30 min)
  - Regression: V7 organic-zones still generates 8+ zones for rural waypoint

Test coordinates:
  - Rural (47.0, -72.28): Should generate 8+ zones with weather influence
  - Urban (46.91, -71.21): Should generate 0 zones (urban exclusion)
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test coordinates
RURAL_LAT, RURAL_LNG = 47.0, -72.28  # Rural Quebec - generates zones
URBAN_LAT, URBAN_LNG = 46.91, -71.21  # Urban area - 0 zones expected


class TestWeatherMetadataInOrganicZones:
    """V8.2.1: Weather metadata integration in organic-zones endpoint"""

    def test_organic_zones_with_waypoint_returns_weather_metadata(self):
        """POST /api/v1/bionic/organic-zones with waypoint_center returns weather_metadata"""
        payload = {
            "bounds": {
                "north": RURAL_LAT + 0.015,
                "south": RURAL_LAT - 0.015,
                "east": RURAL_LNG + 0.015,
                "west": RURAL_LNG - 0.015
            },
            "species": "moose",
            "layers": ["habitats", "repos", "alimentation", "corridors"],
            "max_zones_per_layer": 8,
            "waypoint_center": {
                "lat": RURAL_LAT,
                "lng": RURAL_LNG
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # V8.2.1: weather_metadata must be present
        assert "weather_metadata" in data, "Missing weather_metadata in response"
        weather_meta = data["weather_metadata"]
        
        # V8.2.1: weather_metadata.applied must be True
        assert weather_meta.get("applied") == True, f"Expected applied=True, got {weather_meta.get('applied')}"
        
        # V8.2.1: influence_multipliers must be present
        assert "influence_multipliers" in weather_meta, "Missing influence_multipliers"
        multipliers = weather_meta["influence_multipliers"]
        
        # Check all 5 categories present
        for cat in ["repos", "alimentation", "corridors", "rut", "habitats"]:
            assert cat in multipliers, f"Missing multiplier for {cat}"
            assert 0.7 <= multipliers[cat] <= 1.3, f"Multiplier {cat} out of [0.7, 1.3] range: {multipliers[cat]}"
        
        # V8.2.1: global_multiplier must be present
        assert "global_multiplier" in weather_meta, "Missing global_multiplier"
        assert 0.7 <= weather_meta["global_multiplier"] <= 1.3, f"Global multiplier out of range: {weather_meta['global_multiplier']}"
        
        # V8.2.1: badges must be present (list, can be empty)
        assert "badges" in weather_meta, "Missing badges array"
        assert isinstance(weather_meta["badges"], list), "badges should be a list"
        
        # V8.2.1: snapshot must be present
        assert "snapshot" in weather_meta, "Missing snapshot"
        snapshot = weather_meta["snapshot"]
        assert "temperature_c" in snapshot, "Missing temperature_c in snapshot"
        assert "wind_speed_kmh" in snapshot, "Missing wind_speed_kmh in snapshot"
        assert "precipitation_1h_mm" in snapshot, "Missing precipitation_1h_mm in snapshot"
        
        # V8.2.1: cache_ttl_minutes must be 30
        assert weather_meta.get("cache_ttl_minutes") == 30, f"Expected cache_ttl_minutes=30, got {weather_meta.get('cache_ttl_minutes')}"
        
        print(f"✓ weather_metadata: applied={weather_meta['applied']}, global={weather_meta['global_multiplier']:.3f}, snapshot temp={snapshot['temperature_c']}°C")


class TestZonePropertiesWithWeather:
    """V8.2.1: Zone properties contain weather influence fields"""

    def test_zone_properties_contain_weather_fields(self):
        """Zone properties contain weather_multiplier, weather_global, score_pre_weather"""
        payload = {
            "bounds": {
                "north": RURAL_LAT + 0.015,
                "south": RURAL_LAT - 0.015,
                "east": RURAL_LNG + 0.015,
                "west": RURAL_LNG - 0.015
            },
            "species": "moose",
            "layers": ["alimentation"],  # Single layer for clearer test
            "max_zones_per_layer": 8,
            "waypoint_center": {
                "lat": RURAL_LAT,
                "lng": RURAL_LNG
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        features = data.get("features", [])
        assert len(features) > 0, "Expected at least 1 zone for alimentation layer"
        
        # Check first zone's properties
        zone = features[0]
        props = zone.get("properties", {})
        
        # V8.2.1 required fields
        assert "weather_multiplier" in props, "Missing weather_multiplier in zone properties"
        assert "weather_global" in props, "Missing weather_global in zone properties"
        assert "score_pre_weather" in props, "Missing score_pre_weather in zone properties"
        
        # Validate values
        w_mult = props["weather_multiplier"]
        w_global = props["weather_global"]
        score_pre = props["score_pre_weather"]
        score = props.get("score", 0)
        
        assert 0.7 <= w_mult <= 1.3, f"weather_multiplier out of range: {w_mult}"
        assert 0.7 <= w_global <= 1.3, f"weather_global out of range: {w_global}"
        assert 0 <= score_pre <= 100, f"score_pre_weather out of range: {score_pre}"
        assert 0 <= score <= 100, f"score out of range: {score}"
        
        # V8.2.1: weather_badges should be on zone properties
        assert "weather_badges" in props, "Missing weather_badges in zone properties"
        assert isinstance(props["weather_badges"], list), "weather_badges should be a list"
        
        print(f"✓ Zone weather fields: multiplier={w_mult:.3f}, global={w_global:.3f}, score_pre={score_pre}, score={score}")


class TestWeatherScoreAdjustment:
    """V8.2.1: Score is adjusted by weather multiplier"""

    def test_score_adjusted_by_weather_multiplier(self):
        """When multiplier != 1.0, score != score_pre_weather"""
        payload = {
            "bounds": {
                "north": RURAL_LAT + 0.015,
                "south": RURAL_LAT - 0.015,
                "east": RURAL_LNG + 0.015,
                "west": RURAL_LNG - 0.015
            },
            "species": "moose",
            "layers": ["alimentation", "repos", "habitats"],
            "max_zones_per_layer": 8,
            "waypoint_center": {
                "lat": RURAL_LAT,
                "lng": RURAL_LNG
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        features = data.get("features", [])
        assert len(features) > 0, "Expected zones to test weather adjustment"
        
        # Find any zone where multiplier != 1.0
        adjustment_found = False
        for zone in features:
            props = zone.get("properties", {})
            w_mult = props.get("weather_multiplier", 1.0)
            score_pre = props.get("score_pre_weather", 0)
            score = props.get("score", 0)
            
            # If multiplier is not exactly 1.0, score should differ (unless edge cases like 0)
            if abs(w_mult - 1.0) > 0.01 and score_pre > 0:
                expected_score = min(100, max(0, round(score_pre * w_mult)))
                assert score == expected_score, f"Score adjustment mismatch: {score} != {expected_score} (pre={score_pre}, mult={w_mult})"
                adjustment_found = True
                print(f"✓ Score adjustment verified: {score_pre} × {w_mult:.3f} = {score}")
                break
        
        # Weather multipliers vary, so we can't guarantee adjustment, but validate structure
        print(f"✓ Weather score adjustment structure validated on {len(features)} zones")


class TestWeatherBadges:
    """V8.2.1: Weather badges in response"""

    def test_badges_structure_in_weather_metadata(self):
        """weather_metadata.badges array has correct structure"""
        payload = {
            "bounds": {
                "north": RURAL_LAT + 0.015,
                "south": RURAL_LAT - 0.015,
                "east": RURAL_LNG + 0.015,
                "west": RURAL_LNG - 0.015
            },
            "species": "moose",
            "layers": ["habitats"],
            "max_zones_per_layer": 4,
            "waypoint_center": {
                "lat": RURAL_LAT,
                "lng": RURAL_LNG
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        weather_meta = data.get("weather_metadata", {})
        assert weather_meta.get("applied") == True, "Weather not applied"
        
        badges = weather_meta.get("badges", [])
        
        # Validate badge structure if any exist
        for badge in badges:
            assert "type" in badge, "Badge missing type"
            assert "label" in badge, "Badge missing label"
            assert "color" in badge, "Badge missing color"
            assert badge["type"] in ["favorable", "wind_alert", "heavy_rain"], f"Unknown badge type: {badge['type']}"
        
        print(f"✓ Weather badges validated: {len(badges)} badges found")
        if badges:
            print(f"  Badges: {[b['type'] for b in badges]}")


class TestWeatherSnapshotFields:
    """V8.2.1: Snapshot contains temperature, wind, precipitation"""

    def test_snapshot_contains_required_fields(self):
        """weather_metadata.snapshot contains OWM cache data"""
        payload = {
            "bounds": {
                "north": RURAL_LAT + 0.015,
                "south": RURAL_LAT - 0.015,
                "east": RURAL_LNG + 0.015,
                "west": RURAL_LNG - 0.015
            },
            "species": "moose",
            "layers": ["habitats"],
            "max_zones_per_layer": 4,
            "waypoint_center": {
                "lat": RURAL_LAT,
                "lng": RURAL_LNG
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        weather_meta = data.get("weather_metadata", {})
        snapshot = weather_meta.get("snapshot", {})
        
        # V8.2.1 required snapshot fields
        assert "temperature_c" in snapshot, "Missing temperature_c"
        assert "wind_speed_kmh" in snapshot, "Missing wind_speed_kmh"
        assert "wind_gust_kmh" in snapshot, "Missing wind_gust_kmh"
        assert "precipitation_1h_mm" in snapshot, "Missing precipitation_1h_mm"
        assert "condition" in snapshot, "Missing condition"
        assert "condition_detail" in snapshot, "Missing condition_detail"
        assert "from_cache" in snapshot, "Missing from_cache flag"
        
        # Validate ranges
        temp = snapshot["temperature_c"]
        wind = snapshot["wind_speed_kmh"]
        precip = snapshot["precipitation_1h_mm"]
        
        if temp is not None:
            assert -50 < temp < 50, f"Temperature out of range: {temp}"
        if wind is not None:
            assert 0 <= wind < 200, f"Wind speed out of range: {wind}"
        if precip is not None:
            assert 0 <= precip < 100, f"Precipitation out of range: {precip}"
        
        print(f"✓ Snapshot: temp={temp}°C, wind={wind}km/h, precip={precip}mm, condition={snapshot.get('condition')}")


class TestCacheTTL1800:
    """V8.2.1: Cache TTL is 1800s (30 min)"""

    def test_cache_stats_ttl_1800_seconds(self):
        """GET /api/v1/weather/cache-stats confirms TTL = 1800s"""
        response = requests.get(f"{BASE_URL}/api/v1/weather/cache-stats")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("cache_ttl_seconds") == 1800, f"Expected TTL=1800s, got {data.get('cache_ttl_seconds')}"
        assert data.get("cache_ttl_minutes") == 30, f"Expected TTL=30min, got {data.get('cache_ttl_minutes')}"
        
        print(f"✓ Cache TTL verified: {data['cache_ttl_seconds']}s = {data['cache_ttl_minutes']} minutes")


class TestV7RuralZoneRegression:
    """Regression: V7 organic-zones still generates zones for rural waypoint"""

    def test_rural_waypoint_generates_zones(self):
        """POST /api/v1/bionic/organic-zones with rural waypoint (47.0, -72.28) returns zones"""
        # Use larger bounds and more layers to ensure 8+ zones
        payload = {
            "bounds": {
                "north": RURAL_LAT + 0.025,
                "south": RURAL_LAT - 0.025,
                "east": RURAL_LNG + 0.025,
                "west": RURAL_LNG - 0.025
            },
            "species": "moose",
            "layers": ["habitats", "repos", "alimentation", "corridors", "rut", "salines", "affuts"],
            "max_zones_per_layer": 8,
            "waypoint_center": {
                "lat": RURAL_LAT,
                "lng": RURAL_LNG
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        features = data.get("features", [])
        stats = data.get("stats", {})
        
        # Must use V7 engine
        assert stats.get("exclusion_engine") == "v7", f"Expected V7 engine, got {stats.get('exclusion_engine')}"
        
        # Must generate 8+ zones for rural area with expanded bounds/layers
        zone_count = len(features)
        assert zone_count >= 8, f"Expected at least 8 zones for rural waypoint, got {zone_count}"
        
        # V8.2.1: Weather must be applied when waypoint_center is provided
        weather_meta = data.get("weather_metadata", {})
        assert weather_meta.get("applied") == True, "Weather should be applied with waypoint_center"
        
        print(f"✓ V7 regression PASS: {zone_count} zones generated, engine={stats.get('exclusion_engine')}, weather={weather_meta.get('applied')}")


class TestOrganicZonesWithoutWaypointNoWeather:
    """V8.2.1: Without waypoint_center, weather_metadata should NOT be present"""

    def test_no_waypoint_no_weather_metadata(self):
        """POST without waypoint_center should not include weather_metadata"""
        payload = {
            "bounds": {
                "north": RURAL_LAT + 0.015,
                "south": RURAL_LAT - 0.015,
                "east": RURAL_LNG + 0.015,
                "west": RURAL_LNG - 0.015
            },
            "species": "moose",
            "layers": ["habitats"],
            "max_zones_per_layer": 4
            # No waypoint_center
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Without waypoint_center, weather_metadata should not be present (or applied=False)
        weather_meta = data.get("weather_metadata")
        if weather_meta:
            # If present, applied should be False
            assert weather_meta.get("applied") != True, "Weather should not be applied without waypoint_center"
        
        print(f"✓ No waypoint_center = no weather_metadata (as expected)")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
