"""
BIONIC V8 — Base Écologique Complète
=====================================
Document écologique ×10 pour les 3 espèces principales:
- ORIGNAL (Alces alces)
- CHEVREUIL (Odocoileus virginianus)  
- OURS NOIR (Ursus americanus)

VERSION: 8.0.0 — Base écologique V8-ready
Intégration: corridor_10x, pipeline_v7, BCE

Chaque zone inclut:
- habitat, type de forêt, structure du couvert
- nourriture par saison, hydrologie, ensoleillement
- microclimat, topographie, connectivité écologique
- indices terrain, rôle fonctionnel
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger("bionic_engine.ecological_database")

# =====================================================================
# ENUMS ET CONSTANTES
# =====================================================================

class Species(Enum):
    ORIGNAL = "orignal"
    CHEVREUIL = "chevreuil"
    OURS_NOIR = "ours_noir"

class ZoneType(Enum):
    ALIMENTATION = "alimentation"
    REPOS = "repos"
    RUT = "rut"
    PRE_RUT = "pre_rut"
    POST_RUT = "post_rut"
    CORRIDOR = "corridor"
    TANIERE = "taniere"  # Spécifique ours
    TRANSITION = "transition"
    REFUGE = "refuge"
    THERMIQUE = "thermique"

class Season(Enum):
    PRINTEMPS = "printemps"
    ETE = "ete"
    AUTOMNE = "automne"
    HIVER = "hiver"
    PRE_RUT = "pre_rut"
    RUT = "rut"
    POST_RUT = "post_rut"

class ForestType(Enum):
    CONIFERE = "conifere"
    FEUILLU = "feuillu"
    MIXTE = "mixte"
    REGENERATION = "regeneration"
    MATURE = "mature"
    CLAIRSEMEE = "clairsemee"

# =====================================================================
# DATACLASSES ÉCOLOGIQUES
# =====================================================================

@dataclass
class HabitatConditions:
    """Conditions d'habitat pour une zone écologique"""
    forest_type: List[ForestType]
    canopy_cover_min: float  # %
    canopy_cover_max: float  # %
    understory_density: str  # "dense", "moderate", "sparse"
    ground_cover: List[str]  # ["moss", "fern", "shrub", etc.]

@dataclass
class TopographyConditions:
    """Conditions topographiques"""
    slope_min: float  # %
    slope_max: float  # %
    aspect_preferred: List[str]  # ["N", "NE", "E", etc.]
    elevation_min: float  # m
    elevation_max: float  # m
    terrain_types: List[str]  # ["valley", "ridge", "plateau", etc.]

@dataclass
class HydrologyConditions:
    """Conditions hydrologiques"""
    distance_to_water_min: float  # m
    distance_to_water_max: float  # m
    water_types: List[str]  # ["lake", "river", "stream", "wetland"]
    wetland_affinity: float  # 0-1

@dataclass
class HumanPressureConditions:
    """Conditions de pression humaine"""
    distance_to_roads_min: float  # m
    max_human_pressure: float  # 0-1
    avoid_urban: bool
    avoid_agriculture: bool

@dataclass
class AlgorithmicCriteria:
    """Critères algorithmiques V8-ready"""
    ndvi_min: float
    ndvi_max: float
    ndvi_optimal: float
    landcover_codes: List[int]
    score_weights: Dict[str, float]
    corridor_cost: float  # Pour A*
    bce_rules: List[str]

@dataclass
class SeasonalFood:
    """Nourriture par saison"""
    spring: List[str]
    summer: List[str]
    autumn: List[str]
    winter: List[str]

@dataclass
class EcologicalZone:
    """Zone écologique complète"""
    species: Species
    zone_type: ZoneType
    
    # Habitat
    habitat: HabitatConditions
    topography: TopographyConditions
    hydrology: HydrologyConditions
    human_pressure: HumanPressureConditions
    
    # Écologie
    food_sources: SeasonalFood
    microclimate: Dict[str, Any]
    ecological_connectivity: float  # 0-100
    
    # Indices terrain
    terrain_indices: List[str]
    functional_role: str
    
    # Algorithmique
    criteria: AlgorithmicCriteria
    
    # Métadonnées
    description: str
    scientific_sources: List[str]


# =====================================================================
# BASE ÉCOLOGIQUE — ORIGNAL
# =====================================================================

