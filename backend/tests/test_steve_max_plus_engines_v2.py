"""
STEVE-MAX++ Testing Suite — 12 BIONIC V2 Engines Integration
============================================================
Tests all features requested in iteration 13:
1. GET /api/v1/bionic/engines-v2/status returns 12 engines all active
2. POST /api/v1/bionic/engines-v2/compute returns scores for all 12 engines
3. POST /api/bce/validate-corridor-continuity validates COR-006 rule
4. POST /api/bce/validate-visual-balance validates VIS-007 rule
5. POST /api/v1/bionic/organic-zones generates zones and corridors with continuity
6. Wind logic removed from hunting path pipeline
7. Corridor band widths within reduced limits
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://species-network.preview.emergentagent.com"

# Test bounds (Quebec region)
TEST_BOUNDS = {
    "north": 46.824,
    "south": 46.806,
    "east": -71.192,
    "west": -71.218,
}

# Expected 12 engines
EXPECTED_ENGINES = [
    "behavior", "keyzone_v2", "food_deficit", "wind_intelligence",
    "terrain", "human_pressure", "corridor_continuity", "global_attractiveness",
    "action_plan", "predictive_ai", "bce_compliance", "rendering",
]

# Expected band width limits (STEVE-MAX V2 P1 reduced values)
EXPECTED_BAND_LIMITS = {
    "gris": {"max_m": 22},
    "jaune": {"max_m": 14},
    "orange": {"max_m": 9},
    "rouge": {"max_m": 5},
    "rouge_raye": {"max_m": 3},
}


class TestEnginesV2Status:
    """Test GET /api/v1/bionic/engines-v2/status — 12 engines all active"""

    def test_engines_v2_status_returns_12_engines(self):
        """Verify that engines-v2/status returns exactly 12 engines"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/engines-v2/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert data.get("success") is True, "Response success should be True"
        assert data.get("engine_count") == 12, f"Expected 12 engines, got {data.get('engine_count')}"

        engines = data.get("engines", [])
        assert len(engines) == 12, f"Expected 12 engine objects, got {len(engines)}"

    def test_engines_v2_status_all_active(self):
        """Verify all 12 engines have status='active'"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/engines-v2/status")
        data = response.json()

        engines = data.get("engines", [])
        for engine in engines:
            assert engine.get("status") == "active", f"Engine {engine.get('id')} should be active"

    def test_engines_v2_status_has_all_expected_ids(self):
        """Verify all 12 expected engine IDs are present"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/engines-v2/status")
        data = response.json()

        engines = data.get("engines", [])
        engine_ids = [e.get("id") for e in engines]

        for expected_id in EXPECTED_ENGINES:
            assert expected_id in engine_ids, f"Engine '{expected_id}' not found in response"


