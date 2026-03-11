"""
BIONIC ENGINE - Advanced Behavioral Factors
PHASE G - P0-BETA2 IMPLEMENTATION
Version: 1.0.0-beta2

12 Facteurs Comportementaux Avances pour BIONIC V5 ULTIME x2

Conformite: G-SEC | G-QA | G-DOC
"""

from typing import Dict, List
from enum import Enum


# =============================================================================
# ENUMS - 12 Facteurs Comportementaux
# =============================================================================

class PredatorType(str, Enum):
    """Types de predateurs"""
    WOLF = "wolf"
    BEAR = "bear"
    COYOTE = "coyote"
    COUGAR = "cougar"
    HUMAN = "human"


class StressType(str, Enum):
    """Types de stress physiologique"""
    THERMAL = "thermal"
    HYDRIC = "hydric"
    SOCIAL = "social"
    NUTRITIONAL = "nutritional"


class HormonalPhase(str, Enum):
    """Phases hormonales"""
    PRE_RUT = "pre_rut"
    RUT_PEAK = "rut_peak"
    POST_RUT = "post_rut"
    LACTATION = "lactation"
    ANTLER_GROWTH = "antler_growth"
    ANTLER_VELVET = "antler_velvet"
    ANTLER_HARD = "antler_hard"
    ANTLER_SHED = "antler_shed"
    NEUTRAL = "neutral"


class DigestivePhase(str, Enum):
    """Phases digestives"""
    ACTIVE_FEEDING = "active_feeding"
    DIGESTING = "digesting"
    TRANSITIONING = "transitioning"
    RESTING = "resting"


class SnowCondition(str, Enum):
    """Conditions de neige"""
    NONE = "none"
    LIGHT = "light"
    MODERATE = "moderate"
    DEEP = "deep"
    CRUSTED = "crusted"
    ICY = "icy"


# =============================================================================
# FACTOR 1: PREDATION
# =============================================================================

class PredatorRiskModel:
    """
    Modele de risque de predation.
    
    Impact: Modifie les patterns de deplacement et les zones de repos.
    """
    
    # Risque de base par predateur et espece proie
    PREDATOR_RISK_MATRIX = {
        "moose": {
            PredatorType.WOLF: 0.7,
            PredatorType.BEAR: 0.4,  # Surtout jeunes
            PredatorType.COUGAR: 0.2,
            PredatorType.HUMAN: 0.8
        },
        "deer": {
            PredatorType.WOLF: 0.6,
            PredatorType.COYOTE: 0.5,
            PredatorType.COUGAR: 0.7,
            PredatorType.HUMAN: 0.9
        },
        "elk": {
            PredatorType.WOLF: 0.8,
            PredatorType.COUGAR: 0.5,
            PredatorType.HUMAN: 0.7
        }
    }
    
    # Corridors de predateurs par region (lat ranges)
    PREDATOR_CORRIDORS = {
        "north_quebec": {"lat_min": 50, "lat_max": 62, "wolf_density": 0.8, "bear_density": 0.6},
        "central_quebec": {"lat_min": 47, "lat_max": 50, "wolf_density": 0.5, "bear_density": 0.7},
        "south_quebec": {"lat_min": 45, "lat_max": 47, "wolf_density": 0.2, "bear_density": 0.4}
    }
    
    @classmethod
    def calculate_predation_risk(
        cls,
        species: str,
        latitude: float,
        hour: int,
        month: int
    ) -> Dict:
        """
        Calcule le risque de predation.
        
        Returns:
            Dict avec risk_score (0-100), dominant_predator, behavioral_impact
        """
        # Determiner la region
        if latitude >= 50:
            region = "north_quebec"
        elif latitude >= 47:
            region = "central_quebec"
        else:
            region = "south_quebec"
        
        corridor = cls.PREDATOR_CORRIDORS[region]
        species_risks = cls.PREDATOR_RISK_MATRIX.get(species, {})
        
        # Risque de base
        wolf_risk = species_risks.get(PredatorType.WOLF, 0) * corridor["wolf_density"]
        bear_risk = species_risks.get(PredatorType.BEAR, 0) * corridor["bear_density"]
        
        # Ajustement saisonnier (ours hibernent)
        if month in [12, 1, 2, 3]:
            bear_risk = 0
        
        # Ajustement horaire (loups plus actifs aube/crepuscule)
        if 5 <= hour <= 8 or 17 <= hour <= 20:
            wolf_risk *= 1.3
        elif 0 <= hour <= 4:
            wolf_risk *= 1.5  # Chasse nocturne
        
        # Risque total
        total_risk = min(100, (wolf_risk + bear_risk) * 50)
        
        # Predateur dominant
        dominant = PredatorType.WOLF if wolf_risk > bear_risk else PredatorType.BEAR
        
        return {
            "risk_score": round(total_risk, 1),
            "dominant_predator": dominant.value,
            "wolf_risk": round(wolf_risk * 100, 1),
            "bear_risk": round(bear_risk * 100, 1),
            "behavioral_impact": "increased_vigilance" if total_risk > 50 else "normal"
        }


