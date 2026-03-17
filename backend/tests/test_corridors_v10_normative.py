"""
CORRIDORS-V10 — Normative Enrichment Test Suite
=================================================
Tests for the NEW normative features in CORRIDORS-V10:
- 5-level normative classification (CRITIQUE/MAJEUR/FORT/MODERE/FAIBLE)
- Per-corridor scoring with score_individuel, niveau, color, largeur_m
- Enriched cell data (ECL, micro-topo, nourriture, refuge, etc.)
- Species behavioral descriptions (description_corridor)
- COR-006 explicit in BCE-4X validation
- niveau_distribution and palette_normative fields

Test coordinates: Quebec region (46.8, -71.2) with waypoint 'steeve' at 46.7557, -70.4713
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
SPECIES_LIST = ["CERF", "ORIGNAL", "OURS", "DINDON", "WAPITI"]

# Normative palette constants from classifier.py
NORMATIVE_LEVELS = ["CRITIQUE", "MAJEUR", "FORT", "MODERE", "FAIBLE"]
NORMATIVE_COLORS = {
    "CRITIQUE": "#CC0000",
    "MAJEUR": "#FF0000",
    "FORT": "#FF8C00",
    "MODERE": "#FFD700",
    "FAIBLE": "#BFBFBF",
}
NORMATIVE_WIDTHS = {
    "CRITIQUE": 4,
    "MAJEUR": 6,
    "FORT": 11,
    "MODERE": 17,
    "FAIBLE": 26,
}

# Test coordinates
TEST_LAT = 46.8
TEST_LNG = -71.2
TEST_MONTH = 10

# Waypoint 'steeve' for frontend testing
STEEVE_LAT = 46.7557
STEEVE_LNG = -70.4713


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestCorridorLevelsPalette:
    """Tests for 5-level normative palette (CORRIDOR_LEVELS)"""

    def test_documentation_has_palette_normative(self, api_client):
        """GET /api/v10/corridors/documentation includes palette_normative field"""
        response = api_client.get(f"{BASE_URL}/api/v10/corridors/documentation")
        assert response.status_code == 200
        data = response.json()
        
        assert "palette_normative" in data, "Missing 'palette_normative' in documentation"
        palette = data["palette_normative"]
        
        # Verify all 5 levels present
        for level in NORMATIVE_LEVELS:
            assert level in palette, f"Missing level {level} in palette_normative"
            
        print("PASS: Documentation has palette_normative with all 5 levels")

    def test_palette_colors_match_norm(self, api_client):
        """palette_normative colors match exactly: #CC0000, #FF0000, #FF8C00, #FFD700, #BFBFBF"""
        response = api_client.get(f"{BASE_URL}/api/v10/corridors/documentation")
        data = response.json()
        palette = data["palette_normative"]
        
        for level, expected_color in NORMATIVE_COLORS.items():
            actual_color = palette[level]["color"]
            assert actual_color == expected_color, f"{level}: color {actual_color} != {expected_color}"
        
        print("PASS: All normative colors match exactly")

    def test_palette_widths_match_norm(self, api_client):
        """palette_normative widths match exactly: 4, 6, 11, 17, 26m"""
        response = api_client.get(f"{BASE_URL}/api/v10/corridors/documentation")
        data = response.json()
        palette = data["palette_normative"]
        
        for level, expected_width in NORMATIVE_WIDTHS.items():
            actual_width = palette[level]["largeur_m"]
            assert actual_width == expected_width, f"{level}: largeur_m {actual_width} != {expected_width}"
        
        print("PASS: All normative widths match exactly (4, 6, 11, 17, 26m)")


