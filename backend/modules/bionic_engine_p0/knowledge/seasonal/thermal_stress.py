"""
BIONIC V5 — PHASE C.3: THERMAL STRESS MODELS
=============================================

Modèles de stress thermique estival espèce-spécifiques.

Le stress thermique affecte significativement le comportement des
ongulés et des ursidés pendant les périodes de chaleur intense.

EFFETS PRINCIPAUX:
- Réduction de l'activité diurne
- Shift vers comportement nocturne
- Recherche de refuges thermiques
- Réduction de l'alimentation
- Augmentation de la consommation d'eau

ESPÈCES SENSIBLES:
- Orignal: TRÈS SENSIBLE (seuil critique ~20°C)
- Cerf: MODÉRÉMENT SENSIBLE (seuil critique ~28°C)
- Ours: PEU SENSIBLE (adaptation large)
- Wapiti: SENSIBLE (seuil critique ~25°C)

CONFORMITÉ: G-SEC | G-QA | G-DOC | BIONIC V5
TRAÇABILITÉ: source_ids obligatoires
VERSION: 1.0.0
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("bionic_engine.thermal_stress")


# =============================================================================
# CONSTANTES ET SOURCES
# =============================================================================

SOURCE_IDS = {
    "MFFP": "SRC-MFFP-THERMAL-001",
    "LAVAL": "SRC-LAVAL-THERMO-001",
    "USGS": "SRC-USGS-CLIMATE-001",
    "RENECKER": "SRC-RENECKER-1998",       # Renecker & Hudson - Moose thermoregulation
    "DUSSAULT": "SRC-DUSSAULT-2004",       # Dussault et al. - Moose habitat summer
    "SCIENCE": "SRC-THERMAL-LITERATURE-001",
}


class ThermalSensitivity(str, Enum):
    """Niveaux de sensibilité thermique"""
    CRITICAL = "critical"       # Très sensible (orignal)
    HIGH = "high"              # Sensible (wapiti)
    MODERATE = "moderate"      # Modéré (cerf)
    LOW = "low"               # Peu sensible (ours)


class ThermalRefugeType(str, Enum):
    """Types de refuges thermiques"""
    DENSE_CANOPY = "dense_canopy"           # Couvert forestier dense
    WETLAND = "wetland"                      # Zone humide
    WATER_BODY = "water_body"                # Plan d'eau (immersion)
    NORTH_SLOPE = "north_slope"              # Pente exposée nord
    RAVINE = "ravine"                        # Ravin ombragé
    ALDER_THICKET = "alder_thicket"          # Aulnaie dense
    CONIFER_STAND = "conifer_stand"          # Peuplement conifères


class BehavioralAdaptation(str, Enum):
    """Adaptations comportementales au stress thermique"""
    NOCTURNAL_SHIFT = "nocturnal_shift"          # Activité nocturne
    REDUCED_MOVEMENT = "reduced_movement"         # Réduction des déplacements
    INCREASED_RESTING = "increased_resting"       # Repos prolongé
    WATER_SEEKING = "water_seeking"               # Recherche d'eau
    SHADE_SEEKING = "shade_seeking"               # Recherche d'ombre
    INCREASED_PANTING = "increased_panting"       # Halètement
    IMMERSION = "immersion"                       # Immersion dans l'eau (orignal)


@dataclass
class ThermalStressProfile:
    """
    Profil de stress thermique pour une espèce.
    
    Basé sur études physiologiques et comportementales.
    """
    species: str
    sensitivity: ThermalSensitivity
    
    # Seuils de température (Celsius)
    comfort_max: float              # Température max confortable
    stress_onset: float             # Début du stress thermique
    stress_moderate: float          # Stress modéré
    stress_severe: float            # Stress sévère
    critical_threshold: float       # Seuil critique (danger)
    
    # Humidité relative (facteur aggravant)
    humidity_threshold_pct: float   # Seuil d'humidité aggravant
    
    # Période vulnérable
    vulnerable_months: List[int]    # Mois de vulnérabilité (1-12)
    peak_stress_hours: List[int]    # Heures de stress maximal (0-23)
    
    # Refuges préférés (ordre de préférence)
    preferred_refuges: List[ThermalRefugeType]
    
    # Adaptations comportementales
    behavioral_adaptations: List[BehavioralAdaptation]
    
    # Modificateurs par niveau de stress
    activity_modifier_onset: float
    activity_modifier_moderate: float
    activity_modifier_severe: float
    activity_modifier_critical: float
    
    movement_modifier_onset: float
    movement_modifier_moderate: float
    movement_modifier_severe: float
    movement_modifier_critical: float
    
    feeding_modifier_onset: float
    feeding_modifier_moderate: float
    feeding_modifier_severe: float
    feeding_modifier_critical: float
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=list)
    confidence: float = 0.85
    version: str = "1.0.0"
    notes: str = ""
    
    def get_stress_level(
        self, 
        temperature: float, 
        humidity: Optional[float] = None
    ) -> Tuple[str, float]:
        """
        Détermine le niveau de stress et le modificateur global.
        
        Args:
            temperature: Température en Celsius
            humidity: Humidité relative % (optionnel)
            
        Returns:
            (stress_level, activity_modifier)
        """
        # Ajustement pour humidité élevée
        effective_temp = temperature
        if humidity and humidity > self.humidity_threshold_pct:
            # Effet humidex simplifié
            excess_humidity = humidity - self.humidity_threshold_pct
            effective_temp += excess_humidity * 0.1
        
        if effective_temp < self.comfort_max:
            return "none", 1.0
        elif effective_temp < self.stress_onset:
            return "minimal", 0.95
        elif effective_temp < self.stress_moderate:
            return "onset", self.activity_modifier_onset
        elif effective_temp < self.stress_severe:
            return "moderate", self.activity_modifier_moderate
        elif effective_temp < self.critical_threshold:
            return "severe", self.activity_modifier_severe
        else:
            return "critical", self.activity_modifier_critical
    
    def get_all_modifiers(
        self, 
        temperature: float, 
        humidity: Optional[float] = None
    ) -> Dict[str, float]:
        """Retourne tous les modificateurs pour une température."""
        stress_level, _ = self.get_stress_level(temperature, humidity)
        
        modifiers = {
            "none": {
                "activity": 1.0, "movement": 1.0, "feeding": 1.0
            },
            "minimal": {
                "activity": 0.95, "movement": 0.95, "feeding": 0.98
            },
            "onset": {
                "activity": self.activity_modifier_onset,
                "movement": self.movement_modifier_onset,
                "feeding": self.feeding_modifier_onset
            },
            "moderate": {
                "activity": self.activity_modifier_moderate,
                "movement": self.movement_modifier_moderate,
                "feeding": self.feeding_modifier_moderate
            },
            "severe": {
                "activity": self.activity_modifier_severe,
                "movement": self.movement_modifier_severe,
                "feeding": self.feeding_modifier_severe
            },
            "critical": {
                "activity": self.activity_modifier_critical,
                "movement": self.movement_modifier_critical,
                "feeding": self.feeding_modifier_critical
            }
        }
        
        return modifiers.get(stress_level, modifiers["none"])
    
    def is_peak_stress_hour(self, hour: int) -> bool:
        """Vérifie si l'heure est dans la période de stress maximal."""
        return hour in self.peak_stress_hours
    
    def to_dict(self) -> Dict[str, Any]:
        """Exporte en dictionnaire traçable."""
        return {
            "species": self.species,
            "sensitivity": self.sensitivity.value,
            "thresholds": {
                "comfort_max": self.comfort_max,
                "stress_onset": self.stress_onset,
                "stress_moderate": self.stress_moderate,
                "stress_severe": self.stress_severe,
                "critical": self.critical_threshold,
                "humidity_threshold_pct": self.humidity_threshold_pct
            },
            "vulnerability": {
                "months": self.vulnerable_months,
                "peak_hours": self.peak_stress_hours
            },
            "preferred_refuges": [r.value for r in self.preferred_refuges],
            "behavioral_adaptations": [a.value for a in self.behavioral_adaptations],
            "modifiers": {
                "onset": {
                    "activity": self.activity_modifier_onset,
                    "movement": self.movement_modifier_onset,
                    "feeding": self.feeding_modifier_onset
                },
                "moderate": {
                    "activity": self.activity_modifier_moderate,
                    "movement": self.movement_modifier_moderate,
                    "feeding": self.feeding_modifier_moderate
                },
                "severe": {
                    "activity": self.activity_modifier_severe,
                    "movement": self.movement_modifier_severe,
                    "feeding": self.feeding_modifier_severe
                },
                "critical": {
                    "activity": self.activity_modifier_critical,
                    "movement": self.movement_modifier_critical,
                    "feeding": self.feeding_modifier_critical
                }
            },
            "source_ids": self.source_ids,
            "confidence": self.confidence,
            "version": self.version,
            "notes": self.notes
        }


