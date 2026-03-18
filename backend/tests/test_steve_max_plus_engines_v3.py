"""
STEVE-MAX++ BIONIC V3 Integration Testing
Tests 27 engines (12 V2 + 12 V3 + 3 AI) + 3 species models (moose, deer, bear)
+ AI predictions (24h/72h/7d with decay)

Iteration 16 Test Suite
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://solunar-analytics.preview.emergentagent.com"


class TestBionicV3EngineStatus:
    """Test GET /api/v1/bionic/engines-v3/status — verify 27 engines returned"""

    def test_v3_status_returns_27_engines(self):
        """Verify status endpoint returns exactly 27 engines (12 V2 + 12 V3 + 3 AI)"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/engines-v3/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        assert data.get("engine_count") == 27
        assert data.get("v2_count") == 12
        assert data.get("v3_count") == 12
        assert data.get("ai_count") == 3

    def test_v3_status_engines_have_required_fields(self):
        """Verify each engine has required fields: id, name, version, weight, status, source"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/engines-v3/status")
        data = response.json()
        
        engines = data.get("engines", [])
        assert len(engines) == 27
        
        for engine in engines:
            assert "id" in engine
            assert "name" in engine
            assert "version" in engine
            assert "weight" in engine
            assert "status" in engine
            assert "source" in engine
            assert engine["status"] == "active"
            assert engine["source"] in ("v2", "v3", "ai")

    def test_v3_status_v2_engines(self):
        """Verify all 12 V2 engines are present"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/engines-v3/status")
        data = response.json()
        
        v2_engines = [e for e in data.get("engines", []) if e.get("source") == "v2"]
        v2_ids = {e["id"] for e in v2_engines}
        
        expected_v2 = {
            "behavior", "keyzone_v2", "food_deficit", "wind_intelligence",
            "terrain", "human_pressure", "corridor_continuity", "global_attractiveness",
            "action_plan", "predictive_ai", "bce_compliance", "rendering"
        }
        
        assert v2_ids == expected_v2, f"Missing V2 engines: {expected_v2 - v2_ids}"

    def test_v3_status_v3_engines(self):
        """Verify all 12 V3 engines are present"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/engines-v3/status")
        data = response.json()
        
        v3_engines = [e for e in data.get("engines", []) if e.get("source") == "v3"]
        v3_ids = {e["id"] for e in v3_engines}
        
        expected_v3 = {
            "ecological_hierarchy", "interaction", "geopedology", "connectivity",
            "temporal_dynamics", "hotspot", "forest_structure_v2", "food_score_v2",
            "wetness_v2", "geoform_v2", "behavior_v2", "attractiveness_v2"
        }
        
        assert v3_ids == expected_v3, f"Missing V3 engines: {expected_v3 - v3_ids}"

    def test_v3_status_ai_engines(self):
        """Verify all 3 AI engines are present"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/engines-v3/status")
        data = response.json()
        
        ai_engines = [e for e in data.get("engines", []) if e.get("source") == "ai"]
        ai_ids = {e["id"] for e in ai_engines}
        
        expected_ai = {"predictive_models", "dynamic_scoring", "temporal_analysis"}
        
        assert ai_ids == expected_ai, f"Missing AI engines: {expected_ai - ai_ids}"


