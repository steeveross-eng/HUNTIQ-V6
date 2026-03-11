"""
Tests Unitaires - Legal Time Engine
====================================
Tests complets pour le module de calcul des heures légales de chasse.

Version: 1.0.0
Date: 2026-02-09
"""

import pytest
from datetime import date, time, datetime, timedelta
from unittest.mock import patch, MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.legal_time_engine.v1.service import LegalTimeService
from modules.legal_time_engine.v1.models import LocationInput, SunTimes, LegalHuntingWindow


class TestLegalTimeService:
    """Tests pour LegalTimeService"""
    
    @pytest.fixture
    def service(self):
        """Fixture pour créer une instance du service"""
        return LegalTimeService()
    
    @pytest.fixture
    def quebec_location(self):
        """Fixture pour la localisation Québec par défaut"""
        return LocationInput(
            latitude=46.8139,
            longitude=-71.2080,
            timezone="America/Toronto"
        )
    
    @pytest.fixture
    def montreal_location(self):
        """Fixture pour Montréal"""
        return LocationInput(
            latitude=45.5017,
            longitude=-73.5673,
            timezone="America/Toronto"
        )

    # ==========================================
    # Tests: Configuration par défaut
    # ==========================================
    
    def test_default_location_is_quebec(self, service):
        """Vérifier que la localisation par défaut est Québec"""
        assert service.DEFAULT_LOCATION.latitude == 46.8139
        assert service.DEFAULT_LOCATION.longitude == -71.2080
        assert service.DEFAULT_LOCATION.timezone == "America/Toronto"
    
    def test_legal_offset_is_30_minutes(self, service):
        """Vérifier que l'offset légal est de 30 minutes"""
        assert service.LEGAL_OFFSET_MINUTES == 30

    # ==========================================
    # Tests: Calcul lever/coucher du soleil
    # ==========================================
    
    def test_get_sun_times_returns_valid_structure(self, service, quebec_location):
        """Vérifier que get_sun_times retourne une structure valide"""
        result = service.get_sun_times(date.today(), quebec_location)
        
        assert isinstance(result, SunTimes)
        assert isinstance(result.sunrise, time)
        assert isinstance(result.sunset, time)
        assert isinstance(result.dawn, time)
        assert isinstance(result.dusk, time)
        assert isinstance(result.day_length_minutes, int)
    
    def test_sun_times_sunrise_before_sunset(self, service, quebec_location):
        """Vérifier que le lever est avant le coucher"""
        result = service.get_sun_times(date.today(), quebec_location)
        
        # Convertir en minutes depuis minuit pour comparer
        sunrise_mins = result.sunrise.hour * 60 + result.sunrise.minute
        sunset_mins = result.sunset.hour * 60 + result.sunset.minute
        
        assert sunrise_mins < sunset_mins
    
    def test_sun_times_dawn_before_sunrise(self, service, quebec_location):
        """Vérifier que l'aube civile est avant le lever"""
        result = service.get_sun_times(date.today(), quebec_location)
        
        dawn_mins = result.dawn.hour * 60 + result.dawn.minute
        sunrise_mins = result.sunrise.hour * 60 + result.sunrise.minute
        
        assert dawn_mins < sunrise_mins
    
    def test_sun_times_dusk_after_sunset(self, service, quebec_location):
        """Vérifier que le crépuscule est après le coucher"""
        result = service.get_sun_times(date.today(), quebec_location)
        
        sunset_mins = result.sunset.hour * 60 + result.sunset.minute
        dusk_mins = result.dusk.hour * 60 + result.dusk.minute
        
        assert dusk_mins > sunset_mins
    
    def test_sun_times_day_length_reasonable(self, service, quebec_location):
        """Vérifier que la durée du jour est raisonnable (6-18h)"""
        result = service.get_sun_times(date.today(), quebec_location)
        
        # Entre 6 et 18 heures de jour
        assert 360 <= result.day_length_minutes <= 1080
    
    def test_sun_times_winter_shorter_days(self, service, quebec_location):
        """Vérifier que les jours d'hiver sont plus courts"""
        winter_date = date(2026, 12, 21)  # Solstice d'hiver
        summer_date = date(2026, 6, 21)   # Solstice d'été
        
        winter_result = service.get_sun_times(winter_date, quebec_location)
        summer_result = service.get_sun_times(summer_date, quebec_location)
        
        assert winter_result.day_length_minutes < summer_result.day_length_minutes
    
    def test_sun_times_different_locations(self, service, quebec_location, montreal_location):
        """Vérifier que différentes locations donnent des heures différentes"""
        quebec_result = service.get_sun_times(date.today(), quebec_location)
        montreal_result = service.get_sun_times(date.today(), montreal_location)
        
        # Les heures devraient être légèrement différentes
        # (Québec est plus au nord-est que Montréal)
        assert quebec_result.sunrise != montreal_result.sunrise or \
               quebec_result.sunset != montreal_result.sunset

    # ==========================================
    # Tests: Fenêtre légale de chasse
    # ==========================================
    
    def test_legal_window_30_min_before_sunrise(self, service, quebec_location):
        """Vérifier que le début légal est 30 min avant le lever"""
        result = service.get_legal_hunting_window(date.today(), quebec_location)
        sun_times = service.get_sun_times(date.today(), quebec_location)
        
        # Calculer la différence
        legal_start_mins = result.start_time.hour * 60 + result.start_time.minute
        sunrise_mins = sun_times.sunrise.hour * 60 + sun_times.sunrise.minute
        
        assert sunrise_mins - legal_start_mins == 30
    
    def test_legal_window_30_min_after_sunset(self, service, quebec_location):
        """Vérifier que la fin légale est 30 min après le coucher"""
        result = service.get_legal_hunting_window(date.today(), quebec_location)
        sun_times = service.get_sun_times(date.today(), quebec_location)
        
        # Calculer la différence
        legal_end_mins = result.end_time.hour * 60 + result.end_time.minute
        sunset_mins = sun_times.sunset.hour * 60 + sun_times.sunset.minute
        
        assert legal_end_mins - sunset_mins == 30
    
    def test_legal_window_duration_calculation(self, service, quebec_location):
        """Vérifier le calcul de la durée de la fenêtre légale"""
        result = service.get_legal_hunting_window(date.today(), quebec_location)
        
        # La durée devrait être day_length + 60 minutes (30 avant + 30 après)
        sun_times = service.get_sun_times(date.today(), quebec_location)
        expected_duration = sun_times.day_length_minutes + 60
        
        assert abs(result.duration_minutes - expected_duration) <= 1  # Tolérance 1 min
    
    def test_legal_window_contains_sunrise_sunset(self, service, quebec_location):
        """Vérifier que la fenêtre légale contient le lever et coucher"""
        result = service.get_legal_hunting_window(date.today(), quebec_location)
        
        start_mins = result.start_time.hour * 60 + result.start_time.minute
        end_mins = result.end_time.hour * 60 + result.end_time.minute
        sunrise_mins = result.sunrise.hour * 60 + result.sunrise.minute
        sunset_mins = result.sunset.hour * 60 + result.sunset.minute
        
        assert start_mins < sunrise_mins
        assert end_mins > sunset_mins

    # ==========================================
    # Tests: Vérification légalité temps réel
    # ==========================================
    
    def test_is_time_legal_during_day(self, service, quebec_location):
        """Vérifier qu'une heure en plein jour est légale"""
        # 12:00 devrait toujours être légal
        test_datetime = datetime.combine(
            date.today(), 
            time(12, 0),
            tzinfo=__import__('zoneinfo').ZoneInfo("America/Toronto")
        )
        
        is_legal, message = service.is_time_legal(test_datetime, quebec_location)
        
        assert is_legal is True
        assert "Période légale" in message
    
    def test_is_time_legal_at_night(self, service, quebec_location):
        """Vérifier qu'une heure en pleine nuit est illégale"""
        # 02:00 devrait toujours être illégal
        test_datetime = datetime.combine(
            date.today(), 
            time(2, 0),
            tzinfo=__import__('zoneinfo').ZoneInfo("America/Toronto")
        )
        
        is_legal, message = service.is_time_legal(test_datetime, quebec_location)
        
        assert is_legal is False
        assert "Hors période légale" in message

    # ==========================================
    # Tests: Créneaux recommandés
    # ==========================================
    
    def test_recommended_slots_returns_list(self, service, quebec_location):
        """Vérifier que les créneaux recommandés retournent une liste"""
        result = service.get_recommended_hunting_slots(date.today(), quebec_location)
        
        assert isinstance(result, list)
        assert len(result) >= 3  # Au moins aube, crépuscule, mi-journée
    
    def test_recommended_slots_all_legal(self, service, quebec_location):
        """Vérifier que tous les créneaux recommandés sont légaux"""
        result = service.get_recommended_hunting_slots(date.today(), quebec_location)
        
        for slot in result:
            assert slot.is_legal is True
    
    def test_recommended_slots_dawn_highest_score(self, service, quebec_location):
        """Vérifier que l'aube a le meilleur score"""
        result = service.get_recommended_hunting_slots(date.today(), quebec_location)
        
        # Le premier créneau (trié par score) devrait être l'aube avec score 95
        assert result[0].period_name == "Aube"
        assert result[0].score == 95
    
    def test_recommended_slots_have_recommendations(self, service, quebec_location):
        """Vérifier que chaque créneau a une recommandation"""
        result = service.get_recommended_hunting_slots(date.today(), quebec_location)
        
        for slot in result:
            assert slot.recommendation is not None
            assert len(slot.recommendation) > 0

    # ==========================================
    # Tests: Programme journalier complet
    # ==========================================
    
    def test_daily_schedule_complete(self, service, quebec_location):
        """Vérifier que le programme journalier est complet"""
        result = service.get_daily_schedule(date.today(), quebec_location)
        
        assert result.date == date.today()
        assert result.sun_times is not None
        assert result.legal_window is not None
        assert result.recommended_slots is not None
        assert result.best_slot is not None
    
    def test_daily_schedule_best_slot_is_first(self, service, quebec_location):
        """Vérifier que le meilleur créneau correspond au premier de la liste"""
        result = service.get_daily_schedule(date.today(), quebec_location)
        
        if result.recommended_slots and result.best_slot:
            assert result.best_slot.score == result.recommended_slots[0].score

    # ==========================================
    # Tests: Prévisions multi-jours
    # ==========================================
    
    def test_multi_day_forecast_correct_count(self, service, quebec_location):
        """Vérifier que les prévisions retournent le bon nombre de jours"""
        days = 7
        result = service.get_multi_day_forecast(date.today(), days, quebec_location)
        
        assert len(result.schedules) == days
    
    def test_multi_day_forecast_consecutive_dates(self, service, quebec_location):
        """Vérifier que les dates sont consécutives"""
        days = 7
        result = service.get_multi_day_forecast(date.today(), days, quebec_location)
        
        for i in range(1, len(result.schedules)):
            expected_date = result.schedules[i-1].date + timedelta(days=1)
            assert result.schedules[i].date == expected_date
    
    def test_multi_day_forecast_all_have_legal_windows(self, service, quebec_location):
        """Vérifier que chaque jour a une fenêtre légale"""
        result = service.get_multi_day_forecast(date.today(), 7, quebec_location)
        
        for schedule in result.schedules:
            assert schedule.legal_window is not None
            assert schedule.legal_window.start_time is not None
            assert schedule.legal_window.end_time is not None


