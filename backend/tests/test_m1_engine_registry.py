"""
M1 Engine Registry Tests — Phase M1: Standardisation des moteurs BIONIC
========================================================================
Tests for:
- GET /api/v3/engines/registry (manifest with 5 engines)
- GET /api/v3/engines/score-point (species mapping, exclude param)
- GET /api/v3/engines/score-grid (grid with points, score_avg, engines_integrated)
- Species alias resolution (deer→CHEVREUIL, moose→ORIGNAL, cerf→CHEVREUIL, ours_noir→OURS)
- DynamicConsolidator weights sum to 1.0
- Score classification (OPTIMAL/BON/MODERE/FAIBLE)
- Tracability fields in response
- Non-regression tests for legacy V1/V10 endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test coordinates
LAT, LNG = 46.8139, -71.2080


class TestEngineRegistryManifest:
    """Tests for GET /api/v3/engines/registry — Manifest with 5 engines"""

    def test_registry_returns_200(self):
        """Registry endpoint should return 200 OK"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/registry")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Registry returns 200 OK")

    def test_registry_has_5_engines(self):
        """Registry should contain exactly 5 engines"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/registry")
        data = response.json()
        assert data["total_engines"] == 5, f"Expected 5 engines, got {data['total_engines']}"
        print(f"✓ Registry has {data['total_engines']} engines")

    def test_registry_engine_names(self):
        """Registry should contain the correct 5 engines"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/registry")
        data = response.json()
        engine_names = [e["name"] for e in data["engines"]]
        expected = ["ALIMENTATION-V1", "ALIMENTATION-V2", "REPOS-V1", "CORRIDORS-V10", "PRESSION-V1"]
        for name in expected:
            assert name in engine_names, f"Expected engine {name} not found"
        print(f"✓ Registry contains all expected engines: {expected}")

    def test_registry_engine_metadata(self):
        """Each engine should have required metadata fields"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/registry")
        data = response.json()
        required_fields = ["name", "version", "type", "domain", "species_supported", "unit", "default_weight", "description"]
        for engine in data["engines"]:
            for field in required_fields:
                assert field in engine, f"Engine {engine.get('name', 'unknown')} missing field: {field}"
        print("✓ All engines have required metadata fields")

    def test_registry_all_engines_support_species(self):
        """All engines should support CHEVREUIL/ORIGNAL/OURS/DINDON/WAPITI"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/registry")
        data = response.json()
        canonical_species = ["CHEVREUIL", "ORIGNAL", "OURS", "DINDON", "WAPITI"]
        for engine in data["engines"]:
            for species in canonical_species:
                assert species in engine["species_supported"], f"Engine {engine['name']} missing species {species}"
        print("✓ All engines support all canonical species")