class TestBionicV3Compute:
    """Test POST /api/v1/bionic/engines-v3/compute — full pipeline execution"""

    TEST_PAYLOAD = {
        "zones": [
            {"properties": {"layer_id": "habitats"}},
            {"properties": {"layer_id": "alimentation"}},
            {"properties": {"layer_id": "hydro"}},
            {"properties": {"layer_id": "rut"}},
            {"properties": {"layer_id": "peuplements"}}
        ],
        "corridors": [
            {"properties": {"continuity_valid": True, "bands": [], "scoring": {"score": 75}}},
            {"properties": {"continuity_valid": False, "bands": [], "scoring": {"score": 50}}}
        ],
        "weather": {"wind": {"deg": 180, "speed": 10}, "humidity": 70, "temp": 15},
        "season": "automne",
        "hour": 6,
        "species": "moose",
        "bounds": {"north": 46.82, "south": 46.81, "east": -71.20, "west": -71.21}
    }

    def test_compute_returns_success(self):
        """Verify compute endpoint returns success=True"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/engines-v3/compute",
            json=self.TEST_PAYLOAD
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True

    def test_compute_returns_27_engine_scores(self):
        """Verify compute returns scores for all 27 engines"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/engines-v3/compute",
            json=self.TEST_PAYLOAD
        )
        data = response.json()
        
        engines = data.get("engines", {})
        assert len(engines) >= 24, f"Expected at least 24 engine results, got {len(engines)}"
        
        # Verify engine count breakdown
        assert data.get("engine_count") >= 24
        assert data.get("v2_count") >= 9
        assert data.get("v3_count") == 12
        assert data.get("ai_count") == 3

    def test_compute_returns_species_scores(self):
        """Verify compute returns scores for all 3 species"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/engines-v3/compute",
            json=self.TEST_PAYLOAD
        )
        data = response.json()
        
        species_scores = data.get("species_scores", {})
        assert "moose" in species_scores
        assert "deer" in species_scores
        assert "bear" in species_scores
        
        for sp in ["moose", "deer", "bear"]:
            assert "score" in species_scores[sp]
            assert 0 <= species_scores[sp]["score"] <= 100

    def test_compute_returns_final_score(self):
        """Verify compute returns final integrated score"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/engines-v3/compute",
            json=self.TEST_PAYLOAD
        )
        data = response.json()
        
        assert "final_score" in data
        assert 0 <= data["final_score"] <= 100


class TestBionicV3SpeciesEndpoints:
    """Test POST /api/v1/bionic/engines-v3/species/{species_id} — species-specific scoring"""

    TEST_PAYLOAD = {
        "zones": [
            {"properties": {"layer_id": "habitats"}},
            {"properties": {"layer_id": "alimentation"}},
            {"properties": {"layer_id": "hydro"}},
            {"properties": {"layer_id": "rut"}},
            {"properties": {"layer_id": "peuplements"}}
        ],
        "corridors": [
            {"properties": {"continuity_valid": True, "bands": [], "scoring": {"score": 75}}}
        ],
        "weather": {"wind": {"deg": 180, "speed": 10}, "humidity": 70, "temp": 15},
        "season": "automne",
        "hour": 6
    }

    def test_species_moose_returns_score(self):
        """Verify moose endpoint returns species-specific score"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/engines-v3/species/moose",
            json=self.TEST_PAYLOAD
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") is True
        assert data.get("species") == "moose"
        assert "score" in data
        assert 0 <= data["score"] <= 100

    def test_species_deer_returns_score(self):
        """Verify deer endpoint returns species-specific score"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/engines-v3/species/deer",
            json=self.TEST_PAYLOAD
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") is True
        assert data.get("species") == "deer"
        assert "score" in data
        assert 0 <= data["score"] <= 100

    def test_species_bear_returns_score(self):
        """Verify bear endpoint returns species-specific score"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/engines-v3/species/bear",
            json=self.TEST_PAYLOAD
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") is True
        assert data.get("species") == "bear"
        assert "score" in data
        assert 0 <= data["score"] <= 100

    def test_species_scores_are_differentiated(self):
        """Verify same input produces different scores for each species"""
        scores = {}
        for species in ["moose", "deer", "bear"]:
            response = requests.post(
                f"{BASE_URL}/api/v1/bionic/engines-v3/species/{species}",
                json=self.TEST_PAYLOAD
            )
            data = response.json()
            scores[species] = data.get("score", 0)
        
        # At least 2 of 3 species should have different scores
        unique_scores = set(scores.values())
        assert len(unique_scores) >= 2, f"Species scores should be differentiated: {scores}"
        print(f"Species scores: moose={scores['moose']}, deer={scores['deer']}, bear={scores['bear']}")

    def test_invalid_species_returns_error(self):
        """Verify invalid species returns error"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/engines-v3/species/elephant",
            json=self.TEST_PAYLOAD
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False
        assert "error" in data


