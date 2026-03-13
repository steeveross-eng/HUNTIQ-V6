"""
STEVE-MAX++ Iteration 14 Tests — +20% Corridor Width Increase
=============================================================
Tests:
1. BAND_RATIO values widened by +20% (gris=26m, jaune=17m, orange=11m, rouge=6m, rouge_raye=4m)
2. BCE-4X GEOM-005 validates new +20% widths
3. BCE-4X COR-006 corridor continuity validation
4. BCE-4X VIS-007 visual balance validation
5. Color harmonization between map/panel/core
6. BionicEngineHub shows 12 engines
"""

import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Expected +20% BAND_RATIO values
EXPECTED_BAND_RATIO = {
    "gris": {"ratio": 0.012, "min_m": 6, "max_m": 26},
    "jaune": {"ratio": 0.008, "min_m": 5, "max_m": 17},
    "orange": {"ratio": 0.005, "min_m": 2, "max_m": 11},
    "rouge": {"ratio": 0.004, "min_m": 1, "max_m": 6},
    "rouge_raye": {"ratio": 0.001, "min_m": 1, "max_m": 4},
}

# Expected NORMATIVE_MAX_WIDTHS
EXPECTED_NORMATIVE_MAX_WIDTHS = {
    "gris": 26,
    "jaune": 17,
    "orange": 11,
    "rouge": 6,
    "rouge_raye": 4,
}

# Expected color palette (normalized to uppercase for comparison)
EXPECTED_ZONE_COLORS = {
    "habitats": "#10B981",
    "rut": "#FF4D6D",
    "repos": "#8B5CF6",
    "alimentation": "#22C55E",
    "corridors": "#06B6D4",
    "peuplements": "#15803D",
    "ndvi": "#66BB6A",
    "hydro": "#3B82F6",
    "pentes": "#FF7043",
    "orientation": "#2196F3",
    "ensoleillement": "#FCD34D",
    "salines": "#FFFF00",
    "affuts": "#F5A623",
    "trajets": "#FF9800",
    "altitude": "#78909C",
}


class TestBandRatioWidening:
    """Tests for +20% corridor width increase in BAND_RATIO"""

    def test_band_ratio_gris_max_26m(self):
        """BAND_RATIO gris max_m should be 26 (+20% from 22)"""
        corridors_v9_path = "/app/backend/modules/bionic_engine_p0/engines/corridors_v9.py"
        with open(corridors_v9_path, "r") as f:
            content = f.read()
        
        assert '"max_m": 26' in content, f"gris max_m should be 26, not found in {corridors_v9_path}"
        assert '"ratio": 0.012' in content, f"gris ratio should be 0.012"
        print("PASS: BAND_RATIO gris = 0.012, max_m=26 (+20%)")

    def test_band_ratio_jaune_max_17m(self):
        """BAND_RATIO jaune max_m should be 17 (+20% from 14)"""
        corridors_v9_path = "/app/backend/modules/bionic_engine_p0/engines/corridors_v9.py"
        with open(corridors_v9_path, "r") as f:
            content = f.read()
        
        assert '"max_m": 17' in content, f"jaune max_m should be 17"
        print("PASS: BAND_RATIO jaune max_m=17 (+20%)")

    def test_band_ratio_orange_max_11m(self):
        """BAND_RATIO orange max_m should be 11 (+20% from 9)"""
        corridors_v9_path = "/app/backend/modules/bionic_engine_p0/engines/corridors_v9.py"
        with open(corridors_v9_path, "r") as f:
            content = f.read()
        
        assert '"max_m": 11' in content, f"orange max_m should be 11"
        print("PASS: BAND_RATIO orange max_m=11 (+20%)")

    def test_band_ratio_rouge_max_6m(self):
        """BAND_RATIO rouge max_m should be 6 (+20% from 5)"""
        corridors_v9_path = "/app/backend/modules/bionic_engine_p0/engines/corridors_v9.py"
        with open(corridors_v9_path, "r") as f:
            content = f.read()
        
        assert '"max_m": 6}' in content or ('"max_m": 6,' in content and 'rouge' in content), f"rouge max_m should be 6"
        print("PASS: BAND_RATIO rouge max_m=6 (+20%)")

    def test_band_ratio_rouge_raye_max_4m(self):
        """BAND_RATIO rouge_raye max_m should be 4 (+20% from 3)"""
        corridors_v9_path = "/app/backend/modules/bionic_engine_p0/engines/corridors_v9.py"
        with open(corridors_v9_path, "r") as f:
            content = f.read()
        
        assert '"max_m": 4}' in content, f"rouge_raye max_m should be 4"
        print("PASS: BAND_RATIO rouge_raye max_m=4 (+20%)")


