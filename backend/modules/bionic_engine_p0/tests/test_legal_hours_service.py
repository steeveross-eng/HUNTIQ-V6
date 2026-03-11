"""
BIONIC ENGINE — Legal Hours Service — Tests Unitaires
======================================================
Tests isolés pour le service LegalHoursService.

COUVERTURE:
- Calcul lever/coucher soleil
- Fenêtre de chasse légale (+/- 30 min)
- Vérification statut légal
- Clipping des fenêtres temporelles
- Facteur temporel (temporal_factor)

Conformité: G-QA | BIONIC V5
"""

import pytest
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo

# Import du module à tester
import sys
sys.path.insert(0, '/app/backend')

from modules.bionic_engine_p0.services.legal_hours_service import (
    LegalHoursService,
    get_legal_hours_service,
    LegalStatus,
    LEGAL_MARGIN_MINUTES
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def service():
    """Instance du service pour les tests."""
    return LegalHoursService()


@pytest.fixture
def quebec_coords():
    """Coordonnées de Québec City."""
    return {"latitude": 46.8139, "longitude": -71.2082}


@pytest.fixture
def test_date():
    """Date de test (21 juin - solstice d'été)."""
    return date(2025, 6, 21)


# =============================================================================
# TESTS: Calcul Lever/Coucher Soleil
# =============================================================================

class TestSunTimes:
    """Tests pour le calcul des heures solaires."""
    
    def test_calculate_sun_times_quebec(self, service, quebec_coords, test_date):
        """Test calcul lever/coucher pour Québec."""
        sun_times = service.calculate_sun_times(
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            target_date=test_date,
            region="CA-QC"
        )
        
        # Vérifications de base
        assert sun_times.sunrise is not None
        assert sun_times.sunset is not None
        assert sun_times.sunrise < sun_times.sunset
        
        # En juin à Québec, lever vers 5h, coucher vers 21h
        assert 4 <= sun_times.sunrise.hour <= 6
        assert 20 <= sun_times.sunset.hour <= 22
        
        # Métadonnées
        assert sun_times.latitude == quebec_coords["latitude"]
        assert sun_times.longitude == quebec_coords["longitude"]
        assert sun_times.date == test_date
        assert sun_times.timezone_name == "America/Montreal"
    
    def test_sun_times_serialization(self, service, quebec_coords, test_date):
        """Test sérialisation vers dict."""
        sun_times = service.calculate_sun_times(
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            target_date=test_date,
            region="CA-QC"
        )
        
        data = sun_times.to_dict()
        
        assert "sunrise" in data
        assert "sunset" in data
        assert "date" in data
        assert "timezone" in data
        assert data["timezone"] == "America/Montreal"


# =============================================================================
# TESTS: Fenêtre Légale de Chasse
# =============================================================================

class TestLegalHuntingWindow:
    """Tests pour la fenêtre de chasse légale."""
    
    def test_legal_window_margins(self, service, quebec_coords, test_date):
        """Test application des marges +/- 30 min."""
        window = service.get_legal_hunting_window(
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            target_date=test_date,
            region="CA-QC"
        )
        
        # Marge de 30 minutes
        margin = timedelta(minutes=LEGAL_MARGIN_MINUTES)
        
        # Start = lever - 30 min
        expected_start = window.sunrise - margin
        assert window.start_time == expected_start
        
        # End = coucher + 30 min
        expected_end = window.sunset + margin
        assert window.end_time == expected_end
    
    def test_legal_window_duration(self, service, quebec_coords, test_date):
        """Test calcul de la durée."""
        window = service.get_legal_hunting_window(
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            target_date=test_date,
            region="CA-QC"
        )
        
        # Durée calculée correctement
        expected_duration = (window.end_time - window.start_time).total_seconds() / 3600
        assert abs(window.duration_hours - expected_duration) < 0.01
        
        # En juin, durée d'environ 16-17 heures
        assert 15 <= window.duration_hours <= 18
    
    def test_legal_window_serialization(self, service, quebec_coords, test_date):
        """Test sérialisation de la fenêtre."""
        window = service.get_legal_hunting_window(
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            target_date=test_date,
            region="CA-QC"
        )
        
        data = window.to_dict()
        
        assert "legal_start" in data
        assert "legal_end" in data
        assert "duration_hours" in data
        assert "duration_formatted" in data
        assert "h" in data["duration_formatted"]
        assert "min" in data["duration_formatted"]


# =============================================================================
# TESTS: Vérification Statut Légal
# =============================================================================

class TestLegalStatusCheck:
    """Tests pour la vérification de conformité."""
    
    def test_legal_time_dawn(self, service, quebec_coords, test_date):
        """Test heure légale à l'aube."""
        tz = ZoneInfo("America/Montreal")
        # 6h30 - clairement dans la période légale
        target = datetime.combine(test_date, time(6, 30), tzinfo=tz)
        
        result = service.check_legal_status(
            target_time=target,
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            region="CA-QC"
        )
        
        assert result.is_legal is True
        assert result.status == LegalStatus.LEGAL
    
    def test_illegal_time_night(self, service, quebec_coords, test_date):
        """Test heure illégale (nuit)."""
        tz = ZoneInfo("America/Montreal")
        # 2h du matin - certainement illégal
        target = datetime.combine(test_date, time(2, 0), tzinfo=tz)
        
        result = service.check_legal_status(
            target_time=target,
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            region="CA-QC"
        )
        
        assert result.is_legal is False
        assert result.status == LegalStatus.ILLEGAL
        assert "avant" in result.message.lower()
    
    def test_illegal_time_late_night(self, service, quebec_coords, test_date):
        """Test heure illégale (fin de soirée)."""
        tz = ZoneInfo("America/Montreal")
        # 23h - après la fin légale
        target = datetime.combine(test_date, time(23, 0), tzinfo=tz)
        
        result = service.check_legal_status(
            target_time=target,
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            region="CA-QC"
        )
        
        assert result.is_legal is False
        assert result.status == LegalStatus.ILLEGAL
        assert "après" in result.message.lower()
    
    def test_marginal_time_near_start(self, service, quebec_coords, test_date):
        """Test heure marginale (proche du début)."""
        # Obtenir la fenêtre légale exacte
        window = service.get_legal_hunting_window(
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            target_date=test_date,
            region="CA-QC"
        )
        
        # 5 minutes après le début légal
        target = window.start_time + timedelta(minutes=5)
        
        result = service.check_legal_status(
            target_time=target,
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            region="CA-QC"
        )
        
        assert result.is_legal is True
        assert result.status == LegalStatus.MARGINAL
        assert "proche" in result.message.lower()


# =============================================================================
# TESTS: Clipping des Fenêtres
# =============================================================================

class TestWindowClipping:
    """Tests pour le clipping aux heures légales."""
    
    def test_clip_fully_legal_window(self, service, quebec_coords, test_date):
        """Test fenêtre entièrement légale (pas de clipping)."""
        tz = ZoneInfo("America/Montreal")
        
        # Fenêtre de 8h à 10h - totalement légale
        start = datetime.combine(test_date, time(8, 0), tzinfo=tz)
        end = datetime.combine(test_date, time(10, 0), tzinfo=tz)
        
        result = service.clip_to_legal_window(
            start_time=start,
            end_time=end,
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            region="CA-QC"
        )
        
        assert result.is_fully_legal is True
        assert result.was_clipped is False
        assert result.clipped_start == start
        assert result.clipped_end == end
        assert "LÉGAL" in result.legal_badge
    
    def test_clip_partially_illegal_early(self, service, quebec_coords, test_date):
        """Test fenêtre partiellement illégale (trop tôt)."""
        tz = ZoneInfo("America/Montreal")
        
        # Fenêtre de 3h à 8h - début illégal
        start = datetime.combine(test_date, time(3, 0), tzinfo=tz)
        end = datetime.combine(test_date, time(8, 0), tzinfo=tz)
        
        result = service.clip_to_legal_window(
            start_time=start,
            end_time=end,
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            region="CA-QC"
        )
        
        assert result.was_clipped is True
        assert result.is_fully_legal is False
        assert result.is_fully_illegal is False
        assert result.clipped_start > start  # Clippé au début légal
        assert result.clipped_end == end
        assert "CLIPPÉ" in result.legal_badge
    
    def test_clip_fully_illegal_window(self, service, quebec_coords, test_date):
        """Test fenêtre entièrement illégale."""
        tz = ZoneInfo("America/Montreal")
        
        # Fenêtre de 1h à 3h - totalement illégale
        start = datetime.combine(test_date, time(1, 0), tzinfo=tz)
        end = datetime.combine(test_date, time(3, 0), tzinfo=tz)
        
        result = service.clip_to_legal_window(
            start_time=start,
            end_time=end,
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            region="CA-QC"
        )
        
        assert result.is_fully_illegal is True
        assert result.legal_duration_minutes == 0
        assert "HORS HEURES LÉGALES" in result.legal_badge


# =============================================================================
# TESTS: Facteur Temporel
# =============================================================================

class TestTemporalFactor:
    """Tests pour le facteur temporel."""
    
    def test_temporal_factor_zero_illegal(self, service, quebec_coords, test_date):
        """Test temporal_factor = 0 hors heures légales."""
        tz = ZoneInfo("America/Montreal")
        
        # 2h du matin - illégal
        target = datetime.combine(test_date, time(2, 0), tzinfo=tz)
        
        factor = service.calculate_temporal_factor(
            target_time=target,
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            region="CA-QC"
        )
        
        # RÈGLE BIONIC V5: temporal_factor = 0 hors période légale
        assert factor == 0.0
    
    def test_temporal_factor_high_dawn(self, service, quebec_coords, test_date):
        """Test temporal_factor élevé à l'aube."""
        tz = ZoneInfo("America/Montreal")
        
        # 6h - période d'aube
        target = datetime.combine(test_date, time(6, 0), tzinfo=tz)
        
        factor = service.calculate_temporal_factor(
            target_time=target,
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            region="CA-QC"
        )
        
        # Facteur élevé à l'aube
        assert factor >= 0.9
    
    def test_temporal_factor_low_midday(self, service, quebec_coords, test_date):
        """Test temporal_factor faible à midi."""
        tz = ZoneInfo("America/Montreal")
        
        # 13h - mi-journée
        target = datetime.combine(test_date, time(13, 0), tzinfo=tz)
        
        factor = service.calculate_temporal_factor(
            target_time=target,
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            region="CA-QC"
        )
        
        # Facteur faible à midi
        assert factor <= 0.5


# =============================================================================
# TESTS: Fenêtres Optimales
# =============================================================================

class TestOptimalWindows:
    """Tests pour les fenêtres optimales."""
    
    def test_optimal_windows_structure(self, service, quebec_coords, test_date):
        """Test structure des fenêtres optimales."""
        windows = service.get_optimal_windows_legal(
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            target_date=test_date,
            region="CA-QC"
        )
        
        assert len(windows) >= 2  # Au moins aube et crépuscule
        
        for window in windows:
            assert "period" in window
            assert "label" in window
            assert "start" in window
            assert "end" in window
            assert "quality" in window
            assert "legal_badge" in window
            assert "⚖️" in window["legal_badge"]
    
    def test_optimal_windows_all_legal(self, service, quebec_coords, test_date):
        """Test que toutes les fenêtres sont légales."""
        windows = service.get_optimal_windows_legal(
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            target_date=test_date,
            region="CA-QC"
        )
        
        for window in windows:
            # Toutes les fenêtres doivent avoir le badge légal
            assert "LÉGAL" in window["legal_badge"]
    
    def test_dawn_and_dusk_excellent(self, service, quebec_coords, test_date):
        """Test que aube et crépuscule sont 'excellent'."""
        windows = service.get_optimal_windows_legal(
            latitude=quebec_coords["latitude"],
            longitude=quebec_coords["longitude"],
            target_date=test_date,
            region="CA-QC"
        )
        
        periods = {w["period"]: w for w in windows}
        
        assert "dawn" in periods
        assert periods["dawn"]["quality"] == "excellent"
        
        assert "dusk" in periods
        assert periods["dusk"]["quality"] == "excellent"


# =============================================================================
# TESTS: Singleton et Régions
# =============================================================================

class TestServiceMeta:
    """Tests pour le service et les régions."""
    
    def test_singleton(self):
        """Test pattern singleton."""
        service1 = get_legal_hours_service()
        service2 = get_legal_hours_service()
        
        assert service1 is service2
    
    def test_different_regions(self, service):
        """Test fuseaux horaires par région."""
        coords = {"latitude": 45.5, "longitude": -73.5}
        test_date_local = date(2025, 6, 21)
        
        # Québec
        window_qc = service.get_legal_hunting_window(
            latitude=coords["latitude"],
            longitude=coords["longitude"],
            target_date=test_date_local,
            region="CA-QC"
        )
        
        # France
        window_fr = service.get_legal_hunting_window(
            latitude=coords["latitude"],
            longitude=coords["longitude"],
            target_date=test_date_local,
            region="FR-ARA"
        )
        
        # Fuseaux différents
        assert window_qc.timezone_name == "America/Montreal"
        assert window_fr.timezone_name == "Europe/Paris"


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
