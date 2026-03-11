"""
BIONIC V5 — PHASE C.1: CALVING/FAWNING MODELS
==============================================

Modèles de mise bas espèce-spécifiques et région-spécifiques.

ESPÈCES SUPPORTÉES:
- Orignal (Alces alces) — Calving
- Cerf de Virginie (Odocoileus virginianus) — Fawning
- Ours noir (Ursus americanus) — Cubbing
- Wapiti (Cervus canadensis) — Calving

RÉGIONS SUPPORTÉES:
- CA-QC (Québec)
- CA-ON (Ontario)
- CA-BC (Colombie-Britannique)
- CA-AB (Alberta)
- US-ME (Maine)
- US-MN (Minnesota)

CONFORMITÉ: G-SEC | G-QA | G-DOC | BIONIC V5
TRAÇABILITÉ: source_ids obligatoires
VERSION: 1.0.0
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum

logger = logging.getLogger("bionic_engine.calving_models")


# =============================================================================
# CONSTANTES ET SOURCES
# =============================================================================

SOURCE_IDS = {
    "MFFP": "SRC-MFFP-CALVING-001",           # Ministère Forêts Faune Parcs Québec
    "LAVAL": "SRC-LAVAL-REPRO-001",           # Université Laval - Études reproduction
    "MRNF": "SRC-MRNF-NAISSANCE-001",         # Min. Ressources Naturelles Faune
    "NDA": "SRC-NDA-FAWNING-001",             # National Deer Association
    "RMEF": "SRC-RMEF-CALVING-001",           # Rocky Mountain Elk Foundation
    "QDMA": "SRC-QDMA-REPRO-001",             # Quality Deer Management Association
    "USGS": "SRC-USGS-WILDLIFE-001",          # US Geological Survey
    "CWS": "SRC-CWS-HABITAT-001",             # Canadian Wildlife Service
    "BOONE": "SRC-BOONE-CROCKETT-001",        # Boone and Crockett Club
    "SCIENCE": "SRC-PEER-REVIEWED-001",       # Publications scientifiques peer-reviewed
}


class BirthType(str, Enum):
    """Types de mise bas selon l'espèce"""
    CALVING = "calving"       # Orignal, Wapiti (veaux)
    FAWNING = "fawning"       # Cerf de Virginie (faons)
    CUBBING = "cubbing"       # Ours (oursons)
    

class BirthSitePreference(str, Enum):
    """Préférences de site de mise bas"""
    DENSE_COVER = "dense_cover"           # Couvert dense
    WETLAND_EDGE = "wetland_edge"         # Bordure de milieu humide
    ISLAND = "island"                      # Île (protection prédateurs)
    STEEP_SLOPE = "steep_slope"           # Pente abrupte
    THICKET = "thicket"                   # Fourré dense
    DEN = "den"                           # Tanière (ours)
    MEADOW_EDGE = "meadow_edge"           # Bordure de prairie