# =============================================================================
# FACTOR 2: STRESS PHYSIOLOGIQUE
# =============================================================================

class StressModel:
    """
    Modele de stress physiologique.
    
    3 types: Thermal, Hydric, Social
    """
    
    # Seuils de stress thermique par espece
    THERMAL_THRESHOLDS = {
        "moose": {"cold_stress": -25, "heat_stress": 14, "critical_heat": 20},
        "deer": {"cold_stress": -20, "heat_stress": 25, "critical_heat": 30},
        "bear": {"cold_stress": -30, "heat_stress": 30, "critical_heat": 35},
        "elk": {"cold_stress": -25, "heat_stress": 20, "critical_heat": 25}
    }
    
    @classmethod
    def calculate_thermal_stress(cls, species: str, temperature: float) -> Dict:
        """Calcule le stress thermique."""
        thresholds = cls.THERMAL_THRESHOLDS.get(species, cls.THERMAL_THRESHOLDS["deer"])
        
        if temperature < thresholds["cold_stress"]:
            stress_level = min(100, abs(temperature - thresholds["cold_stress"]) * 5)
            stress_type = "cold"
        elif temperature > thresholds["critical_heat"]:
            stress_level = min(100, (temperature - thresholds["critical_heat"]) * 10)
            stress_type = "critical_heat"
        elif temperature > thresholds["heat_stress"]:
            stress_level = min(50, (temperature - thresholds["heat_stress"]) * 5)
            stress_type = "heat"
        else:
            stress_level = 0
            stress_type = "none"
        
        return {
            "stress_score": round(stress_level, 1),
            "stress_type": stress_type,
            "behavioral_response": cls._get_thermal_response(stress_type, stress_level)
        }
    
    @classmethod
    def calculate_hydric_stress(cls, species: str, water_distance_m: float, temperature: float) -> Dict:
        """Calcule le stress hydrique."""
        # Besoin d'eau augmente avec la chaleur
        base_threshold = 500  # metres
        if temperature > 20:
            threshold = base_threshold * 0.5  # Besoin plus proche
        else:
            threshold = base_threshold
        
        if water_distance_m > threshold * 3:
            stress_level = 80
        elif water_distance_m > threshold * 2:
            stress_level = 50
        elif water_distance_m > threshold:
            stress_level = 25
        else:
            stress_level = 0
        
        return {
            "stress_score": round(stress_level, 1),
            "water_seeking": stress_level > 40,
            "movement_toward_water": stress_level > 60
        }
    
    @classmethod
    def calculate_social_stress(cls, species: str, month: int, group_size: int) -> Dict:
        """Calcule le stress social."""
        # Stress social varie selon saison
        if species in ["moose", "deer", "elk"]:
            # Rut = stress social eleve pour males
            if month in [9, 10, 11]:
                base_stress = 40
            else:
                base_stress = 10
        else:
            base_stress = 5
        
        # Ajustement taille groupe
        if group_size > 10:
            base_stress += 20
        elif group_size > 5:
            base_stress += 10
        
        return {
            "stress_score": min(100, base_stress),
            "dominance_seeking": month in [9, 10, 11],
            "territorial_behavior": base_stress > 30
        }
    
    @staticmethod
    def _get_thermal_response(stress_type: str, level: float) -> str:
        if stress_type == "critical_heat":
            return "seeking_water_shade"
        elif stress_type == "heat":
            return "reduced_activity"
        elif stress_type == "cold":
            return "seeking_shelter" if level > 50 else "increased_feeding"
        return "normal"


# =============================================================================
# FACTOR 3: HIERARCHIE SOCIALE
# =============================================================================

