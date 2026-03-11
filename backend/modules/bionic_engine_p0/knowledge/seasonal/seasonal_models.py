"""
BIONIC V5 — SEASONAL MODELS (Foundation Module)
=================================================
PHASE 7 — Knowledge Layer — Module de base saisonnier

Ce fichier est le MODULE FONDATION du système saisonnier.
Il fournit les types, énumérations et registres de base utilisés par
l'ensemble du moteur BIONIC V5.

EXPORTS CRITIQUES:
- SeasonType (Enum): Types de saisons comportementales
- SeasonalModel: Modèle saisonnier de base  
- SeasonalModelRegistry: Registre central des modèles
- get_seasonal_model(): Accès rapide au modèle saisonnier

MODULES PHASE C (extensions spécialisées):
- calving_models.py    → C.1 Mise bas (modèles avancés)
- juvenile_dispersion.py → C.2 Dispersion juvénile
- thermal_stress.py    → C.3 Stress thermique
- hunting_pressure.py  → C.4 Pression de chasse

NOTE: Ce fichier NE DOIT PAS être supprimé. Les modules C.1-C.4
      étendent ce module de base, ils ne le remplacent pas.

VERSION: 2.0.0-PHASE-C
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, date, timezone
from dateutil.relativedelta import relativedelta
from enum import Enum


class SeasonType(str, Enum):
    """Types de saisons comportementales"""
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"
    PRE_RUT = "pre_rut"
    RUT = "rut"
    POST_RUT = "post_rut"
    FAWNING = "fawning"           # Mise bas cerfs
    CALVING = "calving"           # Mise bas orignaux
    HUNTING_SEASON = "hunting_season"
    HYPERPHAGIA = "hyperphagia"   # Période d'alimentation intensive (ours)
    
    # PHASE C: Phénologie complète
    JUVENILE_DISPERSAL = "juvenile_dispersal"     # Dispersion juvénile
    SUMMER_THERMAL_STRESS = "summer_thermal_stress"  # Stress thermique été
    HUNTING_PRESSURE = "hunting_pressure"         # Pression de chasse réelle


@dataclass
class SeasonPeriod:
    """Période saisonnière avec dates et caractéristiques"""
    season_type: SeasonType
    start_month: int
    start_day: int
    end_month: int
    end_day: int
    
    # Caractéristiques
    activity_modifier: float = 1.0
    movement_modifier: float = 1.0
    feeding_modifier: float = 1.0
    vulnerability_modifier: float = 1.0
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=list)
    confidence: float = 0.5
    notes: str = ""
    
    def is_active(self, check_date: date) -> bool:
        """Vérifier si la saison est active pour une date donnée"""
        check_md = (check_date.month, check_date.day)
        start_md = (self.start_month, self.start_day)
        end_md = (self.end_month, self.end_day)
        
        # Gestion du cas où la période traverse le nouvel an
        if start_md <= end_md:
            return start_md <= check_md <= end_md
        else:
            return check_md >= start_md or check_md <= end_md


@dataclass
class JuvenileDispersalWindow:
    """
    PHASE C.1: Fenêtre de dispersion juvénile dynamique.
    
    Calculée dynamiquement à partir de la date de naissance.
    10-14 mois après naissance = période de dispersion des juvéniles.
    
    Conforme BIONIC V5:
    - Aucune date calendaire fixe
    - Calcul dynamique basé sur calving/fawning
    - Traçabilité complète
    """
    
    species_code: str
    region: str
    
    # Date de naissance de référence (du calving/fawning de l'année précédente)
    birth_date: date
    
    # Fenêtre dynamique calculée (10-14 mois après naissance)
    dispersal_start: date = None
    dispersal_end: date = None
    
    # Modificateurs comportementaux pendant la dispersion
    activity_modifier: float = 1.4       # Activité élevée des juvéniles
    movement_modifier: float = 2.0       # Mouvements erratiques et imprévisibles
    feeding_modifier: float = 1.2        # Recherche de nouvelles ressources
    vulnerability_modifier: float = 1.3  # Juvéniles plus vulnérables
    
    # Variance (caractéristique PHASE C: mouvements imprévisibles)
    movement_variance: float = 0.5       # 50% de variance dans les mouvements
    
    # Traçabilité
    source_ids: List[str] = field(default_factory=list)
    version: str = "2.0.0"
    confidence: float = 0.82
    
    def __post_init__(self):
        """Calcule automatiquement la fenêtre de dispersion à partir de birth_date."""
        if self.birth_date and not self.dispersal_start:
            self._calculate_dispersal_window()
    
    def _calculate_dispersal_window(self):
        """
        PHASE C.1: Calcul dynamique de la fenêtre 10-14 mois.
        
        Logique:
        - dispersal_start = birth_date + 10 mois
        - dispersal_end = birth_date + 14 mois
        """
        self.dispersal_start = self.birth_date + relativedelta(months=10)
        self.dispersal_end = self.birth_date + relativedelta(months=14)
    
    def is_active(self, check_date: date) -> bool:
        """
        Vérifie si la date est dans la fenêtre de dispersion dynamique.
        """
        if not self.dispersal_start or not self.dispersal_end:
            return False
        return self.dispersal_start <= check_date <= self.dispersal_end
    
    def get_modifiers(self) -> Dict[str, float]:
        """Retourne les modificateurs de la période de dispersion."""
        return {
            "activity": self.activity_modifier,
            "movement": self.movement_modifier,
            "feeding": self.feeding_modifier,
            "vulnerability": self.vulnerability_modifier,
            "movement_variance": self.movement_variance
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Sérialisation avec traçabilité complète."""
        return {
            "species_code": self.species_code,
            "region": self.region,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "dispersal_start": self.dispersal_start.isoformat() if self.dispersal_start else None,
            "dispersal_end": self.dispersal_end.isoformat() if self.dispersal_end else None,
            "modifiers": self.get_modifiers(),
            "source_ids": self.source_ids,
            "version": self.version,
            "confidence": self.confidence
        }