ORIGNAL_ZONES = {
    ZoneType.ALIMENTATION: EcologicalZone(
        species=Species.ORIGNAL,
        zone_type=ZoneType.ALIMENTATION,
        habitat=HabitatConditions(
            forest_type=[ForestType.MIXTE, ForestType.FEUILLU, ForestType.REGENERATION],
            canopy_cover_min=30,
            canopy_cover_max=70,
            understory_density="dense",
            ground_cover=["willow", "birch", "aspen", "aquatic_plants"]
        ),
        topography=TopographyConditions(
            slope_min=0,
            slope_max=15,
            aspect_preferred=["S", "SE", "SW"],
            elevation_min=100,
            elevation_max=800,
            terrain_types=["valley", "lowland", "wetland_edge"]
        ),
        hydrology=HydrologyConditions(
            distance_to_water_min=0,
            distance_to_water_max=500,
            water_types=["lake", "pond", "wetland", "stream"],
            wetland_affinity=0.9
        ),
        human_pressure=HumanPressureConditions(
            distance_to_roads_min=200,
            max_human_pressure=0.3,
            avoid_urban=True,
            avoid_agriculture=False
        ),
        food_sources=SeasonalFood(
            spring=["willow_catkins", "aquatic_plants", "sedges", "new_shoots"],
            summer=["aquatic_vegetation", "willow", "birch", "aspen_leaves"],
            autumn=["willow", "birch", "mountain_ash", "twigs"],
            winter=["balsam_fir", "cedar", "willow_twigs", "bark"]
        ),
        microclimate={
            "temperature_preference": "cool",
            "wind_shelter": "moderate",
            "humidity": "high",
            "thermal_cover": True
        },
        ecological_connectivity=85,
        terrain_indices=["fresh_browse", "tracks", "droppings", "bed_depressions"],
        functional_role="Primary foraging area - High energy intake zone",
        criteria=AlgorithmicCriteria(
            ndvi_min=0.4,
            ndvi_max=0.8,
            ndvi_optimal=0.65,
            landcover_codes=[41, 42, 43, 90, 95],  # Mixed/Deciduous forest, Wetlands
            score_weights={
                "ndvi": 0.20,
                "water_proximity": 0.25,
                "canopy": 0.15,
                "slope": 0.10,
                "human_pressure": 0.15,
                "connectivity": 0.15
            },
            corridor_cost=1.5,
            bce_rules=["water_proximity_valid", "canopy_threshold_valid", "ndvi_range_valid"]
        ),
        description="Zone d'alimentation principale de l'orignal - Broutage intensif près des plans d'eau",
        scientific_sources=["MFFP-QC-2023", "Renecker-1987", "Peek-1997"]
    ),
    
    ZoneType.REPOS: EcologicalZone(
        species=Species.ORIGNAL,
        zone_type=ZoneType.REPOS,
        habitat=HabitatConditions(
            forest_type=[ForestType.CONIFERE, ForestType.MIXTE, ForestType.MATURE],
            canopy_cover_min=60,
            canopy_cover_max=90,
            understory_density="moderate",
            ground_cover=["moss", "needles", "fern"]
        ),
        topography=TopographyConditions(
            slope_min=5,
            slope_max=25,
            aspect_preferred=["N", "NE", "NW"],
            elevation_min=200,
            elevation_max=900,
            terrain_types=["ridge", "knoll", "slope"]
        ),
        hydrology=HydrologyConditions(
            distance_to_water_min=100,
            distance_to_water_max=1000,
            water_types=["stream", "lake"],
            wetland_affinity=0.3
        ),
        human_pressure=HumanPressureConditions(
            distance_to_roads_min=500,
            max_human_pressure=0.15,
            avoid_urban=True,
            avoid_agriculture=True
        ),
        food_sources=SeasonalFood(
            spring=[], summer=[], autumn=[], winter=[]  # Not primary function
        ),
        microclimate={
            "temperature_preference": "cool",
            "wind_shelter": "high",
            "humidity": "moderate",
            "thermal_cover": True
        },
        ecological_connectivity=70,
        terrain_indices=["bed_sites", "rub_trees", "trails", "hair_samples"],
        functional_role="Thermal refuge and rest area - Energy conservation zone",
        criteria=AlgorithmicCriteria(
            ndvi_min=0.5,
            ndvi_max=0.85,
            ndvi_optimal=0.7,
            landcover_codes=[42, 43],  # Evergreen/Mixed forest
            score_weights={
                "ndvi": 0.15,
                "canopy": 0.30,
                "slope": 0.15,
                "aspect": 0.15,
                "human_pressure": 0.25
            },
            corridor_cost=2.0,
            bce_rules=["canopy_minimum_valid", "slope_range_valid", "human_distance_valid"]
        ),
        description="Zone de repos et couvert thermique - Protection contre prédateurs et intempéries",
        scientific_sources=["Schwartz-1992", "Dussault-2005", "MFFP-QC-2023"]
    ),
    
    ZoneType.RUT: EcologicalZone(
        species=Species.ORIGNAL,
        zone_type=ZoneType.RUT,
        habitat=HabitatConditions(
            forest_type=[ForestType.MIXTE, ForestType.FEUILLU],
            canopy_cover_min=40,
            canopy_cover_max=70,
            understory_density="moderate",
            ground_cover=["fern", "shrub", "moss"]
        ),
        topography=TopographyConditions(
            slope_min=0,
            slope_max=20,
            aspect_preferred=["S", "SE", "SW", "E", "W"],
            elevation_min=150,
            elevation_max=700,
            terrain_types=["plateau", "gentle_slope", "valley_edge"]
        ),
        hydrology=HydrologyConditions(
            distance_to_water_min=50,
            distance_to_water_max=800,
            water_types=["pond", "wetland", "stream"],
            wetland_affinity=0.7
        ),
        human_pressure=HumanPressureConditions(
            distance_to_roads_min=400,
            max_human_pressure=0.2,
            avoid_urban=True,
            avoid_agriculture=True
        ),
        food_sources=SeasonalFood(
            spring=[], summer=[], 
            autumn=["minimal_during_rut"],
            winter=[]
        ),
        microclimate={
            "temperature_preference": "cool",
            "wind_shelter": "low",  # Bulls prefer open areas for calls
            "humidity": "moderate",
            "thermal_cover": False
        },
        ecological_connectivity=90,
        terrain_indices=["rub_trees", "scrapes", "wallow_pits", "thrashed_vegetation"],
        functional_role="Breeding area - Male display and female aggregation zone",
        criteria=AlgorithmicCriteria(
            ndvi_min=0.35,
            ndvi_max=0.75,
            ndvi_optimal=0.55,
            landcover_codes=[41, 42, 43, 52],  # Forests + Shrubland
            score_weights={
                "ndvi": 0.10,
                "water_proximity": 0.20,
                "openness": 0.25,
                "connectivity": 0.25,
                "human_pressure": 0.20
            },
            corridor_cost=1.0,
            bce_rules=["rut_season_valid", "connectivity_high", "openness_valid"]
        ),
        description="Zone de rut - Activité reproductive intense, souilles et grattages",
        scientific_sources=["Bubenik-1987", "Bowyer-1991", "MFFP-QC-2023"]
    ),
    
    ZoneType.CORRIDOR: EcologicalZone(
        species=Species.ORIGNAL,
        zone_type=ZoneType.CORRIDOR,
        habitat=HabitatConditions(
            forest_type=[ForestType.MIXTE, ForestType.CONIFERE],
            canopy_cover_min=40,
            canopy_cover_max=80,
            understory_density="moderate",
            ground_cover=["shrub", "fern"]
        ),
        topography=TopographyConditions(
            slope_min=0,
            slope_max=15,
            aspect_preferred=["any"],
            elevation_min=100,
            elevation_max=800,
            terrain_types=["valley", "drainage", "ridge_saddle", "plateau"]
        ),
        hydrology=HydrologyConditions(
            distance_to_water_min=0,
            distance_to_water_max=1500,
            water_types=["stream", "drainage"],
            wetland_affinity=0.5
        ),
        human_pressure=HumanPressureConditions(
            distance_to_roads_min=300,
            max_human_pressure=0.25,
            avoid_urban=True,
            avoid_agriculture=False
        ),
        food_sources=SeasonalFood(
            spring=["browse_en_route"],
            summer=["browse_en_route"],
            autumn=["browse_en_route"],
            winter=["browse_en_route"]
        ),
        microclimate={
            "temperature_preference": "any",
            "wind_shelter": "moderate",
            "humidity": "any",
            "thermal_cover": False
        },
        ecological_connectivity=100,
        terrain_indices=["well_worn_trails", "tracks", "droppings_along_path"],
        functional_role="Movement corridor - Connectivity between functional zones",
        criteria=AlgorithmicCriteria(
            ndvi_min=0.3,
            ndvi_max=0.8,
            ndvi_optimal=0.5,
            landcover_codes=[41, 42, 43, 52, 71],
            score_weights={
                "slope": 0.30,
                "continuity": 0.30,
                "human_pressure": 0.20,
                "connectivity": 0.20
            },
            corridor_cost=1.0,
            bce_rules=["continuity_valid", "slope_traversable", "no_barriers"]
        ),
        description="Corridor de déplacement - Connexion entre zones fonctionnelles",
        scientific_sources=["Beier-1998", "Chetkiewicz-2006", "WWF-2020"]
    ),
}