class SocialHierarchyModel:
    """
    Modele de hierarchie sociale.
    
    DominanceScore, GroupBehavior
    """
    
    @classmethod
    def calculate_dominance_context(cls, species: str, month: int, is_male: bool = True) -> Dict:
        """Calcule le contexte de dominance."""
        # Dominance plus importante pendant le rut
        if species in ["moose", "deer", "elk"]:
            if month in [9, 10, 11] and is_male:
                dominance_importance = 90
                behavior = "territorial_display"
            elif month in [9, 10, 11]:
                dominance_importance = 60
                behavior = "mate_selection"
            else:
                dominance_importance = 30
                behavior = "normal_hierarchy"
        else:
            dominance_importance = 20
            behavior = "flock_dynamics"
        
        return {
            "dominance_score": dominance_importance,
            "group_behavior": behavior,
            "aggression_level": "high" if dominance_importance > 70 else "moderate" if dominance_importance > 40 else "low",
            "movement_pattern": "expanded_range" if dominance_importance > 70 else "normal_range"
        }


# =============================================================================
# FACTOR 4: COMPETITION INTER-ESPECES
# =============================================================================

class InterspeciesCompetitionModel:
    """
    Modele de competition inter-especes.
    """
    
    COMPETITION_MATRIX = {
        ("moose", "deer"): {"competition_level": 30, "resource": "browse"},
        ("moose", "elk"): {"competition_level": 50, "resource": "habitat"},
        ("deer", "elk"): {"competition_level": 60, "resource": "browse_habitat"},
        ("bear", "moose"): {"competition_level": 20, "resource": "territory"},
    }
    
    @classmethod
    def calculate_competition(cls, primary_species: str, region_species: List[str]) -> Dict:
        """Calcule la competition avec les autres especes presentes."""
        total_competition = 0
        competitors = []
        
        for other in region_species:
            if other != primary_species:
                key = tuple(sorted([primary_species, other]))
                if key in cls.COMPETITION_MATRIX:
                    comp = cls.COMPETITION_MATRIX[key]
                    total_competition += comp["competition_level"]
                    competitors.append({
                        "species": other,
                        "level": comp["competition_level"],
                        "resource": comp["resource"]
                    })
        
        return {
            "total_competition_score": min(100, total_competition),
            "competitors": competitors,
            "behavioral_impact": "displacement" if total_competition > 70 else "coexistence"
        }


# =============================================================================
# FACTOR 5: SIGNAUX FAIBLES
# =============================================================================

class WeakSignalsModel:
    """
    Detection de signaux faibles et anomalies.
    """
    
    @classmethod
    def detect_anomalies(
        cls,
        current_score: float,
        historical_avg: float,
        weather_rapid_change: bool,
        unusual_activity: bool
    ) -> Dict:
        """Detecte les signaux faibles."""
        anomalies = []
        anomaly_score = 0
        
        # Ecart significatif avec historique
        if abs(current_score - historical_avg) > 20:
            anomalies.append("significant_deviation_from_baseline")
            anomaly_score += 30
        
        # Changement meteo rapide
        if weather_rapid_change:
            anomalies.append("rapid_weather_change")
            anomaly_score += 25
        
        # Activite inhabituelle
        if unusual_activity:
            anomalies.append("unusual_activity_pattern")
            anomaly_score += 35
        
        return {
            "anomaly_score": min(100, anomaly_score),
            "anomalies_detected": anomalies,
            "confidence_adjustment": -0.1 if anomaly_score > 50 else 0,
            "recommendation": "increased_observation" if anomaly_score > 30 else "normal"
        }


# =============================================================================
# FACTOR 6: CYCLES HORMONAUX
# =============================================================================

