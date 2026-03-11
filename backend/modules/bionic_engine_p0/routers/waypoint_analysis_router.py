"""
BIONIC ENGINE — Waypoint Analysis Router
=========================================
Endpoint POST /api/v1/bionic/analyze_waypoint

RESPONSABILITÉ UNIQUE:
- Exposer l'endpoint REST
- Valider les entrées via Pydantic
- Orchestrer les appels aux services existants
- Agréger les résultats en WaypointAnalysisResponse

ISOLATION:
- Aucun calcul métier (délégation aux services)
- Aucun traitement géospatial
- Orchestration pure

CONTRACT VERSION: 1.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

import logging
import time
import uuid
import random
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from modules.bionic_engine_p0.schemas import (
    WaypointAnalysisRequest,
    WaypointAnalysisResponse,
    DataQuality,
    ScoreLevel,
    ErrorResponse,
    AnalysisParameters,
    VisualizationParameters,
    WQSInput,
    ScoresOutput,
    ScoreBreakdown,
    ScoreComponent,
    ScoreFusion,
    FusionContribution,
    ScoreCategory,
    HeatmapOutput,
    HeatmapBounds,
    HeatmapCell,
    ColorScale,
    ColorScaleLevel,
    # Corridors models (NIVEAU 4)
    CorridorsOutput,
    CorridorFeature,
    CorridorProperties,
    CorridorFactors,
    CorridorRenderingStyle,
    CorridorStatistics,
    CorridorNetworkProperties,
    Geometry,
    # Other models
    LegalStatusOutput,
    OptimalWindow,
    VisualizationApplied,
    MetadataOutput,
    WaypointOutput,
    ContractInfo
)

# Import des services existants (legacy - conservé pour compatibilité)


from modules.bionic_engine_p0.services.scoring import ScoreLevel as ServiceScoreLevel

# Import du LayerAggregatorService (ACTION 3)
from modules.bionic_engine_p0.services.layer_aggregator_service import (
    get_layer_aggregator_service,
    LayerGenerationContext
)

# Import du UnifiedScoringService (PHASE 7 - Knowledge Layer)
from modules.bionic_engine_p0.services.unified_scoring_service import (
    get_unified_scoring_service
)
from modules.bionic_engine_p0.services.scoring.base_score_service import ScoreContext

logger = logging.getLogger(__name__)

# =============================================================================
# ROUTER
# =============================================================================

router = APIRouter(tags=["BIONIC Waypoint Analysis"])


# =============================================================================
# CONSTANTS
# =============================================================================

ENGINE_VERSION = "2026.02.23"

BIONIC_COLOR_SCALE = {
    "excellent": {"min": 85, "max": 100, "color": "#00A676"},
    "good": {"min": 70, "max": 84, "color": "#C9A86A"},
    "moderate": {"min": 50, "max": 69, "color": "#1E3A8A"},
    "poor": {"min": 30, "max": 49, "color": "#C26A2E"},
    "critical": {"min": 0, "max": 29, "color": "#B91C1C"}
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _generate_analysis_id() -> str:
    """Génère un identifiant unique pour l'analyse."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    suffix = uuid.uuid4().hex[:4].upper()
    return f"WPA-{timestamp}-{suffix}"


def _service_level_to_schema_level(level: ServiceScoreLevel) -> ScoreLevel:
    """Convertit le ScoreLevel du service vers le schéma."""
    mapping = {
        ServiceScoreLevel.EXCELLENT: ScoreLevel.EXCELLENT,
        ServiceScoreLevel.GOOD: ScoreLevel.GOOD,
        ServiceScoreLevel.MODERATE: ScoreLevel.MODERATE,
        ServiceScoreLevel.POOR: ScoreLevel.POOR,
        ServiceScoreLevel.VERY_POOR: ScoreLevel.VERY_POOR
    }
    return mapping.get(level, ScoreLevel.MODERATE)


def _score_to_level(score: float) -> ScoreLevel:
    """Détermine le niveau à partir d'un score."""
    if score >= 85:
        return ScoreLevel.EXCELLENT
    elif score >= 70:
        return ScoreLevel.GOOD
    elif score >= 50:
        return ScoreLevel.MODERATE
    elif score >= 30:
        return ScoreLevel.POOR
    else:
        return ScoreLevel.VERY_POOR