class TestLegalTimeEdgeCases:
    """Tests pour les cas limites"""
    
    @pytest.fixture
    def service(self):
        return LegalTimeService()
    
    def test_far_north_location_summer(self, service):
        """Tester une localisation nordique en été (jours très longs)"""
        # Kuujjuaq, Nunavik (nord du Québec)
        north_location = LocationInput(
            latitude=58.1,
            longitude=-68.4,
            timezone="America/Toronto"
        )
        
        summer_date = date(2026, 6, 21)
        result = service.get_sun_times(summer_date, north_location)
        
        # Jour très long au nord en été
        assert result.day_length_minutes > 1000  # Plus de 16h
    
    def test_far_north_location_winter(self, service):
        """Tester une localisation nordique en hiver (jours très courts)"""
        north_location = LocationInput(
            latitude=58.1,
            longitude=-68.4,
            timezone="America/Toronto"
        )
        
        winter_date = date(2026, 12, 21)
        result = service.get_sun_times(winter_date, north_location)
        
        # Jour très court au nord en hiver
        assert result.day_length_minutes < 400  # Moins de 6h30
    
    def test_date_in_past(self, service):
        """Tester avec une date passée"""
        past_date = date(2020, 6, 15)
        result = service.get_sun_times(past_date)
        
        assert result is not None
        assert result.date == past_date
    
    def test_date_in_future(self, service):
        """Tester avec une date future"""
        future_date = date(2030, 6, 15)
        result = service.get_sun_times(future_date)
        
        assert result is not None
        assert result.date == future_date