class HormonalCycleModel:
    """
    Modele des cycles hormonaux.
    
    Rut, lactation, croissance des bois
    """
    
    HORMONAL_CALENDAR = {
        "moose": {
            1: HormonalPhase.ANTLER_SHED,
            2: HormonalPhase.NEUTRAL,
            3: HormonalPhase.ANTLER_GROWTH,
            4: HormonalPhase.ANTLER_GROWTH,
            5: HormonalPhase.ANTLER_VELVET,
            6: HormonalPhase.LACTATION,  # Femelles
            7: HormonalPhase.ANTLER_VELVET,
            8: HormonalPhase.ANTLER_HARD,
            9: HormonalPhase.PRE_RUT,
            10: HormonalPhase.RUT_PEAK,
            11: HormonalPhase.POST_RUT,
            12: HormonalPhase.ANTLER_SHED
        },
        "deer": {
            1: HormonalPhase.ANTLER_SHED,
            2: HormonalPhase.NEUTRAL,
            3: HormonalPhase.ANTLER_GROWTH,
            4: HormonalPhase.ANTLER_GROWTH,
            5: HormonalPhase.ANTLER_VELVET,
            6: HormonalPhase.LACTATION,
            7: HormonalPhase.ANTLER_VELVET,
            8: HormonalPhase.ANTLER_HARD,
            9: HormonalPhase.ANTLER_HARD,
            10: HormonalPhase.PRE_RUT,
            11: HormonalPhase.RUT_PEAK,
            12: HormonalPhase.POST_RUT
        }
    }
    
    @classmethod
    def get_hormonal_phase(cls, species: str, month: int) -> Dict:
        """Retourne la phase hormonale."""
        calendar = cls.HORMONAL_CALENDAR.get(species, {})
        phase = calendar.get(month, HormonalPhase.NEUTRAL)
        
        # Impact sur comportement
        activity_modifier = 1.0
        aggression = "low"
        
        if phase == HormonalPhase.RUT_PEAK:
            activity_modifier = 1.5
            aggression = "high"
        elif phase == HormonalPhase.PRE_RUT:
            activity_modifier = 1.3
            aggression = "moderate"
        elif phase == HormonalPhase.POST_RUT:
            activity_modifier = 0.7
            aggression = "low"
        elif phase == HormonalPhase.LACTATION:
            activity_modifier = 0.9
            aggression = "protective"
        
        return {
            "phase": phase.value,
            "activity_modifier": activity_modifier,
            "aggression_level": aggression,
            "behavioral_focus": cls._get_behavioral_focus(phase)
        }
    
    @staticmethod
    def _get_behavioral_focus(phase: HormonalPhase) -> str:
        focuses = {
            HormonalPhase.RUT_PEAK: "breeding",
            HormonalPhase.PRE_RUT: "territorial_marking",
            HormonalPhase.POST_RUT: "recovery_feeding",
            HormonalPhase.LACTATION: "nurturing",
            HormonalPhase.ANTLER_GROWTH: "mineral_seeking",
            HormonalPhase.ANTLER_VELVET: "careful_movement",
            HormonalPhase.ANTLER_HARD: "sparring"
        }
        return focuses.get(phase, "normal")


# =============================================================================
# FACTOR 7: CYCLES DIGESTIFS
# =============================================================================

class DigestiveCycleModel:
    """
    Modele des cycles digestifs.
    
    Transitions feeding -> bedding
    """
    
    # Duree typique des phases digestives (heures)
    DIGESTIVE_CYCLES = {
        "moose": {"feeding": 2.5, "digesting": 4, "transitioning": 0.5},
        "deer": {"feeding": 2, "digesting": 3, "transitioning": 0.5},
        "elk": {"feeding": 2.5, "digesting": 3.5, "transitioning": 0.5}
    }
    
    @classmethod
    def get_digestive_phase(cls, species: str, hour: int, last_feeding_hour: int = None) -> Dict:
        """Determine la phase digestive."""
        cycles = cls.DIGESTIVE_CYCLES.get(species, cls.DIGESTIVE_CYCLES["deer"])
        
        # Si derniere alimentation inconnue, estimer selon l'heure
        if last_feeding_hour is None:
            # Pics d'alimentation typiques: 6-8h et 17-19h
            if 6 <= hour <= 8:
                phase = DigestivePhase.ACTIVE_FEEDING
                hours_since_feeding = 0
            elif 9 <= hour <= 12:
                phase = DigestivePhase.DIGESTING
                hours_since_feeding = hour - 8
            elif 13 <= hour <= 16:
                phase = DigestivePhase.TRANSITIONING
                hours_since_feeding = hour - 8
            elif 17 <= hour <= 19:
                phase = DigestivePhase.ACTIVE_FEEDING
                hours_since_feeding = 0
            else:
                phase = DigestivePhase.RESTING
                hours_since_feeding = (hour - 19) % 24
        else:
            hours_since_feeding = (hour - last_feeding_hour) % 24
            if hours_since_feeding < cycles["feeding"]:
                phase = DigestivePhase.ACTIVE_FEEDING
            elif hours_since_feeding < cycles["feeding"] + cycles["digesting"]:
                phase = DigestivePhase.DIGESTING
            elif hours_since_feeding < cycles["feeding"] + cycles["digesting"] + cycles["transitioning"]:
                phase = DigestivePhase.TRANSITIONING
            else:
                phase = DigestivePhase.RESTING
        
        return {
            "phase": phase.value,
            "hours_since_feeding": hours_since_feeding,
            "movement_likelihood": cls._get_movement_likelihood(phase),
            "feeding_probability": 0.9 if phase == DigestivePhase.ACTIVE_FEEDING else 0.1
        }
    
    @staticmethod
    def _get_movement_likelihood(phase: DigestivePhase) -> float:
        likelihoods = {
            DigestivePhase.ACTIVE_FEEDING: 0.6,
            DigestivePhase.DIGESTING: 0.2,
            DigestivePhase.TRANSITIONING: 0.8,
            DigestivePhase.RESTING: 0.1
        }
        return likelihoods.get(phase, 0.3)


