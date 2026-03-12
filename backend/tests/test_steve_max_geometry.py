"""
STEVE-MAX++ Geometry Compliance Tests
=====================================
Testing corridor bounding box compliance, band width reduction (40%), 
and clipping pipeline validation for V9 corridors.

Tests:
1. POST /api/v1/bionic/organic-zones - corridors with bands WITHIN 2km analysis box
2. Band widths respect 40% reduction: gris≤72m, jaune≤48m, orange≤30m, rouge≤18m, rouge_raye≤9m
3. POST /api/bce/validate-geometry-compliance - CLIP-002, PIPE-002, GEOM-005 checks
4. POST /api/bce/validate-color-contract - 6 color contract checks
5. POST /api/bce/validate-corridors-runtime - GEOM-004 and GEOM-005 runtime checks
"""

import pytest
import requests
import os
import math

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# STEVE-MAX: Normative band width limits (40% reduction)
NORMATIVE_MAX_WIDTHS = {
    "gris": 72,
    "jaune": 48,
    "orange": 30,
    "rouge": 18,
    "rouge_raye": 9,
}

# Test area - same as provided in misc_info
TEST_WAYPOINT = {"lat": 46.815, "lng": -71.205}
TEST_API_BOUNDS = {
    "north": 46.83,
    "south": 46.80,
    "east": -71.19,
    "west": -71.22,
}

# Computed 2km analysis box from waypoint center (1000m radius)
# Using metersPerDegLat=111320 at Quebec latitude ~46.8N
METERS_PER_DEG_LAT = 111320
HALF_M = 1000  # 2km / 2 = 1000m

def compute_2km_box(waypoint_lat, waypoint_lng):
    """Compute strict 2km analysis box from waypoint center."""
    lat_rad = math.radians(waypoint_lat)
    delta_lat = HALF_M / METERS_PER_DEG_LAT
    delta_lng = HALF_M / (METERS_PER_DEG_LAT * math.cos(lat_rad))
    return {
        "south": waypoint_lat - delta_lat,
        "north": waypoint_lat + delta_lat,
        "west": waypoint_lng - delta_lng,
        "east": waypoint_lng + delta_lng,
    }

# Expected 2km box for test waypoint
EXPECTED_2KM_BOX = compute_2km_box(TEST_WAYPOINT["lat"], TEST_WAYPOINT["lng"])


