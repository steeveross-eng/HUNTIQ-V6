"""
BIONIC V5 — MOBILITY MODELS (NIVEAU 5)
======================================
NIVEAU 5 — Mobilité Dynamique

Module de modélisation de la mobilité dynamique pour la faune.

PARAMÈTRES PRINCIPAUX:
1. Vitesse moyenne (average_speed_kmh)
2. Variance de vitesse (speed_variance)
3. Direction préférentielle (preferred_direction)
4. Contraintes digestives (digestive_constraint)
5. Contraintes thermiques (thermal_constraint)
6. Modulation PRES-HUMAN (human_pressure_constraint)

KNOWLEDGE LAYER INTEGRATION:
- Mobilité dynamique basée sur le waypoint
- Intégration des facteurs NIVEAU 1-4
- Versionnement + traçabilité obligatoires

CENTRALISATION:
- Ce module FOURNIT les règles au UnifiedScoringService
- AUCUNE logique de scoring locale
- Traçabilité obligatoire (source_ids, version)

VERSION: 1.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5 NIVEAU 5
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class MovementIntensity(str, Enum):
    """Intensité de mouvement NIVEAU 5"""
    STATIONARY = "stationary"     # Immobile / repos
    LOW = "low"                   # Mouvement faible
    MODERATE = "moderate"         # Mouvement modéré
    HIGH = "high"                 # Mouvement actif
    EXTREME = "extreme"           # Mouvement maximal (rut, fuite)


class MovementDirection(str, Enum):
    """Direction préférentielle de mouvement"""
    NORTH = "north"
    NORTHEAST = "northeast"
    EAST = "east"
    SOUTHEAST = "southeast"
    SOUTH = "south"
    SOUTHWEST = "southwest"
    WEST = "west"
    NORTHWEST = "northwest"
    RANDOM = "random"             # Pas de direction préférentielle
    TOWARDS_REFUGE = "towards_refuge"
    AWAY_FROM_PRESSURE = "away_from_pressure"


class TerrainDifficulty(str, Enum):
    """Difficulté du terrain pour la mobilité"""
    EASY = "easy"                 # Terrain facile
    MODERATE = "moderate"         # Terrain modéré
    DIFFICULT = "difficult"       # Terrain difficile
    VERY_DIFFICULT = "very_difficult"
    IMPASSABLE = "impassable"


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class MobilityConstraint:
    """
    Contrainte affectant la mobilité.
    
    Représente un facteur limitant ou favorisant le mouvement.
    """
    
    constraint_type: str          # digestive, thermal, human_pressure, terrain, corridor
    constraint_level: float       # 0.0 (aucune) à 1.0 (maximale)
    effect_on_speed: float        # Multiplicateur (-1.0 à +1.0)
    effect_on_direction: float    # Impact sur la direction préférentielle
    
    # Métadonnées
    active: bool = True
    description: str = ""
    source_ids: List[str] = field(default_factory=list)
    
    def get_combined_effect(self) -> float:
        """Calcule l'effet combiné de la contrainte."""
        if not self.active:
            return 1.0
        return 1.0 + (self.effect_on_speed * self.constraint_level)


@dataclass
class MobilityParameters:
    """
    Paramètres de mobilité pour une espèce.
    
    Définit les caractéristiques de mouvement par défaut et saisonnières.
    """
    
    species: str
    
    # Vitesse
    average_speed_kmh: float = 2.0        # Vitesse moyenne
    max_speed_kmh: float = 45.0           # Vitesse maximale (fuite)
    cruise_speed_kmh: float = 3.5         # Vitesse de croisière
    
    # Variance
    speed_variance: float = 0.3           # Variance relative (0-1)
    daily_distance_km: float = 5.0        # Distance quotidienne moyenne
    
    # Patterns temporels
    peak_activity_hours: List[int] = field(default_factory=lambda: [5, 6, 7, 17, 18, 19])
    rest_hours: List[int] = field(default_factory=lambda: [11, 12, 13, 14])
    
    # Modificateurs saisonniers
    seasonal_modifiers: Dict[str, float] = field(default_factory=lambda: {
        "rut": 1.5,           # 50% plus de mouvement
        "pre_rut": 1.25,
        "post_rut": 0.9,
        "winter": 0.6,        # Mouvement réduit
        "summer": 0.85,       # Chaleur = moins actif en journée
        "hyperphagia": 1.3    # Alimentation intensive (ours)
    })
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-MOBILITY-V1"])
    version: str = "1.0.0"


