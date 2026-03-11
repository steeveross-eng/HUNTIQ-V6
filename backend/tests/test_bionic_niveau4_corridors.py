"""
BIONIC V5 NIVEAU 4 — Corridor Tests
====================================
Test complet des corridors de déplacement NIVEAU 4 - Habitat & Corridors.

EXIGENCES À TESTER:
1. API POST /api/v1/bionic/analyze_waypoint retourne une clé 'corridors' avec GeoJSON FeatureCollection
2. Corridors générés dynamiquement avec les 5 types (primary, secondary, seasonal, thermal, risk)
3. Styles des corridors conformes aux normes: couleurs, épaisseurs, pointillés
4. Traçabilité complète: source_ids et version présents sur chaque corridor
5. Facteurs d'influence (habitat, edge, thermal_stress, pres_human) présents dans les properties

TYPES DE CORRIDORS:
- PRIMARY: #FF8A00, continu, 4px
- SECONDARY: #FFC04D, pointillé long (12,6), 3px
- SEASONAL: #4DA6FF, pointillé court (6,4), 3px  
- THERMAL: #FF4D4D, continu semi-transparent (0.6), 5px
- RISK: #CC0000, continu, 6px avec halo rose (#FFCCCC)

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 NIVEAU 4
"""

import pytest
import requests
import os
from datetime import datetime, timezone

# Base URL from environment
BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://territory-analysis.preview.emergentagent.com")

# Expected styles per corridor type
EXPECTED_STYLES = {
    "primary": {
        "stroke_color": "#FF8A00",
        "stroke_width": 4,
        "stroke_opacity": 1.0,
        "dash_array": None  # Continu
    },
    "secondary": {
        "stroke_color": "#FFC04D",
        "stroke_width": 3,
        "stroke_opacity": 1.0,
        "dash_array": "12,6"  # Pointillé long
    },
    "seasonal": {
        "stroke_color": "#4DA6FF",
        "stroke_width": 3,
        "stroke_opacity": 1.0,
        "dash_array": "6,4"  # Pointillé court
    },
    "thermal": {
        "stroke_color": "#FF4D4D",
        "stroke_width": 5,
        "stroke_opacity": 0.6,  # Semi-transparent
        "dash_array": None  # Continu
    },
    "risk": {
        "stroke_color": "#CC0000",
        "stroke_width": 6,
        "stroke_opacity": 1.0,
        "dash_array": None,  # Continu
        "halo_color": "#FFCCCC",
        "halo_opacity": 0.4,
        "halo_weight": 12
    }
}


@pytest.fixture
def api_client():
    """Session HTTP pour les tests."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def analysis_request_rut():
    """Requête d'analyse en mode RUT (corridors saisonniers générés)."""
    return {
        "waypoint": {
            "id": "test-niveau4-rut",
            "name": "Test Corridors NIVEAU 4 RUT",
            "latitude": 46.8,
            "longitude": -71.2
        },
        "target_datetime": "2026-01-15T07:30:00Z",
        "species": "orignal",
        "parameters": {
            "mode": "rut",
            "search_radius_km": 3.0
        }
    }


@pytest.fixture
def corridor_response(api_client, analysis_request_rut):
    """Obtenir la réponse avec corridors."""
    response = api_client.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=analysis_request_rut)
    assert response.status_code == 200, f"API failed: {response.text}"
    return response.json()


# =============================================================================
# 1. API STRUCTURE TESTS — Clé 'corridors' avec GeoJSON FeatureCollection
# =============================================================================

