"""
HUNTIQ V3 - Phase P3 Backend API Tests
Tests for Analytics Dashboard, WQS, Success Forecast, Heatmap, and AI Recommendations
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://hotspot-fusion-map.preview.emergentagent.com')


class TestAnalyticsEngine:
    """P3.1 - Analytics Dashboard API Tests"""
    
    def test_analytics_dashboard(self):
        """Test full analytics dashboard endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/analytics/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        # Verify dashboard structure
        assert "overview" in data
        assert "species_breakdown" in data
        assert "weather_analysis" in data
        assert "optimal_times" in data
        assert "monthly_trends" in data
        assert "recent_trips" in data
        
        # Verify overview KPIs
        overview = data["overview"]
        assert "total_trips" in overview
        assert "success_rate" in overview
        assert "total_hours" in overview
        assert "total_observations" in overview
        assert isinstance(overview["total_trips"], int)
        assert isinstance(overview["success_rate"], (int, float))
    
    def test_analytics_overview(self):
        """Test analytics overview endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/analytics/overview")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_trips" in data
        assert "successful_trips" in data
        assert "success_rate" in data
        assert "total_hours" in data
        assert "total_observations" in data
        assert "avg_trip_duration" in data
    
    def test_analytics_species_breakdown(self):
        """Test species breakdown endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/analytics/species")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            species = data[0]
            assert "species" in species
            assert "trips" in species
            assert "success_rate" in species
            assert "total_observations" in species
    
    def test_analytics_weather_analysis(self):
        """Test weather analysis endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/analytics/weather")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            weather = data[0]
            assert "condition" in weather
            assert "trips" in weather
            assert "success_rate" in weather
    
    def test_analytics_optimal_times(self):
        """Test optimal times endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/analytics/optimal-times")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            time_slot = data[0]
            assert "hour" in time_slot
            assert "label" in time_slot
            assert "success_rate" in time_slot
    
    def test_analytics_monthly_trends(self):
        """Test monthly trends endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/analytics/trends")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            trend = data[0]
            assert "month" in trend
            assert "trips" in trend
            assert "successes" in trend
    
    def test_analytics_time_range_filter(self):
        """Test analytics with time range filter"""
        for time_range in ["week", "month", "season", "year", "all"]:
            response = requests.get(f"{BASE_URL}/api/v1/analytics/dashboard?time_range={time_range}")
            assert response.status_code == 200
            data = response.json()
            assert "overview" in data


class TestWaypointScoringEngine:
    """P3.5 - WQS & Success Forecast API Tests"""
    
    def test_wqs_all_waypoints(self):
        """Test WQS for all waypoints"""
        response = requests.get(f"{BASE_URL}/api/v1/waypoint-scoring/wqs")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            wqs = data[0]
            assert "waypoint_id" in wqs
            assert "waypoint_name" in wqs
            assert "total_score" in wqs
            assert "classification" in wqs
            assert "total_visits" in wqs
            assert "success_rate" in wqs
            # Verify score is percentage
            assert 0 <= wqs["total_score"] <= 100
            # Verify classification is valid
            assert wqs["classification"] in ["hotspot", "good", "standard", "weak"]
    
    def test_wqs_ranking(self):
        """Test waypoint ranking endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/waypoint-scoring/ranking")
        assert response.status_code == 200
        
        data = response.json()
        assert "rankings" in data
        assert "generated_at" in data
    
    def test_success_forecast_quick(self):
        """Test quick success forecast"""
        response = requests.get(f"{BASE_URL}/api/v1/waypoint-scoring/forecast/quick?species=deer")
        assert response.status_code == 200
        
        data = response.json()
        assert "probability" in data
        assert "confidence" in data
        assert "best_waypoint" in data
        assert "optimal_time_window" in data
        # Verify probability is percentage
        assert 0 <= data["probability"] <= 100
        assert data["confidence"] in ["high", "medium", "low"]
    
    def test_success_forecast_with_params(self):
        """Test success forecast with various parameters"""
        params = {
            "species": "moose",
            "weather": "Nuageux",
            "hour": 7,
            "temperature": 10
        }
        response = requests.get(f"{BASE_URL}/api/v1/waypoint-scoring/forecast/quick", params=params)
        assert response.status_code == 200
        
        data = response.json()
        assert "probability" in data
        assert "favorable_conditions" in data
        assert "unfavorable_conditions" in data
    
    def test_heatmap_data(self):
        """Test heatmap data endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/waypoint-scoring/heatmap")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            point = data[0]
            assert "lat" in point
            assert "lng" in point
            assert "intensity" in point
            assert "waypoint_id" in point
            assert "wqs" in point
            # Verify intensity is 0-1
            assert 0 <= point["intensity"] <= 1


class TestAIRecommendations:
    """P3.6 - GPT-5.2 AI Recommendations API Tests"""
    
    def test_ai_recommendations(self):
        """Test AI recommendations endpoint"""
        response = requests.get(f"{BASE_URL}/api/v1/waypoint-scoring/recommendations?species=deer")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_ai_gpt_recommendation(self):
        """Test GPT-5.2 powered recommendation"""
        response = requests.get(f"{BASE_URL}/api/v1/waypoint-scoring/recommendations/ai?species=deer")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "recommendation" in data
        assert "waypoint" in data
        assert "species" in data
        assert data["powered_by"] == "GPT-5.2"
        # Verify recommendation is not empty
        assert len(data["recommendation"]) > 0
    
    def test_ai_daily_briefing(self):
        """Test GPT-5.2 daily briefing"""
        response = requests.get(f"{BASE_URL}/api/v1/waypoint-scoring/briefing?species=deer")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "briefing" in data
        assert "species" in data
        assert "waypoints_analyzed" in data
        assert data["powered_by"] == "GPT-5.2"
        # Verify briefing is not empty
        assert len(data["briefing"]) > 0
    
    def test_ai_recommendation_with_weather(self):
        """Test AI recommendation with weather parameter"""
        response = requests.get(f"{BASE_URL}/api/v1/waypoint-scoring/recommendations/ai?species=deer&weather=Nuageux")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["weather"] == "Nuageux"


class TestPWAAssets:
    """P3.4 - PWA Assets Tests"""
    
    def test_manifest_json(self):
        """Test manifest.json is accessible"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "short_name" in data
        assert data["short_name"] == "HUNTIQ"
        assert "name" in data
        assert "icons" in data
        assert "start_url" in data
        assert "display" in data
        assert data["display"] == "standalone"
        assert "theme_color" in data
    
    def test_offline_html(self):
        """Test offline.html is accessible"""
        response = requests.get(f"{BASE_URL}/offline.html")
        assert response.status_code == 200
        
        content = response.text
        assert "HUNTIQ" in content
        assert "Hors Ligne" in content or "offline" in content.lower()


class TestModuleStatus:
    """Test module registration"""
    
    def test_p3_modules_registered(self):
        """Verify P3 modules are registered"""
        response = requests.get(f"{BASE_URL}/api/modules/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_modules"] >= 42
        
        # Find P3 modules
        module_names = [m["name"] for m in data["modules"]]
        assert "analytics_engine" in module_names
        assert "waypoint_scoring_engine" in module_names
        
        # Verify P3 modules have correct phase
        for module in data["modules"]:
            if module["name"] == "analytics_engine":
                assert module["phase"] == "P3"
            if module["name"] == "waypoint_scoring_engine":
                assert module["phase"] == "P3"


class TestUserWaypoints:
    """Test user waypoints API for map integration"""
    
    def test_get_waypoints(self):
        """Test getting user waypoints"""
        response = requests.get(f"{BASE_URL}/api/user/waypoints")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "waypoints" in data
        assert isinstance(data["waypoints"], list)
        
        if len(data["waypoints"]) > 0:
            waypoint = data["waypoints"][0]
            assert "id" in waypoint
            assert "name" in waypoint
            assert "lat" in waypoint
            assert "lng" in waypoint
            assert "type" in waypoint


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