# =============================================================================
# FACTOR 8: MEMOIRE TERRITORIALE
# =============================================================================

class TerritorialMemoryModel:
    """
    Modele de memoire territoriale.
    
    AvoidanceMemory, PreferredRoutes
    """
    
    # Duree de la memoire d'evitement (jours)
    AVOIDANCE_MEMORY_DURATION = {
        "moose": 14,  # 2 semaines
        "deer": 10,
        "elk": 12,
        "bear": 21  # 3 semaines
    }
    
    @classmethod
    def calculate_avoidance_factor(
        cls,
        species: str,
        days_since_disturbance: int,
        disturbance_intensity: float
    ) -> Dict:
        """Calcule le facteur d'evitement base sur la memoire."""
        memory_duration = cls.AVOIDANCE_MEMORY_DURATION.get(species, 10)
        
        if days_since_disturbance >= memory_duration:
            avoidance_score = 0
            memory_active = False
        else:
            # Decroissance exponentielle de la memoire
            decay_factor = days_since_disturbance / memory_duration
            avoidance_score = disturbance_intensity * (1 - decay_factor) * 100
            memory_active = True
        
        return {
            "avoidance_score": round(avoidance_score, 1),
            "memory_active": memory_active,
            "days_until_return": max(0, memory_duration - days_since_disturbance),
            "preferred_route_shift": avoidance_score > 50
        }
    
    @classmethod
    def get_route_preference(cls, species: str, is_familiar_area: bool) -> Dict:
        """Determine la preference de route."""
        if is_familiar_area:
            return {
                "route_preference": "established",
                "exploration_likelihood": 0.2,
                "movement_efficiency": 1.2  # Plus efficace en terrain connu
            }
        else:
            return {
                "route_preference": "exploratory",
                "exploration_likelihood": 0.6,
                "movement_efficiency": 0.8  # Moins efficace
            }


# =============================================================================
# FACTOR 9: APPRENTISSAGE COMPORTEMENTAL
# =============================================================================

class AdaptiveBehaviorModel:
    """
    Modele d'apprentissage comportemental.
    
    AdaptiveBehavior - Comment les animaux s'adaptent
    """
    
    @classmethod
    def calculate_adaptation(
        cls,
        species: str,
        hunting_pressure_history: List[float],  # Derniers 30 jours
        success_rate_hunters: float  # 0-1
    ) -> Dict:
        """Calcule le niveau d'adaptation comportementale."""
        if not hunting_pressure_history:
            return {
                "adaptation_level": 0,
                "behavioral_shift": "none",
                "nocturnal_shift": 0
            }
        
        # Moyenne de pression recente
        avg_pressure = sum(hunting_pressure_history) / len(hunting_pressure_history)
        
        # Plus la pression est haute, plus l'adaptation
        adaptation_level = min(100, avg_pressure * 1.5)
        
        # Si taux de succes des chasseurs est haut, adaptation plus forte
        if success_rate_hunters > 0.3:
            adaptation_level *= 1.2
        
        # Shift nocturne proportionnel a l'adaptation
        nocturnal_shift = min(0.4, adaptation_level / 250)  # Max 40% shift
        
        behavioral_shift = "none"
        if adaptation_level > 70:
            behavioral_shift = "highly_nocturnal"
        elif adaptation_level > 50:
            behavioral_shift = "increased_caution"
        elif adaptation_level > 30:
            behavioral_shift = "modified_patterns"
        
        return {
            "adaptation_level": round(adaptation_level, 1),
            "behavioral_shift": behavioral_shift,
            "nocturnal_shift": round(nocturnal_shift, 2),
            "activity_time_adjustment": -nocturnal_shift  # Reduction activite diurne
        }


# =============================================================================
# FACTOR 10: ACTIVITE HUMAINE NON-CHASSE
# =============================================================================

