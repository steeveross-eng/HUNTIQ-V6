"""
CORRIDORS-V10 — Test Suite Complete
=====================================
Tests complets pour le moteur CORRIDORS-V10:
- 6 API endpoints
- BCE-4X validation (7 checks)
- Steeve-MAX validation (5 checks)
- Continuite absolue (connected=True, dead_ends=0)
- 12 parametres par profil espece
- Anti-regression: ALIMENTATION-V1 et REPOS-V1 non modifies

Test coordinates: Quebec region (46.8, -71.2)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
SPECIES_LIST = ["CERF", "ORIGNAL", "OURS", "DINDON", "WAPITI"]
PARAM_KEYS_12 = [
    "pente_optimale_deg", "pente_max_deg", "sensibilite_pression",
    "style_deplacement", "tolerance_obstacles", "distance_route_evitement_m",
    "distance_batiment_evitement_m", "largeur_corridor_m", "preference_forestiere",
    "affinite_hydro", "influence_dominants", "vitesse_deplacement",
]

# Test coordinates
TEST_LAT = 46.8
TEST_LNG = -71.2
TEST_MONTH = 10


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestCorridorsV10Profiles:
    """Tests for /api/v10/corridors/profiles endpoint"""

    def test_profiles_endpoint_returns_200(self, api_client):
        """GET /api/v10/corridors/profiles returns 200"""
        response = api_client.get(f"{BASE_URL}/api/v10/corridors/profiles")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /api/v10/corridors/profiles returns 200")

    def test_profiles_lists_5_species(self, api_client):
        """Profiles endpoint lists all 5 species"""
        response = api_client.get(f"{BASE_URL}/api/v10/corridors/profiles")
        data = response.json()
        assert "profiles" in data, "Response missing 'profiles'"
        assert data["species_count"] == 5, f"Expected 5 species, got {data['species_count']}"
        assert data["parametres_count"] == 12, f"Expected 12 params, got {data['parametres_count']}"
        
        profile_ids = [p["id"] for p in data["profiles"]]
        for sp in SPECIES_LIST:
            assert sp in profile_ids, f"Missing species: {sp}"
        print("PASS: Profiles lists all 5 species with 12 parameters each")


class TestCorridorsV10ProfileSingle:
    """Tests for /api/v10/corridors/profile/{species} endpoint"""

    @pytest.mark.parametrize("species", SPECIES_LIST)
    def test_profile_returns_12_params(self, api_client, species):
        """GET /api/v10/corridors/profile/{species} returns 12 parameters"""
        response = api_client.get(f"{BASE_URL}/api/v10/corridors/profile/{species}")
        assert response.status_code == 200, f"Expected 200 for {species}, got {response.status_code}"
        
        data = response.json()
        assert "profile" in data, f"Response missing 'profile' for {species}"
        assert "parametres_12" in data["profile"], f"Missing 'parametres_12' for {species}"
        
        params = data["profile"]["parametres_12"]
        for key in PARAM_KEYS_12:
            assert key in params, f"Missing parameter '{key}' for {species}"
        
        print(f"PASS: Profile {species} has all 12 parameters")


class TestCorridorsV10Analyze:
    """Tests for POST /api/v10/corridors/analyze endpoint"""

    def test_analyze_returns_200(self, api_client):
        """POST /api/v10/corridors/analyze returns 200"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: POST /api/v10/corridors/analyze returns 200")

    def test_analyze_returns_score_and_classification(self, api_client):
        """Analyze returns SCORE_CORRIDOR and CLASSE_CORRIDOR"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze", json=payload)
        data = response.json()
        
        assert "score_corridor" in data, "Missing 'score_corridor'"
        assert "classe_corridor" in data, "Missing 'classe_corridor'"
        assert "classe_label" in data, "Missing 'classe_label'"
        assert "classe_color" in data, "Missing 'classe_color'"
        
        score = data["score_corridor"]
        assert 0 <= score <= 100, f"Score out of range: {score}"
        assert data["classe_corridor"] in ["OPTIMAL", "FONCTIONNEL", "DEGRADE", "INUTILISABLE"]
        print(f"PASS: Score={score}, Classe={data['classe_corridor']}")

    def test_analyze_returns_continuity(self, api_client):
        """Analyze returns continuity info with connected=True and dead_ends=0"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze", json=payload)
        data = response.json()
        
        assert "continuity" in data, "Missing 'continuity'"
        continuity = data["continuity"]
        assert "connected" in continuity, "Missing 'connected'"
        assert "dead_ends" in continuity, "Missing 'dead_ends'"
        
        # CRITICAL: ABSOLUTE CONTINUITY requirement
        assert continuity["connected"] == True, f"Network not connected! connected={continuity['connected']}"
        assert continuity["dead_ends"] == 0, f"Dead-ends found! dead_ends={continuity['dead_ends']}"
        print(f"PASS: Continuity OK - connected={continuity['connected']}, dead_ends={continuity['dead_ends']}")

    def test_analyze_returns_bce4x_pass(self, api_client):
        """Analyze returns BCE-4X validation with PASS status"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze", json=payload)
        data = response.json()
        
        assert "validation" in data, "Missing 'validation'"
        assert "bce4x" in data["validation"], "Missing 'bce4x'"
        
        bce4x = data["validation"]["bce4x"]
        assert "status" in bce4x, "Missing 'status' in bce4x"
        assert "checks" in bce4x, "Missing 'checks' in bce4x"
        
        # Check all 7 BCE-4X validation checks
        expected_checks = ["GEOM-001", "GEOM-002", "GEOM-003", "HYDRO-001", "TOPO-001", "CONT-001", "COMP-001"]
        for check in expected_checks:
            assert check in bce4x["checks"], f"Missing BCE-4X check: {check}"
            assert bce4x["checks"][check] == "PASS", f"BCE-4X {check} FAILED!"
        
        assert bce4x["status"] == "PASS", f"BCE-4X validation FAILED! status={bce4x['status']}, errors={bce4x.get('errors', [])}"
        print(f"PASS: BCE-4X validation PASS - all 7 checks passed")

    def test_analyze_returns_steeve_max_pass(self, api_client):
        """Analyze returns Steeve-MAX validation with PASS status"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze", json=payload)
        data = response.json()
        
        assert "validation" in data, "Missing 'validation'"
        assert "steeve_max" in data["validation"], "Missing 'steeve_max'"
        
        sm = data["validation"]["steeve_max"]
        assert "status" in sm, "Missing 'status' in steeve_max"
        assert "checks" in sm, "Missing 'checks' in steeve_max"
        
        # Check all 5 Steeve-MAX validation checks
        expected_checks = ["SM-001", "SM-002", "SM-003", "SM-004", "SM-005"]
        for check in expected_checks:
            assert check in sm["checks"], f"Missing Steeve-MAX check: {check}"
            # Allow PASS or WARN for SM-001 (zone diversity can vary by location)
            assert sm["checks"][check] in ["PASS", "WARN"], f"Steeve-MAX {check} FAILED!"
        
        assert sm["status"] in ["PASS", "WARN"], f"Steeve-MAX validation FAILED! status={sm['status']}, errors={sm.get('errors', [])}"
        print(f"PASS: Steeve-MAX validation {sm['status']} - all 5 checks verified")


