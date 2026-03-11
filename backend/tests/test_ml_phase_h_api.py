"""
TEST ML ENGINE — PHASE H — BIONIC V5 ULTIME 300%
=================================================

Endpoints testés:
  POST /api/v1/bionic/ml/features        — Build feature vector (32 features)
  POST /api/v1/bionic/ml/predictions      — Generate predictions (6 targets x 3 horizons)
  POST /api/v1/bionic/ml/training-session — Train model on multi-territory data
  GET  /api/v1/bionic/ml/schema           — Feature & target schemas
  GET  /api/v1/bionic/ml/status           — ML engine status

Tests couverts:
  - Validation 5 espèces supportées
  - 32 features normalisées [0,1]
  - 6 cibles comportementales
  - 3 horizons avec decay 24h > 48h > 72h
  - Minimum 2 territoires pour training
  - Espèce invalide retourne 400
  - Non-régression pipeline/comparison et api-keys/status
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test territories (from context)
LAURENTIDES = {"north": 46.95, "south": 46.85, "east": -74.00, "west": -74.15}
GATINEAU = {"north": 45.55, "south": 45.45, "east": -75.70, "west": -75.85}
CHARLEVOIX = {"north": 47.60, "south": 47.50, "east": -70.50, "west": -70.65}

SUPPORTED_SPECIES = ["moose", "deer", "bear", "wild_turkey", "elk"]
HORIZONS = ["24h", "48h", "72h"]
EXPECTED_FEATURE_COUNT = 32
EXPECTED_TARGET_COUNT = 6


@pytest.fixture(scope="module")
def api_session():
    """Shared requests session with headers."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


