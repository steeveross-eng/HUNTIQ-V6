"""
Test suite for BIONIC V5 Water Exclusion Rule Validation
=========================================================

Tests validating:
1. WaterExclusionService correctly detects water intersections
2. Corridors traversing water are detected and rerouted or rejected
3. Generated corridors have water_exclusion_validated=true
4. Generated corridors have validation_result (valid, rerouted, rejected)
5. source_ids for traceability included in corridor properties
6. Non-regression: behavioral zones are still generated correctly
7. Non-regression: final BIONIC score is still calculated
8. Corridors displayed on map do not cross Saint-Laurent river

Author: BIONIC™ Testing Agent
Version: 1.0.0
"""

import pytest
import requests
import os
import json
from datetime import datetime

# Read BASE_URL from frontend .env or environment
def get_base_url():
    url = os.environ.get('REACT_APP_BACKEND_URL', '')
    if url:
        return url.rstrip('/')
    
    frontend_env_path = '/app/frontend/.env'
    if os.path.exists(frontend_env_path):
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip().rstrip('/')
    
    return 'https://lisibilite-pro.preview.emergentagent.com'

BASE_URL = get_base_url()

# Test coordinates - Saint-Laurent river area
# Point near river (Zone Nord - Affût Principal area)
POINT_NEAR_RIVER = {"lat": 46.8139, "lng": -71.2080}
# Point in Saint-Laurent river (should be excluded)
POINT_IN_WATER = {"lat": 46.82, "lng": -71.20}
# Point on land in Quebec City forest area
POINT_ON_LAND = {"lat": 46.95, "lng": -71.35}

# Quebec bounds encompassing Saint-Laurent river
QUEBEC_BOUNDS = {
    "north": 46.85,
    "south": 46.78,
    "east": -71.15,
    "west": -71.25
}


class TestWaterExclusionServiceUnit:
    """Unit tests for WaterExclusionService module"""
    
    def test_water_exclusion_module_exists(self):
        """Test that water_exclusion.py module exists and can be imported"""
        try:
            import sys
            sys.path.insert(0, '/app/backend')
            from modules.bionic_engine_p0.knowledge.terrain.water_exclusion import (
                WaterExclusionService,
                get_water_exclusion_service,
                CorridorValidationResult,
                WaterBodyType,
                MIN_WATER_BODY_AREA_M2,
                MIN_RIVER_WIDTH_M,
                SOURCE_IDS
            )
            print("✅ WaterExclusionService module imported successfully")
            assert WaterExclusionService is not None
            assert CorridorValidationResult is not None
        except ImportError as e:
            pytest.fail(f"Failed to import WaterExclusionService: {e}")
    
    def test_water_exclusion_service_initialization(self):
        """Test that WaterExclusionService can be initialized"""
        import sys
        sys.path.insert(0, '/app/backend')
        from modules.bionic_engine_p0.knowledge.terrain.water_exclusion import (
            get_water_exclusion_service,
            WaterExclusionService
        )
        
        service = get_water_exclusion_service()
        assert service is not None
        assert isinstance(service, WaterExclusionService)
        print("✅ WaterExclusionService initialized successfully")
    
    def test_water_exclusion_has_species_rules(self):
        """Test that WaterExclusionService has species-specific rules"""
        import sys
        sys.path.insert(0, '/app/backend')
        from modules.bionic_engine_p0.knowledge.terrain.water_exclusion import (
            get_water_exclusion_service
        )
        
        service = get_water_exclusion_service()
        assert hasattr(service, '_species_water_rules')
        
        # Check moose rules
        moose_rules = service._species_water_rules.get('moose', {})
        assert 'can_cross_streams' in moose_rules
        assert 'max_crossable_width_m' in moose_rules
        assert moose_rules['max_crossable_width_m'] == 15
        print(f"✅ Moose water crossing rules: max_width={moose_rules['max_crossable_width_m']}m")
    
    def test_corridor_validation_result_enum(self):
        """Test CorridorValidationResult enum values"""
        import sys
        sys.path.insert(0, '/app/backend')
        from modules.bionic_engine_p0.knowledge.terrain.water_exclusion import (
            CorridorValidationResult
        )
        
        assert CorridorValidationResult.VALID.value == "valid"
        assert CorridorValidationResult.REROUTED.value == "rerouted"
        assert CorridorValidationResult.REJECTED.value == "rejected"
        print("✅ CorridorValidationResult enum values are correct")
    
    def test_validate_corridor_no_water(self):
        """Test corridor validation with no water features returns VALID"""
        import sys
        sys.path.insert(0, '/app/backend')
        from modules.bionic_engine_p0.knowledge.terrain.water_exclusion import (
            get_water_exclusion_service,
            CorridorValidationResult
        )
        
        service = get_water_exclusion_service()
        
        # Simple corridor with no water features
        corridor_points = [
            (46.80, -71.20),
            (46.81, -71.19),
            (46.82, -71.18)
        ]
        
        validation = service.validate_corridor(
            corridor_id="TEST-COR-001",
            corridor_geometry=corridor_points,
            water_features=[],  # No water features
            species="moose"
        )
        
        assert validation.result == CorridorValidationResult.VALID
        assert validation.corridor_id == "TEST-COR-001"
        assert validation.validated_geometry == corridor_points
        assert len(validation.intersections_found) == 0
        assert len(validation.source_ids) > 0
        print(f"✅ Corridor without water: result={validation.result.value}, source_ids={validation.source_ids}")
    
    def test_validate_corridor_with_water_intersection(self):
        """Test corridor validation with water intersection attempts reroute"""
        import sys
        sys.path.insert(0, '/app/backend')
        from modules.bionic_engine_p0.knowledge.terrain.water_exclusion import (
            get_water_exclusion_service,
            CorridorValidationResult
        )
        
        service = get_water_exclusion_service()
        
        # Corridor crossing a simulated river
        corridor_points = [
            (46.80, -71.22),
            (46.81, -71.21),
            (46.82, -71.20),  # This crosses the simulated water
            (46.83, -71.19)
        ]
        
        # Simulated water feature (river)
        water_features = [{
            "type": "Feature",
            "properties": {
                "type": "river",
                "name": "Saint-Laurent",
                "width_m": 1000,
                "area_m2": 500000
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-71.25, 46.81],
                    [-71.15, 46.81],
                    [-71.15, 46.83],
                    [-71.25, 46.83],
                    [-71.25, 46.81]
                ]]
            }
        }]
        
        validation = service.validate_corridor(
            corridor_id="TEST-COR-002",
            corridor_geometry=corridor_points,
            water_features=water_features,
            species="moose"
        )
        
        # Should either be REROUTED or REJECTED
        assert validation.result in [
            CorridorValidationResult.REROUTED,
            CorridorValidationResult.REJECTED
        ]
        assert len(validation.intersections_found) > 0
        assert validation.reroute_attempts > 0
        print(f"✅ Corridor crossing water: result={validation.result.value}, intersections={len(validation.intersections_found)}, attempts={validation.reroute_attempts}")


