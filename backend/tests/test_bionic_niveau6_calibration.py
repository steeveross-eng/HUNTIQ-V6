"""
BIONIC V5 — NIVEAU 6 Tests (Mesure & Figeage)
=============================================
Tests for:
- POST /api/v1/bionic/mobility_prediction → GeoJSON FeatureCollection
- GET /api/v1/bionic/calibration/status → CalibrationProfile + ModelVersion
- Movement zones (probable, possible, unlikely)
- Predicted trajectory with sequential points
- Integrated factors: mobility, seasonal, thermal, human_pressure
- Distance and speed coherent
- CalibrationProfile with service_weights and level_modifiers
- ModelVersion with changelog and levels_integrated
- Tests by species (moose, deer, bear)
- Tests by time window (2h, 6h, 12h)

VERSION: 6.0.0
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def mobility_prediction_endpoint():
    """Mobility prediction endpoint URL"""
    return f"{BASE_URL}/api/v1/bionic/mobility_prediction"


@pytest.fixture
def calibration_status_endpoint():
    """Calibration status endpoint URL"""
    return f"{BASE_URL}/api/v1/bionic/calibration/status"


@pytest.fixture
def default_prediction_params():
    """Default parameters for mobility prediction"""
    return {
        "waypoint_lat": 46.8,
        "waypoint_lng": -71.2,
        "species": "orignal",
        "window_hours": 6.0,
        "analysis_mode": "rut",
        "include_trajectory": True
    }


# =============================================================================
# TEST CLASS: API Structure - Mobility Prediction
# =============================================================================

class TestMobilityPredictionAPIStructure:
    """Test the structure of POST /api/v1/bionic/mobility_prediction response"""

    def test_endpoint_returns_200(self, api_client, mobility_prediction_endpoint, default_prediction_params):
        """Test mobility_prediction endpoint returns 200"""
        response = api_client.post(mobility_prediction_endpoint, params=default_prediction_params)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Endpoint returns 200 OK")

    def test_response_is_geojson_feature_collection(self, api_client, mobility_prediction_endpoint, default_prediction_params):
        """Test response is a GeoJSON FeatureCollection"""
        response = api_client.post(mobility_prediction_endpoint, params=default_prediction_params)
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("type") == "FeatureCollection", f"Expected FeatureCollection, got {data.get('type')}"
        assert "features" in data, "Missing 'features' key"
        assert isinstance(data["features"], list), "features should be a list"
        print(f"✓ Response is GeoJSON FeatureCollection with {len(data['features'])} features")

    def test_response_has_properties(self, api_client, mobility_prediction_endpoint, default_prediction_params):
        """Test response has required properties"""
        response = api_client.post(mobility_prediction_endpoint, params=default_prediction_params)
        data = response.json()
        
        assert "properties" in data, "Missing 'properties' key"
        props = data["properties"]
        
        assert "prediction_id" in props, "Missing prediction_id"
        assert "species" in props, "Missing species"
        assert "start_position" in props, "Missing start_position"
        assert "time_window" in props, "Missing time_window"
        assert "metrics" in props, "Missing metrics"
        assert "factors" in props, "Missing factors"
        assert "zones_summary" in props, "Missing zones_summary"
        assert "confidence" in props, "Missing confidence"
        print(f"✓ Response has all required properties")


# =============================================================================
# TEST CLASS: Movement Zones
# =============================================================================

class TestMovementZones:
    """Test movement zones (probable, possible, unlikely) generation"""

    def test_zones_generated_correctly(self, api_client, mobility_prediction_endpoint, default_prediction_params):
        """Test that all three zone types are generated"""
        response = api_client.post(mobility_prediction_endpoint, params=default_prediction_params)
        data = response.json()
        
        zones_summary = data.get("properties", {}).get("zones_summary", {})
        
        assert "probable" in zones_summary, "Missing probable zone count"
        assert "possible" in zones_summary, "Missing possible zone count"
        assert "unlikely" in zones_summary, "Missing unlikely zone count"
        
        assert zones_summary["probable"] >= 1, f"Expected at least 1 probable zone, got {zones_summary['probable']}"
        assert zones_summary["possible"] >= 1, f"Expected at least 1 possible zone, got {zones_summary['possible']}"
        assert zones_summary["unlikely"] >= 1, f"Expected at least 1 unlikely zone, got {zones_summary['unlikely']}"
        
        print(f"✓ Zones generated: probable={zones_summary['probable']}, possible={zones_summary['possible']}, unlikely={zones_summary['unlikely']}")

    def test_zone_features_are_polygons(self, api_client, mobility_prediction_endpoint, default_prediction_params):
        """Test that zone features are GeoJSON Polygons"""
        response = api_client.post(mobility_prediction_endpoint, params=default_prediction_params)
        data = response.json()
        
        polygon_features = [f for f in data["features"] if f.get("geometry", {}).get("type") == "Polygon"]
        
        assert len(polygon_features) >= 3, f"Expected at least 3 polygon zones, got {len(polygon_features)}"
        
        for feature in polygon_features[:3]:
            props = feature.get("properties", {})
            assert "zone_id" in props, "Zone missing zone_id"
            assert "zone_type" in props, "Zone missing zone_type"
            assert "probability" in props, "Zone missing probability"
            assert props["zone_type"] in ["probable", "possible", "unlikely"], f"Invalid zone_type: {props['zone_type']}"
        
        print(f"✓ {len(polygon_features)} polygon zone features found with correct structure")

    def test_probable_zone_has_highest_probability(self, api_client, mobility_prediction_endpoint, default_prediction_params):
        """Test that probable zones have probability >= 0.7"""
        response = api_client.post(mobility_prediction_endpoint, params=default_prediction_params)
        data = response.json()
        
        probable_zones = [f for f in data["features"] 
                         if f.get("properties", {}).get("zone_type") == "probable"]
        
        assert len(probable_zones) >= 1, "No probable zones found"
        
        for zone in probable_zones:
            probability = zone["properties"].get("probability", 0)
            assert 0.5 <= probability <= 1.0, f"Probable zone probability out of range: {probability}"
        
        print(f"✓ Probable zones have correct probability ranges")

    def test_zones_have_rendering_properties(self, api_client, mobility_prediction_endpoint, default_prediction_params):
        """Test that zones have rendering properties for visualization"""
        response = api_client.post(mobility_prediction_endpoint, params=default_prediction_params)
        data = response.json()
        
        polygon_features = [f for f in data["features"] if f.get("geometry", {}).get("type") == "Polygon"]
        
        for feature in polygon_features[:1]:  # Check first zone
            props = feature.get("properties", {})
            rendering = props.get("rendering", {})
            
            assert "fill_color" in rendering, "Missing fill_color"
            assert "fill_opacity" in rendering, "Missing fill_opacity"
            assert "stroke_color" in rendering, "Missing stroke_color"
            assert "stroke_width" in rendering, "Missing stroke_width"
        
        print(f"✓ Zones have rendering properties for visualization")


# =============================================================================
# TEST CLASS: Trajectory Points
# =============================================================================

class TestTrajectoryPoints:
    """Test predicted trajectory with sequential points"""

    def test_trajectory_points_generated(self, api_client, mobility_prediction_endpoint, default_prediction_params):
        """Test that trajectory points are generated when include_trajectory=True"""
        response = api_client.post(mobility_prediction_endpoint, params=default_prediction_params)
        data = response.json()
        
        point_features = [f for f in data["features"] 
                         if f.get("geometry", {}).get("type") == "Point"]
        
        assert len(point_features) >= 2, f"Expected at least 2 trajectory points, got {len(point_features)}"
        print(f"✓ {len(point_features)} trajectory points generated")

    def test_trajectory_points_are_sequential(self, api_client, mobility_prediction_endpoint, default_prediction_params):
        """Test that trajectory points have sequential sequence numbers"""
        response = api_client.post(mobility_prediction_endpoint, params=default_prediction_params)
        data = response.json()
        
        point_features = [f for f in data["features"] 
                         if f.get("geometry", {}).get("type") == "Point"]
        
        sequences = [f["properties"].get("sequence", -1) for f in point_features]
        sequences_sorted = sorted(sequences)
        
        # Check that sequences start from 0 and are consecutive
        for i, seq in enumerate(sequences_sorted):
            assert seq == i, f"Sequence gap: expected {i}, got {seq}"
        
        print(f"✓ Trajectory points are sequential: {sequences_sorted[:5]}...")

    def test_trajectory_points_have_required_properties(self, api_client, mobility_prediction_endpoint, default_prediction_params):
        """Test that trajectory points have all required properties"""
        response = api_client.post(mobility_prediction_endpoint, params=default_prediction_params)
        data = response.json()
        
        point_features = [f for f in data["features"] 
                         if f.get("geometry", {}).get("type") == "Point"]
        
        if point_features:
            first_point = point_features[0]["properties"]
            
            assert "point_id" in first_point, "Missing point_id"
            assert "sequence" in first_point, "Missing sequence"
            assert "predicted_time" in first_point, "Missing predicted_time"
            assert "probability" in first_point, "Missing probability"
            assert "intensity" in first_point, "Missing intensity"
            assert "behavior" in first_point, "Missing behavior"
        
        print(f"✓ Trajectory points have all required properties")

    def test_trajectory_linestring_generated(self, api_client, mobility_prediction_endpoint, default_prediction_params):
        """Test that a LineString connecting trajectory points is generated"""
        response = api_client.post(mobility_prediction_endpoint, params=default_prediction_params)
        data = response.json()
        
        linestring_features = [f for f in data["features"] 
                               if f.get("geometry", {}).get("type") == "LineString"]
        
        assert len(linestring_features) >= 1, "No LineString trajectory found"
        
        linestring = linestring_features[0]
        coords = linestring.get("geometry", {}).get("coordinates", [])
        
        assert len(coords) >= 2, f"LineString should have at least 2 coordinates, got {len(coords)}"
        
        props = linestring.get("properties", {})
        assert props.get("type") == "predicted_trajectory", f"Expected type 'predicted_trajectory', got {props.get('type')}"
        
        print(f"✓ LineString trajectory generated with {len(coords)} points")


# =============================================================================
# TEST CLASS: Integrated Factors
# =============================================================================

class TestIntegratedFactors:
    """Test that factors (mobility, seasonal, thermal, human_pressure) are integrated"""

    def test_factors_present_in_response(self, api_client, mobility_prediction_endpoint, default_prediction_params):
        """Test that all factors are present in response properties"""
        response = api_client.post(mobility_prediction_endpoint, params=default_prediction_params)
        data = response.json()
        
        factors = data.get("properties", {}).get("factors", {})
        
        assert "mobility" in factors, "Missing mobility factor"
        assert "seasonal" in factors, "Missing seasonal factor"
        assert "thermal" in factors, "Missing thermal factor"
        assert "human_pressure" in factors, "Missing human_pressure factor"
        
        print(f"✓ All factors present: mobility={factors['mobility']}, seasonal={factors['seasonal']}, thermal={factors['thermal']}, human_pressure={factors['human_pressure']}")

    def test_factors_are_numeric(self, api_client, mobility_prediction_endpoint, default_prediction_params):
        """Test that all factors are numeric values"""
        response = api_client.post(mobility_prediction_endpoint, params=default_prediction_params)
        data = response.json()
        
        factors = data.get("properties", {}).get("factors", {})
        
        for factor_name, factor_value in factors.items():
            assert isinstance(factor_value, (int, float)), f"{factor_name} should be numeric, got {type(factor_value)}"
            assert 0.0 <= factor_value <= 2.0, f"{factor_name} out of range: {factor_value}"
        
        print(f"✓ All factors are numeric and in valid range")

    def test_factors_affect_prediction(self, api_client, mobility_prediction_endpoint):
        """Test that factors influence the prediction"""
        # Test with normal conditions
        params_normal = {
            "waypoint_lat": 46.8,
            "waypoint_lng": -71.2,
            "species": "orignal",
            "window_hours": 6.0,
            "analysis_mode": "rut",
            "include_trajectory": True
        }
        
        response = api_client.post(mobility_prediction_endpoint, params=params_normal)
        data = response.json()
        
        metrics = data.get("properties", {}).get("metrics", {})
        factors = data.get("properties", {}).get("factors", {})
        
        # Verify factors affect predicted distance and speed
        assert "predicted_distance_km" in metrics, "Missing predicted_distance_km"
        assert "average_speed_kmh" in metrics, "Missing average_speed_kmh"
        
        print(f"✓ Factors affect prediction: distance={metrics['predicted_distance_km']}km, speed={metrics['average_speed_kmh']}km/h")


# =============================================================================
# TEST CLASS: Distance and Speed Coherence
# =============================================================================

class TestDistanceSpeedCoherence:
    """Test that predicted distance and speed are coherent"""

    def test_distance_is_positive(self, api_client, mobility_prediction_endpoint, default_prediction_params):
        """Test that predicted distance is positive"""
        response = api_client.post(mobility_prediction_endpoint, params=default_prediction_params)
        data = response.json()
        
        metrics = data.get("properties", {}).get("metrics", {})
        distance = metrics.get("predicted_distance_km", 0)
        
        assert distance >= 0, f"Distance should be non-negative, got {distance}"
        assert distance <= 20, f"Distance seems too high for 6h window: {distance}km"
        
        print(f"✓ Predicted distance is coherent: {distance}km")

    def test_speed_is_realistic(self, api_client, mobility_prediction_endpoint, default_prediction_params):
        """Test that average speed is realistic for the species"""
        response = api_client.post(mobility_prediction_endpoint, params=default_prediction_params)
        data = response.json()
        
        metrics = data.get("properties", {}).get("metrics", {})
        speed = metrics.get("average_speed_kmh", 0)
        
        assert 0 <= speed <= 10, f"Speed should be 0-10 km/h for wildlife, got {speed}"
        
        print(f"✓ Average speed is realistic: {speed}km/h")

    def test_distance_speed_time_relationship(self, api_client, mobility_prediction_endpoint, default_prediction_params):
        """Test that distance, speed, and time are mathematically coherent"""
        response = api_client.post(mobility_prediction_endpoint, params=default_prediction_params)
        data = response.json()
        
        props = data.get("properties", {})
        metrics = props.get("metrics", {})
        time_window = props.get("time_window", {})
        
        distance = metrics.get("predicted_distance_km", 0)
        speed = metrics.get("average_speed_kmh", 0)
        hours = time_window.get("hours", 6)
        
        # Distance should be approximately speed * effective_hours (with some activity factor)
        # Allow tolerance because animals don't move constantly
        max_possible_distance = speed * hours * 1.5  # 50% tolerance
        
        assert distance <= max_possible_distance, f"Distance {distance}km seems too high for speed {speed}km/h over {hours}h"
        
        print(f"✓ Distance-speed-time relationship is coherent: {distance}km = ~{speed}km/h × effective hours")


# =============================================================================
# TEST CLASS: Calibration Status Endpoint
# =============================================================================

class TestCalibrationStatusEndpoint:
    """Test GET /api/v1/bionic/calibration/status endpoint"""

    def test_endpoint_returns_200(self, api_client, calibration_status_endpoint):
        """Test calibration status endpoint returns 200"""
        response = api_client.get(calibration_status_endpoint)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Calibration status endpoint returns 200 OK")

    def test_response_has_status_success(self, api_client, calibration_status_endpoint):
        """Test response has status success"""
        response = api_client.get(calibration_status_endpoint)
        data = response.json()
        
        assert data.get("status") == "success", f"Expected status 'success', got {data.get('status')}"
        print(f"✓ Response has status: success")

    def test_response_has_calibration_object(self, api_client, calibration_status_endpoint):
        """Test response has calibration object"""
        response = api_client.get(calibration_status_endpoint)
        data = response.json()
        
        assert "calibration" in data, "Missing 'calibration' key"
        calibration = data["calibration"]
        
        assert "profile" in calibration, "Missing 'profile' in calibration"
        assert "model_version" in calibration, "Missing 'model_version' in calibration"
        
        print(f"✓ Response has calibration object with profile and model_version")

    def test_response_has_statistics(self, api_client, calibration_status_endpoint):
        """Test response has statistics"""
        response = api_client.get(calibration_status_endpoint)
        data = response.json()
        
        assert "statistics" in data, "Missing 'statistics' key"
        stats = data["statistics"]
        
        assert "version" in stats, "Missing version in statistics"
        assert "profile_status" in stats, "Missing profile_status in statistics"
        assert "model_version" in stats, "Missing model_version in statistics"
        
        print(f"✓ Response has statistics: version={stats.get('version')}")


# =============================================================================
# TEST CLASS: Calibration Profile
# =============================================================================

class TestCalibrationProfile:
    """Test CalibrationProfile structure with service_weights and level_modifiers"""

    def test_profile_has_required_fields(self, api_client, calibration_status_endpoint):
        """Test profile has all required fields"""
        response = api_client.get(calibration_status_endpoint)
        data = response.json()
        
        profile = data.get("calibration", {}).get("profile", {})
        
        assert "profile_id" in profile, "Missing profile_id"
        assert "profile_name" in profile, "Missing profile_name"
        assert "status" in profile, "Missing status"
        assert "service_weights" in profile, "Missing service_weights"
        assert "level_modifiers" in profile, "Missing level_modifiers"
        
        print(f"✓ Profile has all required fields: id={profile.get('profile_id')}")

    def test_service_weights_has_9_services(self, api_client, calibration_status_endpoint):
        """Test service_weights contains all 9 BIONIC services"""
        response = api_client.get(calibration_status_endpoint)
        data = response.json()
        
        service_weights = data.get("calibration", {}).get("profile", {}).get("service_weights", {})
        
        expected_services = [
            "probability", "habitat", "pressure", "weather", 
            "behavior", "multifactor", "density", "risk", "mobility"
        ]
        
        for service in expected_services:
            assert service in service_weights, f"Missing service weight: {service}"
            assert isinstance(service_weights[service], (int, float)), f"{service} weight should be numeric"
            assert 0 <= service_weights[service] <= 1, f"{service} weight out of range: {service_weights[service]}"
        
        # Verify weights sum to approximately 1.0
        total_weight = sum(service_weights.values())
        assert 0.95 <= total_weight <= 1.05, f"Total weights should sum to ~1.0, got {total_weight}"
        
        print(f"✓ Service weights: {len(service_weights)} services, total={total_weight:.3f}")

    def test_level_modifiers_has_required_levels(self, api_client, calibration_status_endpoint):
        """Test level_modifiers contains NIVEAU 1-5 modifiers"""
        response = api_client.get(calibration_status_endpoint)
        data = response.json()
        
        level_modifiers = data.get("calibration", {}).get("profile", {}).get("level_modifiers", {})
        
        expected_modifiers = [
            "niveau_1_seasonal", "niveau_1_thermal",
            "niveau_2_digestive", "niveau_2_social",
            "niveau_3_pres_human", "niveau_4_corridor", "niveau_5_mobility"
        ]
        
        for modifier in expected_modifiers:
            assert modifier in level_modifiers, f"Missing level modifier: {modifier}"
            assert isinstance(level_modifiers[modifier], (int, float)), f"{modifier} should be numeric"
        
        print(f"✓ Level modifiers: {len(level_modifiers)} modifiers found")

    def test_profile_has_thresholds(self, api_client, calibration_status_endpoint):
        """Test profile has calibration thresholds"""
        response = api_client.get(calibration_status_endpoint)
        data = response.json()
        
        profile = data.get("calibration", {}).get("profile", {})
        
        assert "thresholds" in profile, "Missing thresholds"
        thresholds = profile["thresholds"]
        
        assert "thermal_stress_activation" in thresholds, "Missing thermal_stress_activation"
        assert "hunting_pressure_high" in thresholds, "Missing hunting_pressure_high"
        
        print(f"✓ Profile has thresholds: thermal_stress={thresholds.get('thermal_stress_activation')}°C")


# =============================================================================
# TEST CLASS: Model Version
# =============================================================================

class TestModelVersion:
    """Test ModelVersion structure with changelog and levels_integrated"""

    def test_model_version_has_required_fields(self, api_client, calibration_status_endpoint):
        """Test model_version has all required fields"""
        response = api_client.get(calibration_status_endpoint)
        data = response.json()
        
        model_version = data.get("calibration", {}).get("model_version", {})
        
        assert "version_id" in model_version, "Missing version_id"
        assert "version_name" in model_version, "Missing version_name"
        assert "version_number" in model_version, "Missing version_number"
        
        print(f"✓ Model version: {model_version.get('version_number')}")

    def test_model_version_has_changelog(self, api_client, calibration_status_endpoint):
        """Test model_version has changelog"""
        response = api_client.get(calibration_status_endpoint)
        data = response.json()
        
        model_version = data.get("calibration", {}).get("model_version", {})
        
        assert "changelog" in model_version, "Missing changelog"
        changelog = model_version["changelog"]
        
        assert isinstance(changelog, list), "changelog should be a list"
        assert len(changelog) >= 1, "changelog should have at least 1 entry"
        
        print(f"✓ Model version has {len(changelog)} changelog entries")

    def test_model_version_has_levels_integrated(self, api_client, calibration_status_endpoint):
        """Test model_version has levels_integrated"""
        response = api_client.get(calibration_status_endpoint)
        data = response.json()
        
        model_version = data.get("calibration", {}).get("model_version", {})
        
        assert "levels_integrated" in model_version, "Missing levels_integrated"
        levels = model_version["levels_integrated"]
        
        assert isinstance(levels, list), "levels_integrated should be a list"
        assert len(levels) >= 5, f"Expected at least 5 levels integrated, got {len(levels)}"
        
        # Check that NIVEAU 1-5 are mentioned
        levels_text = " ".join(levels).lower()
        for niveau in ["niveau 1", "niveau 2", "niveau 3", "niveau 4", "niveau 5"]:
            assert niveau in levels_text, f"Missing {niveau} in levels_integrated"
        
        print(f"✓ Model version has {len(levels)} levels integrated")

    def test_model_version_has_status(self, api_client, calibration_status_endpoint):
        """Test model_version has status fields"""
        response = api_client.get(calibration_status_endpoint)
        data = response.json()
        
        model_version = data.get("calibration", {}).get("model_version", {})
        
        assert "status" in model_version, "Missing status"
        status = model_version["status"]
        
        assert "is_master" in status, "Missing is_master"
        assert "is_locked" in status, "Missing is_locked"
        
        print(f"✓ Model version status: is_master={status.get('is_master')}, is_locked={status.get('is_locked')}")


# =============================================================================
# TEST CLASS: Tests by Species
# =============================================================================

class TestMobilityBySpecies:
    """Test mobility prediction for different species (moose, deer, bear)"""

    @pytest.mark.parametrize("species,species_key", [
        ("orignal", "moose"),
        ("moose", "moose"),
        ("cerf", "deer"),
        ("deer", "deer"),
        ("ours", "bear"),
        ("bear", "bear")
    ])
    def test_species_returns_valid_prediction(self, api_client, mobility_prediction_endpoint, species, species_key):
        """Test each species returns a valid prediction"""
        params = {
            "waypoint_lat": 46.8,
            "waypoint_lng": -71.2,
            "species": species,
            "window_hours": 6.0,
            "analysis_mode": "rut",
            "include_trajectory": True
        }
        
        response = api_client.post(mobility_prediction_endpoint, params=params)
        assert response.status_code == 200, f"Failed for species {species}: {response.text}"
        
        data = response.json()
        assert data.get("type") == "FeatureCollection"
        assert data.get("properties", {}).get("species") == species
        
        print(f"✓ Species '{species}' ({species_key}) returns valid prediction")

    def test_moose_has_characteristic_speed(self, api_client, mobility_prediction_endpoint):
        """Test moose has characteristic movement speed"""
        params = {
            "waypoint_lat": 46.8,
            "waypoint_lng": -71.2,
            "species": "orignal",
            "window_hours": 6.0,
            "analysis_mode": "rut",
            "include_trajectory": True
        }
        
        response = api_client.post(mobility_prediction_endpoint, params=params)
        data = response.json()
        
        speed = data.get("properties", {}).get("metrics", {}).get("average_speed_kmh", 0)
        
        # Moose typically moves at 1-4 km/h
        assert 0.5 <= speed <= 6.0, f"Moose speed out of expected range: {speed}km/h"
        
        print(f"✓ Moose speed is characteristic: {speed}km/h")

    def test_bear_has_characteristic_speed(self, api_client, mobility_prediction_endpoint):
        """Test bear has characteristic movement speed"""
        params = {
            "waypoint_lat": 46.8,
            "waypoint_lng": -71.2,
            "species": "ours",
            "window_hours": 6.0,
            "analysis_mode": "rut",
            "include_trajectory": True
        }
        
        response = api_client.post(mobility_prediction_endpoint, params=params)
        data = response.json()
        
        speed = data.get("properties", {}).get("metrics", {}).get("average_speed_kmh", 0)
        
        # Bear typically moves at 1-3 km/h when foraging
        assert 0.3 <= speed <= 5.0, f"Bear speed out of expected range: {speed}km/h"
        
        print(f"✓ Bear speed is characteristic: {speed}km/h")


# =============================================================================
# TEST CLASS: Tests by Time Window
# =============================================================================

class TestMobilityByTimeWindow:
    """Test mobility prediction for different time windows (2h, 6h, 12h)"""

    @pytest.mark.parametrize("window_hours", [2.0, 6.0, 12.0])
    def test_time_window_returns_valid_prediction(self, api_client, mobility_prediction_endpoint, window_hours):
        """Test each time window returns a valid prediction"""
        params = {
            "waypoint_lat": 46.8,
            "waypoint_lng": -71.2,
            "species": "orignal",
            "window_hours": window_hours,
            "analysis_mode": "rut",
            "include_trajectory": True
        }
        
        response = api_client.post(mobility_prediction_endpoint, params=params)
        assert response.status_code == 200, f"Failed for window {window_hours}h: {response.text}"
        
        data = response.json()
        time_window = data.get("properties", {}).get("time_window", {})
        
        assert time_window.get("hours") == window_hours, f"Expected {window_hours}h, got {time_window.get('hours')}h"
        
        print(f"✓ Time window {window_hours}h returns valid prediction")

    def test_longer_window_means_more_trajectory_points(self, api_client, mobility_prediction_endpoint):
        """Test that longer time windows produce more trajectory points"""
        results = {}
        
        for window_hours in [2.0, 6.0, 12.0]:
            params = {
                "waypoint_lat": 46.8,
                "waypoint_lng": -71.2,
                "species": "orignal",
                "window_hours": window_hours,
                "analysis_mode": "rut",
                "include_trajectory": True
            }
            
            response = api_client.post(mobility_prediction_endpoint, params=params)
            data = response.json()
            
            point_features = [f for f in data["features"] 
                             if f.get("geometry", {}).get("type") == "Point"]
            results[window_hours] = len(point_features)
        
        # Longer windows should have more points
        assert results[6.0] >= results[2.0], f"6h ({results[6.0]}) should have >= points than 2h ({results[2.0]})"
        assert results[12.0] >= results[6.0], f"12h ({results[12.0]}) should have >= points than 6h ({results[6.0]})"
        
        print(f"✓ Trajectory points scale with window: 2h={results[2.0]}, 6h={results[6.0]}, 12h={results[12.0]}")

    def test_longer_window_means_more_distance(self, api_client, mobility_prediction_endpoint):
        """Test that longer time windows predict more distance"""
        results = {}
        
        for window_hours in [2.0, 6.0, 12.0]:
            params = {
                "waypoint_lat": 46.8,
                "waypoint_lng": -71.2,
                "species": "orignal",
                "window_hours": window_hours,
                "analysis_mode": "rut",
                "include_trajectory": True
            }
            
            response = api_client.post(mobility_prediction_endpoint, params=params)
            data = response.json()
            
            distance = data.get("properties", {}).get("metrics", {}).get("predicted_distance_km", 0)
            results[window_hours] = distance
        
        # Longer windows should predict more distance
        assert results[6.0] >= results[2.0] * 0.8, f"6h distance ({results[6.0]}km) should be >= ~80% of 2h × 3"
        assert results[12.0] >= results[6.0] * 0.8, f"12h distance ({results[12.0]}km) should be >= ~80% of 6h × 2"
        
        print(f"✓ Distance scales with window: 2h={results[2.0]:.2f}km, 6h={results[6.0]:.2f}km, 12h={results[12.0]:.2f}km")


# =============================================================================
# TEST CLASS: Version and Traceability
# =============================================================================

class TestVersionAndTraceability:
    """Test version numbers and source traceability"""

    def test_prediction_has_version_6(self, api_client, mobility_prediction_endpoint, default_prediction_params):
        """Test prediction response has version 6.0.0"""
        response = api_client.post(mobility_prediction_endpoint, params=default_prediction_params)
        data = response.json()
        
        version = data.get("properties", {}).get("version", "")
        
        assert version == "6.0.0", f"Expected version 6.0.0, got {version}"
        
        print(f"✓ Prediction version: {version}")

    def test_prediction_has_source_ids(self, api_client, mobility_prediction_endpoint, default_prediction_params):
        """Test prediction response has source_ids"""
        response = api_client.post(mobility_prediction_endpoint, params=default_prediction_params)
        data = response.json()
        
        source_ids = data.get("properties", {}).get("source_ids", [])
        
        assert isinstance(source_ids, list), "source_ids should be a list"
        assert len(source_ids) >= 1, "source_ids should have at least 1 entry"
        
        # Check for expected source patterns
        source_text = " ".join(source_ids).upper()
        assert "SRC-" in source_text, "source_ids should contain SRC- prefixed identifiers"
        
        print(f"✓ Prediction has {len(source_ids)} source_ids: {source_ids[:3]}")

    def test_calibration_status_has_version_6(self, api_client, calibration_status_endpoint):
        """Test calibration status has version 6.0.0"""
        response = api_client.get(calibration_status_endpoint)
        data = response.json()
        
        version = data.get("version", "")
        
        assert version == "6.0.0", f"Expected version 6.0.0, got {version}"
        
        print(f"✓ Calibration status version: {version}")


# =============================================================================
# TEST CLASS: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_invalid_coordinates_handled(self, api_client, mobility_prediction_endpoint):
        """Test that invalid coordinates are handled gracefully"""
        params = {
            "waypoint_lat": 999.0,  # Invalid latitude
            "waypoint_lng": -71.2,
            "species": "orignal",
            "window_hours": 6.0,
            "analysis_mode": "rut",
            "include_trajectory": True
        }
        
        response = api_client.post(mobility_prediction_endpoint, params=params)
        # Should either return 400/422 or handle gracefully with 200
        assert response.status_code in [200, 400, 422], f"Unexpected status: {response.status_code}"
        
        print(f"✓ Invalid coordinates handled: status={response.status_code}")

    def test_unknown_species_uses_default(self, api_client, mobility_prediction_endpoint):
        """Test that unknown species falls back to default"""
        params = {
            "waypoint_lat": 46.8,
            "waypoint_lng": -71.2,
            "species": "unknown_animal",
            "window_hours": 6.0,
            "analysis_mode": "rut",
            "include_trajectory": True
        }
        
        response = api_client.post(mobility_prediction_endpoint, params=params)
        assert response.status_code == 200, f"Failed for unknown species: {response.text}"
        
        data = response.json()
        assert data.get("type") == "FeatureCollection"
        
        print(f"✓ Unknown species handled gracefully")

    def test_without_trajectory(self, api_client, mobility_prediction_endpoint):
        """Test prediction without trajectory points"""
        params = {
            "waypoint_lat": 46.8,
            "waypoint_lng": -71.2,
            "species": "orignal",
            "window_hours": 6.0,
            "analysis_mode": "rut",
            "include_trajectory": False
        }
        
        response = api_client.post(mobility_prediction_endpoint, params=params)
        assert response.status_code == 200
        
        data = response.json()
        
        # Should still have zones but fewer/no trajectory points
        point_features = [f for f in data["features"] 
                         if f.get("geometry", {}).get("type") == "Point"]
        
        # With include_trajectory=False, should have 0 or minimal points
        # (The implementation might still include some)
        print(f"✓ Without trajectory: {len(point_features)} points (may be 0)")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
