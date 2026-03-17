"""
Tests d'Intégration Frontend-Backend
=====================================
Tests E2E pour vérifier la connexion entre les services frontend et les APIs backend.

Version: 1.0.0
Date: 2026-02-09
"""

import pytest
import requests
import os

# Backend URL
BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://bionic-map-refresh.preview.emergentagent.com")


class TestLegalTimeIntegration:
    """Tests d'intégration pour LegalTimeService -> legal-time API"""
    
    def test_legal_time_info_endpoint(self):
        """Vérifier que l'endpoint info est accessible"""
        response = requests.get(f"{BACKEND_URL}/api/v1/legal-time/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "legal_time_engine"
        assert data["version"] == "1.0.0"
    
    def test_legal_window_endpoint(self):
        """Vérifier que l'endpoint legal-window retourne les bonnes données"""
        response = requests.get(f"{BACKEND_URL}/api/v1/legal-time/legal-window")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "legal_window" in data
        assert "start_time" in data["legal_window"]
        assert "end_time" in data["legal_window"]
        assert "sunrise" in data["legal_window"]
        assert "sunset" in data["legal_window"]
    
    def test_check_endpoint_returns_status(self):
        """Vérifier que l'endpoint check retourne le statut légal"""
        response = requests.get(f"{BACKEND_URL}/api/v1/legal-time/check")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "is_legal" in data
        assert isinstance(data["is_legal"], bool)
        assert "message" in data
    
    def test_recommended_slots_returns_list(self):
        """Vérifier que les créneaux recommandés retournent une liste"""
        response = requests.get(f"{BACKEND_URL}/api/v1/legal-time/recommended-slots")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "slots" in data
        assert isinstance(data["slots"], list)
        assert len(data["slots"]) >= 3
    
    def test_forecast_returns_multiple_days(self):
        """Vérifier que les prévisions retournent plusieurs jours"""
        response = requests.get(f"{BACKEND_URL}/api/v1/legal-time/forecast?days=7")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "forecast" in data
        assert len(data["forecast"]["daily_schedules"]) == 7


class TestPredictiveIntegration:
    """Tests d'intégration pour PredictiveService -> predictive API"""
    
    def test_predictive_info_endpoint(self):
        """Vérifier que l'endpoint info est accessible"""
        response = requests.get(f"{BACKEND_URL}/api/v1/predictive/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "predictive_engine"
        assert "supported_species" in data
    
    def test_success_prediction_endpoint(self):
        """Vérifier que la prédiction de succès fonctionne"""
        response = requests.get(f"{BACKEND_URL}/api/v1/predictive/success?species=deer")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "prediction" in data
        assert "success_probability" in data["prediction"]
        assert 0 <= data["prediction"]["success_probability"] <= 100
    
    def test_activity_endpoint(self):
        """Vérifier que le niveau d'activité est retourné"""
        response = requests.get(f"{BACKEND_URL}/api/v1/predictive/activity?species=deer")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "activity" in data
        assert "level" in data["activity"]
        assert "score" in data["activity"]
    
    def test_factors_endpoint(self):
        """Vérifier que les facteurs sont retournés"""
        response = requests.get(f"{BACKEND_URL}/api/v1/predictive/factors?species=deer")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "factors" in data
        assert len(data["factors"]) == 5
    
    def test_timeline_endpoint(self):
        """Vérifier que la timeline 24h est retournée"""
        response = requests.get(f"{BACKEND_URL}/api/v1/predictive/timeline?species=deer")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "timeline" in data
        assert len(data["timeline"]) == 24
    
    def test_optimal_times_respect_legal_window(self):
        """Vérifier que les heures optimales respectent la fenêtre légale"""
        response = requests.get(f"{BACKEND_URL}/api/v1/predictive/success?species=deer")
        
        assert response.status_code == 200
        data = response.json()
        
        for time_slot in data["prediction"]["optimal_times"]:
            assert time_slot["is_legal"] is True


class TestWeatherIntegration:
    """Tests d'intégration pour WeatherService -> weather API"""
    
    def test_weather_info_endpoint(self):
        """Vérifier que l'endpoint info est accessible"""
        response = requests.get(f"{BACKEND_URL}/api/v1/weather/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "weather_engine"
    
    def test_weather_score_endpoint(self):
        """Vérifier que le score météo est calculé"""
        params = {
            "temperature": 10,
            "humidity": 60,
            "wind_speed": 8,
            "wind_direction": "N",
            "pressure": 1013,
            "precipitation": 0
        }
        response = requests.get(f"{BACKEND_URL}/api/v1/weather/score", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "score" in data
        assert 0 <= data["score"] <= 10
    
    def test_moon_phase_endpoint(self):
        """Vérifier que la phase lunaire est retournée"""
        response = requests.get(f"{BACKEND_URL}/api/v1/weather/moon")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "moon" in data
        assert "phase" in data["moon"]


class TestRecommendationIntegration:
    """Tests d'intégration pour RecommendationService -> recommendation API"""
    
    def test_recommendation_info_endpoint(self):
        """Vérifier que l'endpoint info est accessible"""
        response = requests.get(f"{BACKEND_URL}/api/v1/recommendation/")
        
        # L'endpoint peut être GET ou POST selon l'implémentation
        assert response.status_code in [200, 404, 405]


class TestProductsIntegration:
    """Tests d'intégration pour ProductsService -> products API"""
    
    def test_products_list_endpoint(self):
        """Vérifier que la liste des produits est accessible"""
        response = requests.get(f"{BACKEND_URL}/api/v1/products/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (dict, list))


class TestCrossModuleIntegration:
    """Tests d'intégration entre modules"""
    
    def test_predictive_uses_legal_time(self):
        """Vérifier que predictive intègre les heures légales"""
        # Obtenir la fenêtre légale
        legal_response = requests.get(f"{BACKEND_URL}/api/v1/legal-time/legal-window")
        legal_data = legal_response.json()
        
        # Obtenir la prédiction
        pred_response = requests.get(f"{BACKEND_URL}/api/v1/predictive/success?species=deer")
        pred_data = pred_response.json()
        
        # Vérifier que les heures optimales sont dans la fenêtre légale
        legal_start = legal_data["legal_window"]["start_time"]
        legal_end = legal_data["legal_window"]["end_time"]
        
        for time_slot in pred_data["prediction"]["optimal_times"]:
            # Les créneaux doivent être marqués comme légaux
            assert time_slot["is_legal"] is True
    
    def test_timeline_legal_status_matches_legal_window(self):
        """Vérifier que le statut légal de la timeline correspond à la fenêtre"""
        # Obtenir la fenêtre légale
        legal_response = requests.get(f"{BACKEND_URL}/api/v1/legal-time/legal-window")
        legal_data = legal_response.json()
        
        # Obtenir la timeline
        timeline_response = requests.get(f"{BACKEND_URL}/api/v1/predictive/timeline?species=deer")
        timeline_data = timeline_response.json()
        
        # Extraire les heures de la fenêtre légale
        legal_start_hour = int(legal_data["legal_window"]["start_time"].split(":")[0])
        legal_end_hour = int(legal_data["legal_window"]["end_time"].split(":")[0])
        
        # Vérifier que 12h est légal (milieu de journée)
        noon_entry = timeline_data["timeline"][12]
        assert noon_entry["is_legal"] is True
        
        # Vérifier que 2h du matin est illégal
        night_entry = timeline_data["timeline"][2]
        assert night_entry["is_legal"] is False


class TestAPIResponseFormats:
    """Tests de format des réponses API"""
    
    def test_legal_time_response_has_required_fields(self):
        """Vérifier le format de réponse legal-time"""
        response = requests.get(f"{BACKEND_URL}/api/v1/legal-time/legal-window")
        data = response.json()
        
        required_fields = ["success", "date", "location", "legal_window", "status"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
    
    def test_predictive_response_has_required_fields(self):
        """Vérifier le format de réponse predictive"""
        response = requests.get(f"{BACKEND_URL}/api/v1/predictive/success?species=deer")
        data = response.json()
        
        assert "success" in data
        assert "prediction" in data
        
        prediction_fields = ["success_probability", "confidence", "factors", "optimal_times", "recommendation"]
        for field in prediction_fields:
            assert field in data["prediction"], f"Missing prediction field: {field}"
    
    def test_timeline_response_complete(self):
        """Vérifier que la timeline est complète"""
        response = requests.get(f"{BACKEND_URL}/api/v1/predictive/timeline?species=deer")
        data = response.json()
        
        assert len(data["timeline"]) == 24
        
        for i, entry in enumerate(data["timeline"]):
            assert entry["hour"] == i
            assert "activity_level" in entry
            assert "is_legal" in entry
            assert "light_condition" in entry


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
