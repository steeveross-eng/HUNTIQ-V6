"""
Test BIONIC V5 300% - P1 Dynamic Scores API
=============================================
Tests pour l'endpoint POST /api/v1/bionic/dynamic/scores

Vérifie les exclusions dynamiques:
- Score composite
- Risque (risk_level)
- Facteurs actifs (temporal, thermal_stress, hunting_pressure, seasonal_context)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestDynamicScoresAPI:
    """Tests pour l'API Dynamic Exclusion Scores"""

    def test_dynamic_scores_success(self):
        """Test POST /api/v1/bionic/dynamic/scores avec coordonnées valides"""
        url = f"{BASE_URL}/api/v1/bionic/dynamic/scores"
        payload = {
            "lat": 46.8139,
            "lng": -71.2080,
            "species": "moose"
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        # Status code assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Success assertion
        assert data.get("success") is True, f"Expected success=true, got {data.get('success')}"
        
        # Score assertion
        assert "score" in data, "Response missing 'score' field"
        assert isinstance(data["score"], (int, float)), "Score should be numeric"
        assert 0 <= data["score"] <= 100, f"Score should be 0-100, got {data['score']}"
        
        # Confidence assertion
        assert "confidence" in data, "Response missing 'confidence' field"
        
        # Risk level assertion
        assert "risk_level" in data, "Response missing 'risk_level' field"
        assert data["risk_level"] in ["normal", "elevated", "critical"], f"Unexpected risk_level: {data['risk_level']}"
        
        # Factors assertion
        assert "factors" in data, "Response missing 'factors' field"
        factors = data["factors"]
        
        # Check required factor types
        required_factors = ["temporal", "thermal_stress", "hunting_pressure", "seasonal_context"]
        for factor in required_factors:
            assert factor in factors, f"Missing required factor: {factor}"
        
        # Active factors assertion
        assert "active_factors" in data, "Response missing 'active_factors' field"
        assert "total_factors" in data, "Response missing 'total_factors' field"
        
        print(f"✓ Dynamic scores API working: score={data['score']}, risk={data['risk_level']}, factors={data['active_factors']}/{data['total_factors']}")

    def test_dynamic_scores_temporal_factor(self):
        """Vérifie le facteur temporel dans les scores dynamiques"""
        url = f"{BASE_URL}/api/v1/bionic/dynamic/scores"
        payload = {
            "lat": 46.8139,
            "lng": -71.2080,
            "species": "moose",
            "hour": 6  # Aube - forte activité attendue
        }
        
        response = requests.post(url, json=payload, timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        
        # Check temporal factor
        factors = data.get("factors", {})
        temporal = factors.get("temporal", {})
        
        assert "hour" in temporal, "Temporal factor missing 'hour' field"
        assert "activity_level" in temporal, "Temporal factor missing 'activity_level' field"
        
        print(f"✓ Temporal factor: hour={temporal.get('hour')}, activity_level={temporal.get('activity_level')}")

    def test_dynamic_scores_thermal_stress(self):
        """Vérifie le facteur stress thermique"""
        url = f"{BASE_URL}/api/v1/bionic/dynamic/scores"
        payload = {
            "lat": 46.8139,
            "lng": -71.2080,
            "species": "moose",
            "temperature_c": 25  # Température modérée
        }
        
        response = requests.post(url, json=payload, timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        
        # Check thermal_stress factor
        factors = data.get("factors", {})
        thermal = factors.get("thermal_stress", {})
        
        assert "active" in thermal, "Thermal stress missing 'active' field"
        
        print(f"✓ Thermal stress factor: active={thermal.get('active')}")

    def test_dynamic_scores_hunting_pressure(self):
        """Vérifie le facteur pression de chasse"""
        url = f"{BASE_URL}/api/v1/bionic/dynamic/scores"
        payload = {
            "lat": 46.8139,
            "lng": -71.2080,
            "species": "moose",
            "region": "quebec"
        }
        
        response = requests.post(url, json=payload, timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        
        # Check hunting_pressure factor
        factors = data.get("factors", {})
        hunting = factors.get("hunting_pressure", {})
        
        assert "hunting_season" in hunting, "Hunting pressure missing 'hunting_season' field"
        assert "is_weekend" in hunting, "Hunting pressure missing 'is_weekend' field"
        
        print(f"✓ Hunting pressure factor: season={hunting.get('hunting_season')}, weekend={hunting.get('is_weekend')}")

    def test_dynamic_scores_seasonal_context(self):
        """Vérifie le contexte saisonnier"""
        url = f"{BASE_URL}/api/v1/bionic/dynamic/scores"
        payload = {
            "lat": 46.8139,
            "lng": -71.2080,
            "species": "moose"
        }
        
        response = requests.post(url, json=payload, timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        
        # Check seasonal_context factor
        factors = data.get("factors", {})
        seasonal = factors.get("seasonal_context", {})
        
        assert "season" in seasonal, "Seasonal context missing 'season' field"
        assert seasonal["season"] in ["spring", "summer", "fall", "winter", "rut"], f"Unexpected season: {seasonal['season']}"
        
        print(f"✓ Seasonal context factor: season={seasonal.get('season')}")

    def test_dynamic_scores_meta_info(self):
        """Vérifie les métadonnées de la réponse"""
        url = f"{BASE_URL}/api/v1/bionic/dynamic/scores"
        payload = {
            "lat": 46.8139,
            "lng": -71.2080,
            "species": "moose"
        }
        
        response = requests.post(url, json=payload, timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        
        # Check meta info
        meta = data.get("meta", {})
        assert "species" in meta, "Meta missing 'species' field"
        assert "region" in meta, "Meta missing 'region' field"
        assert "lat" in meta, "Meta missing 'lat' field"
        assert "lng" in meta, "Meta missing 'lng' field"
        assert "version" in meta, "Meta missing 'version' field"
        
        print(f"✓ Meta info: version={meta.get('version')}, species={meta.get('species')}")

    def test_dynamic_scores_recommendations(self):
        """Vérifie que les recommandations sont présentes"""
        url = f"{BASE_URL}/api/v1/bionic/dynamic/scores"
        payload = {
            "lat": 46.8139,
            "lng": -71.2080,
            "species": "moose"
        }
        
        response = requests.post(url, json=payload, timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        
        # Check recommendations field exists
        assert "recommendations" in data, "Response missing 'recommendations' field"
        assert isinstance(data["recommendations"], list), "Recommendations should be a list"
        
        print(f"✓ Recommendations: {len(data['recommendations'])} items")


class TestDynamicScoresEdgeCases:
    """Tests edge cases pour l'API Dynamic Scores"""

    def test_dynamic_scores_without_species(self):
        """Test avec espèce par défaut (moose)"""
        url = f"{BASE_URL}/api/v1/bionic/dynamic/scores"
        payload = {
            "lat": 46.8139,
            "lng": -71.2080
        }
        
        response = requests.post(url, json=payload, timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        # Devrait utiliser "moose" par défaut
        assert data.get("meta", {}).get("species") == "moose"
        
        print("✓ Default species (moose) applied correctly")

    def test_dynamic_scores_extreme_coords(self):
        """Test avec coordonnées extrêmes (zone forestière)"""
        url = f"{BASE_URL}/api/v1/bionic/dynamic/scores"
        payload = {
            "lat": 49.5,  # Nord du Québec
            "lng": -74.0,
            "species": "moose"
        }
        
        response = requests.post(url, json=payload, timeout=30)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        
        print(f"✓ Extreme coords handled: score={data.get('score')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