class TestScorePointSpeciesMapping:
    """Tests for species alias resolution in /api/v3/engines/score-point"""

    def test_chevreuil_direct(self):
        """species=CHEVREUIL should return species='CHEVREUIL'"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-point?lat={LAT}&lng={LNG}&species=CHEVREUIL&month=10")
        data = response.json()
        assert data["species"] == "CHEVREUIL", f"Expected CHEVREUIL, got {data['species']}"
        print("✓ species=CHEVREUIL → CHEVREUIL")

    def test_deer_alias(self):
        """species=deer should resolve to CHEVREUIL"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-point?lat={LAT}&lng={LNG}&species=deer&month=10")
        data = response.json()
        assert data["species"] == "CHEVREUIL", f"Expected CHEVREUIL, got {data['species']}"
        print("✓ species=deer → CHEVREUIL")

    def test_moose_alias(self):
        """species=moose should resolve to ORIGNAL"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-point?lat={LAT}&lng={LNG}&species=moose&month=10")
        data = response.json()
        assert data["species"] == "ORIGNAL", f"Expected ORIGNAL, got {data['species']}"
        print("✓ species=moose → ORIGNAL")

    def test_cerf_alias(self):
        """species=cerf should resolve to CHEVREUIL"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-point?lat={LAT}&lng={LNG}&species=cerf&month=10")
        data = response.json()
        assert data["species"] == "CHEVREUIL", f"Expected CHEVREUIL, got {data['species']}"
        print("✓ species=cerf → CHEVREUIL")

    def test_ours_noir_alias(self):
        """species=ours_noir should resolve to OURS"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-point?lat={LAT}&lng={LNG}&species=ours_noir&month=10")
        data = response.json()
        assert data["species"] == "OURS", f"Expected OURS, got {data['species']}"
        print("✓ species=ours_noir → OURS")


class TestScorePointComponents:
    """Tests for /api/v3/engines/score-point response structure"""

    def test_score_point_has_5_components(self):
        """Score point should have 5 engine components"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-point?lat={LAT}&lng={LNG}&species=CHEVREUIL&month=10")
        data = response.json()
        assert len(data["components"]) == 5, f"Expected 5 components, got {len(data['components'])}"
        expected_components = ["ALIMENTATION-V1", "ALIMENTATION-V2", "REPOS-V1", "CORRIDORS-V10", "PRESSION-V1"]
        for comp in expected_components:
            assert comp in data["components"], f"Missing component: {comp}"
        print(f"✓ Score point has 5 components: {list(data['components'].keys())}")

    def test_score_range_0_100(self):
        """Score should be between 0 and 100"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-point?lat={LAT}&lng={LNG}&species=CHEVREUIL&month=10")
        data = response.json()
        assert 0 <= data["score"] <= 100, f"Score {data['score']} out of range 0-100"
        print(f"✓ Score {data['score']} is within 0-100 range")

    def test_pression_v1_returns_score(self):
        """PRESSION-V1 engine should return a score based on distance to routes/buildings"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-point?lat={LAT}&lng={LNG}&species=CHEVREUIL&month=10")
        data = response.json()
        pression_score = data["components"]["PRESSION-V1"]
        assert 0 <= pression_score <= 100, f"PRESSION-V1 score {pression_score} out of range"
        print(f"✓ PRESSION-V1 score: {pression_score}")


class TestWeightsNormalization:
    """Tests for DynamicConsolidator weights sum to 1.0"""

    def test_weights_sum_to_one_all_engines(self):
        """With all 5 engines active, weights should sum to 1.0"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-point?lat={LAT}&lng={LNG}&species=CHEVREUIL&month=10")
        data = response.json()
        weights_sum = sum(data["weights"].values())
        assert abs(weights_sum - 1.0) < 0.001, f"Weights sum {weights_sum} != 1.0"
        print(f"✓ Weights sum to {weights_sum} (5 engines active)")

    def test_weights_sum_to_one_with_exclusion(self):
        """With CORRIDORS-V10 excluded, remaining weights should sum to 1.0"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-point?lat={LAT}&lng={LNG}&species=CHEVREUIL&month=10&exclude=CORRIDORS-V10")
        data = response.json()
        weights_sum = sum(data["weights"].values())
        assert abs(weights_sum - 1.0) < 0.001, f"Weights sum {weights_sum} != 1.0 after exclusion"
        assert "CORRIDORS-V10" not in data["weights"], "CORRIDORS-V10 should be excluded from weights"
        print(f"✓ Weights sum to {weights_sum} with CORRIDORS-V10 excluded")


