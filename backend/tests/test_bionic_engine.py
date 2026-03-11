"""
BIONIC™ Territory Engine API Tests
===================================
Tests for the BIONIC analysis engine including:
- 8 Thematic Modules (Thermal, Wetness, Food, Pressure, Access, Corridor, GeoForm, Canopy)
- 6 Wildlife Models (Moose, Deer, Bear, Caribou, Wolf, Turkey)
- AI Predictions (24h, 72h, 7d forecasts)
- Temporal Analysis (NDVI/NDWI trends)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestBionicModules:
    """Tests for BIONIC module endpoints"""
    
    def test_list_modules_returns_8_modules(self):
        """GET /api/bionic/modules should return 8 modules"""
        response = requests.get(f"{BASE_URL}/api/bionic/modules")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["total"] == 8
        assert len(data["modules"]) == 8
        
        # Verify all expected modules are present
        module_ids = [m["id"] for m in data["modules"]]
        expected_modules = ["thermal", "wetness", "food", "pressure", "access", "corridor", "geoform", "canopy"]
        for expected in expected_modules:
            assert expected in module_ids, f"Module '{expected}' not found"
    
    def test_module_has_required_fields(self):
        """Each module should have id, name, version, description, factors"""
        response = requests.get(f"{BASE_URL}/api/bionic/modules")
        assert response.status_code == 200
        
        data = response.json()
        for module in data["modules"]:
            assert "id" in module
            assert "name" in module
            assert "version" in module
            assert "description" in module
            assert "factors" in module
            assert isinstance(module["factors"], list)
            assert len(module["factors"]) > 0
    
    def test_get_single_module_thermal(self):
        """GET /api/bionic/modules/thermal should return thermal module details"""
        response = requests.get(f"{BASE_URL}/api/bionic/modules/thermal")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["module"]["id"] == "thermal"
        assert data["module"]["name"] == "ThermalScore"
        assert "temperature" in data["module"]["factors"]
    
    def test_get_invalid_module_returns_404(self):
        """GET /api/bionic/modules/invalid should return 404"""
        response = requests.get(f"{BASE_URL}/api/bionic/modules/invalid_module")
        assert response.status_code == 404


class TestBionicSpecies:
    """Tests for BIONIC species endpoints"""
    
    def test_list_species_returns_6_species(self):
        """GET /api/bionic/species should return 6 species"""
        response = requests.get(f"{BASE_URL}/api/bionic/species")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["total"] == 6
        assert len(data["species"]) == 6
        
        # Verify all expected species are present
        species_ids = [s["id"] for s in data["species"]]
        expected_species = ["moose", "deer", "bear", "caribou", "wolf", "turkey"]
        for expected in expected_species:
            assert expected in species_ids, f"Species '{expected}' not found"
    
    def test_species_has_required_fields(self):
        """Each species should have id, name, common_name, version, module_weights"""
        response = requests.get(f"{BASE_URL}/api/bionic/species")
        assert response.status_code == 200
        
        data = response.json()
        for species in data["species"]:
            assert "id" in species
            assert "name" in species
            assert "common_name" in species
            assert "version" in species
            assert "module_weights" in species
            assert isinstance(species["module_weights"], dict)
    
    def test_get_single_species_moose(self):
        """GET /api/bionic/species/moose should return moose details"""
        response = requests.get(f"{BASE_URL}/api/bionic/species/moose")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["species"]["id"] == "moose"
        assert data["species"]["common_name"] == "Orignal"
    
    def test_get_invalid_species_returns_404(self):
        """GET /api/bionic/species/invalid should return 404"""
        response = requests.get(f"{BASE_URL}/api/bionic/species/invalid_species")
        assert response.status_code == 404


class TestBionicAnalysis:
    """Tests for BIONIC full territory analysis"""
    
    def test_full_analysis_returns_complete_data(self):
        """POST /api/bionic/analyze should return complete analysis"""
        payload = {
            "territory_id": "test-territory-123",
            "latitude": 46.8139,
            "longitude": -71.2082,
            "radius_km": 5.0
        }
        
        response = requests.post(f"{BASE_URL}/api/bionic/analyze", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        
        analysis = data["analysis"]
        
        # Verify location data
        assert analysis["territory_id"] == "test-territory-123"
        assert analysis["location"]["latitude"] == 46.8139
        assert analysis["location"]["longitude"] == -71.2082
        
        # Verify modules (should have 8)
        assert len(analysis["modules"]) == 8
        
        # Verify species (default 3: moose, deer, bear)
        assert len(analysis["species"]) == 3
        
        # Verify overall score
        assert "overall_score" in analysis
        assert 0 <= analysis["overall_score"] <= 100
        assert "overall_rating" in analysis
    
    def test_analysis_includes_ai_predictions(self):
        """Analysis should include AI predictions by default"""
        payload = {
            "territory_id": "test-ai-predictions",
            "latitude": 46.8139,
            "longitude": -71.2082,
            "include_ai_predictions": True
        }
        
        response = requests.post(f"{BASE_URL}/api/bionic/analyze", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        predictions = data["analysis"]["predictions"]
        
        assert predictions is not None
        assert "forecast_24h" in predictions
        assert "forecast_72h" in predictions
        assert "forecast_7d" in predictions
        assert "confidence" in predictions
        assert "weather_impact" in predictions
        assert "movement_prediction" in predictions
    
    def test_analysis_includes_temporal_data(self):
        """Analysis should include temporal data by default"""
        payload = {
            "territory_id": "test-temporal",
            "latitude": 46.8139,
            "longitude": -71.2082,
            "include_temporal": True
        }
        
        response = requests.post(f"{BASE_URL}/api/bionic/analyze", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        temporal = data["analysis"]["temporal"]
        
        assert temporal is not None
        assert "ndvi_trend" in temporal
        assert "ndwi_trend" in temporal
        assert "thermal_trend" in temporal
        assert "snow_cover_trend" in temporal
        assert "phenology" in temporal
        assert "anomalies" in temporal
    
    def test_analysis_with_custom_species(self):
        """Analysis should work with custom species selection"""
        payload = {
            "territory_id": "test-custom-species",
            "latitude": 46.8139,
            "longitude": -71.2082,
            "species": ["moose", "caribou", "wolf", "turkey"]
        }
        
        response = requests.post(f"{BASE_URL}/api/bionic/analyze", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        species_results = data["analysis"]["species"]
        
        assert len(species_results) == 4
        assert "moose" in species_results
        assert "caribou" in species_results
        assert "wolf" in species_results
        assert "turkey" in species_results
    
    def test_analysis_module_scores_have_required_fields(self):
        """Each module result should have score, rating, factors, recommendations"""
        payload = {
            "territory_id": "test-module-fields",
            "latitude": 46.8139,
            "longitude": -71.2082
        }
        
        response = requests.post(f"{BASE_URL}/api/bionic/analyze", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        for module_id, module_result in data["analysis"]["modules"].items():
            assert "module" in module_result
            assert "version" in module_result
            assert "score" in module_result
            assert 0 <= module_result["score"] <= 100
            assert "rating" in module_result
            assert "factors" in module_result
            assert "recommendations" in module_result
            assert "confidence" in module_result
    
    def test_analysis_species_scores_have_required_fields(self):
        """Each species result should have score, habitat metrics, hotspots"""
        payload = {
            "territory_id": "test-species-fields",
            "latitude": 46.8139,
            "longitude": -71.2082
        }
        
        response = requests.post(f"{BASE_URL}/api/bionic/analyze", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        for species_id, species_result in data["analysis"]["species"].items():
            assert "species" in species_result
            assert "common_name" in species_result
            assert "score" in species_result
            assert 0 <= species_result["score"] <= 100
            assert "rating" in species_result
            assert "habitat_suitability" in species_result
            assert "food_availability" in species_result
            assert "cover_quality" in species_result
            assert "water_access" in species_result
            assert "hotspots" in species_result
            assert isinstance(species_result["hotspots"], list)


class TestBionicAIPredictions:
    """Tests for BIONIC AI prediction endpoints"""
    
    def test_ai_predict_endpoint(self):
        """POST /api/bionic/ai/predict should return predictions"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/ai/predict",
            params={
                "territory_id": "test-predict",
                "latitude": 46.8139,
                "longitude": -71.2082
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "predictions" in data
    
    def test_dynamic_score_endpoint(self):
        """POST /api/bionic/ai/dynamic-score should return weather-adjusted scores"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/ai/dynamic-score",
            params={
                "territory_id": "test-dynamic",
                "latitude": 46.8139,
                "longitude": -71.2082,
                "weather_temp": 15,
                "weather_precip": 20,
                "time_of_day": "dawn"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "conditions" in data
        assert "dynamic_scores" in data
        
        # Verify conditions are captured
        assert data["conditions"]["temperature"] == 15
        assert data["conditions"]["precipitation"] == 20
        assert data["conditions"]["time_of_day"] == "dawn"
    
    def test_time_series_endpoint(self):
        """POST /api/bionic/ai/time-series should return temporal analysis"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/ai/time-series",
            params={
                "territory_id": "test-timeseries",
                "latitude": 46.8139,
                "longitude": -71.2082
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "temporal_analysis" in data


class TestBionicModuleRun:
    """Tests for running individual modules"""
    
    def test_run_thermal_module(self):
        """POST /api/bionic/modules/thermal/run should return thermal analysis"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/modules/thermal/run",
            params={
                "territory_id": "test-thermal-run",
                "latitude": 46.8139,
                "longitude": -71.2082
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["result"]["module"] == "ThermalScore"
        assert "score" in data["result"]
        assert "factors" in data["result"]
    
    def test_run_food_module(self):
        """POST /api/bionic/modules/food/run should return food analysis"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/modules/food/run",
            params={
                "territory_id": "test-food-run",
                "latitude": 46.8139,
                "longitude": -71.2082
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["result"]["module"] == "FoodScore"


class TestBionicSpeciesScore:
    """Tests for species habitat scoring"""
    
    def test_calculate_moose_score(self):
        """POST /api/bionic/species/moose/score should return moose habitat score"""
        response = requests.post(
            f"{BASE_URL}/api/bionic/species/moose/score",
            params={
                "territory_id": "test-moose-score",
                "latitude": 46.8139,
                "longitude": -71.2082
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["result"]["species"] == "MooseScore"
        assert data["result"]["common_name"] == "Orignal"
        assert "hotspots" in data["result"]
        assert len(data["result"]["hotspots"]) > 0


class TestBionicStats:
    """Tests for BIONIC statistics endpoint"""
    
    def test_get_analysis_stats(self):
        """GET /api/bionic/stats should return analysis statistics"""
        response = requests.get(f"{BASE_URL}/api/bionic/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "stats" in data
        assert "total_analyses" in data["stats"]
        assert "total_module_results" in data["stats"]
        assert "total_species_scores" in data["stats"]


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
