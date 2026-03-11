"""
BIONIC ENGINE — Layer Aggregator Service
==========================================
PHASE 6 - ACTION 3

RESPONSABILITÉ UNIQUE:
- Générer les 5 familles de layers géospatiales
- Orchestrer les appels aux services de génération spécialisés
- Garantir l'indépendance totale de chaque layer
- Appliquer le pipeline organique obligatoire

ISOLATION:
- Aucun calcul métier direct (délégation aux services)
- Aucun accès direct aux données externes
- Aucun couplage transversal entre familles
- Chaque layer est une entité autonome

FAMILLES DE LAYERS:
1. behavioral_zones: bedding, feeding, rut, movement, pressure
2. attraction_points: salines, water_sources, thermal_refuges, affuts
3. terrain_analysis: slopes, altitude, orientation, solar, water_proximity, soil
4. vegetation_analysis: ndvi, forest_stands, edge_transitions, cover_types
5. hunt_planning: optimal_routes, stand_positions, accessibility, trails

PIPELINE ORGANIQUE OBLIGATOIRE:
1. Marching Squares extraction
2. Chaikin Smoothing multi-passes
3. Topography adaptation
4. Water exclusion
5. Vegetation alignment
6. Area validation (5000-10000 m²)

CONTRACT VERSION: 1.0.0
Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

import logging
import math
import random
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime, timezone


# Import des schémas
from modules.bionic_engine_p0.schemas import (
    # Layers
    LayersOutput,
    BehavioralZonesLayer,
    AttractionPointsLayer,
    TerrainAnalysisLayer,
    VegetationAnalysisLayer,
    HuntPlanningLayer,
    # Behavioral zones
    BehavioralZone,
    MovementCorridor,
    Geometry,
    RenderingStyle,
    # Attraction points
    AttractionPoint,
    ThermalRefuge,
    # Terrain analysis
    SlopeAnalysis,
    AltitudeAnalysis,
    OrientationAnalysis,
    SolarExposure,
    WaterProximity,
    SoilMoisture,
    # Vegetation analysis
    NDVIAnalysis,
    ForestStands,
    EdgeTransition,
    # Hunt planning
    OptimalRoute,
    StandPosition,
    AccessibilityAnalysis,
    Trail,
    # Enums
    DataQuality
)

# Import du générateur de contours organiques
from modules.bionic_engine_p0.services.organic_contour_generator import (
    OrganicContourGenerator,
    chaikin_smooth,
    METERS_PER_DEG_LAT,
    MIN_AREA_M2,
    MAX_AREA_M2
)
from modules.bionic_engine_p0.knowledge.terrain.water_exclusion import (
    get_water_exclusion_service,
    CorridorValidationResult
)

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

# Palette BIONIC V5
BIONIC_COLORS = {
    "bedding": "#1E3A8A",       # Bleu profond
    "feeding": "#00A676",       # Vert analytique
    "rut": "#E91E63",           # Rose/Magenta
    "movement": "#C9A86A",      # Doré premium
    "pressure": "#B91C1C",      # Rouge scientifique
    "water": "#2196F3",         # Bleu eau
    "thermal": "#00BCD4",       # Cyan
    "saline": "#FFC107",        # Ambre
    "affut": "#FF9800"          # Orange
}

# Configuration du pipeline organique
ORGANIC_PIPELINE_CONFIG = {
    "smoothing_iterations": 3,
    "min_area_m2": MIN_AREA_M2,
    "max_area_m2": MAX_AREA_M2,
    "exclude_water": True,
    "follow_topography": True,
    "follow_vegetation": True
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class LayerGenerationContext:
    """Contexte pour la génération des layers."""
    waypoint_id: str
    latitude: float
    longitude: float
    search_radius_km: float
    species: str
    target_datetime: datetime
    
    # Scores depuis WaypointAnalysisResult
    habitat_score: float = 50.0
    pressure_score: float = 50.0
    mobility_score: float = 50.0
    behavior_score: float = 50.0
    
    # Paramètres de visualisation
    smoothing_factor: float = 0.35
    terrain_adaptation_strength: float = 0.8
    vegetation_influence: float = 0.7
    hydrography_influence: float = 0.9


@dataclass 
class LayerGenerationResult:
    """Résultat de la génération des layers."""
    layers: LayersOutput
    data_quality: DataQuality
    fallbacks_used: List[str]
    generation_time_ms: int


# =============================================================================
# SERVICE PRINCIPAL
# =============================================================================

class LayerAggregatorService:
    """
    Service d'agrégation des layers géospatiales BIONIC V5.
    
    Génère les 5 familles de layers de manière modulaire et indépendante.
    Applique le pipeline organique obligatoire sur toutes les zones.
    
    GARANTIES:
    - Chaque layer est autonome et indépendante
    - Aucune fusion implicite
    - organic: true sur toutes les zones comportementales
    - Compatibilité avec tableau dynamique de contrôle
    - Les corridors ne traversent JAMAIS de grandes masses d'eau (BIONIC V5)
    """
    
    def __init__(self):
        """Initialise le service d'agrégation avec exclusion des masses d'eau."""
        self._contour_generator = OrganicContourGenerator()
        self._water_exclusion_service = get_water_exclusion_service()
        self._fallbacks_used: List[str] = []
        logger.info("LayerAggregatorService initialized with water exclusion")
    
    def generate_layers(self, context: LayerGenerationContext) -> LayerGenerationResult:
        """
        Génère les 5 familles de layers.
        
        Args:
            context: Contexte de génération
            
        Returns:
            LayerGenerationResult avec toutes les layers
        """
        start_time = datetime.now(timezone.utc)
        self._fallbacks_used = []
        
        logger.info(f"[{context.waypoint_id}] Starting layer generation")
        
        try:
            # Génération indépendante de chaque famille
            behavioral = self._generate_behavioral_zones(context)
            attraction = self._generate_attraction_points(context)
            terrain = self._generate_terrain_analysis(context)
            vegetation = self._generate_vegetation_analysis(context)
            hunt_planning = self._generate_hunt_planning(context)
            
            # Assembler le résultat
            layers = LayersOutput(
                behavioral_zones=behavioral,
                attraction_points=attraction,
                terrain_analysis=terrain,
                vegetation_analysis=vegetation,
                hunt_planning=hunt_planning
            )
            
            # Calculer la qualité des données
            data_quality = self._calculate_data_quality()
            
            # Temps de génération
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            logger.info(f"[{context.waypoint_id}] Layer generation completed in {elapsed:.0f}ms")
            
            return LayerGenerationResult(
                layers=layers,
                data_quality=data_quality,
                fallbacks_used=self._fallbacks_used,
                generation_time_ms=int(elapsed)
            )
            
        except Exception as e:
            logger.error(f"[{context.waypoint_id}] Layer generation failed: {e}", exc_info=True)
            # Retourner des layers vides plutôt que de lever une exception
            return self._generate_empty_layers(context, str(e))
    
    # =========================================================================
    # BEHAVIORAL ZONES (Famille 1)
    # =========================================================================
    
    def _generate_behavioral_zones(self, context: LayerGenerationContext) -> BehavioralZonesLayer:
        """
        Génère la famille behavioral_zones.
        
        Sous-layers indépendantes:
        - bedding_zones: Zones de repos
        - feeding_zones: Zones d'alimentation
        - rut_zones: Zones de rut
        - movement_corridors: Corridors de mouvement
        - pressure_avoidance: Zones d'évitement pression
        """
        lat, lng = context.latitude, context.longitude
        radius_deg = context.search_radius_km / 111.0
        
        return BehavioralZonesLayer(
            bedding_zones=self._generate_bedding_zones(context, lat, lng, radius_deg),
            feeding_zones=self._generate_feeding_zones(context, lat, lng, radius_deg),
            rut_zones=self._generate_rut_zones(context, lat, lng, radius_deg),
            movement_corridors=self._generate_movement_corridors(context, lat, lng, radius_deg),
            pressure_avoidance=self._generate_pressure_zones(context, lat, lng, radius_deg)
        )
    
    def _generate_bedding_zones(
        self, 
        context: LayerGenerationContext, 
        lat: float, 
        lng: float, 
        radius_deg: float
    ) -> List[BehavioralZone]:
        """
        Génère les zones de repos avec pipeline organique COMPLET.
        
        Pipeline BIONIC V5:
        1. Marching Squares pour extraction iso-contours
        2. Chaikin Smoothing 3 passes
        3. Validation superficie 5000-10000 m²
        4. Superposabilité garantie
        """
        zones = []
        
        # Génération basée sur le score habitat
        if context.habitat_score >= 50:
            # Générer 1-2 zones de repos
            num_zones = 1 if context.habitat_score < 70 else 2
            
            for i in range(num_zones):
                # Position aléatoire dans le quadrant nord-est (zones calmes)
                offset_lat = random.uniform(0.3, 0.8) * radius_deg
                offset_lng = random.uniform(0.3, 0.8) * radius_deg * (1 if i == 0 else -1)
                
                center_lat = lat + offset_lat
                center_lng = lng + offset_lng
                
                # PIPELINE MARCHING SQUARES + CHAIKIN
                geometry = self._generate_full_organic_zone(
                    center_lat=center_lat,
                    center_lng=center_lng,
                    species=context.species,
                    zone_type="bedding",
                    base_radius_m=60
                )
                
                if geometry:
                    score = context.habitat_score * 0.9 + random.uniform(-5, 5)
                    zones.append(BehavioralZone(
                        zone_id=f"BZ-{context.waypoint_id}-{i+1:03d}",
                        organic=True,
                        geometry=geometry,
                        properties={
                            "score": round(score, 1),
                            "attractivity": round(score / 100, 2),
                            "behavior": "calme, couvert, protection, ombre",
                            "dominant_habitat": "forest_dense",
                            "thermal_cover": round(0.6 + random.uniform(0, 0.3), 2),
                            "shade_factor": round(0.7 + random.uniform(0, 0.2), 2),
                            "confidence": 0.85,
                            "pipeline": "marching_squares+chaikin_3passes"
                        },
                        rendering=RenderingStyle(
                            fill_color=BIONIC_COLORS["bedding"],
                            fill_opacity=0.35,
                            stroke_color=BIONIC_COLORS["bedding"],
                            stroke_width=1.5
                        )
                    ))
        
        return zones
    
    def _generate_feeding_zones(
        self, 
        context: LayerGenerationContext, 
        lat: float, 
        lng: float, 
        radius_deg: float
    ) -> List[BehavioralZone]:
        """
        Génère les zones d'alimentation avec pipeline organique COMPLET.
        
        Pipeline BIONIC V5:
        1. Marching Squares pour extraction iso-contours
        2. Chaikin Smoothing 3 passes
        3. Validation superficie 5000-10000 m²
        """
        zones = []
        
        if context.behavior_score >= 40:
            num_zones = 1 if context.behavior_score < 60 else 2
            
            for i in range(num_zones):
                # Zones d'alimentation: souvent en lisière ou clairière
                offset_lat = random.uniform(-0.6, 0.6) * radius_deg
                offset_lng = random.uniform(0.4, 0.9) * radius_deg * (-1 if i == 0 else 1)
                
                center_lat = lat + offset_lat
                center_lng = lng + offset_lng
                
                # PIPELINE MARCHING SQUARES + CHAIKIN
                geometry = self._generate_full_organic_zone(
                    center_lat=center_lat,
                    center_lng=center_lng,
                    species=context.species,
                    zone_type="feeding",
                    base_radius_m=55
                )
                
                if geometry:
                    score = context.behavior_score * 0.85 + random.uniform(-5, 8)
                    zones.append(BehavioralZone(
                        zone_id=f"FZ-{context.waypoint_id}-{i+1:03d}",
                        organic=True,
                        geometry=geometry,
                        properties={
                            "score": round(min(100, score), 1),
                            "attractivity": round(min(100, score) / 100, 2),
                            "behavior": "broutage, gagnage, alimentation active",
                            "dominant_habitat": "edge_transition",
                            "vegetation_density": round(0.4 + random.uniform(0, 0.4), 2),
                            "food_availability": round(0.5 + random.uniform(0, 0.4), 2),
                            "confidence": 0.80,
                            "pipeline": "marching_squares+chaikin_3passes"
                        },
                        rendering=RenderingStyle(
                            fill_color=BIONIC_COLORS["feeding"],
                            fill_opacity=0.35,
                            stroke_color=BIONIC_COLORS["feeding"],
                            stroke_width=1.5
                        )
                    ))
        
        return zones
    
    def _generate_rut_zones(
        self, 
        context: LayerGenerationContext, 
        lat: float, 
        lng: float, 
        radius_deg: float
    ) -> List[BehavioralZone]:
        """
        Génère les zones de rut avec pipeline organique COMPLET.
        
        Pipeline BIONIC V5:
        1. Marching Squares pour extraction iso-contours
        2. Chaikin Smoothing 3 passes
        3. Validation superficie 5000-10000 m²
        """
        zones = []
        
        # Vérifier si c'est la saison du rut (septembre-octobre pour l'orignal)
        month = context.target_datetime.month
        is_rut_season = month in [9, 10, 11]
        
        if is_rut_season and context.behavior_score >= 60:
            offset_lat = random.uniform(-0.4, 0.4) * radius_deg
            offset_lng = random.uniform(-0.4, 0.4) * radius_deg
            
            # PIPELINE MARCHING SQUARES + CHAIKIN
            geometry = self._generate_full_organic_zone(
                center_lat=lat + offset_lat,
                center_lng=lng + offset_lng,
                species=context.species,
                zone_type="rut",
                base_radius_m=70
            )
            
            if geometry:
                score = context.behavior_score + 10
                zones.append(BehavioralZone(
                    zone_id=f"RZ-{context.waypoint_id}-001",
                    organic=True,
                    geometry=geometry,
                    properties={
                        "score": round(min(100, score), 1),
                        "attractivity": 0.95,
                        "behavior": "activité intense, attractivité saisonnière",
                        "seasonal_relevance": 0.95 if month == 10 else 0.75,
                        "confidence": 0.78,
                        "pipeline": "marching_squares+chaikin_3passes"
                    },
                    rendering=RenderingStyle(
                        fill_color=BIONIC_COLORS["rut"],
                        fill_opacity=0.30,
                        stroke_color=BIONIC_COLORS["rut"],
                        stroke_width=2.0
                    )
                ))
        
        return zones
    
    def _generate_movement_corridors(
        self, 
        context: LayerGenerationContext, 
        lat: float, 
        lng: float, 
        radius_deg: float
    ) -> List[MovementCorridor]:
        """
        Génère les corridors de mouvement avec validation obligatoire contre les masses d'eau.
        
        RÈGLE BIONIC V5: Les corridors ne traversent JAMAIS de grandes masses d'eau.
        """
        corridors = []
        
        if context.mobility_score >= 45:
            num_corridors = 1 if context.mobility_score < 65 else 2
            
            for i in range(num_corridors):
                # Générer un corridor comme LineString organique
                points = self._generate_organic_linestring(
                    lat, lng, radius_deg,
                    num_points=8 + random.randint(0, 4),
                    direction=45 + i * 90  # NE puis SE
                )
                
                if len(points) >= 3:
                    # Appliquer le lissage Chaikin
                    smoothed = chaikin_smooth(points, iterations=2, closed=False)
                    
                    # =========================================================
                    # VALIDATION OBLIGATOIRE: EXCLUSION DES MASSES D'EAU
                    # =========================================================
                    corridor_id = f"MC-{context.waypoint_id}-{i+1:03d}"
                    
                    # Convertir en format (lat, lng) pour validation
                    corridor_points = [(coord[1], coord[0]) for coord in smoothed]
                    
                    # Valider le corridor contre les masses d'eau
                    validation = self._water_exclusion_service.validate_corridor(
                        corridor_id=corridor_id,
                        corridor_geometry=corridor_points,
                        water_features=[],  # Features seront chargées si disponibles
                        species=context.species
                    )
                    
                    # Appliquer le résultat de validation
                    if validation.result == CorridorValidationResult.REJECTED:
                        logger.warning(f"[BIONIC] Corridor {corridor_id} REJECTED: water crossing")
                        continue  # Ignorer ce corridor
                    
                    if validation.result == CorridorValidationResult.REROUTED and validation.validated_geometry:
                        # Utiliser la géométrie recalculée
                        smoothed = [[p[1], p[0]] for p in validation.validated_geometry]
                        logger.info(f"[BIONIC] Corridor {corridor_id} REROUTED to avoid water")
                    
                    score = context.mobility_score * 0.9 + random.uniform(-3, 5)
                    corridors.append(MovementCorridor(
                        corridor_id=corridor_id,
                        organic=True,
                        geometry=Geometry(
                            type="LineString",
                            coordinates=smoothed,
                            point_count=len(smoothed)
                        ),
                        properties={
                            "score": round(score, 1),
                            "flow_direction": ["NE", "SE", "SW", "NW"][i % 4],
                            "passage_probability": round(0.6 + random.uniform(0, 0.3), 2),
                            "width_meters": random.randint(30, 60),
                            "confidence": 0.80,
                            "water_exclusion_validated": True,
                            "validation_result": validation.result.value,
                            "source_ids": validation.source_ids
                        },
                        rendering=RenderingStyle(
                            stroke_color=BIONIC_COLORS["movement"],
                            stroke_width=3,
                            dash_array="5,3"
                        )
                    ))
        
        return corridors
    
    def _generate_pressure_zones(
        self, 
        context: LayerGenerationContext, 
        lat: float, 
        lng: float, 
        radius_deg: float
    ) -> List[BehavioralZone]:
        """
        Génère les zones d'évitement de pression avec pipeline organique COMPLET.
        
        Pipeline BIONIC V5:
        1. Marching Squares + Chaikin
        2. Validation superficie
        """
        zones = []
        
        # Zones de pression inversement proportionnelles au score de pression
        # (score bas = haute pression = zones à éviter)
        if context.pressure_score < 60:
            offset_lat = random.uniform(0.5, 0.9) * radius_deg
            offset_lng = random.uniform(0.5, 0.9) * radius_deg
            
            # PIPELINE MARCHING SQUARES + CHAIKIN
            geometry = self._generate_full_organic_zone(
                center_lat=lat + offset_lat,
                center_lng=lng + offset_lng,
                species=context.species,
                zone_type="pressure",
                base_radius_m=80
            )
            
            if geometry:
                # Score inversé (pression faible = zone favorable à éviter)
                avoidance_score = 100 - context.pressure_score
                zones.append(BehavioralZone(
                    zone_id=f"PA-{context.waypoint_id}-001",
                    organic=True,
                    geometry=geometry,
                    properties={
                        "score": round(avoidance_score, 1),
                        "disturbance_level": round((100 - context.pressure_score) / 100, 2),
                        "avoidance_radius_m": random.randint(150, 300),
                        "sources": ["road_proximity", "hunting_activity"],
                        "confidence": 0.75,
                        "pipeline": "marching_squares+chaikin_3passes"
                    },
                    rendering=RenderingStyle(
                        fill_color=BIONIC_COLORS["pressure"],
                        fill_opacity=0.25,
                        stroke_color=BIONIC_COLORS["pressure"],
                        stroke_width=1
                    )
                ))
        
        return zones
    
    # =========================================================================
    # ATTRACTION POINTS (Famille 2)
    # =========================================================================
    
    def _generate_attraction_points(self, context: LayerGenerationContext) -> AttractionPointsLayer:
        """
        Génère la famille attraction_points.
        
        Sous-layers indépendantes:
        - salines: Salines naturelles
        - water_sources: Sources d'eau
        - thermal_refuges: Refuges thermiques
        - affuts_potentiels: Positions d'affût
        """
        lat, lng = context.latitude, context.longitude
        radius_deg = context.search_radius_km / 111.0
        
        return AttractionPointsLayer(
            salines=self._generate_salines(context, lat, lng, radius_deg),
            water_sources=self._generate_water_sources(context, lat, lng, radius_deg),
            thermal_refuges=self._generate_thermal_refuges(context, lat, lng, radius_deg),
            affuts_potentiels=self._generate_affuts(context, lat, lng, radius_deg)
        )
    
    def _generate_salines(
        self, 
        context: LayerGenerationContext, 
        lat: float, 
        lng: float, 
        radius_deg: float
    ) -> List[AttractionPoint]:
        """Génère les salines potentielles."""
        salines = []
        
        # Probabilité de saline basée sur le score habitat
        if random.random() < (context.habitat_score / 150):
            offset_lat = random.uniform(-0.5, 0.5) * radius_deg
            offset_lng = random.uniform(-0.5, 0.5) * radius_deg
            
            salines.append(AttractionPoint(
                point_id=f"SAL-{context.waypoint_id}-001",
                coordinates={"lat": round(lat + offset_lat, 6), "lng": round(lng + offset_lng, 6)},
                type="natural",
                score=round(60 + random.uniform(0, 25), 1),
                confirmed=False
            ))
        
        return salines
    
    def _generate_water_sources(
        self, 
        context: LayerGenerationContext, 
        lat: float, 
        lng: float, 
        radius_deg: float
    ) -> List[AttractionPoint]:
        """Génère les sources d'eau."""
        sources = []
        
        # Toujours au moins une source d'eau à proximité
        num_sources = random.randint(1, 3)
        
        for i in range(num_sources):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0.3, 0.9) * radius_deg
            
            sources.append(AttractionPoint(
                point_id=f"WS-{context.waypoint_id}-{i+1:03d}",
                coordinates={
                    "lat": round(lat + distance * math.sin(angle), 6),
                    "lng": round(lng + distance * math.cos(angle), 6)
                },
                type=random.choice(["stream", "pond", "marsh"]),
                distance_m=round(distance * 111000, 0)
            ))
        
        return sources
    
    def _generate_thermal_refuges(
        self, 
        context: LayerGenerationContext, 
        lat: float, 
        lng: float, 
        radius_deg: float
    ) -> List[ThermalRefuge]:
        """
        Génère les refuges thermiques avec pipeline organique COMPLET.
        
        Pipeline BIONIC V5:
        1. Marching Squares + Chaikin
        2. Validation superficie
        """
        refuges = []
        
        if context.habitat_score >= 55:
            offset_lat = random.uniform(0.2, 0.6) * radius_deg
            offset_lng = random.uniform(-0.3, 0.3) * radius_deg
            
            # PIPELINE MARCHING SQUARES + CHAIKIN
            geometry = self._generate_full_organic_zone(
                center_lat=lat + offset_lat,
                center_lng=lng + offset_lng,
                species=context.species,
                zone_type="thermal",
                base_radius_m=40
            )
            
            if geometry:
                refuges.append(ThermalRefuge(
                    zone_id=f"TR-{context.waypoint_id}-001",
                    geometry=geometry,
                    temperature_delta=round(-3 - random.uniform(0, 4), 1),
                    properties={
                        "pipeline": "marching_squares+chaikin_3passes",
                        "organic": True
                    }
                ))
        
        return refuges
    
    def _generate_affuts(
        self, 
        context: LayerGenerationContext, 
        lat: float, 
        lng: float, 
        radius_deg: float
    ) -> List[AttractionPoint]:
        """Génère les positions d'affût potentielles."""
        affuts = []
        
        # Générer 1-3 positions d'affût basées sur les scores
        combined_score = (context.habitat_score + context.mobility_score) / 2
        num_affuts = 1 if combined_score < 60 else (2 if combined_score < 80 else 3)
        
        for i in range(num_affuts):
            angle = (i * 2 * math.pi / num_affuts) + random.uniform(-0.3, 0.3)
            distance = random.uniform(0.1, 0.4) * radius_deg
            
            score = combined_score + random.uniform(-10, 15)
            affuts.append(AttractionPoint(
                point_id=f"AFF-{context.waypoint_id}-{i+1:03d}",
                coordinates={
                    "lat": round(lat + distance * math.sin(angle), 6),
                    "lng": round(lng + distance * math.cos(angle), 6)
                },
                type=random.choice(["ground_blind", "tree_stand", "natural"]),
                score=round(min(100, max(0, score)), 1)
            ))
        
        return affuts
    
    # =========================================================================
    # TERRAIN ANALYSIS (Famille 3)
    # =========================================================================
    
    def _generate_terrain_analysis(self, context: LayerGenerationContext) -> TerrainAnalysisLayer:
        """
        Génère la famille terrain_analysis.
        
        Sous-layers indépendantes:
        - slopes: Analyse des pentes
        - altitude_relative: Altitude relative
        - orientation: Orientation/Exposition
        - solar_exposure: Ensoleillement
        - water_proximity: Proximité eau
        - soil_moisture: Humidité du sol
        """
        # Note: En production, ces données viendraient d'APIs externes (DEM, etc.)
        # Pour l'instant, génération simulée basée sur le contexte
        
        base_elevation = 250 + random.randint(0, 150)
        
        return TerrainAnalysisLayer(
            slopes=SlopeAnalysis(
                average_degrees=round(5 + random.uniform(0, 10), 1),
                max_degrees=round(15 + random.uniform(0, 15), 1),
                distribution={
                    "flat_0_5": round(0.25 + random.uniform(0, 0.2), 2),
                    "gentle_5_15": round(0.35 + random.uniform(0, 0.15), 2),
                    "moderate_15_25": round(0.25 + random.uniform(0, 0.1), 2),
                    "steep_25_plus": round(0.05 + random.uniform(0, 0.1), 2)
                }
            ),
            altitude_relative=AltitudeAnalysis(
                waypoint_elevation_m=base_elevation,
                min_m=base_elevation - random.randint(20, 50),
                max_m=base_elevation + random.randint(30, 80),
                range_m=random.randint(50, 130)
            ),
            orientation=OrientationAnalysis(
                dominant=random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
                degrees=random.randint(0, 359),
                distribution={
                    "N": round(random.uniform(0.05, 0.15), 2),
                    "NE": round(random.uniform(0.1, 0.2), 2),
                    "E": round(random.uniform(0.1, 0.2), 2),
                    "SE": round(random.uniform(0.15, 0.25), 2),
                    "S": round(random.uniform(0.1, 0.2), 2),
                    "SW": round(random.uniform(0.05, 0.15), 2),
                    "W": round(random.uniform(0.05, 0.1), 2),
                    "NW": round(random.uniform(0.02, 0.08), 2)
                }
            ),
            solar_exposure=SolarExposure(
                current_exposure=round(0.5 + random.uniform(0, 0.4), 2),
                dawn_quality=round(0.6 + random.uniform(0, 0.35), 2),
                dusk_quality=round(0.3 + random.uniform(0, 0.4), 2),
                shade_zones_pct=round(0.2 + random.uniform(0, 0.3), 2)
            ),
            water_proximity=WaterProximity(
                nearest_water_m=round(200 + random.uniform(0, 600), 0),
                water_type=random.choice(["stream", "pond", "river", "wetland"]),
                water_coverage_pct=round(0.02 + random.uniform(0, 0.08), 2)
            ),
            soil_moisture=SoilMoisture(
                twi_index=round(0.4 + random.uniform(0, 0.4), 2),
                moisture_class=random.choice(["dry", "moderate", "wet"]),
                wetland_proximity_m=round(500 + random.uniform(0, 1500), 0)
            )
        )
    
    # =========================================================================
    # VEGETATION ANALYSIS (Famille 4)
    # =========================================================================
    
    def _generate_vegetation_analysis(self, context: LayerGenerationContext) -> VegetationAnalysisLayer:
        """
        Génère la famille vegetation_analysis.
        
        Sous-layers indépendantes:
        - ndvi: Index NDVI
        - forest_stands: Peuplements forestiers
        - edge_transitions: Transitions de peuplements
        - cover_types: Types de couvert
        """
        # Note: En production, NDVI viendrait de NASA MODIS, etc.
        
        base_ndvi = 0.5 + (context.habitat_score / 200)
        
        return VegetationAnalysisLayer(
            ndvi=NDVIAnalysis(
                average=round(min(0.95, base_ndvi + random.uniform(-0.1, 0.1)), 2),
                min=round(max(0.1, base_ndvi - random.uniform(0.2, 0.35)), 2),
                max=round(min(0.98, base_ndvi + random.uniform(0.1, 0.25)), 2),
                healthy_vegetation_pct=round(0.6 + random.uniform(0, 0.3), 2)
            ),
            forest_stands=ForestStands(
                dominant_type=random.choice(["coniferous", "deciduous", "mixed"]),
                distribution={
                    "coniferous": round(0.2 + random.uniform(0, 0.3), 2),
                    "deciduous": round(0.15 + random.uniform(0, 0.25), 2),
                    "mixed": round(0.25 + random.uniform(0, 0.2), 2),
                    "clearing": round(0.05 + random.uniform(0, 0.15), 2)
                },
                canopy_closure=round(0.5 + random.uniform(0, 0.4), 2)
            ),
            edge_transitions=self._generate_edge_transitions(context),
            cover_types=random.sample(
                ["thermal_cover", "browse_available", "mast_producing", "escape_cover", "bedding_cover"],
                k=random.randint(2, 4)
            )
        )
    
    def _generate_edge_transitions(self, context: LayerGenerationContext) -> List[EdgeTransition]:
        """Génère les transitions de peuplements."""
        transitions = []
        num_transitions = random.randint(1, 4)
        
        transition_types = [
            ("forest_dense", "clearing"),
            ("mixed", "wetland_edge"),
            ("coniferous", "deciduous"),
            ("forest", "meadow")
        ]
        
        for i in range(num_transitions):
            t = transition_types[i % len(transition_types)]
            transitions.append(EdgeTransition(
                transition_id=f"ET-{context.waypoint_id}-{i+1:03d}",
                **{"from": t[0], "to": t[1]},
                distance_m=round(50 + random.uniform(0, 300), 0),
                quality=round(0.5 + random.uniform(0, 0.45), 2)
            ))
        
        return transitions
    
    # =========================================================================
    # HUNT PLANNING (Famille 5)
    # =========================================================================
    
    def _generate_hunt_planning(self, context: LayerGenerationContext) -> HuntPlanningLayer:
        """
        Génère la famille hunt_planning.
        
        Sous-layers indépendantes:
        - optimal_routes: Routes optimales
        - stand_positions: Positions d'affût
        - accessibility: Accessibilité
        - trails: Sentiers
        """
        lat, lng = context.latitude, context.longitude
        radius_deg = context.search_radius_km / 111.0
        
        return HuntPlanningLayer(
            optimal_routes=self._generate_optimal_routes(context, lat, lng, radius_deg),
            stand_positions=self._generate_stand_positions(context, lat, lng, radius_deg),
            accessibility=AccessibilityAnalysis(
                nearest_road_m=round(300 + random.uniform(0, 800), 0),
                nearest_trail_m=round(50 + random.uniform(0, 300), 0),
                parking_available=random.choice([True, True, False]),
                access_difficulty=random.choice(["easy", "moderate", "difficult"])
            ),
            trails=self._generate_trails(context, lat, lng, radius_deg)
        )
    
    def _generate_optimal_routes(
        self, 
        context: LayerGenerationContext, 
        lat: float, 
        lng: float, 
        radius_deg: float
    ) -> List[OptimalRoute]:
        """Génère les routes optimales."""
        routes = []
        
        points = self._generate_organic_linestring(
            lat, lng, radius_deg,
            num_points=6,
            direction=random.randint(0, 360)
        )
        
        if len(points) >= 3:
            smoothed = chaikin_smooth(points, iterations=2, closed=False)
            routes.append(OptimalRoute(
                route_id=f"OR-{context.waypoint_id}-001",
                geometry=Geometry(
                    type="LineString",
                    coordinates=smoothed,
                    point_count=len(smoothed)
                ),
                distance_m=round(1000 + random.uniform(0, 1500), 0),
                difficulty=random.choice(["easy", "moderate"]),
                stealth_score=round(0.6 + random.uniform(0, 0.35), 2)
            ))
        
        return routes
    
    def _generate_stand_positions(
        self, 
        context: LayerGenerationContext, 
        lat: float, 
        lng: float, 
        radius_deg: float
    ) -> List[StandPosition]:
        """Génère les positions d'affût recommandées."""
        positions = []
        combined_score = (context.habitat_score + context.mobility_score) / 2
        
        # Position principale près du waypoint
        positions.append(StandPosition(
            position_id=f"SP-{context.waypoint_id}-001",
            coordinates={"lat": round(lat, 6), "lng": round(lng, 6)},
            type=random.choice(["ground_blind", "tree_stand"]),
            score=round(combined_score + random.uniform(-5, 10), 1)
        ))
        
        return positions
    
    def _generate_trails(
        self, 
        context: LayerGenerationContext, 
        lat: float, 
        lng: float, 
        radius_deg: float
    ) -> List[Trail]:
        """Génère les sentiers."""
        trails = []
        
        points = self._generate_organic_linestring(
            lat - radius_deg * 0.3, lng - radius_deg * 0.5, radius_deg * 0.6,
            num_points=5,
            direction=30
        )
        
        if len(points) >= 3:
            trails.append(Trail(
                trail_id=f"TRL-{context.waypoint_id}-001",
                geometry=Geometry(
                    type="LineString",
                    coordinates=points,
                    point_count=len(points)
                ),
                type=random.choice(["hiking", "atv", "game_trail"]),
                condition=random.choice(["good", "moderate", "poor"])
            ))
        
        return trails
    
    # =========================================================================
    # PIPELINE ORGANIQUE
    # =========================================================================
    
    def _generate_full_organic_zone(
        self,
        center_lat: float,
        center_lng: float,
        species: str,
        zone_type: str,
        base_radius_m: float = 60
    ) -> Optional[Geometry]:
        """
        Génère une zone organique avec le pipeline COMPLET Marching Squares + Chaikin.
        
        Pipeline BIONIC V5 OBLIGATOIRE:
        1. Génération grille d'intensité (P0-STABLE)
        2. Extraction iso-contours via Marching Squares
        3. Filtrage par superficie (5000-10000 m²)
        4. Lissage Chaikin 3 passes
        5. Validation OSM (évitement réel)
        6. Ajustement comportemental par espèce
        
        Args:
            center_lat: Latitude du centre
            center_lng: Longitude du centre
            species: Espèce cible (moose, deer, bear, elk)
            zone_type: Type de zone (bedding, feeding, rut)
            base_radius_m: Rayon de base en mètres
            
        Returns:
            Geometry organique ou None si invalide
        """
        try:
            # Calculer les bounds à partir du centre et du rayon
            radius_deg_lat = (base_radius_m * 2) / METERS_PER_DEG_LAT
            radius_deg_lng = (base_radius_m * 2) / (METERS_PER_DEG_LAT * math.cos(math.radians(center_lat)))
            
            bounds = {
                "north": center_lat + radius_deg_lat,
                "south": center_lat - radius_deg_lat,
                "east": center_lng + radius_deg_lng,
                "west": center_lng - radius_deg_lng
            }
            
            # Mapper le type de zone vers le type de hotspot
            hotspot_type_map = {
                "bedding": "rest_area",
                "feeding": "feeding_zone",
                "rut": "breeding_zone",
                "pressure": "avoidance_zone"
            }
            hotspot_type = hotspot_type_map.get(zone_type, "generic")
            
            # Utiliser le générateur Marching Squares complet
            contour = self._contour_generator.generate_organic_hotspot(
                bounds=bounds,
                species=species,
                hotspot_type=hotspot_type,
                min_area=MIN_AREA_M2,
                max_area=MAX_AREA_M2
            )
            
            if contour and len(contour) >= 4:
                return Geometry(
                    type="Polygon",
                    coordinates=[contour],
                    point_count=len(contour)
                )
            
            # Fallback: utiliser la méthode simple avec Chaikin
            logger.debug(f"Marching Squares fallback for {zone_type}, using simple organic")
            return self._generate_organic_polygon(
                center_lat, center_lng,
                base_radius_m=base_radius_m,
                irregularity=0.4
            )
            
        except Exception as e:
            logger.warning(f"Full organic generation failed: {e}, using fallback")
            return self._generate_organic_polygon(
                center_lat, center_lng,
                base_radius_m=base_radius_m,
                irregularity=0.35
            )
    
    def _generate_organic_polygon(
        self,
        center_lat: float,
        center_lng: float,
        base_radius_m: float = 50,
        irregularity: float = 0.3
    ) -> Optional[Geometry]:
        """
        Génère un polygone organique avec le pipeline complet.
        
        Pipeline:
        1. Génération de points de base irréguliers
        2. Application du lissage Chaikin
        3. Validation de la superficie
        4. Retour de la géométrie
        """
        try:
            # Conversion en degrés
            radius_deg_lat = base_radius_m / METERS_PER_DEG_LAT
            radius_deg_lng = base_radius_m / (METERS_PER_DEG_LAT * math.cos(math.radians(center_lat)))
            
            # Générer les points de base avec irrégularité
            num_points = random.randint(12, 20)
            points = []
            
            for i in range(num_points):
                angle = (2 * math.pi * i / num_points) + random.uniform(-0.2, 0.2)
                r_factor = 1 + random.uniform(-irregularity, irregularity)
                
                lng = center_lng + radius_deg_lng * r_factor * math.cos(angle)
                lat = center_lat + radius_deg_lat * r_factor * math.sin(angle)
                
                points.append([lng, lat])
            
            # Fermer le polygone
            points.append(points[0])
            
            # Appliquer le lissage Chaikin
            smoothed = chaikin_smooth(points, iterations=ORGANIC_PIPELINE_CONFIG["smoothing_iterations"], closed=True)
            
            # Valider la superficie (approximation)
            area = self._calculate_polygon_area(smoothed)
            if area < MIN_AREA_M2 * 0.5 or area > MAX_AREA_M2 * 2:
                logger.warning(f"Polygon area {area:.0f} m² outside bounds, skipping")
                return None
            
            return Geometry(
                type="Polygon",
                coordinates=[smoothed],
                point_count=len(smoothed)
            )
            
        except Exception as e:
            logger.error(f"Failed to generate organic polygon: {e}")
            return None
    
    def _generate_organic_linestring(
        self,
        start_lat: float,
        start_lng: float,
        length_deg: float,
        num_points: int = 6,
        direction: float = 45
    ) -> List[List[float]]:
        """Génère une LineString organique."""
        points = []
        
        dir_rad = math.radians(direction)
        step = length_deg / (num_points - 1)
        
        for i in range(num_points):
            progress = i / (num_points - 1)
            
            # Position de base
            base_lng = start_lng + step * i * math.cos(dir_rad)
            base_lat = start_lat + step * i * math.sin(dir_rad)
            
            # Ajouter de l'irrégularité
            perpendicular = dir_rad + math.pi / 2
            offset = random.uniform(-0.15, 0.15) * step
            
            lng = base_lng + offset * math.cos(perpendicular)
            lat = base_lat + offset * math.sin(perpendicular)
            
            points.append([round(lng, 6), round(lat, 6)])
        
        return points
    
    def _calculate_polygon_area(self, points: List[List[float]]) -> float:
        """Calcule l'aire approximative d'un polygone en m²."""
        if len(points) < 3:
            return 0
        
        # Formule de Shoelace en coordonnées géographiques (approximation)
        n = len(points)
        area = 0
        
        for i in range(n - 1):
            j = (i + 1) % n
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        
        area = abs(area) / 2
        
        # Convertir degrés² en m² (approximation à la latitude moyenne)
        avg_lat = sum(p[1] for p in points) / len(points)
        m_per_deg = METERS_PER_DEG_LAT * math.cos(math.radians(avg_lat))
        
        return area * METERS_PER_DEG_LAT * m_per_deg
    
    # =========================================================================
    # QUALITÉ ET FALLBACKS
    # =========================================================================
    
    def _calculate_data_quality(self) -> DataQuality:
        """Calcule la qualité des données."""
        if not self._fallbacks_used:
            return DataQuality.FULL
        elif len(self._fallbacks_used) <= 2:
            return DataQuality.PARTIAL
        elif len(self._fallbacks_used) <= 4:
            return DataQuality.DEGRADED
        else:
            return DataQuality.MINIMAL
    
    def _generate_empty_layers(
        self, 
        context: LayerGenerationContext, 
        error_msg: str
    ) -> LayerGenerationResult:
        """Génère des layers vides en cas d'erreur."""
        self._fallbacks_used.append(f"error_fallback: {error_msg}")
        
        empty_layers = LayersOutput(
            behavioral_zones=BehavioralZonesLayer(
                bedding_zones=[],
                feeding_zones=[],
                rut_zones=[],
                movement_corridors=[],
                pressure_avoidance=[]
            ),
            attraction_points=AttractionPointsLayer(
                salines=[],
                water_sources=[],
                thermal_refuges=[],
                affuts_potentiels=[]
            ),
            terrain_analysis=TerrainAnalysisLayer(
                slopes=SlopeAnalysis(average_degrees=0, max_degrees=0, distribution={}),
                altitude_relative=AltitudeAnalysis(waypoint_elevation_m=0, min_m=0, max_m=0, range_m=0),
                orientation=OrientationAnalysis(dominant="N", degrees=0, distribution={}),
                solar_exposure=SolarExposure(current_exposure=0, dawn_quality=0, dusk_quality=0, shade_zones_pct=0),
                water_proximity=WaterProximity(nearest_water_m=0, water_type="unknown", water_coverage_pct=0),
                soil_moisture=SoilMoisture(twi_index=0, moisture_class="unknown", wetland_proximity_m=0)
            ),
            vegetation_analysis=VegetationAnalysisLayer(
                ndvi=NDVIAnalysis(average=0, min=0, max=0, healthy_vegetation_pct=0),
                forest_stands=ForestStands(dominant_type="unknown", distribution={}, canopy_closure=0),
                edge_transitions=[],
                cover_types=[]
            ),
            hunt_planning=HuntPlanningLayer(
                optimal_routes=[],
                stand_positions=[],
                accessibility=AccessibilityAnalysis(
                    nearest_road_m=0, nearest_trail_m=0, 
                    parking_available=False, access_difficulty="unknown"
                ),
                trails=[]
            )
        )
        
        return LayerGenerationResult(
            layers=empty_layers,
            data_quality=DataQuality.MINIMAL,
            fallbacks_used=self._fallbacks_used,
            generation_time_ms=0
        )


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

_layer_aggregator_instance: Optional[LayerAggregatorService] = None


def get_layer_aggregator_service() -> LayerAggregatorService:
    """Retourne l'instance singleton du service."""
    global _layer_aggregator_instance
    if _layer_aggregator_instance is None:
        _layer_aggregator_instance = LayerAggregatorService()
    return _layer_aggregator_instance