class TestExcludeEngines:
    """Tests for exclude parameter in score-point"""

    def test_exclude_corridors_v10(self):
        """exclude=CORRIDORS-V10 should remove it from active engines"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-point?lat={LAT}&lng={LNG}&species=CHEVREUIL&month=10&exclude=CORRIDORS-V10")
        data = response.json()
        assert "CORRIDORS-V10" not in data["components"], "CORRIDORS-V10 should be excluded from components"
        assert "CORRIDORS-V10" in data["tracability"]["engines_excluded"], "CORRIDORS-V10 should be in excluded list"
        assert len(data["components"]) == 4, f"Expected 4 components after exclusion, got {len(data['components'])}"
        print("✓ exclude=CORRIDORS-V10 works correctly")

    def test_exclude_multiple_engines(self):
        """exclude=CORRIDORS-V10,PRESSION-V1 should exclude both"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-point?lat={LAT}&lng={LNG}&species=CHEVREUIL&month=10&exclude=CORRIDORS-V10,PRESSION-V1")
        data = response.json()
        assert "CORRIDORS-V10" not in data["components"]
        assert "PRESSION-V1" not in data["components"]
        assert len(data["components"]) == 3, f"Expected 3 components after exclusion, got {len(data['components'])}"
        print("✓ Multiple engine exclusion works correctly")


class TestScoreClassification:
    """Tests for score classification thresholds"""

    def test_classification_labels_present(self):
        """Response should contain classe, label, color"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-point?lat={LAT}&lng={LNG}&species=CHEVREUIL&month=10")
        data = response.json()
        assert "classe" in data, "Missing 'classe' field"
        assert "label" in data, "Missing 'label' field"
        assert "color" in data, "Missing 'color' field"
        print(f"✓ Classification: {data['classe']} ({data['label']}) - {data['color']}")

    def test_classification_thresholds(self):
        """Verify classification thresholds: >=80 OPTIMAL, >=60 BON, >=40 MODERE, <40 FAIBLE"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-point?lat={LAT}&lng={LNG}&species=CHEVREUIL&month=10")
        data = response.json()
        score = data["score"]
        classe = data["classe"]
        
        if score >= 80:
            assert classe == "OPTIMAL", f"Score {score} should be OPTIMAL, got {classe}"
        elif score >= 60:
            assert classe == "BON", f"Score {score} should be BON, got {classe}"
        elif score >= 40:
            assert classe == "MODERE", f"Score {score} should be MODERE, got {classe}"
        else:
            assert classe == "FAIBLE", f"Score {score} should be FAIBLE, got {classe}"
        print(f"✓ Score {score} correctly classified as {classe}")


class TestTracability:
    """Tests for tracability fields in score-point response"""

    def test_tracability_fields_present(self):
        """Response should contain tracability with engines_active, engines_excluded, consolidator"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-point?lat={LAT}&lng={LNG}&species=CHEVREUIL&month=10")
        data = response.json()
        assert "tracability" in data, "Missing 'tracability' field"
        tracability = data["tracability"]
        assert "engines_active" in tracability, "Missing 'engines_active' in tracability"
        assert "engines_excluded" in tracability, "Missing 'engines_excluded' in tracability"
        assert "consolidator" in tracability, "Missing 'consolidator' in tracability"
        print(f"✓ Tracability fields present: {list(tracability.keys())}")

    def test_tracability_consolidator_version(self):
        """Consolidator should be DynamicConsolidator-v1"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-point?lat={LAT}&lng={LNG}&species=CHEVREUIL&month=10")
        data = response.json()
        assert data["tracability"]["consolidator"] == "DynamicConsolidator-v1"
        print("✓ Consolidator version: DynamicConsolidator-v1")