class HumanDisturbanceModel:
    """
    Modele d'activite humaine non-chasse.
    
    Randonnee, VTT, camping, exploitation forestiere
    """
    
    DISTURBANCE_TYPES = {
        "hiking": {"base_impact": 30, "radius_m": 200, "recovery_hours": 2},
        "atv": {"base_impact": 60, "radius_m": 500, "recovery_hours": 4},
        "logging": {"base_impact": 90, "radius_m": 1000, "recovery_hours": 24},
        "camping": {"base_impact": 50, "radius_m": 300, "recovery_hours": 8},
        "road_traffic": {"base_impact": 40, "radius_m": 150, "recovery_hours": 1}
    }
    
    @classmethod
    def calculate_disturbance(
        cls,
        disturbance_types: List[str],
        is_weekend: bool,
        is_summer: bool
    ) -> Dict:
        """Calcule l'impact du derangement humain non-chasse."""
        total_impact = 0
        affected_radius = 0
        
        for dtype in disturbance_types:
            if dtype in cls.DISTURBANCE_TYPES:
                d = cls.DISTURBANCE_TYPES[dtype]
                total_impact += d["base_impact"]
                affected_radius = max(affected_radius, d["radius_m"])
        
        # Ajustements
        if is_weekend:
            total_impact *= 1.5
        if is_summer:
            total_impact *= 1.3
        
        total_impact = min(100, total_impact)
        
        return {
            "disturbance_score": round(total_impact, 1),
            "affected_radius_m": affected_radius,
            "behavioral_response": "avoidance" if total_impact > 60 else "caution" if total_impact > 30 else "normal",
            "activity_reduction": round(total_impact / 200, 2)  # Max 50% reduction
        }


# =============================================================================
# FACTOR 11: DISPONIBILITE MINERALE
# =============================================================================

class MineralAvailabilityModel:
    """
    Modele de disponibilite minerale.
    
    MineralAvailability, SaltLickAttraction
    """
    
    # Besoin mineral par espece et saison
    MINERAL_NEEDS = {
        "moose": {
            "spring": 0.9,   # Croissance bois
            "summer": 0.7,
            "fall": 0.4,
            "winter": 0.5    # Compensation alimentation pauvre
        },
        "deer": {
            "spring": 0.85,
            "summer": 0.6,
            "fall": 0.3,
            "winter": 0.4
        },
        "elk": {
            "spring": 0.9,
            "summer": 0.7,
            "fall": 0.35,
            "winter": 0.45
        }
    }
    
    @classmethod
    def calculate_mineral_attraction(
        cls,
        species: str,
        month: int,
        salt_lick_distance_m: float
    ) -> Dict:
        """Calcule l'attraction vers les sources minerales."""
        # Determiner la saison
        if month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        elif month in [9, 10, 11]:
            season = "fall"
        else:
            season = "winter"
        
        needs = cls.MINERAL_NEEDS.get(species, {})
        need_level = needs.get(season, 0.5)
        
        # Attraction inversement proportionnelle a la distance
        if salt_lick_distance_m < 100:
            distance_factor = 1.0
        elif salt_lick_distance_m < 500:
            distance_factor = 0.7
        elif salt_lick_distance_m < 1000:
            distance_factor = 0.4
        else:
            distance_factor = 0.1
        
        attraction = need_level * distance_factor * 100
        
        return {
            "mineral_need_score": round(need_level * 100, 1),
            "salt_lick_attraction": round(attraction, 1),
            "seeking_behavior": attraction > 50,
            "optimal_monitoring_time": "early_morning" if need_level > 0.7 else "anytime"
        }


# =============================================================================
# FACTOR 12: CONDITIONS DE NEIGE
# =============================================================================