class TestAPICorridorsStructure:
    """Tests de la structure de la réponse corridors."""
    
    def test_api_returns_corridors_key(self, corridor_response):
        """La réponse contient une clé 'corridors'."""
        assert "corridors" in corridor_response, "Key 'corridors' missing in response"
        print("✓ API returns 'corridors' key")
    
    def test_corridors_is_geojson_feature_collection(self, corridor_response):
        """Les corridors sont un GeoJSON FeatureCollection."""
        corridors = corridor_response.get("corridors")
        assert corridors is not None
        assert corridors.get("type") == "FeatureCollection", f"Expected FeatureCollection, got {corridors.get('type')}"
        print("✓ Corridors is GeoJSON FeatureCollection")
    
    def test_corridors_has_features_array(self, corridor_response):
        """Le FeatureCollection contient un tableau 'features'."""
        corridors = corridor_response.get("corridors", {})
        assert "features" in corridors, "Missing 'features' in corridors"
        assert isinstance(corridors["features"], list), "'features' should be a list"
        print(f"✓ Features array present with {len(corridors['features'])} corridors")
    
    def test_corridors_has_properties(self, corridor_response):
        """Le FeatureCollection a des propriétés réseau."""
        corridors = corridor_response.get("corridors", {})
        props = corridors.get("properties", {})
        
        assert "network_id" in props, "Missing network_id"
        assert "waypoint_id" in props, "Missing waypoint_id"
        assert "statistics" in props, "Missing statistics"
        assert "species" in props, "Missing species"
        assert "source_ids" in props, "Missing source_ids"
        assert "version" in props, "Missing version"
        
        print(f"✓ Network properties complete: {props.get('network_id')}")
    
    def test_corridors_statistics_complete(self, corridor_response):
        """Les statistiques du réseau sont complètes."""
        corridors = corridor_response.get("corridors", {})
        stats = corridors.get("properties", {}).get("statistics", {})
        
        assert "total_corridors" in stats
        assert "total_length_km" in stats
        assert "average_quality" in stats
        assert "by_type" in stats
        
        # Vérifier by_type contient les 5 types
        by_type = stats.get("by_type", {})
        expected_types = {"primary", "secondary", "seasonal", "thermal", "risk"}
        actual_types = set(by_type.keys())
        
        assert expected_types.issubset(actual_types), f"Missing types in by_type: {expected_types - actual_types}"
        
        print(f"✓ Statistics: {stats['total_corridors']} corridors, {stats['total_length_km']:.2f}km")


# =============================================================================
# 2. CORRIDOR TYPES TESTS — 5 types de corridors
# =============================================================================

class TestCorridorTypes:
    """Tests des types de corridors générés."""
    
    def test_corridors_contain_primary_type(self, corridor_response):
        """Au moins un corridor PRIMARY est généré."""
        features = corridor_response.get("corridors", {}).get("features", [])
        primary_corridors = [f for f in features if f["properties"]["corridor_type"] == "primary"]
        
        assert len(primary_corridors) >= 1, "No PRIMARY corridors found"
        print(f"✓ Found {len(primary_corridors)} PRIMARY corridors")
    
    def test_corridors_contain_secondary_type(self, corridor_response):
        """Au moins un corridor SECONDARY est généré."""
        features = corridor_response.get("corridors", {}).get("features", [])
        secondary_corridors = [f for f in features if f["properties"]["corridor_type"] == "secondary"]
        
        assert len(secondary_corridors) >= 1, "No SECONDARY corridors found"
        print(f"✓ Found {len(secondary_corridors)} SECONDARY corridors")
    
    def test_corridors_contain_seasonal_type_in_rut_mode(self, corridor_response):
        """Corridors SEASONAL générés en mode RUT."""
        features = corridor_response.get("corridors", {}).get("features", [])
        seasonal_corridors = [f for f in features if f["properties"]["corridor_type"] == "seasonal"]
        
        # En mode RUT, les corridors saisonniers sont attendus
        assert len(seasonal_corridors) >= 1, "No SEASONAL corridors in RUT mode"
        
        # Vérifier que le nom contient "RUT"
        for corridor in seasonal_corridors:
            name = corridor["properties"]["name"]
            assert "RUT" in name.upper() or "SAISONNIER" in name.upper(), f"Seasonal corridor name should mention RUT: {name}"
        
        print(f"✓ Found {len(seasonal_corridors)} SEASONAL corridors in RUT mode")
    
    def test_corridors_types_are_valid(self, corridor_response):
        """Tous les types de corridors sont valides."""
        features = corridor_response.get("corridors", {}).get("features", [])
        valid_types = {"primary", "secondary", "seasonal", "thermal", "risk"}
        
        for feature in features:
            corridor_type = feature["properties"]["corridor_type"]
            assert corridor_type in valid_types, f"Invalid corridor type: {corridor_type}"
        
        print(f"✓ All {len(features)} corridors have valid types")


# =============================================================================
# 3. CORRIDOR STYLES TESTS — Couleurs, épaisseurs, pointillés
# =============================================================================

