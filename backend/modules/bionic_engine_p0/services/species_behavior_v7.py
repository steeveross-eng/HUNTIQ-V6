"""
BIONIC V7 — Species Behavior V7
Matrices comportementales detaillees par espece, saison, sexe et besoin.

Source de verite pour:
  - Besoins par espece (alimentation, repos, rut, refuge chaleur/pression)
  - Facteurs par sexe (male vs femelle: rayons, tolerances, preferences)
  - Modificateurs saisonniers
  - Parametres corridors (cout grille male/femelle)

100% independant. Consomme par zone_typology_v7 et corridor_v7.
"""

from typing import Dict


# =====================================================================
# BESOINS PAR ESPECE — facteurs de scoring par type de zone (0.0-2.0)
# =====================================================================

SPECIES_NEEDS: Dict[str, Dict[str, Dict[str, float]]] = {
    "moose": {
        "feed": {
            "mixed_cover": 1.4, "edge_proximity": 1.3, "water_proximity": 1.2,
            "regeneration": 1.5, "wetland_positive": 1.3, "elevation_low": 1.1,
            "slope_gentle": 1.1, "road_distance": 0.8,
        },
        "rest": {
            "canopy_dense": 1.4, "conifer_mature": 1.3, "slope_gentle": 1.2,
            "road_distance": 1.3, "wind_shelter": 1.2, "elevation_mid": 1.0,
            "water_proximity": 0.9, "urban_distance": 1.2,
        },
        "rut": {
            "open_area": 1.4, "water_proximity": 1.3, "wetland_positive": 1.5,
            "visibility": 1.3, "edge_proximity": 1.2, "road_distance": 1.0,
            "slope_gentle": 1.1, "elevation_low": 1.0,
        },
        "heat_ref": {
            "canopy_dense": 1.5, "north_aspect": 1.4, "water_proximity": 1.5,
            "elevation_high": 1.3, "shade": 1.4, "road_distance": 1.0,
            "wind_exposure": 0.7, "slope_gentle": 1.0,
        },
        "hunt_ref": {
            "canopy_dense": 1.5, "road_distance": 1.6, "terrain_rugged": 1.4,
            "urban_distance": 1.5, "elevation_high": 1.2, "slope_steep": 1.1,
            "water_proximity": 0.9, "visibility": 0.6,
        },
    },
    "deer": {
        "feed": {
            "mixed_cover": 1.3, "edge_proximity": 1.5, "fallow_field": 1.4,
            "orchard": 1.3, "clearing": 1.3, "water_proximity": 1.0,
            "slope_gentle": 1.2, "south_aspect": 1.1,
        },
        "rest": {
            "understory_dense": 1.5, "conifer_low": 1.4, "south_aspect": 1.2,
            "wind_shelter": 1.4, "road_distance": 1.2, "slope_gentle": 1.1,
            "canopy_dense": 1.2, "urban_distance": 1.0,
        },
        "rut": {
            "edge_proximity": 1.6, "scrape_area": 1.5, "rub_area": 1.5,
            "funnel": 1.4, "mixed_cover": 1.2, "water_proximity": 1.0,
            "road_distance": 1.0, "visibility": 1.1,
        },
        "heat_ref": {
            "deciduous_mature": 1.4, "stream_proximity": 1.5, "north_aspect": 1.3,
            "canopy_dense": 1.3, "shade": 1.3, "wind_shelter": 1.0,
            "elevation_mid": 1.0, "road_distance": 1.0,
        },
        "hunt_ref": {
            "canopy_dense": 1.5, "understory_dense": 1.6, "ravage": 1.5,
            "road_distance": 1.4, "urban_distance": 1.3, "terrain_rugged": 1.1,
            "water_proximity": 0.9, "slope_steep": 1.0,
        },
    },
    "bear": {
        "feed": {
            "berry_zone": 1.8, "mast_tree": 1.5, "stream_fish": 1.4,
            "post_fire": 1.5, "clearing": 1.2, "water_proximity": 1.3,
            "elevation_mid": 1.1, "slope_gentle": 1.0,
        },
        "rest": {
            "mature_forest": 1.3, "rocky_terrain": 1.4, "den_site": 1.5,
            "slope_steep": 1.3, "road_distance": 1.4, "urban_distance": 1.5,
            "canopy_dense": 1.2, "elevation_high": 1.1,
        },
        "heat_ref": {
            "canopy_dense": 1.4, "water_proximity": 1.5, "north_aspect": 1.3,
            "elevation_high": 1.4, "shade": 1.3, "stream_proximity": 1.4,
            "wind_shelter": 0.9, "road_distance": 1.0,
        },
        "hunt_ref": {
            "terrain_rugged": 1.6, "urban_distance": 1.5, "elevation_high": 1.4,
            "canopy_dense": 1.4, "road_distance": 1.5, "slope_steep": 1.3,
            "water_proximity": 0.8, "visibility": 0.5,
        },
    },
    "elk": {
        "feed": {
            "grassland": 1.5, "pasture": 1.4, "meadow": 1.4,
            "herbaceous": 1.3, "edge_proximity": 1.2, "water_proximity": 1.1,
            "elevation_mid": 1.1, "slope_gentle": 1.2,
        },
        "rest": {
            "open_forest": 1.3, "slope_gentle": 1.2, "water_proximity": 1.1,
            "canopy_moderate": 1.2, "road_distance": 1.2, "elevation_mid": 1.1,
            "wind_shelter": 1.1, "urban_distance": 1.0,
        },
        "rut": {
            "open_area": 1.6, "grassland": 1.5, "clearing": 1.4,
            "bugling_arena": 1.5, "visibility": 1.3, "water_proximity": 1.1,
            "edge_proximity": 1.2, "slope_gentle": 1.1,
        },
        "heat_ref": {
            "canopy_dense": 1.3, "water_proximity": 1.4, "north_aspect": 1.3,
            "elevation_high": 1.4, "shade": 1.3, "wind_shelter": 1.0,
            "stream_proximity": 1.3, "road_distance": 1.0,
        },
        "hunt_ref": {
            "canopy_dense": 1.4, "elevation_high": 1.5, "terrain_rugged": 1.3,
            "road_distance": 1.6, "urban_distance": 1.4, "slope_steep": 1.2,
            "water_proximity": 0.9, "visibility": 0.6,
        },
    },
    "wild_turkey": {
        "feed": {
            "oak_mast": 1.5, "clearing": 1.4, "edge_proximity": 1.5,
            "fallow_field": 1.4, "orchard": 1.3, "water_proximity": 1.0,
            "slope_gentle": 1.2, "south_aspect": 1.1,
        },
        "rest": {
            "canopy_dense": 1.4, "conifer_mature": 1.3, "elevation_mid": 1.1,
            "road_distance": 1.2, "urban_distance": 1.1, "slope_gentle": 1.0,
            "wind_shelter": 1.2, "roost_tree": 1.5,
        },
        "rut": {
            "open_area": 1.5, "clearing": 1.4, "edge_proximity": 1.3,
            "visibility": 1.4, "strutting_ground": 1.5, "water_proximity": 0.9,
            "slope_gentle": 1.2, "south_aspect": 1.1,
        },
        "heat_ref": {
            "canopy_dense": 1.4, "water_proximity": 1.3, "shade": 1.3,
            "north_aspect": 1.2, "stream_proximity": 1.2, "road_distance": 1.0,
            "elevation_mid": 1.1, "wind_shelter": 1.0,
        },
        "hunt_ref": {
            "canopy_dense": 1.5, "terrain_rugged": 1.2, "road_distance": 1.4,
            "urban_distance": 1.3, "elevation_mid": 1.1, "slope_moderate": 1.0,
            "water_proximity": 0.8, "visibility": 0.5,
        },
    },
}


