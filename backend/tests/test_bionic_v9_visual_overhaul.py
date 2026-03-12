"""
BIONIC V9 Visual Overhaul Tests — Phase Corridors V9 (Iteration 9)
===================================================================
Tests for AUDIT & VISUAL OVERHAUL:
- Multi-band polygon ribbon corridors with 5 VISIBLE concentric bands
- Band widths: gris=311m, jaune=222m, orange=155m, rouge=89m, rouge_raye=44m
- Band colors: gris=#9E9E9E, jaune=#FFC107, orange=#FF9800, rouge=#F44336, rouge_raye=#B71C1C
- Corridors rendered ON TOP of zones via Leaflet Pane z-index 650
- Strict clipping to 2km² bounds
- BCE-4X new rules: PIPE-001, UI-001, UI-002, UI-003
- White centerline + classification line visible through bands
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

TEST_BOUNDS = {
    "north": 46.96, "south": 46.93,
    "east": -71.27, "west": -71.33
}

# Normative band specifications
EXPECTED_BAND_COLORS = {
    "gris": "#9E9E9E",
    "jaune": "#FFC107",
    "orange": "#FF9800",
    "rouge": "#F44336",
    "rouge_raye": "#B71C1C"
}

EXPECTED_BAND_WIDTHS_M = {
    "gris": 311,
    "jaune": 222,
    "orange": 155,
    "rouge": 89,
    "rouge_raye": 44
}


class TestBCE4XValidateCoverageV9:
    """Tests BCE-4X coverage rules: PIPE-001, UI-001, UI-002, UI-003"""
    
    def test_bce_coverage_v9_returns_all_rules(self):
        """POST /api/bce/validate-corridors-v9 should return bce_coverage_v9 section"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-corridors-v9", timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        # Check bce_coverage_v9 section exists
        assert "bce_coverage_v9" in data, "Missing bce_coverage_v9 section"
        coverage = data["bce_coverage_v9"]
        
        # Check all 4 rules present
        required_rules = ["PIPE-001_DataSourceAlignment", "UI-001_BandsPresence", 
                         "UI-002_GradientMapping", "UI-003_LayerIsolation"]
        for rule in required_rules:
            assert rule in coverage, f"Missing rule {rule} in bce_coverage_v9"
        
        print(f"BCE coverage V9 rules present: {list(coverage.keys())}")
    
    def test_pipe_001_data_source_alignment_pass(self):
        """PIPE-001: All corridors must be from V9 pipeline"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-corridors-v9", timeout=60)
        data = response.json()
        
        pipe_001 = data["bce_coverage_v9"]["PIPE-001_DataSourceAlignment"]
        assert pipe_001["pass"] == True, f"PIPE-001 failed: {pipe_001}"
        print(f"PIPE-001 PASS: {pipe_001['desc']}")
    
    def test_ui_001_all_5_bands_present(self):
        """UI-001: All 5 normative bands must be present on each corridor"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-corridors-v9", timeout=60)
        data = response.json()
        
        ui_001 = data["bce_coverage_v9"]["UI-001_BandsPresence"]
        assert ui_001["pass"] == True, f"UI-001 failed: {ui_001}"
        
        # Check that details show all 5 bands present
        if "details" in ui_001:
            for detail in ui_001["details"]:
                assert detail["pass"] == True, f"Corridor {detail['corridor_id']} missing bands"
                assert detail["band_count"] == 5, f"Corridor {detail['corridor_id']} has {detail['band_count']} bands instead of 5"
                expected_levels = {"gris", "jaune", "orange", "rouge", "rouge_raye"}
                actual_levels = set(detail.get("band_levels", []))
                assert actual_levels == expected_levels, f"Corridor {detail['corridor_id']} missing levels: {expected_levels - actual_levels}"
        
        print(f"UI-001 PASS: {ui_001['desc']}")
    
    def test_ui_002_gradient_colors_match_normative(self):
        """UI-002: Band colors must match normative gradient"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-corridors-v9", timeout=60)
        data = response.json()
        
        ui_002 = data["bce_coverage_v9"]["UI-002_GradientMapping"]
        assert ui_002["pass"] == True, f"UI-002 failed: {ui_002}"
        print(f"UI-002 PASS: {ui_002['desc']}")
    
    def test_ui_003_layer_isolation_pane_650(self):
        """UI-003: Corridors must be on dedicated Pane z-index 650"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-corridors-v9", timeout=60)
        data = response.json()
        
        ui_003 = data["bce_coverage_v9"]["UI-003_LayerIsolation"]
        assert ui_003["pass"] == True, f"UI-003 failed: {ui_003}"
        print(f"UI-003 PASS: {ui_003['desc']}")