class TestCorridorStyles:
    """Tests des styles graphiques des corridors."""
    
    def test_primary_corridor_style(self, corridor_response):
        """Style PRIMARY: #FF8A00, continu, 4px."""
        features = corridor_response.get("corridors", {}).get("features", [])
        primary = next((f for f in features if f["properties"]["corridor_type"] == "primary"), None)
        
        assert primary is not None, "No PRIMARY corridor found"
        
        rendering = primary["properties"]["rendering"]
        expected = EXPECTED_STYLES["primary"]
        
        assert rendering["stroke_color"] == expected["stroke_color"], f"Color mismatch: {rendering['stroke_color']}"
        assert rendering["stroke_width"] == expected["stroke_width"], f"Width mismatch: {rendering['stroke_width']}"
        assert rendering.get("dash_array") is None or rendering.get("dash_array") == expected["dash_array"], "PRIMARY should be continu (no dash)"
        
        print(f"✓ PRIMARY style: {rendering['stroke_color']}, {rendering['stroke_width']}px, continu")
    
    def test_secondary_corridor_style(self, corridor_response):
        """Style SECONDARY: #FFC04D, pointillé long (12,6), 3px."""
        features = corridor_response.get("corridors", {}).get("features", [])
        secondary = next((f for f in features if f["properties"]["corridor_type"] == "secondary"), None)
        
        assert secondary is not None, "No SECONDARY corridor found"
        
        rendering = secondary["properties"]["rendering"]
        expected = EXPECTED_STYLES["secondary"]
        
        assert rendering["stroke_color"] == expected["stroke_color"], f"Color mismatch: {rendering['stroke_color']}"
        assert rendering["stroke_width"] == expected["stroke_width"], f"Width mismatch: {rendering['stroke_width']}"
        assert rendering.get("dash_array") == expected["dash_array"], f"Dash mismatch: {rendering.get('dash_array')}"
        
        print(f"✓ SECONDARY style: {rendering['stroke_color']}, {rendering['stroke_width']}px, dash={rendering.get('dash_array')}")
    
    def test_seasonal_corridor_style(self, corridor_response):
        """Style SEASONAL: #4DA6FF, pointillé court (6,4), 3px."""
        features = corridor_response.get("corridors", {}).get("features", [])
        seasonal = next((f for f in features if f["properties"]["corridor_type"] == "seasonal"), None)
        
        assert seasonal is not None, "No SEASONAL corridor found"
        
        rendering = seasonal["properties"]["rendering"]
        expected = EXPECTED_STYLES["seasonal"]
        
        assert rendering["stroke_color"] == expected["stroke_color"], f"Color mismatch: {rendering['stroke_color']}"
        assert rendering["stroke_width"] == expected["stroke_width"], f"Width mismatch: {rendering['stroke_width']}"
        assert rendering.get("dash_array") == expected["dash_array"], f"Dash mismatch: {rendering.get('dash_array')}"
        
        print(f"✓ SEASONAL style: {rendering['stroke_color']}, {rendering['stroke_width']}px, dash={rendering.get('dash_array')}")
    
    def test_rendering_has_line_cap_and_join(self, corridor_response):
        """Tous les corridors ont line_cap et line_join."""
        features = corridor_response.get("corridors", {}).get("features", [])
        
        for feature in features:
            rendering = feature["properties"]["rendering"]
            assert rendering.get("line_cap") == "round", f"Missing or wrong line_cap"
            assert rendering.get("line_join") == "round", f"Missing or wrong line_join"
        
        print(f"✓ All corridors have line_cap='round', line_join='round'")


# =============================================================================
# 4. TRACEABILITY TESTS — source_ids et version
# =============================================================================