class TestGeometryComplianceValidator:
    """Tests for BCE-4X GEOM-005 validation with +20% widths"""

    def test_normative_max_widths_updated(self):
        """NORMATIVE_MAX_WIDTHS should have +20% values"""
        gc_path = "/app/backend/bce/validators/geometry_compliance.py"
        with open(gc_path, "r") as f:
            content = f.read()
        
        for level, expected_max in EXPECTED_NORMATIVE_MAX_WIDTHS.items():
            assert f'"{level}": {expected_max}' in content, f"NORMATIVE_MAX_WIDTHS {level} should be {expected_max}"
        print(f"PASS: NORMATIVE_MAX_WIDTHS updated to +20%: {EXPECTED_NORMATIVE_MAX_WIDTHS}")

    def test_geom_005_api_returns_pass(self):
        """POST /api/bce/validate-geometry-compliance should return PASS"""
        resp = requests.post(f"{BASE_URL}/api/bce/validate-geometry-compliance", timeout=30)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert data.get("status") == "PASS", f"GEOM-005 status should be PASS, got {data.get('status')}"
        
        # Check GEOM-005 specific check
        checks = data.get("checks", [])
        geom_005_check = next((c for c in checks if "GEOM-005" in c.get("name", "")), None)
        assert geom_005_check is not None, "GEOM-005 check should be present"
        assert geom_005_check.get("status") == "PASS", f"GEOM-005 check should PASS: {geom_005_check}"
        print(f"PASS: BCE-4X GEOM-005 validates +20% widths: {geom_005_check.get('detail', '')}")


