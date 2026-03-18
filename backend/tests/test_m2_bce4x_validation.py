"""
Phase M2 Backend Tests — BCE-4X Validation + Individual Engine Scoring
=======================================================================
Tests:
- GET /api/v3/engines/registry returns 5 engines with engine_type field
- GET /api/v3/engines/{name}/score returns individual engine score
- GET /api/v3/engines/validate returns bce4x + steeve_max validation
- NON-REGRESSION: V1/V10 legacy endpoints still work
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestEngineRegistryV3:
    """V3 Engine Registry endpoint tests"""
    
    def test_registry_returns_5_engines(self):
        """GET /api/v3/engines/registry returns 5 engines with engine_type field"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/registry")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "total_engines" in data, "Missing total_engines field"
        assert data["total_engines"] == 5, f"Expected 5 engines, got {data['total_engines']}"
        
        assert "engines" in data, "Missing engines list"
        for engine in data["engines"]:
            assert "engine_type" in engine, f"Engine {engine.get('name')} missing engine_type field"
            assert "name" in engine
            assert "version" in engine
            assert "domain" in engine
        
        # Check all expected engines are present
        engine_names = [e["name"] for e in data["engines"]]
        expected = ["ALIMENTATION-V1", "ALIMENTATION-V2", "REPOS-V1", "CORRIDORS-V10", "PRESSION-V1"]
        for exp in expected:
            assert exp in engine_names, f"Expected engine {exp} not found in registry"
        
        print(f"PASS: Registry returns {data['total_engines']} engines with engine_type field")