# =====================================================================
# BASE ÉCOLOGIQUE — CHEVREUIL
# =====================================================================

CHEVREUIL_ZONES = {
    ZoneType.ALIMENTATION: EcologicalZone(
        species=Species.CHEVREUIL,
        zone_type=ZoneType.ALIMENTATION,
        habitat=HabitatConditions(
            forest_type=[ForestType.FEUILLU, ForestType.MIXTE, ForestType.REGENERATION],
            canopy_cover_min=20,
            canopy_cover_max=60,
            understory_density="dense",
            ground_cover=["forbs", "shrub", "grass", "agricultural_edge"]
        ),
        topography=TopographyConditions(
            slope_min=0,
            slope_max=20,
            aspect_preferred=["S", "SE", "SW"],
            elevation_min=50,
            elevation_max=600,
            terrain_types=["edge", "clearing", "gentle_slope"]
        ),
        hydrology=HydrologyConditions(
            distance_to_water_min=50,
            distance_to_water_max=800,
            water_types=["stream", "pond"],
            wetland_affinity=0.4
        ),
        human_pressure=HumanPressureConditions(
            distance_to_roads_min=100,
            max_human_pressure=0.4,
            avoid_urban=True,
            avoid_agriculture=False  # Uses agricultural edges
        ),
        food_sources=SeasonalFood(
            spring=["clover", "alfalfa", "new_shoots", "forbs"],
            summer=["agricultural_crops", "forbs", "browse", "fruits"],
            autumn=["acorns", "apples", "agricultural_waste", "browse"],
            winter=["cedar", "browse", "bark", "agricultural_residue"]
        ),
        microclimate={
            "temperature_preference": "moderate",
            "wind_shelter": "low",
            "humidity": "moderate",
            "thermal_cover": False
        },
        ecological_connectivity=75,
        terrain_indices=["browse_line", "tracks", "droppings", "bed_sites"],
        functional_role="Primary foraging area - Edge habitat specialist",
        criteria=AlgorithmicCriteria(
            ndvi_min=0.3,
            ndvi_max=0.7,
            ndvi_optimal=0.5,
            landcover_codes=[41, 43, 52, 71, 81, 82],  # Forests + Grass + Agriculture
            score_weights={
                "ndvi": 0.15,
                "edge_proximity": 0.25,
                "canopy": 0.15,
                "slope": 0.10,
                "human_pressure": 0.15,
                "food_availability": 0.20
            },
            corridor_cost=1.5,
            bce_rules=["edge_habitat_valid", "food_sources_valid", "ndvi_range_valid"]
        ),
        description="Zone d'alimentation du chevreuil - Lisières et bordures agricoles",
        scientific_sources=["VerCauteren-2003", "Nixon-1991", "MFFP-QC-2023"]
    ),
    
    ZoneType.REPOS: EcologicalZone(
        species=Species.CHEVREUIL,
        zone_type=ZoneType.REPOS,
        habitat=HabitatConditions(
            forest_type=[ForestType.CONIFERE, ForestType.MIXTE],
            canopy_cover_min=50,
            canopy_cover_max=85,
            understory_density="dense",
            ground_cover=["needles", "shrub", "grass"]
        ),
        topography=TopographyConditions(
            slope_min=0,
            slope_max=25,
            aspect_preferred=["S", "SW", "SE"],
            elevation_min=50,
            elevation_max=500,
            terrain_types=["thicket", "knoll", "depression"]
        ),
        hydrology=HydrologyConditions(
            distance_to_water_min=100,
            distance_to_water_max=600,
            water_types=["stream", "pond"],
            wetland_affinity=0.3
        ),
        human_pressure=HumanPressureConditions(
            distance_to_roads_min=150,
            max_human_pressure=0.2,
            avoid_urban=True,
            avoid_agriculture=False
        ),
        food_sources=SeasonalFood(
            spring=[], summer=[], autumn=[], winter=[]
        ),
        microclimate={
            "temperature_preference": "warm",
            "wind_shelter": "high",
            "humidity": "low",
            "thermal_cover": True
        },
        ecological_connectivity=60,
        terrain_indices=["bed_sites", "trails", "rub_posts", "scrapes"],
        functional_role="Bedding and thermal refuge - Security cover",
        criteria=AlgorithmicCriteria(
            ndvi_min=0.45,
            ndvi_max=0.8,
            ndvi_optimal=0.65,
            landcover_codes=[42, 43],
            score_weights={
                "canopy": 0.30,
                "understory": 0.25,
                "human_pressure": 0.25,
                "thermal": 0.20
            },
            corridor_cost=2.5,
            bce_rules=["canopy_minimum_valid", "security_cover_valid"]
        ),
        description="Zone de repos et couvert de sécurité du chevreuil",
        scientific_sources=["Beier-1987", "Kilpatrick-1988", "MFFP-QC-2023"]
    ),
    
    ZoneType.RUT: EcologicalZone(
        species=Species.CHEVREUIL,
        zone_type=ZoneType.RUT,
        habitat=HabitatConditions(
            forest_type=[ForestType.MIXTE, ForestType.FEUILLU],
            canopy_cover_min=30,
            canopy_cover_max=65,
            understory_density="moderate",
            ground_cover=["shrub", "grass", "forbs"]
        ),
        topography=TopographyConditions(
            slope_min=0,
            slope_max=15,
            aspect_preferred=["S", "SE", "SW"],
            elevation_min=50,
            elevation_max=400,
            terrain_types=["edge", "funnel", "saddle"]
        ),
        hydrology=HydrologyConditions(
            distance_to_water_min=50,
            distance_to_water_max=500,
            water_types=["stream", "pond"],
            wetland_affinity=0.4
        ),
        human_pressure=HumanPressureConditions(
            distance_to_roads_min=200,
            max_human_pressure=0.25,
            avoid_urban=True,
            avoid_agriculture=False
        ),
        food_sources=SeasonalFood(
            spring=[], summer=[], 
            autumn=["secondary_during_rut"],
            winter=[]
        ),
        microclimate={
            "temperature_preference": "cool",
            "wind_shelter": "low",
            "humidity": "moderate",
            "thermal_cover": False
        },
        ecological_connectivity=85,
        terrain_indices=["scrapes", "rubs", "trails", "licking_branches"],
        functional_role="Breeding signpost area - Buck signaling zone",
        criteria=AlgorithmicCriteria(
            ndvi_min=0.3,
            ndvi_max=0.65,
            ndvi_optimal=0.45,
            landcover_codes=[41, 43, 52, 71],
            score_weights={
                "funnel_factor": 0.30,
                "connectivity": 0.25,
                "edge_proximity": 0.20,
                "human_pressure": 0.25
            },
            corridor_cost=1.0,
            bce_rules=["rut_season_valid", "funnel_geometry_valid"]
        ),
        description="Zone de rut du chevreuil - Grattages et frottoirs",
        scientific_sources=["Marchinton-1990", "Miller-1987", "MFFP-QC-2023"]
    ),
    
    ZoneType.CORRIDOR: EcologicalZone(
        species=Species.CHEVREUIL,
        zone_type=ZoneType.CORRIDOR,
        habitat=HabitatConditions(
            forest_type=[ForestType.MIXTE, ForestType.FEUILLU],
            canopy_cover_min=30,
            canopy_cover_max=70,
            understory_density="moderate",
            ground_cover=["shrub", "grass"]
        ),
        topography=TopographyConditions(
            slope_min=0,
            slope_max=20,
            aspect_preferred=["any"],
            elevation_min=50,
            elevation_max=500,
            terrain_types=["fenceline", "hedgerow", "drainage", "edge"]
        ),
        hydrology=HydrologyConditions(
            distance_to_water_min=0,
            distance_to_water_max=1000,
            water_types=["stream", "drainage"],
            wetland_affinity=0.4
        ),
        human_pressure=HumanPressureConditions(
            distance_to_roads_min=50,
            max_human_pressure=0.35,
            avoid_urban=True,
            avoid_agriculture=False
        ),
        food_sources=SeasonalFood(
            spring=["browse_en_route"],
            summer=["browse_en_route"],
            autumn=["browse_en_route"],
            winter=["browse_en_route"]
        ),
        microclimate={
            "temperature_preference": "any",
            "wind_shelter": "moderate",
            "humidity": "any",
            "thermal_cover": False
        },
        ecological_connectivity=100,
        terrain_indices=["trails", "tracks", "fence_crossings"],
        functional_role="Movement corridor - Linear habitat connectors",
        criteria=AlgorithmicCriteria(
            ndvi_min=0.25,
            ndvi_max=0.7,
            ndvi_optimal=0.45,
            landcover_codes=[41, 43, 52, 71, 81],
            score_weights={
                "linearity": 0.25,
                "cover_continuity": 0.30,
                "human_pressure": 0.20,
                "connectivity": 0.25
            },
            corridor_cost=1.0,
            bce_rules=["continuity_valid", "linear_cover_valid"]
        ),
        description="Corridor de déplacement du chevreuil - Haies et lisières",
        scientific_sources=["Beier-1998", "Nixon-1991", "WWF-2020"]
    ),
}