class TestSteveMaxGeometry:
    """STEVE-MAX++ Geometry Compliance Tests"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session."""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def test_01_health_check(self):
        """Verify backend is healthy before running tests."""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"PASS: Backend healthy - {data.get('version', 'unknown')}")

    def test_02_organic_zones_returns_corridors_with_bands(self):
        """POST /api/v1/bionic/organic-zones returns corridors with band data."""
        payload = {
            "bounds": TEST_API_BOUNDS,
            "layers": ["habitats", "alimentation", "repos", "rut", "trajets"],
            "species": "moose",
            "resolution": 40,
            "max_zones_per_layer": 5,
            "waypoint_center": TEST_WAYPOINT,
        }
        response = self.session.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:500]}"
        
        data = response.json()
        corridors = data.get("corridors", [])
        print(f"INFO: Received {len(corridors)} corridors")
        
        # V9 corridors should have bands
        corridors_with_bands = [c for c in corridors if c.get("properties", {}).get("has_bands")]
        print(f"INFO: {len(corridors_with_bands)} corridors have bands")
        
        # Store corridors for subsequent tests
        self.__class__.corridors = corridors
        self.__class__.data = data
        
        assert len(corridors) > 0, "Expected at least 1 corridor"
        print(f"PASS: organic-zones returned {len(corridors)} corridors, {len(corridors_with_bands)} with bands")

    def test_03_all_band_coordinates_within_2km_box(self):
        """BCE-4X-GEOM-004: ALL band coordinates must be WITHIN the 2km analysis box."""
        corridors = getattr(self.__class__, 'corridors', [])
        if not corridors:
            pytest.skip("No corridors from previous test")
        
        box = EXPECTED_2KM_BOX
        print(f"INFO: 2km analysis box: south={box['south']:.6f}, north={box['north']:.6f}, west={box['west']:.6f}, east={box['east']:.6f}")
        
        total_coords = 0
        out_of_bounds = 0
        violation_samples = []
        
        for corridor in corridors:
            props = corridor.get("properties", {})
            bands = props.get("bands", [])
            for band in bands:
                for ring in band.get("coordinates", []):
                    for coord in ring:
                        total_coords += 1
                        lng, lat = coord[0], coord[1]
                        # Check with small tolerance (0.00001 degrees ~ 1m)
                        if (lat < box["south"] - 0.00001 or lat > box["north"] + 0.00001 or
                            lng < box["west"] - 0.00001 or lng > box["east"] + 0.00001):
                            out_of_bounds += 1
                            if len(violation_samples) < 5:
                                violation_samples.append(f"[{lng:.6f}, {lat:.6f}]")
        
        print(f"INFO: Checked {total_coords} band coordinates")
        
        if out_of_bounds > 0:
            print(f"FAIL: {out_of_bounds}/{total_coords} coordinates OUTSIDE 2km box")
            print(f"Sample violations: {violation_samples}")
        
        assert out_of_bounds == 0, f"GEOM-004 FAIL: {out_of_bounds} band coordinates outside 2km bounds. Samples: {violation_samples}"
        print(f"PASS: BCE-4X-GEOM-004 - All {total_coords} band coordinates within 2km bounds")

    def test_04_band_widths_respect_40_percent_reduction(self):
        """BCE-4X-GEOM-005: Band widths must respect 40% reduced limits."""
        corridors = getattr(self.__class__, 'corridors', [])
        if not corridors:
            pytest.skip("No corridors from previous test")
        
        violations = []
        checked_bands = 0
        
        for corridor in corridors:
            props = corridor.get("properties", {})
            bands = props.get("bands", [])
            for band in bands:
                level = band.get("level")
                width_m = band.get("width_m", 0)
                max_allowed = NORMATIVE_MAX_WIDTHS.get(level, 999)
                checked_bands += 1
                
                if width_m > max_allowed + 0.5:  # small tolerance
                    violations.append(f"{level}: {width_m}m > {max_allowed}m max")
        
        print(f"INFO: Checked {checked_bands} bands for width compliance")
        
        if violations:
            print(f"FAIL: Band width violations: {violations[:5]}")
        
        assert len(violations) == 0, f"GEOM-005 FAIL: {len(violations)} width violations: {violations[:5]}"
        print(f"PASS: BCE-4X-GEOM-005 - All {checked_bands} bands within 40%-reduced width limits")

    def test_05_corridors_have_5_band_levels(self):
        """V9-GEOM-003: All 5 band levels must be generated (gris/jaune/orange/rouge/rouge_raye)."""
        corridors = getattr(self.__class__, 'corridors', [])
        if not corridors:
            pytest.skip("No corridors from previous test")
        
        expected_levels = {"gris", "jaune", "orange", "rouge", "rouge_raye"}
        corridors_with_all_5 = 0
        missing_levels_samples = []
        
        for idx, corridor in enumerate(corridors):
            props = corridor.get("properties", {})
            bands = props.get("bands", [])
            levels_present = {band.get("level") for band in bands}
            
            if levels_present == expected_levels:
                corridors_with_all_5 += 1
            else:
                missing = expected_levels - levels_present
                if len(missing_levels_samples) < 3:
                    missing_levels_samples.append(f"Corridor {idx}: missing {missing}")
        
        print(f"INFO: {corridors_with_all_5}/{len(corridors)} corridors have all 5 band levels")
        
        if missing_levels_samples:
            print(f"INFO: Some corridors missing levels: {missing_levels_samples}")
        
        # At least 50% of corridors should have all 5 bands
        success_rate = corridors_with_all_5 / len(corridors) if corridors else 0
        assert success_rate >= 0.5, f"Expected ≥50% corridors with all 5 bands, got {success_rate*100:.0f}%"
        print(f"PASS: V9-GEOM-003 - {corridors_with_all_5}/{len(corridors)} ({success_rate*100:.0f}%) corridors have 5-level gradient")

    def test_06_frontend_filter_properties(self):
        """Frontend filtering: corridors should have inPerimeter and hasBands properties."""
        corridors = getattr(self.__class__, 'corridors', [])
        if not corridors:
            pytest.skip("No corridors from previous test")
        
        in_perimeter_count = 0
        has_bands_count = 0
        both_true_count = 0
        
        for corridor in corridors:
            props = corridor.get("properties", {})
            in_perimeter = props.get("in_perimeter", False)
            has_bands = props.get("has_bands", False)
            
            if in_perimeter:
                in_perimeter_count += 1
            if has_bands:
                has_bands_count += 1
            if in_perimeter and has_bands:
                both_true_count += 1
        
        print(f"INFO: Corridors with inPerimeter=true: {in_perimeter_count}/{len(corridors)}")
        print(f"INFO: Corridors with hasBands=true: {has_bands_count}/{len(corridors)}")
        print(f"INFO: Corridors passing frontend filter (both true): {both_true_count}/{len(corridors)}")
        
        # At least some corridors should be renderable
        assert both_true_count > 0, "No corridors pass frontend filter (inPerimeter=true AND hasBands=true)"
        print(f"PASS: Frontend filter - {both_true_count} corridors will render (inPerimeter && hasBands)")