@dataclass
class MobilityState:
    """
    État de mobilité calculé pour un instant donné.
    
    Résultat de l'évaluation de la mobilité avec tous les facteurs.
    """
    
    state_id: str
    timestamp: datetime
    
    # Paramètres calculés
    current_speed_kmh: float
    speed_variance: float
    intensity: MovementIntensity
    preferred_direction: MovementDirection
    
    # Contraintes actives
    constraints: List[MobilityConstraint] = field(default_factory=list)
    
    # Modificateur global
    mobility_modifier: float = 1.0
    
    # Scores
    mobility_score: float = 50.0          # Score de mobilité (0-100)
    predictability_score: float = 50.0    # Prévisibilité du mouvement
    interception_score: float = 50.0      # Probabilité d'interception
    
    # Facteurs d'influence (NIVEAUx 1-4 intégrés)
    digestive_factor: float = 1.0
    thermal_factor: float = 1.0
    human_pressure_factor: float = 1.0
    seasonal_factor: float = 1.0
    corridor_factor: float = 1.0
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-MOBILITY-STATE"])
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour l'API."""
        return {
            "state_id": self.state_id,
            "timestamp": self.timestamp.isoformat(),
            "current_speed_kmh": round(self.current_speed_kmh, 2),
            "speed_variance": round(self.speed_variance, 3),
            "intensity": self.intensity.value,
            "preferred_direction": self.preferred_direction.value,
            "mobility_modifier": round(self.mobility_modifier, 3),
            "scores": {
                "mobility": round(self.mobility_score, 1),
                "predictability": round(self.predictability_score, 1),
                "interception": round(self.interception_score, 1)
            },
            "factors": {
                "digestive": round(self.digestive_factor, 3),
                "thermal": round(self.thermal_factor, 3),
                "human_pressure": round(self.human_pressure_factor, 3),
                "seasonal": round(self.seasonal_factor, 3),
                "corridor": round(self.corridor_factor, 3)
            },
            "constraints": [
                {
                    "type": c.constraint_type,
                    "level": round(c.constraint_level, 2),
                    "active": c.active
                }
                for c in self.constraints
            ],
            "source_ids": self.source_ids,
            "version": self.version
        }


@dataclass
class MobilityPrediction:
    """
    Prédiction de mobilité pour une fenêtre temporelle.
    """
    
    prediction_id: str
    waypoint_lat: float
    waypoint_lng: float
    species: str
    
    # Fenêtre de prédiction
    prediction_start: datetime
    prediction_end: datetime
    
    # États prédits
    current_state: MobilityState
    
    # Probabilités de direction
    direction_probabilities: Dict[str, float] = field(default_factory=dict)
    
    # Zone de mouvement probable (rayon en km)
    probable_radius_km: float = 1.0
    max_radius_km: float = 3.0
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=lambda: ["SRC-MOBILITY-PRED"])
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour l'API."""
        return {
            "prediction_id": self.prediction_id,
            "location": {"lat": self.waypoint_lat, "lng": self.waypoint_lng},
            "species": self.species,
            "window": {
                "start": self.prediction_start.isoformat(),
                "end": self.prediction_end.isoformat()
            },
            "current_state": self.current_state.to_dict(),
            "direction_probabilities": {k: round(v, 2) for k, v in self.direction_probabilities.items()},
            "zones": {
                "probable_radius_km": round(self.probable_radius_km, 2),
                "max_radius_km": round(self.max_radius_km, 2)
            },
            "source_ids": self.source_ids,
            "version": self.version
        }


# =============================================================================
# MOBILITY REGISTRY
# =============================================================================