class TestCorridorTraceability:
    """Tests de traçabilité des corridors."""
    
    def test_corridors_have_source_ids(self, corridor_response):
        """Chaque corridor a des source_ids."""
        features = corridor_response.get("corridors", {}).get("features", [])
        
        for feature in features:
            source_ids = feature["properties"].get("source_ids", [])
            assert len(source_ids) > 0, f"Corridor {feature['properties']['corridor_id']} has no source_ids"
            assert "SRC-CORRIDOR-V1" in source_ids, "Missing SRC-CORRIDOR-V1 source"
        
        print(f"✓ All {len(features)} corridors have source_ids")
    
    def test_corridors_have_version(self, corridor_response):
        """Chaque corridor a une version."""
        features = corridor_response.get("corridors", {}).get("features", [])
        
        for feature in features:
            version = feature["properties"].get("version")
            assert version is not None, f"Corridor {feature['properties']['corridor_id']} has no version"
            assert version == "1.0.0", f"Expected version 1.0.0, got {version}"
        
        print(f"✓ All corridors have version 1.0.0")
    
    def test_network_has_source_ids(self, corridor_response):
        """Le réseau de corridors a des source_ids."""
        props = corridor_response.get("corridors", {}).get("properties", {})
        source_ids = props.get("source_ids", [])
        
        expected_sources = ["SRC-CORRIDOR-NETWORK", "SRC-CORRIDOR-V1"]
        for src in expected_sources:
            assert src in source_ids, f"Missing {src} in network source_ids"
        
        print(f"✓ Network source_ids: {source_ids}")
    
    def test_corridor_id_format(self, corridor_response):
        """Les corridor_id suivent le format COR-XXX-HHMMSS-NNNN."""
        features = corridor_response.get("corridors", {}).get("features", [])
        
        for feature in features:
            corridor_id = feature["properties"]["corridor_id"]
            assert corridor_id.startswith("COR-"), f"Invalid corridor_id format: {corridor_id}"
            parts = corridor_id.split("-")
            assert len(parts) >= 4, f"Invalid corridor_id parts: {corridor_id}"
        
        print(f"✓ All corridor_ids follow COR-XXX-HHMMSS-NNNN format")


# =============================================================================
# 5. FACTORS TESTS — habitat, edge, thermal_stress, pres_human, behavior, seasonal
# =============================================================================

class TestCorridorFactors:
    """Tests des facteurs d'influence sur les corridors."""
    
    def test_corridors_have_factors(self, corridor_response):
        """Chaque corridor a des facteurs d'influence."""
        features = corridor_response.get("corridors", {}).get("features", [])
        
        required_factors = ["habitat", "edge", "thermal_stress", "pres_human", "behavior", "seasonal"]
        
        for feature in features:
            factors = feature["properties"].get("factors", {})
            for factor in required_factors:
                assert factor in factors, f"Missing factor '{factor}' in corridor {feature['properties']['corridor_id']}"
                assert isinstance(factors[factor], (int, float)), f"Factor '{factor}' should be numeric"
        
        print(f"✓ All {len(features)} corridors have 6 influence factors")
    
    def test_factors_values_in_range(self, corridor_response):
        """Les valeurs des facteurs sont dans [0, 100]."""
        features = corridor_response.get("corridors", {}).get("features", [])
        
        for feature in features:
            factors = feature["properties"].get("factors", {})
            for factor_name, value in factors.items():
                assert 0 <= value <= 100, f"Factor {factor_name}={value} out of range [0,100]"
        
        print(f"✓ All factor values in [0, 100] range")
    
    def test_corridors_have_composite_score(self, corridor_response):
        """Chaque corridor a un composite_score."""
        features = corridor_response.get("corridors", {}).get("features", [])
        
        for feature in features:
            composite_score = feature["properties"].get("composite_score")
            assert composite_score is not None, "Missing composite_score"
            assert 0 <= composite_score <= 100, f"composite_score {composite_score} out of range"
        
        print(f"✓ All corridors have composite_score")
    
    def test_corridors_have_quality(self, corridor_response):
        """Chaque corridor a une qualité."""
        features = corridor_response.get("corridors", {}).get("features", [])
        valid_qualities = {"excellent", "good", "moderate", "poor", "blocked"}
        
        for feature in features:
            quality = feature["properties"].get("quality")
            assert quality in valid_qualities, f"Invalid quality: {quality}"
        
        print(f"✓ All corridors have valid quality label")


# =============================================================================
# 6. GEOMETRY TESTS — LineString valide
# =============================================================================

