"""
TEST DEM SHADOW API — BIONIC V5 ULTIME 300%
Shadow Pipeline with Real DEM Injection

Tests:
1. GET /api/v1/bionic/dem-shadow/status — Shadow integration status
2. POST /api/v1/bionic/dem-shadow/pipeline — Full pipeline with real DEM
3. POST /api/v1/bionic/dem-shadow/compare — Synthetic vs Real DEM comparison
4. Non-regression: pipeline/full-analysis, dem/analyze still work

IMPORTANT: Use timeout=180s for all dem-shadow endpoints (OpenTopography ~10s latency)
Territory: ONLY Laurentides to conserve rate limits (200 calls/24h)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    BASE_URL = "https://bionic-toolbar-slim.preview.emergentagent.com"

# Laurentides territory (ONLY use this to conserve rate limits)
LAURENTIDES_BOUNDS = {
    "north": 46.95,
    "south": 46.85,
    "east": -74.00,
    "west": -74.15
}

# Long timeout for OpenTopography API calls
SHADOW_TIMEOUT = 180


class TestDemShadowStatus:
    """GET /api/v1/bionic/dem-shadow/status tests"""

    def test_status_returns_200(self):
        """Status endpoint returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/status",
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /dem-shadow/status returns 200")

    def test_status_active(self):
        """Status shows active when API key configured"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/status",
            timeout=30
        )
        data = response.json()
        assert data.get("status") == "active", f"Expected status=active, got {data.get('status')}"
        print("PASS: status=active")

    def test_status_mode_shadow(self):
        """Status shows mode=shadow (non-destructif)"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/status",
            timeout=30
        )
        data = response.json()
        mode = data.get("mode", "")
        assert "shadow" in mode.lower(), f"Expected mode containing 'shadow', got {mode}"
        print(f"PASS: mode={mode}")

    def test_status_impact_zero(self):
        """Status shows zero impact on production"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/status",
            timeout=30
        )
        data = response.json()
        impact = data.get("impact_on_production", "")
        assert impact == "zero", f"Expected impact_on_production=zero, got {impact}"
        print("PASS: impact_on_production=zero")

    def test_status_enriched_modules_tcve_tfe(self):
        """Status shows enriched_modules=[TCVE, TFE]"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/status",
            timeout=30
        )
        data = response.json()
        enriched = data.get("enriched_modules", [])
        assert "TCVE" in enriched, f"Expected TCVE in enriched_modules, got {enriched}"
        assert "TFE" in enriched, f"Expected TFE in enriched_modules, got {enriched}"
        print(f"PASS: enriched_modules={enriched}")

    def test_status_three_endpoints(self):
        """Status lists 3 endpoints"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/status",
            timeout=30
        )
        data = response.json()
        endpoints = data.get("endpoints", [])
        assert len(endpoints) >= 3, f"Expected 3+ endpoints, got {len(endpoints)}"
        print(f"PASS: {len(endpoints)} endpoints listed")

    def test_status_dem_key_configured(self):
        """Status shows dem_key_configured=true"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/status",
            timeout=30
        )
        data = response.json()
        key_ok = data.get("dem_key_configured", False)
        assert key_ok is True, f"Expected dem_key_configured=true, got {key_ok}"
        print("PASS: dem_key_configured=true")