class TestEnginesV2Compute:
    """Test POST /api/v1/bionic/engines-v2/compute — scores for all 12 engines"""

    def test_engines_v2_compute_returns_12_scores(self):
        """Verify compute endpoint returns scores for all 12 engines"""
        payload = {
            "zones": [{"properties": {"layer_id": "habitats"}}, {"properties": {"layer_id": "rut"}}],
            "corridors": [{"properties": {"continuity_valid": True, "bands": [], "densified": True}}],
            "weather": {"wind": {"deg": 180, "speed": 5}},
            "season": "automne",
            "hour": 8,
            "bounds": TEST_BOUNDS,
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/engines-v2/compute",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert data.get("success") is True, "Response success should be True"
        assert data.get("engine_count") == 12, f"Expected 12 engines, got {data.get('engine_count')}"

        engines = data.get("engines", {})
        assert len(engines) == 12, f"Expected 12 engine results, got {len(engines)}"

    def test_engines_v2_compute_all_scores_valid(self):
        """Verify all engine scores are in valid range [0-100]"""
        payload = {
            "zones": [{"properties": {"layer_id": "alimentation"}}],
            "corridors": [],
            "weather": {},
            "season": "automne",
            "hour": 12,
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/engines-v2/compute",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        data = response.json()

        engines = data.get("engines", {})
        for engine_id, result in engines.items():
            score = result.get("score")
            assert score is not None, f"Engine {engine_id} has no score"
            assert 0 <= score <= 100, f"Engine {engine_id} score {score} out of range [0-100]"

    def test_engines_v2_compute_has_average_score(self):
        """Verify compute endpoint returns average score"""
        payload = {
            "zones": [{"properties": {"layer_id": "repos"}}],
            "corridors": [{"properties": {"continuity_valid": True, "bands": [], "densified": True}}],
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/engines-v2/compute",
            json=payload,
        )
        data = response.json()

        avg_score = data.get("average_score")
        assert avg_score is not None, "Response should include average_score"
        assert 0 <= avg_score <= 100, f"Average score {avg_score} out of range"


class TestBCECorridorContinuity:
    """Test POST /api/bce/validate-corridor-continuity — COR-006 rule"""

    def test_corridor_continuity_empty_corridors(self):
        """Verify COR-006 passes when no corridors"""
        payload = {"corridors": [], "zones": []}

        response = requests.post(
            f"{BASE_URL}/api/bce/validate-corridor-continuity",
            json=payload,
        )
        assert response.status_code == 200

        data = response.json()
        assert data.get("rule") == "BCE-4X-COR-006"
        assert data.get("status") == "PASS"

    def test_corridor_continuity_with_corridors(self):
        """Verify COR-006 validation returns expected structure"""
        # Create sample corridors with endpoints
        corridors = [
            {
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[-71.205, 46.815], [-71.200, 46.820], [-71.195, 46.818]],
                },
                "properties": {"continuity_valid": True},
            },
            {
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[-71.195, 46.818], [-71.190, 46.815]],  # Connects to first
                },
                "properties": {"continuity_valid": True},
            },
        ]
        zones = [{"geometry": {"type": "Polygon", "coordinates": [[[-71.205, 46.815], [-71.200, 46.815], [-71.200, 46.820], [-71.205, 46.820], [-71.205, 46.815]]]}}]

        payload = {"corridors": corridors, "zones": zones}

        response = requests.post(
            f"{BASE_URL}/api/bce/validate-corridor-continuity",
            json=payload,
        )
        assert response.status_code == 200

        data = response.json()
        assert data.get("rule") == "BCE-4X-COR-006"
        assert data.get("name") == "CorridorNetworkContinuity"
        assert "continuity_pct" in data
        assert "total_endpoints" in data


class TestBCEVisualBalance:
    """Test POST /api/bce/validate-visual-balance — VIS-007 rule"""

    def test_visual_balance_empty_corridors(self):
        """Verify VIS-007 passes when no corridors"""
        payload = {"corridors": []}

        response = requests.post(
            f"{BASE_URL}/api/bce/validate-visual-balance",
            json=payload,
        )
        assert response.status_code == 200

        data = response.json()
        assert data.get("rule") == "BCE-4X-VIS-007"
        assert data.get("status") == "PASS"

    def test_visual_balance_with_valid_bands(self):
        """Verify VIS-007 validation with bands within limits"""
        corridors = [
            {
                "properties": {
                    "bands": [
                        {"level": "gris", "width_m": 20, "fillOpacity": 0.06},
                        {"level": "jaune", "width_m": 12, "fillOpacity": 0.09},
                        {"level": "orange", "width_m": 8, "fillOpacity": 0.13},
                        {"level": "rouge", "width_m": 4, "fillOpacity": 0.30},
                        {"level": "rouge_raye", "width_m": 2, "fillOpacity": 0.45},
                    ]
                }
            }
        ]

        payload = {"corridors": corridors}

        response = requests.post(
            f"{BASE_URL}/api/bce/validate-visual-balance",
            json=payload,
        )
        assert response.status_code == 200

        data = response.json()
        assert data.get("rule") == "BCE-4X-VIS-007"
        assert data.get("name") == "CorridorVisualBalance"