class TestCorridorGeometry:
    """Tests de la géométrie des corridors."""
    
    def test_corridors_are_linestrings(self, corridor_response):
        """Chaque corridor est un LineString GeoJSON."""
        features = corridor_response.get("corridors", {}).get("features", [])
        
        for feature in features:
            assert feature["type"] == "Feature", "Expected GeoJSON Feature"
            assert feature["geometry"]["type"] == "LineString", f"Expected LineString, got {feature['geometry']['type']}"
        
        print(f"✓ All {len(features)} corridors are LineString features")
    
    def test_corridors_have_valid_coordinates(self, corridor_response):
        """Les coordonnées sont valides [lng, lat]."""
        features = corridor_response.get("corridors", {}).get("features", [])
        
        for feature in features:
            coords = feature["geometry"]["coordinates"]
            assert len(coords) >= 2, "LineString should have at least 2 points"
            
            for coord in coords:
                assert len(coord) == 2, "Coordinate should be [lng, lat]"
                lng, lat = coord
                assert -180 <= lng <= 180, f"Invalid longitude: {lng}"
                assert -90 <= lat <= 90, f"Invalid latitude: {lat}"
        
        print(f"✓ All corridors have valid coordinates")
    
    def test_corridors_have_total_length(self, corridor_response):
        """Chaque corridor a une longueur totale."""
        features = corridor_response.get("corridors", {}).get("features", [])
        
        for feature in features:
            total_length = feature["properties"].get("total_length_m")
            assert total_length is not None, "Missing total_length_m"
            assert total_length > 0, f"total_length_m should be > 0, got {total_length}"
        
        print(f"✓ All corridors have total_length_m > 0")


# =============================================================================
# 7. ADDITIONAL PROPERTIES TESTS
# =============================================================================

class TestCorridorAdditionalProperties:
    """Tests des propriétés additionnelles."""
    
    def test_corridors_have_priority(self, corridor_response):
        """Chaque corridor a une priorité."""
        features = corridor_response.get("corridors", {}).get("features", [])
        valid_priorities = {"critical", "high", "moderate", "low"}
        
        for feature in features:
            priority = feature["properties"].get("priority")
            assert priority in valid_priorities, f"Invalid priority: {priority}"
        
        print(f"✓ All corridors have valid priority")
    
    def test_corridors_have_name_and_description(self, corridor_response):
        """Chaque corridor a un nom et une description."""
        features = corridor_response.get("corridors", {}).get("features", [])
        
        for feature in features:
            name = feature["properties"].get("name")
            description = feature["properties"].get("description")
            
            assert name is not None and len(name) > 0, "Missing corridor name"
            assert description is not None, "Missing corridor description"
        
        print(f"✓ All corridors have name and description")
    
    def test_seasonal_corridors_have_active_seasons(self, corridor_response):
        """Les corridors saisonniers ont des saisons actives."""
        features = corridor_response.get("corridors", {}).get("features", [])
        seasonal = [f for f in features if f["properties"]["corridor_type"] == "seasonal"]
        
        for corridor in seasonal:
            active_seasons = corridor["properties"].get("active_seasons", [])
            assert len(active_seasons) > 0, "SEASONAL corridor should have active_seasons"
            assert "rut" in active_seasons or "pre_rut" in active_seasons or "all" in active_seasons, \
                f"Expected rut/pre_rut/all in active_seasons, got {active_seasons}"
        
        print(f"✓ SEASONAL corridors have active_seasons")


# =============================================================================
# 8. INTEGRATION WITH ANALYSIS MODES
# =============================================================================

class TestCorridorAnalysisModes:
    """Tests de génération de corridors selon les modes d'analyse."""
    
    def test_rut_mode_generates_seasonal_corridors(self, api_client):
        """Mode RUT génère des corridors saisonniers."""
        request = {
            "waypoint": {"id": "test-rut", "name": "Test RUT", "latitude": 46.8, "longitude": -71.2},
            "target_datetime": "2026-10-15T07:00:00Z",
            "species": "orignal",
            "parameters": {"mode": "rut"}
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=request)
        assert response.status_code == 200
        
        data = response.json()
        corridors = data.get("corridors", {}).get("features", [])
        seasonal = [c for c in corridors if c["properties"]["corridor_type"] == "seasonal"]
        
        assert len(seasonal) >= 1, "RUT mode should generate seasonal corridors"
        print(f"✓ RUT mode: {len(seasonal)} seasonal corridors generated")
    
    def test_pre_rut_mode_generates_seasonal_corridors(self, api_client):
        """Mode PRE_RUT génère des corridors saisonniers."""
        request = {
            "waypoint": {"id": "test-pre-rut", "name": "Test PRE_RUT", "latitude": 46.8, "longitude": -71.2},
            "target_datetime": "2026-09-15T07:00:00Z",
            "species": "orignal",
            "parameters": {"mode": "pre_rut"}
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=request)
        assert response.status_code == 200
        
        data = response.json()
        corridors = data.get("corridors", {}).get("features", [])
        seasonal = [c for c in corridors if c["properties"]["corridor_type"] == "seasonal"]
        
        assert len(seasonal) >= 1, "PRE_RUT mode should generate seasonal corridors"
        print(f"✓ PRE_RUT mode: {len(seasonal)} seasonal corridors generated")
    
    def test_live_mode_generates_corridors(self, api_client):
        """Mode LIVE génère des corridors de base."""
        request = {
            "waypoint": {"id": "test-live", "name": "Test LIVE", "latitude": 46.8, "longitude": -71.2},
            "target_datetime": datetime.now(timezone.utc).isoformat(),
            "species": "orignal",
            "parameters": {"mode": "live"}
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=request)
        assert response.status_code == 200
        
        data = response.json()
        corridors = data.get("corridors", {}).get("features", [])
        
        assert len(corridors) >= 2, "LIVE mode should generate at least primary/secondary corridors"
        print(f"✓ LIVE mode: {len(corridors)} corridors generated")


