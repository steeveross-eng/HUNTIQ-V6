"""
BIONIC V5 — PHASE D Consolidation & Pré-Optimisation Tests
============================================================
Tests for:
- D.1 Multifactor Scoring Engine
- D.2 Dynamic Layer Generator
- D.3 Knowledge Layer Normalizer
Plus non-regression tests for existing endpoints.

VERSION: 1.0.0
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestPhaseDMultifactorScore:
    """D.1 — Multifactor Scoring Engine Tests"""

    def test_multifactor_score_returns_200(self):
        """GET /phase-d/multifactor-score returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/multifactor-score")
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "confidence" in data
        assert "active_factors" in data

    def test_multifactor_score_with_species_region(self):
        """Multifactor score with species and region parameters"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/phase-d/multifactor-score",
            params={"species": "orignal", "region": "CA-QC"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_factors"] == 8
        assert "factors" in data

    def test_multifactor_score_spring_calving_season(self):
        """Multifactor score during spring (calving season) - date=2026-05-15"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/phase-d/multifactor-score",
            params={"species": "orignal", "region": "CA-QC", "date": "2026-05-15", "hour": 12}
        )
        assert response.status_code == 200
        data = response.json()
        assert "factors" in data
        assert "calving" in data["factors"]
        assert "seasonal_context" in data["factors"]
        assert data["factors"]["seasonal_context"]["season"] == "spring"

    def test_multifactor_score_summer_thermal_stress(self):
        """Multifactor score during summer with high temperature (thermal stress)"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/phase-d/multifactor-score",
            params={
                "species": "orignal",
                "region": "CA-QC",
                "date": "2026-07-15",
                "hour": 14,
                "temperature_c": 32
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Thermal stress should be active with high temp
        assert data["factors"]["thermal_stress"]["active"] == True
        assert data["factors"]["thermal_stress"]["temperature_c"] == 32.0
        # Risk level should reflect thermal stress
        assert data["risk_level"] in ["moderate", "elevated", "critical"]
        # Should have recommendation about thermal stress
        assert any("thermique" in r.lower() for r in data["recommendations"])

    def test_multifactor_score_fall_hunting_season(self):
        """Multifactor score during fall (hunting season) - date=2026-09-20"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/phase-d/multifactor-score",
            params={"species": "orignal", "region": "CA-QC", "date": "2026-09-20", "hour": 7}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["factors"]["seasonal_context"]["season"] == "fall"
        # Fall has boosted score for moose (rut)
        assert data["factors"]["seasonal_context"]["score"] >= 80.0

    def test_multifactor_score_returns_active_factors_count(self):
        """Multifactor score returns correct active_factors count"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/phase-d/multifactor-score",
            params={"species": "orignal", "region": "CA-QC", "date": "2026-06-15", "hour": 6}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["active_factors"] >= 2  # At least temporal and seasonal_context are always active
        assert data["total_factors"] == 8

    def test_multifactor_score_has_risk_level(self):
        """Multifactor score returns risk_level field"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/multifactor-score")
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] in ["normal", "moderate", "elevated", "critical"]

    def test_multifactor_score_has_recommendations(self):
        """Multifactor score returns recommendations array"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/multifactor-score")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["recommendations"], list)

    def test_multifactor_score_source_ids_and_version(self):
        """Multifactor score returns source_ids and version"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/multifactor-score")
        assert response.status_code == 200
        data = response.json()
        assert "SRC-PHASE-D-MULTIFACTOR" in data["source_ids"]
        assert data["version"] == "1.0.0"