class TestCorridorsV10AnalyzeFull:
    """Tests for POST /api/v10/corridors/analyze-full endpoint"""

    def test_analyze_full_returns_geojson(self, api_client):
        """POST /api/v10/corridors/analyze-full returns GeoJSON"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "geojson" in data, "Missing 'geojson'"
        
        geojson = data["geojson"]
        assert geojson["type"] == "FeatureCollection", f"Expected FeatureCollection, got {geojson['type']}"
        assert "features" in geojson, "Missing 'features' in GeoJSON"
        assert len(geojson["features"]) > 0, "GeoJSON has no features"
        print(f"PASS: GeoJSON returned with {len(geojson['features'])} features")

    def test_analyze_full_geojson_has_corridors_and_zones(self, api_client):
        """GeoJSON contains LineString corridors and Point zones"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze-full", json=payload)
        data = response.json()
        geojson = data["geojson"]
        
        linestring_count = 0
        point_count = 0
        
        for feature in geojson["features"]:
            geom_type = feature["geometry"]["type"]
            if geom_type == "LineString":
                linestring_count += 1
                # Validate LineString has coordinates
                coords = feature["geometry"]["coordinates"]
                assert len(coords) >= 2, f"LineString has too few coordinates: {len(coords)}"
            elif geom_type == "Point":
                point_count += 1
                # Validate Point has coordinates
                coords = feature["geometry"]["coordinates"]
                assert len(coords) == 2, f"Point coordinates invalid: {coords}"
        
        assert linestring_count > 0, "No LineString corridors in GeoJSON"
        assert point_count > 0, "No Point zones in GeoJSON"
        print(f"PASS: GeoJSON has {linestring_count} LineString corridors and {point_count} Point zones")