class TestIndividualEngineScore:
    """Individual engine scoring endpoint tests"""
    
    @pytest.mark.parametrize("engine_name,expected_domain", [
        ("ALIMENTATION-V1", "alimentation"),
        ("PRESSION-V1", "pression"),
        ("REPOS-V1", "repos"),
        ("CORRIDORS-V10", "corridors"),
    ])
    def test_individual_engine_score(self, engine_name, expected_domain):
        """GET /api/v3/engines/{name}/score returns score with version and domain"""
        params = {"lat": 46.8139, "lng": -71.2080, "species": "CHEVREUIL", "month": 10}
        response = requests.get(f"{BASE_URL}/api/v3/engines/{engine_name}/score", params=params)
        assert response.status_code == 200, f"Expected 200 for {engine_name}, got {response.status_code}"
        
        data = response.json()
        assert "engine" in data, f"Missing engine field for {engine_name}"
        assert data["engine"] == engine_name
        assert "version" in data, f"Missing version field for {engine_name}"
        assert "domain" in data, f"Missing domain field for {engine_name}"
        assert data["domain"] == expected_domain, f"Expected domain {expected_domain}, got {data['domain']}"
        assert "score" in data, f"Missing score field for {engine_name}"
        assert 0 <= data["score"] <= 100, f"Score {data['score']} not in range 0-100"
        
        print(f"PASS: {engine_name} returns score={data['score']}, version={data['version']}, domain={data['domain']}")
    
    def test_pression_v1_score_range(self):
        """GET /api/v3/engines/PRESSION-V1/score returns score 0-100"""
        params = {"lat": 46.8139, "lng": -71.2080, "species": "CHEVREUIL", "month": 10}
        response = requests.get(f"{BASE_URL}/api/v3/engines/PRESSION-V1/score", params=params)
        assert response.status_code == 200
        
        data = response.json()
        assert 0 <= data["score"] <= 100, f"PRESSION-V1 score {data['score']} not in 0-100 range"
        print(f"PASS: PRESSION-V1 score={data['score']} is in 0-100 range")
    
    def test_corridors_species_resolution(self):
        """GET /api/v3/engines/CORRIDORS-V10/score?species=orignal resolves to ORIGNAL"""
        params = {"lat": 46.8139, "lng": -71.2080, "species": "orignal", "month": 10}
        response = requests.get(f"{BASE_URL}/api/v3/engines/CORRIDORS-V10/score", params=params)
        assert response.status_code == 200
        
        data = response.json()
        assert data["species"] == "ORIGNAL", f"Expected species ORIGNAL, got {data['species']}"
        print(f"PASS: species=orignal correctly resolved to {data['species']}")
    
    def test_nonexistent_engine_returns_error(self):
        """GET /api/v3/engines/NONEXISTENT/score returns error with available engines list"""
        params = {"lat": 46.8139, "lng": -71.2080, "species": "CHEVREUIL", "month": 10}
        response = requests.get(f"{BASE_URL}/api/v3/engines/NONEXISTENT/score", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "error" in data, "Expected error field in response"
        assert "available" in data, "Expected available engines list in error response"
        assert len(data["available"]) >= 5, "Expected at least 5 available engines"
        print(f"PASS: NONEXISTENT engine returns error with {len(data['available'])} available engines")


class TestBCE4XValidationEndpoint:
    """BCE-4X and STEEVE-MAX validation endpoint tests"""
    
    def test_validate_endpoint_structure(self):
        """GET /api/v3/engines/validate returns overall_compliant with bce4x and steeve_max sub-reports"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/validate")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Check overall structure
        assert "overall_compliant" in data, "Missing overall_compliant field"
        assert isinstance(data["overall_compliant"], bool), "overall_compliant must be boolean"
        
        # Check bce4x sub-report
        assert "bce4x" in data, "Missing bce4x sub-report"
        bce4x = data["bce4x"]
        assert "passed" in bce4x, "bce4x missing passed count"
        assert "total" in bce4x, "bce4x missing total tests count"
        assert "compliant" in bce4x, "bce4x missing compliant field"
        
        # Check steeve_max sub-report
        assert "steeve_max" in data, "Missing steeve_max sub-report"
        sm = data["steeve_max"]
        assert "passed" in sm, "steeve_max missing passed count"
        assert "total" in sm, "steeve_max missing total tests count"
        assert "compliant" in sm, "steeve_max missing compliant field"
        
        print(f"PASS: Validate endpoint returns overall_compliant={data['overall_compliant']}")
        print(f"      BCE4X: {bce4x['passed']}/{bce4x['total']} tests passed, compliant={bce4x['compliant']}")
        print(f"      STEEVE-MAX: {sm['passed']}/{sm['total']} tests passed, compliant={sm['compliant']}")
    
    def test_validate_bce4x_passes(self):
        """BCE-4X validation should pass with all engine registry rules verified"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/validate")
        assert response.status_code == 200
        
        data = response.json()
        assert data["bce4x"]["compliant"] == True, "BCE4X validation should pass"
        assert data["bce4x"]["passed"] >= 15, f"Expected at least 15 BCE4X tests passed, got {data['bce4x']['passed']}"
        print(f"PASS: BCE4X compliant with {data['bce4x']['passed']} tests passed")
    
    def test_validate_steeve_max_passes(self):
        """STEEVE-MAX validation should pass with architecture rules verified"""
        response = requests.get(f"{BASE_URL}/api/v3/engines/validate")
        assert response.status_code == 200
        
        data = response.json()
        assert data["steeve_max"]["compliant"] == True, "STEEVE-MAX validation should pass"
        print(f"PASS: STEEVE-MAX compliant with {data['steeve_max']['passed']} tests passed")