class TestBCEValidators:
    """BCE-4X Validator Endpoint Tests"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session."""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def test_07_validate_geometry_compliance(self):
        """POST /api/bce/validate-geometry-compliance - CLIP-002, PIPE-002, GEOM-005 checks."""
        response = self.session.post(f"{BASE_URL}/api/bce/validate-geometry-compliance")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        print(f"INFO: Geometry compliance status: {data.get('status')}")
        
        checks = data.get("checks", [])
        for check in checks:
            status = check.get("status")
            name = check.get("name")
            detail = check.get("detail", "")
            print(f"  {name}: {status} - {detail[:60]}")
        
        # All 3 checks should PASS
        failed_checks = [c for c in checks if c.get("status") != "PASS"]
        assert len(failed_checks) == 0, f"Geometry compliance FAIL: {[c['name'] for c in failed_checks]}"
        print(f"PASS: All {len(checks)} geometry compliance checks PASS")

    def test_08_validate_color_contract(self):
        """POST /api/bce/validate-color-contract - All 6 color contract rules."""
        response = self.session.post(f"{BASE_URL}/api/bce/validate-color-contract")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        print(f"INFO: Color contract status: {data.get('status')}")
        
        checks = data.get("checks", [])
        for check in checks:
            status = check.get("status")
            name = check.get("name")
            detail = check.get("detail", "")
            print(f"  {name}: {status} - {detail[:60]}")
        
        # All 6 checks should PASS
        failed_checks = [c for c in checks if c.get("status") != "PASS"]
        assert len(failed_checks) == 0, f"Color contract FAIL: {[c['name'] for c in failed_checks]}"
        print(f"PASS: All {len(checks)} color contract checks PASS")

    def test_09_validate_corridors_runtime_geom_004_005(self):
        """POST /api/bce/validate-corridors-runtime - GEOM-004 and GEOM-005 with actual data."""
        # First get corridors
        payload = {
            "bounds": TEST_API_BOUNDS,
            "layers": ["habitats", "alimentation", "repos", "rut", "trajets"],
            "species": "moose",
            "resolution": 40,
            "max_zones_per_layer": 5,
            "waypoint_center": TEST_WAYPOINT,
        }
        zones_response = self.session.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload)
        assert zones_response.status_code == 200
        
        corridors = zones_response.json().get("corridors", [])
        if not corridors:
            pytest.skip("No corridors to validate")
        
        # Use the 2km analysis box for runtime validation
        runtime_payload = {
            "corridors": corridors,
            "bounds": EXPECTED_2KM_BOX,
        }
        
        response = self.session.post(f"{BASE_URL}/api/bce/validate-corridors-runtime", json=runtime_payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        print(f"INFO: Runtime validation status: {data.get('status')}")
        
        checks = data.get("checks", [])
        for check in checks:
            status = check.get("status")
            name = check.get("name")
            detail = check.get("detail", "")
            print(f"  {name}: {status} - {detail[:80]}")
        
        # Both GEOM-004 and GEOM-005 should PASS
        geom_004 = next((c for c in checks if "GEOM-004" in c.get("name", "")), None)
        geom_005 = next((c for c in checks if "GEOM-005" in c.get("name", "")), None)
        
        assert geom_004 and geom_004.get("status") == "PASS", f"GEOM-004 failed: {geom_004}"
        assert geom_005 and geom_005.get("status") == "PASS", f"GEOM-005 failed: {geom_005}"
        print("PASS: Runtime validation - GEOM-004 and GEOM-005 both PASS")


class TestPipelineOrder:
    """Tests for corridor processing pipeline order."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session."""
        self.session = requests.Session()

    def test_10_corridors_v9_pipeline_order(self):
        """Verify corridors_v9.py has correct pipeline: clip → smooth → buffer → re-clip."""
        # Read the corridors_v9.py file content via API or direct check
        # The geometry_compliance validator already checks this, but let's verify
        response = self.session.post(f"{BASE_URL}/api/bce/validate-geometry-compliance")
        assert response.status_code == 200
        
        data = response.json()
        checks = data.get("checks", [])
        
        clip_002 = next((c for c in checks if "CLIP-002" in c.get("name", "")), None)
        assert clip_002 is not None, "CLIP-002 check not found"
        assert clip_002.get("status") == "PASS", f"CLIP-002 FAIL: {clip_002.get('detail')}"
        
        print("PASS: Pipeline order (clip → smooth → buffer → re-clip) verified via CLIP-002")


class TestBandWidthDetails:
    """Detailed band width validation tests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session."""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def test_11_band_width_detailed_check(self):
        """Check each band level's width_m values are within normative limits."""
        payload = {
            "bounds": TEST_API_BOUNDS,
            "layers": ["habitats", "alimentation", "repos", "rut", "trajets"],
            "species": "moose",
            "resolution": 40,
            "max_zones_per_layer": 5,
            "waypoint_center": TEST_WAYPOINT,
        }
        response = self.session.post(f"{BASE_URL}/api/v1/bionic/organic-zones", json=payload)
        assert response.status_code == 200
        
        corridors = response.json().get("corridors", [])
        if not corridors:
            pytest.skip("No corridors")
        
        # Collect all widths by level
        widths_by_level = {level: [] for level in NORMATIVE_MAX_WIDTHS.keys()}
        
        for corridor in corridors:
            bands = corridor.get("properties", {}).get("bands", [])
            for band in bands:
                level = band.get("level")
                width_m = band.get("width_m", 0)
                if level in widths_by_level:
                    widths_by_level[level].append(width_m)
        
        # Report and validate
        all_pass = True
        for level, max_width in NORMATIVE_MAX_WIDTHS.items():
            widths = widths_by_level.get(level, [])
            if widths:
                min_w = min(widths)
                max_w = max(widths)
                avg_w = sum(widths) / len(widths)
                over_limit = [w for w in widths if w > max_width + 0.5]
                
                status = "PASS" if not over_limit else "FAIL"
                if over_limit:
                    all_pass = False
                
                print(f"  {level}: min={min_w:.0f}m, max={max_w:.0f}m, avg={avg_w:.0f}m, limit={max_width}m [{status}]")
            else:
                print(f"  {level}: no data")
        
        assert all_pass, "Some band widths exceed normative limits"
        print("PASS: All band widths within 40%-reduced normative limits")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