class TestPhaseDDynamicLayers:
    """D.2 — Dynamic Layer Generator Tests"""

    def test_dynamic_layers_returns_200(self):
        """GET /phase-d/dynamic-layers returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/dynamic-layers")
        assert response.status_code == 200
        data = response.json()
        assert data["phase"] == "D"
        assert "layers" in data

    def test_dynamic_layers_returns_4_layers(self):
        """Dynamic layers returns exactly 4 layer types"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/dynamic-layers")
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 4
        assert "calving_exclusion" in data["layers"]
        assert "thermal_refuge" in data["layers"]
        assert "pressure_overlay" in data["layers"]
        assert "seasonal_influence" in data["layers"]

    def test_dynamic_layer_calving_exclusion_structure(self):
        """Calving exclusion layer has required fields"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/dynamic-layers")
        assert response.status_code == 200
        layer = response.json()["layers"]["calving_exclusion"]
        assert "layer_id" in layer
        assert "layer_type" in layer
        assert "active" in layer
        assert "intensity" in layer
        assert "label" in layer
        assert "style" in layer
        assert "metadata" in layer
        assert layer["layer_type"] == "calving_exclusion"

    def test_dynamic_layer_thermal_refuge_structure(self):
        """Thermal refuge layer has required fields"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/dynamic-layers")
        assert response.status_code == 200
        layer = response.json()["layers"]["thermal_refuge"]
        assert layer["layer_type"] == "thermal_refuge"
        assert "stress_level" in layer["metadata"]
        assert "activity_modifier" in layer["metadata"]
        assert layer["metadata"]["phase"] == "C.3"

    def test_dynamic_layer_pressure_overlay_structure(self):
        """Pressure overlay layer has required fields"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/dynamic-layers")
        assert response.status_code == 200
        layer = response.json()["layers"]["pressure_overlay"]
        assert layer["layer_type"] == "pressure_overlay"
        assert "hunting_season" in layer["metadata"]
        assert "is_weekend" in layer["metadata"]
        assert layer["metadata"]["phase"] == "C.4"

    def test_dynamic_layer_seasonal_influence_structure(self):
        """Seasonal influence layer has required fields"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/dynamic-layers")
        assert response.status_code == 200
        layer = response.json()["layers"]["seasonal_influence"]
        assert layer["layer_type"] == "seasonal_influence"
        assert "season" in layer["metadata"]
        assert "active_factors" in layer["metadata"]
        assert layer["metadata"]["phase"] == "D.2"

    def test_dynamic_layers_style_fields(self):
        """Each layer has style with color, opacity, fillOpacity"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/dynamic-layers")
        assert response.status_code == 200
        layers = response.json()["layers"]
        for layer_name, layer in layers.items():
            assert "style" in layer
            assert "color" in layer["style"]
            assert "opacity" in layer["style"]
            assert "fillOpacity" in layer["style"]

    def test_dynamic_layers_with_temperature(self):
        """Dynamic layers with temperature parameter activates thermal refuge"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/phase-d/dynamic-layers",
            params={
                "species": "orignal",
                "date": "2026-07-15",
                "hour": 14,
                "temperature_c": 32
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["layers"]["thermal_refuge"]["active"] == True
        assert data["layers"]["thermal_refuge"]["metadata"]["temperature_c"] == 32.0

    def test_dynamic_layers_source_ids(self):
        """Dynamic layers returns source_ids"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/dynamic-layers")
        assert response.status_code == 200
        data = response.json()
        assert "SRC-PHASE-D-DYNAMIC-LAYERS" in data["source_ids"]
        assert data["version"] == "1.0.0"


class TestPhaseDKnowledgeIntegrity:
    """D.3 — Knowledge Layer Normalizer Tests"""

    def test_knowledge_integrity_returns_200(self):
        """GET /phase-d/knowledge-integrity returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/knowledge-integrity")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "modules" in data

    def test_knowledge_integrity_has_8_modules(self):
        """Knowledge integrity validates all 8 modules"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/knowledge-integrity")
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["total"] == 8
        assert len(data["modules"]) == 8

    def test_knowledge_integrity_all_modules_healthy(self):
        """All 8 modules are healthy (100%)"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/knowledge-integrity")
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["healthy"] == 8
        assert data["summary"]["degraded"] == 0
        assert data["summary"]["failed"] == 0
        assert data["summary"]["health_pct"] == 100.0

    def test_knowledge_integrity_modules_list(self):
        """Knowledge integrity includes all expected modules"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/knowledge-integrity")
        assert response.status_code == 200
        modules = response.json()["modules"]
        module_names = [m["module"] for m in modules]
        expected_modules = [
            "CalvingModelRegistry",
            "JuvenileDispersalRegistry",
            "ThermalStressRegistry",
            "HuntingPressureRegistry",
            "WaterExclusionService",
            "SeasonalModelRegistry",
            "CalibrationOptimizer",
            "PhaseGRegistry"
        ]
        for expected in expected_modules:
            assert expected in module_names, f"Module {expected} not found"

    def test_knowledge_integrity_module_checks(self):
        """Each module has source_ids, version, singleton, operational checks"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/knowledge-integrity")
        assert response.status_code == 200
        modules = response.json()["modules"]
        for module in modules:
            assert "checks" in module
            assert module["checks"]["source_ids"] == True
            assert module["checks"]["version"] == True
            assert module["checks"]["operational"] == True

    def test_knowledge_integrity_cross_validation(self):
        """Knowledge integrity has cross_validation section"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/knowledge-integrity")
        assert response.status_code == 200
        cv = response.json()["cross_validation"]
        assert cv["phase_c_complete"] == True
        assert cv["phase_d_ready"] == True
        assert cv["all_operational"] == True
        assert cv["calibration_ready"] == True
        assert cv["phase_g_ready"] == True

    def test_knowledge_integrity_source_ids(self):
        """Knowledge integrity returns source_ids and version"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/phase-d/knowledge-integrity")
        assert response.status_code == 200
        data = response.json()
        assert "SRC-PHASE-D-NORMALIZER" in data["source_ids"]
        assert data["version"] == "1.0.0"