@dataclass
class CalvingPeriod:
    """
    Période de mise bas pour une espèce dans une région donnée.
    
    Attributs scientifiques:
    - peak_date: Date pic de mise bas (50% des naissances)
    - range_days: Écart-type en jours
    - gestation_days: Durée moyenne de gestation
    - litter_size: Taille moyenne de la portée
    """
    species: str
    region: str
    birth_type: BirthType
    
    # Période
    start_month: int
    start_day: int
    end_month: int
    end_day: int
    peak_month: int
    peak_day: int
    
    # Données biologiques
    gestation_days: int
    litter_size_avg: float
    litter_size_range: Tuple[int, int]
    survival_rate_first_month: float
    
    # Comportement
    isolation_days_before: int      # Jours d'isolement avant mise bas
    mother_calf_bond_weeks: int     # Durée du lien mère-petit
    activity_modifier: float
    movement_modifier: float
    vulnerability_modifier: float
    
    # Sites préférés
    preferred_sites: List[BirthSitePreference]
    
    # Facteurs environnementaux
    min_temp_celsius: float         # Température minimale favorable
    max_temp_celsius: float         # Température maximale favorable
    snow_depth_max_cm: float        # Profondeur neige max acceptable
    
    # Traçabilité BIONIC V5
    source_ids: List[str] = field(default_factory=list)
    confidence: float = 0.85
    version: str = "1.0.0"
    notes: str = ""
    
    def is_active(self, check_date: date) -> bool:
        """Vérifie si la période de mise bas est active."""
        check_md = (check_date.month, check_date.day)
        start_md = (self.start_month, self.start_day)
        end_md = (self.end_month, self.end_day)
        
        if start_md <= end_md:
            return start_md <= check_md <= end_md
        else:
            return check_md >= start_md or check_md <= end_md
    
    def days_from_peak(self, check_date: date) -> int:
        """Calcule le nombre de jours depuis/jusqu'au pic de mise bas."""
        peak = date(check_date.year, self.peak_month, self.peak_day)
        return (check_date - peak).days
    
    def get_activity_score(self, check_date: date) -> float:
        """
        Calcule le score d'activité basé sur la proximité du pic.
        Plus proche du pic = activité plus réduite (femelles isolées).
        """
        if not self.is_active(check_date):
            return 1.0  # Hors période, activité normale
        
        days_from = abs(self.days_from_peak(check_date))
        peak_period_days = 14  # ±2 semaines autour du pic
        
        if days_from <= peak_period_days:
            # Proche du pic: activité très réduite
            return self.activity_modifier * (0.5 + 0.5 * (days_from / peak_period_days))
        else:
            # En dehors du pic immédiat
            return self.activity_modifier
    
    def to_dict(self) -> Dict[str, Any]:
        """Exporte les données en dictionnaire traçable."""
        return {
            "species": self.species,
            "region": self.region,
            "birth_type": self.birth_type.value,
            "period": {
                "start": f"{self.start_month:02d}-{self.start_day:02d}",
                "end": f"{self.end_month:02d}-{self.end_day:02d}",
                "peak": f"{self.peak_month:02d}-{self.peak_day:02d}"
            },
            "biology": {
                "gestation_days": self.gestation_days,
                "litter_size_avg": self.litter_size_avg,
                "litter_size_range": list(self.litter_size_range),
                "survival_rate_first_month": self.survival_rate_first_month
            },
            "behavior": {
                "isolation_days_before": self.isolation_days_before,
                "mother_calf_bond_weeks": self.mother_calf_bond_weeks,
                "activity_modifier": self.activity_modifier,
                "movement_modifier": self.movement_modifier,
                "vulnerability_modifier": self.vulnerability_modifier
            },
            "preferred_sites": [s.value for s in self.preferred_sites],
            "environmental_limits": {
                "min_temp_celsius": self.min_temp_celsius,
                "max_temp_celsius": self.max_temp_celsius,
                "snow_depth_max_cm": self.snow_depth_max_cm
            },
            "source_ids": self.source_ids,
            "confidence": self.confidence,
            "version": self.version,
            "notes": self.notes
        }


# =============================================================================
# REGISTRY DES MODÈLES DE MISE BAS
# =============================================================================