class TestM1RegressionChecks:
    """M1 regression checks — ensure score-point and score-grid still work with exclude param"""
    
    def test_score_point_with_exclude(self):
        """GET /api/v3/engines/score-point with exclude param still works"""
        params = {
            "lat": 46.8139, "lng": -71.2080,
            "species": "CHEVREUIL", "month": 10,
            "exclude": "CORRIDORS-V10"
        }
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-point", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "CORRIDORS-V10" not in data["components"], "CORRIDORS-V10 should be excluded"
        assert "CORRIDORS-V10" in data["tracability"]["engines_excluded"], "CORRIDORS-V10 should be in excluded list"
        print(f"PASS: score-point exclude param works, score={data['score']}")
    
    def test_score_grid_still_works(self):
        """GET /api/v3/engines/score-grid still works (M1 regression check)"""
        params = {"lat": 46.8139, "lng": -71.2080, "species": "CHEVREUIL", "month": 10, "grid_size": 5}
        response = requests.get(f"{BASE_URL}/api/v3/engines/score-grid", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "points" in data, "Missing points in grid response"
        assert len(data["points"]) == 25, f"Expected 25 points (5x5 grid), got {len(data['points'])}"
        print(f"PASS: score-grid returns {len(data['points'])} points, avg={data.get('score_avg')}")


class TestNonRegressionV1V10:
    """Non-regression tests for V1/V10 legacy endpoints"""
    
    def test_alimentation_v1_point(self):
        """NON-REGRESSION: GET /api/v1/alimentation/point works"""
        params = {"lat": 46.8139, "lng": -71.2080, "species": "CERF", "month": 10}
        response = requests.get(f"{BASE_URL}/api/v1/alimentation/point", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Legacy V1 endpoint returns score_alimentation instead of score
        assert "score_alimentation" in data or "score" in data, "Missing score in alimentation/point response"
        score = data.get("score_alimentation") or data.get("score")
        print(f"PASS: V1 alimentation/point returns score_alimentation={score}")
    
    def test_repos_v1_point(self):
        """NON-REGRESSION: GET /api/v1/repos/point works"""
        params = {"lat": 46.8139, "lng": -71.2080, "species": "CERF", "month": 10}
        response = requests.get(f"{BASE_URL}/api/v1/repos/point", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Legacy V1 endpoint returns score_repos instead of score
        assert "score_repos" in data or "score" in data, "Missing score in repos/point response"
        score = data.get("score_repos") or data.get("score")
        print(f"PASS: V1 repos/point returns score_repos={score}")
    
    def test_score_consolide_point(self):
        """NON-REGRESSION: GET /api/v1/score-consolide/point works"""
        params = {"lat": 46.8139, "lng": -71.2080, "species": "CERF", "month": 10}
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/point", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "score" in data, "Missing score in score-consolide/point response"
        print(f"PASS: V1 score-consolide/point returns score={data.get('score')}")
    
    def test_score_consolide_heatmap(self):
        """NON-REGRESSION: GET /api/v1/score-consolide/heatmap works"""
        params = {"lat": 46.8139, "lng": -71.2080, "species": "CERF", "month": 10, "grid_size": 5}
        response = requests.get(f"{BASE_URL}/api/v1/score-consolide/heatmap", params=params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "points" in data or "grid" in data, "Missing points/grid in heatmap response"
        print(f"PASS: V1 score-consolide/heatmap works")


class TestConfigFiles:
    """Config file verification tests"""
    
    def test_bce4x_toml_species_canonical(self):
        """BCE4X.toml exists with species.canonical = CHEVREUIL,ORIGNAL,OURS,DINDON,WAPITI"""
        import tomllib
        from pathlib import Path
        
        toml_path = Path("/app/bionic/BCE4X.toml")
        assert toml_path.exists(), "BCE4X.toml not found at /app/bionic/BCE4X.toml"
        
        with open(toml_path, "rb") as f:
            config = tomllib.load(f)
        
        assert "species" in config, "BCE4X.toml missing [species] section"
        assert "canonical" in config["species"], "BCE4X.toml missing species.canonical"
        
        expected = ["CHEVREUIL", "ORIGNAL", "OURS", "DINDON", "WAPITI"]
        actual = config["species"]["canonical"]
        assert actual == expected, f"Expected {expected}, got {actual}"
        print(f"PASS: BCE4X.toml species.canonical = {actual}")
    
    def test_steevemax_toml_exists(self):
        """STEEVEMAX.toml exists at /app/bionic/STEEVEMAX.toml"""
        from pathlib import Path
        
        toml_path = Path("/app/bionic/STEEVEMAX.toml")
        assert toml_path.exists(), "STEEVEMAX.toml not found at /app/bionic/STEEVEMAX.toml"
        
        with open(toml_path, "rb") as f:
            import tomllib
            config = tomllib.load(f)
        
        assert "metadata" in config, "STEEVEMAX.toml missing [metadata] section"
        assert config["metadata"]["norm"] == "STEEVE-MAX"
        print(f"PASS: STEEVEMAX.toml exists with norm=STEEVE-MAX, version={config['metadata'].get('version')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