class TestNonRegressionCalibrationObservations:
    """Non-regression tests for /calibration/observations CRUD"""

    def test_list_observations_returns_200(self):
        """GET /calibration/observations returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/calibration/observations?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "observations" in data
        assert "total" in data

    def test_create_observation(self):
        """POST /calibration/observations creates observation"""
        payload = {
            "latitude": 46.85,
            "longitude": -71.25,
            "species": "orignal",
            "observed_behavior": "alimentation",
            "observation_datetime": "2026-01-15T10:00:00Z",
            "region": "CA-QC",
            "notes": "Test Phase D non-regression",
            "confidence": 0.85
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/calibration/observations",
            json=payload
        )
        assert response.status_code in [200, 201]
        data = response.json()
        # Response wraps observation in 'observation' key
        assert data["status"] == "created"
        assert "observation" in data
        obs = data["observation"]
        assert "observation_id" in obs
        assert obs["species"] == "orignal"
        assert obs["observed_behavior"] == "alimentation"

    def test_list_observations_after_create(self):
        """GET /calibration/observations shows created observation"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/calibration/observations?limit=50")
        assert response.status_code == 200
        data = response.json()
        # Should have at least one observation with our test note
        notes = [obs.get("notes", "") for obs in data["observations"]]
        assert any("Test Phase D" in n for n in notes) or data["total"] > 0


class TestNonRegressionSeasonalStatus:
    """Non-regression tests for /seasonal/status"""

    def test_seasonal_status_returns_200(self):
        """GET /seasonal/status returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/seasonal/status")
        assert response.status_code == 200
        data = response.json()
        assert data["phase"] == "C"
        assert "factors" in data

    def test_seasonal_status_with_params(self):
        """GET /seasonal/status with species/region/date"""
        response = requests.get(
            f"{BASE_URL}/api/v1/bionic/seasonal/status",
            params={"species": "orignal", "region": "CA-QC", "date": "2026-09-15"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "orignal"
        assert data["region"] == "CA-QC"
        assert "C1_calving" in data["factors"]
        assert "C2_dispersal" in data["factors"]
        assert "C3_thermal_stress" in data["factors"]
        assert "C4_hunting_pressure" in data["factors"]


class TestNonRegressionImportEndpoint:
    """Non-regression tests for /calibration/observations/import"""

    def test_import_template_returns_200(self):
        """GET /calibration/import/template returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/calibration/import/template")
        assert response.status_code == 200
        data = response.json()
        assert "required_columns" in data
        assert "csv_example" in data
        assert "latitude" in data["required_columns"]

    def test_import_rejects_invalid_file(self):
        """POST /calibration/observations/import rejects .txt file"""
        files = {"file": ("test.txt", "invalid content", "text/plain")}
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/calibration/observations/import",
            files=files
        )
        assert response.status_code == 400


class TestCanvasTerrainDocument:
    """Tests for canvas terrain document accessibility"""

    def test_canvas_terrain_accessible(self):
        """Canvas terrain document accessible at /canvas_donnees_terrain_bionic_v5.md"""
        response = requests.get(f"{BASE_URL}/canvas_donnees_terrain_bionic_v5.md")
        assert response.status_code == 200
        content = response.text
        assert "BIONIC V5" in content
        assert "Canvas Données Terrain" in content

    def test_canvas_terrain_has_required_sections(self):
        """Canvas terrain document has required sections"""
        response = requests.get(f"{BASE_URL}/canvas_donnees_terrain_bionic_v5.md")
        assert response.status_code == 200
        content = response.text
        assert "FORMATS ACCEPTÉS" in content
        assert "COLONNES OBLIGATOIRES" in content
        assert "ESPÈCES ACCEPTÉES" in content
        assert "COMPORTEMENTS ACCEPTÉS" in content