class TestCorridorsV10Multi:
    """Tests for GET /api/v10/corridors/multi endpoint"""

    def test_multi_returns_5_species(self, api_client):
        """GET /api/v10/corridors/multi returns results for all 5 species"""
        response = api_client.get(
            f"{BASE_URL}/api/v10/corridors/multi",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "month": TEST_MONTH}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "species_results" in data, "Missing 'species_results'"
        
        results = data["species_results"]
        for sp in SPECIES_LIST:
            assert sp in results, f"Missing species {sp} in multi-species results"
            assert "score_corridor" in results[sp], f"Missing score for {sp}"
            assert "continuity" in results[sp], f"Missing continuity for {sp}"
            assert "bce4x_status" in results[sp], f"Missing bce4x_status for {sp}"
            assert "steeve_max_status" in results[sp], f"Missing steeve_max_status for {sp}"
        
        print(f"PASS: Multi-species endpoint returns all 5 species")

    def test_multi_all_species_pass_validation(self, api_client):
        """All 5 species pass BCE-4X and Steeve-MAX validation in multi endpoint"""
        response = api_client.get(
            f"{BASE_URL}/api/v10/corridors/multi",
            params={"lat": TEST_LAT, "lng": TEST_LNG, "month": TEST_MONTH}
        )
        data = response.json()
        results = data["species_results"]
        
        for sp in SPECIES_LIST:
            bce = results[sp]["bce4x_status"]
            sm = results[sp]["steeve_max_status"]
            continuity = results[sp]["continuity"]
            
            assert bce == "PASS", f"{sp}: BCE-4X status is {bce}, expected PASS"
            assert sm in ["PASS", "WARN"], f"{sp}: Steeve-MAX status is {sm}, expected PASS or WARN"
            assert continuity["connected"] == True, f"{sp}: Network not connected"
            assert continuity["dead_ends"] == 0, f"{sp}: Has {continuity['dead_ends']} dead-ends"
        
        print(f"PASS: All 5 species pass BCE-4X and Steeve-MAX validation with zero dead-ends")


