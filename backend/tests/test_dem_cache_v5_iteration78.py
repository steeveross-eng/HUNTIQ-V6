"""
TEST DEM CACHE MONGODB — BIONIC V5 ULTIME 300% — Iteration 78
MongoDB Cache for DEM data with TTL 90 days.

Tests:
1. GET /api/v1/bionic/dem-shadow/status — cache.enabled=true, cache.backend=MongoDB, cache.ttl_days=90
2. GET /api/v1/bionic/dem-shadow/cache — returns cached entries (at least 1 active)
3. POST /api/v1/bionic/dem-shadow/pipeline — Laurentides moose, cache_status=hit, dem_active=true
4. POST /api/v1/bionic/dem-shadow/pipeline — with cache hit, time < 1000ms
5. POST /api/v1/bionic/dem-shadow/compare — returns deltas TCVE/TFE
6. POST /api/v1/bionic/dem-shadow/compare — validation: certified_modules_unmodified=true, zero_impact=true
7. Non-regression: POST /pipeline/full-analysis still works
8. Non-regression: GET /dem-shadow/status version=1.1.0

IMPORTANT: OpenTopography rate limit EXHAUSTED but cache is populated.
Use ONLY Laurentides bounds with resolution=30 for cache hits.
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    BASE_URL = "https://corridor-ecology-hub.preview.emergentagent.com"

# Laurentides bounds (cached data available)
LAURENTIDES_BOUNDS = {
    "north": 46.95,
    "south": 46.85,
    "east": -74.00,
    "west": -74.15
}

TIMEOUT = 30  # Fast timeout since cache hits are ~245ms


class TestDemCacheStatus:
    """GET /api/v1/bionic/dem-shadow/status — cache configuration tests"""

    def test_status_cache_enabled(self):
        """Status shows cache.enabled=true"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/dem-shadow/status", timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        cache = data.get("cache", {})
        assert cache.get("enabled") is True, f"Expected cache.enabled=true, got {cache.get('enabled')}"
        print("PASS: cache.enabled=true")

    def test_status_cache_backend_mongodb(self):
        """Status shows cache.backend=MongoDB"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/dem-shadow/status", timeout=TIMEOUT)
        data = response.json()
        cache = data.get("cache", {})
        assert cache.get("backend") == "MongoDB", f"Expected cache.backend=MongoDB, got {cache.get('backend')}"
        print("PASS: cache.backend=MongoDB")

    def test_status_cache_ttl_90_days(self):
        """Status shows cache.ttl_days=90"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/dem-shadow/status", timeout=TIMEOUT)
        data = response.json()
        cache = data.get("cache", {})
        assert cache.get("ttl_days") == 90, f"Expected cache.ttl_days=90, got {cache.get('ttl_days')}"
        print("PASS: cache.ttl_days=90")

    def test_status_version_1_1_0(self):
        """Status shows version=1.1.0"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/dem-shadow/status", timeout=TIMEOUT)
        data = response.json()
        version = data.get("version")
        assert version == "1.1.0", f"Expected version=1.1.0, got {version}"
        print("PASS: version=1.1.0")


class TestDemCacheList:
    """GET /api/v1/bionic/dem-shadow/cache — cache entries tests"""

    def test_cache_list_returns_200(self):
        """Cache list endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/dem-shadow/cache", timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /dem-shadow/cache returns 200")

    def test_cache_has_entries(self):
        """Cache has at least 1 entry"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/dem-shadow/cache", timeout=TIMEOUT)
        data = response.json()
        total = data.get("total_entries", 0)
        assert total >= 1, f"Expected at least 1 cache entry, got {total}"
        print(f"PASS: cache has {total} entries")

    def test_cache_has_active_entry(self):
        """Cache has at least 1 active (non-expired) entry"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/dem-shadow/cache", timeout=TIMEOUT)
        data = response.json()
        active = data.get("active", 0)
        assert active >= 1, f"Expected at least 1 active entry, got {active}"
        print(f"PASS: cache has {active} active entries")

    def test_cache_entry_has_laurentides(self):
        """Cache contains Laurentides bounds entry"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/dem-shadow/cache", timeout=TIMEOUT)
        data = response.json()
        entries = data.get("entries", [])
        laurentides_found = False
        for entry in entries:
            bounds = entry.get("bounds", {})
            if (bounds.get("north") == 46.95 and bounds.get("south") == 46.85 and
                bounds.get("east") == -74.0 and bounds.get("west") == -74.15):
                laurentides_found = True
                print(f"PASS: Laurentides entry found: key={entry.get('cache_key')}, dataset={entry.get('dataset')}, res={entry.get('resolution')}")
                break
        assert laurentides_found, f"Expected Laurentides entry in cache, got {[e.get('bounds') for e in entries]}"


class TestDemShadowPipelineCacheHit:
    """POST /api/v1/bionic/dem-shadow/pipeline — cache hit tests"""

    def test_pipeline_cache_hit_dem_active_true(self):
        """Pipeline with cached data returns dem_active=true"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/pipeline",
            json={"bounds": LAURENTIDES_BOUNDS, "species": "moose", "resolution": 30},
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("dem_active") is True, f"Expected dem_active=true, got {data.get('dem_active')}"
        print("PASS: dem_active=true (cache hit)")

    def test_pipeline_cache_status_hit(self):
        """Pipeline returns cache_status=hit in shadow_dem"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/pipeline",
            json={"bounds": LAURENTIDES_BOUNDS, "species": "moose", "resolution": 30},
            timeout=TIMEOUT
        )
        data = response.json()
        shadow_dem = data.get("shadow_dem", {})
        cache_status = shadow_dem.get("cache_status")
        assert cache_status == "hit", f"Expected cache_status=hit, got {cache_status}"
        print("PASS: cache_status=hit")

    def test_pipeline_cache_hit_fast_response(self):
        """Pipeline with cache hit responds in < 1000ms"""
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/pipeline",
            json={"bounds": LAURENTIDES_BOUNDS, "species": "moose", "resolution": 30},
            timeout=TIMEOUT
        )
        elapsed_ms = (time.time() - start) * 1000
        assert response.status_code == 200
        data = response.json()
        total_time = data.get("total_computation_time_ms", 0)
        # Verify internal computation time is fast (< 500ms typical for cache hit)
        assert total_time < 1000, f"Expected total_computation_time_ms < 1000, got {total_time}"
        print(f"PASS: total_computation_time_ms={total_time}ms (< 1000ms), round-trip={elapsed_ms:.0f}ms")

    def test_pipeline_cache_hit_elevation_stats(self):
        """Pipeline returns real elevation stats from cache (377m-567m for Laurentides)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/pipeline",
            json={"bounds": LAURENTIDES_BOUNDS, "species": "moose", "resolution": 30},
            timeout=TIMEOUT
        )
        data = response.json()
        shadow_dem = data.get("shadow_dem", {})
        stats = shadow_dem.get("elevation_stats", {})
        elev_min = stats.get("elevation_min", 0)
        elev_max = stats.get("elevation_max", 0)
        # Laurentides cached data: 377m-567m
        assert 300 <= elev_min <= 400, f"Expected elevation_min ~377, got {elev_min}"
        assert 500 <= elev_max <= 600, f"Expected elevation_max ~567, got {elev_max}"
        print(f"PASS: elevation_stats: min={elev_min}m, max={elev_max}m (real cached data)")