# =============================================================================
# REGISTRY DES PROFILS THERMIQUES
# =============================================================================

class ThermalStressRegistry:
    """
    Registre central des profils de stress thermique.
    
    Pipeline BIONIC V5:
    - Données centralisées dans le Knowledge Layer
    - Basé sur études physiologiques (Renecker, Dussault, etc.)
    - Traçabilité source_ids obligatoire
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._profiles: Dict[str, ThermalStressProfile] = {}
        self._initialize_profiles()
        self._initialized = True
        logger.info(f"[BIONIC] ThermalStressRegistry initialized with {len(self._profiles)} profiles")
    
    def _initialize_profiles(self):
        """Initialise tous les profils de stress thermique."""
        
        # =====================================================================
        # ORIGNAL (MOOSE) — TRÈS SENSIBLE
        # =====================================================================
        
        self._profiles["moose"] = ThermalStressProfile(
            species="moose",
            sensitivity=ThermalSensitivity.CRITICAL,
            
            # Seuils (basés sur Renecker & Hudson 1986, Dussault et al. 2004)
            comfort_max=14.0,
            stress_onset=17.0,
            stress_moderate=20.0,
            stress_severe=25.0,
            critical_threshold=30.0,
            
            humidity_threshold_pct=60.0,
            
            # Vulnérabilité: juillet-août
            vulnerable_months=[6, 7, 8],
            peak_stress_hours=[11, 12, 13, 14, 15, 16],  # 11h-16h
            
            # Refuges (ordre de préférence)
            preferred_refuges=[
                ThermalRefugeType.WATER_BODY,       # Immersion préférée
                ThermalRefugeType.WETLAND,
                ThermalRefugeType.DENSE_CANOPY,
                ThermalRefugeType.ALDER_THICKET,
                ThermalRefugeType.NORTH_SLOPE
            ],
            
            # Adaptations
            behavioral_adaptations=[
                BehavioralAdaptation.IMMERSION,
                BehavioralAdaptation.NOCTURNAL_SHIFT,
                BehavioralAdaptation.REDUCED_MOVEMENT,
                BehavioralAdaptation.SHADE_SEEKING,
                BehavioralAdaptation.INCREASED_PANTING
            ],
            
            # Modificateurs onset
            activity_modifier_onset=0.75,
            movement_modifier_onset=0.70,
            feeding_modifier_onset=0.85,
            
            # Modificateurs modéré
            activity_modifier_moderate=0.50,
            movement_modifier_moderate=0.40,
            feeding_modifier_moderate=0.70,
            
            # Modificateurs sévère
            activity_modifier_severe=0.25,
            movement_modifier_severe=0.20,
            feeding_modifier_severe=0.50,
            
            # Modificateurs critique
            activity_modifier_critical=0.10,
            movement_modifier_critical=0.10,
            feeding_modifier_critical=0.30,
            
            source_ids=[
                SOURCE_IDS["RENECKER"],
                SOURCE_IDS["DUSSAULT"],
                SOURCE_IDS["LAVAL"],
                SOURCE_IDS["MFFP"]
            ],
            confidence=0.92,
            notes="L'orignal est l'ongulé le plus sensible au stress thermique en raison de sa grande masse corporelle "
                  "et de sa fourrure isolante. Seuil critique ~20°C (Renecker & Hudson). "
                  "Recherche activement les plans d'eau pour immersion à partir de 17°C. "
                  "Shift quasi-total vers activité nocturne au-delà de 25°C."
        )
        
        # =====================================================================
        # CERF DE VIRGINIE — MODÉRÉMENT SENSIBLE
        # =====================================================================
        
        self._profiles["deer"] = ThermalStressProfile(
            species="deer",
            sensitivity=ThermalSensitivity.MODERATE,
            
            comfort_max=22.0,
            stress_onset=25.0,
            stress_moderate=28.0,
            stress_severe=32.0,
            critical_threshold=38.0,
            
            humidity_threshold_pct=70.0,
            
            vulnerable_months=[7, 8],
            peak_stress_hours=[12, 13, 14, 15],
            
            preferred_refuges=[
                ThermalRefugeType.DENSE_CANOPY,
                ThermalRefugeType.CONIFER_STAND,
                ThermalRefugeType.RAVINE,
                ThermalRefugeType.NORTH_SLOPE
            ],
            
            behavioral_adaptations=[
                BehavioralAdaptation.NOCTURNAL_SHIFT,
                BehavioralAdaptation.SHADE_SEEKING,
                BehavioralAdaptation.INCREASED_RESTING,
                BehavioralAdaptation.WATER_SEEKING
            ],
            
            activity_modifier_onset=0.85,
            movement_modifier_onset=0.80,
            feeding_modifier_onset=0.90,
            
            activity_modifier_moderate=0.65,
            movement_modifier_moderate=0.55,
            feeding_modifier_moderate=0.75,
            
            activity_modifier_severe=0.40,
            movement_modifier_severe=0.35,
            feeding_modifier_severe=0.55,
            
            activity_modifier_critical=0.20,
            movement_modifier_critical=0.15,
            feeding_modifier_critical=0.35,
            
            source_ids=[
                SOURCE_IDS["MFFP"],
                SOURCE_IDS["USGS"],
                SOURCE_IDS["SCIENCE"]
            ],
            confidence=0.88,
            notes="Le cerf de Virginie tolère mieux la chaleur que l'orignal grâce à sa plus petite taille "
                  "et sa fourrure moins dense en été. Préfère l'ombre au point d'eau. "
                  "Shift vers activité crépusculaire/nocturne à partir de 28°C."
        )
        
        # =====================================================================
        # OURS NOIR — PEU SENSIBLE
        # =====================================================================
        
        self._profiles["bear"] = ThermalStressProfile(
            species="bear",
            sensitivity=ThermalSensitivity.LOW,
            
            comfort_max=28.0,
            stress_onset=32.0,
            stress_moderate=35.0,
            stress_severe=38.0,
            critical_threshold=42.0,
            
            humidity_threshold_pct=75.0,
            
            vulnerable_months=[7, 8],
            peak_stress_hours=[13, 14, 15],
            
            preferred_refuges=[
                ThermalRefugeType.DENSE_CANOPY,
                ThermalRefugeType.WATER_BODY,
                ThermalRefugeType.RAVINE,
                ThermalRefugeType.WETLAND
            ],
            
            behavioral_adaptations=[
                BehavioralAdaptation.SHADE_SEEKING,
                BehavioralAdaptation.INCREASED_RESTING,
                BehavioralAdaptation.NOCTURNAL_SHIFT,
                BehavioralAdaptation.IMMERSION
            ],
            
            activity_modifier_onset=0.90,
            movement_modifier_onset=0.85,
            feeding_modifier_onset=0.95,
            
            activity_modifier_moderate=0.75,
            movement_modifier_moderate=0.70,
            feeding_modifier_moderate=0.85,
            
            activity_modifier_severe=0.55,
            movement_modifier_severe=0.50,
            feeding_modifier_severe=0.70,
            
            activity_modifier_critical=0.35,
            movement_modifier_critical=0.30,
            feeding_modifier_critical=0.50,
            
            source_ids=[
                SOURCE_IDS["MFFP"],
                SOURCE_IDS["SCIENCE"]
            ],
            confidence=0.85,
            notes="L'ours noir est relativement tolérant à la chaleur mais préfère les températures modérées. "
                  "En période de canicule, privilégie les zones humides et plans d'eau. "
                  "L'hyperphagie automnale peut être affectée par des étés très chauds."
        )
        
        # =====================================================================
        # WAPITI (ELK) — SENSIBLE
        # =====================================================================
        
        self._profiles["elk"] = ThermalStressProfile(
            species="elk",
            sensitivity=ThermalSensitivity.HIGH,
            
            comfort_max=18.0,
            stress_onset=22.0,
            stress_moderate=25.0,
            stress_severe=30.0,
            critical_threshold=35.0,
            
            humidity_threshold_pct=65.0,
            
            vulnerable_months=[6, 7, 8],
            peak_stress_hours=[11, 12, 13, 14, 15, 16],
            
            preferred_refuges=[
                ThermalRefugeType.CONIFER_STAND,
                ThermalRefugeType.NORTH_SLOPE,
                ThermalRefugeType.DENSE_CANOPY,
                ThermalRefugeType.WATER_BODY,
                ThermalRefugeType.RAVINE
            ],
            
            behavioral_adaptations=[
                BehavioralAdaptation.NOCTURNAL_SHIFT,
                BehavioralAdaptation.REDUCED_MOVEMENT,
                BehavioralAdaptation.SHADE_SEEKING,
                BehavioralAdaptation.WATER_SEEKING,
                BehavioralAdaptation.INCREASED_PANTING
            ],
            
            activity_modifier_onset=0.80,
            movement_modifier_onset=0.75,
            feeding_modifier_onset=0.85,
            
            activity_modifier_moderate=0.55,
            movement_modifier_moderate=0.50,
            feeding_modifier_moderate=0.70,
            
            activity_modifier_severe=0.30,
            movement_modifier_severe=0.25,
            feeding_modifier_severe=0.50,
            
            activity_modifier_critical=0.15,
            movement_modifier_critical=0.10,
            feeding_modifier_critical=0.35,
            
            source_ids=[
                SOURCE_IDS["USGS"],
                SOURCE_IDS["SCIENCE"]
            ],
            confidence=0.86,
            notes="Le wapiti est sensible au stress thermique, particulièrement dans les zones de prairie. "
                  "Migration altitudinale estivale courante pour éviter la chaleur. "
                  "Les hardes recherchent les versants nord et les zones de haute altitude."
        )
    
    # =========================================================================
    # MÉTHODES PUBLIQUES
    # =========================================================================
    
    def get_profile(self, species: str) -> Optional[ThermalStressProfile]:
        """Récupère le profil de stress thermique pour une espèce."""
        return self._profiles.get(species)
    
    def calculate_stress(
        self,
        species: str,
        temperature: float,
        humidity: Optional[float] = None,
        hour: Optional[int] = None,
        month: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calcule le stress thermique complet pour des conditions données.
        
        Returns:
            Dictionnaire avec niveau de stress, modificateurs, et recommandations
        """
        profile = self.get_profile(species)
        if not profile:
            return {
                "species": species,
                "profile_found": False,
                "stress_level": "unknown"
            }
        
        stress_level, _ = profile.get_stress_level(temperature, humidity)
        modifiers = profile.get_all_modifiers(temperature, humidity)
        
        # Vérifier si c'est une période vulnérable
        in_vulnerable_month = month in profile.vulnerable_months if month else False
        in_peak_hour = profile.is_peak_stress_hour(hour) if hour is not None else False
        
        # Ajustement si période de stress maximal
        if in_peak_hour and stress_level not in ["none", "minimal"]:
            for key in modifiers:
                modifiers[key] *= 0.9  # Réduction supplémentaire de 10%
        
        return {
            "species": species,
            "profile_found": True,
            "sensitivity": profile.sensitivity.value,
            "temperature": temperature,
            "humidity": humidity,
            "stress_level": stress_level,
            "in_vulnerable_month": in_vulnerable_month,
            "in_peak_hour": in_peak_hour,
            "modifiers": modifiers,
            "recommended_refuges": [r.value for r in profile.preferred_refuges[:3]],
            "expected_adaptations": [a.value for a in profile.behavioral_adaptations[:3]],
            "thresholds": {
                "comfort_max": profile.comfort_max,
                "stress_onset": profile.stress_onset,
                "critical": profile.critical_threshold
            },
            "source_ids": profile.source_ids
        }
    
    def get_all_species(self) -> List[str]:
        """Retourne la liste des espèces supportées."""
        return list(self._profiles.keys())
    
    def export_all_profiles(self) -> Dict[str, Dict]:
        """Exporte tous les profils pour documentation/API."""
        return {
            species: profile.to_dict()
            for species, profile in self._profiles.items()
        }


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_thermal_registry: Optional[ThermalStressRegistry] = None


def get_thermal_stress_registry() -> ThermalStressRegistry:
    """Retourne l'instance singleton du registre de stress thermique."""
    global _thermal_registry
    if _thermal_registry is None:
        _thermal_registry = ThermalStressRegistry()
    return _thermal_registry
