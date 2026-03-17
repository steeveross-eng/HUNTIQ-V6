"""
BIONIC V3 - Score Consolidé & Plan de Match Testing
=====================================================
Tests for:
- Plan de Match Steeve-MAX v1 document (MD + PDF)
- Score consolidé API (/api/v1/score-consolide/point)
- Heatmap API (/api/v1/score-consolide/heatmap)
- Multi-species support (CERF, ORIGNAL, OURS, DINDON, WAPITI)
- Audit file listing
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test coordinates - Quebec region
TEST_LAT = 46.8
TEST_LNG = -71.2

# All 5 species to test
SPECIES_LIST = ["CERF", "ORIGNAL", "OURS", "DINDON", "WAPITI"]


class TestPlanDeMatchDocument:
    """Tests for Plan de Match Steeve-MAX v1 document endpoints"""

    def test_audit_list_contains_plan_de_match_files(self):
        """GET /api/audit/list returns list with Plan de Match files"""
        response = requests.get(f"{BASE_URL}/api/audit/list")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "audit_files" in data
        assert "total" in data
        
        # Check total count - should have 6 files now
        assert data["total"] >= 6, f"Expected at least 6 audit files, got {data['total']}"
        
        filenames = [f["filename"] for f in data["audit_files"]]
        assert "PLAN_DE_MATCH_STEEVE_MAX_v1.md" in filenames, f"MD file not found in {filenames}"
        assert "PLAN_DE_MATCH_STEEVE_MAX_v1.pdf" in filenames, f"PDF file not found in {filenames}"
        print(f"PASS: Found {data['total']} audit files including Plan de Match")

    def test_plan_de_match_md_returns_200(self):
        """GET /api/audit/PLAN_DE_MATCH_STEEVE_MAX_v1.md returns 200"""
        response = requests.get(f"{BASE_URL}/api/audit/PLAN_DE_MATCH_STEEVE_MAX_v1.md")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        content = response.text
        assert len(content) > 1000, f"File too small: {len(content)} bytes"
        assert "PLAN DE MATCH STEEVE-MAX" in content, "Missing title"
        assert "BCE-4X" in content, "Missing BCE-4X reference"
        assert "Steeve-MAX" in content, "Missing Steeve-MAX reference"
        print(f"PASS: MD file returned with {len(content)} bytes")

    def test_plan_de_match_md_contains_9_definitions(self):
        """Plan de Match MD contains 9 ecological definitions"""
        response = requests.get(f"{BASE_URL}/api/audit/PLAN_DE_MATCH_STEEVE_MAX_v1.md")
        assert response.status_code == 200
        
        content = response.text
        # Check for key definitions
        definitions = [
            "Habitat optimal",
            "Zones de rut",
            "Corridors fauniques",
            "Hydrographie",
            "Pentes",
            "Orientation",
            "Ensoleillement",
            "Affûts potentiels",
            "Trajets de chasse"
        ]
        
        found = 0
        for defn in definitions:
            if defn in content:
                found += 1
                print(f"  Found: {defn}")
        
        assert found >= 9, f"Expected 9 definitions, found {found}"
        print(f"PASS: Found {found}/9 ecological definitions")

    def test_plan_de_match_pdf_returns_200(self):
        """GET /api/audit/PLAN_DE_MATCH_STEEVE_MAX_v1.pdf returns 200 with valid PDF"""
        response = requests.get(f"{BASE_URL}/api/audit/PLAN_DE_MATCH_STEEVE_MAX_v1.pdf")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Check PDF header
        content = response.content
        assert len(content) > 1000, f"PDF too small: {len(content)} bytes"
        assert content[:4] == b'%PDF', f"Invalid PDF header: {content[:10]}"
        print(f"PASS: PDF file returned with {len(content)} bytes")

    def test_plan_de_match_content_type_headers(self):
        """Verify correct content-type headers for Plan de Match files"""
        # MD file
        response_md = requests.get(f"{BASE_URL}/api/audit/PLAN_DE_MATCH_STEEVE_MAX_v1.md")
        assert "text/markdown" in response_md.headers.get("content-type", ""), \
            f"Expected text/markdown, got {response_md.headers.get('content-type')}"
        
        # PDF file
        response_pdf = requests.get(f"{BASE_URL}/api/audit/PLAN_DE_MATCH_STEEVE_MAX_v1.pdf")
        assert "application/pdf" in response_pdf.headers.get("content-type", ""), \
            f"Expected application/pdf, got {response_pdf.headers.get('content-type')}"
        print("PASS: Content-type headers are correct")


class TestScoreConsolidePoint:
    """Tests for /api/v1/score-consolide/point endpoint"""

    def test_score_consolide_point_returns_200(self):
        """GET /api/v1/score-consolide/point returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/v1/score-consolide/point",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "species": "CERF", "month": 10}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "score" in data
        assert "classe" in data
        assert "label" in data
        assert "color" in data
        print(f"PASS: Score consolidé returned: {data['score']} ({data['label']})")

    def test_score_in_valid_range(self):
        """Score is within [0, 100] range"""
        response = requests.get(
            f"{BASE_URL}/api/v1/score-consolide/point",
            params={"lat": TEST_LAT, "lng": TEST_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 0 <= data["score"] <= 100, f"Score {data['score']} out of range [0, 100]"
        print(f"PASS: Score {data['score']} is within valid range")

    def test_score_has_components(self):
        """Score includes alimentation, repos, pression components"""
        response = requests.get(
            f"{BASE_URL}/api/v1/score-consolide/point",
            params={"lat": TEST_LAT, "lng": TEST_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "components" in data, "Missing components field"
        
        components = data["components"]
        assert "alimentation" in components, "Missing alimentation component"
        assert "repos" in components, "Missing repos component"
        assert "pression" in components, "Missing pression component"
        
        # Verify component scores are valid
        for comp, score in components.items():
            assert 0 <= score <= 100, f"Component {comp} score {score} out of range"
        
        print(f"PASS: Components found: {list(components.keys())}")

    def test_score_has_weights(self):
        """Score includes normalized weights"""
        response = requests.get(
            f"{BASE_URL}/api/v1/score-consolide/point",
            params={"lat": TEST_LAT, "lng": TEST_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "weights" in data, "Missing weights field"
        
        weights = data["weights"]
        assert len(weights) >= 3, f"Expected at least 3 weights, got {len(weights)}"
        
        # Verify weights sum to ~1.0
        total_weight = sum(weights.values())
        assert abs(total_weight - 1.0) < 0.01, f"Weights sum to {total_weight}, expected 1.0"
        
        print(f"PASS: Weights: {weights}, sum={total_weight:.3f}")

    def test_score_has_tracability(self):
        """Score includes tracability with engines_active and engines_pending"""
        response = requests.get(
            f"{BASE_URL}/api/v1/score-consolide/point",
            params={"lat": TEST_LAT, "lng": TEST_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "tracability" in data, "Missing tracability field"
        
        trace = data["tracability"]
        assert "engines_active" in trace, "Missing engines_active"
        assert "engines_pending" in trace, "Missing engines_pending"
        
        assert "alimentation" in trace["engines_active"], "alimentation not in active engines"
        assert "repos" in trace["engines_active"], "repos not in active engines"
        
        assert "corridors_v10" in trace["engines_pending"] or "habitat_v1" in trace["engines_pending"], \
            f"Expected pending engines, got {trace['engines_pending']}"
        
        print(f"PASS: Active engines: {trace['engines_active']}, Pending: {trace['engines_pending']}")

    def test_score_classification_labels(self):
        """Score classification uses correct labels"""
        response = requests.get(
            f"{BASE_URL}/api/v1/score-consolide/point",
            params={"lat": TEST_LAT, "lng": TEST_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        valid_classes = ["OPTIMAL", "BON", "MODERE", "FAIBLE"]
        valid_labels = ["Optimal", "Bon", "Modere", "Faible"]
        
        assert data["classe"] in valid_classes, f"Invalid classe: {data['classe']}"
        assert data["label"] in valid_labels, f"Invalid label: {data['label']}"
        assert data["color"].startswith("#"), f"Invalid color format: {data['color']}"
        
        print(f"PASS: Classification: {data['classe']} / {data['label']} / {data['color']}")


class TestScoreConsolideMultiSpecies:
    """Test score consolidé for all 5 species"""

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_score_consolide_for_species(self, species):
        """GET /api/v1/score-consolide/point works for each species"""
        response = requests.get(
            f"{BASE_URL}/api/v1/score-consolide/point",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "species": species, "month": 10}
        )
        assert response.status_code == 200, f"Failed for species {species}: {response.status_code}"
        
        data = response.json()
        assert "score" in data
        assert data.get("species") == species, f"Expected species {species}, got {data.get('species')}"
        assert 0 <= data["score"] <= 100
        
        print(f"PASS: {species} score: {data['score']} ({data['label']})")


class TestHeatmapGrid:
    """Tests for /api/v1/score-consolide/heatmap endpoint"""

    def test_heatmap_returns_200(self):
        """GET /api/v1/score-consolide/heatmap returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/v1/score-consolide/heatmap",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "species": "CERF", "month": 10}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "points" in data
        assert "center" in data
        print(f"PASS: Heatmap returned with {len(data.get('points', []))} points")

    def test_heatmap_grid_size_default(self):
        """Heatmap default grid_size is 20 (400 points)"""
        response = requests.get(
            f"{BASE_URL}/api/v1/score-consolide/heatmap",
            params={"lat": TEST_LAT, "lng": TEST_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("grid_size") == 20, f"Expected grid_size 20, got {data.get('grid_size')}"
        assert data.get("total_points") == 400, f"Expected 400 points, got {data.get('total_points')}"
        
        print(f"PASS: Grid size {data['grid_size']}, total points {data['total_points']}")

    def test_heatmap_points_have_scores(self):
        """Each heatmap point has lat, lng, score, classe, color"""
        response = requests.get(
            f"{BASE_URL}/api/v1/score-consolide/heatmap",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "grid_size": 5}
        )
        assert response.status_code == 200
        
        data = response.json()
        points = data.get("points", [])
        assert len(points) > 0, "No points returned"
        
        # Check first point structure
        point = points[0]
        assert "lat" in point, "Missing lat"
        assert "lng" in point, "Missing lng"
        assert "score" in point, "Missing score"
        assert "classe" in point, "Missing classe"
        assert "color" in point, "Missing color"
        
        # Verify score is valid
        assert 0 <= point["score"] <= 100, f"Invalid score: {point['score']}"
        
        print(f"PASS: Points have correct structure. Sample: score={point['score']}")

    def test_heatmap_has_statistics(self):
        """Heatmap includes score_avg, score_min, score_max, overall_classe"""
        response = requests.get(
            f"{BASE_URL}/api/v1/score-consolide/heatmap",
            params={"lat": TEST_LAT, "lng": TEST_LNG}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "score_avg" in data, "Missing score_avg"
        assert "score_min" in data, "Missing score_min"
        assert "score_max" in data, "Missing score_max"
        assert "overall_classe" in data, "Missing overall_classe"
        assert "overall_label" in data, "Missing overall_label"
        
        # Verify min <= avg <= max
        assert data["score_min"] <= data["score_avg"] <= data["score_max"], \
            f"Invalid stats: min={data['score_min']}, avg={data['score_avg']}, max={data['score_max']}"
        
        print(f"PASS: Stats - min={data['score_min']}, avg={data['score_avg']}, max={data['score_max']}")

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_heatmap_works_for_species(self, species):
        """GET /api/v1/score-consolide/heatmap works for all 5 species"""
        response = requests.get(
            f"{BASE_URL}/api/v1/score-consolide/heatmap",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "species": species, "grid_size": 5}
        )
        assert response.status_code == 200, f"Failed for species {species}: {response.status_code}"
        
        data = response.json()
        assert data.get("species") == species, f"Expected species {species}, got {data.get('species')}"
        assert len(data.get("points", [])) > 0, f"No points for {species}"
        
        print(f"PASS: {species} heatmap - {len(data['points'])} points, avg={data.get('score_avg')}")


class TestALIMENTATIONV1Regression:
    """Regression tests for ALIMENTATION-V1 (no breaking changes)"""

    def test_alimentation_profiles_still_works(self):
        """GET /api/v1/alimentation/profiles returns 5 species"""
        response = requests.get(f"{BASE_URL}/api/v1/alimentation/profiles")
        assert response.status_code == 200
        
        data = response.json()
        assert "profiles" in data
        assert len(data["profiles"]) == 5
        
        species_ids = [p["id"] for p in data["profiles"]]
        for sp in SPECIES_LIST:
            assert sp in species_ids, f"Missing species {sp}"
        
        print(f"PASS: ALIMENTATION-V1 profiles: {species_ids}")

    def test_alimentation_point_still_works(self):
        """GET /api/v1/alimentation/point returns valid score"""
        response = requests.get(
            f"{BASE_URL}/api/v1/alimentation/point",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "species": "CERF", "month": 10}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "score_alimentation" in data
        assert 0 <= data["score_alimentation"] <= 100
        
        print(f"PASS: ALIMENTATION-V1 point score: {data['score_alimentation']}")


class TestREPOSV1Regression:
    """Regression tests for REPOS-V1 (no breaking changes)"""

    def test_repos_profiles_still_works(self):
        """GET /api/v1/repos/profiles returns 5 species"""
        response = requests.get(f"{BASE_URL}/api/v1/repos/profiles")
        assert response.status_code == 200
        
        data = response.json()
        assert "profiles" in data
        assert len(data["profiles"]) == 5
        
        species_ids = [p["id"] for p in data["profiles"]]
        for sp in SPECIES_LIST:
            assert sp in species_ids, f"Missing species {sp}"
        
        print(f"PASS: REPOS-V1 profiles: {species_ids}")

    def test_repos_point_still_works(self):
        """GET /api/v1/repos/point returns valid score"""
        response = requests.get(
            f"{BASE_URL}/api/v1/repos/point",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "species": "CERF", "month": 10}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "score_repos" in data
        assert 0 <= data["score_repos"] <= 100
        
        print(f"PASS: REPOS-V1 point score: {data['score_repos']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