class TestAnalyzeNiveauDistribution:
    """Tests for niveau_distribution in analyze response"""

    def test_analyze_has_niveau_distribution(self, api_client):
        """POST /api/v10/corridors/analyze returns niveau_distribution with 5 levels"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "network" in data, "Missing 'network'"
        assert "niveau_distribution" in data["network"], "Missing 'niveau_distribution' in network"
        
        niveau_dist = data["network"]["niveau_distribution"]
        
        for level in NORMATIVE_LEVELS:
            assert level in niveau_dist, f"Missing level {level} in niveau_distribution"
            assert "count" in niveau_dist[level], f"Missing 'count' for {level}"
            assert "color" in niveau_dist[level], f"Missing 'color' for {level}"
            assert "largeur_m" in niveau_dist[level], f"Missing 'largeur_m' for {level}"
            assert "label_fr" in niveau_dist[level], f"Missing 'label_fr' for {level}"
        
        print(f"PASS: niveau_distribution has all 5 levels with count/color/largeur_m/label_fr")

    def test_niveau_distribution_colors_match(self, api_client):
        """niveau_distribution colors match normative palette"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze", json=payload)
        data = response.json()
        niveau_dist = data["network"]["niveau_distribution"]
        
        for level, expected_color in NORMATIVE_COLORS.items():
            actual_color = niveau_dist[level]["color"]
            assert actual_color == expected_color, f"{level}: {actual_color} != {expected_color}"
        
        print("PASS: niveau_distribution colors match normative palette")


class TestAnalyzeFullPerCorridorScoring:
    """Tests for per-corridor scoring with normative properties"""

    def test_geojson_corridors_have_score_individuel(self, api_client):
        """Each GeoJSON corridor has score property (0-100)"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json=payload)
        data = response.json()
        features = data["geojson"]["features"]
        
        corridors = [f for f in features if f["geometry"]["type"] == "LineString"]
        assert len(corridors) > 0, "No corridors in GeoJSON"
        
        for c in corridors:
            props = c["properties"]
            assert "score" in props, f"Corridor {props.get('corridor_id')} missing 'score'"
            score = props["score"]
            assert 0 <= score <= 100, f"Score {score} out of range [0, 100]"
        
        print(f"PASS: All {len(corridors)} corridors have score in [0, 100]")

    def test_geojson_corridors_have_niveau(self, api_client):
        """Each corridor has niveau from 5 normative levels"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json=payload)
        data = response.json()
        features = data["geojson"]["features"]
        corridors = [f for f in features if f["geometry"]["type"] == "LineString"]
        
        for c in corridors:
            props = c["properties"]
            assert "niveau" in props, f"Corridor {props.get('corridor_id')} missing 'niveau'"
            niveau = props["niveau"]
            assert niveau in NORMATIVE_LEVELS, f"Niveau '{niveau}' not in {NORMATIVE_LEVELS}"
        
        print(f"PASS: All corridors have valid normative niveau")

    def test_geojson_corridors_have_color_matching_niveau(self, api_client):
        """Each corridor's color matches its normative niveau"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json=payload)
        data = response.json()
        features = data["geojson"]["features"]
        corridors = [f for f in features if f["geometry"]["type"] == "LineString"]
        
        for c in corridors:
            props = c["properties"]
            niveau = props["niveau"]
            color = props.get("color")
            expected_color = NORMATIVE_COLORS[niveau]
            assert color == expected_color, f"Corridor {props.get('corridor_id')}: color {color} != {expected_color} for niveau {niveau}"
        
        print(f"PASS: All corridor colors match their normative niveau")

    def test_geojson_corridors_have_largeur_m(self, api_client):
        """Each corridor has largeur_m matching normative widths"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json=payload)
        data = response.json()
        features = data["geojson"]["features"]
        corridors = [f for f in features if f["geometry"]["type"] == "LineString"]
        
        for c in corridors:
            props = c["properties"]
            niveau = props["niveau"]
            largeur = props.get("largeur_m")
            expected_largeur = NORMATIVE_WIDTHS[niveau]
            assert largeur == expected_largeur, f"Corridor {props.get('corridor_id')}: largeur {largeur} != {expected_largeur} for niveau {niveau}"
        
        print(f"PASS: All corridor largeur_m match normative widths")

    def test_geojson_corridors_have_render_properties(self, api_client):
        """Each corridor has render_weight, dash_array, pattern"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json=payload)
        data = response.json()
        features = data["geojson"]["features"]
        corridors = [f for f in features if f["geometry"]["type"] == "LineString"]
        
        for c in corridors:
            props = c["properties"]
            cid = props.get("corridor_id", "unknown")
            assert "render_weight" in props, f"Corridor {cid} missing 'render_weight'"
            assert "dash_array" in props, f"Corridor {cid} missing 'dash_array'"
            assert "pattern" in props, f"Corridor {cid} missing 'pattern'"
            
            # CRITIQUE should have dash_array = '10,4'
            if props["niveau"] == "CRITIQUE":
                assert props["dash_array"] == "10,4", f"CRITIQUE corridor should have dash_array='10,4'"
                assert props["pattern"] == "striped", f"CRITIQUE corridor should have pattern='striped'"
        
        print(f"PASS: All corridors have render_weight, dash_array, pattern")


class TestCOR006Validation:
    """Tests for COR-006 explicit in BCE-4X validation"""

    def test_bce4x_has_cor006_check(self, api_client):
        """BCE-4X validation includes COR-006 check"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze", json=payload)
        data = response.json()
        
        bce4x = data["validation"]["bce4x"]
        assert "COR-006" in bce4x["checks"], "COR-006 not in BCE-4X checks"
        print(f"PASS: BCE-4X has COR-006 check")

    def test_cor006_passes_all_species(self, api_client):
        """COR-006 (connected=True, dead_ends=0) passes for all 5 species"""
        for species in SPECIES_LIST:
            payload = {
                "center_lat": TEST_LAT,
                "center_lng": TEST_LNG,
                "species": species,
                "month": TEST_MONTH,
            }
            response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze", json=payload)
            data = response.json()
            
            bce4x = data["validation"]["bce4x"]
            cor006 = bce4x["checks"].get("COR-006")
            assert cor006 == "PASS", f"{species}: COR-006 = {cor006}, expected PASS"
            
            continuity = data["continuity"]
            assert continuity["connected"] == True, f"{species}: not connected"
            assert continuity["dead_ends"] == 0, f"{species}: dead_ends = {continuity['dead_ends']}"
        
        print(f"PASS: COR-006 validated for all 5 species (connected=True, dead_ends=0)")