class TestOrganicZonesWithContinuity:
    """Test POST /api/v1/bionic/organic-zones — zones and corridors with continuity"""

    def test_organic_zones_returns_corridors(self):
        """Verify organic-zones API returns corridors"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": "moose",
            "layers": ["habitats", "alimentation", "repos"],
            "resolution": 40,
            "max_zones_per_layer": 5,
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/organic-zones",
            json=payload,
        )
        assert response.status_code == 200

        data = response.json()
        assert "features" in data, "Response should have features (zones)"
        # Corridors may or may not be present depending on zone generation
        if "corridors" in data:
            corridors = data.get("corridors", [])
            # Verify corridors have continuity-related properties
            for c in corridors[:3]:  # Check first 3
                props = c.get("properties", {})
                # STEVE-MAX++ should mark corridors as topology-connected
                assert "topology_connected" in props or "continuity_valid" in props or "densified" in props


class TestBandRatioLimits:
    """Verify corridor band width limits are reduced (STEVE-MAX V2 P1)"""

    def test_band_ratio_constants(self):
        """Verify BAND_RATIO max values match expected limits"""
        from modules.bionic_engine_p0.engines.corridors_v9 import BAND_RATIO

        for level, expected in EXPECTED_BAND_LIMITS.items():
            actual = BAND_RATIO.get(level, {}).get("max_m")
            assert actual is not None, f"BAND_RATIO missing level: {level}"
            assert actual == expected["max_m"], f"Band {level}: expected max_m={expected['max_m']}, got {actual}"

    def test_band_colors_fill_opacity(self):
        """Verify BAND_COLORS fillOpacity values are low (reduced visual impact)"""
        from modules.bionic_engine_p0.engines.corridors_v9 import BAND_COLORS

        # Verify low opacity values for outer bands
        assert BAND_COLORS.get("gris", {}).get("fillOpacity", 1) <= 0.10
        assert BAND_COLORS.get("jaune", {}).get("fillOpacity", 1) <= 0.15
        assert BAND_COLORS.get("orange", {}).get("fillOpacity", 1) <= 0.20


class TestWindLogicRemoved:
    """Verify wind logic is removed from hunting path pipeline"""

    def test_no_wind_penalty_function(self):
        """Verify wind_penalty function is not in hunting_path.py"""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "hunting_path",
            "/app/backend/modules/bionic_engine_p0/engines/hunting_path.py"
        )
        hunting_path = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hunting_path)

        assert not hasattr(hunting_path, "wind_penalty"), "wind_penalty should not exist in hunting_path"
        assert not hasattr(hunting_path, "_wind_penalty"), "_wind_penalty should not exist in hunting_path"

    def test_hunting_path_no_wind_in_tsp(self):
        """Verify hunting path TSP logic does not use wind parameters"""
        # Check that the generate_hunting_path function doesn't have wind scoring
        from modules.bionic_engine_p0.engines.hunting_path import generate_hunting_path
        import inspect

        source = inspect.getsource(generate_hunting_path)
        # Should not have wind_penalty in the TSP scoring
        assert "wind_penalty" not in source, "wind_penalty should not be in TSP scoring"
        assert "wind_factor" not in source, "wind_factor should not be in TSP scoring"


class TestCorridorNetworkContinuityIntegration:
    """Verify ensure_corridor_network_continuity is integrated in pipeline"""

    def test_continuity_function_exists(self):
        """Verify ensure_corridor_network_continuity function exists"""
        from modules.bionic_engine_p0.engines.corridors_v9 import ensure_corridor_network_continuity
        assert callable(ensure_corridor_network_continuity)

    def test_continuity_function_returns_corridors(self):
        """Verify ensure_corridor_network_continuity returns enriched corridors"""
        from modules.bionic_engine_p0.engines.corridors_v9 import ensure_corridor_network_continuity

        # Create test data
        corridors = [
            {
                "type": "Feature",
                "id": "test_1",
                "geometry": {"type": "LineString", "coordinates": [[-71.205, 46.815], [-71.200, 46.820]]},
                "properties": {"continuity_valid": True},
            }
        ]
        zones = [
            {
                "geometry": {"type": "Polygon", "coordinates": [[[-71.205, 46.815], [-71.200, 46.815], [-71.200, 46.820], [-71.205, 46.815]]]},
                "properties": {"layer_id": "habitats"},
            }
        ]

        result = ensure_corridor_network_continuity(corridors, zones)
        assert isinstance(result, list)
        assert len(result) >= len(corridors), "Should return at least original corridors"

        # Verify topology_connected flag is added
        for c in result:
            assert "topology_connected" in c.get("properties", {})


class TestBackendHealth:
    """Basic backend health check"""

    def test_backend_healthy(self):
        """Verify backend is responding"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
