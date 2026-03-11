"""
TEST API — Pipeline Full Analysis & Metrics Endpoints
BIONIC V5 ULTIME 300% — PHASE G

Tests:
- GET /api/v1/bionic/pipeline/status
- POST /api/v1/bionic/pipeline/full-analysis (5 species x 3 territories)
- POST /api/v1/bionic/pipeline/metrics (multi-species)
- Validation: source_ids, module_stats, module_timings, corridor_analyses
- Non-regression: TFE + BMPE endpoints

Uses resolution=30 for faster tests.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

SPECIES_LIST = ["moose", "deer", "bear", "wild_turkey", "elk"]

TERRITORIES = {
    "laurentides": {"north": 46.95, "south": 46.85, "east": -74.00, "west": -74.15},
    "gatineau": {"north": 45.55, "south": 45.45, "east": -75.70, "west": -75.85},
    "charlevoix": {"north": 47.60, "south": 47.50, "east": -70.50, "west": -70.65},
}

MODULE_ORDER = ["SSE", "OSG", "CME", "WSE_WIV", "VFE", "SSVL", "TCVE", "PME", "BMPE", "TFE"]
SOURCE_ID_KEYS = ["sse", "osg", "cme", "wse", "vfe", "ssvl", "tcve", "pme", "bmpe", "tfe"]


class TestPipelineStatus:
    """GET /api/v1/bionic/pipeline/status"""

    def test_status_returns_200(self):
        """Pipeline status endpoint returns 200"""
        r = requests.get(f"{BASE_URL}/api/v1/bionic/pipeline/status", timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"

    def test_status_pipeline_info(self):
        """Pipeline status returns correct pipeline info"""
        r = requests.get(f"{BASE_URL}/api/v1/bionic/pipeline/status", timeout=10)
        data = r.json()
        
        assert data["pipeline"] == "BIONIC_V5_ULTIME_300"
        assert data["label"] == "Full Pipeline Orchestrator"
        assert data["version"] == "1.0.0"
        assert data["status"] == "active"
        assert data["module_count"] == 10

    def test_status_pipeline_order(self):
        """Pipeline status returns correct module order"""
        r = requests.get(f"{BASE_URL}/api/v1/bionic/pipeline/status", timeout=10)
        data = r.json()
        
        assert data["pipeline_order"] == MODULE_ORDER

    def test_status_species_supported(self):
        """Pipeline status returns all 5 supported species"""
        r = requests.get(f"{BASE_URL}/api/v1/bionic/pipeline/status", timeout=10)
        data = r.json()
        
        assert sorted(data["species_supported"]) == sorted(SPECIES_LIST)

    def test_status_endpoints_list(self):
        """Pipeline status lists all 3 endpoints"""
        r = requests.get(f"{BASE_URL}/api/v1/bionic/pipeline/status", timeout=10)
        data = r.json()
        
        expected_endpoints = [
            "POST /api/v1/bionic/pipeline/full-analysis",
            "POST /api/v1/bionic/pipeline/metrics",
            "GET /api/v1/bionic/pipeline/status",
        ]
        for ep in expected_endpoints:
            assert ep in data["endpoints"], f"Missing endpoint: {ep}"

    def test_status_conformity_flags(self):
        """Pipeline status returns conformity flags"""
        r = requests.get(f"{BASE_URL}/api/v1/bionic/pipeline/status", timeout=10)
        data = r.json()
        
        assert data["conformity"]["zero_transversality"] is True
        assert data["conformity"]["zero_duplication"] is True
        assert data["conformity"]["strict_sequential_order"] is True
        assert data["conformity"]["backend_truth"] is True


class TestFullAnalysis:
    """POST /api/v1/bionic/pipeline/full-analysis — 5 species x 3 territories"""

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_full_analysis_returns_200(self, species):
        """Full analysis returns 200 for each species"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": species,
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/full-analysis", json=payload, timeout=60)
        assert r.status_code == 200, f"Species {species}: Expected 200, got {r.status_code}: {r.text}"

    @pytest.mark.parametrize("territory", TERRITORIES.keys())
    def test_full_analysis_all_territories(self, territory):
        """Full analysis works for all 3 territories"""
        payload = {
            "bounds": TERRITORIES[territory],
            "species": "moose",
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/full-analysis", json=payload, timeout=60)
        assert r.status_code == 200, f"Territory {territory}: Expected 200, got {r.status_code}"
        data = r.json()
        assert data["bounds"] == TERRITORIES[territory]

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_full_analysis_10_source_ids(self, species):
        """Full analysis returns 10 dynamic source_ids"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": species,
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/full-analysis", json=payload, timeout=60)
        data = r.json()
        
        source_ids = data["pipeline_source_ids"]
        assert len(source_ids) == 10, f"Expected 10 source_ids, got {len(source_ids)}"
        
        for key in SOURCE_ID_KEYS:
            assert key in source_ids, f"Missing source_id key: {key}"
            assert species.upper() in source_ids[key], f"source_id {key} missing species: {source_ids[key]}"

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_full_analysis_module_stats_10_modules(self, species):
        """Full analysis returns module_stats for all 10 modules"""
        payload = {
            "bounds": TERRITORIES["gatineau"],
            "species": species,
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/full-analysis", json=payload, timeout=60)
        data = r.json()
        
        module_stats = data["module_stats"]
        for mod in MODULE_ORDER:
            assert mod in module_stats, f"Module stats missing for: {mod}"

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_full_analysis_module_timings_10_modules(self, species):
        """Full analysis returns module_timings_ms for all 10 modules"""
        payload = {
            "bounds": TERRITORIES["charlevoix"],
            "species": species,
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/full-analysis", json=payload, timeout=60)
        data = r.json()
        
        timings = data["module_timings_ms"]
        for mod in MODULE_ORDER:
            assert mod in timings, f"Module timings missing for: {mod}"
            assert timings[mod] >= 0, f"Invalid timing for {mod}: {timings[mod]}"

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_full_analysis_corridor_analyses(self, species):
        """Full analysis returns corridor_analyses for PME, BMPE, TFE"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": species,
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/full-analysis", json=payload, timeout=60)
        data = r.json()
        
        ca = data["corridor_analyses"]
        assert "pme_pressure" in ca, "Missing pme_pressure in corridor_analyses"
        assert "bmpe_micro_patterns" in ca, "Missing bmpe_micro_patterns in corridor_analyses"
        assert "tfe_thermal" in ca, "Missing tfe_thermal in corridor_analyses"

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_full_analysis_validation_flags(self, species):
        """Full analysis validation: all_modules_executed=true, zero_transversality=true, zero_duplication=true"""
        payload = {
            "bounds": TERRITORIES["gatineau"],
            "species": species,
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/full-analysis", json=payload, timeout=60)
        data = r.json()
        
        v = data["validation"]
        assert v["all_modules_executed"] is True, "all_modules_executed should be True"
        assert v["zero_transversality"] is True, "zero_transversality should be True"
        assert v["zero_duplication"] is True, "zero_duplication should be True"
        assert v["source_ids_dynamic"] is True, "source_ids_dynamic should be True"
        assert v["pipeline_order"] == "SSE->OSG->CME->WSE->VFE->SSVL->TCVE->PME->BMPE->TFE"

    def test_full_analysis_invalid_species_returns_400(self):
        """Full analysis with invalid species returns 400"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": "invalid_species",
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/full-analysis", json=payload, timeout=60)
        assert r.status_code == 400, f"Expected 400 for invalid species, got {r.status_code}"

    def test_full_analysis_module_count_10(self):
        """Full analysis returns module_count=10"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": "moose",
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/full-analysis", json=payload, timeout=60)
        data = r.json()
        
        assert data["module_count"] == 10, f"Expected module_count=10, got {data['module_count']}"

    def test_full_analysis_pipeline_identifier(self):
        """Full analysis returns BIONIC_V5_ULTIME_300 pipeline identifier"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": "moose",
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/full-analysis", json=payload, timeout=60)
        data = r.json()
        
        assert data["pipeline"] == "BIONIC_V5_ULTIME_300"


class TestPipelineMetrics:
    """POST /api/v1/bionic/pipeline/metrics — multi-species"""

    def test_metrics_all_5_species(self):
        """Metrics endpoint works for all 5 species"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": SPECIES_LIST,
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/metrics", json=payload, timeout=120)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        
        data = r.json()
        assert data["species_count"] == 5

    def test_metrics_species_results_structure(self):
        """Metrics returns species_results for each species"""
        payload = {
            "bounds": TERRITORIES["gatineau"],
            "species": SPECIES_LIST,
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/metrics", json=payload, timeout=120)
        data = r.json()
        
        for sp in SPECIES_LIST:
            assert sp in data["species_results"], f"Missing species_results for: {sp}"
            result = data["species_results"][sp]
            assert "source_ids" in result
            assert "module_stats" in result
            assert "module_timings_ms" in result
            assert "total_ms" in result
            assert "corridor_count" in result

    def test_metrics_subset_species(self):
        """Metrics works for a subset of species"""
        payload = {
            "bounds": TERRITORIES["charlevoix"],
            "species": ["moose", "bear"],
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/metrics", json=payload, timeout=120)
        data = r.json()
        
        assert data["species_count"] == 2
        assert "moose" in data["species_results"]
        assert "bear" in data["species_results"]

    def test_metrics_validation(self):
        """Metrics returns validation flags"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": ["moose"],
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/metrics", json=payload, timeout=120)
        data = r.json()
        
        assert data["validation"]["all_species_processed"] is True
        assert data["validation"]["pipeline_order"] == "SSE->OSG->CME->WSE->VFE->SSVL->TCVE->PME->BMPE->TFE"

    def test_metrics_pipeline_identifier(self):
        """Metrics returns BIONIC_V5_ULTIME_300 pipeline identifier"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": ["moose"],
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/metrics", json=payload, timeout=120)
        data = r.json()
        
        assert data["pipeline"] == "BIONIC_V5_ULTIME_300"

    def test_metrics_invalid_species_returns_400(self):
        """Metrics with invalid species returns 400"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": ["moose", "invalid_species"],
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/metrics", json=payload, timeout=120)
        assert r.status_code == 400, f"Expected 400 for invalid species, got {r.status_code}"

    def test_metrics_total_computation_time(self):
        """Metrics returns total_computation_time_ms"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": ["moose", "deer"],
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/pipeline/metrics", json=payload, timeout=120)
        data = r.json()
        
        assert "total_computation_time_ms" in data
        assert data["total_computation_time_ms"] > 0


class TestNonRegression:
    """Non-régression: TFE + BMPE endpoints"""

    def test_tfe_status_working(self):
        """TFE status endpoint still works"""
        r = requests.get(f"{BASE_URL}/api/v1/bionic/tfe/status", timeout=10)
        assert r.status_code == 200

    def test_tfe_analyze_working(self):
        """TFE analyze endpoint still works"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": "moose",
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/tfe/analyze", json=payload, timeout=60)
        assert r.status_code == 200
        data = r.json()
        assert data["source_id"] == "TFE_MOOSE"

    def test_bmpe_status_working(self):
        """BMPE status endpoint still works"""
        r = requests.get(f"{BASE_URL}/api/v1/bionic/bmpe/status", timeout=10)
        assert r.status_code == 200

    def test_bmpe_analyze_working(self):
        """BMPE analyze endpoint still works"""
        payload = {
            "bounds": TERRITORIES["laurentides"],
            "species": "moose",
            "resolution": 30,
        }
        r = requests.post(f"{BASE_URL}/api/v1/bionic/bmpe/analyze", json=payload, timeout=60)
        assert r.status_code == 200
        data = r.json()
        assert data["source_id"] == "BMPE_MOOSE"