class MobilityRegistry:
    """
    Registre centralisé de calcul de la mobilité dynamique.
    
    NIVEAU 5 - Knowledge Layer:
    - Calcul dynamique basé sur le contexte
    - Intégration des facteurs NIVEAUx 1-4
    - Versionnement et traçabilité
    """
    
    def __init__(self):
        self._version = "1.0.0"
        self._state_counter = 0
        
        # Paramètres par espèce
        self._species_params: Dict[str, MobilityParameters] = {
            "moose": MobilityParameters(
                species="moose",
                average_speed_kmh=2.5,
                max_speed_kmh=55.0,
                cruise_speed_kmh=4.0,
                speed_variance=0.35,
                daily_distance_km=8.0,
                peak_activity_hours=[5, 6, 7, 17, 18, 19, 20],
                rest_hours=[11, 12, 13, 14],
                source_ids=["SRC-MOBILITY-MOOSE-V1", "SRC-LAVAL-001"]
            ),
            "deer": MobilityParameters(
                species="deer",
                average_speed_kmh=3.0,
                max_speed_kmh=50.0,
                cruise_speed_kmh=4.5,
                speed_variance=0.4,
                daily_distance_km=6.0,
                peak_activity_hours=[5, 6, 7, 16, 17, 18, 19],
                rest_hours=[10, 11, 12, 13, 14],
                source_ids=["SRC-MOBILITY-DEER-V1", "SRC-MFFP-001"]
            ),
            "bear": MobilityParameters(
                species="bear",
                average_speed_kmh=2.0,
                max_speed_kmh=48.0,
                cruise_speed_kmh=3.0,
                speed_variance=0.5,
                daily_distance_km=10.0,
                peak_activity_hours=[5, 6, 7, 8, 17, 18, 19, 20],
                rest_hours=[12, 13, 14],
                seasonal_modifiers={
                    "rut": 1.2,
                    "hyperphagia": 1.6,  # Très actif avant hibernation
                    "winter": 0.0,       # Hibernation
                    "spring": 1.3,       # Sortie hibernation = faim
                    "summer": 0.9
                },
                source_ids=["SRC-MOBILITY-BEAR-V1"]
            )
        }
        
        logger.info(f"MobilityRegistry initialized: {len(self._species_params)} species")
    
    def _generate_state_id(self) -> str:
        """Génère un ID unique pour un état de mobilité."""
        self._state_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
        return f"MOB-{timestamp}-{self._state_counter:04d}"
    
    def _get_species_key(self, species: str) -> str:
        """Convertit le nom d'espèce en clé normalisée."""
        species_lower = species.lower()
        if "orignal" in species_lower or "moose" in species_lower:
            return "moose"
        elif "cerf" in species_lower or "deer" in species_lower:
            return "deer"
        elif "ours" in species_lower or "bear" in species_lower:
            return "bear"
        return "deer"  # Default
    
    def _get_intensity_from_speed(
        self,
        current_speed: float,
        params: MobilityParameters
    ) -> MovementIntensity:
        """Détermine l'intensité de mouvement à partir de la vitesse."""
        ratio = current_speed / params.max_speed_kmh
        
        if ratio < 0.05:
            return MovementIntensity.STATIONARY
        elif ratio < 0.15:
            return MovementIntensity.LOW
        elif ratio < 0.3:
            return MovementIntensity.MODERATE
        elif ratio < 0.6:
            return MovementIntensity.HIGH
        else:
            return MovementIntensity.EXTREME
    
    def _get_preferred_direction(
        self,
        thermal_active: bool,
        human_pressure_active: bool,
        season: str,
        hour: int
    ) -> MovementDirection:
        """Détermine la direction préférentielle de mouvement."""
        
        # Priorité 1: Fuir la pression humaine
        if human_pressure_active:
            return MovementDirection.AWAY_FROM_PRESSURE
        
        # Priorité 2: Chercher un refuge thermique
        if thermal_active:
            return MovementDirection.TOWARDS_REFUGE
        
        # Priorité 3: Direction basée sur l'heure et la saison
        if hour in [5, 6, 7]:
            # Matin: vers les zones d'alimentation
            return MovementDirection.EAST if season in ["rut", "pre_rut"] else MovementDirection.RANDOM
        elif hour in [17, 18, 19]:
            # Soir: vers les zones de repos
            return MovementDirection.WEST
        
        return MovementDirection.RANDOM
    
    def calculate_mobility_state(
        self,
        species: str,
        check_datetime: datetime,
        # Facteurs NIVEAU 1-4
        digestive_phase: str = "unknown",
        digestive_mobility: float = 0.5,
        thermal_stress_active: bool = False,
        thermal_stress_modifier: float = 1.0,
        human_pressure_active: bool = False,
        human_pressure_modifier: float = 1.0,
        seasonal_modifier: float = 1.0,
        current_season: str = "default",
        # Corridors NIVEAU 4
        in_corridor: bool = False,
        corridor_type: str = "primary"
    ) -> MobilityState:
        """
        NIVEAU 5 BIONIC V5 — Calcul de l'état de mobilité dynamique.
        
        Calcule l'état de mobilité en intégrant tous les facteurs des NIVEAUx 1-4.
        
        Args:
            species: Espèce cible
            check_datetime: Date/heure de l'évaluation
            digestive_phase: Phase digestive courante (NIVEAU 2)
            digestive_mobility: Niveau de mobilité digestive (0-1)
            thermal_stress_active: Stress thermique actif (NIVEAU 1)
            thermal_stress_modifier: Modificateur de stress thermique
            human_pressure_active: Pression humaine active (NIVEAU 3)
            human_pressure_modifier: Modificateur de pression humaine
            seasonal_modifier: Modificateur saisonnier (NIVEAU 1)
            current_season: Saison courante
            in_corridor: Est dans un corridor (NIVEAU 4)
            corridor_type: Type de corridor si applicable
            
        Returns:
            MobilityState: État complet de mobilité
        """
        state_id = self._generate_state_id()
        species_key = self._get_species_key(species)
        params = self._species_params.get(species_key, self._species_params["deer"])
        hour = check_datetime.hour
        
        constraints = []
        source_ids = params.source_ids.copy()
        
        # =================================================================
        # 1. FACTEUR DE BASE: Heure de la journée
        # =================================================================
        
        is_peak_activity = hour in params.peak_activity_hours
        is_rest_hour = hour in params.rest_hours
        
        if is_peak_activity:
            hourly_factor = 1.2
        elif is_rest_hour:
            hourly_factor = 0.5
        else:
            hourly_factor = 0.8
        
        # =================================================================
        # 2. CONTRAINTE DIGESTIVE (NIVEAU 2)
        # =================================================================
        
        digestive_factor = 0.5 + (digestive_mobility * 0.5)  # Range: 0.5-1.0
        
        if digestive_phase in ["rumination", "rest"]:
            digestive_constraint = MobilityConstraint(
                constraint_type="digestive",
                constraint_level=0.7 if digestive_phase == "rest" else 0.4,
                effect_on_speed=-0.3 if digestive_phase == "rest" else -0.15,
                effect_on_direction=0.0,
                active=True,
                description=f"Phase digestive: {digestive_phase}",
                source_ids=["SRC-DIGESTIVE", "SRC-BEHAVIOR-V2"]
            )
            constraints.append(digestive_constraint)
            source_ids.append("SRC-DIGESTIVE")
        elif digestive_phase in ["feeding", "water_search"]:
            digestive_factor *= 1.15  # Plus actif en alimentation
            source_ids.append("SRC-DIGESTIVE")
        
        # =================================================================
        # 3. CONTRAINTE THERMIQUE (NIVEAU 1)
        # =================================================================
        
        thermal_factor = thermal_stress_modifier
        
        if thermal_stress_active:
            # Stress thermique réduit la mobilité
            thermal_level = 1.0 - thermal_stress_modifier
            thermal_constraint = MobilityConstraint(
                constraint_type="thermal",
                constraint_level=thermal_level,
                effect_on_speed=-0.4 * thermal_level,
                effect_on_direction=0.8,  # Forte orientation vers refuge
                active=True,
                description="Stress thermique actif",
                source_ids=["SRC-THERMAL-STRESS", "SRC-SEASONAL-V2"]
            )
            constraints.append(thermal_constraint)
            source_ids.extend(["SRC-THERMAL-STRESS", "SRC-SEASONAL-V2"])
        
        # =================================================================
        # 4. CONTRAINTE PRESSION HUMAINE (NIVEAU 3)
        # =================================================================
        
        human_factor = human_pressure_modifier
        
        if human_pressure_active:
            # Pression humaine = mouvement d'évitement
            pressure_level = 1.0 - human_pressure_modifier
            human_constraint = MobilityConstraint(
                constraint_type="human_pressure",
                constraint_level=pressure_level,
                effect_on_speed=0.3 * pressure_level,  # Fuite = plus rapide
                effect_on_direction=1.0,  # Orientation maximale d'évitement
                active=True,
                description="Pression humaine détectée",
                source_ids=["SRC-PRES-HUMAN", "SRC-HUNTING-PRESSURE"]
            )
            constraints.append(human_constraint)
            source_ids.extend(["SRC-PRES-HUMAN", "SRC-HUNTING-PRESSURE"])
        
        # =================================================================
        # 5. MODIFICATEUR SAISONNIER (NIVEAU 1)
        # =================================================================
        
        season_key = current_season.lower()
        seasonal_factor = params.seasonal_modifiers.get(season_key, seasonal_modifier)
        source_ids.append("SRC-SEASONAL-V2")
        
        # =================================================================
        # 6. FACTEUR CORRIDOR (NIVEAU 4)
        # =================================================================
        
        corridor_factor = 1.0
        if in_corridor:
            corridor_factors = {
                "primary": 1.3,       # Corridors principaux = plus de mouvement
                "secondary": 1.15,
                "seasonal": 1.25,
                "thermal": 1.1,
                "risk": 0.7           # Corridors à risque = évitement
            }
            corridor_factor = corridor_factors.get(corridor_type, 1.0)
            
            corridor_constraint = MobilityConstraint(
                constraint_type="corridor",
                constraint_level=0.5,
                effect_on_speed=(corridor_factor - 1.0),
                effect_on_direction=0.3,
                active=True,
                description=f"Dans corridor {corridor_type}",
                source_ids=["SRC-CORRIDOR-V1", "SRC-NIVEAU4"]
            )
            constraints.append(corridor_constraint)
            source_ids.extend(["SRC-CORRIDOR-V1", "SRC-NIVEAU4"])
        
        # =================================================================
        # 7. CALCUL DE LA VITESSE ACTUELLE
        # =================================================================
        
        # Vitesse de base
        base_speed = params.average_speed_kmh * hourly_factor
        
        # Appliquer les facteurs
        combined_factor = (
            digestive_factor *
            thermal_factor *
            human_factor *
            seasonal_factor *
            corridor_factor
        )
        
        current_speed = base_speed * combined_factor
        
        # Appliquer les contraintes
        for constraint in constraints:
            current_speed *= constraint.get_combined_effect()
        
        # Limiter à la vitesse max (sauf fuite)
        if human_pressure_active:
            current_speed = min(current_speed * 1.5, params.max_speed_kmh * 0.5)
        else:
            current_speed = min(current_speed, params.cruise_speed_kmh * 1.5)
        
        current_speed = max(0.1, current_speed)  # Minimum 0.1 km/h
        
        # =================================================================
        # 8. CALCUL DES SCORES
        # =================================================================
        
        # Score de mobilité (vitesse relative)
        mobility_score = (current_speed / params.cruise_speed_kmh) * 50 + 25
        mobility_score = max(0, min(100, mobility_score))
        
        # Score de prévisibilité (moins de contraintes = plus prévisible)
        active_constraints = sum(1 for c in constraints if c.active)
        predictability_score = 80 - (active_constraints * 10) + (15 if is_peak_activity else 0)
        predictability_score = max(0, min(100, predictability_score))
        
        # Score d'interception (fonction de la prévisibilité et vitesse)
        if human_pressure_active:
            interception_score = 30  # Fuite = difficile à intercepter
        elif is_rest_hour:
            interception_score = 75  # Repos = plus facile
        else:
            interception_score = predictability_score * 0.6 + (100 - mobility_score) * 0.4
        interception_score = max(0, min(100, interception_score))
        
        # =================================================================
        # 9. MODIFICATEUR GLOBAL DE MOBILITÉ
        # =================================================================
        
        # Moyenne pondérée des facteurs
        mobility_modifier = (
            digestive_factor * 0.2 +
            thermal_factor * 0.2 +
            human_factor * 0.2 +
            seasonal_factor * 0.25 +
            corridor_factor * 0.15
        )
        
        # =================================================================
        # 10. CRÉATION DE L'ÉTAT
        # =================================================================
        
        intensity = self._get_intensity_from_speed(current_speed, params)
        direction = self._get_preferred_direction(
            thermal_stress_active,
            human_pressure_active,
            current_season,
            hour
        )
        
        # Variance ajustée
        variance = params.speed_variance
        if human_pressure_active:
            variance *= 1.5  # Plus erratique sous pression
        elif is_rest_hour:
            variance *= 0.5  # Moins variable au repos
        
        state = MobilityState(
            state_id=state_id,
            timestamp=check_datetime,
            current_speed_kmh=current_speed,
            speed_variance=variance,
            intensity=intensity,
            preferred_direction=direction,
            constraints=constraints,
            mobility_modifier=mobility_modifier,
            mobility_score=mobility_score,
            predictability_score=predictability_score,
            interception_score=interception_score,
            digestive_factor=digestive_factor,
            thermal_factor=thermal_factor,
            human_pressure_factor=human_factor,
            seasonal_factor=seasonal_factor,
            corridor_factor=corridor_factor,
            source_ids=list(set(source_ids)),
            version=self._version
        )
        
        logger.info(
            f"MobilityState calculated: {state_id}, "
            f"species={species_key}, speed={current_speed:.2f}km/h, "
            f"intensity={intensity.value}, modifier={mobility_modifier:.3f}"
        )
        
        return state
    
    def get_mobility_modifier(
        self,
        species: str,
        check_datetime: datetime,
        digestive_phase: str = "unknown",
        digestive_mobility: float = 0.5,
        thermal_stress_active: bool = False,
        thermal_stress_modifier: float = 1.0,
        human_pressure_active: bool = False,
        human_pressure_modifier: float = 1.0,
        seasonal_modifier: float = 1.0,
        current_season: str = "default",
        in_corridor: bool = False,
        corridor_type: str = "primary"
    ) -> Tuple[float, Dict[str, Any], List[str]]:
        """
        NIVEAU 5 BIONIC V5 — Obtenir le modificateur de mobilité.
        
        Interface simplifiée pour UnifiedScoringService.
        
        Returns:
            Tuple[modifier, details, source_ids]
        """
        state = self.calculate_mobility_state(
            species=species,
            check_datetime=check_datetime,
            digestive_phase=digestive_phase,
            digestive_mobility=digestive_mobility,
            thermal_stress_active=thermal_stress_active,
            thermal_stress_modifier=thermal_stress_modifier,
            human_pressure_active=human_pressure_active,
            human_pressure_modifier=human_pressure_modifier,
            seasonal_modifier=seasonal_modifier,
            current_season=current_season,
            in_corridor=in_corridor,
            corridor_type=corridor_type
        )
        
        details = state.to_dict()
        
        return state.mobility_modifier, details, state.source_ids
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques du registre."""
        return {
            "version": self._version,
            "supported_species": list(self._species_params.keys()),
            "intensity_levels": [i.value for i in MovementIntensity],
            "direction_types": [d.value for d in MovementDirection],
            "factors_integrated": [
                "NIVEAU 1 - Saisonnalité",
                "NIVEAU 1 - Stress thermique",
                "NIVEAU 2 - Cycles digestifs",
                "NIVEAU 3 - Pression humaine",
                "NIVEAU 4 - Corridors"
            ]
        }


# =============================================================================
# SINGLETON
# =============================================================================

_registry_instance: Optional[MobilityRegistry] = None


def get_mobility_registry() -> MobilityRegistry:
    """Obtenir l'instance singleton du registre de mobilité."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = MobilityRegistry()
    return _registry_instance


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'MovementIntensity',
    'MovementDirection',
    'TerrainDifficulty',
    # Data models
    'MobilityParameters',
    'MobilityConstraint',
    'MobilityState',
    'MobilityPrediction',
    # Registry
    'MobilityRegistry',
    'get_mobility_registry'
]