class CalvingModelRegistry:
    """
    Registre central des modèles de mise bas.
    
    Pipeline BIONIC V5:
    - Données centralisées dans le Knowledge Layer
    - Aucun calcul local
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
        
        self._models: Dict[str, CalvingPeriod] = {}
        self._initialize_models()
        self._initialized = True
        logger.info(f"[BIONIC] CalvingModelRegistry initialized with {len(self._models)} models")
    
    def _initialize_models(self):
        """Initialise tous les modèles de mise bas."""
        
        # =====================================================================
        # ORIGNAL (MOOSE) — CALVING
        # =====================================================================
        
        # Orignal - Québec
        self._models["moose_CA-QC"] = CalvingPeriod(
            species="moose",
            region="CA-QC",
            birth_type=BirthType.CALVING,
            
            # Période: mi-mai à mi-juin, pic fin mai
            start_month=5, start_day=10,
            end_month=6, end_day=20,
            peak_month=5, peak_day=28,
            
            # Biologie
            gestation_days=231,  # ~7.5 mois
            litter_size_avg=1.3,
            litter_size_range=(1, 2),
            survival_rate_first_month=0.75,
            
            # Comportement
            isolation_days_before=14,
            mother_calf_bond_weeks=52,  # ~1 an
            activity_modifier=0.6,
            movement_modifier=0.4,
            vulnerability_modifier=0.5,
            
            # Sites préférés
            preferred_sites=[
                BirthSitePreference.ISLAND,
                BirthSitePreference.WETLAND_EDGE,
                BirthSitePreference.DENSE_COVER
            ],
            
            # Environnement
            min_temp_celsius=5.0,
            max_temp_celsius=20.0,
            snow_depth_max_cm=10.0,
            
            # Traçabilité
            source_ids=[
                SOURCE_IDS["MFFP"],
                SOURCE_IDS["LAVAL"],
                SOURCE_IDS["SCIENCE"]
            ],
            confidence=0.90,
            notes="Femelles recherchent îlots ou zones humides pour protection contre prédateurs. "
                  "Isolement 1-2 semaines avant mise bas. Veaux peuvent marcher dans les heures suivant la naissance."
        )
        
        # Orignal - Ontario
        self._models["moose_CA-ON"] = CalvingPeriod(
            species="moose",
            region="CA-ON",
            birth_type=BirthType.CALVING,
            
            start_month=5, start_day=15,
            end_month=6, end_day=25,
            peak_month=6, peak_day=1,
            
            gestation_days=231,
            litter_size_avg=1.2,
            litter_size_range=(1, 2),
            survival_rate_first_month=0.72,
            
            isolation_days_before=12,
            mother_calf_bond_weeks=50,
            activity_modifier=0.6,
            movement_modifier=0.45,
            vulnerability_modifier=0.5,
            
            preferred_sites=[
                BirthSitePreference.WETLAND_EDGE,
                BirthSitePreference.DENSE_COVER,
                BirthSitePreference.ISLAND
            ],
            
            min_temp_celsius=6.0,
            max_temp_celsius=22.0,
            snow_depth_max_cm=5.0,
            
            source_ids=[
                SOURCE_IDS["MRNF"],
                SOURCE_IDS["CWS"],
                SOURCE_IDS["SCIENCE"]
            ],
            confidence=0.88,
            notes="Légèrement plus tardif qu'au Québec dû au climat. "
                  "Pression des loups plus importante dans certaines régions."
        )
        
        # Orignal - Alaska (référence nord)
        self._models["moose_US-AK"] = CalvingPeriod(
            species="moose",
            region="US-AK",
            birth_type=BirthType.CALVING,
            
            start_month=5, start_day=20,
            end_month=6, end_day=15,
            peak_month=6, peak_day=5,
            
            gestation_days=235,
            litter_size_avg=1.4,
            litter_size_range=(1, 3),
            survival_rate_first_month=0.65,
            
            isolation_days_before=10,
            mother_calf_bond_weeks=54,
            activity_modifier=0.55,
            movement_modifier=0.35,
            vulnerability_modifier=0.45,
            
            preferred_sites=[
                BirthSitePreference.ISLAND,
                BirthSitePreference.STEEP_SLOPE,
                BirthSitePreference.WETLAND_EDGE
            ],
            
            min_temp_celsius=2.0,
            max_temp_celsius=18.0,
            snow_depth_max_cm=20.0,
            
            source_ids=[
                SOURCE_IDS["USGS"],
                SOURCE_IDS["SCIENCE"]
            ],
            confidence=0.85,
            notes="Taux de jumeaux plus élevé. Pression prédation (ours, loups) très importante. "
                  "Survie fortement influencée par conditions printanières."
        )
        
        # =====================================================================
        # CERF DE VIRGINIE (WHITE-TAILED DEER) — FAWNING
        # =====================================================================
        
        # Cerf - Québec
        self._models["deer_CA-QC"] = CalvingPeriod(
            species="deer",
            region="CA-QC",
            birth_type=BirthType.FAWNING,
            
            start_month=5, start_day=20,
            end_month=7, end_day=10,
            peak_month=6, peak_day=10,
            
            gestation_days=200,  # ~6.5 mois
            litter_size_avg=1.8,
            litter_size_range=(1, 3),
            survival_rate_first_month=0.70,
            
            isolation_days_before=7,
            mother_calf_bond_weeks=26,  # ~6 mois
            activity_modifier=0.7,
            movement_modifier=0.5,
            vulnerability_modifier=0.6,
            
            preferred_sites=[
                BirthSitePreference.THICKET,
                BirthSitePreference.MEADOW_EDGE,
                BirthSitePreference.DENSE_COVER
            ],
            
            min_temp_celsius=10.0,
            max_temp_celsius=28.0,
            snow_depth_max_cm=0.0,
            
            source_ids=[
                SOURCE_IDS["MFFP"],
                SOURCE_IDS["NDA"],
                SOURCE_IDS["QDMA"]
            ],
            confidence=0.88,
            notes="Faons tachetés restent cachés 2-3 semaines. Mère revient allaiter 3-4 fois/jour. "
                  "Stratégie anti-prédation: immobilité et absence d'odeur."
        )
        
        # Cerf - Ontario
        self._models["deer_CA-ON"] = CalvingPeriod(
            species="deer",
            region="CA-ON",
            birth_type=BirthType.FAWNING,
            
            start_month=5, start_day=25,
            end_month=7, end_day=15,
            peak_month=6, peak_day=15,
            
            gestation_days=200,
            litter_size_avg=1.7,
            litter_size_range=(1, 3),
            survival_rate_first_month=0.68,
            
            isolation_days_before=5,
            mother_calf_bond_weeks=24,
            activity_modifier=0.7,
            movement_modifier=0.55,
            vulnerability_modifier=0.6,
            
            preferred_sites=[
                BirthSitePreference.THICKET,
                BirthSitePreference.DENSE_COVER,
                BirthSitePreference.MEADOW_EDGE
            ],
            
            min_temp_celsius=12.0,
            max_temp_celsius=30.0,
            snow_depth_max_cm=0.0,
            
            source_ids=[
                SOURCE_IDS["MRNF"],
                SOURCE_IDS["NDA"]
            ],
            confidence=0.86,
            notes="Population dense dans le sud ontarien. "
                  "Faons vulnérables aux coyotes pendant les premières semaines."
        )
        
        # Cerf - Maine (US)
        self._models["deer_US-ME"] = CalvingPeriod(
            species="deer",
            region="US-ME",
            birth_type=BirthType.FAWNING,
            
            start_month=5, start_day=25,
            end_month=7, end_day=5,
            peak_month=6, peak_day=8,
            
            gestation_days=200,
            litter_size_avg=1.6,
            litter_size_range=(1, 2),
            survival_rate_first_month=0.65,
            
            isolation_days_before=6,
            mother_calf_bond_weeks=25,
            activity_modifier=0.7,
            movement_modifier=0.5,
            vulnerability_modifier=0.6,
            
            preferred_sites=[
                BirthSitePreference.DENSE_COVER,
                BirthSitePreference.THICKET
            ],
            
            min_temp_celsius=10.0,
            max_temp_celsius=26.0,
            snow_depth_max_cm=0.0,
            
            source_ids=[
                SOURCE_IDS["USGS"],
                SOURCE_IDS["NDA"]
            ],
            confidence=0.84,
            notes="Région nordique des États-Unis. Hivers rigoureux affectent condition des biches."
        )
        
        # =====================================================================
        # OURS NOIR (BLACK BEAR) — CUBBING
        # =====================================================================
        
        # Ours - Québec
        self._models["bear_CA-QC"] = CalvingPeriod(
            species="bear",
            region="CA-QC",
            birth_type=BirthType.CUBBING,
            
            # Naissance en tanière (janvier-février)
            start_month=1, start_day=15,
            end_month=2, end_day=15,
            peak_month=1, peak_day=28,
            
            gestation_days=220,  # Incluant implantation différée
            litter_size_avg=2.2,
            litter_size_range=(1, 4),
            survival_rate_first_month=0.85,  # Protégés en tanière
            
            isolation_days_before=60,  # Entrée en tanière
            mother_calf_bond_weeks=78,  # ~18 mois
            activity_modifier=0.0,  # En tanière, aucune activité
            movement_modifier=0.0,
            vulnerability_modifier=0.9,  # Très vulnérable si dérangée
            
            preferred_sites=[
                BirthSitePreference.DEN
            ],
            
            min_temp_celsius=-30.0,
            max_temp_celsius=5.0,
            snow_depth_max_cm=200.0,  # Couverture isolante
            
            source_ids=[
                SOURCE_IDS["MFFP"],
                SOURCE_IDS["CWS"],
                SOURCE_IDS["SCIENCE"]
            ],
            confidence=0.92,
            notes="Naissance en tanière pendant hibernation. Oursons minuscules (~300g). "
                  "Femelle ne s'alimente pas pendant 5-6 mois. Sortie de tanière: avril-mai."
        )
        
        # Ours - Colombie-Britannique
        self._models["bear_CA-BC"] = CalvingPeriod(
            species="bear",
            region="CA-BC",
            birth_type=BirthType.CUBBING,
            
            start_month=1, start_day=10,
            end_month=2, end_day=20,
            peak_month=1, peak_day=25,
            
            gestation_days=220,
            litter_size_avg=2.0,
            litter_size_range=(1, 3),
            survival_rate_first_month=0.82,
            
            isolation_days_before=50,
            mother_calf_bond_weeks=72,
            activity_modifier=0.0,
            movement_modifier=0.0,
            vulnerability_modifier=0.85,
            
            preferred_sites=[
                BirthSitePreference.DEN
            ],
            
            min_temp_celsius=-25.0,
            max_temp_celsius=8.0,
            snow_depth_max_cm=150.0,
            
            source_ids=[
                SOURCE_IDS["CWS"],
                SOURCE_IDS["SCIENCE"]
            ],
            confidence=0.88,
            notes="Climat côtier plus doux. Hibernation plus courte dans certaines régions."
        )
        
        # =====================================================================
        # WAPITI (ELK) — CALVING
        # =====================================================================
        
        # Wapiti - Alberta
        self._models["elk_CA-AB"] = CalvingPeriod(
            species="elk",
            region="CA-AB",
            birth_type=BirthType.CALVING,
            
            start_month=5, start_day=20,
            end_month=6, end_day=30,
            peak_month=6, peak_day=5,
            
            gestation_days=240,  # ~8 mois
            litter_size_avg=1.0,
            litter_size_range=(1, 1),  # Rarement jumeaux
            survival_rate_first_month=0.70,
            
            isolation_days_before=10,
            mother_calf_bond_weeks=40,
            activity_modifier=0.6,
            movement_modifier=0.4,
            vulnerability_modifier=0.55,
            
            preferred_sites=[
                BirthSitePreference.MEADOW_EDGE,
                BirthSitePreference.STEEP_SLOPE,
                BirthSitePreference.DENSE_COVER
            ],
            
            min_temp_celsius=5.0,
            max_temp_celsius=25.0,
            snow_depth_max_cm=5.0,
            
            source_ids=[
                SOURCE_IDS["RMEF"],
                SOURCE_IDS["CWS"],
                SOURCE_IDS["BOONE"]
            ],
            confidence=0.88,
            notes="Hardes se dispersent pour la mise bas. Femelles recherchent pentes abruptes "
                  "et lisières de prairies. Veaux peuvent suivre la mère après quelques heures."
        )
        
        # Wapiti - Colombie-Britannique
        self._models["elk_CA-BC"] = CalvingPeriod(
            species="elk",
            region="CA-BC",
            birth_type=BirthType.CALVING,
            
            start_month=5, start_day=25,
            end_month=7, end_day=5,
            peak_month=6, peak_day=10,
            
            gestation_days=242,
            litter_size_avg=1.0,
            litter_size_range=(1, 1),
            survival_rate_first_month=0.68,
            
            isolation_days_before=8,
            mother_calf_bond_weeks=38,
            activity_modifier=0.6,
            movement_modifier=0.45,
            vulnerability_modifier=0.55,
            
            preferred_sites=[
                BirthSitePreference.MEADOW_EDGE,
                BirthSitePreference.DENSE_COVER
            ],
            
            min_temp_celsius=8.0,
            max_temp_celsius=25.0,
            snow_depth_max_cm=0.0,
            
            source_ids=[
                SOURCE_IDS["RMEF"],
                SOURCE_IDS["CWS"]
            ],
            confidence=0.85,
            notes="Population de l'île de Vancouver a des patrons légèrement différents. "
                  "Pression des couguars sur les veaux nouveau-nés."
        )
    
    # =========================================================================
    # MÉTHODES PUBLIQUES
    # =========================================================================
    
    def get_model(self, species: str, region: str) -> Optional[CalvingPeriod]:
        """
        Récupère le modèle de mise bas pour une espèce et région.
        
        Args:
            species: Code espèce (moose, deer, bear, elk)
            region: Code région (CA-QC, CA-ON, US-ME, etc.)
            
        Returns:
            CalvingPeriod ou None si non trouvé
        """
        key = f"{species}_{region}"
        return self._models.get(key)
    
    def get_model_with_fallback(self, species: str, region: str) -> Optional[CalvingPeriod]:
        """
        Récupère le modèle avec fallback vers une région par défaut.
        
        Ordre de fallback:
        1. Région exacte demandée
        2. Région par défaut de l'espèce
        """
        # Essayer la région exacte
        model = self.get_model(species, region)
        if model:
            return model
        
        # Fallback vers région par défaut
        default_regions = {
            "moose": "CA-QC",
            "deer": "CA-QC",
            "bear": "CA-QC",
            "elk": "CA-AB"
        }
        
        default_region = default_regions.get(species)
        if default_region and default_region != region:
            logger.warning(f"[BIONIC] Calving model not found for {species}_{region}, "
                          f"using fallback {species}_{default_region}")
            return self.get_model(species, default_region)
        
        return None
    
    def is_calving_active(
        self, 
        species: str, 
        region: str, 
        check_date: date
    ) -> Tuple[bool, Optional[CalvingPeriod]]:
        """
        Vérifie si la période de mise bas est active.
        
        Returns:
            (is_active, model)
        """
        model = self.get_model_with_fallback(species, region)
        if not model:
            return False, None
        
        return model.is_active(check_date), model
    
    def get_calving_modifier(
        self, 
        species: str, 
        region: str, 
        check_date: date,
        modifier_type: str = "activity"
    ) -> float:
        """
        Récupère le modificateur approprié pour la période de mise bas.
        
        Args:
            modifier_type: "activity", "movement", ou "vulnerability"
            
        Returns:
            Modificateur (1.0 si hors période ou modèle non trouvé)
        """
        model = self.get_model_with_fallback(species, region)
        if not model or not model.is_active(check_date):
            return 1.0
        
        if modifier_type == "activity":
            return model.get_activity_score(check_date)
        elif modifier_type == "movement":
            return model.movement_modifier
        elif modifier_type == "vulnerability":
            return model.vulnerability_modifier
        
        return 1.0
    
    def get_all_species(self) -> List[str]:
        """Retourne la liste des espèces supportées."""
        return list(set(m.species for m in self._models.values()))
    
    def get_all_regions(self, species: str = None) -> List[str]:
        """Retourne la liste des régions supportées."""
        if species:
            return [m.region for m in self._models.values() if m.species == species]
        return list(set(m.region for m in self._models.values()))
    
    def export_all_models(self) -> Dict[str, Any]:
        """Exporte tous les modèles pour documentation/API."""
        return {
            key: model.to_dict() 
            for key, model in self._models.items()
        }


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_calving_registry: Optional[CalvingModelRegistry] = None


def get_calving_registry() -> CalvingModelRegistry:
    """Retourne l'instance singleton du registre de mise bas."""
    global _calving_registry
    if _calving_registry is None:
        _calving_registry = CalvingModelRegistry()
    return _calving_registry


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def calculate_birth_date_estimate(
    species: str,
    region: str,
    observation_date: date,
    calf_age_weeks: int
) -> date:
    """
    Estime la date de naissance d'un jeune observé.
    
    Args:
        species: Code espèce
        region: Code région
        observation_date: Date d'observation du jeune
        calf_age_weeks: Âge estimé en semaines
        
    Returns:
        Date de naissance estimée
    """
    birth_date = observation_date - timedelta(weeks=calf_age_weeks)
    
    # Valider que la date est dans la période de mise bas
    registry = get_calving_registry()
    model = registry.get_model_with_fallback(species, region)
    
    if model and not model.is_active(birth_date):
        logger.warning(f"[BIONIC] Estimated birth date {birth_date} is outside "
                      f"calving period for {species}_{region}")
    
    return birth_date


def get_expected_dispersal_window(
    species: str,
    region: str,
    birth_date: date
) -> Tuple[date, date]:
    """
    Calcule la fenêtre de dispersion attendue basée sur la date de naissance.
    
    Returns:
        (start_date, end_date) de la fenêtre de dispersion
    """
    # Délais de dispersion par espèce (en mois)
    dispersal_delays = {
        "moose": (10, 14),   # 10-14 mois
        "deer": (6, 12),     # 6-12 mois
        "bear": (16, 18),    # 16-18 mois (après 2e hiver)
        "elk": (10, 12)      # 10-12 mois
    }
    
    delay = dispersal_delays.get(species, (10, 14))
    
    start = birth_date + timedelta(days=delay[0] * 30)
    end = birth_date + timedelta(days=delay[1] * 30)
    
    return start, end