class TestLegalTimeIntegration:
    """Tests d'intégration avec le router FastAPI"""
    
    @pytest.fixture
    def client(self):
        """Créer un client de test FastAPI"""
        from fastapi.testclient import TestClient
        from modules.legal_time_engine.v1.router import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Tester l'endpoint racine"""
        response = client.get("/api/v1/legal-time/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "legal_time_engine"
        assert data["version"] == "1.0.0"
    
    def test_legal_window_endpoint(self, client):
        """Tester l'endpoint legal-window"""
        response = client.get("/api/v1/legal-time/legal-window")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "legal_window" in data
        assert "start_time" in data["legal_window"]
        assert "end_time" in data["legal_window"]
    
    def test_sun_times_endpoint(self, client):
        """Tester l'endpoint sun-times"""
        response = client.get("/api/v1/legal-time/sun-times")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "sun_times" in data
    
    def test_check_endpoint(self, client):
        """Tester l'endpoint check"""
        response = client.get("/api/v1/legal-time/check")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "is_legal" in data
        assert "message" in data
    
    def test_recommended_slots_endpoint(self, client):
        """Tester l'endpoint recommended-slots"""
        response = client.get("/api/v1/legal-time/recommended-slots")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "slots" in data
        assert isinstance(data["slots"], list)
    
    def test_schedule_endpoint(self, client):
        """Tester l'endpoint schedule"""
        response = client.get("/api/v1/legal-time/schedule")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "schedule" in data
    
    def test_forecast_endpoint(self, client):
        """Tester l'endpoint forecast"""
        response = client.get("/api/v1/legal-time/forecast?days=7")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "forecast" in data
        assert len(data["forecast"]["daily_schedules"]) == 7
    
    def test_invalid_date_format(self, client):
        """Tester avec un format de date invalide"""
        response = client.get("/api/v1/legal-time/legal-window?date=invalid")
        
        assert response.status_code == 400
    
    def test_custom_coordinates(self, client):
        """Tester avec des coordonnées personnalisées"""
        response = client.get("/api/v1/legal-time/legal-window?lat=45.5&lng=-73.5")
        
        assert response.status_code == 200
        data = response.json()
        assert data["location"]["latitude"] == 45.5
        assert data["location"]["longitude"] == -73.5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
