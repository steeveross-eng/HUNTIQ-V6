"""
Test Suite for BIONIC ENGINE - Hunt Plan Analyzer Endpoint
Tests for POST /api/v1/bionic/analyze_hunt_plan and GET /api/v1/bionic/analyze_hunt_plan/status

Features tested:
- Endpoint principal d'analyse POST /api/v1/bionic/analyze_hunt_plan
- Endpoint statut GET /api/v1/bionic/analyze_hunt_plan/status
- Validation des bounds (zone géographique)
- Synthèse par espèce (moose, deer)
- Génération des fenêtres optimales globales
- Intégration correcte du scoring dynamique
- Qualité de l'analyse (partial car météo inactive)
- Réponse JSON conforme au contrat
"""

import pytest
import requests
import os
import time

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test bounds for Quebec region CA-QC
TEST_BOUNDS = {
    "north": 46.95,
    "south": 46.85,
    "east": -71.15,
    "west": -71.35
}

# Invalid bounds for testing validation
INVALID_BOUNDS = {
    "north": 200,  # Invalid latitude
    "south": 46.85,
    "east": -71.15,
    "west": -71.35
}


class TestHuntPlanAnalyzerStatus:
    """Tests for GET /api/v1/bionic/analyze_hunt_plan/status endpoint"""
    
    def test_status_returns_200(self):
        """Test that status endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Status endpoint returns 200 OK")
    
    def test_status_response_structure(self):
        """Test status response has required fields"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan/status")
        data = response.json()
        
        # Verify required fields
        assert "status" in data, "Missing 'status' field"
        assert "services" in data, "Missing 'services' field"
        assert "weather_info" in data, "Missing 'weather_info' field"
        assert "supported_species" in data, "Missing 'supported_species' field"
        assert "supported_time_ranges" in data, "Missing 'supported_time_ranges' field"
        assert "supported_hotspot_types" in data, "Missing 'supported_hotspot_types' field"
        assert "version" in data, "Missing 'version' field"
        print("✓ Status response has all required fields")
    
    def test_status_shows_operational(self):
        """Test that status is operational"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan/status")
        data = response.json()
        
        assert data["status"] == "operational", f"Expected 'operational', got {data['status']}"
        print("✓ Status shows operational")
    
    def test_services_status(self):
        """Test individual services status"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan/status")
        data = response.json()
        
        services = data["services"]
        
        # Hotspot service should be active
        assert services["hotspot_service"] == "active", "Hotspot service should be active"
        
        # Scoring service should be active
        assert services["scoring_service"] == "active", "Scoring service should be active"
        
        # Hunt plan analyzer should be active
        assert services["hunt_plan_analyzer"] == "active", "Hunt plan analyzer should be active"
        
        # Weather service should be inactive (no OWM_API_KEY)
        assert services["weather_service"] == "inactive", "Weather service should be inactive without API key"
        
        print("✓ All services status correct (weather inactive as expected)")
    
    def test_supported_species(self):
        """Test supported species list"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan/status")
        data = response.json()
        
        expected_species = ["moose", "deer", "bear", "wild_turkey", "elk"]
        
        for species in expected_species:
            assert species in data["supported_species"], f"Missing species: {species}"
        
        print(f"✓ All expected species supported: {expected_species}")
    
    def test_supported_time_ranges(self):
        """Test supported time ranges"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan/status")
        data = response.json()
        
        expected_ranges = ["24h", "72h", "7d"]
        
        for time_range in expected_ranges:
            assert time_range in data["supported_time_ranges"], f"Missing time range: {time_range}"
        
        print(f"✓ All expected time ranges supported: {expected_ranges}")
    
    def test_supported_hotspot_types(self):
        """Test supported hotspot types"""
        response = requests.get(f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan/status")
        data = response.json()
        
        expected_types = ["activity_peak", "feeding_zone", "rut_zone", "thermal_refuge", "water_source", "predation_risk"]
        
        for hotspot_type in expected_types:
            assert hotspot_type in data["supported_hotspot_types"], f"Missing hotspot type: {hotspot_type}"
        
        print(f"✓ All expected hotspot types supported")


class TestHuntPlanAnalyzerPost:
    """Tests for POST /api/v1/bionic/analyze_hunt_plan endpoint"""
    
    def test_analyze_basic_request(self):
        """Test basic analysis request with minimal parameters"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["success"] == True, "Expected success=true"
        print("✓ Basic analysis request successful")
    
    def test_analyze_multi_species(self):
        """Test analysis with multiple species (moose and deer)"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose", "deer"],
            "time_range": "24h",
            "hotspot_types": ["activity_peak", "feeding_zone"],
            "min_score_threshold": 70
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify species synthesis for both species
        species_in_synthesis = [s["species"] for s in data["species_synthesis"]]
        assert "moose" in species_in_synthesis, "Missing moose in species synthesis"
        assert "deer" in species_in_synthesis, "Missing deer in species synthesis"
        
        print("✓ Multi-species analysis successful with moose and deer")
    
    def test_response_structure_complete(self):
        """Test that response contains all required fields per contract"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose"],
            "include_scored_hotspots": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        data = response.json()
        
        # Top-level required fields
        required_fields = [
            "success", "analysis_id", "generated_at", "quality", "request",
            "summary", "species_synthesis", "global_optimal_windows",
            "weather", "global_recommendations", "scored_hotspots", "metadata"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Summary structure
        assert "total_hotspots" in data["summary"]
        assert "global_average_score" in data["summary"]
        assert "global_score_level" in data["summary"]
        
        # Request structure
        assert "bounds" in data["request"]
        assert "time_range" in data["request"]
        
        # Metadata structure
        assert "calculation_time_ms" in data["metadata"]
        assert "services" in data["metadata"]
        assert "version" in data["metadata"]
        
        print("✓ Response structure is complete per contract")
    
    def test_analysis_quality_partial(self):
        """Test that quality is 'partial' when weather is inactive"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        data = response.json()
        
        # Quality should be partial (weather inactive)
        assert data["quality"] == "partial", f"Expected 'partial', got {data['quality']}"
        
        # Weather status should reflect inactive state
        assert data["weather"]["status"] == "inactive"
        
        print("✓ Analysis quality is 'partial' as expected (weather inactive)")
    
    def test_weather_summary_inactive(self):
        """Test weather summary when service is inactive"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        data = response.json()
        weather = data["weather"]
        
        assert weather["status"] == "inactive"
        assert weather["current_conditions"] is None
        assert weather["behavior_factors"] is None
        assert weather["overall_impact"] == "neutral"
        assert "Service météo inactif" in weather["key_factors"][0]
        
        print("✓ Weather summary correctly shows inactive state")
    
    def test_species_synthesis_structure(self):
        """Test species synthesis has correct structure"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        data = response.json()
        
        assert len(data["species_synthesis"]) > 0, "Expected at least one species synthesis"
        
        synthesis = data["species_synthesis"][0]
        
        # Check required fields
        assert synthesis["species"] == "moose"
        assert synthesis["species_label"] == "Orignal"
        assert "total_hotspots" in synthesis
        assert "scores" in synthesis
        assert "average_base" in synthesis["scores"]
        assert "average_final" in synthesis["scores"]
        assert "improvement" in synthesis["scores"]
        assert "best_hotspot" in synthesis
        assert "hotspots_by_type" in synthesis
        assert "optimal_windows" in synthesis
        assert "recommendations" in synthesis
        
        print("✓ Species synthesis structure is correct")
    
    def test_global_optimal_windows(self):
        """Test global optimal windows are generated"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose", "deer"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        data = response.json()
        windows = data["global_optimal_windows"]
        
        assert len(windows) > 0, "Expected at least one optimal window"
        
        # Check window structure
        window = windows[0]
        assert "period" in window
        assert "time_range" in window
        assert "quality" in window
        assert "species_active" in window
        assert "combined_score" in window
        assert "description" in window
        
        # Check dawn and dusk windows exist
        periods = [w["period"] for w in windows]
        assert "dawn" in periods or "dusk" in periods, "Expected dawn or dusk window"
        
        print("✓ Global optimal windows generated correctly")
    
    def test_scored_hotspots_included(self):
        """Test scored hotspots are included when requested"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose"],
            "include_scored_hotspots": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        data = response.json()
        
        # Should have hotspots
        assert len(data["scored_hotspots"]) > 0, "Expected scored hotspots"
        
        # Check hotspot structure
        hotspot = data["scored_hotspots"][0]
        assert "hotspot_id" in hotspot
        assert "type" in hotspot
        assert "species" in hotspot
        assert "geometry" in hotspot
        assert "base_score" in hotspot
        assert "final_score" in hotspot
        assert "score_delta" in hotspot
        assert "dynamic_score" in hotspot
        assert "style" in hotspot
        assert "time_validity" in hotspot
        
        # Check geometry is polygon
        assert hotspot["geometry"]["type"] == "Polygon"
        assert "coordinates" in hotspot["geometry"]
        
        print(f"✓ Scored hotspots included: {len(data['scored_hotspots'])} hotspots")
    
    def test_scored_hotspots_excluded(self):
        """Test scored hotspots are excluded when not requested"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose"],
            "include_scored_hotspots": False
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        data = response.json()
        
        # Should have empty hotspots list
        assert len(data["scored_hotspots"]) == 0, "Expected no scored hotspots"
        
        print("✓ Scored hotspots excluded when not requested")
    
    def test_dynamic_scoring_integration(self):
        """Test dynamic scoring is properly integrated"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose"],
            "include_scored_hotspots": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        data = response.json()
        
        if len(data["scored_hotspots"]) > 0:
            hotspot = data["scored_hotspots"][0]
            
            # Check dynamic score structure
            dynamic = hotspot["dynamic_score"]
            assert "composite" in dynamic, "Missing composite score"
            assert "level" in dynamic, "Missing score level"
            assert "recommendations" in dynamic, "Missing recommendations"
            
            # Score delta should be calculated
            assert "score_delta" in hotspot
            
            print(f"✓ Dynamic scoring integrated: composite={dynamic['composite']}, level={dynamic['level']}")
        else:
            pytest.skip("No hotspots generated to verify dynamic scoring")
    
    def test_metadata_services_status(self):
        """Test metadata contains correct services status"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        data = response.json()
        services = data["metadata"]["services"]
        
        assert services["hotspots"] == "active", "Hotspots service should be active"
        assert services["scoring"] == "active", "Scoring service should be active"
        assert services["weather"] == "inactive", "Weather service should be inactive"
        
        print("✓ Metadata services status is correct")
    
    def test_global_recommendations(self):
        """Test global recommendations are generated"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose", "deer"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        data = response.json()
        recommendations = data["global_recommendations"]
        
        assert len(recommendations) > 0, "Expected at least one recommendation"
        
        # Should have recommendation about weather
        weather_rec_found = any("météo" in rec.lower() for rec in recommendations)
        assert weather_rec_found, "Expected recommendation about inactive weather"
        
        print(f"✓ Global recommendations generated: {len(recommendations)} items")
    
    def test_calculation_time_in_metadata(self):
        """Test calculation time is recorded in metadata"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        data = response.json()
        
        calc_time = data["metadata"]["calculation_time_ms"]
        assert calc_time > 0, "Calculation time should be positive"
        
        print(f"✓ Calculation time recorded: {calc_time:.0f}ms")


class TestHuntPlanAnalyzerValidation:
    """Tests for input validation"""
    
    def test_invalid_bounds_latitude(self):
        """Test validation of invalid latitude in bounds"""
        payload = {
            "bounds": {
                "north": 100,  # Invalid - exceeds 90
                "south": 46.85,
                "east": -71.15,
                "west": -71.35
            },
            "species": ["moose"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 422, f"Expected 422 for invalid latitude, got {response.status_code}"
        print("✓ Invalid latitude correctly rejected with 422")
    
    def test_invalid_bounds_longitude(self):
        """Test validation of invalid longitude in bounds"""
        payload = {
            "bounds": {
                "north": 46.95,
                "south": 46.85,
                "east": -200,  # Invalid - below -180
                "west": -71.35
            },
            "species": ["moose"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 422, f"Expected 422 for invalid longitude, got {response.status_code}"
        print("✓ Invalid longitude correctly rejected with 422")
    
    def test_invalid_min_score_threshold(self):
        """Test validation of invalid min_score_threshold"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose"],
            "min_score_threshold": 150  # Invalid - exceeds 100
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 422, f"Expected 422 for invalid threshold, got {response.status_code}"
        print("✓ Invalid min_score_threshold correctly rejected with 422")
    
    def test_invalid_datetime_format(self):
        """Test validation of invalid datetime format"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose"],
            "target_datetime": "not-a-date"  # Invalid format
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid datetime, got {response.status_code}"
        print("✓ Invalid datetime format correctly rejected with 400")
    
    def test_missing_bounds(self):
        """Test validation when bounds is missing"""
        payload = {
            "species": ["moose"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 422, f"Expected 422 for missing bounds, got {response.status_code}"
        print("✓ Missing bounds correctly rejected with 422")
    
    def test_valid_time_range_24h(self):
        """Test valid time_range 24h"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose"],
            "time_range": "24h"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["request"]["time_range"] == "24h"
        print("✓ time_range 24h accepted")
    
    def test_valid_iso_datetime(self):
        """Test valid ISO 8601 datetime"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose"],
            "target_datetime": "2026-02-22T10:00:00Z"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        assert response.status_code == 200
        print("✓ Valid ISO datetime accepted")


class TestHuntPlanAnalyzerEdgeCases:
    """Edge case tests"""
    
    def test_empty_species_uses_default(self):
        """Test that empty species list uses default"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": []
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        # Should still succeed - may use default or return empty synthesis
        assert response.status_code == 200
        print("✓ Empty species list handled")
    
    def test_unknown_species_ignored(self):
        """Test that unknown species are ignored gracefully"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose", "unicorn"]  # unicorn is not valid
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have synthesis only for moose
        species_in_synthesis = [s["species"] for s in data["species_synthesis"]]
        assert "moose" in species_in_synthesis
        assert "unicorn" not in species_in_synthesis
        
        print("✓ Unknown species ignored gracefully")
    
    def test_small_bounds_area(self):
        """Test with small bounds area"""
        payload = {
            "bounds": {
                "north": 46.91,
                "south": 46.90,
                "east": -71.20,
                "west": -71.21
            },
            "species": ["moose"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        assert response.status_code == 200
        print("✓ Small bounds area handled")
    
    def test_all_hotspot_types(self):
        """Test with all supported hotspot types"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose"],
            "hotspot_types": [
                "activity_peak",
                "feeding_zone",
                "rut_zone",
                "thermal_refuge",
                "water_source",
                "predation_risk"
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        assert response.status_code == 200
        print("✓ All hotspot types handled")
    
    def test_high_min_score_threshold(self):
        """Test with high minimum score threshold (may return fewer hotspots)"""
        payload = {
            "bounds": TEST_BOUNDS,
            "species": ["moose"],
            "min_score_threshold": 95
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/bionic/analyze_hunt_plan",
            json=payload,
            timeout=120
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # With high threshold, might have few or no hotspots
        print(f"✓ High threshold handled: {data['summary']['total_hotspots']} hotspots")


# Fixture for API session
@pytest.fixture
def api_session():
    """Create requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