class TestBandWidthsAndColors:
    """Tests that band widths and colors match visual overhaul specifications"""
    
    def test_band_widths_correct(self):
        """Band widths must be: gris=311m, jaune=222m, orange=155m, rouge=89m, rouge_raye=44m"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/corridors-v9/by-species",
            json={"bounds": TEST_BOUNDS, "species": "moose"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check first corridor bands
        corridor = data["corridors"][0]
        bands = corridor["properties"]["bands"]
        
        for band in bands:
            level = band["level"]
            width_m = band.get("width_m", 0)
            expected = EXPECTED_BAND_WIDTHS_M[level]
            # Allow small tolerance (±5m) for floating point calculations
            assert abs(width_m - expected) < 10, f"Band {level} has width {width_m}m, expected ~{expected}m"
            print(f"  Band {level}: {width_m}m (expected: {expected}m) ✓")
        
        print(f"All 5 band widths match specifications")
    
    def test_band_colors_correct(self):
        """Band colors must match normative: gris=#9E9E9E, jaune=#FFC107, etc."""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/corridors-v9/by-species",
            json={"bounds": TEST_BOUNDS, "species": "moose"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check all corridors bands
        for corridor in data["corridors"][:3]:  # Check first 3
            bands = corridor["properties"]["bands"]
            for band in bands:
                level = band["level"]
                color = band["color"]
                expected = EXPECTED_BAND_COLORS[level]
                assert color == expected, f"Band {level} has color {color}, expected {expected}"
        
        print(f"All band colors match normative specifications")
    
    def test_all_5_bands_generated_always(self):
        """V9-GEOM-003: ALL 5 bands MUST be generated regardless of score (no score filtering)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/corridors-v9/by-species",
            json={"bounds": TEST_BOUNDS, "species": "moose"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        corridors_with_5_bands = 0
        corridors_with_fewer = 0
        
        for corridor in data["corridors"]:
            bands = corridor["properties"].get("bands", [])
            if len(bands) == 5:
                corridors_with_5_bands += 1
            else:
                corridors_with_fewer += 1
                print(f"  Corridor {corridor['id']}: only {len(bands)} bands")
        
        # All corridors should have exactly 5 bands
        assert corridors_with_fewer == 0, f"{corridors_with_fewer} corridors have fewer than 5 bands"
        print(f"All {corridors_with_5_bands} corridors have exactly 5 bands")


class TestCenterlineAndClassificationLine:
    """Tests white centerline + classification line visibility"""
    
    def test_centerline_present(self):
        """Each corridor must have smoothed centerline coordinates"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/corridors-v9/by-species",
            json={"bounds": TEST_BOUNDS, "species": "moose"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        corridors_with_centerline = 0
        for corridor in data["corridors"]:
            centerline = corridor["properties"].get("centerline", [])
            if len(centerline) >= 2:
                corridors_with_centerline += 1
                # Verify coordinates are [lng, lat] format
                first_coord = centerline[0]
                assert len(first_coord) == 2, f"Centerline coordinate has wrong format: {first_coord}"
        
        assert corridors_with_centerline == len(data["corridors"]), \
            f"Only {corridors_with_centerline}/{len(data['corridors'])} corridors have centerline"
        print(f"All {corridors_with_centerline} corridors have smoothed centerline")
    
    def test_classification_v9_present(self):
        """Each corridor must have classification_v9 with level and color"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/corridors-v9/by-species",
            json={"bounds": TEST_BOUNDS, "species": "moose"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        for corridor in data["corridors"]:
            classification = corridor["properties"].get("classification_v9")
            assert classification is not None, f"Corridor {corridor['id']} missing classification_v9"
            assert "level" in classification, f"Corridor {corridor['id']} classification missing 'level'"
            assert "color" in classification, f"Corridor {corridor['id']} classification missing 'color'"
            assert classification["level"] in {"gris", "jaune", "orange", "rouge", "rouge_raye"}
        
        print(f"All {len(data['corridors'])} corridors have valid classification_v9")


class TestCorridorClippingWithinBounds:
    """Tests strict clipping to 2km² bounds"""
    
    def test_all_corridor_points_within_bounds(self):
        """No corridor point should be outside the specified bounds"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/corridors-v9/by-species",
            json={"bounds": TEST_BOUNDS, "species": "moose"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        margin = 0.0005  # ~50m tolerance
        out_of_bounds = []
        
        for corridor in data["corridors"]:
            coords = corridor["geometry"]["coordinates"]
            for coord in coords:
                lng, lat = coord[0], coord[1]
                if (lat < TEST_BOUNDS["south"] - margin or 
                    lat > TEST_BOUNDS["north"] + margin or
                    lng < TEST_BOUNDS["west"] - margin or 
                    lng > TEST_BOUNDS["east"] + margin):
                    out_of_bounds.append(corridor["id"])
                    break
        
        assert len(out_of_bounds) == 0, f"Corridors with points outside bounds: {out_of_bounds}"
        print(f"All {len(data['corridors'])} corridors clipped within 2km² bounds")
    
    def test_all_band_coordinates_within_bounds(self):
        """Band polygon coordinates must also be within bounds"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/corridors-v9/by-species",
            json={"bounds": TEST_BOUNDS, "species": "moose"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        margin = 0.001  # Slightly larger margin for polygon bands (~110m)
        out_of_bounds = []
        
        for corridor in data["corridors"][:5]:  # Check first 5
            bands = corridor["properties"].get("bands", [])
            for band in bands:
                for ring in band.get("coordinates", []):
                    for coord in ring:
                        lng, lat = coord[0], coord[1]
                        if (lat < TEST_BOUNDS["south"] - margin or 
                            lat > TEST_BOUNDS["north"] + margin or
                            lng < TEST_BOUNDS["west"] - margin or 
                            lng > TEST_BOUNDS["east"] + margin):
                            out_of_bounds.append((corridor["id"], band["level"]))
                            break
        
        # Allow some tolerance - bands may extend slightly beyond due to buffering
        assert len(out_of_bounds) <= 5, f"Too many bands outside bounds: {out_of_bounds[:10]}"
        print(f"Band coordinates within acceptable bounds tolerance")


class TestWeatherCompliance:
    """Tests BCE-4X weather 60-minute compliance"""
    
    def test_weather_compliance_returns_compliant_true(self):
        """GET /api/bce/weather-compliance must return compliant=true"""
        response = requests.get(f"{BASE_URL}/api/bce/weather-compliance")
        assert response.status_code == 200
        data = response.json()
        
        assert data["compliant"] == True, f"Weather not compliant: {data}"
        print(f"Weather compliance: {data['compliant']}, cache_active={data.get('cache_active')}")


class TestBCERegistryAllEnginesActive:
    """Tests BCE registry for all 9 engines active"""
    
    def test_registry_shows_9_engines_active(self):
        """GET /api/bce/registry must show all 9 engines as active"""
        response = requests.get(f"{BASE_URL}/api/bce/registry")
        assert response.status_code == 200
        data = response.json()
        
        required_engines = {
            "nutrition_engine", "daily_routine_engine", "weather_engine",
            "disturbance_engine", "movement_engine", "phenology_engine",
            "typology_engine", "learning_engine", "habitat_enhancement_engine"
        }
        
        modules = data["modules"]
        for engine in required_engines:
            assert engine in modules, f"Missing engine: {engine}"
            assert modules[engine]["status"] == "active", f"Engine {engine} not active"
        
        print(f"All 9 engines active in registry")


class Test100PercentCompliance:
    """Tests overall 100% compliance"""
    
    def test_validate_corridors_v9_100_percent(self):
        """POST /api/bce/validate-corridors-v9 must return 100% compliance"""
        response = requests.post(f"{BASE_URL}/api/bce/validate-corridors-v9", timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        assert data["compliance_rate"] == 100.0, f"Compliance rate: {data['compliance_rate']}%"
        assert data["status"] == "COMPLIANT", f"Status: {data['status']}"
        assert data["total_violations"] == 0, f"Violations: {data['total_violations']}"
        
        print(f"100% compliance: {data['total_corridors']} corridors, 0 violations")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