class TestScoreGrid:
    """Tests for GET /api/v3/engines/score-grid"""

    def test_score_grid_returns_200(self):
        """Score grid should return 200 OK"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-grid?lat={LAT}&lng={LNG}&species=CHEVREUIL&month=10&grid_size=5")
        assert response.status_code == 200
        print("✓ Score grid returns 200 OK")

    def test_score_grid_has_points(self):
        """Score grid should have points array"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-grid?lat={LAT}&lng={LNG}&species=CHEVREUIL&month=10&grid_size=5")
        data = response.json()
        assert "points" in data, "Missing 'points' in grid response"
        assert data["total_points"] == 25, f"Expected 25 points (5x5), got {data['total_points']}"
        print(f"✓ Score grid has {data['total_points']} points")

    def test_score_grid_has_score_avg(self):
        """Score grid should have score_avg"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-grid?lat={LAT}&lng={LNG}&species=CHEVREUIL&month=10&grid_size=5")
        data = response.json()
        assert "score_avg" in data, "Missing 'score_avg' in grid response"
        assert 0 <= data["score_avg"] <= 100
        print(f"✓ Score grid score_avg: {data['score_avg']}")

    def test_score_grid_has_engines_integrated(self):
        """Score grid should have engines_integrated list"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-grid?lat={LAT}&lng={LNG}&species=CHEVREUIL&month=10&grid_size=5")
        data = response.json()
        assert "engines_integrated" in data, "Missing 'engines_integrated' in grid response"
        assert len(data["engines_integrated"]) == 5
        print(f"✓ Engines integrated: {data['engines_integrated']}")

    def test_score_grid_point_structure(self):
        """Each point should have lat, lng, score, classe, color"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-grid?lat={LAT}&lng={LNG}&species=CHEVREUIL&month=10&grid_size=5")
        data = response.json()
        required_fields = ["lat", "lng", "score", "classe", "color"]
        for point in data["points"]:
            for field in required_fields:
                assert field in point, f"Point missing field: {field}"
        print("✓ All points have required fields")


class TestLegacyNonRegression:
    """Non-regression tests for legacy V1/V10 endpoints"""

    def test_legacy_alimentation_v1_point(self):
        """GET /api/v1/alimentation/point should still work with species=CERF"""
        response = requests.get(f"{BASE_URL}/api/v1/alimentation/point?lat={LAT}&lng={LNG}&species=CERF&month=10")
        assert response.status_code == 200, f"Legacy alimentation/point failed: {response.status_code}"
        data = response.json()
        assert "score_alimentation" in data, "Missing score_alimentation in legacy response"
        print(f"✓ Legacy /api/v1/alimentation/point works (score: {data['score_alimentation']})")

    def test_legacy_repos_v1_point(self):
        """GET /api/v1/repos/point should still work"""
        response = requests.get(f"{BASE_URL}/api/v1/repos/point?lat={LAT}&lng={LNG}&species=CERF&month=10")
        assert response.status_code == 200, f"Legacy repos/point failed: {response.status_code}"
        data = response.json()
        assert "score_repos" in data, "Missing score_repos in legacy response"
        print(f"✓ Legacy /api/v1/repos/point works (score: {data['score_repos']})")

    def test_legacy_score_consolide_point(self):
        """GET /api/v1/score-consolide/point should still work"""
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/point?lat={LAT}&lng={LNG}&species=CERF&month=10")
        assert response.status_code == 200, f"Legacy score-consolide/point failed: {response.status_code}"
        data = response.json()
        assert "score" in data, "Missing score in legacy response"
        assert "components" in data, "Missing components in legacy response"
        print(f"✓ Legacy /api/v1/score-consolide/point works (score: {data['score']})")

    def test_legacy_score_consolide_heatmap_with_include_corridors(self):
        """GET /api/v1/score-consolide/heatmap with include_corridors should work"""
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap?lat={LAT}&lng={LNG}&species=CERF&month=10&grid_size=5&include_corridors=1")
        assert response.status_code == 200, f"Legacy heatmap failed: {response.status_code}"
        data = response.json()
        assert "corridors_v10_included" in data, "Missing corridors_v10_included in heatmap response"
        assert data["corridors_v10_included"] == True
        print(f"✓ Legacy /api/v1/score-consolide/heatmap with include_corridors=1 works")

    def test_legacy_corridors_v10_analyze_full(self):
        """POST /api/v10/corridors/analyze-full should still work"""
        payload = {"center_lat": LAT, "center_lng": LNG, "species": "CERF", "month": 10}
        response = requests.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json=payload)
        assert response.status_code == 200, f"Legacy corridors/analyze-full failed: {response.status_code}"
        data = response.json()
        assert "score_corridor" in data, "Missing score_corridor in response"
        print(f"✓ Legacy POST /api/v10/corridors/analyze-full works (score: {data['score_corridor']})")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