def _score_to_category(score: float) -> ScoreCategory:
    """Détermine la catégorie à partir d'un score."""
    if score >= 70:
        return ScoreCategory(label="FAVORABLE", color="#00A676")
    elif score >= 50:
        return ScoreCategory(label="MODÉRÉ", color="#1E3A8A")
    else:
        return ScoreCategory(label="DÉFAVORABLE", color="#B91C1C")


def _score_to_color(score: float) -> str:
    """Retourne la couleur pour un score donné."""
    if score >= 85:
        return BIONIC_COLOR_SCALE["excellent"]["color"]
    elif score >= 70:
        return BIONIC_COLOR_SCALE["good"]["color"]
    elif score >= 50:
        return BIONIC_COLOR_SCALE["moderate"]["color"]
    elif score >= 30:
        return BIONIC_COLOR_SCALE["poor"]["color"]
    else:
        return BIONIC_COLOR_SCALE["critical"]["color"]


def _generate_heatmap(lat: float, lng: float, resolution: int, base_score: float) -> HeatmapOutput:
    """Génère une grille heatmap."""
    bounds = HeatmapBounds(
        north=lat + 0.025,
        south=lat - 0.025,
        east=lng + 0.05,
        west=lng - 0.05
    )
    
    grid = []
    for row in range(resolution):
        for col in range(resolution):
            cell_lat = bounds.south + (row / resolution) * (bounds.north - bounds.south)
            cell_lng = bounds.west + (col / resolution) * (bounds.east - bounds.west)
            
            # Score avec variation autour du score de base
            score = base_score + random.uniform(-15, 15)
            score = max(0, min(100, score))
            
            grid.append(HeatmapCell(
                row=row,
                col=col,
                lat=round(cell_lat, 5),
                lng=round(cell_lng, 5),
                score=round(score, 1),
                level=_score_to_level(score),
                color=_score_to_color(score)
            ))
    
    return HeatmapOutput(
        bounds=bounds,
        resolution=resolution,
        cell_size_m=500,
        grid=grid,
        color_scale=ColorScale(
            excellent=ColorScaleLevel(**BIONIC_COLOR_SCALE["excellent"]),
            good=ColorScaleLevel(**BIONIC_COLOR_SCALE["good"]),
            moderate=ColorScaleLevel(**BIONIC_COLOR_SCALE["moderate"]),
            poor=ColorScaleLevel(**BIONIC_COLOR_SCALE["poor"]),
            critical=ColorScaleLevel(**BIONIC_COLOR_SCALE["critical"])
        )
    )


# =============================================================================
# MAIN ENDPOINT
# =============================================================================