# =====================================================================
# BASE ÉCOLOGIQUE — OURS NOIR
# =====================================================================

OURS_NOIR_ZONES = {
    ZoneType.ALIMENTATION: EcologicalZone(
        species=Species.OURS_NOIR,
        zone_type=ZoneType.ALIMENTATION,
        habitat=HabitatConditions(
            forest_type=[ForestType.MIXTE, ForestType.FEUILLU, ForestType.MATURE],
            canopy_cover_min=30,
            canopy_cover_max=80,
            understory_density="dense",
            ground_cover=["berry_shrubs", "forbs", "grass"]
        ),
        topography=TopographyConditions(
            slope_min=0,
            slope_max=35,
            aspect_preferred=["S", "SE", "SW"],
            elevation_min=100,
            elevation_max=1200,
            terrain_types=["slope", "valley", "clearing"]
        ),
        hydrology=HydrologyConditions(
            distance_to_water_min=0,
            distance_to_water_max=2000,
            water_types=["stream", "river", "wetland"],
            wetland_affinity=0.6
        ),
        human_pressure=HumanPressureConditions(
            distance_to_roads_min=200,
            max_human_pressure=0.3,
            avoid_urban=True,
            avoid_agriculture=False
        ),
        food_sources=SeasonalFood(
            spring=["skunk_cabbage", "sedges", "insects", "carrion", "new_vegetation"],
            summer=["berries", "insects", "fish", "vegetation", "small_mammals"],
            autumn=["acorns", "beechnuts", "hazelnuts", "berries", "apples"],
            winter=[]  # Hibernation
        ),
        microclimate={
            "temperature_preference": "moderate",
            "wind_shelter": "low",
            "humidity": "moderate",
            "thermal_cover": False
        },
        ecological_connectivity=80,
        terrain_indices=["scat", "claw_marks", "overturned_logs", "ant_hills_dug"],
        functional_role="Primary foraging area - Hyperphagia preparation zone",
        criteria=AlgorithmicCriteria(
            ndvi_min=0.35,
            ndvi_max=0.85,
            ndvi_optimal=0.6,
            landcover_codes=[41, 42, 43, 52, 90],
            score_weights={
                "ndvi": 0.15,
                "food_diversity": 0.30,
                "human_pressure": 0.20,
                "slope": 0.10,
                "season": 0.25
            },
            corridor_cost=1.5,
            bce_rules=["food_sources_valid", "season_appropriate", "human_distance_valid"]
        ),
        description="Zone d'alimentation de l'ours noir - Préparation à l'hibernation",
        scientific_sources=["Rogers-1987", "Pelton-2003", "MFFP-QC-2023"]
    ),
    
    ZoneType.REPOS: EcologicalZone(
        species=Species.OURS_NOIR,
        zone_type=ZoneType.REPOS,
        habitat=HabitatConditions(
            forest_type=[ForestType.CONIFERE, ForestType.MIXTE, ForestType.MATURE],
            canopy_cover_min=50,
            canopy_cover_max=95,
            understory_density="dense",
            ground_cover=["deadfall", "shrub", "moss"]
        ),
        topography=TopographyConditions(
            slope_min=10,
            slope_max=45,
            aspect_preferred=["N", "NE", "NW"],
            elevation_min=200,
            elevation_max=1000,
            terrain_types=["steep_slope", "ravine", "thicket"]
        ),
        hydrology=HydrologyConditions(
            distance_to_water_min=100,
            distance_to_water_max=1500,
            water_types=["stream"],
            wetland_affinity=0.2
        ),
        human_pressure=HumanPressureConditions(
            distance_to_roads_min=500,
            max_human_pressure=0.1,
            avoid_urban=True,
            avoid_agriculture=True
        ),
        food_sources=SeasonalFood(
            spring=[], summer=[], autumn=[], winter=[]
        ),
        microclimate={
            "temperature_preference": "cool",
            "wind_shelter": "high",
            "humidity": "moderate",
            "thermal_cover": True
        },
        ecological_connectivity=50,
        terrain_indices=["day_beds", "escape_trees", "claw_marks_on_trees"],
        functional_role="Day bedding and escape terrain - Security zone",
        criteria=AlgorithmicCriteria(
            ndvi_min=0.5,
            ndvi_max=0.9,
            ndvi_optimal=0.75,
            landcover_codes=[42, 43],
            score_weights={
                "canopy": 0.25,
                "slope": 0.25,
                "human_pressure": 0.30,
                "escape_terrain": 0.20
            },
            corridor_cost=3.0,
            bce_rules=["canopy_dense_valid", "escape_terrain_valid", "isolation_valid"]
        ),
        description="Zone de repos diurne de l'ours noir - Terrain d'évasion",
        scientific_sources=["Alt-1984", "Pelton-2003", "MFFP-QC-2023"]
    ),
    
    ZoneType.TANIERE: EcologicalZone(
        species=Species.OURS_NOIR,
        zone_type=ZoneType.TANIERE,
        habitat=HabitatConditions(
            forest_type=[ForestType.CONIFERE, ForestType.MIXTE],
            canopy_cover_min=40,
            canopy_cover_max=90,
            understory_density="moderate",
            ground_cover=["deadfall", "rock", "root_mass"]
        ),
        topography=TopographyConditions(
            slope_min=15,
            slope_max=60,
            aspect_preferred=["N", "NE", "NW"],
            elevation_min=300,
            elevation_max=1200,
            terrain_types=["steep_slope", "rock_outcrop", "root_cavity"]
        ),
        hydrology=HydrologyConditions(
            distance_to_water_min=200,
            distance_to_water_max=2000,
            water_types=["stream"],
            wetland_affinity=0.1
        ),
        human_pressure=HumanPressureConditions(
            distance_to_roads_min=800,
            max_human_pressure=0.05,
            avoid_urban=True,
            avoid_agriculture=True
        ),
        food_sources=SeasonalFood(
            spring=[], summer=[], autumn=[], winter=[]
        ),
        microclimate={
            "temperature_preference": "stable",
            "wind_shelter": "maximum",
            "humidity": "low",
            "thermal_cover": True
        },
        ecological_connectivity=30,
        terrain_indices=["excavated_cavity", "hair_on_entrance", "worn_entrance"],
        functional_role="Winter den site - Hibernation chamber",
        criteria=AlgorithmicCriteria(
            ndvi_min=0.4,
            ndvi_max=0.85,
            ndvi_optimal=0.6,
            landcover_codes=[42, 43, 31],  # Forest + Rock
            score_weights={
                "slope": 0.25,
                "aspect": 0.20,
                "isolation": 0.30,
                "drainage": 0.15,
                "substrate": 0.10
            },
            corridor_cost=5.0,  # High cost - avoid disturbing
            bce_rules=["den_isolation_valid", "slope_steep_valid", "drainage_good"]
        ),
        description="Site de tanière d'hibernation de l'ours noir",
        scientific_sources=["Johnson-1978", "Pelton-2003", "MFFP-QC-2023"]
    ),
    
    ZoneType.CORRIDOR: EcologicalZone(
        species=Species.OURS_NOIR,
        zone_type=ZoneType.CORRIDOR,
        habitat=HabitatConditions(
            forest_type=[ForestType.MIXTE, ForestType.CONIFERE],
            canopy_cover_min=30,
            canopy_cover_max=80,
            understory_density="moderate",
            ground_cover=["shrub", "deadfall"]
        ),
        topography=TopographyConditions(
            slope_min=0,
            slope_max=30,
            aspect_preferred=["any"],
            elevation_min=100,
            elevation_max=1000,
            terrain_types=["valley", "ridge", "drainage", "saddle"]
        ),
        hydrology=HydrologyConditions(
            distance_to_water_min=0,
            distance_to_water_max=2000,
            water_types=["stream", "river", "drainage"],
            wetland_affinity=0.5
        ),
        human_pressure=HumanPressureConditions(
            distance_to_roads_min=300,
            max_human_pressure=0.25,
            avoid_urban=True,
            avoid_agriculture=False
        ),
        food_sources=SeasonalFood(
            spring=["opportunistic"],
            summer=["opportunistic"],
            autumn=["opportunistic"],
            winter=[]
        ),
        microclimate={
            "temperature_preference": "any",
            "wind_shelter": "moderate",
            "humidity": "any",
            "thermal_cover": False
        },
        ecological_connectivity=100,
        terrain_indices=["trails", "scat", "claw_marks", "rub_trees"],
        functional_role="Travel corridor - Large-scale connectivity",
        criteria=AlgorithmicCriteria(
            ndvi_min=0.3,
            ndvi_max=0.8,
            ndvi_optimal=0.5,
            landcover_codes=[41, 42, 43, 52, 90],
            score_weights={
                "continuity": 0.30,
                "cover": 0.25,
                "human_pressure": 0.25,
                "topography": 0.20
            },
            corridor_cost=1.0,
            bce_rules=["continuity_valid", "cover_continuous", "low_human_pressure"]
        ),
        description="Corridor de déplacement de l'ours noir - Grande échelle",
        scientific_sources=["Rogers-1987", "Beier-1998", "WWF-2020"]
    ),
}