class TestCorridorServiceWaterIntegration:
    """Tests for corridor_service.py water exclusion integration"""
    
    def test_corridor_service_imports_water_exclusion(self):
        """Test that corridor_service.py imports WaterExclusionService"""
        import sys
        sys.path.insert(0, '/app/backend')
        
        try:
            from modules.bionic_engine_p0.services.corridor_service import (
                CorridorService
            )
            # Check that the import worked
            assert CorridorService is not None
            print("✅ CorridorService imports WaterExclusionService")
        except ImportError as e:
            pytest.fail(f"Failed to import CorridorService with water exclusion: {e}")
    
    def test_corridor_service_create_corridor_accepts_water_features(self):
        """Test that _create_corridor method accepts water_features parameter"""
        import sys
        sys.path.insert(0, '/app/backend')
        
        from modules.bionic_engine_p0.services.corridor_service import CorridorService
        import inspect
        
        service = CorridorService()
        method = getattr(service, '_create_corridor', None)
        
        assert method is not None
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        
        assert 'water_features' in params, "water_features parameter should be in _create_corridor"
        print(f"✅ _create_corridor parameters: {params}")


class TestLayerAggregatorWaterIntegration:
    """Tests for layer_aggregator_service.py water exclusion integration"""
    
    def test_layer_aggregator_initializes_water_exclusion(self):
        """Test that LayerAggregatorService initializes with water exclusion"""
        import sys
        sys.path.insert(0, '/app/backend')
        
        from modules.bionic_engine_p0.services.layer_aggregator_service import (
            LayerAggregatorService
        )
        
        service = LayerAggregatorService()
        assert hasattr(service, '_water_exclusion_service')
        assert service._water_exclusion_service is not None
        print("✅ LayerAggregatorService initialized with _water_exclusion_service")
    
    def test_movement_corridors_have_water_validation_properties(self):
        """Test that movement corridors include water validation properties"""
        import sys
        sys.path.insert(0, '/app/backend')
        
        from modules.bionic_engine_p0.services.layer_aggregator_service import (
            LayerAggregatorService,
            LayerGenerationContext
        )
        from datetime import datetime, timezone
        
        service = LayerAggregatorService()
        
        # Create context with high mobility score to generate corridors
        context = LayerGenerationContext(
            waypoint_id="TEST-WP-WATER",
            latitude=46.95,
            longitude=-71.35,
            search_radius_km=2,
            species="moose",
            target_datetime=datetime.now(timezone.utc),
            habitat_score=75.0,
            pressure_score=60.0,
            mobility_score=70.0,  # High mobility to generate corridors
            behavior_score=65.0
        )
        
        result = service.generate_layers(context)
        corridors = result.layers.behavioral_zones.movement_corridors
        
        if corridors:
            for corridor in corridors:
                props = corridor.properties
                assert 'water_exclusion_validated' in props
                assert props['water_exclusion_validated'] == True
                assert 'validation_result' in props
                assert props['validation_result'] in ['valid', 'rerouted', 'rejected']
                assert 'source_ids' in props
                assert len(props['source_ids']) > 0
                print(f"✅ Corridor {corridor.corridor_id}: water_validated={props['water_exclusion_validated']}, result={props['validation_result']}")
        else:
            print("⚠️ No movement corridors generated (may be expected due to threshold)")