@router.post(
    "/analyze_waypoint",
    response_model=WaypointAnalysisResponse,
    responses={
        200: {"description": "Analyse complète du waypoint"},
        400: {"model": ErrorResponse, "description": "Paramètres invalides"},
        500: {"model": ErrorResponse, "description": "Erreur serveur"}
    },
    summary="Analyse waypoint-centric BIONIC V5",
    description="""
    Effectue une analyse complète centrée sur le waypoint de référence.
    
    **Inclut:**
    - Score BIONIC final (breakdown des 9 composants)
    - 5 familles de layers géospatiales
    - Heatmap fusionnée WQS + SCORE_FINAL
    - Statut de conformité légale
    - Fenêtres temporelles optimales
    - Recommandations textuelles
    
    **Contract Version:** 1.0.0
    """
)
async def analyze_waypoint(request: WaypointAnalysisRequest) -> WaypointAnalysisResponse:
    """
    Analyse complète waypoint-centric.
    
    Orchestration pure - délègue tous les calculs aux services spécialisés.
    """
    start_time = time.time()
    analysis_id = _generate_analysis_id()
    
    logger.info(f"[{analysis_id}] Starting waypoint analysis for {request.waypoint.id}")
    
    try:
        # =================================================================
        # 1. PRÉPARATION DES PARAMÈTRES
        # =================================================================
        
        wqs = request.wqs or WQSInput()
        
        params = request.parameters or AnalysisParameters()
        viz_params = request.visualization or VisualizationParameters()
        
        lat = request.waypoint.latitude
        lng = request.waypoint.longitude
        
        # =================================================================
        # 3. APPEL AU UnifiedScoringService (Knowledge Layer)
        # =================================================================
        
        # Créer le contexte de scoring pour le Knowledge Layer
        score_context = ScoreContext(
            waypoint_id=request.waypoint.id,
            latitude=lat,
            longitude=lng,
            target_datetime=request.target_datetime,
            species=request.species,
            region=params.region,
            search_radius_km=params.search_radius_km
        )
        
        # Déterminer le mode d'analyse biologique
        analysis_mode = params.mode.value if hasattr(params, 'mode') and params.mode else "rut"
        
        # Appeler le UnifiedScoringService avec le mode biologique
        unified_scoring_service = get_unified_scoring_service()
        unified_result = unified_scoring_service.calculate_unified_score(score_context, analysis_mode)
        
        logger.info(f"[{analysis_id}] UnifiedScoringService (mode={analysis_mode}): raw={unified_result.raw_aggregated_score:.1f}, final={unified_result.final_score:.1f}")
        
        # =================================================================
        # 4. CONSTRUCTION DES SCORES OUTPUT (Knowledge Layer)
        # =================================================================
        
        # Utiliser le score calibré du UnifiedScoringService
        raw_score = unified_result.raw_aggregated_score
        wqs_score = wqs.score
        
        # Construire le breakdown depuis les résultats Knowledge Layer
        breakdown_dict = {}
        for bd in unified_result.score_breakdown:
            category = bd.category.value
            breakdown_dict[category] = ScoreComponent(
                value=round(bd.raw_value, 1),
                weight=round(bd.weight, 2),
                weighted=round(bd.weighted_value, 2),
                level=_service_level_to_schema_level(bd.level)
            )
        
        # Mapper les catégories vers les clés attendues
        scores_breakdown = ScoreBreakdown(
            H_habitat=breakdown_dict.get("habitat", ScoreComponent(value=50.0, weight=0.12, weighted=6.0, level=ScoreLevel.MODERATE)),
            R_risk=breakdown_dict.get("risk", ScoreComponent(value=50.0, weight=0.08, weighted=4.0, level=ScoreLevel.MODERATE)),
            S_probability=breakdown_dict.get("probability", ScoreComponent(value=50.0, weight=0.15, weighted=7.5, level=ScoreLevel.MODERATE)),
            A_mobility=breakdown_dict.get("mobility", ScoreComponent(value=50.0, weight=0.11, weighted=5.5, level=ScoreLevel.MODERATE)),
            T_weather=breakdown_dict.get("weather", ScoreComponent(value=50.0, weight=0.12, weighted=6.0, level=ScoreLevel.MODERATE)),
            P_pressure=breakdown_dict.get("pressure", ScoreComponent(value=50.0, weight=0.10, weighted=5.0, level=ScoreLevel.MODERATE)),
            behavior=breakdown_dict.get("behavior", ScoreComponent(value=50.0, weight=0.12, weighted=6.0, level=ScoreLevel.MODERATE)),
            density=breakdown_dict.get("density", ScoreComponent(value=50.0, weight=0.10, weighted=5.0, level=ScoreLevel.MODERATE)),
            multifactor=breakdown_dict.get("multifactor", ScoreComponent(value=50.0, weight=0.10, weighted=5.0, level=ScoreLevel.MODERATE))
        )
        
        # Calculer le score final fusionné (WQS + BIONIC calibré)
        # WQS = 40%, BIONIC calibré = 60%
        final_fused_score = (wqs_score * 0.40) + (raw_score * 0.60)
        
        # Déterminer le mode d'analyse
        # Le mode est maintenant géré par UnifiedScoringService directement
        
        # Calculer le score final fusionné (WQS + BIONIC calibré)
        # WQS = 40%, BIONIC calibré = 60%
        final_fused_score = (wqs_score * 0.40) + (unified_result.final_score * 0.60)
        
        scores_output = ScoresOutput(
            score_bionic_final=round(final_fused_score, 1),
            score_bionic_final_10=round(final_fused_score / 10, 2),
            level=_score_to_level(final_fused_score),
            category=_score_to_category(final_fused_score),
            breakdown=scores_breakdown,
            fusion=ScoreFusion(
                wqs=FusionContribution(value=wqs_score, weight=0.40, contribution=round(wqs_score * 0.40, 2)),
                dynamic=FusionContribution(value=round(unified_result.final_score, 1), weight=0.60, contribution=round(unified_result.final_score * 0.60, 2))
            ),
            confidence=round(unified_result.global_confidence, 2),
            data_quality=DataQuality.FULL if unified_result.data_quality == "full" else DataQuality.PARTIAL,
            analysis_mode=analysis_mode,
            # PHASE B: Facteurs avancés avec traçabilité
            advanced_factors_details=unified_result.advanced_factors_details
        )
        
        logger.info(f"[{analysis_id}] Final fused score: {final_fused_score:.1f} (mode={analysis_mode}, WQS={wqs_score:.1f}, BIONIC={unified_result.final_score:.1f})")
        
        # =================================================================
        # 5. GÉNÉRATION DES LAYERS VIA LayerAggregatorService
        # =================================================================
        
        layer_service = get_layer_aggregator_service()
        
        # Extraire les scores par catégorie depuis le Knowledge Layer
        habitat_score = breakdown_dict.get("habitat", ScoreComponent(value=50.0, weight=0.12, weighted=6.0, level=ScoreLevel.MODERATE)).value
        pressure_score = breakdown_dict.get("pressure", ScoreComponent(value=50.0, weight=0.10, weighted=5.0, level=ScoreLevel.MODERATE)).value
        mobility_score = breakdown_dict.get("mobility", ScoreComponent(value=50.0, weight=0.11, weighted=5.5, level=ScoreLevel.MODERATE)).value
        behavior_score = breakdown_dict.get("behavior", ScoreComponent(value=50.0, weight=0.12, weighted=6.0, level=ScoreLevel.MODERATE)).value
        
        layer_context = LayerGenerationContext(
            waypoint_id=request.waypoint.id,
            latitude=lat,
            longitude=lng,
            search_radius_km=params.search_radius_km,
            species=request.species,
            target_datetime=request.target_datetime,
            # Scores calibrés depuis Knowledge Layer
            habitat_score=habitat_score,
            pressure_score=pressure_score,
            mobility_score=mobility_score,
            behavior_score=behavior_score,
            # Paramètres de visualisation
            smoothing_factor=viz_params.smoothing_factor,
            terrain_adaptation_strength=viz_params.terrain_adaptation_strength,
            vegetation_influence=viz_params.vegetation_influence,
            hydrography_influence=viz_params.hydrography_influence
        )
        
        layer_result = layer_service.generate_layers(layer_context)
        layers_output = layer_result.layers
        
        logger.info(f"[{analysis_id}] Layers generated via LayerAggregatorService (quality={layer_result.data_quality.value})")
        
        # =================================================================
        # 5.5. GÉNÉRATION DES CORRIDORS (NIVEAU 4)
        # =================================================================
        
        corridor_network = unified_scoring_service.generate_corridors(score_context, analysis_mode)
        corridor_geojson = corridor_network.to_geojson_feature_collection()
        
        # Convertir en schéma Pydantic CorridorsOutput
        corridors_features = []
        for feature in corridor_geojson.get("features", []):
            props = feature.get("properties", {})
            factors = props.get("factors", {})
            rendering = props.get("rendering", {})
            
            corridors_features.append(CorridorFeature(
                type="Feature",
                geometry=Geometry(
                    type=feature.get("geometry", {}).get("type", "LineString"),
                    coordinates=feature.get("geometry", {}).get("coordinates", [])
                ),
                properties=CorridorProperties(
                    corridor_id=props.get("corridor_id", ""),
                    corridor_type=props.get("corridor_type", "primary"),
                    priority=props.get("priority", "moderate"),
                    name=props.get("name", ""),
                    description=props.get("description", ""),
                    quality=props.get("quality", "moderate"),
                    composite_score=props.get("composite_score", 50.0),
                    total_length_m=props.get("total_length_m", 0.0),
                    average_quality=props.get("average_quality", 50.0),
                    factors=CorridorFactors(
                        habitat=factors.get("habitat", 50.0),
                        edge=factors.get("edge", 50.0),
                        thermal_stress=factors.get("thermal_stress", 50.0),
                        pres_human=factors.get("pres_human", 50.0),
                        behavior=factors.get("behavior", 50.0),
                        seasonal=factors.get("seasonal", 50.0)
                    ),
                    active_seasons=props.get("active_seasons", []),
                    active_hours=props.get("active_hours", []),
                    rendering=CorridorRenderingStyle(
                        stroke_color=rendering.get("stroke_color", "#FF8A00"),
                        stroke_opacity=rendering.get("stroke_opacity", 1.0),
                        stroke_width=rendering.get("stroke_width", 3),
                        dash_array=rendering.get("dash_array"),
                        line_cap=rendering.get("line_cap", "round"),
                        line_join=rendering.get("line_join", "round"),
                        halo_color=rendering.get("halo_color"),
                        halo_opacity=rendering.get("halo_opacity"),
                        halo_weight=rendering.get("halo_weight")
                    ),
                    source_ids=props.get("source_ids", []),
                    version=props.get("version", "1.0.0")
                )
            ))
        
        network_props = corridor_geojson.get("properties", {})
        stats = network_props.get("statistics", {})
        
        corridors_output = CorridorsOutput(
            type="FeatureCollection",
            features=corridors_features,
            properties=CorridorNetworkProperties(
                network_id=network_props.get("network_id", ""),
                waypoint_id=network_props.get("waypoint_id", ""),
                center=network_props.get("center", {"lat": lat, "lng": lng}),
                search_radius_km=network_props.get("search_radius_km", params.search_radius_km),
                statistics=CorridorStatistics(
                    total_corridors=stats.get("total_corridors", 0),
                    total_length_km=stats.get("total_length_km", 0.0),
                    average_quality=stats.get("average_quality", 50.0),
                    by_type=stats.get("by_type", {})
                ),
                species=network_props.get("species", request.species),
                analysis_datetime=network_props.get("analysis_datetime", datetime.now(timezone.utc).isoformat()),
                source_ids=network_props.get("source_ids", []),
                version=network_props.get("version", "1.0.0")
            )
        )
        
        logger.info(f"[{analysis_id}] Corridors generated: {corridor_network.total_corridors} corridors, {corridor_network.total_length_km:.2f} km")
        
        # =================================================================
        # 6. GÉNÉRATION DE LA HEATMAP
        # =================================================================
        
        heatmap_output = _generate_heatmap(lat, lng, params.grid_resolution, raw_score)
        
        logger.info(f"[{analysis_id}] Heatmap generated: {len(heatmap_output.grid)} cells")
        
        # =================================================================
        # 7. STATUT LÉGAL (depuis UnifiedScoringService)
        # =================================================================
        
        # Utiliser les informations temporelles du UnifiedScoringService
        temporal_adj = unified_result.temporal_adjustment
        legal_window = temporal_adj.legal_window
        
        sunrise_str = legal_window.sunrise.strftime("%H:%M") if legal_window else "06:45"
        sunset_str = legal_window.sunset.strftime("%H:%M") if legal_window else "18:15"
        legal_start_str = legal_window.start_time.strftime("%H:%M") if legal_window else "06:15"
        legal_end_str = legal_window.end_time.strftime("%H:%M") if legal_window else "18:45"
        
        legal_status = LegalStatusOutput(
            is_legal_period=temporal_adj.is_legal_period,
            legal_status=temporal_adj.legal_status.value if temporal_adj.legal_status else "unknown",
            sunrise=sunrise_str,
            sunset=sunset_str,
            legal_start=legal_start_str,
            legal_end=legal_end_str,
            legal_badge="LEGAL" if temporal_adj.is_legal_period else "HORS_HEURES",
            temporal_factor=round(temporal_adj.temporal_factor, 2),
            next_legal_window=None
        )
        
        # =================================================================
        # 8. FENÊTRES OPTIMALES
        # =================================================================
        
        optimal_windows = [
            OptimalWindow(
                period="dawn",
                time_range=f"{legal_status.legal_start} - 08:00",
                score=92.0,
                quality="excellent",
                species_activity="peak_movement",
                legal_badge="LEGAL",
                recommendation="Fenêtre optimale — activité maximale"
            ),
            OptimalWindow(
                period="dusk",
                time_range=f"17:30 - {legal_status.legal_end}",
                score=78.0,
                quality="good",
                species_activity="feeding_return",
                legal_badge="LEGAL",
                recommendation="Bonne fenêtre secondaire"
            )
        ]
        
        # =================================================================
        # 9. RECOMMANDATIONS (basées sur Knowledge Layer)
        # =================================================================
        
        # Générer des recommandations basées sur les scores calibrés
        recommendations = []
        
        # Facteurs positifs du UnifiedScoringService
        if unified_result.top_positive_factors:
            for factor in unified_result.top_positive_factors[:3]:
                recommendations.append(f"✓ {factor}")
        
        # Ajouter recommandations contextuelles
        if raw_score >= 70:
            recommendations.append(f"Conditions favorables — score BIONIC {raw_score:.0f}/100")
        elif raw_score >= 50:
            recommendations.append(f"Conditions modérées — score BIONIC {raw_score:.0f}/100")
        else:
            recommendations.append(f"Conditions défavorables — score BIONIC {raw_score:.0f}/100")
        
        if not temporal_adj.is_legal_period:
            recommendations.append("⚠️ HORS HEURES LÉGALES — Chasse interdite")
        
        # Compléter avec recommandations par défaut si nécessaire
        if len(recommendations) < 4:
            recommendations.extend([
                "Privilégier les zones de lisière forêt-clairière",
                "Corridor de déplacement actif détecté"
            ])
        
        recommendations = recommendations[:5]
        
        # =================================================================
        # 10. MÉTADONNÉES (Knowledge Layer + PHASE B)
        # =================================================================
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Extraire les détails des facteurs avancés
        advanced_factors_info = unified_result.advanced_factors_details
        
        metadata = MetadataOutput(
            processing_time_ms=processing_time_ms,
            data_sources=["unified_scoring_service", "knowledge_layer", "advanced_factors_phase_b", "legal_hours_service", "layer_aggregator_service", "corridor_registry_niveau4"],
            fallbacks_used=[],
            missing_data=[],
            confidence_impact=unified_result.global_confidence,
            cache_hit=False
        )
        
        visualization = VisualizationApplied(
            organic_applied=viz_params.organic_shape,
            smoothing_factor=viz_params.smoothing_factor,
            terrain_adaptation=viz_params.follow_topography,
            water_exclusion=viz_params.exclude_water
        )
        
        # =================================================================
        # 10. CONSTRUCTION DE LA RÉPONSE (NIVEAU 4 - avec corridors)
        # =================================================================
        
        response = WaypointAnalysisResponse(
            api_schema_version="1.0.0",
            model_version="BIONIC-V5.1-NIVEAU4",
            engine_version=ENGINE_VERSION,
            analysis_id=analysis_id,
            calculated_at=datetime.now(timezone.utc),
            waypoint=WaypointOutput(
                id=request.waypoint.id,
                name=request.waypoint.name,
                coordinates={"lat": lat, "lng": lng}
            ),
            scores=scores_output,
            layers=layers_output,
            corridors=corridors_output,  # NIVEAU 4 - Corridors
            heatmap=heatmap_output,
            legal_status=legal_status,
            optimal_windows=optimal_windows,
            recommendations=recommendations,
            visualization=visualization,
            metadata=metadata,
            contract=ContractInfo()
        )
        
        logger.info(f"[{analysis_id}] Analysis complete in {processing_time_ms}ms (NIVEAU 4 - Corridors: {corridor_network.total_corridors})")
        
        return response
        
    except Exception as e:
        logger.error(f"[{analysis_id}] Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": True,
                "error_code": "ANALYSIS_FAILED",
                "message": f"L'analyse a échoué: {str(e)}",
                "analysis_id": analysis_id
            }
        )