class TestCorridorContinuityValidation:
    """Tests for BCE-4X COR-006 corridor network continuity"""

    def test_cor_006_empty_corridors_pass(self):
        """COR-006 should PASS with empty corridors"""
        resp = requests.post(
            f"{BASE_URL}/api/bce/validate-corridor-continuity",
            json={"corridors": [], "zones": []},
            timeout=30
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert data.get("status") == "PASS", f"COR-006 should PASS with empty corridors: {data}"
        print("PASS: BCE-4X COR-006 passes with empty corridors")

    def test_cor_006_with_connected_corridors(self):
        """COR-006 should validate connected corridors"""
        # Create test corridors that are topologically connected
        test_corridors = [
            {
                "geometry": {"type": "LineString", "coordinates": [[-70.47, 46.75], [-70.46, 46.76]]},
                "properties": {"continuity_valid": True, "topology_connected": True}
            },
            {
                "geometry": {"type": "LineString", "coordinates": [[-70.46, 46.76], [-70.45, 46.77]]},
                "properties": {"continuity_valid": True, "topology_connected": True}
            }
        ]
        test_zones = [
            {
                "geometry": {"type": "Polygon", "coordinates": [[[-70.47, 46.75], [-70.46, 46.75], [-70.46, 46.76], [-70.47, 46.76], [-70.47, 46.75]]]},
                "properties": {"layer_id": "habitats"}
            }
        ]
        
        resp = requests.post(
            f"{BASE_URL}/api/bce/validate-corridor-continuity",
            json={"corridors": test_corridors, "zones": test_zones},
            timeout=30
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert "continuity_pct" in data, "Response should include continuity_pct"
        assert "total_endpoints" in data, "Response should include total_endpoints"
        print(f"PASS: BCE-4X COR-006 validates connected corridors: continuity={data.get('continuity_pct')}%")


class TestVisualBalanceValidation:
    """Tests for BCE-4X VIS-007 visual balance"""

    def test_vis_007_empty_corridors_pass(self):
        """VIS-007 should PASS with empty corridors"""
        resp = requests.post(
            f"{BASE_URL}/api/bce/validate-visual-balance",
            json={"corridors": []},
            timeout=30
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert data.get("status") == "PASS", f"VIS-007 should PASS with empty corridors: {data}"
        print("PASS: BCE-4X VIS-007 passes with empty corridors")

    def test_vis_007_validates_band_limits(self):
        """VIS-007 should validate band widths and opacities within limits"""
        test_corridors = [
            {
                "properties": {
                    "bands": [
                        {"level": "gris", "width_m": 25, "fillOpacity": 0.06},
                        {"level": "jaune", "width_m": 16, "fillOpacity": 0.09},
                        {"level": "orange", "width_m": 10, "fillOpacity": 0.13},
                        {"level": "rouge", "width_m": 5, "fillOpacity": 0.30},
                        {"level": "rouge_raye", "width_m": 3, "fillOpacity": 0.45},
                    ]
                }
            }
        ]
        
        resp = requests.post(
            f"{BASE_URL}/api/bce/validate-visual-balance",
            json={"corridors": test_corridors},
            timeout=30
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert data.get("status") == "PASS", f"VIS-007 should PASS with valid bands: {data}"
        print(f"PASS: BCE-4X VIS-007 validates band limits: {data.get('total_violations', 0)} violations")


class TestColorHarmonization:
    """Tests for color harmonization between map/panel/core"""

    def test_zone_normative_colors_in_map(self):
        """BionicMicroZones.jsx should have ZONE_NORMATIVE_COLORS"""
        map_path = "/app/frontend/src/components/territoire/BionicMicroZones.jsx"
        with open(map_path, "r") as f:
            content = f.read()
        
        for layer_id, color in EXPECTED_ZONE_COLORS.items():
            # Normalize color comparison (case-insensitive)
            assert layer_id in content, f"Layer {layer_id} should be in ZONE_NORMATIVE_COLORS"
            assert color.upper() in content.upper(), f"Color {color} for {layer_id} should be in map"
        print("PASS: ZONE_NORMATIVE_COLORS in BionicMicroZones.jsx has all expected colors")

    def test_layer_types_in_panel(self):
        """BionicZoneService.js should have LAYER_TYPES with matching colors"""
        panel_path = "/app/frontend/src/services/BionicZoneService.js"
        with open(panel_path, "r") as f:
            content = f.read()
        
        for layer_id, color in EXPECTED_ZONE_COLORS.items():
            assert layer_id in content, f"Layer {layer_id} should be in LAYER_TYPES"
            assert color.upper() in content.upper(), f"Color {color} for {layer_id} should be in panel"
        print("PASS: LAYER_TYPES in BionicZoneService.js has matching colors")

    def test_bionic_modules_in_core(self):
        """bionicModules.js should have BIONIC_MODULES with matching colors"""
        core_path = "/app/frontend/src/core/bionic/bionicModules.js"
        with open(core_path, "r") as f:
            content = f.read()
        
        for layer_id, color in EXPECTED_ZONE_COLORS.items():
            assert layer_id in content, f"Module {layer_id} should be in BIONIC_MODULES"
            assert color.upper() in content.upper(), f"Color {color} for {layer_id} should be in core"
        print("PASS: BIONIC_MODULES in bionicModules.js has matching colors")


class TestBionicEngineHub:
    """Tests for BionicEngineHub showing 12 engines"""

    def test_engines_v2_status_returns_12(self):
        """GET /api/v1/bionic/engines-v2/status should return 12 engines"""
        resp = requests.get(f"{BASE_URL}/api/v1/bionic/engines-v2/status", timeout=30)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert data.get("engine_count") == 12, f"Should have 12 engines, got {data.get('engine_count')}"
        
        expected_ids = {
            "behavior", "keyzone_v2", "food_deficit", "wind_intelligence",
            "terrain", "human_pressure", "corridor_continuity", "global_attractiveness",
            "action_plan", "predictive_ai", "bce_compliance", "rendering"
        }
        # engines is a list of dicts with 'id' field
        engines_list = data.get("engines", [])
        actual_ids = set(e.get("id") for e in engines_list)
        assert expected_ids == actual_ids, f"Engine IDs mismatch. Missing: {expected_ids - actual_ids}"
        print(f"PASS: /api/v1/bionic/engines-v2/status returns 12 engines: {sorted(actual_ids)}")

    def test_engines_v2_all_active(self):
        """All 12 engines should have status='active'"""
        resp = requests.get(f"{BASE_URL}/api/v1/bionic/engines-v2/status", timeout=30)
        data = resp.json()
        
        # engines is a list of dicts
        engines_list = data.get("engines", [])
        for engine in engines_list:
            assert engine.get("status") == "active", f"Engine {engine.get('id')} should be active"
        print("PASS: All 12 engines have status='active'")


class TestCorridorContinuityPipeline:
    """Tests for corridor continuity graph-based post-processing"""

    def test_ensure_corridor_network_continuity_exists(self):
        """ensure_corridor_network_continuity function should exist"""
        corridors_v9_path = "/app/backend/modules/bionic_engine_p0/engines/corridors_v9.py"
        with open(corridors_v9_path, "r") as f:
            content = f.read()
        
        assert "def ensure_corridor_network_continuity" in content, "Function should exist"
        print("PASS: ensure_corridor_network_continuity function exists")

    def test_continuity_in_zone_engine_core_v2(self):
        """ensure_corridor_network_continuity should be called in zone_engine_core_v2.py"""
        core_path = "/app/backend/modules/bionic_engine_p0/services/zone_engine_core_v2.py"
        with open(core_path, "r") as f:
            content = f.read()
        
        assert "ensure_corridor_network_continuity" in content, "Function should be imported/called in zone_engine_core_v2.py"
        assert "corridors = ensure_corridor_network_continuity" in content, "Function should be called in pipeline"
        print("PASS: ensure_corridor_network_continuity integrated in zone_engine_core_v2.py pipeline")


class TestOrganicZonesEndpoint:
    """Tests for organic zones endpoint with corridor data"""

    def test_organic_zones_returns_corridors_with_bands(self):
        """POST /api/v1/bionic/organic-zones should return corridors with bands"""
        test_bounds = {
            "north": 46.77,
            "south": 46.74,
            "east": -70.45,
            "west": -70.50,
        }
        
        resp = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json={
                "bounds": test_bounds,
                "species": "moose",
                "layers": ["habitats", "alimentation", "corridors"],
                "resolution": 40,
                "max_zones_per_layer": 5,
            },
            timeout=60
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        corridors = data.get("corridors", [])
        print(f"PASS: /api/v1/bionic/organic-zones returns {len(corridors)} corridors")
        
        # Check corridor properties if any exist
        if corridors:
            for c in corridors[:3]:  # Check first 3
                props = c.get("properties", {})
                assert "bands" in props or "band_count" in props, "Corridor should have bands data"
            print(f"PASS: Corridors have bands property")


class TestBackendHealth:
    """Basic backend health check"""

    def test_backend_healthy(self):
        """Backend should be healthy"""
        resp = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert data.get("status") == "healthy", f"Backend should be healthy: {data}"
        print(f"PASS: Backend healthy - version {data.get('version', 'unknown')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