class TestDemShadowPipeline:
    """POST /api/v1/bionic/dem-shadow/pipeline tests"""

    def test_pipeline_moose_laurentides_200(self):
        """Shadow pipeline for moose/Laurentides returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/pipeline",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=SHADOW_TIMEOUT
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:500]}"
        print("PASS: POST /dem-shadow/pipeline moose/Laurentides returns 200")

    def test_pipeline_returns_json(self):
        """Pipeline returns valid JSON with expected structure"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/pipeline",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=SHADOW_TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()
        # Should have key fields regardless of DEM status
        assert "dem_active" in data, "Expected dem_active field"
        assert "mode" in data, "Expected mode field"
        assert "validation" in data, "Expected validation field"
        print(f"PASS: Pipeline returns valid JSON with dem_active={data.get('dem_active')}")

    def test_pipeline_dem_active_boolean(self):
        """Pipeline returns dem_active as boolean (true when API works, false when rate limited)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/pipeline",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=SHADOW_TIMEOUT
        )
        data = response.json()
        dem_active = data.get("dem_active")
        assert isinstance(dem_active, bool), f"Expected dem_active to be boolean, got {type(dem_active)}"
        if dem_active:
            print("PASS: dem_active=true (real DEM data injected)")
        else:
            print("PASS: dem_active=false (fallback to synthetic - likely rate limited)")

    def test_pipeline_shadow_dem_when_active(self):
        """Pipeline returns shadow_dem with elevation_stats when DEM API is available"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/pipeline",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=SHADOW_TIMEOUT
        )
        data = response.json()
        dem_active = data.get("dem_active", False)
        shadow_dem = data.get("shadow_dem")
        
        if dem_active:
            assert shadow_dem is not None, "Expected shadow_dem when dem_active=true"
            stats = shadow_dem.get("elevation_stats", {})
            assert "elevation_min" in stats, f"Expected elevation_min in stats"
            elev_min = stats.get("elevation_min", 0)
            elev_max = stats.get("elevation_max", 0)
            assert elev_max > elev_min, f"Expected max > min: {elev_max} > {elev_min}"
            print(f"PASS: shadow_dem.elevation_stats: min={elev_min}, max={elev_max}")
        else:
            # shadow_dem should be None when rate limited
            assert shadow_dem is None, f"Expected shadow_dem=None when dem_active=false"
            print("PASS: shadow_dem=None (rate limited - graceful degradation)")

    def test_pipeline_tcve_stats_present(self):
        """Pipeline returns tcve_stats_with_real_dem (may be empty if rate limited)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/pipeline",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=SHADOW_TIMEOUT
        )
        data = response.json()
        tcve_stats = data.get("tcve_stats_with_real_dem", {})
        # Stats should be present (even if empty when rate limited)
        assert "tcve_stats_with_real_dem" in data, "Expected tcve_stats_with_real_dem field"
        print(f"PASS: tcve_stats_with_real_dem present: {list(tcve_stats.keys()) if tcve_stats else 'empty (rate limited)'}")

    def test_pipeline_tfe_stats_present(self):
        """Pipeline returns tfe_stats_with_real_dem (may be empty if rate limited)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/pipeline",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=SHADOW_TIMEOUT
        )
        data = response.json()
        tfe_stats = data.get("tfe_stats_with_real_dem", {})
        assert "tfe_stats_with_real_dem" in data, "Expected tfe_stats_with_real_dem field"
        print(f"PASS: tfe_stats_with_real_dem present: {list(tfe_stats.keys()) if tfe_stats else 'empty (rate limited)'}")

    def test_pipeline_validation_certified_modules_unmodified(self):
        """Pipeline validation shows certified_modules_unmodified=true"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/pipeline",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=SHADOW_TIMEOUT
        )
        data = response.json()
        validation = data.get("validation", {})
        assert validation.get("certified_modules_unmodified") is True, \
            f"Expected certified_modules_unmodified=true, got {validation.get('certified_modules_unmodified')}"
        print("PASS: validation.certified_modules_unmodified=true")

    def test_pipeline_validation_shadow_mode(self):
        """Pipeline validation shows shadow_mode=true"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/pipeline",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=SHADOW_TIMEOUT
        )
        data = response.json()
        validation = data.get("validation", {})
        assert validation.get("shadow_mode") is True, \
            f"Expected shadow_mode=true, got {validation.get('shadow_mode')}"
        print("PASS: validation.shadow_mode=true")

    def test_pipeline_validation_dem_injection_matches_active(self):
        """Pipeline validation.dem_real_data_injected matches dem_active"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/pipeline",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=SHADOW_TIMEOUT
        )
        data = response.json()
        dem_active = data.get("dem_active", False)
        validation = data.get("validation", {})
        dem_injected = validation.get("dem_real_data_injected", False)
        assert dem_active == dem_injected, \
            f"Expected dem_active ({dem_active}) to match validation.dem_real_data_injected ({dem_injected})"
        print(f"PASS: dem_active={dem_active} matches validation.dem_real_data_injected={dem_injected}")

    def test_pipeline_invalid_species_400(self):
        """Invalid species returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/pipeline",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "invalid_animal",
                "resolution": 30
            },
            timeout=30
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: Invalid species returns 400")

    def test_pipeline_source_ids(self):
        """Pipeline returns pipeline_source_ids from all modules"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/pipeline",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=SHADOW_TIMEOUT
        )
        data = response.json()
        source_ids = data.get("pipeline_source_ids", {})
        assert len(source_ids) >= 9, f"Expected 9+ source_ids, got {len(source_ids)}: {source_ids.keys()}"
        print(f"PASS: pipeline_source_ids: {list(source_ids.keys())}")


class TestDemShadowCompare:
    """POST /api/v1/bionic/dem-shadow/compare tests"""

    def test_compare_moose_laurentides_200(self):
        """Compare endpoint for moose/Laurentides returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/compare",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=SHADOW_TIMEOUT
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:500]}"
        print("PASS: POST /dem-shadow/compare moose/Laurentides returns 200")

    def test_compare_synthetic_section(self):
        """Compare returns synthetic section with tcve/tfe stats"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/compare",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=SHADOW_TIMEOUT
        )
        data = response.json()
        synthetic = data.get("synthetic", {})
        assert synthetic, "Expected synthetic section"
        assert "tcve_stats" in synthetic, f"Expected tcve_stats in synthetic, got {synthetic.keys()}"
        assert "tfe_stats" in synthetic, f"Expected tfe_stats in synthetic, got {synthetic.keys()}"
        print(f"PASS: synthetic section: {list(synthetic.keys())}")

    def test_compare_shadow_real_dem_section(self):
        """Compare returns shadow_real_dem section (dem_active may be false if rate limited)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/compare",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=SHADOW_TIMEOUT
        )
        data = response.json()
        shadow = data.get("shadow_real_dem", {})
        assert shadow, "Expected shadow_real_dem section"
        dem_active = shadow.get("dem_active", False)
        if dem_active:
            print(f"PASS: shadow_real_dem section: dem_active=true, keys={list(shadow.keys())}")
        else:
            print(f"PASS: shadow_real_dem section: dem_active=false (rate limited), keys={list(shadow.keys())}")

    def test_compare_deltas_structure(self):
        """Compare returns deltas structure with tcve and tfe keys"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/compare",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=SHADOW_TIMEOUT
        )
        data = response.json()
        deltas = data.get("deltas", {})
        assert "tcve" in deltas, f"Expected tcve in deltas, got {deltas.keys()}"
        assert "tfe" in deltas, f"Expected tfe in deltas, got {deltas.keys()}"
        print(f"PASS: deltas structure: tcve={deltas.get('tcve')}, tfe={deltas.get('tfe')}")

    def test_compare_validation_certified_unmodified(self):
        """Compare validation shows certified_modules_unmodified=true"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/compare",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=SHADOW_TIMEOUT
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        validation = data.get("validation", {})
        assert validation.get("certified_modules_unmodified") is True, \
            f"Expected certified_modules_unmodified=true, got {validation}"
        print("PASS: validation.certified_modules_unmodified=true")

    def test_compare_validation_shadow_non_destructive(self):
        """Compare validation shows shadow_mode_non_destructive=true"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/compare",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=SHADOW_TIMEOUT
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        validation = data.get("validation", {})
        assert validation.get("shadow_mode_non_destructive") is True, \
            f"Expected shadow_mode_non_destructive=true, got {validation}"
        print("PASS: validation.shadow_mode_non_destructive=true")

    def test_compare_validation_zero_impact(self):
        """Compare validation shows zero_impact_on_production=true"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/compare",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=SHADOW_TIMEOUT
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        validation = data.get("validation", {})
        assert validation.get("zero_impact_on_production") is True, \
            f"Expected zero_impact_on_production=true, got {validation}"
        print("PASS: validation.zero_impact_on_production=true")

    def test_compare_invalid_species_400(self):
        """Invalid species returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem-shadow/compare",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "invalid_animal",
                "resolution": 30
            },
            timeout=30
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: Invalid species returns 400")


class TestNonRegression:
    """Non-regression tests: existing endpoints still work"""

    def test_pipeline_full_analysis_works(self):
        """POST /pipeline/full-analysis still works (synthetic unchanged)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/pipeline/full-analysis",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=60
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        # Should have 10 pipeline source IDs for synthetic
        source_ids = data.get("pipeline_source_ids", {})
        assert len(source_ids) >= 9, f"Expected 9+ source_ids, got {len(source_ids)}"
        print(f"PASS: Non-regression: /pipeline/full-analysis works ({len(source_ids)} modules)")

    def test_dem_analyze_or_rate_limited(self):
        """POST /dem/analyze still works (may return 401 if rate limited)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/dem/analyze",
            json={
                "bounds": LAURENTIDES_BOUNDS,
                "species": "moose",
                "resolution": 30
            },
            timeout=SHADOW_TIMEOUT
        )
        # Accept 200 (success) or 401 (rate limited - API key temporarily rejected)
        if response.status_code == 200:
            data = response.json()
            assert data.get("status") == "success", f"Expected status=success, got {data.get('status')}"
            print("PASS: Non-regression: /dem/analyze works")
        elif response.status_code == 401:
            # OpenTopography rate limit hit (200 calls/24h)
            print("PASS: Non-regression: /dem/analyze returns 401 (rate limited - expected)")
            pytest.skip("OpenTopography rate limit hit (200 calls/24h)")
        else:
            assert False, f"Unexpected status {response.status_code}: {response.text[:200]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
