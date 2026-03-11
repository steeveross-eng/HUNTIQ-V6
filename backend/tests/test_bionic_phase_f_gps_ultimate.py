"""
BIONIC V5 — PHASE F GPS ULTIMATE Tests
=======================================
Tests for Observations and GPS Ultimate endpoints.

Endpoints tested:
- POST /api/v1/bionic/observations - Create observation
- GET /api/v1/bionic/observations - List observations
- GET /api/v1/bionic/observations/stats - Statistics
- POST /api/v1/bionic/observations/{id}/validate - Validate observation
- POST /api/v1/bionic/gps/hotspots/generate - Generate hotspots
- GET /api/v1/bionic/gps/hotspots/stats - Cartography stats
- POST /api/v1/bionic/gps/safety/check - Check safety
- POST /api/v1/bionic/gps/safety/report - Report danger
- GET /api/v1/bionic/gps/safety/zones - List danger zones
- GET /api/v1/bionic/gps/health - GPS Ultimate health
"""

import pytest
import requests
import os
from datetime import datetime, timezone

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestGPSUltimateHealth:
    """Health check endpoint tests"""
    
    def test_gps_health_returns_200(self):
        """Test GPS health endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/gps/health")
        assert response.status_code == 200
        print("PASSED: GPS health endpoint returns 200")
    
    def test_gps_health_response_structure(self):
        """Test GPS health response has correct structure"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/gps/health")
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["phase"] == "PHASE F - GPS ULTIMATE"
        assert data["version"] == "7.0.0"
        assert "engines" in data
        assert "auto_cartography" in data["engines"]
        assert "safety" in data["engines"]
        assert data["engines"]["auto_cartography"]["status"] == "active"
        assert data["engines"]["safety"]["status"] == "active"
        print("PASSED: GPS health response structure is correct")
    
    def test_gps_health_has_features(self):
        """Test GPS health lists available features"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/gps/health")
        data = response.json()
        
        expected_features = [
            "hotspot_generation",
            "dynamic_corridors", 
            "danger_zone_detection",
            "real_time_alerts",
            "safety_scoring"
        ]
        
        for feature in expected_features:
            assert feature in data["features"], f"Missing feature: {feature}"
        print(f"PASSED: GPS health has all {len(expected_features)} expected features")


class TestObservationsStats:
    """Observations stats endpoint tests"""
    
    def test_observations_stats_returns_200(self):
        """Test observations stats endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/observations/stats")
        assert response.status_code == 200
        print("PASSED: Observations stats returns 200")
    
    def test_observations_stats_structure(self):
        """Test observations stats response structure"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/observations/stats")
        data = response.json()
        
        assert data["status"] == "success"
        assert "statistics" in data
        stats = data["statistics"]
        
        assert "version" in stats
        assert "total_observations" in stats
        assert "validated_observations" in stats
        assert "validation_rate" in stats
        assert "by_species" in stats
        assert "by_behavior" in stats
        print("PASSED: Observations stats has correct structure")


class TestCreateObservation:
    """Create observation endpoint tests"""
    
    def test_create_observation_success(self):
        """Test creating a valid observation"""
        payload = {
            "species": "moose",
            "latitude": 46.8139,
            "longitude": -71.2080,
            "behavior": "feeding",
            "behavior_details": "Feeding on young birch shoots",
            "species_count": 1,
            "weather": "clear",
            "temperature_c": 8.5,
            "source": "direct_visual",
            "confidence": "high",
            "notes": "TEST Adult female with calf nearby",
            "observer_name": "Test Observer"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/observations",
            json=payload
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["status"] == "success"
        assert "observation" in data
        assert "observation_id" in data["observation"]
        assert data["observation"]["species"]["type"] == "moose"
        assert data["observation"]["species"]["count"] == 1
        print(f"PASSED: Created observation with ID {data['observation']['observation_id']}")
        
        return data["observation"]["observation_id"]
    
    def test_create_observation_deer(self):
        """Test creating a deer observation"""
        payload = {
            "species": "deer",
            "latitude": 45.5231,
            "longitude": -73.5673,
            "behavior": "resting",
            "species_count": 3,
            "weather": "cloudy",
            "source": "trail_camera",
            "confidence": "medium",
            "notes": "TEST Three deer resting in clearing"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/observations",
            json=payload
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["observation"]["species"]["type"] == "deer"
        assert data["observation"]["species"]["count"] == 3
        print("PASSED: Created deer observation")
    
    def test_create_observation_bear(self):
        """Test creating a bear observation"""
        payload = {
            "species": "bear",
            "latitude": 48.1234,
            "longitude": -68.5678,
            "behavior": "feeding",
            "species_count": 1,
            "weather": "rain",
            "source": "direct_visual",
            "confidence": "high",
            "notes": "TEST Bear feeding on berries"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/observations",
            json=payload
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["observation"]["species"]["type"] == "bear"
        print("PASSED: Created bear observation")
    
    def test_create_observation_with_all_fields(self):
        """Test creating observation with all optional fields"""
        payload = {
            "species": "elk",
            "latitude": 47.0000,
            "longitude": -70.0000,
            "behavior": "rut_activity",
            "behavior_details": "Male bugling during rut",
            "observation_datetime": datetime.now(timezone.utc).isoformat(),
            "duration_minutes": 30,
            "species_count": 2,
            "weather": "fog",
            "temperature_c": 5.0,
            "wind_speed_kmh": 15.0,
            "source": "audio",
            "confidence": "high",
            "notes": "TEST Elk rut activity observation",
            "observer_name": "Field Tester",
            "habitat_observed": "Forest edge",
            "terrain_type": "Hilly",
            "vegetation_type": "Mixed forest"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/observations",
            json=payload
        )
        
        assert response.status_code == 201
        data = response.json()
        
        obs = data["observation"]
        assert obs["species"]["type"] == "elk"
        assert obs["behavior"]["type"] == "rut_activity"
        assert obs["conditions"]["temperature_c"] == 5.0
        assert obs["conditions"]["wind_speed_kmh"] == 15.0
        assert obs["habitat"]["observed"] == "Forest edge"
        print("PASSED: Created observation with all fields")
    
    def test_create_observation_minimal(self):
        """Test creating observation with minimal required fields"""
        payload = {
            "species": "moose",
            "latitude": 46.0,
            "longitude": -71.0
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/observations",
            json=payload
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Should have defaults
        assert data["observation"]["behavior"]["type"] == "unknown"
        assert data["observation"]["conditions"]["weather"] == "clear"
        assert data["observation"]["source"]["confidence"] == "medium"
        print("PASSED: Created observation with minimal fields")
    
    def test_create_observation_calibration_impact(self):
        """Test observation returns calibration impact info"""
        payload = {
            "species": "moose",
            "latitude": 46.5,
            "longitude": -71.5,
            "notes": "TEST calibration impact check"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/observations",
            json=payload
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "calibration_impact" in data
        assert data["calibration_impact"]["will_contribute_to_calibration"] == True
        assert data["calibration_impact"]["requires_validation"] == True
        print("PASSED: Observation has calibration impact info")


class TestListObservations:
    """List observations endpoint tests"""
    
    def test_list_observations_returns_200(self):
        """Test list observations returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/observations")
        assert response.status_code == 200
        print("PASSED: List observations returns 200")
    
    def test_list_observations_structure(self):
        """Test list observations response structure"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/observations")
        data = response.json()
        
        assert data["status"] == "success"
        assert "total" in data
        assert "observations" in data
        assert isinstance(data["observations"], list)
        print(f"PASSED: List observations structure correct, total: {data['total']}")
    
    def test_list_observations_filter_by_species(self):
        """Test filtering observations by species"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/observations?species=moose")
        assert response.status_code == 200
        
        data = response.json()
        for obs in data["observations"]:
            assert obs["species"] == "moose"
        print(f"PASSED: Filter by species works, found {len(data['observations'])} moose observations")
    
    def test_list_observations_with_limit(self):
        """Test limiting observation results"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/observations?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["observations"]) <= 5
        print(f"PASSED: Limit works, got {len(data['observations'])} observations")


class TestValidateObservation:
    """Validate observation endpoint tests"""
    
    def test_validate_observation_success(self):
        """Test validating an existing observation"""
        # First create an observation
        create_payload = {
            "species": "moose",
            "latitude": 46.9,
            "longitude": -71.1,
            "notes": "TEST observation for validation"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/v1/bionic/observations",
            json=create_payload
        )
        
        assert create_response.status_code == 201
        obs_id = create_response.json()["observation"]["observation_id"]
        
        # Now validate it
        validate_payload = {
            "validated_by": "test_validator"
        }
        
        validate_response = requests.post(
            f"{BASE_URL}/api/v1/bionic/observations/{obs_id}/validate",
            json=validate_payload
        )
        
        assert validate_response.status_code == 200
        data = validate_response.json()
        
        assert data["status"] == "success"
        assert data["observation_id"] == obs_id
        assert data["validated_by"] == "test_validator"
        assert "validated_at" in data
        assert "calibration_status" in data
        print(f"PASSED: Validated observation {obs_id}")
    
    def test_validate_observation_not_found(self):
        """Test validating non-existent observation"""
        validate_payload = {
            "validated_by": "test_validator"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/observations/OBS-NONEXISTENT-9999/validate",
            json=validate_payload
        )
        
        assert response.status_code == 404
        print("PASSED: Non-existent observation returns 404")


class TestGenerateHotspots:
    """Generate hotspots endpoint tests"""
    
    def test_generate_hotspots_success(self):
        """Test generating hotspots"""
        payload = {
            "center_lat": 46.8139,
            "center_lng": -71.2080,
            "radius_km": 5.0,
            "species": "moose",
            "include_corridors": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/gps/hotspots/generate",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "generated_at" in data
        assert "parameters" in data
        assert "hotspots" in data
        assert "corridors" in data
        
        # Check hotspots structure
        hotspots = data["hotspots"]
        assert hotspots["type"] == "FeatureCollection"
        assert "features" in hotspots
        assert hotspots["count"] >= 1
        
        print(f"PASSED: Generated {hotspots['count']} hotspots and {data['corridors']['count']} corridors")
    
    def test_generate_hotspots_feature_structure(self):
        """Test hotspot feature structure is valid GeoJSON"""
        payload = {
            "center_lat": 46.8,
            "center_lng": -71.2,
            "radius_km": 3.0,
            "species": "deer",
            "include_corridors": False
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/gps/hotspots/generate",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for feature in data["hotspots"]["features"]:
            assert feature["type"] == "Feature"
            assert "geometry" in feature
            assert feature["geometry"]["type"] == "Polygon"
            assert "coordinates" in feature["geometry"]
            
            props = feature["properties"]
            assert "hotspot_id" in props
            assert "hotspot_type" in props
            assert "center" in props
            assert "scores" in props
            assert "intensity" in props["scores"]
            assert "confidence" in props["scores"]
            assert "probability" in props["scores"]
            assert "rendering" in props
        
        print("PASSED: Hotspot features have valid GeoJSON structure")
    
    def test_generate_hotspots_types(self):
        """Test different hotspot types are generated"""
        payload = {
            "center_lat": 46.8,
            "center_lng": -71.2,
            "radius_km": 5.0,
            "species": "moose",
            "include_corridors": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/gps/hotspots/generate",
            json=payload
        )
        
        data = response.json()
        hotspot_types = set()
        
        for feature in data["hotspots"]["features"]:
            hotspot_types.add(feature["properties"]["hotspot_type"])
        
        # Should have at least feeding, resting, water_source
        expected_types = {"feeding", "resting", "water_source"}
        found_expected = hotspot_types.intersection(expected_types)
        
        assert len(found_expected) >= 2, f"Expected at least 2 of {expected_types}, got {hotspot_types}"
        print(f"PASSED: Generated hotspot types: {hotspot_types}")
    
    def test_generate_hotspots_with_corridors(self):
        """Test corridors are generated when requested"""
        payload = {
            "center_lat": 46.8,
            "center_lng": -71.2,
            "radius_km": 5.0,
            "species": "moose",
            "include_corridors": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/gps/hotspots/generate",
            json=payload
        )
        
        data = response.json()
        corridors = data["corridors"]
        
        assert corridors["type"] == "FeatureCollection"
        # With 4+ hotspots, should have corridors connecting them
        if data["hotspots"]["count"] >= 2:
            assert corridors["count"] >= 1
            
            for feature in corridors["features"]:
                assert feature["type"] == "Feature"
                assert feature["geometry"]["type"] == "LineString"
                assert "corridor_id" in feature["properties"]
                assert "status" in feature["properties"]
                assert "scores" in feature["properties"]
        
        print(f"PASSED: Corridors generated: {corridors['count']}")


class TestHotspotsStats:
    """Hotspots stats endpoint tests"""
    
    def test_hotspots_stats_returns_200(self):
        """Test hotspots stats returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/gps/hotspots/stats")
        assert response.status_code == 200
        print("PASSED: Hotspots stats returns 200")
    
    def test_hotspots_stats_structure(self):
        """Test hotspots stats response structure"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/gps/hotspots/stats")
        data = response.json()
        
        assert data["status"] == "success"
        assert data["engine"] == "AutoCartographyEngine"
        assert "statistics" in data
        
        stats = data["statistics"]
        assert "version" in stats
        assert "hotspots_count" in stats
        assert "corridors_count" in stats
        print(f"PASSED: Hotspots stats structure correct, {stats['hotspots_count']} hotspots")


class TestSafetyCheck:
    """Safety check endpoint tests"""
    
    def test_safety_check_success(self):
        """Test safety check at position"""
        payload = {
            "lat": 46.8139,
            "lng": -71.2080,
            "radius_m": 500.0
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/gps/safety/check",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "checked_at" in data
        assert "position" in data
        assert "safety_assessment" in data
        assert "active_threats" in data
        assert "alerts" in data
        assert "metadata" in data
        
        assessment = data["safety_assessment"]
        assert "overall_score" in assessment
        assert 0 <= assessment["overall_score"] <= 1
        assert "danger_level" in assessment
        assert "is_safe" in assessment
        assert "recommendations" in assessment
        
        print(f"PASSED: Safety check - score: {assessment['overall_score']}, safe: {assessment['is_safe']}")
    
    def test_safety_check_response_structure(self):
        """Test safety check returns proper metadata"""
        payload = {
            "lat": 46.5,
            "lng": -71.5,
            "radius_m": 1000.0
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/gps/safety/check",
            json=payload
        )
        
        data = response.json()
        
        assert data["metadata"]["engine"] == "SafetyEngine"
        assert data["metadata"]["version"] == "7.0.0"
        assert data["metadata"]["phase"] == "PHASE F"
        print("PASSED: Safety check has proper metadata")


class TestReportDanger:
    """Report danger endpoint tests"""
    
    def test_report_danger_success(self):
        """Test reporting a danger"""
        payload = {
            "lat": 46.82,
            "lng": -71.20,
            "danger_type": "hunting_active",
            "description": "TEST Active hunting observed in area",
            "radius_m": 300.0
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/gps/safety/report",
            json=payload
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["status"] == "success"
        assert "danger_zone" in data
        assert "zone_id" in data
        assert "expires_at" in data
        
        zone = data["danger_zone"]
        assert zone["type"] == "Feature"
        assert zone["geometry"]["type"] == "Polygon"
        assert zone["properties"]["zone_type"] == "hunting_active"
        
        print(f"PASSED: Reported danger zone {data['zone_id']}")
    
    def test_report_danger_human_presence(self):
        """Test reporting human presence danger"""
        payload = {
            "lat": 46.9,
            "lng": -71.3,
            "danger_type": "human_presence",
            "description": "TEST Hikers spotted in area",
            "radius_m": 200.0
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/gps/safety/report",
            json=payload
        )
        
        assert response.status_code == 201
        data = response.json()
        
        zone = data["danger_zone"]
        assert zone["properties"]["zone_type"] == "human_presence"
        assert zone["properties"]["danger_level"] == "moderate"
        print("PASSED: Reported human presence danger")
    
    def test_report_danger_restricted_area(self):
        """Test reporting restricted area danger"""
        payload = {
            "lat": 47.0,
            "lng": -71.0,
            "danger_type": "restricted_area",
            "description": "TEST Private property boundary",
            "radius_m": 500.0
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/gps/safety/report",
            json=payload
        )
        
        assert response.status_code == 201
        data = response.json()
        
        zone = data["danger_zone"]
        assert zone["properties"]["zone_type"] == "restricted_area"
        assert zone["properties"]["danger_level"] == "critical"
        print("PASSED: Reported restricted area danger")


class TestListDangerZones:
    """List danger zones endpoint tests"""
    
    def test_list_danger_zones_returns_200(self):
        """Test list danger zones returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/gps/safety/zones")
        assert response.status_code == 200
        print("PASSED: List danger zones returns 200")
    
    def test_list_danger_zones_structure(self):
        """Test list danger zones response structure"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/gps/safety/zones")
        data = response.json()
        
        assert data["status"] == "success"
        assert "danger_zones" in data
        assert "filters" in data
        
        zones = data["danger_zones"]
        assert zones["type"] == "FeatureCollection"
        assert "features" in zones
        assert "count" in zones
        
        print(f"PASSED: List danger zones structure correct, {zones['count']} zones")
    
    def test_list_danger_zones_active_only(self):
        """Test list only active danger zones"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/gps/safety/zones?active_only=true")
        assert response.status_code == 200
        
        data = response.json()
        assert data["filters"]["active_only"] == True
        print("PASSED: Active only filter works")
    
    def test_list_danger_zones_all(self):
        """Test list all danger zones"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/gps/safety/zones?active_only=false")
        assert response.status_code == 200
        
        data = response.json()
        assert data["filters"]["active_only"] == False
        print("PASSED: List all zones works")


class TestSafetyStats:
    """Safety stats endpoint tests"""
    
    def test_safety_stats_returns_200(self):
        """Test safety stats returns 200"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/gps/safety/stats")
        assert response.status_code == 200
        print("PASSED: Safety stats returns 200")
    
    def test_safety_stats_structure(self):
        """Test safety stats response structure"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/gps/safety/stats")
        data = response.json()
        
        assert data["status"] == "success"
        assert data["engine"] == "SafetyEngine"
        assert "statistics" in data
        
        stats = data["statistics"]
        assert "version" in stats
        assert "total_zones" in stats
        assert "active_zones" in stats
        assert "total_alerts" in stats
        assert "pending_alerts" in stats
        print(f"PASSED: Safety stats structure correct, {stats['total_zones']} zones")


class TestObservationsHealth:
    """Observations health endpoint tests"""
    
    def test_observations_health_returns_200(self):
        """Test observations health endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/observations/health")
        assert response.status_code == 200
        print("PASSED: Observations health returns 200")
    
    def test_observations_health_structure(self):
        """Test observations health response structure"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/observations/health")
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["endpoint"] == "/api/v1/bionic/observations"
        assert data["version"] == "7.0.0"
        assert data["phase"] == "PHASE F - GPS ULTIMATE"
        assert "statistics" in data
        assert "features" in data
        
        expected_features = ["create_observation", "list_observations", "validate_observation", "statistics"]
        for feature in expected_features:
            assert feature in data["features"]
        
        print("PASSED: Observations health structure correct")


class TestIntegrationFlow:
    """Integration tests for complete workflow"""
    
    def test_complete_observation_workflow(self):
        """Test complete observation workflow: create -> list -> validate"""
        # Step 1: Create observation
        create_payload = {
            "species": "moose",
            "latitude": 46.85,
            "longitude": -71.25,
            "behavior": "feeding",
            "notes": "TEST Integration workflow observation"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/v1/bionic/observations",
            json=create_payload
        )
        assert create_response.status_code == 201
        obs_id = create_response.json()["observation"]["observation_id"]
        print(f"Step 1: Created observation {obs_id}")
        
        # Step 2: Verify in list
        list_response = requests.get(f"{BASE_URL}/api/v1/bionic/observations")
        assert list_response.status_code == 200
        observations = list_response.json()["observations"]
        obs_ids = [obs["observation_id"] for obs in observations]
        assert obs_id in obs_ids
        print("Step 2: Observation found in list")
        
        # Step 3: Validate observation
        validate_response = requests.post(
            f"{BASE_URL}/api/v1/bionic/observations/{obs_id}/validate",
            json={"validated_by": "integration_tester"}
        )
        assert validate_response.status_code == 200
        print("Step 3: Observation validated")
        
        # Step 4: Check stats updated
        stats_response = requests.get(f"{BASE_URL}/api/v1/bionic/observations/stats")
        stats = stats_response.json()["statistics"]
        assert stats["validated_observations"] >= 1
        print(f"Step 4: Stats show {stats['validated_observations']} validated observations")
        
        print("PASSED: Complete observation workflow")
    
    def test_complete_safety_workflow(self):
        """Test complete safety workflow: report -> check -> list"""
        # Step 1: Report danger
        report_payload = {
            "lat": 46.88,
            "lng": -71.22,
            "danger_type": "hunting_active",
            "description": "TEST Integration safety workflow",
            "radius_m": 250.0
        }
        
        report_response = requests.post(
            f"{BASE_URL}/api/v1/bionic/gps/safety/report",
            json=report_payload
        )
        assert report_response.status_code == 201
        zone_id = report_response.json()["zone_id"]
        print(f"Step 1: Reported danger zone {zone_id}")
        
        # Step 2: Check safety at location
        check_payload = {
            "lat": 46.88,
            "lng": -71.22,
            "radius_m": 500.0
        }
        
        check_response = requests.post(
            f"{BASE_URL}/api/v1/bionic/gps/safety/check",
            json=check_payload
        )
        assert check_response.status_code == 200
        print("Step 2: Safety check completed")
        
        # Step 3: List danger zones
        list_response = requests.get(f"{BASE_URL}/api/v1/bionic/gps/safety/zones")
        assert list_response.status_code == 200
        zones = list_response.json()["danger_zones"]
        zone_ids = [f["properties"]["zone_id"] for f in zones["features"]]
        assert zone_id in zone_ids
        print("Step 3: Danger zone found in list")
        
        print("PASSED: Complete safety workflow")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