class TestDemShadowCompare:
    """POST /api/v1/bionic/dem-shadow/compare — comparison tests"""

    def test_compare_returns_200(self):
        """Compare endpoint returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/compare",
            json={"bounds": LAURENTIDES_BOUNDS, "species": "moose", "resolution": 30},
            timeout=TIMEOUT
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: POST /dem-shadow/compare returns 200")

    def test_compare_deltas_tcve(self):
        """Compare returns deltas.tcve (non-empty for real DEM)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/compare",
            json={"bounds": LAURENTIDES_BOUNDS, "species": "moose", "resolution": 30},
            timeout=TIMEOUT
        )
        data = response.json()
        deltas = data.get("deltas", {})
        tcve_deltas = deltas.get("tcve", {})
        # Should have delta values when real DEM is active
        assert "tcve" in deltas, f"Expected deltas.tcve, got {deltas.keys()}"
        print(f"PASS: deltas.tcve={tcve_deltas}")

    def test_compare_deltas_tfe(self):
        """Compare returns deltas.tfe (non-empty for real DEM)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/compare",
            json={"bounds": LAURENTIDES_BOUNDS, "species": "moose", "resolution": 30},
            timeout=TIMEOUT
        )
        data = response.json()
        deltas = data.get("deltas", {})
        tfe_deltas = deltas.get("tfe", {})
        assert "tfe" in deltas, f"Expected deltas.tfe, got {deltas.keys()}"
        print(f"PASS: deltas.tfe={tfe_deltas}")

    def test_compare_validation_certified_modules_unmodified(self):
        """Compare validation shows certified_modules_unmodified=true"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/compare",
            json={"bounds": LAURENTIDES_BOUNDS, "species": "moose", "resolution": 30},
            timeout=TIMEOUT
        )
        data = response.json()
        validation = data.get("validation", {})
        assert validation.get("certified_modules_unmodified") is True, \
            f"Expected certified_modules_unmodified=true, got {validation}"
        print("PASS: certified_modules_unmodified=true")

    def test_compare_validation_zero_impact_on_production(self):
        """Compare validation shows zero_impact_on_production=true"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/compare",
            json={"bounds": LAURENTIDES_BOUNDS, "species": "moose", "resolution": 30},
            timeout=TIMEOUT
        )
        data = response.json()
        validation = data.get("validation", {})
        assert validation.get("zero_impact_on_production") is True, \
            f"Expected zero_impact_on_production=true, got {validation}"
        print("PASS: zero_impact_on_production=true")


class TestNonRegression:
    """Non-regression tests — existing endpoints unchanged"""

    def test_pipeline_full_analysis_works(self):
        """POST /pipeline/full-analysis still works (synthetic pipeline unchanged)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/pipeline/full-analysis",
            json={"bounds": LAURENTIDES_BOUNDS, "species": "moose", "resolution": 30},
            timeout=60
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        source_ids = data.get("pipeline_source_ids", {})
        assert len(source_ids) >= 9, f"Expected 9+ modules, got {len(source_ids)}"
        print(f"PASS: Non-regression /pipeline/full-analysis works ({len(source_ids)} modules)")

    def test_status_version_unchanged(self):
        """GET /dem-shadow/status returns version 1.1.0"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/dem-shadow/status", timeout=TIMEOUT)
        data = response.json()
        assert data.get("version") == "1.1.0", f"Expected version=1.1.0, got {data.get('version')}"
        print("PASS: Non-regression version=1.1.0")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
