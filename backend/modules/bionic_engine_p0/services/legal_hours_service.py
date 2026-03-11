"""
BIONIC ENGINE — Legal Hours Service
=====================================
Module isolé pour le calcul des heures légales de chasse.

RÈGLE RÉGLEMENTAIRE:
- Début: 30 minutes AVANT le lever du soleil
- Fin: 30 minutes APRÈS le coucher du soleil

FONCTIONNALITÉS:
- Calcul lever/coucher soleil pour une position GPS
- Application de la marge réglementaire (+/- 30 min)
- Clipping des fenêtres temporelles aux heures légales
- Validation de conformité d'une heure donnée

ISOLATION:
- Aucune dépendance aux autres services BIONIC
- Aucun import transversal
- Interface pure via fonctions et dataclasses

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

import logging
from datetime import datetime, date, time, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
from zoneinfo import ZoneInfo

from astral import LocationInfo
from astral.sun import sun

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

# Marge réglementaire en minutes
LEGAL_MARGIN_MINUTES = 30

# Fuseaux horaires par région
TIMEZONE_BY_REGION = {
    "CA-QC": "America/Montreal",
    "CA-ON": "America/Toronto",
    "US-NY": "America/New_York",
    "FR-ARA": "Europe/Paris",
    "DEFAULT": "America/Montreal"
}


# =============================================================================
# DATA CONTRACTS
# =============================================================================

class LegalStatus(str, Enum):
    """Statut de conformité aux heures légales."""
    LEGAL = "legal"           # Dans la période autorisée
    ILLEGAL = "illegal"       # Hors période autorisée
    MARGINAL = "marginal"     # Proche des limites (< 15 min)


@dataclass
class SunTimes:
    """Heures de lever et coucher du soleil."""
    sunrise: datetime
    sunset: datetime
    dawn: datetime      # Aube civile
    dusk: datetime      # Crépuscule civil
    date: date
    latitude: float
    longitude: float
    timezone_name: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sunrise": self.sunrise.isoformat(),
            "sunset": self.sunset.isoformat(),
            "dawn": self.dawn.isoformat(),
            "dusk": self.dusk.isoformat(),
            "date": self.date.isoformat(),
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone_name
        }


@dataclass
class LegalHuntingWindow:
    """Fenêtre de chasse légale pour une journée."""
    date: date
    start_time: datetime      # Lever - 30 min
    end_time: datetime        # Coucher + 30 min
    sunrise: datetime
    sunset: datetime
    duration_hours: float
    timezone_name: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "legal_start": self.start_time.strftime("%H:%M"),
            "legal_end": self.end_time.strftime("%H:%M"),
            "sunrise": self.sunrise.strftime("%H:%M"),
            "sunset": self.sunset.strftime("%H:%M"),
            "duration_hours": round(self.duration_hours, 2),
            "duration_formatted": f"{int(self.duration_hours)}h{int((self.duration_hours % 1) * 60):02d}min",
            "timezone": self.timezone_name
        }


@dataclass
class LegalCheckResult:
    """Résultat de vérification de conformité."""
    is_legal: bool
    status: LegalStatus
    target_time: datetime
    legal_window: LegalHuntingWindow
    minutes_from_start: float   # Minutes depuis le début légal (négatif si avant)
    minutes_to_end: float       # Minutes jusqu'à la fin légale (négatif si après)
    message: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_legal": self.is_legal,
            "status": self.status.value,
            "target_time": self.target_time.isoformat(),
            "legal_window": self.legal_window.to_dict(),
            "minutes_from_start": round(self.minutes_from_start, 1),
            "minutes_to_end": round(self.minutes_to_end, 1),
            "message": self.message
        }


@dataclass
class ClippedTimeWindow:
    """Fenêtre temporelle clippée aux heures légales."""
    original_start: datetime
    original_end: datetime
    clipped_start: datetime
    clipped_end: datetime
    was_clipped: bool
    is_fully_legal: bool
    is_fully_illegal: bool
    legal_duration_minutes: float
    legal_badge: str    # "⚖️ LÉGAL" ou "⚠️ CLIPPÉ" ou "❌ ILLÉGAL"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "original": {
                "start": self.original_start.strftime("%H:%M"),
                "end": self.original_end.strftime("%H:%M")
            },
            "clipped": {
                "start": self.clipped_start.strftime("%H:%M"),
                "end": self.clipped_end.strftime("%H:%M")
            },
            "was_clipped": self.was_clipped,
            "is_fully_legal": self.is_fully_legal,
            "is_fully_illegal": self.is_fully_illegal,
            "legal_duration_minutes": round(self.legal_duration_minutes, 1),
            "legal_badge": self.legal_badge
        }


# =============================================================================
# LEGAL HOURS SERVICE
# =============================================================================

class LegalHoursService:
    """
    Service de calcul des heures légales de chasse.
    
    ISOLATION TOTALE:
    - Aucune dépendance aux autres services BIONIC
    - Utilise uniquement la bibliothèque 'astral' pour les calculs solaires
    - Interface pure via méthodes stateless
    
    RÈGLE RÉGLEMENTAIRE:
    - Chasse autorisée: 30 min avant lever → 30 min après coucher
    """
    
    def __init__(self, default_region: str = "CA-QC"):
        """
        Initialise le service.
        
        Args:
            default_region: Région par défaut pour le fuseau horaire
        """
        self._default_region = default_region
        self._margin = timedelta(minutes=LEGAL_MARGIN_MINUTES)
    
    def get_timezone_for_region(self, region: str) -> ZoneInfo:
        """Retourne le fuseau horaire pour une région."""
        tz_name = TIMEZONE_BY_REGION.get(region, TIMEZONE_BY_REGION["DEFAULT"])
        return ZoneInfo(tz_name)
    
    def get_timezone_name_for_region(self, region: str) -> str:
        """Retourne le nom du fuseau horaire pour une région."""
        return TIMEZONE_BY_REGION.get(region, TIMEZONE_BY_REGION["DEFAULT"])
    
    def calculate_sun_times(
        self,
        latitude: float,
        longitude: float,
        target_date: Optional[date] = None,
        region: str = "CA-QC"
    ) -> SunTimes:
        """
        Calcule les heures de lever et coucher du soleil.
        
        Args:
            latitude: Latitude de la position
            longitude: Longitude de la position
            target_date: Date cible (défaut: aujourd'hui)
            region: Région pour le fuseau horaire
            
        Returns:
            SunTimes avec toutes les informations solaires
        """
        if target_date is None:
            tz = self.get_timezone_for_region(region)
            target_date = datetime.now(tz).date()
        
        tz_name = self.get_timezone_name_for_region(region)
        
        # Créer la location pour astral
        location = LocationInfo(
            name="Target",
            region=region,
            timezone=tz_name,
            latitude=latitude,
            longitude=longitude
        )
        
        # Calculer les heures solaires
        s = sun(location.observer, date=target_date, tzinfo=ZoneInfo(tz_name))
        
        return SunTimes(
            sunrise=s["sunrise"],
            sunset=s["sunset"],
            dawn=s["dawn"],
            dusk=s["dusk"],
            date=target_date,
            latitude=latitude,
            longitude=longitude,
            timezone_name=tz_name
        )
    
    def get_legal_hunting_window(
        self,
        latitude: float,
        longitude: float,
        target_date: Optional[date] = None,
        region: str = "CA-QC"
    ) -> LegalHuntingWindow:
        """
        Calcule la fenêtre de chasse légale pour une position et une date.
        
        RÈGLE: 30 min avant lever → 30 min après coucher
        
        Args:
            latitude: Latitude de la position
            longitude: Longitude de la position
            target_date: Date cible (défaut: aujourd'hui)
            region: Région pour le fuseau horaire
            
        Returns:
            LegalHuntingWindow avec les bornes légales
        """
        sun_times = self.calculate_sun_times(latitude, longitude, target_date, region)
        
        # Appliquer la marge réglementaire
        legal_start = sun_times.sunrise - self._margin
        legal_end = sun_times.sunset + self._margin
        
        # Calculer la durée
        duration = (legal_end - legal_start).total_seconds() / 3600
        
        return LegalHuntingWindow(
            date=sun_times.date,
            start_time=legal_start,
            end_time=legal_end,
            sunrise=sun_times.sunrise,
            sunset=sun_times.sunset,
            duration_hours=duration,
            timezone_name=sun_times.timezone_name
        )
    
    def check_legal_status(
        self,
        target_time: datetime,
        latitude: float,
        longitude: float,
        region: str = "CA-QC"
    ) -> LegalCheckResult:
        """
        Vérifie si une heure est dans la période légale de chasse.
        
        Args:
            target_time: Heure à vérifier
            latitude: Latitude de la position
            longitude: Longitude de la position
            region: Région pour le fuseau horaire
            
        Returns:
            LegalCheckResult avec le statut de conformité
        """
        # S'assurer que target_time a un fuseau horaire
        if target_time.tzinfo is None:
            tz = self.get_timezone_for_region(region)
            target_time = target_time.replace(tzinfo=tz)
        
        # Obtenir la fenêtre légale pour cette date
        legal_window = self.get_legal_hunting_window(
            latitude, longitude, 
            target_time.date(), 
            region
        )
        
        # Calculer les distances aux bornes
        minutes_from_start = (target_time - legal_window.start_time).total_seconds() / 60
        minutes_to_end = (legal_window.end_time - target_time).total_seconds() / 60
        
        # Déterminer le statut
        is_legal = legal_window.start_time <= target_time <= legal_window.end_time
        
        if not is_legal:
            status = LegalStatus.ILLEGAL
            if minutes_from_start < 0:
                message = f"Trop tôt: {abs(minutes_from_start):.0f} min avant le début légal"
            else:
                message = f"Trop tard: {abs(minutes_to_end):.0f} min après la fin légale"
        elif minutes_from_start < 15 or minutes_to_end < 15:
            status = LegalStatus.MARGINAL
            if minutes_from_start < 15:
                message = f"Proche du début: {minutes_from_start:.0f} min depuis l'ouverture"
            else:
                message = f"Proche de la fin: {minutes_to_end:.0f} min avant la fermeture"
        else:
            status = LegalStatus.LEGAL
            message = "Période légale de chasse"
        
        return LegalCheckResult(
            is_legal=is_legal,
            status=status,
            target_time=target_time,
            legal_window=legal_window,
            minutes_from_start=minutes_from_start,
            minutes_to_end=minutes_to_end,
            message=message
        )
    
    def clip_to_legal_window(
        self,
        start_time: datetime,
        end_time: datetime,
        latitude: float,
        longitude: float,
        region: str = "CA-QC"
    ) -> ClippedTimeWindow:
        """
        Clippe une fenêtre temporelle aux heures légales.
        
        Args:
            start_time: Début de la fenêtre originale
            end_time: Fin de la fenêtre originale
            latitude: Latitude de la position
            longitude: Longitude de la position
            region: Région pour le fuseau horaire
            
        Returns:
            ClippedTimeWindow avec la fenêtre ajustée
        """
        # S'assurer des fuseaux horaires
        tz = self.get_timezone_for_region(region)
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=tz)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=tz)
        
        # Obtenir la fenêtre légale
        legal_window = self.get_legal_hunting_window(
            latitude, longitude,
            start_time.date(),
            region
        )
        
        legal_start = legal_window.start_time
        legal_end = legal_window.end_time
        
        # Vérifier si complètement illégal
        if end_time <= legal_start or start_time >= legal_end:
            return ClippedTimeWindow(
                original_start=start_time,
                original_end=end_time,
                clipped_start=start_time,
                clipped_end=start_time,  # Durée = 0
                was_clipped=True,
                is_fully_legal=False,
                is_fully_illegal=True,
                legal_duration_minutes=0,
                legal_badge="❌ HORS HEURES LÉGALES"
            )
        
        # Clipper aux bornes légales
        clipped_start = max(start_time, legal_start)
        clipped_end = min(end_time, legal_end)
        
        # Calculer la durée légale
        legal_duration = (clipped_end - clipped_start).total_seconds() / 60
        
        # Déterminer si clippé
        was_clipped = (start_time < legal_start) or (end_time > legal_end)
        is_fully_legal = not was_clipped
        
        # Badge
        if is_fully_legal:
            badge = "⚖️ LÉGAL"
        else:
            badge = "⚖️ CLIPPÉ"
        
        return ClippedTimeWindow(
            original_start=start_time,
            original_end=end_time,
            clipped_start=clipped_start,
            clipped_end=clipped_end,
            was_clipped=was_clipped,
            is_fully_legal=is_fully_legal,
            is_fully_illegal=False,
            legal_duration_minutes=legal_duration,
            legal_badge=badge
        )
    
    def get_optimal_windows_legal(
        self,
        latitude: float,
        longitude: float,
        target_date: Optional[date] = None,
        region: str = "CA-QC"
    ) -> List[Dict[str, Any]]:
        """
        Retourne les fenêtres optimales de chasse respectant les heures légales.
        
        Les fenêtres sont:
        - Aube: début légal → lever + 2h (ou max 3h après début légal)
        - Matin: lever + 2h → 11h
        - Crépuscule: coucher - 2h → fin légale
        - Soir: 16h → coucher - 2h
        
        Args:
            latitude: Latitude
            longitude: Longitude
            target_date: Date cible
            region: Région
            
        Returns:
            Liste des fenêtres optimales avec scores relatifs
        """
        legal_window = self.get_legal_hunting_window(
            latitude, longitude, target_date, region
        )
        
        tz = self.get_timezone_for_region(region)
        sunrise = legal_window.sunrise
        sunset = legal_window.sunset
        legal_start = legal_window.start_time
        legal_end = legal_window.end_time
        
        windows = []
        
        # 1. AUBE (Excellent) - début légal → lever + 2h
        dawn_end = min(sunrise + timedelta(hours=2), legal_end)
        if legal_start < dawn_end:
            windows.append({
                "period": "dawn",
                "label": "Aube",
                "icon": "🌅",
                "start": legal_start.strftime("%H:%M"),
                "end": dawn_end.strftime("%H:%M"),
                "start_hour": legal_start.hour,
                "end_hour": dawn_end.hour,
                "quality": "excellent",
                "score_modifier": 1.0,
                "description": "Période d'activité maximale",
                "legal_badge": "⚖️ LÉGAL"
            })
        
        # 2. MATIN (Bon) - lever + 2h → 11h
        morning_start = sunrise + timedelta(hours=2)
        morning_end = datetime.combine(legal_window.date, time(11, 0), tzinfo=tz)
        if morning_start < morning_end and morning_start < legal_end:
            morning_end = min(morning_end, legal_end)
            windows.append({
                "period": "morning",
                "label": "Matin",
                "icon": "🌤",
                "start": morning_start.strftime("%H:%M"),
                "end": morning_end.strftime("%H:%M"),
                "start_hour": morning_start.hour,
                "end_hour": morning_end.hour,
                "quality": "good",
                "score_modifier": 0.7,
                "description": "Activité modérée",
                "legal_badge": "⚖️ LÉGAL"
            })
        
        # 3. CRÉPUSCULE (Excellent) - coucher - 2h → fin légale
        dusk_start = max(sunset - timedelta(hours=2), legal_start)
        if dusk_start < legal_end:
            windows.append({
                "period": "dusk",
                "label": "Crépuscule",
                "icon": "🌆",
                "start": dusk_start.strftime("%H:%M"),
                "end": legal_end.strftime("%H:%M"),
                "start_hour": dusk_start.hour,
                "end_hour": legal_end.hour,
                "quality": "excellent",
                "score_modifier": 1.0,
                "description": "Période d'activité maximale",
                "legal_badge": "⚖️ LÉGAL"
            })
        
        # 4. APRÈS-MIDI (Modéré) - 14h → coucher - 2h
        afternoon_start = datetime.combine(legal_window.date, time(14, 0), tzinfo=tz)
        afternoon_end = sunset - timedelta(hours=2)
        if afternoon_start < afternoon_end and afternoon_start >= legal_start:
            windows.append({
                "period": "afternoon",
                "label": "Après-midi",
                "icon": "☀️",
                "start": afternoon_start.strftime("%H:%M"),
                "end": afternoon_end.strftime("%H:%M"),
                "start_hour": afternoon_start.hour,
                "end_hour": afternoon_end.hour,
                "quality": "moderate",
                "score_modifier": 0.5,
                "description": "Activité réduite",
                "legal_badge": "⚖️ LÉGAL"
            })
        
        return windows
    
    def calculate_temporal_factor(
        self,
        target_time: datetime,
        latitude: float,
        longitude: float,
        region: str = "CA-QC"
    ) -> float:
        """
        Calcule le facteur temporel pour le scoring.
        
        RÈGLE: temporal_factor = 0 si hors heures légales
        
        Args:
            target_time: Heure cible
            latitude: Latitude
            longitude: Longitude
            region: Région
            
        Returns:
            Facteur temporel entre 0 et 1
        """
        check = self.check_legal_status(target_time, latitude, longitude, region)
        
        if not check.is_legal:
            # RÈGLE BIONIC V5: temporal_factor = 0 hors période légale
            return 0.0
        
        legal_window = check.legal_window
        sunrise = legal_window.sunrise
        sunset = legal_window.sunset
        
        # Calculer la position relative dans la journée
        hour = target_time.hour + target_time.minute / 60
        
        # Heures d'aube et crépuscule
        sunrise_hour = sunrise.hour + sunrise.minute / 60
        sunset_hour = sunset.hour + sunset.minute / 60
        
        # Facteur maximal à l'aube et au crépuscule
        dawn_window = (sunrise_hour - 0.5, sunrise_hour + 2)
        dusk_window = (sunset_hour - 2, sunset_hour + 0.5)
        
        if dawn_window[0] <= hour <= dawn_window[1]:
            # Dans la fenêtre de l'aube - score élevé
            return 0.95
        elif dusk_window[0] <= hour <= dusk_window[1]:
            # Dans la fenêtre du crépuscule - score élevé
            return 0.95
        elif hour < 12:
            # Matin - score modéré décroissant
            return max(0.4, 0.7 - (hour - sunrise_hour) * 0.05)
        elif hour < 16:
            # Mi-journée - score faible
            return 0.3
        else:
            # Après-midi - score modéré croissant vers le crépuscule
            return min(0.7, 0.3 + (hour - 14) * 0.1)


# =============================================================================
# SINGLETON
# =============================================================================

_legal_hours_service: Optional[LegalHoursService] = None


def get_legal_hours_service() -> LegalHoursService:
    """Retourne l'instance singleton du service."""
    global _legal_hours_service
    if _legal_hours_service is None:
        _legal_hours_service = LegalHoursService()
    return _legal_hours_service


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'LegalHoursService',
    'get_legal_hours_service',
    'LegalHuntingWindow',
    'LegalCheckResult',
    'ClippedTimeWindow',
    'SunTimes',
    'LegalStatus',
    'LEGAL_MARGIN_MINUTES',
    'TIMEZONE_BY_REGION'
]