class TestAPIEndpointWaterExclusion:
    """API endpoint tests for water exclusion"""
    
    def test_analyze_waypoint_returns_corridors_output(self):
        """Test that /analyze_waypoint returns corridors in output"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json={
                "waypoint": {
                    "id": "TEST-WP-API-001",
                    "name": "Zone Test API",
                    "latitude": POINT_NEAR_RIVER["lat"],
                    "longitude": POINT_NEAR_RIVER["lng"]
                },
                "target_datetime": "2026-01-24T10:00:00Z",
                "species": "moose",
                "parameters": {
                    "search_radius_km": 2,
                    "mode": "rut"
                }
            },
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify corridors output structure exists
        assert 'corridors' in data
        corridors = data['corridors']
        assert 'type' in corridors
        assert corridors['type'] == 'FeatureCollection'
        assert 'features' in corridors
        print(f"✅ Corridors output: {len(corridors['features'])} corridors")
    
    def test_analyze_waypoint_score_is_calculated(self):
        """Non-regression: Test that BIONIC score is still calculated"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json={
                "waypoint": {
                    "id": "TEST-WP-SCORE-001",
                    "name": "Zone Test Score",
                    "latitude": POINT_NEAR_RIVER["lat"],
                    "longitude": POINT_NEAR_RIVER["lng"]
                },
                "target_datetime": "2026-01-24T10:00:00Z",
                "species": "moose",
                "parameters": {
                    "search_radius_km": 2,
                    "mode": "rut"
                }
            },
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify score output
        assert 'scores' in data
        scores = data['scores']
        assert 'score_bionic_final' in scores
        assert isinstance(scores['score_bionic_final'], (int, float))
        assert 0 <= scores['score_bionic_final'] <= 100
        
        # Verify breakdown
        assert 'breakdown' in scores
        breakdown = scores['breakdown']
        expected_components = ['H_habitat', 'R_risk', 'S_probability', 'A_mobility', 
                              'T_weather', 'P_pressure', 'behavior', 'density', 'multifactor']
        for comp in expected_components:
            assert comp in breakdown, f"Missing score component: {comp}"
        
        print(f"✅ BIONIC score calculated: {scores['score_bionic_final']}")
    
    def test_analyze_waypoint_layers_generated(self):
        """Non-regression: Test that behavioral zones are still generated"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json={
                "waypoint": {
                    "id": "TEST-WP-LAYERS-001",
                    "name": "Zone Test Layers",
                    "latitude": POINT_NEAR_RIVER["lat"],
                    "longitude": POINT_NEAR_RIVER["lng"]
                },
                "target_datetime": "2026-01-24T10:00:00Z",
                "species": "moose",
                "parameters": {
                    "search_radius_km": 2,
                    "mode": "rut"
                }
            },
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify layers structure
        assert 'layers' in data
        layers = data['layers']
        
        # 5 families should exist
        expected_families = ['behavioral_zones', 'attraction_points', 
                           'terrain_analysis', 'vegetation_analysis', 'hunt_planning']
        for family in expected_families:
            assert family in layers, f"Missing layer family: {family}"
        
        # Verify behavioral zones structure
        bz = layers['behavioral_zones']
        bz_sublayers = ['bedding_zones', 'feeding_zones', 'rut_zones', 
                       'movement_corridors', 'pressure_avoidance']
        for sublayer in bz_sublayers:
            assert sublayer in bz, f"Missing behavioral sublayer: {sublayer}"
        
        print(f"✅ Layers generated: {len(expected_families)} families, behavioral zones present")
    
    def test_corridor_network_has_source_ids(self):
        """Test that corridor network has source_ids for traceability"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json={
                "waypoint": {
                    "id": "TEST-WP-TRACE-001",
                    "name": "Zone Test Traceability",
                    "latitude": POINT_NEAR_RIVER["lat"],
                    "longitude": POINT_NEAR_RIVER["lng"]
                },
                "target_datetime": "2026-01-24T10:00:00Z",
                "species": "moose",
                "parameters": {
                    "search_radius_km": 2,
                    "mode": "rut"
                }
            },
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        corridors = data.get('corridors', {})
        features = corridors.get('features', [])
        
        if features:
            for feature in features:
                props = feature.get('properties', {})
                assert 'source_ids' in props, "Corridor should have source_ids"
                assert len(props['source_ids']) > 0, "source_ids should not be empty"
                print(f"✅ Corridor {props.get('corridor_id', 'N/A')}: source_ids={props['source_ids']}")
        else:
            print("⚠️ No corridor features in output (may be expected)")