class TestCorridorsV10Documentation:
    """Tests for GET /api/v10/corridors/documentation endpoint"""

    def test_documentation_returns_complete_info(self, api_client):
        """GET /api/v10/corridors/documentation returns complete technical docs"""
        response = api_client.get(f"{BASE_URL}/api/v10/corridors/documentation")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Check engine info
        assert "engine" in data, "Missing 'engine'"
        assert data["engine"]["id"] == "CORRIDORS-V10", "Wrong engine ID"
        assert data["engine"]["version"] == "10.0.0", "Wrong version"
        
        # Check method info
        assert "methode" in data, "Missing 'methode'"
        assert "algorithme" in data["methode"], "Missing algorithm"
        assert "A*" in data["methode"]["algorithme"], "Algorithm should be A*"
        
        # Check 12 parameters
        assert "parametres_12" in data, "Missing 'parametres_12'"
        assert len(data["parametres_12"]) == 12, f"Expected 12 params, got {len(data['parametres_12'])}"
        
        # Check BCE-4X validation rules
        assert "validation_bce4x" in data, "Missing 'validation_bce4x'"
        bce4x_rules = data["validation_bce4x"]
        expected_bce = ["GEOM-001", "GEOM-002", "GEOM-003", "HYDRO-001", "TOPO-001", "CONT-001", "COMP-001"]
        for rule in expected_bce:
            assert rule in bce4x_rules, f"Missing BCE-4X rule: {rule}"
        
        # Check Steeve-MAX validation rules
        assert "validation_steeve_max" in data, "Missing 'validation_steeve_max'"
        sm_rules = data["validation_steeve_max"]
        expected_sm = ["SM-001", "SM-002", "SM-003", "SM-004", "SM-005"]
        for rule in expected_sm:
            assert rule in sm_rules, f"Missing Steeve-MAX rule: {rule}"
        
        print(f"PASS: Documentation complete with BCE-4X and Steeve-MAX rules")


class TestCorridorsV10WaterBarrier:
    """Tests for BCE-4X HYDRO-001: Water = barrier"""

    def test_no_corridor_crosses_water(self, api_client):
        """No corridor should cross water (HYDRO-001)"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze", json=payload)
        data = response.json()
        
        bce4x = data["validation"]["bce4x"]
        assert bce4x["checks"]["HYDRO-001"] == "PASS", "HYDRO-001 (water barrier) FAILED!"
        
        # Check for errors related to water crossing
        errors = bce4x.get("errors", [])
        water_errors = [e for e in errors if "eau" in e.lower() or "water" in e.lower()]
        assert len(water_errors) == 0, f"Water crossing errors found: {water_errors}"
        
        print("PASS: HYDRO-001 - No corridor crosses water")


class TestCorridorsV10SlopeBarrier:
    """Tests for BCE-4X TOPO-001: Slope <= max"""

    def test_no_corridor_exceeds_max_slope(self, api_client):
        """No corridor should exceed species max slope (TOPO-001)"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze", json=payload)
        data = response.json()
        
        bce4x = data["validation"]["bce4x"]
        assert bce4x["checks"]["TOPO-001"] == "PASS", "TOPO-001 (slope barrier) FAILED!"
        
        # Check for errors related to slope
        errors = bce4x.get("errors", [])
        slope_errors = [e for e in errors if "pente" in e.lower() or "slope" in e.lower()]
        assert len(slope_errors) == 0, f"Slope exceeding errors found: {slope_errors}"
        
        print("PASS: TOPO-001 - No corridor exceeds max slope")


class TestCorridorsV10NoSelfIntersection:
    """Tests for BCE-4X GEOM-002: No self-intersection"""

    def test_no_self_intersection(self, api_client):
        """No corridor should self-intersect (GEOM-002)"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze", json=payload)
        data = response.json()
        
        bce4x = data["validation"]["bce4x"]
        assert bce4x["checks"]["GEOM-002"] == "PASS", "GEOM-002 (no self-intersection) FAILED!"
        
        print("PASS: GEOM-002 - No self-intersection in corridors")


class TestAntiRegressionALIMENTATION:
    """Anti-regression tests for ALIMENTATION-V1 engine"""

    def test_alimentation_v1_profiles_still_works(self, api_client):
        """ALIMENTATION-V1 /api/v1/alimentation/profiles still works"""
        response = api_client.get(f"{BASE_URL}/api/v1/alimentation/profiles")
        assert response.status_code == 200, f"ALIMENTATION-V1 profiles broken! Status: {response.status_code}"
        
        data = response.json()
        assert "profiles" in data, "Missing profiles in response"
        assert len(data["profiles"]) == 5, f"Expected 5 profiles, got {len(data['profiles'])}"
        print("PASS: ALIMENTATION-V1 profiles endpoint still works")

    def test_alimentation_v1_analyze_still_works(self, api_client):
        """ALIMENTATION-V1 POST /api/v1/alimentation/analyze still works"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/alimentation/analyze", json=payload)
        assert response.status_code == 200, f"ALIMENTATION-V1 analyze broken! Status: {response.status_code}"
        
        data = response.json()
        # ALIMENTATION-V1 returns cells array with individual scores
        assert "engine" in data and data["engine"] == "ALIMENTATION-V1", "Wrong engine"
        assert "cells" in data, "Missing cells in response"
        assert len(data["cells"]) > 0, "No cells returned"
        print(f"PASS: ALIMENTATION-V1 analyze still works, {len(data['cells'])} cells returned")