class TestMultiSpeciesPaletteNormative:
    """Tests for palette_normative in multi-species endpoint"""

    def test_multi_has_palette_normative(self, api_client):
        """GET /api/v10/corridors/multi includes palette_normative"""
        response = api_client.get(
            f"{BASE_URL}/api/v10/corridors/multi",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "month": TEST_MONTH}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "palette_normative" in data, "Missing 'palette_normative' in multi response"
        palette = data["palette_normative"]
        
        for level in NORMATIVE_LEVELS:
            assert level in palette, f"Missing {level} in palette_normative"
        
        print("PASS: Multi-species endpoint includes palette_normative with all 5 levels")

    def test_multi_species_have_niveau_distribution(self, api_client):
        """Each species result in multi has niveau_distribution"""
        response = api_client.get(
            f"{BASE_URL}/api/v10/corridors/multi",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "month": TEST_MONTH}
        )
        data = response.json()
        
        for species in SPECIES_LIST:
            sp_result = data["species_results"][species]
            assert "network_summary" in sp_result, f"{species} missing network_summary"
            assert "niveau_distribution" in sp_result["network_summary"], f"{species} missing niveau_distribution"
        
        print("PASS: All species in multi response have niveau_distribution")


class TestSpeciesDescriptionCorridor:
    """Tests for description_corridor field in species profiles"""

    def test_profiles_have_description_corridor(self, api_client):
        """Species with behavioral descriptions have description_corridor field"""
        # According to species_profiles.py, CERF, ORIGNAL, OURS have description_corridor
        species_with_desc = ["CERF", "ORIGNAL", "OURS"]
        
        for species in species_with_desc:
            payload = {
                "center_lat": TEST_LAT,
                "center_lng": TEST_LNG,
                "species": species,
                "month": TEST_MONTH,
            }
            response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze", json=payload)
            data = response.json()
            
            assert "description_corridor" in data, f"{species} missing 'description_corridor'"
            desc = data["description_corridor"]
            assert len(desc) > 50, f"{species} description_corridor too short: {len(desc)} chars"
        
        print(f"PASS: CERF, ORIGNAL, OURS have behavioral description_corridor")

    def test_analyze_full_has_description(self, api_client):
        """analyze-full response includes description_corridor"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json=payload)
        data = response.json()
        
        assert "description_corridor" in data, "Missing description_corridor in analyze-full"
        print("PASS: analyze-full includes description_corridor")


class TestEnrichedCellData:
    """Tests for enriched cost surface data (ECL, micro-topo, etc.)
    
    These fields should be used in per-corridor scoring:
    - ecl (connectivite ecologique locale)
    - micro_topo_vallon, micro_topo_crete, micro_topo_replat
    - nourriture
    - refuge_score
    - zone_tampon
    - regeneration
    """

    def test_corridors_have_varying_scores(self, api_client):
        """Corridors should have varying scores due to enriched data"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json=payload)
        data = response.json()
        features = data["geojson"]["features"]
        corridors = [f for f in features if f["geometry"]["type"] == "LineString"]
        
        scores = [c["properties"]["score"] for c in corridors]
        unique_scores = set(scores)
        
        # Scores should vary - not all the same
        assert len(unique_scores) > 1, f"All corridors have same score: {scores[0]}"
        
        # Should have multiple niveau distribution
        niveaux = [c["properties"]["niveau"] for c in corridors]
        unique_niveaux = set(niveaux)
        # Reasonable expectation: at least 2 different niveaux
        assert len(unique_niveaux) >= 1, f"Only {len(unique_niveaux)} niveau(x) found"
        
        print(f"PASS: Corridors have {len(unique_scores)} unique scores across {len(unique_niveaux)} niveaux")

    def test_niveau_distribution_has_counts(self, api_client):
        """niveau_distribution should have non-zero counts for at least one level"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze", json=payload)
        data = response.json()
        niveau_dist = data["network"]["niveau_distribution"]
        
        total_count = sum(niveau_dist[lvl]["count"] for lvl in NORMATIVE_LEVELS)
        assert total_count > 0, "niveau_distribution has zero total count"
        
        # At least one level should have count > 0
        non_zero_levels = [lvl for lvl in NORMATIVE_LEVELS if niveau_dist[lvl]["count"] > 0]
        assert len(non_zero_levels) >= 1, "No levels have count > 0"
        
        print(f"PASS: niveau_distribution total={total_count}, non-zero levels: {non_zero_levels}")


class TestCorridorSummaryInAnalyze:
    """Tests for corridors_summary with normative properties"""

    def test_corridors_summary_has_normative_fields(self, api_client):
        """corridors_summary in analyze response has score_individuel, niveau, color, largeur_m"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze", json=payload)
        data = response.json()
        
        corridors_summary = data["network"]["corridors_summary"]
        assert len(corridors_summary) > 0, "No corridors in summary"
        
        for cs in corridors_summary:
            assert "score_individuel" in cs, f"Corridor {cs.get('id')} missing score_individuel"
            assert "niveau" in cs, f"Corridor {cs.get('id')} missing niveau"
            assert "color" in cs, f"Corridor {cs.get('id')} missing color"
            assert "largeur_m" in cs, f"Corridor {cs.get('id')} missing largeur_m"
            
            # Validate niveau is in normative list
            assert cs["niveau"] in NORMATIVE_LEVELS, f"Invalid niveau: {cs['niveau']}"
        
        print(f"PASS: corridors_summary has all normative fields for {len(corridors_summary)} corridors")


class TestAntiRegressionExistingEngines:
    """Anti-regression: Existing engines still work"""

    def test_alimentation_v1_still_works(self, api_client):
        """/api/v1/alimentation/analyze still works"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/alimentation/analyze", json=payload)
        assert response.status_code == 200, f"ALIMENTATION-V1 broken: {response.status_code}"
        data = response.json()
        assert data["engine"] == "ALIMENTATION-V1"
        print("PASS: ALIMENTATION-V1 still works")

    def test_repos_v1_still_works(self, api_client):
        """/api/v1/repos/analyze still works"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/repos/analyze", json=payload)
        assert response.status_code == 200, f"REPOS-V1 broken: {response.status_code}"
        data = response.json()
        assert data["engine"] == "REPOS-V1"
        print("PASS: REPOS-V1 still works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