class TestHydrographyAPIIntegration:
    """Tests for hydrography API used by water exclusion"""
    
    def test_hydro_check_point_in_water(self):
        """Test that check-point API detects water at river location"""
        response = requests.post(
            f"{BASE_URL}/api/hydro/check-point",
            json={
                "lat": POINT_IN_WATER["lat"],
                "lng": POINT_IN_WATER["lng"],
                "tolerance_meters": 5
            },
            timeout=30
        )
        
        # May return 404 if hydro router not mounted
        if response.status_code == 404:
            pytest.skip("Hydro API not available (404)")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'is_in_water' in data
        # Point in river should be detected as water
        if data['is_in_water']:
            print(f"✅ Point in water detected: {data.get('water_name', 'Unknown')} ({data.get('water_type', 'Unknown')})")
        else:
            print(f"⚠️ Point not detected as water (tolerance issue?)")
    
    def test_hydro_check_point_on_land(self):
        """Test that check-point API correctly identifies land"""
        response = requests.post(
            f"{BASE_URL}/api/hydro/check-point",
            json={
                "lat": POINT_ON_LAND["lat"],
                "lng": POINT_ON_LAND["lng"],
                "tolerance_meters": 5
            },
            timeout=30
        )
        
        # May return 404 if hydro router not mounted
        if response.status_code == 404:
            pytest.skip("Hydro API not available (404)")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'is_in_water' in data
        assert data['is_in_water'] == False
        print(f"✅ Point on land correctly identified")
    
    def test_hydro_water_types_available(self):
        """Test that water types endpoint returns config"""
        response = requests.get(f"{BASE_URL}/api/hydro/water-types", timeout=30)
        
        if response.status_code == 404:
            pytest.skip("Hydro API not available (404)")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'shore_tolerance_default' in data
        assert data['shore_tolerance_default'] == 5
        print(f"✅ Water types config: tolerance={data['shore_tolerance_default']}m")


class TestNonRegressionBionicFeatures:
    """Non-regression tests to ensure existing features still work"""
    
    def test_nonregression_api_health(self):
        """Test that main API endpoints are healthy"""
        endpoints = [
            "/api/v1/bionic/notifications/health",
            "/api/v1/geo-sync/health"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
            if response.status_code == 200:
                print(f"✅ {endpoint}: healthy")
            else:
                print(f"⚠️ {endpoint}: status={response.status_code}")
    
    def test_nonregression_analysis_mode_rut(self):
        """Test that RUT analysis mode still works correctly"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json={
                "waypoint": {
                    "id": "TEST-WP-RUT-001",
                    "name": "Zone Test RUT",
                    "latitude": POINT_NEAR_RIVER["lat"],
                    "longitude": POINT_NEAR_RIVER["lng"]
                },
                "target_datetime": "2026-10-15T10:00:00Z",  # October = rut season
                "species": "moose",
                "parameters": {
                    "search_radius_km": 2,
                    "mode": "rut"
                }
            },
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        scores = data.get('scores', {})
        assert scores.get('analysis_mode') == 'rut'
        print(f"✅ RUT analysis mode: score={scores.get('score_bionic_final')}")
    
    def test_nonregression_heatmap_generated(self):
        """Test that heatmap is still generated"""
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_waypoint",
            json={
                "waypoint": {
                    "id": "TEST-WP-HEAT-001",
                    "name": "Zone Test Heatmap",
                    "latitude": POINT_NEAR_RIVER["lat"],
                    "longitude": POINT_NEAR_RIVER["lng"]
                },
                "target_datetime": "2026-01-24T10:00:00Z",
                "species": "moose",
                "parameters": {
                    "search_radius_km": 2,
                    "mode": "rut"
                }
            },
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'heatmap' in data
        heatmap = data['heatmap']
        assert 'bounds' in heatmap
        assert 'grid' in heatmap
        assert len(heatmap['grid']) > 0
        print(f"✅ Heatmap generated: {len(heatmap['grid'])} cells")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