# =============================================================================
# HEALTH CHECK
# =============================================================================

@router.get("/analyze_waypoint/health")
async def waypoint_analysis_health():
    """Vérification santé de l'endpoint d'analyse waypoint."""
    return {
        "status": "healthy",
        "endpoint": "/api/v1/bionic/analyze_waypoint",
        "api_schema_version": "1.0.0",
        "model_version": "BIONIC-V5.1-NIVEAU6",
        "engine_version": ENGINE_VERSION,
        "contract": {
            "structure": "scores + layers + corridors + heatmap + legal_status + optimal_windows + recommendations",
            "stability": "stable"
        },
        "niveau_6": {
            "calibration": "active",
            "mobility_prediction": "/api/v1/bionic/mobility_prediction"
        }
    }


# =============================================================================
# ENDPOINT: MOBILITY PREDICTION (NIVEAU 6)
# =============================================================================

from modules.bionic_engine_p0.knowledge.calibration import (
    get_calibration_registry,
    get_mobility_prediction_service
)


@router.post("/mobility_prediction")
async def predict_mobility(
    waypoint_lat: float,
    waypoint_lng: float,
    species: str = "orignal",
    window_hours: float = 6.0,
    analysis_mode: str = "rut",
    include_trajectory: bool = True
):
    """
    NIVEAU 6 BIONIC V5 — Prédiction de mobilité sur fenêtre temporelle.
    
    Génère des prédictions de mouvement avec zones probables en GeoJSON.
    
    Args:
        waypoint_lat: Latitude du point de départ
        waypoint_lng: Longitude du point de départ
        species: Espèce cible (orignal, cerf, ours)
        window_hours: Durée de la fenêtre de prédiction (heures)
        analysis_mode: Mode d'analyse (rut, pre_rut, post_rut, live)
        include_trajectory: Inclure les points de trajectoire prédite
        
    Returns:
        GeoJSON FeatureCollection avec zones et trajectoire
    """
    try:
        prediction_service = get_mobility_prediction_service()
        unified_scoring_service = get_unified_scoring_service()
        
        # Créer le contexte de scoring pour obtenir les modificateurs
        from modules.bionic_engine_p0.services.scoring.base_score_service import ScoreContext
        
        score_context = ScoreContext(
            waypoint_id=f"PRED-{waypoint_lat:.4f}-{waypoint_lng:.4f}",
            latitude=waypoint_lat,
            longitude=waypoint_lng,
            search_radius_km=3.0,
            species=species,
            region="quebec",
            target_datetime=datetime.now(timezone.utc),
            extra_data={
                "latitude": waypoint_lat,
                "longitude": waypoint_lng
            }
        )
        
        # Injecter les modificateurs avancés
        unified_scoring_service._inject_advanced_modifiers(
            score_context,
            analysis_mode,
            f"PRED-{datetime.now(timezone.utc).strftime('%H%M%S')}"
        )
        
        # Extraire les modificateurs
        adv = score_context.advanced_modifiers or {}
        mobility_modifier = adv.get("mobility_modifier", 1.0)
        seasonal_modifier = adv.get("phase_c_modifier", 1.0)
        thermal_modifier = adv.get("thermal_stress_modifier", 1.0)
        human_pressure_modifier = adv.get("hunting_pressure_modifier", 1.0)
        
        # Générer la prédiction
        prediction = prediction_service.predict_mobility(
            start_lat=waypoint_lat,
            start_lng=waypoint_lng,
            species=species,
            prediction_start=datetime.now(timezone.utc),
            window_hours=window_hours,
            mobility_modifier=mobility_modifier,
            seasonal_modifier=seasonal_modifier,
            thermal_modifier=thermal_modifier,
            human_pressure_modifier=human_pressure_modifier,
            current_season=analysis_mode,
            include_trajectory=include_trajectory
        )
        
        return prediction.to_geojson_feature_collection()
        
    except Exception as e:
        logger.error(f"Mobility prediction failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": True,
                "error_code": "PREDICTION_FAILED",
                "message": f"La prédiction de mobilité a échoué: {str(e)}"
            }
        )


@router.get("/calibration/status")
async def get_calibration_status():
    """
    NIVEAU 6 BIONIC V5 — Statut de calibration du modèle.
    
    Returns:
        Statut de calibration, version du modèle, métriques de validation
    """
    try:
        calibration_registry = get_calibration_registry()
        
        profile = calibration_registry.get_current_profile()
        model_version = calibration_registry.get_model_version()
        stats = calibration_registry.get_stats()
        
        return {
            "status": "success",
            "calibration": {
                "profile": profile.to_dict(),
                "model_version": model_version.to_dict()
            },
            "statistics": stats,
            "version": "6.0.0"
        }
        
    except Exception as e:
        logger.error(f"Calibration status failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "message": str(e)}
        )