# =====================================================================
# PARAMETRES PAR SEXE
# =====================================================================

SEX_PARAMS: Dict[str, Dict[str, Dict[str, float]]] = {
    "moose": {
        "male": {
            "daily_range_km": 5.0, "rut_range_km": 12.0,
            "exposure_tolerance": 0.8, "cover_preference": 0.5,
            "slope_tolerance": 0.8, "nocturnal_activity": 0.7,
            "min_road_distance_m": 200, "min_urban_distance_m": 500,
            "corridor_width_m": 100,
        },
        "female": {
            "daily_range_km": 2.5, "rut_range_km": 3.0,
            "exposure_tolerance": 0.4, "cover_preference": 0.8,
            "slope_tolerance": 0.5, "nocturnal_activity": 0.5,
            "min_road_distance_m": 400, "min_urban_distance_m": 800,
            "corridor_width_m": 60,
        },
    },
    "deer": {
        "male": {
            "daily_range_km": 4.0, "rut_range_km": 10.0,
            "exposure_tolerance": 0.7, "cover_preference": 0.5,
            "slope_tolerance": 0.7, "nocturnal_activity": 0.8,
            "min_road_distance_m": 150, "min_urban_distance_m": 400,
            "corridor_width_m": 80,
        },
        "female": {
            "daily_range_km": 2.0, "rut_range_km": 2.5,
            "exposure_tolerance": 0.3, "cover_preference": 0.85,
            "slope_tolerance": 0.4, "nocturnal_activity": 0.5,
            "min_road_distance_m": 350, "min_urban_distance_m": 700,
            "corridor_width_m": 50,
        },
    },
    "bear": {
        "male": {
            "daily_range_km": 8.0, "rut_range_km": 15.0,
            "exposure_tolerance": 0.7, "cover_preference": 0.5,
            "slope_tolerance": 0.9, "nocturnal_activity": 0.6,
            "min_road_distance_m": 300, "min_urban_distance_m": 800,
            "corridor_width_m": 120,
        },
        "female": {
            "daily_range_km": 4.0, "rut_range_km": 4.0,
            "exposure_tolerance": 0.4, "cover_preference": 0.7,
            "slope_tolerance": 0.6, "nocturnal_activity": 0.5,
            "min_road_distance_m": 500, "min_urban_distance_m": 1000,
            "corridor_width_m": 70,
        },
    },
    "elk": {
        "male": {
            "daily_range_km": 6.0, "rut_range_km": 12.0,
            "exposure_tolerance": 0.8, "cover_preference": 0.4,
            "slope_tolerance": 0.8, "nocturnal_activity": 0.5,
            "min_road_distance_m": 250, "min_urban_distance_m": 600,
            "corridor_width_m": 110,
        },
        "female": {
            "daily_range_km": 3.0, "rut_range_km": 3.0,
            "exposure_tolerance": 0.4, "cover_preference": 0.7,
            "slope_tolerance": 0.5, "nocturnal_activity": 0.4,
            "min_road_distance_m": 450, "min_urban_distance_m": 900,
            "corridor_width_m": 60,
        },
    },
}