@dataclass
class SeasonalModel:
    """
    Modèle saisonnier complet pour une espèce.
    
    Définit toutes les périodes saisonnières avec leurs modificateurs
    comportementaux calibrés et sourcés.
    """
    
    species_code: str
    region: str = "CA-QC"
    
    # Périodes
    periods: Dict[SeasonType, SeasonPeriod] = field(default_factory=dict)
    
    # Métadonnées
    source_ids: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    last_calibrated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def get_current_season(self, check_date: date = None) -> Optional[SeasonType]:
        """Obtenir la saison active pour une date"""
        if check_date is None:
            check_date = date.today()
        
        # Priorité aux saisons spéciales (rut, fawning, etc.)
        # PHASE C: Ajout des nouvelles saisons avec priorité appropriée
        priority_seasons = [
            SeasonType.RUT,
            SeasonType.PRE_RUT,
            SeasonType.POST_RUT,
            SeasonType.FAWNING,
            SeasonType.CALVING,
            SeasonType.HYPERPHAGIA,
            SeasonType.HUNTING_PRESSURE,        # PHASE C: Pression de chasse réelle (haute priorité)
            SeasonType.HUNTING_SEASON,
            SeasonType.JUVENILE_DISPERSAL,      # PHASE C: Dispersion juvénile
            SeasonType.SUMMER_THERMAL_STRESS    # PHASE C: Stress thermique été
        ]
        
        for season_type in priority_seasons:
            period = self.periods.get(season_type)
            if period and period.is_active(check_date):
                return season_type
        
        # Sinon, retourner la saison calendaire
        for season_type in [SeasonType.SPRING, SeasonType.SUMMER, SeasonType.FALL, SeasonType.WINTER]:
            period = self.periods.get(season_type)
            if period and period.is_active(check_date):
                return season_type
        
        return None
    
    def get_modifiers(self, check_date: date = None) -> Dict[str, float]:
        """Obtenir les modificateurs comportementaux pour une date"""
        season_type = self.get_current_season(check_date)
        
        if not season_type or season_type not in self.periods:
            return {
                "activity": 1.0,
                "movement": 1.0,
                "feeding": 1.0,
                "vulnerability": 1.0
            }
        
        period = self.periods[season_type]
        return {
            "activity": period.activity_modifier,
            "movement": period.movement_modifier,
            "feeding": period.feeding_modifier,
            "vulnerability": period.vulnerability_modifier
        }
    
    def get_phase_c_modifiers(
        self, 
        check_date: date = None,
        temperature_c: float = None,
        hunting_pressure_detected: bool = False
    ) -> Dict[str, Any]:
        """
        PHASE C: Obtenir les modificateurs phénologiques avancés.
        
        Args:
            check_date: Date de vérification
            temperature_c: Température actuelle (optionnel)
            hunting_pressure_detected: Pression de chasse détectée (terrain)
            
        Returns:
            Dict avec modificateurs PHASE C et source_ids
        """
        if check_date is None:
            check_date = date.today()
        
        result = {
            "thermal_stress_active": False,
            "thermal_stress_modifier": 1.0,
            "juvenile_dispersal_active": False,
            "juvenile_dispersal_modifier": 1.0,
            "hunting_pressure_active": False,
            "hunting_pressure_modifier": 1.0,
            "source_ids": []
        }
        
        # Vérifier stress thermique
        thermal_period = self.periods.get(SeasonType.SUMMER_THERMAL_STRESS)
        if thermal_period and thermal_period.is_active(check_date):
            result["thermal_stress_active"] = True
            result["thermal_stress_modifier"] = thermal_period.activity_modifier
            result["source_ids"].extend(thermal_period.source_ids)
        
        # Vérifier dispersion juvénile
        dispersal_period = self.periods.get(SeasonType.JUVENILE_DISPERSAL)
        if dispersal_period and dispersal_period.is_active(check_date):
            result["juvenile_dispersal_active"] = True
            result["juvenile_dispersal_modifier"] = dispersal_period.movement_modifier
            result["source_ids"].extend(dispersal_period.source_ids)
        
        # Vérifier pression de chasse
        pressure_period = self.periods.get(SeasonType.HUNTING_PRESSURE)
        if pressure_period and pressure_period.is_active(check_date):
            # Amplifier si pression détectée par données terrain
            modifier = pressure_period.activity_modifier
            if hunting_pressure_detected:
                modifier *= 0.7  # Réduction supplémentaire
            result["hunting_pressure_active"] = True
            result["hunting_pressure_modifier"] = modifier
            result["source_ids"].extend(pressure_period.source_ids)
        
        return result
    
    def calculate_dynamic_dispersal_window(
        self,
        check_date: date = None,
        reference_year: int = None
    ) -> Optional[JuvenileDispersalWindow]:
        """
        PHASE C.1: Calcul dynamique de la fenêtre de dispersion juvénile.
        
        Logique BIONIC V5 (NON NÉGOCIABLE):
        - La dispersion se produit 10-14 mois APRÈS la naissance
        - La date de naissance est déterminée par la période calving/fawning
        - AUCUNE date calendaire fixe
        
        Args:
            check_date: Date de vérification (défaut: aujourd'hui)
            reference_year: Année de référence pour le calving (défaut: année précédente)
            
        Returns:
            JuvenileDispersalWindow avec fenêtre calculée dynamiquement
        """
        if check_date is None:
            check_date = date.today()
        
        if reference_year is None:
            # L'année de naissance est l'année précédente
            reference_year = check_date.year - 1
        
        # Obtenir la période de calving/fawning pour déterminer la date de naissance
        calving_period = self.periods.get(SeasonType.CALVING)
        fawning_period = self.periods.get(SeasonType.FAWNING)
        
        birth_period = calving_period or fawning_period
        
        if not birth_period:
            # Pas de période de naissance définie pour cette espèce
            return None
        
        # Date de naissance moyenne = milieu de la période calving/fawning
        birth_start = date(reference_year, birth_period.start_month, birth_period.start_day)
        birth_end = date(reference_year, birth_period.end_month, birth_period.end_day)
        birth_midpoint = birth_start + (birth_end - birth_start) / 2
        
        # Créer la fenêtre de dispersion dynamique (10-14 mois après naissance)
        dispersal_window = JuvenileDispersalWindow(
            species_code=self.species_code,
            region=self.region,
            birth_date=birth_midpoint,
            source_ids=birth_period.source_ids + ["SRC-DISPERSAL-DYNAMIC-001"],
            version="2.0.0",
            confidence=birth_period.confidence * 0.95  # Légère réduction pour le calcul
        )
        
        return dispersal_window
    
    def is_in_dynamic_dispersal(
        self,
        check_date: date = None,
        reference_year: int = None
    ) -> Tuple[bool, Optional[JuvenileDispersalWindow]]:
        """
        PHASE C.1: Vérifie si une date est dans la fenêtre de dispersion dynamique.
        
        Retourne:
        - (True, JuvenileDispersalWindow) si dans la fenêtre
        - (False, None) sinon
        """
        window = self.calculate_dynamic_dispersal_window(check_date, reference_year)
        
        if window and window.is_active(check_date):
            return True, window
        
        return False, window