# =============================================================================
# 9. SPECIES-SPECIFIC TESTS
# =============================================================================

class TestCorridorSpecies:
    """Tests des corridors pour différentes espèces."""
    
    def test_moose_corridors(self, api_client):
        """Génération de corridors pour l'orignal."""
        request = {
            "waypoint": {"id": "test-moose", "name": "Test Moose", "latitude": 46.8, "longitude": -71.2},
            "target_datetime": "2026-10-15T07:00:00Z",
            "species": "orignal",
            "parameters": {"mode": "rut"}
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=request)
        assert response.status_code == 200
        
        data = response.json()
        corridors = data.get("corridors", {})
        
        assert corridors.get("properties", {}).get("species") == "orignal"
        assert corridors.get("properties", {}).get("statistics", {}).get("total_corridors") >= 4
        
        print(f"✓ Moose corridors: {corridors['properties']['statistics']['total_corridors']} generated")
    
    def test_deer_corridors(self, api_client):
        """Génération de corridors pour le cerf."""
        request = {
            "waypoint": {"id": "test-deer", "name": "Test Deer", "latitude": 46.8, "longitude": -71.2},
            "target_datetime": "2026-10-15T07:00:00Z",
            "species": "cerf",
            "parameters": {"mode": "rut"}
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/bionic/analyze_waypoint", json=request)
        assert response.status_code == 200
        
        data = response.json()
        corridors = data.get("corridors", {})
        
        assert corridors.get("properties", {}).get("species") == "cerf"
        assert corridors.get("properties", {}).get("statistics", {}).get("total_corridors") >= 4
        
        print(f"✓ Deer corridors: {corridors['properties']['statistics']['total_corridors']} generated")


# =============================================================================
# 10. PERFORMANCE/VOLUME TESTS
# =============================================================================

class TestCorridorVolume:
    """Tests de volume et cohérence des corridors."""
    
    def test_minimum_corridors_generated(self, corridor_response):
        """Au moins 4 corridors générés (2 primary + 2 secondary)."""
        stats = corridor_response.get("corridors", {}).get("properties", {}).get("statistics", {})
        total = stats.get("total_corridors", 0)
        
        assert total >= 4, f"Expected at least 4 corridors, got {total}"
        print(f"✓ {total} corridors generated (min 4 expected)")
    
    def test_primary_corridors_count(self, corridor_response):
        """Au moins 2 corridors PRIMARY."""
        stats = corridor_response.get("corridors", {}).get("properties", {}).get("statistics", {})
        primary_count = stats.get("by_type", {}).get("primary", 0)
        
        assert primary_count >= 2, f"Expected at least 2 primary corridors, got {primary_count}"
        print(f"✓ {primary_count} PRIMARY corridors")
    
    def test_total_length_reasonable(self, corridor_response):
        """Longueur totale raisonnable (< 50km pour rayon de 3km)."""
        stats = corridor_response.get("corridors", {}).get("properties", {}).get("statistics", {})
        total_km = stats.get("total_length_km", 0)
        
        assert 0 < total_km < 50, f"Total length {total_km}km seems unreasonable"
        print(f"✓ Total network length: {total_km:.2f}km")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