# =====================================================================
# REGISTRE ÉCOLOGIQUE GLOBAL
# =====================================================================

class EcologicalDatabase:
    """
    Base de données écologique V8 - Singleton
    Accès unifié aux zones écologiques des 3 espèces
    """
    
    def __init__(self):
        self.species_zones = {
            Species.ORIGNAL: ORIGNAL_ZONES,
            Species.CHEVREUIL: CHEVREUIL_ZONES,
            Species.OURS_NOIR: OURS_NOIR_ZONES,
        }
        self.logger = logging.getLogger("bionic_engine.ecological_database")
    
    def get_zone(self, species: Species, zone_type: ZoneType) -> Optional[EcologicalZone]:
        """Récupère une zone écologique spécifique"""
        species_data = self.species_zones.get(species)
        if not species_data:
            return None
        return species_data.get(zone_type)
    
    def get_all_zones_for_species(self, species: Species) -> Dict[ZoneType, EcologicalZone]:
        """Récupère toutes les zones d'une espèce"""
        return self.species_zones.get(species, {})
    
    def get_algorithmic_criteria(self, species: Species, zone_type: ZoneType) -> Optional[AlgorithmicCriteria]:
        """Récupère les critères algorithmiques V8-ready"""
        zone = self.get_zone(species, zone_type)
        if zone:
            return zone.criteria
        return None
    
    def get_corridor_cost(self, species: Species, zone_type: ZoneType) -> float:
        """Récupère le coût corridor pour A*"""
        zone = self.get_zone(species, zone_type)
        if zone and zone.criteria:
            return zone.criteria.corridor_cost
        return 2.0  # Coût par défaut
    
    def get_bce_rules(self, species: Species, zone_type: ZoneType) -> List[str]:
        """Récupère les règles BCE pour validation"""
        zone = self.get_zone(species, zone_type)
        if zone and zone.criteria:
            return zone.criteria.bce_rules
        return []
    
    def validate_zone_conditions(
        self,
        species: Species,
        zone_type: ZoneType,
        conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Valide si les conditions terrain correspondent à une zone écologique
        
        Args:
            species: Espèce cible
            zone_type: Type de zone
            conditions: Conditions terrain mesurées
            
        Returns:
            Dict avec score de correspondance et détails
        """
        zone = self.get_zone(species, zone_type)
        if not zone:
            return {"valid": False, "score": 0, "reason": "Zone not found"}
        
        criteria = zone.criteria
        score = 0
        details = []
        
        # Validation NDVI
        ndvi = conditions.get("ndvi", 0)
        if criteria.ndvi_min <= ndvi <= criteria.ndvi_max:
            ndvi_score = 100 - abs(ndvi - criteria.ndvi_optimal) * 100
            score += ndvi_score * criteria.score_weights.get("ndvi", 0.15)
            details.append(f"NDVI: {ndvi:.2f} (optimal: {criteria.ndvi_optimal})")
        
        # Validation pente
        slope = conditions.get("slope", 0)
        topo = zone.topography
        if topo.slope_min <= slope <= topo.slope_max:
            score += 80 * criteria.score_weights.get("slope", 0.15)
            details.append(f"Slope: {slope}% (range: {topo.slope_min}-{topo.slope_max}%)")
        
        # Validation distance eau
        water_dist = conditions.get("distance_to_water", 0)
        hydro = zone.hydrology
        if hydro.distance_to_water_min <= water_dist <= hydro.distance_to_water_max:
            score += 90 * criteria.score_weights.get("water_proximity", 0.15)
            details.append(f"Water distance: {water_dist}m")
        
        # Validation pression humaine
        human_pressure = conditions.get("human_pressure", 0)
        if human_pressure <= zone.human_pressure.max_human_pressure:
            score += 100 * criteria.score_weights.get("human_pressure", 0.20)
            details.append(f"Human pressure: {human_pressure:.2f}")
        
        return {
            "valid": score >= 50,
            "score": round(score, 1),
            "zone_type": zone_type.value,
            "species": species.value,
            "details": details,
            "functional_role": zone.functional_role
        }
    
    def export_to_json(self) -> Dict[str, Any]:
        """Exporte la base écologique en JSON pour le frontend"""
        result = {}
        for species, zones in self.species_zones.items():
            result[species.value] = {}
            for zone_type, zone in zones.items():
                result[species.value][zone_type.value] = {
                    "description": zone.description,
                    "functional_role": zone.functional_role,
                    "habitat": {
                        "forest_types": [ft.value for ft in zone.habitat.forest_type],
                        "canopy_cover": f"{zone.habitat.canopy_cover_min}-{zone.habitat.canopy_cover_max}%",
                        "understory": zone.habitat.understory_density
                    },
                    "topography": {
                        "slope": f"{zone.topography.slope_min}-{zone.topography.slope_max}%",
                        "terrain_types": zone.topography.terrain_types
                    },
                    "criteria": {
                        "ndvi_range": f"{zone.criteria.ndvi_min}-{zone.criteria.ndvi_max}",
                        "corridor_cost": zone.criteria.corridor_cost,
                        "bce_rules": zone.criteria.bce_rules
                    },
                    "terrain_indices": zone.terrain_indices,
                    "scientific_sources": zone.scientific_sources
                }
        return result


# Instance singleton
ecological_database = EcologicalDatabase()
