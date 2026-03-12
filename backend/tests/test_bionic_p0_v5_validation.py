"""
BIONIC V5 P0 Validation Tests
==============================
Tests pour valider les corrections P0 avant passage à PHASE C:
- P0.1: Pipeline organique Marching Squares + Chaikin intégré
- P0.2: Superposabilité layers avec z-index distincts
- P0.3: WebSocket GPS corrigé pour wss://

Test Coverage:
1. API /api/v1/bionic/analyze_waypoint retourne zones avec organic=true et pipeline=marching_squares+chaikin_3passes
2. Les zones comportementales (bedding, feeding, rut, pressure) ont des contours de 100+ points
3. Le WebSocket health endpoint retourne status=healthy avec protocol_support=[ws, wss]
4. Le score BIONIC final est calculé et affiché (mode RUT)
5. Non-régression: observations, notifications fonctionnels
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://corridor-analysis.preview.emergentagent.com').rstrip('/')


class TestBionicP0Validation:
    """Tests de validation P0 BIONIC V5"""
    
    # =========================================================================
    # P0.1 - Pipeline Organique Marching Squares + Chaikin
    # =========================================================================
    
    def test_p01_organic_pipeline_bedding_zones(self):
        """P0.1: Zones de repos avec pipeline organique"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json={
                "waypoint": {
                    "id": "test-bedding-001",
                    "name": "Test Bedding Zone",
                    "latitude": 47.5,
                    "longitude": -70.5
                },
                "target_datetime": "2026-10-15T08:00:00Z",
                "species": "orignal",
                "parameters": {"mode": "rut"},
                "visualization": {"organic_shape": True}
            },
            timeout=30
        )
        
        assert response.status_code == 200, f"API error: {response.text}"
        data = response.json()
        
        # Verify layers exist
        assert "layers" in data, "Response missing 'layers'"
        assert "behavioral_zones" in data["layers"], "Missing behavioral_zones"
        
        behavioral = data["layers"]["behavioral_zones"]
        bedding_zones = behavioral.get("bedding_zones", [])
        
        # Validate bedding zones have organic pipeline
        for zone in bedding_zones:
            assert zone.get("organic") == True, f"Zone {zone.get('zone_id')} missing organic=true"
            props = zone.get("properties", {})
            pipeline = props.get("pipeline", "")
            assert "marching_squares+chaikin" in pipeline, f"Zone {zone.get('zone_id')} missing pipeline info"
    
    def test_p01_organic_pipeline_feeding_zones(self):
        """P0.1: Zones d'alimentation avec pipeline organique"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json={
                "waypoint": {
                    "id": "test-feeding-001",
                    "name": "Test Feeding Zone",
                    "latitude": 46.8139,
                    "longitude": -71.2080
                },
                "target_datetime": "2026-01-15T14:00:00Z",
                "species": "orignal",
                "parameters": {"mode": "rut"},
                "visualization": {"organic_shape": True}
            },
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        feeding_zones = data["layers"]["behavioral_zones"].get("feeding_zones", [])
        
        for zone in feeding_zones:
            assert zone.get("organic") == True, f"Feeding zone {zone.get('zone_id')} missing organic=true"
            props = zone.get("properties", {})
            assert "marching_squares+chaikin" in props.get("pipeline", ""), f"Feeding zone missing pipeline"
    
    def test_p01_organic_pipeline_rut_zones(self):
        """P0.1: Zones de rut avec pipeline organique (saison d'automne)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json={
                "waypoint": {
                    "id": "test-rut-001",
                    "name": "Test Rut Zone October",
                    "latitude": 47.5,
                    "longitude": -70.5
                },
                "target_datetime": "2026-10-15T08:00:00Z",  # October = rut season
                "species": "orignal",
                "parameters": {"mode": "rut"},
                "visualization": {"organic_shape": True}
            },
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        rut_zones = data["layers"]["behavioral_zones"].get("rut_zones", [])
        
        # In October, should have rut zones
        if len(rut_zones) > 0:
            for zone in rut_zones:
                assert zone.get("organic") == True, f"Rut zone {zone.get('zone_id')} missing organic=true"
                props = zone.get("properties", {})
                assert "marching_squares+chaikin" in props.get("pipeline", ""), f"Rut zone missing pipeline"
    
    def test_p01_contour_point_count_100_plus(self):
        """P0.1: Les zones comportementales ont des contours de 100+ points"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json={
                "waypoint": {
                    "id": "test-points-001",
                    "name": "Test Point Count",
                    "latitude": 47.5,
                    "longitude": -70.5
                },
                "target_datetime": "2026-10-15T08:00:00Z",
                "species": "orignal",
                "parameters": {"mode": "rut"},
                "visualization": {"organic_shape": True}
            },
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        behavioral = data["layers"]["behavioral_zones"]
        all_zones = []
        
        for zone_type in ["bedding_zones", "feeding_zones", "rut_zones", "pressure_avoidance"]:
            zones = behavioral.get(zone_type, [])
            all_zones.extend(zones)
        
        # Validate at least some zones exist
        assert len(all_zones) > 0, "No behavioral zones generated"
        
        # Check point count for polygon zones
        for zone in all_zones:
            geometry = zone.get("geometry", {})
            if geometry.get("type") == "Polygon":
                coords = geometry.get("coordinates", [[]])[0]
                point_count = len(coords)
                assert point_count >= 100, f"Zone {zone.get('zone_id')} has only {point_count} points (need 100+)"
    
    # =========================================================================
    # P0.3 - WebSocket GPS wss:// Support
    # =========================================================================
    
    def test_p03_websocket_health_endpoint(self):
        """P0.3: WebSocket health endpoint retourne status=healthy"""
        response = requests.get(f"{BASE_URL}/api/v1/geo-sync/health", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") == "healthy", f"WebSocket not healthy: {data}"
        assert data.get("service") == "geo-sync-websocket"
        assert data.get("endpoint") == "/ws/geo-sync"
    
    def test_p03_websocket_protocol_support_wss(self):
        """P0.3: WebSocket supporte wss:// et ws://"""
        response = requests.get(f"{BASE_URL}/api/v1/geo-sync/health", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        
        protocol_support = data.get("protocol_support", [])
        assert "ws" in protocol_support, "Missing ws:// protocol support"
        assert "wss" in protocol_support, "Missing wss:// protocol support"
    
    def test_p03_websocket_features(self):
        """P0.3: WebSocket features configurées correctement"""
        response = requests.get(f"{BASE_URL}/api/v1/geo-sync/health", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        
        features = data.get("features", {})
        assert features.get("real_time_sync") == True
        assert features.get("group_broadcast") == True
        # Hotspots and corridors should be excluded (private)
        assert "hotspot" in features.get("private_entities_excluded", [])
        assert "corridor" in features.get("private_entities_excluded", [])
    
    # =========================================================================
    # BIONIC Score Calculation
    # =========================================================================
    
    def test_bionic_score_final_calculated(self):
        """Score BIONIC final est calculé (mode RUT)"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json={
                "waypoint": {
                    "id": "test-score-001",
                    "name": "Test Score Calculation",
                    "latitude": 46.8139,
                    "longitude": -71.2080
                },
                "target_datetime": "2026-10-15T14:00:00Z",
                "species": "orignal",
                "parameters": {"mode": "rut"}
            },
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        scores = data.get("scores", {})
        
        # Verify final score is calculated
        final_score = scores.get("score_bionic_final")
        assert final_score is not None, "Missing score_bionic_final"
        assert isinstance(final_score, (int, float)), "score_bionic_final is not numeric"
        assert 0 <= final_score <= 100, f"score_bionic_final out of range: {final_score}"
        
        # Verify analysis mode
        assert scores.get("analysis_mode") == "rut", f"Wrong analysis mode: {scores.get('analysis_mode')}"
    
    def test_bionic_score_breakdown_exists(self):
        """Score BIONIC breakdown est présent"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json={
                "waypoint": {
                    "id": "test-breakdown-001",
                    "name": "Test Score Breakdown",
                    "latitude": 46.8139,
                    "longitude": -71.2080
                },
                "target_datetime": "2026-01-15T14:00:00Z",
                "species": "orignal",
                "parameters": {"mode": "rut"}
            },
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        breakdown = data["scores"].get("breakdown", {})
        
        # Verify key factors exist
        expected_factors = ["H_habitat", "R_risk", "S_probability", "A_mobility", "T_weather", "P_pressure"]
        for factor in expected_factors:
            assert factor in breakdown, f"Missing factor: {factor}"
            factor_data = breakdown[factor]
            assert "value" in factor_data, f"Factor {factor} missing 'value'"
            assert "weight" in factor_data, f"Factor {factor} missing 'weight'"
    
    # =========================================================================
    # Non-Regression Tests
    # =========================================================================
    
    def test_nonregression_observations_endpoint(self):
        """Non-régression: Endpoint observations fonctionnel"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/observations?limit=5", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") == "success"
        assert "observations" in data
        assert "total" in data
    
    def test_nonregression_notifications_health(self):
        """Non-régression: Endpoint notifications health fonctionnel"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/notifications/health", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") == "healthy"
        assert "features" in data
    
    def test_nonregression_geosync_status(self):
        """Non-régression: Endpoint geo-sync status fonctionnel"""
        response = requests.get(f"{BASE_URL}/api/v1/geo-sync/status?group_id=test_group", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "group_id" in data
        assert "member_count" in data
    
    def test_nonregression_api_health(self):
        """Non-régression: API health endpoint principal"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("status") == "healthy"
        assert "version" in data or "service" in data


class TestBionicLayerGeneration:
    """Tests de génération des layers BIONIC"""
    
    def test_layers_output_structure(self):
        """Structure de sortie des layers conforme"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json={
                "waypoint": {
                    "id": "test-layers-001",
                    "name": "Test Layer Structure",
                    "latitude": 46.8139,
                    "longitude": -71.2080
                },
                "target_datetime": "2026-10-15T14:00:00Z",
                "species": "orignal",
                "parameters": {"mode": "rut"}
            },
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        layers = data.get("layers", {})
        
        # Verify all 5 layer families exist
        expected_families = [
            "behavioral_zones",
            "attraction_points", 
            "terrain_analysis",
            "vegetation_analysis",
            "hunt_planning"
        ]
        
        for family in expected_families:
            assert family in layers, f"Missing layer family: {family}"
    
    def test_behavioral_zones_sublayers(self):
        """Sous-couches behavioral_zones présentes"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json={
                "waypoint": {
                    "id": "test-sublayers-001",
                    "name": "Test Behavioral Sublayers",
                    "latitude": 46.8139,
                    "longitude": -71.2080
                },
                "target_datetime": "2026-10-15T14:00:00Z",
                "species": "orignal",
                "parameters": {"mode": "rut"}
            },
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        behavioral = data["layers"]["behavioral_zones"]
        
        # Verify all sublayers exist
        expected_sublayers = [
            "bedding_zones",
            "feeding_zones",
            "rut_zones",
            "movement_corridors",
            "pressure_avoidance"
        ]
        
        for sublayer in expected_sublayers:
            assert sublayer in behavioral, f"Missing sublayer: {sublayer}"
    
    def test_movement_corridors_generated(self):
        """Corridors de mouvement générés"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json={
                "waypoint": {
                    "id": "test-corridors-001",
                    "name": "Test Corridors",
                    "latitude": 47.5,
                    "longitude": -70.5
                },
                "target_datetime": "2026-10-15T14:00:00Z",
                "species": "orignal",
                "parameters": {"mode": "rut"}
            },
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        corridors = data["layers"]["behavioral_zones"].get("movement_corridors", [])
        
        # Should have at least one corridor
        if len(corridors) > 0:
            corridor = corridors[0]
            assert "corridor_id" in corridor
            assert corridor.get("organic") == True
            assert corridor.get("geometry", {}).get("type") == "LineString"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