# =====================================================================
# MODIFICATEURS SAISONNIERS (mois → facteur par type de zone)
# =====================================================================

SEASON_MODIFIERS: Dict[str, Dict[int, float]] = {
    "feed":     {1: 0.6, 2: 0.6, 3: 0.7, 4: 0.8, 5: 1.0, 6: 1.1, 7: 1.0, 8: 0.9, 9: 1.0, 10: 1.0, 11: 0.8, 12: 0.6},
    "rest":     {1: 1.3, 2: 1.3, 3: 1.1, 4: 0.9, 5: 0.8, 6: 0.8, 7: 0.9, 8: 0.9, 9: 0.9, 10: 1.0, 11: 1.1, 12: 1.3},
    "rut":      {1: 0.1, 2: 0.1, 3: 0.1, 4: 0.1, 5: 0.1, 6: 0.2, 7: 0.3, 8: 0.5, 9: 1.5, 10: 2.0, 11: 1.2, 12: 0.2},
    "heat_ref": {1: 0.0, 2: 0.0, 3: 0.2, 4: 0.4, 5: 0.7, 6: 1.2, 7: 1.8, 8: 1.5, 9: 0.8, 10: 0.3, 11: 0.0, 12: 0.0},
    "hunt_ref": {1: 0.3, 2: 0.3, 3: 0.3, 4: 0.3, 5: 0.4, 6: 0.4, 7: 0.4, 8: 0.5, 9: 1.2, 10: 1.5, 11: 1.8, 12: 1.0},
    "corridor": {1: 0.7, 2: 0.7, 3: 0.8, 4: 0.9, 5: 1.0, 6: 1.0, 7: 1.0, 8: 1.0, 9: 1.2, 10: 1.3, 11: 1.1, 12: 0.8},
}