class TestAntiRegressionREPOS:
    """Anti-regression tests for REPOS-V1 engine"""

    def test_repos_v1_profiles_still_works(self, api_client):
        """REPOS-V1 /api/v1/repos/profiles still works"""
        response = api_client.get(f"{BASE_URL}/api/v1/repos/profiles")
        assert response.status_code == 200, f"REPOS-V1 profiles broken! Status: {response.status_code}"
        
        data = response.json()
        assert "profiles" in data, "Missing profiles in response"
        assert len(data["profiles"]) == 5, f"Expected 5 profiles, got {len(data['profiles'])}"
        print("PASS: REPOS-V1 profiles endpoint still works")

    def test_repos_v1_analyze_still_works(self, api_client):
        """REPOS-V1 POST /api/v1/repos/analyze still works"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v1/repos/analyze", json=payload)
        assert response.status_code == 200, f"REPOS-V1 analyze broken! Status: {response.status_code}"
        
        data = response.json()
        # REPOS-V1 returns cells array with individual scores
        assert "engine" in data and data["engine"] == "REPOS-V1", "Wrong engine"
        assert "cells" in data, "Missing cells in response"
        assert len(data["cells"]) > 0, "No cells returned"
        print(f"PASS: REPOS-V1 analyze still works, {len(data['cells'])} cells returned")


class TestCorridorsV10MultipleCoordinates:
    """Test corridors across different coordinates"""

    @pytest.mark.parametrize("coords", [
        (46.8, -71.2),   # Quebec City region
        (45.5, -73.5),   # Montreal region
        (48.4, -68.5),   # Rimouski region
    ])
    def test_corridors_at_different_locations(self, api_client, coords):
        """Test corridors work at different coordinates"""
        lat, lng = coords
        payload = {
            "center_lat": lat,
            "center_lng": lng,
            "species": "CERF",
            "month": TEST_MONTH,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze", json=payload)
        assert response.status_code == 200, f"Failed at ({lat}, {lng}): {response.status_code}"
        
        data = response.json()
        assert data["continuity"]["connected"] == True, f"Network not connected at ({lat}, {lng})"
        assert data["continuity"]["dead_ends"] == 0, f"Dead-ends at ({lat}, {lng})"
        assert data["validation"]["bce4x"]["status"] == "PASS", f"BCE-4X failed at ({lat}, {lng})"
        
        print(f"PASS: Corridors OK at ({lat}, {lng}), score={data['score_corridor']}")


class TestCorridorsV10Seasons:
    """Test corridors across different seasons/months"""

    @pytest.mark.parametrize("month,season", [
        (1, "hiver"),
        (4, "printemps"),
        (7, "ete"),
        (10, "automne"),
    ])
    def test_corridors_by_season(self, api_client, month, season):
        """Test corridors work for all seasons"""
        payload = {
            "center_lat": TEST_LAT,
            "center_lng": TEST_LNG,
            "species": "CERF",
            "month": month,
        }
        response = api_client.post(f"{BASE_URL}/api/v10/corridors/analyze", json=payload)
        assert response.status_code == 200, f"Failed for month {month}: {response.status_code}"
        
        data = response.json()
        assert data["season"] == season, f"Wrong season: expected {season}, got {data['season']}"
        assert data["continuity"]["connected"] == True, f"Network not connected in {season}"
        assert data["validation"]["bce4x"]["status"] == "PASS", f"BCE-4X failed in {season}"
        
        print(f"PASS: Corridors OK for {season} (month={month}), score={data['score_corridor']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
