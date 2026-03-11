"""
BIONIC ENGINE — Heatmap Fusion Service
=======================================
Service de fusion pour la Heatmap Unifiée BIONIC V5 ULTIME.

RESPONSABILITÉ UNIQUE:
- Fusionner WQS (structure) avec SCORE_FINAL (dynamique)
- Intégrer les scores de densité, pression, mobilité, risques
- Appliquer les contraintes légales
- Produire une HeatmapUnifieeResult standardisée

SOURCES DE DONNÉES:
- WQS: Score de qualité structurelle du waypoint (40%)
- SCORE_FINAL: Score dynamique unifié des 9 services (60%)
- Sous-scores extraits: densité, pression, mobilité, risques

ISOLATION:
- Aucun calcul interne des scores (appel uniquement)
- Aucun import transversal non autorisé
- Waypoint-centric obligatoire
- Aucune modification des services existants

INPUTS:
- HeatmapFusionContext (waypoint + WQS + paramètres)

OUTPUTS:
- HeatmapUnifieeResult (grille unifiée + métadonnées)

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

import logging
import math
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field

# Import du service de scoring unifié
from modules.bionic_engine_p0.services.unified_scoring_service import (
    get_unified_scoring_service,
    UnifiedScoreResult
)

# Import des services de scoring pour les catégories
from modules.bionic_engine_p0.services.scoring import (
    ScoreContext,
    ScoreCategory,
    ScoreLevel
)

# Import du service des heures légales
from modules.bionic_engine_p0.services.legal_hours_service import (
    get_legal_hours_service,
    LegalHuntingWindow
)

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

# Pondérations de fusion WQS/SCORE_FINAL
WQS_WEIGHT = 0.40       # 40% structurel
SCORE_FINAL_WEIGHT = 0.60  # 60% dynamique

# Couleurs de la heatmap par niveau
HEATMAP_COLORS = {
    ScoreLevel.EXCELLENT: {"color": "#FFD700", "opacity": 0.9, "label": "Excellent"},
    ScoreLevel.GOOD: {"color": "#22C55E", "opacity": 0.8, "label": "Bon"},
    ScoreLevel.MODERATE: {"color": "#F59E0B", "opacity": 0.7, "label": "Modéré"},
    ScoreLevel.POOR: {"color": "#F97316", "opacity": 0.6, "label": "Faible"},
    ScoreLevel.VERY_POOR: {"color": "#EF4444", "opacity": 0.5, "label": "Très faible"}
}


# =============================================================================
# DATA CONTRACTS
# =============================================================================

@dataclass
class WQSInput:
    """
    Données WQS en entrée (score structurel).
    
    Le WQS est fourni en entrée, non calculé par ce service.
    """
    waypoint_id: str
    wqs_score: float           # 0-100
    success_history: float     # 0-100
    weather_correlation: float # 0-100
    activity_history: float    # 0-100
    accessibility: float       # 0-100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "waypoint_id": self.waypoint_id,
            "wqs_score": round(self.wqs_score, 1),
            "components": {
                "success_history": round(self.success_history, 1),
                "weather_correlation": round(self.weather_correlation, 1),
                "activity_history": round(self.activity_history, 1),
                "accessibility": round(self.accessibility, 1)
            }
        }


@dataclass
class HeatmapFusionContext:
    """
    Contexte d'entrée pour la fusion heatmap.
    
    Combine le contexte de scoring avec les données WQS.
    """
    # Waypoint de référence (obligatoire)
    waypoint_id: str
    latitude: float
    longitude: float
    
    # Temporel
    target_datetime: datetime
    
    # Espèce cible
    species: str
    
    # Données WQS (fournies en entrée)
    wqs_input: WQSInput
    
    # Paramètres de grille
    grid_radius_km: float = 3.0    # Rayon de la grille
    grid_resolution: int = 10      # Nombre de cellules par côté
    
    # Région
    region: str = "CA-QC"
    
    def to_score_context(self) -> ScoreContext:
        """Convertit en ScoreContext pour les services de scoring."""
        return ScoreContext(
            waypoint_id=self.waypoint_id,
            latitude=self.latitude,
            longitude=self.longitude,
            target_datetime=self.target_datetime,
            species=self.species,
            region=self.region,
            search_radius_km=self.grid_radius_km
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "waypoint_id": self.waypoint_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "target_datetime": self.target_datetime.isoformat(),
            "species": self.species,
            "wqs_input": self.wqs_input.to_dict(),
            "grid_radius_km": self.grid_radius_km,
            "grid_resolution": self.grid_resolution,
            "region": self.region
        }


@dataclass
class HeatmapCell:
    """
    Cellule individuelle de la heatmap.
    """
    # Position
    row: int
    col: int
    center_lat: float
    center_lng: float
    
    # Score fusionné
    fused_score: float         # 0-100
    level: ScoreLevel
    
    # Composants du score fusionné
    wqs_contribution: float    # WQS × 0.40
    score_final_contribution: float  # SCORE_FINAL × 0.60
    
    # Sous-scores extraits (pour analyse)
    density_score: float
    pressure_score: float
    mobility_score: float
    risk_score: float
    
    # Style visuel
    color: str
    opacity: float
    
    # Conformité légale
    is_legal_period: bool
    legal_badge: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": {"row": self.row, "col": self.col},
            "coordinates": {"lat": round(self.center_lat, 6), "lng": round(self.center_lng, 6)},
            "fused_score": round(self.fused_score, 1),
            "level": self.level.value,
            "contributions": {
                "wqs": round(self.wqs_contribution, 1),
                "score_final": round(self.score_final_contribution, 1)
            },
            "sub_scores": {
                "density": round(self.density_score, 1),
                "pressure": round(self.pressure_score, 1),
                "mobility": round(self.mobility_score, 1),
                "risk": round(self.risk_score, 1)
            },
            "style": {"color": self.color, "opacity": self.opacity},
            "legal": {"is_legal": self.is_legal_period, "badge": self.legal_badge}
        }


@dataclass
class HeatmapStatistics:
    """
    Statistiques de la heatmap.
    """
    total_cells: int
    cells_excellent: int
    cells_good: int
    cells_moderate: int
    cells_poor: int
    cells_very_poor: int
    
    average_score: float
    median_score: float
    min_score: float
    max_score: float
    std_deviation: float
    
    # Centres de gravité
    hotspot_center_lat: float   # Centre des cellules > 70
    hotspot_center_lng: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_cells": self.total_cells,
            "distribution": {
                "excellent": self.cells_excellent,
                "good": self.cells_good,
                "moderate": self.cells_moderate,
                "poor": self.cells_poor,
                "very_poor": self.cells_very_poor
            },
            "statistics": {
                "average": round(self.average_score, 1),
                "median": round(self.median_score, 1),
                "min": round(self.min_score, 1),
                "max": round(self.max_score, 1),
                "std_deviation": round(self.std_deviation, 2)
            },
            "hotspot_center": {
                "lat": round(self.hotspot_center_lat, 6),
                "lng": round(self.hotspot_center_lng, 6)
            }
        }


@dataclass
class HeatmapUnifieeResult:
    """
    Résultat de la fusion heatmap unifiée BIONIC.
    """
    # Identification
    heatmap_id: str
    calculated_at: datetime
    
    # Grille de cellules
    cells: List[HeatmapCell]
    grid_bounds: Dict[str, float]  # north, south, east, west
    
    # Score central (waypoint de référence)
    central_fused_score: float
    central_level: ScoreLevel
    
    # Scores sources
    wqs_score: float
    score_final: float
    
    # Statistiques
    statistics: HeatmapStatistics
    
    # Fenêtre légale
    legal_window: Optional[LegalHuntingWindow]
    
    # Contexte d'entrée
    context: HeatmapFusionContext
    
    # Métadonnées
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "heatmap_id": self.heatmap_id,
            "calculated_at": self.calculated_at.isoformat(),
            "central_score": {
                "fused_score": round(self.central_fused_score, 1),
                "level": self.central_level.value,
                "wqs_contribution": round(self.wqs_score * WQS_WEIGHT, 1),
                "score_final_contribution": round(self.score_final * SCORE_FINAL_WEIGHT, 1)
            },
            "sources": {
                "wqs_score": round(self.wqs_score, 1),
                "score_final": round(self.score_final, 1),
                "wqs_weight": WQS_WEIGHT,
                "score_final_weight": SCORE_FINAL_WEIGHT
            },
            "grid": {
                "bounds": self.grid_bounds,
                "cells_count": len(self.cells),
                "resolution": self.context.grid_resolution
            },
            "cells": [c.to_dict() for c in self.cells],
            "statistics": self.statistics.to_dict(),
            "legal_window": self.legal_window.to_dict() if self.legal_window else None,
            "context": self.context.to_dict(),
            "metadata": self.metadata
        }
    
    @staticmethod
    def get_level_from_value(value: float) -> ScoreLevel:
        """Détermine le niveau qualitatif à partir de la valeur."""
        if value >= 85:
            return ScoreLevel.EXCELLENT
        elif value >= 70:
            return ScoreLevel.GOOD
        elif value >= 50:
            return ScoreLevel.MODERATE
        elif value >= 30:
            return ScoreLevel.POOR
        else:
            return ScoreLevel.VERY_POOR


# =============================================================================
# HEATMAP FUSION SERVICE
# =============================================================================

class HeatmapFusionService:
    """
    Service de fusion pour la Heatmap Unifiée BIONIC V5 ULTIME.
    
    RESPONSABILITÉ:
    - Appeler UnifiedScoringService pour obtenir le SCORE_FINAL
    - Fusionner avec le WQS fourni en entrée (40% WQS + 60% SCORE_FINAL)
    - Générer une grille de cellules autour du waypoint
    - Calculer les statistiques de la heatmap
    - Appliquer les contraintes légales
    
    ISOLATION:
    - N'effectue AUCUN calcul interne des scores
    - Appelle uniquement les services via leurs interfaces publiques
    - Ne modifie pas les services existants
    """
    
    def __init__(self):
        """Initialise le service."""
        self._unified_scoring_service = get_unified_scoring_service()
        self._legal_hours_service = get_legal_hours_service()
        self._heatmap_counter = 0
        
        logger.info("HeatmapFusionService initialized")
    
    def _generate_heatmap_id(self) -> str:
        """Génère un ID unique pour la heatmap."""
        self._heatmap_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"HM-{timestamp}-{self._heatmap_counter:04d}"
    
    def calculate_fused_heatmap(
        self, 
        context: HeatmapFusionContext
    ) -> HeatmapUnifieeResult:
        """
        Calcule la heatmap fusionnée unifiée.
        
        PROCESSUS:
        1. Calculer le SCORE_FINAL via UnifiedScoringService
        2. Fusionner avec WQS (40% WQS + 60% SCORE_FINAL)
        3. Générer la grille de cellules
        4. Calculer les statistiques
        5. Appliquer les contraintes légales
        6. Produire le HeatmapUnifieeResult
        
        Args:
            context: Contexte de fusion (waypoint + WQS + paramètres)
            
        Returns:
            HeatmapUnifieeResult avec grille et statistiques
        """
        start_time = datetime.now(timezone.utc)
        heatmap_id = self._generate_heatmap_id()
        
        logger.info(f"[{heatmap_id}] Starting heatmap fusion")
        logger.debug(f"[{heatmap_id}] Waypoint: {context.waypoint_id}, WQS: {context.wqs_input.wqs_score}")
        
        # ==== ÉTAPE 1: Calculer le SCORE_FINAL ====
        score_context = context.to_score_context()
        unified_result = self._unified_scoring_service.calculate_unified_score(score_context)
        score_final = unified_result.final_score
        
        logger.info(f"[{heatmap_id}] SCORE_FINAL: {score_final:.1f}")
        
        # ==== ÉTAPE 2: Extraire les sous-scores ====
        sub_scores = self._extract_sub_scores(unified_result)
        
        # ==== ÉTAPE 3: Calculer le score fusionné central ====
        wqs_score = context.wqs_input.wqs_score
        central_fused = self._calculate_fused_score(wqs_score, score_final)
        central_level = HeatmapUnifieeResult.get_level_from_value(central_fused)
        
        logger.info(f"[{heatmap_id}] Central fused score: {central_fused:.1f}")
        
        # ==== ÉTAPE 4: Obtenir la fenêtre légale ====
        legal_window = self._legal_hours_service.get_legal_hunting_window(
            latitude=context.latitude,
            longitude=context.longitude,
            target_date=context.target_datetime.date(),
            region=context.region
        )
        
        # Vérifier conformité légale
        legal_check = self._legal_hours_service.check_legal_status(
            target_time=context.target_datetime,
            latitude=context.latitude,
            longitude=context.longitude,
            region=context.region
        )
        
        # ==== ÉTAPE 5: Générer la grille ====
        cells, grid_bounds = self._generate_grid(
            context=context,
            central_fused=central_fused,
            wqs_score=wqs_score,
            score_final=score_final,
            sub_scores=sub_scores,
            is_legal=legal_check.is_legal
        )
        
        # ==== ÉTAPE 6: Calculer les statistiques ====
        statistics = self._calculate_statistics(cells)
        
        # ==== ÉTAPE 7: Construire le résultat ====
        calc_time_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        result = HeatmapUnifieeResult(
            heatmap_id=heatmap_id,
            calculated_at=datetime.now(timezone.utc),
            cells=cells,
            grid_bounds=grid_bounds,
            central_fused_score=central_fused,
            central_level=central_level,
            wqs_score=wqs_score,
            score_final=score_final,
            statistics=statistics,
            legal_window=legal_window,
            context=context,
            metadata={
                "calculation_time_ms": round(calc_time_ms, 1),
                "wqs_weight": WQS_WEIGHT,
                "score_final_weight": SCORE_FINAL_WEIGHT,
                "unified_score_id": unified_result.score_id,
                "is_legal_period": legal_check.is_legal,
                "version": "BIONIC-V5-ULTIME-HEATMAP-1.0"
            }
        )
        
        logger.info(f"[{heatmap_id}] Heatmap fusion completed in {calc_time_ms:.0f}ms")
        
        return result
    
    def _calculate_fused_score(self, wqs: float, score_final: float) -> float:
        """
        Calcule le score fusionné.
        
        Formule: FUSED = WQS × 0.40 + SCORE_FINAL × 0.60
        """
        return (wqs * WQS_WEIGHT) + (score_final * SCORE_FINAL_WEIGHT)
    
    def _extract_sub_scores(self, unified_result: UnifiedScoreResult) -> Dict[str, float]:
        """Extrait les sous-scores pertinents du résultat unifié."""
        sub_scores = {
            "density": 50.0,
            "pressure": 50.0,
            "mobility": 50.0,
            "risk": 50.0
        }
        
        for breakdown in unified_result.score_breakdown:
            if breakdown.category == ScoreCategory.DENSITY:
                sub_scores["density"] = breakdown.raw_value
            elif breakdown.category == ScoreCategory.PRESSURE:
                sub_scores["pressure"] = breakdown.raw_value
            elif breakdown.category == ScoreCategory.MOBILITY:
                sub_scores["mobility"] = breakdown.raw_value
            elif breakdown.category == ScoreCategory.RISK:
                sub_scores["risk"] = breakdown.raw_value
        
        return sub_scores
    
    def _generate_grid(
        self,
        context: HeatmapFusionContext,
        central_fused: float,
        wqs_score: float,
        score_final: float,
        sub_scores: Dict[str, float],
        is_legal: bool
    ) -> Tuple[List[HeatmapCell], Dict[str, float]]:
        """
        Génère la grille de cellules autour du waypoint.
        
        La grille est centrée sur le waypoint avec un rayon et une résolution définis.
        """
        cells = []
        resolution = context.grid_resolution
        radius_km = context.grid_radius_km
        
        # Calculer les bornes de la grille
        # 1 degré latitude ≈ 111 km
        # 1 degré longitude ≈ 111 km × cos(latitude)
        lat_deg_per_km = 1 / 111.0
        lng_deg_per_km = 1 / (111.0 * math.cos(math.radians(context.latitude)))
        
        half_size_lat = radius_km * lat_deg_per_km
        half_size_lng = radius_km * lng_deg_per_km
        
        grid_bounds = {
            "north": context.latitude + half_size_lat,
            "south": context.latitude - half_size_lat,
            "east": context.longitude + half_size_lng,
            "west": context.longitude - half_size_lng
        }
        
        # Taille de chaque cellule
        cell_height = (2 * half_size_lat) / resolution
        cell_width = (2 * half_size_lng) / resolution
        
        # Badge légal
        legal_badge = "⚖️ LÉGAL" if is_legal else "❌ HORS HEURES LÉGALES"
        
        # Générer les cellules
        for row in range(resolution):
            for col in range(resolution):
                # Centre de la cellule
                cell_lat = grid_bounds["south"] + (row + 0.5) * cell_height
                cell_lng = grid_bounds["west"] + (col + 0.5) * cell_width
                
                # Distance au centre (waypoint)
                dist_lat = abs(cell_lat - context.latitude)
                dist_lng = abs(cell_lng - context.longitude)
                distance_km = math.sqrt(
                    (dist_lat / lat_deg_per_km) ** 2 + 
                    (dist_lng / lng_deg_per_km) ** 2
                )
                
                # Atténuation du score avec la distance
                # Score diminue de ~10% par km
                distance_factor = max(0.5, 1 - (distance_km * 0.1))
                
                # Score fusionné de la cellule
                cell_fused = central_fused * distance_factor
                
                # Si hors heures légales, score = 0
                if not is_legal:
                    cell_fused = 0
                
                cell_level = HeatmapUnifieeResult.get_level_from_value(cell_fused)
                color_info = HEATMAP_COLORS[cell_level]
                
                cell = HeatmapCell(
                    row=row,
                    col=col,
                    center_lat=cell_lat,
                    center_lng=cell_lng,
                    fused_score=cell_fused,
                    level=cell_level,
                    wqs_contribution=wqs_score * WQS_WEIGHT * distance_factor,
                    score_final_contribution=score_final * SCORE_FINAL_WEIGHT * distance_factor,
                    density_score=sub_scores["density"] * distance_factor,
                    pressure_score=sub_scores["pressure"] * distance_factor,
                    mobility_score=sub_scores["mobility"] * distance_factor,
                    risk_score=sub_scores["risk"] * distance_factor,
                    color=color_info["color"],
                    opacity=color_info["opacity"],
                    is_legal_period=is_legal,
                    legal_badge=legal_badge
                )
                cells.append(cell)
        
        return cells, grid_bounds
    
    def _calculate_statistics(self, cells: List[HeatmapCell]) -> HeatmapStatistics:
        """Calcule les statistiques de la heatmap."""
        if not cells:
            return HeatmapStatistics(
                total_cells=0,
                cells_excellent=0, cells_good=0, cells_moderate=0,
                cells_poor=0, cells_very_poor=0,
                average_score=0, median_score=0, min_score=0, max_score=0,
                std_deviation=0, hotspot_center_lat=0, hotspot_center_lng=0
            )
        
        scores = [c.fused_score for c in cells]
        
        # Comptage par niveau
        levels_count = {level: 0 for level in ScoreLevel}
        for cell in cells:
            levels_count[cell.level] += 1
        
        # Statistiques de base
        avg = sum(scores) / len(scores)
        sorted_scores = sorted(scores)
        median = sorted_scores[len(sorted_scores) // 2]
        
        # Écart-type
        variance = sum((s - avg) ** 2 for s in scores) / len(scores)
        std_dev = math.sqrt(variance)
        
        # Centre de gravité des hotspots (score > 70)
        hotspot_cells = [c for c in cells if c.fused_score >= 70]
        if hotspot_cells:
            hotspot_lat = sum(c.center_lat for c in hotspot_cells) / len(hotspot_cells)
            hotspot_lng = sum(c.center_lng for c in hotspot_cells) / len(hotspot_cells)
        else:
            # Si pas de hotspots, utiliser le centre
            hotspot_lat = sum(c.center_lat for c in cells) / len(cells)
            hotspot_lng = sum(c.center_lng for c in cells) / len(cells)
        
        return HeatmapStatistics(
            total_cells=len(cells),
            cells_excellent=levels_count[ScoreLevel.EXCELLENT],
            cells_good=levels_count[ScoreLevel.GOOD],
            cells_moderate=levels_count[ScoreLevel.MODERATE],
            cells_poor=levels_count[ScoreLevel.POOR],
            cells_very_poor=levels_count[ScoreLevel.VERY_POOR],
            average_score=avg,
            median_score=median,
            min_score=min(scores),
            max_score=max(scores),
            std_deviation=std_dev,
            hotspot_center_lat=hotspot_lat,
            hotspot_center_lng=hotspot_lng
        )


# =============================================================================
# SINGLETON
# =============================================================================

_heatmap_fusion_service: Optional[HeatmapFusionService] = None


def get_heatmap_fusion_service() -> HeatmapFusionService:
    """Retourne l'instance singleton du service."""
    global _heatmap_fusion_service
    if _heatmap_fusion_service is None:
        _heatmap_fusion_service = HeatmapFusionService()
    return _heatmap_fusion_service


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'HeatmapFusionService',
    'get_heatmap_fusion_service',
    'HeatmapUnifieeResult',
    'HeatmapCell',
    'HeatmapStatistics',
    'HeatmapFusionContext',
    'WQSInput',
    'WQS_WEIGHT',
    'SCORE_FINAL_WEIGHT',
    'HEATMAP_COLORS'
]