# =====================================================================
# GRILLE DE COUT CORRIDORS A* (par feature terrain)
# =====================================================================

CORRIDOR_COST_GRID: Dict[str, Dict[str, float]] = {
    "male": {
        "dense_forest": 1.0, "open_forest": 0.8, "clearing": 0.6,
        "edge": 0.5, "valley_floor": 0.4, "ridge": 0.7,
        "steep_slope": 1.5, "water_near": 0.6, "road_near": 2.0,
        "urban": 10.0, "pass_saddle": 0.3, "wetland": 0.8,
        "stream_corridor": 0.5,
    },
    "female": {
        "dense_forest": 0.7, "open_forest": 1.0, "clearing": 1.5,
        "edge": 0.6, "valley_floor": 0.5, "ridge": 1.3,
        "steep_slope": 2.5, "water_near": 0.5, "road_near": 3.0,
        "urban": 10.0, "pass_saddle": 0.4, "wetland": 1.2,
        "stream_corridor": 0.6,
    },
}


# =====================================================================
# MODIFICATEURS METEO (condition → facteur par type de zone)
# =====================================================================

WEATHER_MODIFIERS: Dict[str, Dict[str, float]] = {
    "high_wind": {"feed": 0.6, "rest": 0.8, "rut": 0.5, "heat_ref": 0.8, "hunt_ref": 1.3, "corridor": 0.7},
    "rain": {"feed": 0.7, "rest": 1.3, "rut": 0.6, "heat_ref": 1.0, "hunt_ref": 1.1, "corridor": 0.8},
    "cold": {"feed": 0.8, "rest": 1.5, "rut": 0.7, "heat_ref": 0.3, "hunt_ref": 1.2, "corridor": 0.5},
    "heat": {"feed": 0.7, "rest": 0.6, "rut": 0.5, "heat_ref": 2.0, "hunt_ref": 1.0, "corridor": 0.6},
    "snow": {"feed": 0.5, "rest": 1.4, "rut": 0.4, "heat_ref": 0.2, "hunt_ref": 1.3, "corridor": 0.6},
    "fog": {"feed": 1.2, "rest": 0.9, "rut": 0.8, "heat_ref": 0.9, "hunt_ref": 0.9, "corridor": 1.2},
    "clear": {"feed": 1.0, "rest": 1.0, "rut": 1.0, "heat_ref": 1.0, "hunt_ref": 1.0, "corridor": 1.0},
}


# =====================================================================
# API HELPERS
# =====================================================================

def get_species_needs(species: str) -> Dict[str, Dict[str, float]]:
    """Retourne les besoins pour une espece donnee."""
    return SPECIES_NEEDS.get(species, SPECIES_NEEDS["moose"])


def get_sex_params(species: str, sex: str) -> Dict[str, float]:
    """Retourne les parametres pour une espece/sexe."""
    sp = SEX_PARAMS.get(species, SEX_PARAMS["moose"])
    return sp.get(sex, sp["male"])


def get_season_modifier(zone_type: str, month: int) -> float:
    """Retourne le modificateur saisonnier pour un type de zone."""
    mods = SEASON_MODIFIERS.get(zone_type, SEASON_MODIFIERS.get("corridor", {}))
    return mods.get(month, 1.0)


def get_corridor_cost(sex: str, feature: str) -> float:
    """Retourne le cout corridor pour un sexe/feature."""
    costs = CORRIDOR_COST_GRID.get(sex, CORRIDOR_COST_GRID["male"])
    return costs.get(feature, 1.0)


def get_weather_modifier(condition: str, zone_type: str) -> float:
    """Retourne le modificateur meteo pour un type de zone."""
    mods = WEATHER_MODIFIERS.get(condition, WEATHER_MODIFIERS["clear"])
    return mods.get(zone_type, 1.0)