class SeasonalModelRegistry:
    """Registre des modèles saisonniers par espèce et région"""
    
    def __init__(self):
        self._models: Dict[str, SeasonalModel] = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialiser les modèles saisonniers"""
        
        # =====================================================
        # ORIGNAL - QUÉBEC
        # =====================================================
        
        moose_qc = SeasonalModel(
            species_code="moose",
            region="CA-QC",
            source_ids=["SRC-LAVAL-001", "SRC-MFFP-001", "SRC-GAGNON-001"]
        )
        
        moose_qc.periods[SeasonType.SPRING] = SeasonPeriod(
            season_type=SeasonType.SPRING,
            start_month=4, start_day=15,
            end_month=5, end_day=31,
            activity_modifier=1.2,
            movement_modifier=1.3,
            feeding_modifier=1.4,
            vulnerability_modifier=0.8,
            source_ids=["SRC-LAVAL-001"],
            confidence=0.85,
            notes="Période de sortie d'hiver, recherche active de nourriture fraîche"
        )
        
        moose_qc.periods[SeasonType.SUMMER] = SeasonPeriod(
            season_type=SeasonType.SUMMER,
            start_month=6, start_day=1,
            end_month=8, end_day=31,
            activity_modifier=0.9,
            movement_modifier=0.8,
            feeding_modifier=1.0,
            vulnerability_modifier=0.7,
            source_ids=["SRC-LAVAL-001", "SRC-MFFP-001"],
            confidence=0.88,
            notes="Activité réduite aux heures fraîches, fréquentation des zones humides"
        )
        
        # PRE_RUT: 10 sept → 20 sept (Source: MFFP 2024, Laval 2023)
        moose_qc.periods[SeasonType.PRE_RUT] = SeasonPeriod(
            season_type=SeasonType.PRE_RUT,
            start_month=9, start_day=10,
            end_month=9, end_day=20,
            activity_modifier=1.3,
            movement_modifier=1.4,
            feeding_modifier=0.9,
            vulnerability_modifier=1.1,
            source_ids=["SRC-LAVAL-001", "SRC-MFFP-001", "SRC-GAGNON-001"],
            confidence=0.92,
            notes="Mâles commencent à marquer le territoire, frottoirs actifs"
        )
        
        # FULL_RUT: 21 sept → 10 oct (Source: MFFP 2024, Laval 2023, UQAR)
        moose_qc.periods[SeasonType.RUT] = SeasonPeriod(
            season_type=SeasonType.RUT,
            start_month=9, start_day=21,
            end_month=10, end_day=10,
            activity_modifier=1.8,
            movement_modifier=2.5,
            feeding_modifier=0.6,
            vulnerability_modifier=1.5,
            source_ids=["SRC-LAVAL-001", "SRC-MFFP-001", "SRC-GAGNON-001", "SRC-UQAR-001"],
            confidence=0.95,
            notes="Pic du rut - mâles très actifs et réactifs aux appels"
        )
        
        # POST_RUT: 11 oct → 25 oct (Source: MFFP 2024)
        moose_qc.periods[SeasonType.POST_RUT] = SeasonPeriod(
            season_type=SeasonType.POST_RUT,
            start_month=10, start_day=11,
            end_month=10, end_day=25,
            activity_modifier=1.1,
            movement_modifier=1.0,
            feeding_modifier=1.3,
            vulnerability_modifier=1.0,
            source_ids=["SRC-MFFP-001", "SRC-LAVAL-001"],
            confidence=0.88,
            notes="Mâles épuisés, reprise de l'alimentation intensive"
        )
        
        moose_qc.periods[SeasonType.FALL] = SeasonPeriod(
            season_type=SeasonType.FALL,
            start_month=10, start_day=26,
            end_month=11, end_day=30,
            activity_modifier=1.0,
            movement_modifier=0.9,
            feeding_modifier=1.4,
            vulnerability_modifier=0.9,
            source_ids=["SRC-MFFP-001"],
            confidence=0.82,
            notes="Constitution des réserves pour l'hiver"
        )
        
        moose_qc.periods[SeasonType.WINTER] = SeasonPeriod(
            season_type=SeasonType.WINTER,
            start_month=12, start_day=1,
            end_month=4, end_day=14,
            activity_modifier=0.7,
            movement_modifier=0.5,
            feeding_modifier=0.8,
            vulnerability_modifier=0.6,
            source_ids=["SRC-LAVAL-001", "SRC-MFFP-001"],
            confidence=0.88,
            notes="Activité réduite, regroupement dans les ravages"
        )
        
        moose_qc.periods[SeasonType.CALVING] = SeasonPeriod(
            season_type=SeasonType.CALVING,
            start_month=5, start_day=15,
            end_month=6, end_day=15,
            activity_modifier=0.8,
            movement_modifier=0.6,
            feeding_modifier=1.1,
            vulnerability_modifier=0.5,
            source_ids=["SRC-LAVAL-001"],
            confidence=0.85,
            notes="Femelles isolées avec veaux, très discrètes"
        )
        
        # =====================================================
        # PHASE C: MODÈLES SAISONNIERS AVANCÉS - ORIGNAL
        # =====================================================
        
        # Dispersion juvénile (10-14 mois après naissance = mai de l'année suivante)
        moose_qc.periods[SeasonType.JUVENILE_DISPERSAL] = SeasonPeriod(
            season_type=SeasonType.JUVENILE_DISPERSAL,
            start_month=5, start_day=1,
            end_month=7, end_day=15,
            activity_modifier=1.4,              # Activité accrue des juvéniles
            movement_modifier=2.0,              # Mouvements imprévisibles, erratiques
            feeding_modifier=1.1,
            vulnerability_modifier=1.3,         # Juvéniles plus vulnérables
            source_ids=["SRC-LAVAL-001", "SRC-MFFP-001", "SRC-HABITAT-001"],
            confidence=0.82,
            notes="PHASE C: Dispersion des juvéniles 10-14 mois après naissance. Mouvements erratiques et imprévisibles. "
                  "Jeunes mâles quittent le territoire maternel. Variance de mobilité élevée."
        )
        
        # Stress thermique été (>25°C pour orignal)
        moose_qc.periods[SeasonType.SUMMER_THERMAL_STRESS] = SeasonPeriod(
            season_type=SeasonType.SUMMER_THERMAL_STRESS,
            start_month=7, start_day=1,
            end_month=8, end_day=20,
            activity_modifier=0.5,              # Activité réduite significativement
            movement_modifier=0.4,              # Déplacements limités
            feeding_modifier=0.7,               # Alimentation réduite
            vulnerability_modifier=0.6,         # Recherche refuges thermiques
            source_ids=["SRC-LAVAL-001", "SRC-MFFP-001", "SRC-THERM-001"],
            confidence=0.88,
            notes="PHASE C: Stress thermique >25°C. Recherche refuges thermiques (zones humides, sous-bois). "
                  "Activité diurne minimale, shift vers nocturne. Seuil critique: 30°C."
        )
        
        # Pression de chasse réelle (basée sur données terrain MFFP)
        moose_qc.periods[SeasonType.HUNTING_PRESSURE] = SeasonPeriod(
            season_type=SeasonType.HUNTING_PRESSURE,
            start_month=9, start_day=13,        # Début saison orignal QC
            end_month=11, end_day=15,           # Fin saison
            activity_modifier=0.6,              # Réduction activité diurne
            movement_modifier=0.5,              # Déplacements réduits
            feeding_modifier=0.7,
            vulnerability_modifier=0.4,         # Évitement zones de pression
            source_ids=["SRC-MFFP-001", "SRC-TERRAIN-001", "SRC-GPS-HUNT-001"],
            confidence=0.90,
            notes="PHASE C: Pression de chasse réelle. Zones d'évitement dynamiques basées sur: "
                  "caméras terrain, GPS chasseurs, traces humaines. Shift comportement nocturne."
        )
        
        self._models["moose_CA-QC"] = moose_qc
        
        # =====================================================
        # CERF DE VIRGINIE - QUÉBEC
        # =====================================================
        
        deer_qc = SeasonalModel(
            species_code="deer",
            region="CA-QC",
            source_ids=["SRC-MFFP-001", "SRC-NDA-001"]
        )
        
        deer_qc.periods[SeasonType.SPRING] = SeasonPeriod(
            season_type=SeasonType.SPRING,
            start_month=4, start_day=1,
            end_month=5, end_day=14,
            activity_modifier=1.2,
            movement_modifier=1.3,
            feeding_modifier=1.3,
            vulnerability_modifier=0.9,
            source_ids=["SRC-NDA-001"],
            confidence=0.85
        )
        
        deer_qc.periods[SeasonType.FAWNING] = SeasonPeriod(
            season_type=SeasonType.FAWNING,
            start_month=5, start_day=15,
            end_month=6, end_day=30,
            activity_modifier=0.9,
            movement_modifier=0.7,
            feeding_modifier=1.1,
            vulnerability_modifier=0.6,
            source_ids=["SRC-NDA-001", "SRC-MFFP-001"],
            confidence=0.88,
            notes="Femelles avec faons, comportement très discret"
        )
        
        deer_qc.periods[SeasonType.SUMMER] = SeasonPeriod(
            season_type=SeasonType.SUMMER,
            start_month=7, start_day=1,
            end_month=9, end_day=30,
            activity_modifier=0.9,
            movement_modifier=0.8,
            feeding_modifier=1.0,
            vulnerability_modifier=0.8,
            source_ids=["SRC-NDA-001"],
            confidence=0.85
        )
        
        deer_qc.periods[SeasonType.PRE_RUT] = SeasonPeriod(
            season_type=SeasonType.PRE_RUT,
            start_month=10, start_day=20,
            end_month=11, end_day=4,
            activity_modifier=1.4,
            movement_modifier=1.5,
            feeding_modifier=1.2,
            vulnerability_modifier=1.2,
            source_ids=["SRC-NDA-001", "SRC-WHS-001"],
            confidence=0.92,
            notes="Création des grattages et frottoirs"
        )
        
        deer_qc.periods[SeasonType.RUT] = SeasonPeriod(
            season_type=SeasonType.RUT,
            start_month=11, start_day=5,
            end_month=11, end_day=20,
            activity_modifier=2.0,
            movement_modifier=3.0,
            feeding_modifier=0.5,
            vulnerability_modifier=1.6,
            source_ids=["SRC-NDA-001", "SRC-WHS-001", "SRC-MFFP-001"],
            confidence=0.96,
            notes="Pic du rut - activité diurne maximale des mâles"
        )
        
        deer_qc.periods[SeasonType.POST_RUT] = SeasonPeriod(
            season_type=SeasonType.POST_RUT,
            start_month=11, start_day=21,
            end_month=12, end_day=10,
            activity_modifier=0.8,
            movement_modifier=0.7,
            feeding_modifier=1.4,
            vulnerability_modifier=0.9,
            source_ids=["SRC-NDA-001"],
            confidence=0.85
        )
        
        deer_qc.periods[SeasonType.WINTER] = SeasonPeriod(
            season_type=SeasonType.WINTER,
            start_month=12, start_day=11,
            end_month=3, end_day=31,
            activity_modifier=0.6,
            movement_modifier=0.4,
            feeding_modifier=0.7,
            vulnerability_modifier=0.5,
            source_ids=["SRC-MFFP-001", "SRC-NDA-001"],
            confidence=0.88,
            notes="Ravages d'hiver, déplacements limités"
        )
        
        deer_qc.periods[SeasonType.HUNTING_SEASON] = SeasonPeriod(
            season_type=SeasonType.HUNTING_SEASON,
            start_month=11, start_day=1,
            end_month=11, end_day=30,
            activity_modifier=0.7,
            movement_modifier=0.6,
            feeding_modifier=0.8,
            vulnerability_modifier=0.5,
            source_ids=["SRC-NDA-001", "SRC-STATE-001"],
            confidence=0.90,
            notes="Shift vers comportement nocturne sous pression"
        )
        
        # =====================================================
        # PHASE C: MODÈLES SAISONNIERS AVANCÉS - CERF
        # =====================================================
        
        # Dispersion juvénile (12-14 mois après naissance = juin de l'année suivante)
        deer_qc.periods[SeasonType.JUVENILE_DISPERSAL] = SeasonPeriod(
            season_type=SeasonType.JUVENILE_DISPERSAL,
            start_month=5, start_day=15,
            end_month=7, end_day=31,
            activity_modifier=1.5,              # Activité très élevée des juvéniles
            movement_modifier=2.2,              # Mouvements erratiques
            feeding_modifier=1.2,
            vulnerability_modifier=1.4,         # Juvéniles très vulnérables
            source_ids=["SRC-NDA-001", "SRC-MFFP-001", "SRC-QDMA-001"],
            confidence=0.85,
            notes="PHASE C: Dispersion des faons mâles 12-14 mois après naissance. "
                  "Mouvements imprévisibles jusqu'à établissement nouveau territoire."
        )
        
        # Stress thermique été (>30°C pour cerf)
        deer_qc.periods[SeasonType.SUMMER_THERMAL_STRESS] = SeasonPeriod(
            season_type=SeasonType.SUMMER_THERMAL_STRESS,
            start_month=7, start_day=10,
            end_month=8, end_day=25,
            activity_modifier=0.6,              # Activité réduite
            movement_modifier=0.5,              # Déplacements limités
            feeding_modifier=0.8,
            vulnerability_modifier=0.7,
            source_ids=["SRC-NDA-001", "SRC-THERM-001"],
            confidence=0.82,
            notes="PHASE C: Stress thermique >30°C. Recherche refuges (zones boisées ombragées). "
                  "Activité crépusculaire/nocturne. Seuil critique: 35°C."
        )
        
        # Pression de chasse réelle
        deer_qc.periods[SeasonType.HUNTING_PRESSURE] = SeasonPeriod(
            season_type=SeasonType.HUNTING_PRESSURE,
            start_month=11, start_day=1,
            end_month=11, end_day=30,
            activity_modifier=0.5,              # Forte réduction activité diurne
            movement_modifier=0.4,              # Déplacements très réduits
            feeding_modifier=0.6,
            vulnerability_modifier=0.3,         # Évitement maximal
            source_ids=["SRC-NDA-001", "SRC-TERRAIN-001", "SRC-GPS-HUNT-001"],
            confidence=0.92,
            notes="PHASE C: Pression de chasse réelle intense (saison carabine). "
                  "Cerfs matures deviennent pratiquement nocturnes. Zones d'évitement dynamiques."
        )
        
        self._models["deer_CA-QC"] = deer_qc
        
        # =====================================================
        # OURS NOIR - QUÉBEC
        # =====================================================
        
        bear_qc = SeasonalModel(
            species_code="bear",
            region="CA-QC",
            source_ids=["SRC-MFFP-001", "SRC-PARCS-001"]
        )
        
        bear_qc.periods[SeasonType.SPRING] = SeasonPeriod(
            season_type=SeasonType.SPRING,
            start_month=4, start_day=15,
            end_month=6, end_day=15,
            activity_modifier=1.3,
            movement_modifier=1.4,
            feeding_modifier=1.2,
            vulnerability_modifier=1.0,
            source_ids=["SRC-MFFP-001", "SRC-PARCS-001"],
            confidence=0.88,
            notes="Sortie de tanière, recherche de nourriture"
        )
        
        bear_qc.periods[SeasonType.SUMMER] = SeasonPeriod(
            season_type=SeasonType.SUMMER,
            start_month=6, start_day=16,
            end_month=8, end_day=14,
            activity_modifier=1.0,
            movement_modifier=1.0,
            feeding_modifier=1.0,
            vulnerability_modifier=0.9,
            source_ids=["SRC-MFFP-001"],
            confidence=0.85
        )
        
        bear_qc.periods[SeasonType.HYPERPHAGIA] = SeasonPeriod(
            season_type=SeasonType.HYPERPHAGIA,
            start_month=8, start_day=15,
            end_month=11, end_day=1,
            activity_modifier=1.5,
            movement_modifier=1.3,
            feeding_modifier=2.0,
            vulnerability_modifier=1.2,
            source_ids=["SRC-MFFP-001", "SRC-USGS-001"],
            confidence=0.93,
            notes="Alimentation intensive - jusqu'à 20h/jour"
        )
        
        bear_qc.periods[SeasonType.WINTER] = SeasonPeriod(
            season_type=SeasonType.WINTER,
            start_month=11, start_day=2,
            end_month=4, end_day=14,
            activity_modifier=0.0,
            movement_modifier=0.0,
            feeding_modifier=0.0,
            vulnerability_modifier=0.0,
            source_ids=["SRC-MFFP-001"],
            confidence=0.95,
            notes="Hibernation"
        )
        
        self._models["bear_CA-QC"] = bear_qc
        
        # =====================================================
        # WAPITI - OUEST / ALBERTA
        # =====================================================
        
        elk_ab = SeasonalModel(
            species_code="elk",
            region="CA-AB",
            source_ids=["SRC-USGS-001", "SRC-RMEF-001"]
        )
        
        elk_ab.periods[SeasonType.SPRING] = SeasonPeriod(
            season_type=SeasonType.SPRING,
            start_month=4, start_day=1,
            end_month=5, end_day=31,
            activity_modifier=1.2,
            movement_modifier=1.3,
            feeding_modifier=1.4,
            vulnerability_modifier=0.8,
            source_ids=["SRC-USGS-001"],
            confidence=0.85,
            notes="Migration vers les zones d'estivage"
        )
        
        elk_ab.periods[SeasonType.SUMMER] = SeasonPeriod(
            season_type=SeasonType.SUMMER,
            start_month=6, start_day=1,
            end_month=8, end_day=31,
            activity_modifier=0.9,
            movement_modifier=0.8,
            feeding_modifier=1.0,
            vulnerability_modifier=0.7,
            source_ids=["SRC-USGS-001", "SRC-RMEF-001"],
            confidence=0.88
        )
        
        # PRE_RUT Wapiti: 1 sept → 10 sept
        elk_ab.periods[SeasonType.PRE_RUT] = SeasonPeriod(
            season_type=SeasonType.PRE_RUT,
            start_month=9, start_day=1,
            end_month=9, end_day=10,
            activity_modifier=1.4,
            movement_modifier=1.5,
            feeding_modifier=0.9,
            vulnerability_modifier=1.2,
            source_ids=["SRC-RMEF-001", "SRC-USGS-001"],
            confidence=0.90,
            notes="Bugling commence, mâles rassemblent les harems"
        )
        
        # FULL_RUT Wapiti: 11 sept → 30 sept
        elk_ab.periods[SeasonType.RUT] = SeasonPeriod(
            season_type=SeasonType.RUT,
            start_month=9, start_day=11,
            end_month=9, end_day=30,
            activity_modifier=2.0,
            movement_modifier=2.8,
            feeding_modifier=0.5,
            vulnerability_modifier=1.6,
            source_ids=["SRC-RMEF-001", "SRC-USGS-001"],
            confidence=0.95,
            notes="Pic du rut - bugling intense, combats entre mâles"
        )
        
        # POST_RUT Wapiti: 1 oct → 15 oct
        elk_ab.periods[SeasonType.POST_RUT] = SeasonPeriod(
            season_type=SeasonType.POST_RUT,
            start_month=10, start_day=1,
            end_month=10, end_day=15,
            activity_modifier=1.0,
            movement_modifier=0.9,
            feeding_modifier=1.3,
            vulnerability_modifier=0.9,
            source_ids=["SRC-RMEF-001"],
            confidence=0.85,
            notes="Harems se dispersent, alimentation intensive"
        )
        
        elk_ab.periods[SeasonType.FALL] = SeasonPeriod(
            season_type=SeasonType.FALL,
            start_month=10, start_day=16,
            end_month=11, end_day=30,
            activity_modifier=1.0,
            movement_modifier=1.0,
            feeding_modifier=1.4,
            vulnerability_modifier=0.9,
            source_ids=["SRC-USGS-001"],
            confidence=0.82
        )
        
        elk_ab.periods[SeasonType.WINTER] = SeasonPeriod(
            season_type=SeasonType.WINTER,
            start_month=12, start_day=1,
            end_month=3, end_day=31,
            activity_modifier=0.6,
            movement_modifier=0.5,
            feeding_modifier=0.7,
            vulnerability_modifier=0.6,
            source_ids=["SRC-USGS-001", "SRC-RMEF-001"],
            confidence=0.88,
            notes="Migration vers les aires d'hivernage"
        )
        
        elk_ab.periods[SeasonType.CALVING] = SeasonPeriod(
            season_type=SeasonType.CALVING,
            start_month=5, start_day=15,
            end_month=6, end_day=15,
            activity_modifier=0.8,
            movement_modifier=0.6,
            feeding_modifier=1.1,
            vulnerability_modifier=0.5,
            source_ids=["SRC-RMEF-001"],
            confidence=0.85
        )
        
        self._models["elk_CA-AB"] = elk_ab
        
        # =====================================================
        # CERF-MULET - OUEST / BRITISH COLUMBIA
        # =====================================================
        
        mule_deer_bc = SeasonalModel(
            species_code="mule_deer",
            region="CA-BC",
            source_ids=["SRC-USGS-001", "SRC-BCWF-001"]
        )
        
        mule_deer_bc.periods[SeasonType.SPRING] = SeasonPeriod(
            season_type=SeasonType.SPRING,
            start_month=4, start_day=1,
            end_month=5, end_day=31,
            activity_modifier=1.2,
            movement_modifier=1.3,
            feeding_modifier=1.3,
            vulnerability_modifier=0.9,
            source_ids=["SRC-USGS-001"],
            confidence=0.85
        )
        
        mule_deer_bc.periods[SeasonType.SUMMER] = SeasonPeriod(
            season_type=SeasonType.SUMMER,
            start_month=6, start_day=1,
            end_month=10, end_day=31,
            activity_modifier=0.9,
            movement_modifier=0.8,
            feeding_modifier=1.0,
            vulnerability_modifier=0.8,
            source_ids=["SRC-USGS-001"],
            confidence=0.85
        )
        
        # PRE_RUT Cerf-mulet: 1 nov → 10 nov
        mule_deer_bc.periods[SeasonType.PRE_RUT] = SeasonPeriod(
            season_type=SeasonType.PRE_RUT,
            start_month=11, start_day=1,
            end_month=11, end_day=10,
            activity_modifier=1.4,
            movement_modifier=1.5,
            feeding_modifier=1.2,
            vulnerability_modifier=1.2,
            source_ids=["SRC-USGS-001", "SRC-BCWF-001"],
            confidence=0.90,
            notes="Mâles deviennent plus actifs, marquage territorial"
        )
        
        # FULL_RUT Cerf-mulet: 11 nov → 25 nov
        mule_deer_bc.periods[SeasonType.RUT] = SeasonPeriod(
            season_type=SeasonType.RUT,
            start_month=11, start_day=11,
            end_month=11, end_day=25,
            activity_modifier=1.8,
            movement_modifier=2.5,
            feeding_modifier=0.5,
            vulnerability_modifier=1.5,
            source_ids=["SRC-USGS-001", "SRC-BCWF-001"],
            confidence=0.94,
            notes="Pic du rut - déplacements erratiques des mâles"
        )
        
        # POST_RUT Cerf-mulet: 26 nov → 10 déc
        mule_deer_bc.periods[SeasonType.POST_RUT] = SeasonPeriod(
            season_type=SeasonType.POST_RUT,
            start_month=11, start_day=26,
            end_month=12, end_day=10,
            activity_modifier=0.9,
            movement_modifier=0.8,
            feeding_modifier=1.3,
            vulnerability_modifier=0.9,
            source_ids=["SRC-BCWF-001"],
            confidence=0.85
        )
        
        mule_deer_bc.periods[SeasonType.WINTER] = SeasonPeriod(
            season_type=SeasonType.WINTER,
            start_month=12, start_day=11,
            end_month=3, end_day=31,
            activity_modifier=0.6,
            movement_modifier=0.5,
            feeding_modifier=0.7,
            vulnerability_modifier=0.5,
            source_ids=["SRC-USGS-001", "SRC-BCWF-001"],
            confidence=0.88,
            notes="Regroupement hivernal, déplacements limités"
        )
        
        mule_deer_bc.periods[SeasonType.FAWNING] = SeasonPeriod(
            season_type=SeasonType.FAWNING,
            start_month=5, start_day=15,
            end_month=6, end_day=30,
            activity_modifier=0.9,
            movement_modifier=0.7,
            feeding_modifier=1.1,
            vulnerability_modifier=0.6,
            source_ids=["SRC-BCWF-001"],
            confidence=0.88
        )
        
        self._models["mule_deer_CA-BC"] = mule_deer_bc
    
    def get_rut_period(self, species: str, region: str = "CA-QC", rut_phase: str = "rut") -> Optional[SeasonPeriod]:
        """
        Obtenir la période de rut spécifique pour une espèce.
        
        Args:
            species: Nom de l'espèce
            region: Région
            rut_phase: 'pre_rut', 'rut', ou 'post_rut'
        
        Returns:
            SeasonPeriod ou None
        """
        model = self.get(species, region)
        if not model:
            return None
        
        phase_map = {
            "pre_rut": SeasonType.PRE_RUT,
            "rut": SeasonType.RUT,
            "full_rut": SeasonType.RUT,
            "post_rut": SeasonType.POST_RUT
        }
        
        season_type = phase_map.get(rut_phase.lower())
        if not season_type:
            return None
        
        return model.periods.get(season_type)
    
    def get_all_rut_periods(self, species: str, region: str = "CA-QC") -> Dict[str, SeasonPeriod]:
        """Obtenir toutes les périodes de rut pour une espèce"""
        model = self.get(species, region)
        if not model:
            return {}
        
        result = {}
        for phase in [SeasonType.PRE_RUT, SeasonType.RUT, SeasonType.POST_RUT]:
            period = model.periods.get(phase)
            if period:
                result[phase.value] = period
        
        # Pour l'ours, retourner l'hyperphagie
        if "bear" in species.lower() or "ours" in species.lower():
            hyperphagia = model.periods.get(SeasonType.HYPERPHAGIA)
            if hyperphagia:
                result["hyperphagia"] = hyperphagia
        
        return result
    
    def get(self, species: str, region: str = "CA-QC") -> Optional[SeasonalModel]:
        """Obtenir le modèle saisonnier pour une espèce et région"""
        # Normalize species name
        species_normalized = species.lower().strip()
        species_map = {
            "orignal": "moose",
            "cerf de virginie": "deer",
            "cerf": "deer",
            "ours noir": "bear",
            "ours": "bear",
            "wapiti": "elk"
        }
        species_code = species_map.get(species_normalized, species_normalized)
        
        key = f"{species_code}_{region}"
        return self._models.get(key)
    
    def get_all_species(self) -> List[str]:
        """Obtenir la liste des espèces disponibles"""
        return list(set(key.split("_")[0] for key in self._models.keys()))


# Singleton
_registry_instance: Optional[SeasonalModelRegistry] = None


def get_seasonal_model(species: str, region: str = "CA-QC") -> Optional[SeasonalModel]:
    """Obtenir le modèle saisonnier pour une espèce"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = SeasonalModelRegistry()
    return _registry_instance.get(species, region)


__all__ = [
    'SeasonType',
    'SeasonPeriod',
    'SeasonalModel',
    'SeasonalModelRegistry',
    'get_seasonal_model'
]
