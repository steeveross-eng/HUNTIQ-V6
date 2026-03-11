"""
BIONIC HUNT/Chasse V3 - Backend API Tests
Tests for Phase 10+ API integration with frontend modules

Modules tested:
- Weather Engine (/api/v1/weather)
- Recommendation Engine (/api/v1/recommendation)
- Wildlife Behavior Engine (/api/v1/wildlife)
- Predictive Engine (/api/v1/predictive)
- Scoring Engine (/api/v1/scoring)
- Nutrition Engine (/api/v1/nutrition)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestAPIHealth:
    """Test API root and module health endpoints"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "version" in data
        print(f"API Version: {data['version']}")
    
    def test_modules_status(self):
        """Test modules status endpoint"""
        response = requests.get(f"{BASE_URL}/api/modules/status")
        assert response.status_code == 200
        data = response.json()
        assert data["total_modules"] >= 38
        assert "modules" in data
        print(f"Total modules: {data['total_modules']}")


class TestWeatherEngine:
    """Weather Engine API tests - /api/v1/weather"""
    
    def test_weather_engine_info(self):
        """Test weather engine info endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/weather/")
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "weather_engine"
        assert "features" in data
        print(f"Weather engine features: {len(data['features'])}")
    
    def test_weather_score_calculation(self):
        """Test weather score calculation with parameters"""
        params = {
            "temperature": 8,
            "humidity": 72,
            "wind_speed": 12,
            "wind_direction": "SW",
            "pressure": 1015,
            "precipitation": 0
        }
        response = requests.get(f"{BASE_URL}/api/v1/weather/score", params=params)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "score" in data
        assert "activity_level" in data
        assert "rating" in data
        assert 0 <= data["score"] <= 10
        print(f"Weather score: {data['score']}, Activity: {data['activity_level']}")
    
    def test_weather_optimal_conditions(self):
        """Test optimal conditions endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/weather/optimal")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "optimal_conditions" in data
        assert "temperature" in data["optimal_conditions"]
        assert "humidity" in data["optimal_conditions"]
    
    def test_weather_moon_phase(self):
        """Test moon phase endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/weather/moon")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "moon" in data
        assert "phase" in data["moon"]
        assert "illumination" in data["moon"]
        print(f"Moon phase: {data['moon']['phase_name']}")
    
    def test_weather_best_times(self):
        """Test best hunting times endpoint"""
        params = {"temperature": 10, "wind_speed": 10, "precipitation": 0}
        response = requests.get(f"{BASE_URL}/api/v1/weather/times", params=params)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "best_times" in data


class TestRecommendationEngine:
    """Recommendation Engine API tests - /api/v1/recommendation"""
    
    def test_recommendation_engine_info(self):
        """Test recommendation engine info endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/recommendation/")
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "recommendation_engine"
        assert data["status"] == "operational"
        print(f"Recommendation features: {len(data['features'])}")
    
    def test_product_recommendations(self):
        """Test product recommendations POST endpoint"""
        payload = {
            "species": "deer",
            "season": "rut"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/recommendation/products",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        assert "products" in data["data"]
        products = data["data"]["products"]
        assert len(products) > 0
        # Verify product structure
        first_product = products[0]
        assert "product_name" in first_product
        assert "score" in first_product
        print(f"Got {len(products)} product recommendations")
    
    def test_strategy_recommendations(self):
        """Test strategy recommendations endpoint"""
        params = {"species": "deer", "season": "rut"}
        response = requests.get(
            f"{BASE_URL}/api/v1/recommendation/strategies",
            params=params
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        assert "strategies" in data["data"]
        print(f"Got {len(data['data']['strategies'])} strategies")
    
    def test_contextual_recommendations(self):
        """Test contextual recommendations endpoint"""
        params = {
            "species": "deer",
            "season": "rut",
            "temperature": 8,
            "humidity": 72,
            "limit": 5
        }
        response = requests.get(
            f"{BASE_URL}/api/v1/recommendation/for-context",
            params=params
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True


class TestWildlifeEngine:
    """Wildlife Behavior Engine API tests - /api/v1/wildlife"""
    
    def test_wildlife_engine_info(self):
        """Test wildlife engine info endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/wildlife/")
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "wildlife_behavior_engine"
        assert data["status"] == "operational"
        print(f"Tracked species: {data['statistics']['tracked_species']}")
    
    def test_predict_activity(self):
        """Test activity prediction endpoint"""
        params = {
            "species": "deer",
            "lat": 45.5,
            "lng": -73.5
        }
        response = requests.get(
            f"{BASE_URL}/api/v1/wildlife/predict-activity",
            params=params
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "prediction" in data
        prediction = data["prediction"]
        assert "activity_level" in prediction
        assert "activity_score" in prediction
        assert "primary_behavior" in prediction
        print(f"Activity: {prediction['activity_level']}, Score: {prediction['activity_score']}")
    
    def test_species_list(self):
        """Test species list endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/wildlife/species")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "species" in data
        print(f"Available species: {len(data['species'])}")


class TestScoringEngine:
    """Scoring Engine API tests - /api/v1/scoring"""
    
    def test_scoring_engine_info(self):
        """Test scoring engine info endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/scoring/")
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "scoring_engine"
    
    def test_calculate_score(self):
        """Test score calculation endpoint"""
        payload = {
            "product_id": "test-product-1",
            "product_name": "Test Attractant Premium"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/scoring/calculate",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "score" in data
        assert "pastille" in data
        assert "breakdown" in data
        print(f"Score: {data['score']}, Pastille: {data['pastille']}")
    
    def test_scoring_criteria(self):
        """Test scoring criteria endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/scoring/criteria")
        assert response.status_code == 200
        data = response.json()
        assert "criteria" in data


class TestNutritionEngine:
    """Nutrition Engine API tests - /api/v1/nutrition"""
    
    def test_nutrition_engine_info(self):
        """Test nutrition engine info endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/nutrition/")
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "nutrition_engine"
    
    def test_analyze_ingredients(self):
        """Test ingredient analysis endpoint - expects list of ingredient names"""
        # The nutrition analyze endpoint expects a list of ingredient names (strings)
        payload = ["corn", "salt", "mineral"]
        response = requests.post(
            f"{BASE_URL}/api/v1/nutrition/analyze",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "analysis" in data
        print(f"Nutrition analysis completed for {data['input_count']} ingredients")
    
    def test_list_ingredients(self):
        """Test list ingredients endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/nutrition/ingredients")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "ingredients" in data
        print(f"Found {data['count']} ingredients")


class TestPredictiveEngine:
    """Predictive Engine API tests - NOTE: /api/v1/predictive does NOT exist
    
    The frontend PredictiveService gracefully falls back to placeholder data
    when the predictive API is unavailable. This is expected behavior.
    """
    
    def test_predictive_endpoint_not_available(self):
        """Verify predictive endpoint returns 404 (expected - frontend uses fallback)"""
        response = requests.get(f"{BASE_URL}/api/v1/predictive/")
        # This endpoint doesn't exist - frontend uses placeholder data
        assert response.status_code == 404
        print("Predictive API not available - frontend uses placeholder data (expected)")
    
    def test_wildlife_predict_activity_as_alternative(self):
        """Wildlife predict-activity can be used for predictions"""
        params = {
            "species": "deer",
            "lat": 45.5,
            "lng": -73.5
        }
        response = requests.get(
            f"{BASE_URL}/api/v1/wildlife/predict-activity",
            params=params
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "prediction" in data
        prediction = data["prediction"]
        assert "activity_score" in prediction
        print(f"Wildlife activity score: {prediction['activity_score']}")


class TestIntegrationFlow:
    """Integration tests - Full flow from frontend perspective"""
    
    def test_dashboard_data_flow(self):
        """Test data flow for Core Dashboard"""
        # 1. Get weather score
        weather_response = requests.get(
            f"{BASE_URL}/api/v1/weather/score",
            params={"temperature": 8, "humidity": 72, "wind_speed": 12, "wind_direction": "SW", "pressure": 1015}
        )
        assert weather_response.status_code == 200
        weather_data = weather_response.json()
        
        # 2. Get recommendations
        rec_response = requests.post(
            f"{BASE_URL}/api/v1/recommendation/products",
            json={"species": "deer", "season": "rut"}
        )
        assert rec_response.status_code == 200
        
        # 3. Get wildlife prediction
        wildlife_response = requests.get(
            f"{BASE_URL}/api/v1/wildlife/predict-activity",
            params={"species": "deer", "lat": 45.5, "lng": -73.5}
        )
        assert wildlife_response.status_code == 200
        
        print("Dashboard data flow: All APIs responding correctly")
    
    def test_plan_maitre_data_flow(self):
        """Test data flow for Plan Maître Dashboard"""
        # 1. Get product recommendations
        rec_response = requests.post(
            f"{BASE_URL}/api/v1/recommendation/products",
            json={"species": "deer", "season": "rut"}
        )
        assert rec_response.status_code == 200
        rec_data = rec_response.json()
        assert len(rec_data["data"]["products"]) > 0
        
        # 2. Get wildlife activity (predictive endpoint doesn't exist, frontend uses fallback)
        wildlife_response = requests.get(
            f"{BASE_URL}/api/v1/wildlife/predict-activity",
            params={"species": "deer"}
        )
        assert wildlife_response.status_code == 200
        wildlife_data = wildlife_response.json()
        assert "activity_score" in wildlife_data["prediction"]
        
        # 3. Get strategy recommendations
        strategy_response = requests.get(
            f"{BASE_URL}/api/v1/recommendation/strategies",
            params={"species": "deer"}
        )
        assert strategy_response.status_code == 200
        
        print("Plan Maître data flow: All available APIs responding correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