class SnowConditionModel:
    """
    Modele des conditions de neige.
    
    SnowDepth, CrustRisk, WinterPenalty
    """
    
    # Seuils de profondeur de neige par espece (cm)
    SNOW_THRESHOLDS = {
        "moose": {"comfort": 50, "difficult": 80, "critical": 100},
        "deer": {"comfort": 30, "difficult": 50, "critical": 70},
        "elk": {"comfort": 40, "difficult": 60, "critical": 80}
    }
    
    @classmethod
    def calculate_snow_impact(
        cls,
        species: str,
        snow_depth_cm: float,
        is_crusted: bool,
        temperature: float
    ) -> Dict:
        """Calcule l'impact des conditions de neige."""
        thresholds = cls.SNOW_THRESHOLDS.get(species, cls.SNOW_THRESHOLDS["deer"])
        
        # Determiner la condition
        if snow_depth_cm == 0:
            condition = SnowCondition.NONE
            mobility_penalty = 0
        elif snow_depth_cm < thresholds["comfort"]:
            condition = SnowCondition.LIGHT
            mobility_penalty = 5
        elif snow_depth_cm < thresholds["difficult"]:
            condition = SnowCondition.MODERATE
            mobility_penalty = 20
        elif snow_depth_cm < thresholds["critical"]:
            condition = SnowCondition.DEEP
            mobility_penalty = 40
        else:
            condition = SnowCondition.DEEP
            mobility_penalty = 60
        
        # Croute de glace = danger accru
        crust_risk = 0
        if is_crusted:
            condition = SnowCondition.CRUSTED
            crust_risk = 30
            mobility_penalty += 20
        
        # Glace si temperature fluctue autour de 0
        if -2 < temperature < 2 and snow_depth_cm > 0:
            condition = SnowCondition.ICY
            mobility_penalty += 15
        
        # Penalite hivernale totale
        winter_penalty = min(100, mobility_penalty + crust_risk)
        
        return {
            "snow_condition": condition.value,
            "snow_depth_cm": snow_depth_cm,
            "mobility_penalty": round(mobility_penalty, 1),
            "crust_risk": crust_risk,
            "winter_penalty_score": round(winter_penalty, 1),
            "yarding_likelihood": winter_penalty > 50,
            "energy_expenditure_increase": round(winter_penalty / 100, 2)  # 0-1
        }


# =============================================================================
# INTEGRATED BEHAVIORAL FACTORS
# =============================================================================

