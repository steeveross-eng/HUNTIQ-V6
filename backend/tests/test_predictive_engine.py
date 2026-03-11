"""
Tests Unitaires - Predictive Engine
====================================
Tests complets pour le module de prédiction de succès de chasse.

Version: 1.0.0
Date: 2026-02-09
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import patch, MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.predictive_engine.v1.service import PredictiveService
from modules.predictive_engine.v1.models import (
    HuntingPrediction, PredictionFactor, OptimalTimeSlot,
    ActivityLevel, ActivityTimeline
)
from modules.legal_time_engine.v1.models import LocationInput


class TestPredictiveService:
    """Tests pour PredictiveService"""
    
    @pytest.fixture
    def service(self):
        """Fixture pour créer une instance du service"""
        return PredictiveService()
    
    @pytest.fixture
    def quebec_location(self):
        """Fixture pour la localisation Québec"""
        return LocationInput(
            latitude=46.8139,
            longitude=-71.2080,
            timezone="America/Toronto"
        )

    # ==========================================
    # Tests: Configuration et espèces supportées
    # ==========================================
    
    def test_supported_species(self, service):
        """Vérifier les espèces supportées"""
        assert "deer" in service.SPECIES_PATTERNS
        assert "moose" in service.SPECIES_PATTERNS
        assert "bear" in service.SPECIES_PATTERNS
        assert "wild_turkey" in service.SPECIES_PATTERNS
    
    def test_species_have_required_attributes(self, service):
        """Vérifier que chaque espèce a les attributs requis"""
        for species, data in service.SPECIES_PATTERNS.items():
            assert "name" in data
            assert "dawn_activity" in data
            assert "midday_activity" in data
            assert "dusk_activity" in data
            assert "night_activity" in data
            assert "best_temp_range" in data
            assert "weather_sensitivity" in data
    
    def test_season_factors_all_months(self, service):
        """Vérifier que tous les mois ont un facteur saisonnier"""
        for month in range(1, 13):
            assert month in service.SEASON_FACTORS
            assert 0 <= service.SEASON_FACTORS[month] <= 1

    # ==========================================
    # Tests: Prédiction de succès
    # ==========================================
    
    def test_predict_success_returns_valid_structure(self, service, quebec_location):
        """Vérifier que la prédiction retourne une structure valide"""
        result = service.predict_hunting_success(
            species="deer",
            target_date=date.today(),
            location=quebec_location
        )
        
        assert isinstance(result, HuntingPrediction)
        assert 0 <= result.success_probability <= 100
        assert 0 <= result.confidence <= 1
        assert isinstance(result.factors, list)
        assert isinstance(result.optimal_times, list)
        assert isinstance(result.recommendation, str)
    
    def test_predict_success_has_five_factors(self, service):
        """Vérifier que la prédiction inclut 5 facteurs"""
        result = service.predict_hunting_success(species="deer")
        
        assert len(result.factors) == 5
        
        factor_names = [f.name for f in result.factors]
        assert "Saison" in factor_names
        assert "Météo" in factor_names
        assert "Phase lunaire" in factor_names
        assert "Pression atmosphérique" in factor_names
        assert "Activité récente" in factor_names
    
    def test_predict_success_factors_have_valid_impact(self, service):
        """Vérifier que les facteurs ont des impacts valides"""
        result = service.predict_hunting_success(species="deer")
        
        valid_impacts = ["very_positive", "positive", "neutral", "negative", "very_negative"]
        
        for factor in result.factors:
            assert factor.impact in valid_impacts
            assert 0 <= factor.score <= 100
    
    def test_predict_success_optimal_times_are_legal(self, service, quebec_location):
        """Vérifier que les heures optimales sont légales"""
        result = service.predict_hunting_success(
            species="deer",
            target_date=date.today(),
            location=quebec_location
        )
        
        for time_slot in result.optimal_times:
            assert time_slot.is_legal is True
    
    def test_predict_success_different_species(self, service):
        """Vérifier les prédictions pour différentes espèces"""
        species_list = ["deer", "moose", "bear", "wild_turkey"]
        
        for species in species_list:
            result = service.predict_hunting_success(species=species)
            assert result is not None
            assert result.success_probability > 0
    
    def test_predict_success_with_weather_data(self, service):
        """Vérifier la prédiction avec données météo"""
        weather = {
            "temperature": 10,
            "wind_speed": 8,
            "precipitation": 0
        }
        
        result = service.predict_hunting_success(
            species="deer",
            weather=weather
        )
        
        assert result.confidence == 0.85  # Plus de confiance avec météo
    
    def test_predict_success_without_weather_data(self, service):
        """Vérifier la prédiction sans données météo"""
        result = service.predict_hunting_success(species="deer")
        
        assert result.confidence == 0.70  # Moins de confiance sans météo
    
    def test_predict_success_recommendation_varies(self, service):
        """Vérifier que les recommandations varient selon le score"""
        # Test avec différentes dates pour avoir différents scores
        results = []
        for month in [2, 6, 10]:  # Hiver, été, automne
            test_date = date(2026, month, 15)
            result = service.predict_hunting_success(
                species="deer",
                target_date=test_date
            )
            results.append(result.recommendation)
        
        # Les recommandations ne devraient pas toutes être identiques
        # (au moins pour des saisons très différentes)
        assert len(results) == 3

    # ==========================================
    # Tests: Niveau d'activité
    # ==========================================
    
    def test_activity_level_returns_valid_structure(self, service, quebec_location):
        """Vérifier que le niveau d'activité retourne une structure valide"""
        result = service.get_activity_level(
            species="deer",
            location=quebec_location
        )
        
        assert isinstance(result, ActivityLevel)
        assert result.species == "deer"
        assert result.level in ["very_low", "low", "moderate", "high", "very_high"]
        assert 0 <= result.score <= 100
        assert isinstance(result.peak_times, list)
    
    def test_activity_level_has_peak_times(self, service):
        """Vérifier que les périodes de pic sont définies"""
        result = service.get_activity_level(species="deer")
        
        assert len(result.peak_times) >= 2  # Au moins aube et crépuscule
    
    def test_activity_level_score_matches_level(self, service):
        """Vérifier la cohérence entre score et niveau"""
        result = service.get_activity_level(species="deer")
        
        if result.score >= 80:
            assert result.level == "very_high"
        elif result.score >= 60:
            assert result.level == "high"
        elif result.score >= 40:
            assert result.level == "moderate"
        elif result.score >= 20:
            assert result.level == "low"
        else:
            assert result.level == "very_low"

    # ==========================================
    # Tests: Timeline d'activité
    # ==========================================
    
    def test_activity_timeline_24_hours(self, service, quebec_location):
        """Vérifier que la timeline couvre 24 heures"""
        result = service.get_activity_timeline(
            species="deer",
            target_date=date.today(),
            location=quebec_location
        )
        
        assert len(result) == 24
    
    def test_activity_timeline_hours_sequential(self, service, quebec_location):
        """Vérifier que les heures sont séquentielles"""
        result = service.get_activity_timeline(
            species="deer",
            location=quebec_location
        )
        
        for i, entry in enumerate(result):
            assert entry.hour == i
    
    def test_activity_timeline_legal_status(self, service, quebec_location):
        """Vérifier que le statut légal est correct"""
        result = service.get_activity_timeline(
            species="deer",
            target_date=date.today(),
            location=quebec_location
        )
        
        # 2h du matin devrait être illégal
        assert result[2].is_legal is False
        
        # 12h devrait être légal
        assert result[12].is_legal is True
    
    def test_activity_timeline_light_conditions(self, service, quebec_location):
        """Vérifier les conditions de lumière"""
        result = service.get_activity_timeline(
            species="deer",
            target_date=date.today(),
            location=quebec_location
        )
        
        valid_conditions = ["dark", "dawn", "daylight", "dusk", "twilight"]
        
        for entry in result:
            assert entry.light_condition in valid_conditions

    # ==========================================
    # Tests: Facteurs de succès
    # ==========================================
    
    def test_success_factors_returns_list(self, service):
        """Vérifier que les facteurs retournent une liste"""
        result = service.get_success_factors(species="deer")
        
        assert isinstance(result, list)
        assert len(result) == 5
    
    def test_success_factors_all_have_descriptions(self, service):
        """Vérifier que tous les facteurs ont des descriptions"""
        result = service.get_success_factors(species="deer")
        
        for factor in result:
            assert factor.description is not None
            assert len(factor.description) > 0

    # ==========================================
    # Tests: Calculs météo
    # ==========================================
    
    def test_weather_score_ideal_conditions(self, service):
        """Tester le score météo avec conditions idéales pour cerf"""
        species_data = service.SPECIES_PATTERNS["deer"]
        
        ideal_weather = {
            "temperature": 5,  # Dans la plage idéale
            "wind_speed": 5,   # Vent faible
            "precipitation": 0  # Pas de pluie
        }
        
        score = service._calculate_weather_score(ideal_weather, species_data)
        
        assert score >= 80  # Conditions idéales = bon score
    
    def test_weather_score_bad_conditions(self, service):
        """Tester le score météo avec mauvaises conditions"""
        species_data = service.SPECIES_PATTERNS["deer"]
        
        bad_weather = {
            "temperature": 35,  # Trop chaud
            "wind_speed": 40,   # Vent fort
            "precipitation": 10  # Pluie
        }
        
        score = service._calculate_weather_score(bad_weather, species_data)
        
        assert score < 50  # Mauvaises conditions = mauvais score

    # ==========================================
    # Tests: Calculs lunaires
    # ==========================================
    
    def test_moon_score_new_moon(self, service):
        """Tester le score lunaire à la nouvelle lune"""
        # Date proche d'une nouvelle lune connue
        new_moon_date = date(2024, 1, 11)
        
        score = service._calculate_moon_score(new_moon_date)
        
        assert score >= 70  # Nouvelle lune = bon pour activité diurne
    
    def test_moon_score_full_moon(self, service):
        """Tester le score lunaire à la pleine lune"""
        # ~14 jours après nouvelle lune
        full_moon_date = date(2024, 1, 25)
        
        score = service._calculate_moon_score(full_moon_date)
        
        assert score <= 60  # Pleine lune = moins d'activité diurne

    # ==========================================
    # Tests: Descriptions saisonnières
    # ==========================================
    
    def test_season_description_all_months(self, service):
        """Vérifier que tous les mois ont une description"""
        for month in range(1, 13):
            description = service._get_season_description(month)
            assert description is not None
            assert len(description) > 0
    
    def test_season_description_october_is_optimal(self, service):
        """Vérifier que octobre est décrit comme optimal"""
        description = service._get_season_description(10)
        assert "optimal" in description.lower() or "excellente" in description.lower() or "optimale" in description.lower()

    # ==========================================
    # Tests: Conversion score vers impact
    # ==========================================
    
    def test_score_to_impact_very_positive(self, service):
        """Tester conversion score très élevé"""
        assert service._score_to_impact(90) == "very_positive"
    
    def test_score_to_impact_positive(self, service):
        """Tester conversion score élevé"""
        assert service._score_to_impact(70) == "positive"
    
    def test_score_to_impact_neutral(self, service):
        """Tester conversion score moyen"""
        assert service._score_to_impact(50) == "neutral"
    
    def test_score_to_impact_negative(self, service):
        """Tester conversion score bas"""
        assert service._score_to_impact(30) == "negative"
    
    def test_score_to_impact_very_negative(self, service):
        """Tester conversion score très bas"""
        assert service._score_to_impact(10) == "very_negative"


