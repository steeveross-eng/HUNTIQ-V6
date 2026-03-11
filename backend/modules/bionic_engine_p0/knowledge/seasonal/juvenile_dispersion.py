"""
BIONIC V5 — PHASE C.2: JUVENILE DISPERSAL MODELS
=================================================

Modèles de dispersion juvénile espèce-spécifiques et région-spécifiques.

La dispersion juvénile est le mouvement des jeunes animaux quittant
leur territoire natal pour établir leur propre domaine vital.

CARACTÉRISTIQUES CLÉS:
- Mouvements erratiques et imprévisibles
- Distance de dispersion variable selon l'espèce
- Mortalité élevée pendant cette période
- Fenêtre temporelle dépendante de la date de naissance

ESPÈCES SUPPORTÉES:
- Orignal (Alces alces)
- Cerf de Virginie (Odocoileus virginianus)
- Ours noir (Ursus americanus)
- Wapiti (Cervus canadensis)

CONFORMITÉ: G-SEC | G-QA | G-DOC | BIONIC V5
TRAÇABILITÉ: source_ids obligatoires
VERSION: 1.0.0
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum

logger = logging.getLogger("bionic_engine.juvenile_dispersal")


# =============================================================================
# CONSTANTES ET SOURCES
# =============================================================================

SOURCE_IDS = {
    "MFFP": "SRC-MFFP-DISPERSAL-001",
    "LAVAL": "SRC-LAVAL-JUVEN-001",
    "GPS_COLLAR": "SRC-GPS-COLLAR-001",
    "USGS": "SRC-USGS-DISPERSAL-001",
    "RMEF": "SRC-RMEF-DISPERSAL-001",
    "NDA": "SRC-NDA-DISPERSAL-001",
    "SCIENCE": "SRC-DISPERSAL-LITERATURE-001",
    "BOONE": "SRC-BOONE-MOVEMENT-001",
}


class DispersalSex(str, Enum):
    """Sexe et patrons de dispersion associés"""
    MALE = "male"
    FEMALE = "female"
    BOTH = "both"


class DispersalType(str, Enum):
    """Types de dispersion"""
    NATAL = "natal"               # Quitte le territoire de naissance
    BREEDING = "breeding"         # Dispersion pour reproduction
    EXPLORATORY = "exploratory"   # Exploration sans établissement


class DispersalTrigger(str, Enum):
    """Déclencheurs de la dispersion"""
    MATERNAL_AGGRESSION = "maternal_aggression"    # Mère rejette le jeune
    SIBLING_COMPETITION = "sibling_competition"    # Compétition fratrie
    RESOURCE_LIMITATION = "resource_limitation"    # Ressources insuffisantes
    HORMONAL = "hormonal"                          # Maturation sexuelle
    POPULATION_DENSITY = "population_density"      # Densité locale élevée


@dataclass
class DispersalPattern:
    """
    Patron de dispersion pour une espèce dans une région.
    
    Données basées sur études GPS et télémétrie.
    """
    species: str
    region: str
    sex: DispersalSex
    
    # Timing (mois après naissance)
    onset_months_min: int
    onset_months_max: int
    duration_weeks_avg: int
    duration_weeks_range: Tuple[int, int]
    
    # Distances
    distance_km_avg: float
    distance_km_range: Tuple[float, float]
    distance_km_max_recorded: float
    
    # Comportement
    movement_pattern: str  # "directional", "random_walk", "exploratory_return"
    daily_movement_km: float
    activity_modifier: float
    vulnerability_modifier: float
    
    # Mortalité
    mortality_rate_during_dispersal: float
    main_mortality_causes: List[str]
    
    # Déclencheurs
    triggers: List[DispersalTrigger]
    
    # Habitat
    habitat_preference_during_dispersal: str
    road_crossing_frequency: str  # "high", "medium", "low"
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=list)
    sample_size: int = 0
    confidence: float = 0.80
    version: str = "1.0.0"
    notes: str = ""
    
    def get_dispersal_window(self, birth_date: date) -> Tuple[date, date]:
        """Calcule la fenêtre de dispersion basée sur la date de naissance."""
        start = birth_date + timedelta(days=self.onset_months_min * 30)
        end = birth_date + timedelta(days=self.onset_months_max * 30)
        return start, end
    
    def is_in_dispersal_window(self, birth_date: date, check_date: date) -> bool:
        """Vérifie si une date est dans la fenêtre de dispersion."""
        start, end = self.get_dispersal_window(birth_date)
        return start <= check_date <= end
    
    def to_dict(self) -> Dict[str, Any]:
        """Exporte en dictionnaire traçable."""
        return {
            "species": self.species,
            "region": self.region,
            "sex": self.sex.value,
            "timing": {
                "onset_months": f"{self.onset_months_min}-{self.onset_months_max}",
                "duration_weeks_avg": self.duration_weeks_avg,
                "duration_weeks_range": list(self.duration_weeks_range)
            },
            "distances": {
                "avg_km": self.distance_km_avg,
                "range_km": list(self.distance_km_range),
                "max_recorded_km": self.distance_km_max_recorded
            },
            "behavior": {
                "movement_pattern": self.movement_pattern,
                "daily_movement_km": self.daily_movement_km,
                "activity_modifier": self.activity_modifier,
                "vulnerability_modifier": self.vulnerability_modifier
            },
            "mortality": {
                "rate": self.mortality_rate_during_dispersal,
                "main_causes": self.main_mortality_causes
            },
            "triggers": [t.value for t in self.triggers],
            "habitat": {
                "preference": self.habitat_preference_during_dispersal,
                "road_crossing": self.road_crossing_frequency
            },
            "metadata": {
                "source_ids": self.source_ids,
                "sample_size": self.sample_size,
                "confidence": self.confidence,
                "version": self.version
            },
            "notes": self.notes
        }


# =============================================================================
# REGISTRY DES MODÈLES DE DISPERSION
# =============================================================================

class JuvenileDispersalRegistry:
    """
    Registre central des modèles de dispersion juvénile.
    
    Pipeline BIONIC V5:
    - Données centralisées dans le Knowledge Layer
    - Basé sur études GPS et télémétrie
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
        
        self._patterns: Dict[str, List[DispersalPattern]] = {}
        self._initialize_patterns()
        self._initialized = True
        
        total = sum(len(p) for p in self._patterns.values())
        logger.info(f"[BIONIC] JuvenileDispersalRegistry initialized with {total} patterns")
    
    def _initialize_patterns(self):
        """Initialise tous les patrons de dispersion."""
        
        # =====================================================================
        # ORIGNAL (MOOSE)
        # =====================================================================
        
        self._patterns["moose"] = []
        
        # Orignal mâle - Québec
        self._patterns["moose"].append(DispersalPattern(
            species="moose",
            region="CA-QC",
            sex=DispersalSex.MALE,
            
            # Timing: 10-14 mois après naissance
            onset_months_min=10,
            onset_months_max=14,
            duration_weeks_avg=8,
            duration_weeks_range=(4, 16),
            
            # Distances
            distance_km_avg=35.0,
            distance_km_range=(8.0, 120.0),
            distance_km_max_recorded=180.0,
            
            # Comportement
            movement_pattern="directional",
            daily_movement_km=4.5,
            activity_modifier=1.5,
            vulnerability_modifier=1.4,
            
            # Mortalité
            mortality_rate_during_dispersal=0.35,
            main_mortality_causes=[
                "collision_routiere",
                "predation_ours",
                "noyade",
                "epuisement"
            ],
            
            # Déclencheurs
            triggers=[
                DispersalTrigger.MATERNAL_AGGRESSION,
                DispersalTrigger.HORMONAL
            ],
            
            # Habitat
            habitat_preference_during_dispersal="corridor_forestier",
            road_crossing_frequency="high",
            
            # Traçabilité
            source_ids=[
                SOURCE_IDS["MFFP"],
                SOURCE_IDS["LAVAL"],
                SOURCE_IDS["GPS_COLLAR"]
            ],
            sample_size=156,
            confidence=0.88,
            notes="Mâles dispersent plus loin et plus tôt que les femelles. "
                  "Pic de dispersion en mai-juin. Mouvements erratiques pendant 4-8 semaines. "
                  "Risque élevé de collision routière pendant cette période."
        ))
        
        # Orignal femelle - Québec
        self._patterns["moose"].append(DispersalPattern(
            species="moose",
            region="CA-QC",
            sex=DispersalSex.FEMALE,
            
            onset_months_min=12,
            onset_months_max=24,
            duration_weeks_avg=4,
            duration_weeks_range=(2, 8),
            
            distance_km_avg=12.0,
            distance_km_range=(2.0, 35.0),
            distance_km_max_recorded=65.0,
            
            movement_pattern="exploratory_return",
            daily_movement_km=2.5,
            activity_modifier=1.2,
            vulnerability_modifier=1.2,
            
            mortality_rate_during_dispersal=0.20,
            main_mortality_causes=[
                "predation_ours",
                "collision_routiere"
            ],
            
            triggers=[
                DispersalTrigger.MATERNAL_AGGRESSION,
                DispersalTrigger.RESOURCE_LIMITATION
            ],
            
            habitat_preference_during_dispersal="proximite_habitat_natal",
            road_crossing_frequency="medium",
            
            source_ids=[
                SOURCE_IDS["MFFP"],
                SOURCE_IDS["LAVAL"],
                SOURCE_IDS["GPS_COLLAR"]
            ],
            sample_size=142,
            confidence=0.85,
            notes="Femelles souvent philopatriques - peuvent rester près du territoire maternel. "
                  "Dispersion plus courte et plus tardive que les mâles."
        ))
        
        # Orignal - Ontario (patterns similaires avec variations)
        self._patterns["moose"].append(DispersalPattern(
            species="moose",
            region="CA-ON",
            sex=DispersalSex.MALE,
            
            onset_months_min=10,
            onset_months_max=14,
            duration_weeks_avg=10,
            duration_weeks_range=(5, 18),
            
            distance_km_avg=42.0,
            distance_km_range=(10.0, 150.0),
            distance_km_max_recorded=210.0,
            
            movement_pattern="directional",
            daily_movement_km=5.0,
            activity_modifier=1.6,
            vulnerability_modifier=1.5,
            
            mortality_rate_during_dispersal=0.38,
            main_mortality_causes=[
                "collision_routiere",
                "predation_loup",
                "predation_ours"
            ],
            
            triggers=[
                DispersalTrigger.MATERNAL_AGGRESSION,
                DispersalTrigger.HORMONAL,
                DispersalTrigger.POPULATION_DENSITY
            ],
            
            habitat_preference_during_dispersal="corridor_forestier",
            road_crossing_frequency="high",
            
            source_ids=[
                SOURCE_IDS["GPS_COLLAR"],
                SOURCE_IDS["USGS"]
            ],
            sample_size=98,
            confidence=0.84,
            notes="Distances de dispersion plus élevées en Ontario. "
                  "Pression des loups plus importante. "
                  "Corridors autoroute 17 et 11 sont des zones à risque."
        ))
        
        # =====================================================================
        # CERF DE VIRGINIE (WHITE-TAILED DEER)
        # =====================================================================
        
        self._patterns["deer"] = []
        
        # Cerf mâle - Québec
        self._patterns["deer"].append(DispersalPattern(
            species="deer",
            region="CA-QC",
            sex=DispersalSex.MALE,
            
            # Dispersion plus précoce: 6-12 mois
            onset_months_min=6,
            onset_months_max=12,
            duration_weeks_avg=4,
            duration_weeks_range=(2, 8),
            
            distance_km_avg=8.0,
            distance_km_range=(2.0, 25.0),
            distance_km_max_recorded=45.0,
            
            movement_pattern="exploratory_return",
            daily_movement_km=2.0,
            activity_modifier=1.3,
            vulnerability_modifier=1.3,
            
            mortality_rate_during_dispersal=0.45,
            main_mortality_causes=[
                "predation_coyote",
                "collision_routiere",
                "chasse",
                "hiver_rigoureux"
            ],
            
            triggers=[
                DispersalTrigger.SIBLING_COMPETITION,
                DispersalTrigger.HORMONAL
            ],
            
            habitat_preference_during_dispersal="lisiere_agricole",
            road_crossing_frequency="high",
            
            source_ids=[
                SOURCE_IDS["MFFP"],
                SOURCE_IDS["NDA"]
            ],
            sample_size=245,
            confidence=0.86,
            notes="Pic de dispersion en automne (octobre-novembre) coïncide avec pré-rut. "
                  "Jeunes mâles très vulnérables pendant cette période. "
                  "50% mortalité première année de vie."
        ))
        
        # Cerf femelle - Québec
        self._patterns["deer"].append(DispersalPattern(
            species="deer",
            region="CA-QC",
            sex=DispersalSex.FEMALE,
            
            onset_months_min=12,
            onset_months_max=24,
            duration_weeks_avg=2,
            duration_weeks_range=(1, 4),
            
            distance_km_avg=2.5,
            distance_km_range=(0.5, 8.0),
            distance_km_max_recorded=15.0,
            
            movement_pattern="exploratory_return",
            daily_movement_km=1.0,
            activity_modifier=1.1,
            vulnerability_modifier=1.1,
            
            mortality_rate_during_dispersal=0.15,
            main_mortality_causes=[
                "predation_coyote",
                "hiver_rigoureux"
            ],
            
            triggers=[
                DispersalTrigger.POPULATION_DENSITY,
                DispersalTrigger.RESOURCE_LIMITATION
            ],
            
            habitat_preference_during_dispersal="proximite_habitat_natal",
            road_crossing_frequency="low",
            
            source_ids=[
                SOURCE_IDS["MFFP"],
                SOURCE_IDS["NDA"]
            ],
            sample_size=312,
            confidence=0.90,
            notes="Femelles très philopatriques. Restent souvent dans le domaine vital maternel. "
                  "Dispersion rare et courte distance."
        ))
        
        # Cerf - Maine
        self._patterns["deer"].append(DispersalPattern(
            species="deer",
            region="US-ME",
            sex=DispersalSex.MALE,
            
            onset_months_min=6,
            onset_months_max=10,
            duration_weeks_avg=5,
            duration_weeks_range=(3, 10),
            
            distance_km_avg=10.0,
            distance_km_range=(3.0, 30.0),
            distance_km_max_recorded=55.0,
            
            movement_pattern="directional",
            daily_movement_km=2.5,
            activity_modifier=1.4,
            vulnerability_modifier=1.4,
            
            mortality_rate_during_dispersal=0.50,
            main_mortality_causes=[
                "chasse",
                "predation_coyote",
                "collision_routiere",
                "hiver"
            ],
            
            triggers=[
                DispersalTrigger.SIBLING_COMPETITION,
                DispersalTrigger.HORMONAL
            ],
            
            habitat_preference_during_dispersal="foret_mixte",
            road_crossing_frequency="high",
            
            source_ids=[
                SOURCE_IDS["USGS"],
                SOURCE_IDS["NDA"]
            ],
            sample_size=178,
            confidence=0.82,
            notes="Région nordique avec hivers rigoureux. "
                  "Mortalité hivernale importante pour les juvéniles dispersants."
        ))
        
        # =====================================================================
        # OURS NOIR (BLACK BEAR)
        # =====================================================================
        
        self._patterns["bear"] = []
        
        # Ours mâle - Québec
        self._patterns["bear"].append(DispersalPattern(
            species="bear",
            region="CA-QC",
            sex=DispersalSex.MALE,
            
            # Dispersion tardive: 16-18 mois (après 2e hiver avec la mère)
            onset_months_min=16,
            onset_months_max=18,
            duration_weeks_avg=12,
            duration_weeks_range=(6, 24),
            
            distance_km_avg=60.0,
            distance_km_range=(15.0, 200.0),
            distance_km_max_recorded=350.0,
            
            movement_pattern="directional",
            daily_movement_km=8.0,
            activity_modifier=1.8,
            vulnerability_modifier=1.3,
            
            mortality_rate_during_dispersal=0.25,
            main_mortality_causes=[
                "collision_routiere",
                "chasse_nuisance",
                "conflit_males_adultes"
            ],
            
            triggers=[
                DispersalTrigger.MATERNAL_AGGRESSION,
                DispersalTrigger.HORMONAL
            ],
            
            habitat_preference_during_dispersal="corridor_forestier_continu",
            road_crossing_frequency="medium",
            
            source_ids=[
                SOURCE_IDS["MFFP"],
                SOURCE_IDS["GPS_COLLAR"],
                SOURCE_IDS["SCIENCE"]
            ],
            sample_size=87,
            confidence=0.85,
            notes="Mâles dispersent très loin - record de 350km au Québec. "
                  "Dispersion en juin-juillet après émergence du 2e hiver. "
                  "Conflits avec mâles adultes territoriaux fréquents."
        ))
        
        # Ours femelle - Québec
        self._patterns["bear"].append(DispersalPattern(
            species="bear",
            region="CA-QC",
            sex=DispersalSex.FEMALE,
            
            onset_months_min=16,
            onset_months_max=20,
            duration_weeks_avg=4,
            duration_weeks_range=(2, 8),
            
            distance_km_avg=8.0,
            distance_km_range=(2.0, 25.0),
            distance_km_max_recorded=45.0,
            
            movement_pattern="exploratory_return",
            daily_movement_km=3.0,
            activity_modifier=1.3,
            vulnerability_modifier=1.1,
            
            mortality_rate_during_dispersal=0.12,
            main_mortality_causes=[
                "collision_routiere",
                "conflit_femelle_adulte"
            ],
            
            triggers=[
                DispersalTrigger.MATERNAL_AGGRESSION,
                DispersalTrigger.RESOURCE_LIMITATION
            ],
            
            habitat_preference_during_dispersal="proximite_habitat_natal",
            road_crossing_frequency="low",
            
            source_ids=[
                SOURCE_IDS["MFFP"],
                SOURCE_IDS["GPS_COLLAR"]
            ],
            sample_size=64,
            confidence=0.83,
            notes="Femelles souvent établies près ou dans le domaine maternel. "
                  "Mère peut céder une partie de son territoire à ses filles."
        ))
        
        # =====================================================================
        # WAPITI (ELK)
        # =====================================================================
        
        self._patterns["elk"] = []
        
        # Wapiti mâle - Alberta
        self._patterns["elk"].append(DispersalPattern(
            species="elk",
            region="CA-AB",
            sex=DispersalSex.MALE,
            
            onset_months_min=10,
            onset_months_max=14,
            duration_weeks_avg=6,
            duration_weeks_range=(3, 12),
            
            distance_km_avg=25.0,
            distance_km_range=(5.0, 80.0),
            distance_km_max_recorded=120.0,
            
            movement_pattern="directional",
            daily_movement_km=5.0,
            activity_modifier=1.4,
            vulnerability_modifier=1.3,
            
            mortality_rate_during_dispersal=0.30,
            main_mortality_causes=[
                "predation_loup",
                "predation_couguar",
                "chasse"
            ],
            
            triggers=[
                DispersalTrigger.HORMONAL,
                DispersalTrigger.SIBLING_COMPETITION
            ],
            
            habitat_preference_during_dispersal="prairie_montagne_transition",
            road_crossing_frequency="medium",
            
            source_ids=[
                SOURCE_IDS["RMEF"],
                SOURCE_IDS["GPS_COLLAR"],
                SOURCE_IDS["BOONE"]
            ],
            sample_size=134,
            confidence=0.86,
            notes="Jeunes mâles quittent la harde maternelle au printemps. "
                  "Rejoignent souvent des groupes de mâles célibataires. "
                  "Forte pression de prédation par les loups."
        ))
        
        # Wapiti femelle - Alberta
        self._patterns["elk"].append(DispersalPattern(
            species="elk",
            region="CA-AB",
            sex=DispersalSex.FEMALE,
            
            onset_months_min=12,
            onset_months_max=24,
            duration_weeks_avg=3,
            duration_weeks_range=(1, 6),
            
            distance_km_avg=5.0,
            distance_km_range=(1.0, 15.0),
            distance_km_max_recorded=30.0,
            
            movement_pattern="exploratory_return",
            daily_movement_km=2.0,
            activity_modifier=1.1,
            vulnerability_modifier=1.1,
            
            mortality_rate_during_dispersal=0.15,
            main_mortality_causes=[
                "predation_loup",
                "predation_couguar"
            ],
            
            triggers=[
                DispersalTrigger.POPULATION_DENSITY
            ],
            
            habitat_preference_during_dispersal="dans_harde_maternelle",
            road_crossing_frequency="low",
            
            source_ids=[
                SOURCE_IDS["RMEF"],
                SOURCE_IDS["GPS_COLLAR"]
            ],
            sample_size=156,
            confidence=0.88,
            notes="Femelles restent généralement dans la harde maternelle. "
                  "Structure sociale matriarcale maintenue."
        ))
    
    # =========================================================================
    # MÉTHODES PUBLIQUES
    # =========================================================================
    
    def get_patterns(
        self, 
        species: str, 
        region: Optional[str] = None,
        sex: Optional[DispersalSex] = None
    ) -> List[DispersalPattern]:
        """
        Récupère les patrons de dispersion pour une espèce.
        
        Args:
            species: Code espèce
            region: Filtre par région (optionnel)
            sex: Filtre par sexe (optionnel)
            
        Returns:
            Liste de DispersalPattern correspondants
        """
        patterns = self._patterns.get(species, [])
        
        if region:
            patterns = [p for p in patterns if p.region == region]
        
        if sex:
            patterns = [p for p in patterns if p.sex == sex or p.sex == DispersalSex.BOTH]
        
        return patterns
    
    def get_best_match(
        self, 
        species: str, 
        region: str, 
        sex: DispersalSex
    ) -> Optional[DispersalPattern]:
        """
        Trouve le meilleur patron correspondant avec fallback.
        """
        # Essayer correspondance exacte
        patterns = self.get_patterns(species, region, sex)
        if patterns:
            return patterns[0]
        
        # Fallback: région par défaut
        default_regions = {
            "moose": "CA-QC",
            "deer": "CA-QC",
            "bear": "CA-QC",
            "elk": "CA-AB"
        }
        
        default_region = default_regions.get(species)
        if default_region and default_region != region:
            patterns = self.get_patterns(species, default_region, sex)
            if patterns:
                logger.warning(f"[BIONIC] Dispersal pattern not found for {species}_{region}_{sex.value}, "
                              f"using {species}_{default_region}_{sex.value}")
                return patterns[0]
        
        return None
    
    def calculate_dispersal_risk(
        self,
        species: str,
        region: str,
        sex: DispersalSex,
        birth_date: date,
        check_date: date
    ) -> Dict[str, Any]:
        """
        Calcule le risque et les caractéristiques de dispersion pour une date.
        
        Returns:
            Dictionnaire avec risque, modificateurs, et recommandations
        """
        pattern = self.get_best_match(species, region, sex)
        if not pattern:
            return {
                "in_dispersal_window": False,
                "risk_level": "unknown",
                "pattern_found": False
            }
        
        in_window = pattern.is_in_dispersal_window(birth_date, check_date)
        
        if not in_window:
            return {
                "in_dispersal_window": False,
                "risk_level": "low",
                "pattern_found": True,
                "activity_modifier": 1.0,
                "vulnerability_modifier": 1.0
            }
        
        return {
            "in_dispersal_window": True,
            "risk_level": "high" if sex == DispersalSex.MALE else "medium",
            "pattern_found": True,
            "activity_modifier": pattern.activity_modifier,
            "vulnerability_modifier": pattern.vulnerability_modifier,
            "expected_daily_movement_km": pattern.daily_movement_km,
            "expected_distance_km": pattern.distance_km_avg,
            "mortality_risk": pattern.mortality_rate_during_dispersal,
            "main_risks": pattern.main_mortality_causes,
            "road_crossing_risk": pattern.road_crossing_frequency,
            "source_ids": pattern.source_ids
        }
    
    def get_all_species(self) -> List[str]:
        """Retourne la liste des espèces supportées."""
        return list(self._patterns.keys())
    
    def export_all_patterns(self) -> Dict[str, List[Dict]]:
        """Exporte tous les patrons pour documentation/API."""
        return {
            species: [p.to_dict() for p in patterns]
            for species, patterns in self._patterns.items()
        }


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_dispersal_registry: Optional[JuvenileDispersalRegistry] = None


def get_dispersal_registry() -> JuvenileDispersalRegistry:
    """Retourne l'instance singleton du registre de dispersion."""
    global _dispersal_registry
    if _dispersal_registry is None:
        _dispersal_registry = JuvenileDispersalRegistry()
    return _dispersal_registry