class IntegratedBehavioralFactors:
    """
    Integration des 12 facteurs comportementaux.
    
    Calcule un score global et des recommandations.
    """
    
    # Poids des 12 facteurs
    FACTOR_WEIGHTS = {
        "predation": 0.10,
        "thermal_stress": 0.08,
        "hydric_stress": 0.05,
        "social_stress": 0.05,
        "competition": 0.05,
        "weak_signals": 0.05,
        "hormonal": 0.12,
        "digestive": 0.08,
        "territorial_memory": 0.08,
        "adaptive_behavior": 0.10,
        "human_disturbance": 0.09,
        "mineral": 0.05,
        "snow": 0.10
    }
    
    @classmethod
    def calculate_all_factors(
        cls,
        species: str,
        latitude: float,
        hour: int,
        month: int,
        temperature: float,
        snow_depth_cm: float = 0,
        is_crusted: bool = False,
        is_weekend: bool = False
    ) -> Dict:
        """
        Calcule tous les 12 facteurs et retourne un score integre.
        """
        factors = {}
        
        # 1. Predation
        factors["predation"] = PredatorRiskModel.calculate_predation_risk(
            species, latitude, hour, month
        )
        
        # 2. Stress thermique
        factors["thermal_stress"] = StressModel.calculate_thermal_stress(
            species, temperature
        )
        
        # 3. Stress hydrique (simulation distance eau)
        estimated_water_distance = 300 if latitude < 50 else 500
        factors["hydric_stress"] = StressModel.calculate_hydric_stress(
            species, estimated_water_distance, temperature
        )
        
        # 4. Stress social
        factors["social_stress"] = StressModel.calculate_social_stress(
            species, month, group_size=3  # Estimation
        )
        
        # 5. Competition (simulation especes presentes)
        region_species = ["deer", "bear"] if latitude < 50 else ["moose", "caribou"]
        factors["competition"] = InterspeciesCompetitionModel.calculate_competition(
            species, region_species
        )
        
        # 6. Signaux faibles
        factors["weak_signals"] = WeakSignalsModel.detect_anomalies(
            current_score=70,  # Placeholder
            historical_avg=65,
            weather_rapid_change=abs(temperature) > 20,
            unusual_activity=False
        )
        
        # 7. Cycles hormonaux
        factors["hormonal"] = HormonalCycleModel.get_hormonal_phase(species, month)
        
        # 8. Cycles digestifs
        factors["digestive"] = DigestiveCycleModel.get_digestive_phase(species, hour)
        
        # 9. Memoire territoriale
        factors["territorial_memory"] = TerritorialMemoryModel.calculate_avoidance_factor(
            species, days_since_disturbance=7, disturbance_intensity=0.5
        )
        
        # 10. Apprentissage comportemental
        factors["adaptive_behavior"] = AdaptiveBehaviorModel.calculate_adaptation(
            species,
            hunting_pressure_history=[30, 40, 35, 50, 45],  # Simulation
            success_rate_hunters=0.15
        )
        
        # 11. Derangement humain
        disturbances = ["hiking"] if is_weekend else []
        factors["human_disturbance"] = HumanDisturbanceModel.calculate_disturbance(
            disturbances,
            is_weekend=is_weekend,
            is_summer=month in [6, 7, 8]
        )
        
        # 12. Conditions de neige
        factors["snow"] = SnowConditionModel.calculate_snow_impact(
            species, snow_depth_cm, is_crusted, temperature
        )
        
        # 13. Disponibilite minerale
        factors["mineral"] = MineralAvailabilityModel.calculate_mineral_attraction(
            species, month, salt_lick_distance_m=800
        )
        
        # Calcul du score integre
        integrated_score = cls._calculate_integrated_score(factors)
        
        return {
            "factors": factors,
            "integrated_score": integrated_score,
            "dominant_factors": cls._get_dominant_factors(factors),
            "behavioral_recommendations": cls._generate_recommendations(factors, species)
        }
    
    @classmethod
    def _calculate_integrated_score(cls, factors: Dict) -> float:
        """Calcule le score integre pondere."""
        score = 100  # Score de base
        
        # Appliquer les penalites/bonus de chaque facteur
        score -= factors["predation"]["risk_score"] * cls.FACTOR_WEIGHTS["predation"]
        score -= factors["thermal_stress"]["stress_score"] * cls.FACTOR_WEIGHTS["thermal_stress"]
        score -= factors["hydric_stress"]["stress_score"] * cls.FACTOR_WEIGHTS["hydric_stress"]
        score -= factors["social_stress"]["stress_score"] * cls.FACTOR_WEIGHTS["social_stress"]
        score -= factors["competition"]["total_competition_score"] * cls.FACTOR_WEIGHTS["competition"]
        score -= factors["weak_signals"]["anomaly_score"] * cls.FACTOR_WEIGHTS["weak_signals"]
        score *= factors["hormonal"]["activity_modifier"]
        score -= factors["territorial_memory"]["avoidance_score"] * cls.FACTOR_WEIGHTS["territorial_memory"]
        score -= factors["adaptive_behavior"]["adaptation_level"] * cls.FACTOR_WEIGHTS["adaptive_behavior"] * 0.5
        score -= factors["human_disturbance"]["disturbance_score"] * cls.FACTOR_WEIGHTS["human_disturbance"]
        score += factors["mineral"]["salt_lick_attraction"] * cls.FACTOR_WEIGHTS["mineral"] * 0.3
        score -= factors["snow"]["winter_penalty_score"] * cls.FACTOR_WEIGHTS["snow"]
        
        return round(max(0, min(100, score)), 1)
    
    @classmethod
    def _get_dominant_factors(cls, factors: Dict) -> List[str]:
        """Identifie les facteurs dominants."""
        dominant = []
        
        if factors["predation"]["risk_score"] > 50:
            dominant.append("high_predation_risk")
        if factors["thermal_stress"]["stress_score"] > 40:
            dominant.append("thermal_stress")
        if factors["hormonal"]["activity_modifier"] > 1.2:
            dominant.append("hormonal_peak")
        if factors["snow"]["winter_penalty_score"] > 50:
            dominant.append("snow_conditions")
        if factors["human_disturbance"]["disturbance_score"] > 40:
            dominant.append("human_activity")
        
        return dominant if dominant else ["balanced"]
    
    @classmethod
    def _generate_recommendations(cls, factors: Dict, species: str) -> List[str]:
        """Genere des recommandations basees sur les facteurs."""
        recommendations = []
        
        if factors["predation"]["risk_score"] > 50:
            recommendations.append(f"Surveiller les zones de couvert - risque predation eleve ({factors['predation']['dominant_predator']})")
        
        if factors["thermal_stress"]["stress_score"] > 30:
            recommendations.append(f"Animal en stress thermique - cherchera {factors['thermal_stress']['behavioral_response']}")
        
        if factors["hormonal"]["phase"] in ["rut_peak", "pre_rut"]:
            recommendations.append(f"Phase {factors['hormonal']['phase']} - activite accrue, utiliser appels/leurres")
        
        if factors["digestive"]["phase"] == "active_feeding":
            recommendations.append("Phase d'alimentation active - surveiller zones de nourriture")
        
        if factors["mineral"]["seeking_behavior"]:
            recommendations.append("Forte attraction minerale - surveiller salines et licks")
        
        if factors["snow"]["yarding_likelihood"]:
            recommendations.append("Conditions de neige difficiles - animaux concentres dans les ravages")
        
        return recommendations