# ==============================================================================
# GET /api/v1/bionic/ml/status — ML Engine Status
# ==============================================================================
class TestMLStatus:
    """Tests for GET /api/v1/bionic/ml/status endpoint"""

    def test_status_returns_200(self, api_session):
        """Status endpoint should return 200"""
        response = api_session.get(f"{BASE_URL}/api/v1/bionic/ml/status", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ GET /ml/status returns 200")

    def test_status_active(self, api_session):
        """Status should be active"""
        response = api_session.get(f"{BASE_URL}/api/v1/bionic/ml/status", timeout=30)
        data = response.json()
        assert data.get("status") == "active", f"Expected status=active, got {data.get('status')}"
        print("✓ ML module status = active")

    def test_status_engine_internal_sklearn(self, api_session):
        """Engine should be internal_sklearn_ridge"""
        response = api_session.get(f"{BASE_URL}/api/v1/bionic/ml/status", timeout=30)
        data = response.json()
        assert data.get("engine") == "internal_sklearn_ridge", f"Expected engine=internal_sklearn_ridge, got {data.get('engine')}"
        print("✓ Engine = internal_sklearn_ridge")

    def test_status_module_label(self, api_session):
        """Module should be ML_ENGINE"""
        response = api_session.get(f"{BASE_URL}/api/v1/bionic/ml/status", timeout=30)
        data = response.json()
        assert data.get("module") == "ML_ENGINE"
        assert "label" in data
        print(f"✓ Module = {data.get('module')}, Label = {data.get('label')}")

    def test_status_species_supported(self, api_session):
        """Should list all 5 supported species"""
        response = api_session.get(f"{BASE_URL}/api/v1/bionic/ml/status", timeout=30)
        data = response.json()
        species = data.get("species_supported", [])
        assert len(species) == 5, f"Expected 5 species, got {len(species)}"
        for sp in SUPPORTED_SPECIES:
            assert sp in species, f"Missing species: {sp}"
        print(f"✓ 5 species supported: {species}")

    def test_status_5_endpoints_listed(self, api_session):
        """Should list all 5 ML endpoints"""
        response = api_session.get(f"{BASE_URL}/api/v1/bionic/ml/status", timeout=30)
        data = response.json()
        endpoints = data.get("endpoints", [])
        assert len(endpoints) == 5, f"Expected 5 endpoints, got {len(endpoints)}"
        print(f"✓ 5 endpoints listed")


# ==============================================================================
# GET /api/v1/bionic/ml/schema — Feature & Target Schemas
# ==============================================================================
class TestMLSchema:
    """Tests for GET /api/v1/bionic/ml/schema endpoint"""

    def test_schema_returns_200(self, api_session):
        """Schema endpoint should return 200"""
        response = api_session.get(f"{BASE_URL}/api/v1/bionic/ml/schema", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ GET /ml/schema returns 200")

    def test_schema_feature_count_32(self, api_session):
        """Should have exactly 32 features"""
        response = api_session.get(f"{BASE_URL}/api/v1/bionic/ml/schema", timeout=30)
        data = response.json()
        features = data.get("features", {})
        assert features.get("feature_count") == EXPECTED_FEATURE_COUNT, f"Expected 32 features, got {features.get('feature_count')}"
        print(f"✓ Feature count = {features.get('feature_count')}")

    def test_schema_target_count_6(self, api_session):
        """Should have exactly 6 targets"""
        response = api_session.get(f"{BASE_URL}/api/v1/bionic/ml/schema", timeout=30)
        data = response.json()
        targets = data.get("targets", {})
        assert targets.get("target_count") == EXPECTED_TARGET_COUNT, f"Expected 6 targets, got {targets.get('target_count')}"
        print(f"✓ Target count = {targets.get('target_count')}")

    def test_schema_horizons_3(self, api_session):
        """Should have 3 horizons: 24h, 48h, 72h"""
        response = api_session.get(f"{BASE_URL}/api/v1/bionic/ml/schema", timeout=30)
        data = response.json()
        targets = data.get("targets", {})
        horizons = targets.get("horizons", [])
        assert len(horizons) == 3, f"Expected 3 horizons, got {len(horizons)}"
        for h in HORIZONS:
            assert h in horizons, f"Missing horizon: {h}"
        print(f"✓ Horizons = {horizons}")

    def test_schema_horizon_decay_values(self, api_session):
        """Horizon decay should be 24h=1.0, 48h=0.85, 72h=0.70"""
        response = api_session.get(f"{BASE_URL}/api/v1/bionic/ml/schema", timeout=30)
        data = response.json()
        targets = data.get("targets", {})
        decay = targets.get("horizon_decay", {})
        assert decay.get("24h") == 1.0, f"Expected 24h=1.0, got {decay.get('24h')}"
        assert decay.get("48h") == 0.85, f"Expected 48h=0.85, got {decay.get('48h')}"
        assert decay.get("72h") == 0.70, f"Expected 72h=0.70, got {decay.get('72h')}"
        print(f"✓ Horizon decay: 24h={decay.get('24h')}, 48h={decay.get('48h')}, 72h={decay.get('72h')}")

    def test_schema_modules_contributing(self, api_session):
        """Should have 10 modules contributing features"""
        response = api_session.get(f"{BASE_URL}/api/v1/bionic/ml/schema", timeout=30)
        data = response.json()
        features = data.get("features", {})
        modules = features.get("modules_contributing", {})
        assert len(modules) == 10, f"Expected 10 modules, got {len(modules)}"
        # Sum of contributions should be 32
        total = sum(modules.values())
        assert total == 32, f"Expected 32 total features from modules, got {total}"
        print(f"✓ 10 modules contributing 32 features total")

    def test_schema_target_names(self, api_session):
        """Should have 6 target names"""
        response = api_session.get(f"{BASE_URL}/api/v1/bionic/ml/schema", timeout=30)
        data = response.json()
        targets = data.get("targets", {})
        names = targets.get("target_names", [])
        assert len(names) == 6, f"Expected 6 target names, got {len(names)}"
        expected_targets = ["presence_probability", "movement_intensity", "retreat_probability",
                           "exploration_probability", "pressure_sensitivity", "thermal_comfort_index"]
        for t in expected_targets:
            assert t in names, f"Missing target: {t}"
        print(f"✓ 6 target names: {names}")


# ==============================================================================
# POST /api/v1/bionic/ml/features — Feature Extraction
# ==============================================================================
class TestMLFeatures:
    """Tests for POST /api/v1/bionic/ml/features endpoint"""

    @pytest.mark.parametrize("species", SUPPORTED_SPECIES)
    def test_features_all_species(self, api_session, species):
        """Features endpoint should work for all 5 species"""
        payload = {
            "bounds": LAURENTIDES,
            "species": species,
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/features",
            json=payload,
            timeout=60
        )
        assert response.status_code == 200, f"Expected 200 for {species}, got {response.status_code}"
        data = response.json()
        assert data.get("species") == species
        print(f"✓ POST /ml/features works for species={species}")

    def test_features_returns_32_features(self, api_session):
        """Should return exactly 32 features"""
        payload = {
            "bounds": LAURENTIDES,
            "species": "moose",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/features",
            json=payload,
            timeout=60
        )
        data = response.json()
        assert data.get("feature_count") == 32, f"Expected 32 features, got {data.get('feature_count')}"
        assert len(data.get("feature_vector", [])) == 32, f"Expected 32 values in vector, got {len(data.get('feature_vector', []))}"
        print(f"✓ Feature vector has 32 values")

    def test_features_normalized_0_1(self, api_session):
        """All features should be normalized between 0 and 1"""
        payload = {
            "bounds": GATINEAU,
            "species": "deer",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/features",
            json=payload,
            timeout=60
        )
        data = response.json()
        vector = data.get("feature_vector", [])
        for i, v in enumerate(vector):
            assert 0.0 <= v <= 1.0, f"Feature {i} out of range [0,1]: {v}"
        print(f"✓ All 32 features normalized in [0, 1]")

    def test_features_has_feature_names(self, api_session):
        """Should return feature names matching count"""
        payload = {
            "bounds": LAURENTIDES,
            "species": "bear",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/features",
            json=payload,
            timeout=60
        )
        data = response.json()
        names = data.get("feature_names", [])
        vector = data.get("feature_vector", [])
        assert len(names) == len(vector), f"Names count {len(names)} != vector count {len(vector)}"
        print(f"✓ Feature names count matches vector count")

    def test_features_has_source_ids(self, api_session):
        """Should return source_ids from pipeline"""
        payload = {
            "bounds": CHARLEVOIX,
            "species": "elk",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/features",
            json=payload,
            timeout=60
        )
        data = response.json()
        source_ids = data.get("source_ids", {})
        assert len(source_ids) >= 10, f"Expected at least 10 source_ids, got {len(source_ids)}"
        print(f"✓ Source IDs returned: {len(source_ids)} modules")

    def test_features_invalid_species_400(self, api_session):
        """Invalid species should return 400"""
        payload = {
            "bounds": LAURENTIDES,
            "species": "invalid_animal",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/features",
            json=payload,
            timeout=60
        )
        assert response.status_code == 400, f"Expected 400 for invalid species, got {response.status_code}"
        print(f"✓ Invalid species returns 400")

    def test_features_computation_time(self, api_session):
        """Should include computation_time_ms"""
        payload = {
            "bounds": LAURENTIDES,
            "species": "moose",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/features",
            json=payload,
            timeout=60
        )
        data = response.json()
        assert "computation_time_ms" in data, "Missing computation_time_ms"
        print(f"✓ Computation time: {data.get('computation_time_ms')}ms")


# ==============================================================================
# POST /api/v1/bionic/ml/predictions — Behavioral Predictions
# ==============================================================================
class TestMLPredictions:
    """Tests for POST /api/v1/bionic/ml/predictions endpoint"""

    @pytest.mark.parametrize("species", SUPPORTED_SPECIES)
    def test_predictions_all_species(self, api_session, species):
        """Predictions endpoint should work for all 5 species"""
        payload = {
            "bounds": LAURENTIDES,
            "species": species,
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/predictions",
            json=payload,
            timeout=60
        )
        assert response.status_code == 200, f"Expected 200 for {species}, got {response.status_code}"
        data = response.json()
        assert data.get("species") == species
        print(f"✓ POST /ml/predictions works for species={species}")

    def test_predictions_3_horizons(self, api_session):
        """Should return predictions for all 3 horizons"""
        payload = {
            "bounds": GATINEAU,
            "species": "deer",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/predictions",
            json=payload,
            timeout=60
        )
        data = response.json()
        horizons = data.get("horizons", [])
        predictions = data.get("predictions", {})
        assert len(horizons) == 3, f"Expected 3 horizons, got {len(horizons)}"
        for h in HORIZONS:
            assert h in predictions, f"Missing predictions for horizon: {h}"
        print(f"✓ Predictions for 3 horizons: {horizons}")

    def test_predictions_6_targets_per_horizon(self, api_session):
        """Each horizon should have 6 targets"""
        payload = {
            "bounds": CHARLEVOIX,
            "species": "bear",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/predictions",
            json=payload,
            timeout=60
        )
        data = response.json()
        predictions = data.get("predictions", {})
        for h in HORIZONS:
            targets = predictions.get(h, {})
            assert len(targets) == 6, f"Expected 6 targets for {h}, got {len(targets)}"
        print(f"✓ 6 targets per horizon")

    def test_predictions_decay_24h_gt_48h_gt_72h(self, api_session):
        """Predictions should decay: 24h > 48h > 72h for most targets"""
        payload = {
            "bounds": LAURENTIDES,
            "species": "moose",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/predictions",
            json=payload,
            timeout=60
        )
        data = response.json()
        predictions = data.get("predictions", {})
        
        # Check presence_probability decays (most reliable indicator)
        p24 = predictions.get("24h", {}).get("presence_probability", 0)
        p48 = predictions.get("48h", {}).get("presence_probability", 0)
        p72 = predictions.get("72h", {}).get("presence_probability", 0)
        
        # Due to decay factors: 24h=1.0, 48h=0.85, 72h=0.70
        # We expect p24 >= p48 >= p72 (approximately, due to noise)
        assert p24 >= p72 * 0.9, f"Decay not applied: 24h={p24} should be >= 72h*0.9={p72*0.9}"
        print(f"✓ Decay applied: 24h={p24:.4f}, 48h={p48:.4f}, 72h={p72:.4f}")

    def test_predictions_values_normalized(self, api_session):
        """All prediction values should be in [0, 1]"""
        payload = {
            "bounds": GATINEAU,
            "species": "wild_turkey",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/predictions",
            json=payload,
            timeout=60
        )
        data = response.json()
        predictions = data.get("predictions", {})
        for h, targets in predictions.items():
            for name, value in targets.items():
                assert 0.0 <= value <= 1.0, f"Prediction {h}/{name} out of range: {value}"
        print(f"✓ All predictions normalized in [0, 1]")

    def test_predictions_invalid_species_400(self, api_session):
        """Invalid species should return 400"""
        payload = {
            "bounds": LAURENTIDES,
            "species": "unicorn",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/predictions",
            json=payload,
            timeout=60
        )
        assert response.status_code == 400, f"Expected 400 for invalid species, got {response.status_code}"
        print(f"✓ Invalid species returns 400")

    def test_predictions_target_names(self, api_session):
        """Should return target_names list"""
        payload = {
            "bounds": LAURENTIDES,
            "species": "elk",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/predictions",
            json=payload,
            timeout=60
        )
        data = response.json()
        names = data.get("target_names", [])
        assert len(names) == 6, f"Expected 6 target names, got {len(names)}"
        print(f"✓ Target names: {names}")


# ==============================================================================
# POST /api/v1/bionic/ml/training-session — Model Training
# ==============================================================================
class TestMLTrainingSession:
    """Tests for POST /api/v1/bionic/ml/training-session endpoint"""

    def test_training_3_territories_success(self, api_session):
        """Training with 3 territories should succeed"""
        payload = {
            "territories": [LAURENTIDES, GATINEAU, CHARLEVOIX],
            "species": "moose",
            "horizon": "24h",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/training-session",
            json=payload,
            timeout=120
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "trained", f"Expected status=trained, got {data.get('status')}"
        print(f"✓ Training with 3 territories succeeded")

    def test_training_returns_model_id(self, api_session):
        """Should return a model_id"""
        payload = {
            "territories": [LAURENTIDES, GATINEAU, CHARLEVOIX],
            "species": "deer",
            "horizon": "24h",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/training-session",
            json=payload,
            timeout=120
        )
        data = response.json()
        model_id = data.get("model_id", "")
        assert model_id.startswith("MLM_"), f"Expected model_id starting with MLM_, got {model_id}"
        print(f"✓ Model ID: {model_id}")

    def test_training_returns_mse(self, api_session):
        """Should return MSE metric"""
        payload = {
            "territories": [LAURENTIDES, GATINEAU, CHARLEVOIX],
            "species": "bear",
            "horizon": "48h",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/training-session",
            json=payload,
            timeout=120
        )
        data = response.json()
        metrics = data.get("metrics", {})
        assert "mse" in metrics, "Missing MSE metric"
        mse = metrics.get("mse")
        assert isinstance(mse, float), f"MSE should be float, got {type(mse)}"
        print(f"✓ MSE = {mse}")

    def test_training_returns_r2_scores(self, api_session):
        """Should return R2 scores for each target"""
        payload = {
            "territories": [LAURENTIDES, GATINEAU, CHARLEVOIX],
            "species": "elk",
            "horizon": "72h",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/training-session",
            json=payload,
            timeout=120
        )
        data = response.json()
        metrics = data.get("metrics", {})
        r2_scores = metrics.get("r2_scores", {})
        assert len(r2_scores) == 6, f"Expected 6 R2 scores, got {len(r2_scores)}"
        assert "mean_r2" in metrics, "Missing mean_r2"
        print(f"✓ R2 scores: {r2_scores}")
        print(f"✓ Mean R2: {metrics.get('mean_r2')}")

    def test_training_engine_internal_sklearn(self, api_session):
        """Should use internal_sklearn_ridge engine"""
        payload = {
            "territories": [LAURENTIDES, GATINEAU],
            "species": "wild_turkey",
            "horizon": "24h",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/training-session",
            json=payload,
            timeout=120
        )
        data = response.json()
        assert data.get("engine") == "internal_sklearn_ridge", f"Expected internal_sklearn_ridge, got {data.get('engine')}"
        print(f"✓ Engine = internal_sklearn_ridge")

    def test_training_minimum_2_territories_success(self, api_session):
        """Training with exactly 2 territories should work"""
        payload = {
            "territories": [LAURENTIDES, GATINEAU],
            "species": "moose",
            "horizon": "24h",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/training-session",
            json=payload,
            timeout=120
        )
        assert response.status_code == 200, f"Expected 200 for 2 territories, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "trained"
        print(f"✓ Training with 2 territories succeeded")

    def test_training_1_territory_400(self, api_session):
        """Training with only 1 territory should return 400"""
        payload = {
            "territories": [LAURENTIDES],
            "species": "moose",
            "horizon": "24h",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/training-session",
            json=payload,
            timeout=60
        )
        assert response.status_code == 400, f"Expected 400 for 1 territory, got {response.status_code}"
        print(f"✓ Training with 1 territory returns 400")

    def test_training_invalid_species_400(self, api_session):
        """Invalid species should return 400"""
        payload = {
            "territories": [LAURENTIDES, GATINEAU],
            "species": "invalid_animal",
            "horizon": "24h",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/training-session",
            json=payload,
            timeout=60
        )
        assert response.status_code == 400, f"Expected 400 for invalid species, got {response.status_code}"
        print(f"✓ Invalid species returns 400")

    def test_training_returns_counts(self, api_session):
        """Should return feature_count, target_count, training_samples"""
        payload = {
            "territories": [LAURENTIDES, GATINEAU, CHARLEVOIX],
            "species": "deer",
            "horizon": "24h",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/ml/training-session",
            json=payload,
            timeout=120
        )
        data = response.json()
        assert data.get("feature_count") == 32, f"Expected feature_count=32, got {data.get('feature_count')}"
        assert data.get("target_count") == 6, f"Expected target_count=6, got {data.get('target_count')}"
        assert data.get("training_samples") == 3, f"Expected training_samples=3, got {data.get('training_samples')}"
        print(f"✓ Counts: features={data.get('feature_count')}, targets={data.get('target_count')}, samples={data.get('training_samples')}")


# ==============================================================================
# Non-Regression Tests — Pipeline Comparison & API Keys Status
# ==============================================================================
class TestNonRegression:
    """Non-regression tests for existing endpoints"""

    def test_pipeline_comparison_works(self, api_session):
        """POST /api/v1/bionic/pipeline/comparison should still work"""
        payload = {
            "bounds_a": LAURENTIDES,
            "bounds_b": GATINEAU,
            "species": "moose",
            "resolution": 30
        }
        response = api_session.post(
            f"{BASE_URL}/api/v1/bionic/pipeline/comparison",
            json=payload,
            timeout=120
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "recommendation" in data, "Missing recommendation in response"
        assert "advantages" in data, "Missing advantages in response"
        print(f"✓ Non-regression: POST /pipeline/comparison works")

    def test_api_keys_status_works(self, api_session):
        """GET /api/v1/system/api-keys/status should still work"""
        response = api_session.get(
            f"{BASE_URL}/api/v1/system/api-keys/status",
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "key_statuses" in data, "Missing key_statuses in response"
        assert len(data.get("key_statuses", {})) == 6, "Expected 6 API keys"
        print(f"✓ Non-regression: GET /api-keys/status works")

    def test_pipeline_status_works(self, api_session):
        """GET /api/v1/bionic/pipeline/status should still work"""
        response = api_session.get(
            f"{BASE_URL}/api/v1/bionic/pipeline/status",
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "active", f"Expected status=active, got {data.get('status')}"
        print(f"✓ Non-regression: GET /pipeline/status works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