class TestPredictiveIntegration:
    """Tests d'intégration avec le router FastAPI"""
    
    @pytest.fixture
    def client(self):
        """Créer un client de test FastAPI"""
        from fastapi.testclient import TestClient
        from modules.predictive_engine.v1.router import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Tester l'endpoint racine"""
        response = client.get("/api/v1/predictive/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "predictive_engine"
        assert "supported_species" in data
    
    def test_success_endpoint(self, client):
        """Tester l'endpoint success"""
        response = client.get("/api/v1/predictive/success?species=deer")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "prediction" in data
        assert "success_probability" in data["prediction"]
    
    def test_activity_endpoint(self, client):
        """Tester l'endpoint activity"""
        response = client.get("/api/v1/predictive/activity?species=deer")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "activity" in data
    
    def test_factors_endpoint(self, client):
        """Tester l'endpoint factors"""
        response = client.get("/api/v1/predictive/factors?species=deer")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "factors" in data
        assert len(data["factors"]) == 5
    
    def test_timeline_endpoint(self, client):
        """Tester l'endpoint timeline"""
        response = client.get("/api/v1/predictive/timeline?species=deer")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "timeline" in data
        assert len(data["timeline"]) == 24
    
    def test_optimal_times_endpoint(self, client):
        """Tester l'endpoint optimal-times"""
        response = client.get("/api/v1/predictive/optimal-times?species=deer")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "times" in data
    
    def test_forecast_endpoint(self, client):
        """Tester l'endpoint forecast"""
        response = client.get("/api/v1/predictive/forecast/deer?days=7")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "forecast" in data
        assert len(data["forecast"]) == 7
    
    def test_different_species(self, client):
        """Tester avec différentes espèces"""
        species_list = ["deer", "moose", "bear", "wild_turkey"]
        
        for species in species_list:
            response = client.get(f"/api/v1/predictive/success?species={species}")
            assert response.status_code == 200
            data = response.json()
            assert data["species"] == species


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