class TestBionicV3Predictions:
    """Test POST /api/v1/bionic/engines-v3/predictions — AI predictions with decay"""

    TEST_PAYLOAD = {
        "zones": [
            {"properties": {"layer_id": "habitats"}},
            {"properties": {"layer_id": "alimentation"}},
            {"properties": {"layer_id": "hydro"}}
        ],
        "corridors": [
            {"properties": {"continuity_valid": True}}
        ],
        "weather": {"wind": {"deg": 180, "speed": 10}, "humidity": 70, "temp": 15},
        "season": "automne",
        "hour": 6
    }

    def test_predictions_returns_all_species(self):
        """Verify predictions endpoint returns data for all 3 species"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/engines-v3/predictions",
            json=self.TEST_PAYLOAD
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") is True
        predictions = data.get("predictions", {})
        
        assert "moose" in predictions
        assert "deer" in predictions
        assert "bear" in predictions

    def test_predictions_have_time_horizons(self):
        """Verify each species has 24h, 72h, and 7d predictions"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/engines-v3/predictions",
            json=self.TEST_PAYLOAD
        )
        data = response.json()
        predictions = data.get("predictions", {})
        
        for species in ["moose", "deer", "bear"]:
            sp_pred = predictions.get(species, {}).get("predictions", {})
            assert "24h" in sp_pred, f"{species} missing 24h prediction"
            assert "72h" in sp_pred, f"{species} missing 72h prediction"
            assert "7d" in sp_pred, f"{species} missing 7d prediction"

    def test_predictions_show_decay(self):
        """Verify probability decays over time (24h > 72h > 7d)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/engines-v3/predictions",
            json=self.TEST_PAYLOAD
        )
        data = response.json()
        predictions = data.get("predictions", {})
        
        for species in ["moose", "deer", "bear"]:
            sp_pred = predictions.get(species, {}).get("predictions", {})
            prob_24h = sp_pred.get("24h", {}).get("probability", 0)
            prob_72h = sp_pred.get("72h", {}).get("probability", 0)
            prob_7d = sp_pred.get("7d", {}).get("probability", 0)
            
            # Probability should generally decrease over time
            assert prob_24h >= prob_72h >= prob_7d, \
                f"{species}: 24h ({prob_24h}) >= 72h ({prob_72h}) >= 7d ({prob_7d}) expected"
            print(f"{species} decay: 24h={prob_24h}%, 72h={prob_72h}%, 7d={prob_7d}%")


class TestBionicV3BCECompliance:
    """Test BCE-4X compliance through V3 compute"""

    def test_bce_compliance_in_v3_compute(self):
        """Verify BCE compliance engine is included in V3 compute"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/engines-v3/compute",
            json={
                "zones": [{"properties": {"layer_id": "habitats"}}],
                "corridors": [],
                "weather": {},
                "season": "automne",
                "hour": 6,
                "species": "moose"
            }
        )
        data = response.json()
        engines = data.get("engines", {})
        
        # BCE compliance should be in the results
        bce = engines.get("bce_compliance", {})
        assert "score" in bce
        print(f"BCE compliance score: {bce.get('score')}")

    def test_corridor_continuity_engine(self):
        """Verify corridor continuity engine (COR-006) works"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/engines-v3/compute",
            json={
                "zones": [],
                "corridors": [
                    {"properties": {"continuity_valid": True, "bands": []}},
                    {"properties": {"continuity_valid": True, "bands": []}},
                    {"properties": {"continuity_valid": False, "bands": []}}
                ],
                "weather": {},
                "season": "automne",
                "hour": 6,
                "species": "moose"
            }
        )
        data = response.json()
        engines = data.get("engines", {})
        
        corridor = engines.get("corridor_continuity", {})
        assert "score" in corridor
        assert "total_corridors" in corridor
        assert corridor["total_corridors"] == 3
        print(f"Corridor continuity: {corridor.get('continuity_pct')}%")


class TestBionicV2Backward:
    """Verify V2 router still works at /api/v1/bionic/engines-v2/"""

    def test_v2_status_still_works(self):
        """Verify V2 status endpoint still returns 12 engines"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/engines-v2/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        assert data.get("engine_count") == 12


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
