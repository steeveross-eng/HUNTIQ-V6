"""
BIONIC V8 — Router API Écologique
==================================
Endpoints pour accéder à la base écologique et aux validateurs BCE.

Endpoints:
  - GET /api/v1/ecological/species
  - GET /api/v1/ecological/species/{species}/zones
  - GET /api/v1/ecological/species/{species}/zones/{zone_type}
  - POST /api/v1/ecological/validate
  - GET /api/v1/ecological/corridors/active

VERSION: 8.0.0 — API écologique V8-ready
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger("bionic_engine.ecological_router")

router = APIRouter(prefix="/api/v1/ecological", tags=["Ecological V8"])


# =====================================================================
# MODÈLES PYDANTIC
# =====================================================================

class EcologicalZoneResponse(BaseModel):
    species: str
    zone_type: str
    description: str
    functional_role: str
    habitat: Dict[str, Any]
    topography: Dict[str, Any]
    criteria: Dict[str, Any]
    terrain_indices: List[str]

class CorridorSummary(BaseModel):
    total_corridors: int
    macro_corridors: int
    biological_corridors: int
    conservation_corridors: int
    active_species: List[str]

class ValidationRequest(BaseModel):
    species: str
    zone_type: Optional[str] = "alimentation"
    season: Optional[str] = "automne"
    ndvi: Optional[float] = 0.5
    slope: Optional[float] = 10
    distance_to_water: Optional[float] = 500
    human_pressure: Optional[float] = 0.2
    corridor_points: Optional[List[Dict[str, float]]] = None
    width_m: Optional[float] = None


# =====================================================================
# ENDPOINTS
# =====================================================================

@router.get("/species")
async def get_species_list():
    """Liste toutes les espèces disponibles dans la base écologique."""
    try:
        from modules.bionic_engine_p0.knowledge.ecological_database_v8 import ecological_database, Species
        
        species_list = [
            {
                "id": s.value,
                "name": s.name,
                "label_fr": {
                    "orignal": "Orignal (Alces alces)",
                    "chevreuil": "Chevreuil (Odocoileus virginianus)",
                    "ours_noir": "Ours noir (Ursus americanus)",
                }.get(s.value, s.name)
            }
            for s in Species
        ]
        
        return {
            "species": species_list,
            "count": len(species_list),
            "version": "ecological_database_v8.0.0"
        }
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return {
            "species": [
                {"id": "orignal", "name": "ORIGNAL", "label_fr": "Orignal (Alces alces)"},
                {"id": "chevreuil", "name": "CHEVREUIL", "label_fr": "Chevreuil (Odocoileus virginianus)"},
                {"id": "ours_noir", "name": "OURS_NOIR", "label_fr": "Ours noir (Ursus americanus)"},
            ],
            "count": 3,
            "version": "ecological_database_v8.0.0"
        }


@router.get("/species/{species}/zones")
async def get_species_zones(species: str):
    """Récupère toutes les zones écologiques pour une espèce."""
    try:
        from modules.bionic_engine_p0.knowledge.ecological_database_v8 import ecological_database, Species
        
        # Convertir le nom d'espèce
        species_enum = None
        for s in Species:
            if s.value == species.lower():
                species_enum = s
                break
        
        if not species_enum:
            raise HTTPException(status_code=404, detail=f"Espèce '{species}' non trouvée")
        
        zones = ecological_database.get_all_zones_for_species(species_enum)
        
        zones_data = {}
        for zone_type, zone in zones.items():
            zones_data[zone_type.value] = {
                "description": zone.description,
                "functional_role": zone.functional_role,
                "habitat": {
                    "forest_types": [ft.value for ft in zone.habitat.forest_type],
                    "canopy_cover": f"{zone.habitat.canopy_cover_min}-{zone.habitat.canopy_cover_max}%",
                    "understory": zone.habitat.understory_density,
                },
                "topography": {
                    "slope_range": f"{zone.topography.slope_min}-{zone.topography.slope_max}%",
                    "terrain_types": zone.topography.terrain_types,
                    "preferred_aspect": zone.topography.aspect_preferred,
                },
                "criteria": {
                    "ndvi_range": f"{zone.criteria.ndvi_min}-{zone.criteria.ndvi_max}",
                    "ndvi_optimal": zone.criteria.ndvi_optimal,
                    "corridor_cost": zone.criteria.corridor_cost,
                    "bce_rules": zone.criteria.bce_rules,
                },
                "terrain_indices": zone.terrain_indices,
                "scientific_sources": zone.scientific_sources,
            }
        
        return {
            "species": species,
            "zones": zones_data,
            "zones_count": len(zones_data),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except ImportError:
        # Fallback si le module n'est pas encore chargé
        return _get_fallback_zones(species)


@router.get("/species/{species}/zones/{zone_type}")
async def get_specific_zone(species: str, zone_type: str):
    """Récupère une zone écologique spécifique."""
    try:
        from modules.bionic_engine_p0.knowledge.ecological_database_v8 import ecological_database, Species, ZoneType
        
        # Convertir les enums
        species_enum = None
        zone_enum = None
        
        for s in Species:
            if s.value == species.lower():
                species_enum = s
                break
        
        for z in ZoneType:
            if z.value == zone_type.lower():
                zone_enum = z
                break
        
        if not species_enum:
            raise HTTPException(status_code=404, detail=f"Espèce '{species}' non trouvée")
        if not zone_enum:
            raise HTTPException(status_code=404, detail=f"Type de zone '{zone_type}' non trouvé")
        
        zone = ecological_database.get_zone(species_enum, zone_enum)
        
        if not zone:
            raise HTTPException(status_code=404, detail=f"Zone '{zone_type}' non disponible pour '{species}'")
        
        return {
            "species": species,
            "zone_type": zone_type,
            "data": {
                "description": zone.description,
                "functional_role": zone.functional_role,
                "habitat": {
                    "forest_types": [ft.value for ft in zone.habitat.forest_type],
                    "canopy_cover_min": zone.habitat.canopy_cover_min,
                    "canopy_cover_max": zone.habitat.canopy_cover_max,
                    "understory_density": zone.habitat.understory_density,
                    "ground_cover": zone.habitat.ground_cover,
                },
                "topography": {
                    "slope_min": zone.topography.slope_min,
                    "slope_max": zone.topography.slope_max,
                    "elevation_min": zone.topography.elevation_min,
                    "elevation_max": zone.topography.elevation_max,
                    "terrain_types": zone.topography.terrain_types,
                    "preferred_aspect": zone.topography.aspect_preferred,
                },
                "hydrology": {
                    "distance_to_water_min": zone.hydrology.distance_to_water_min,
                    "distance_to_water_max": zone.hydrology.distance_to_water_max,
                    "water_types": zone.hydrology.water_types,
                    "wetland_affinity": zone.hydrology.wetland_affinity,
                },
                "human_pressure": {
                    "distance_to_roads_min": zone.human_pressure.distance_to_roads_min,
                    "max_human_pressure": zone.human_pressure.max_human_pressure,
                },
                "food_sources": {
                    "spring": zone.food_sources.spring,
                    "summer": zone.food_sources.summer,
                    "autumn": zone.food_sources.autumn,
                    "winter": zone.food_sources.winter,
                },
                "microclimate": zone.microclimate,
                "ecological_connectivity": zone.ecological_connectivity,
                "terrain_indices": zone.terrain_indices,
                "criteria": {
                    "ndvi_min": zone.criteria.ndvi_min,
                    "ndvi_max": zone.criteria.ndvi_max,
                    "ndvi_optimal": zone.criteria.ndvi_optimal,
                    "landcover_codes": zone.criteria.landcover_codes,
                    "score_weights": zone.criteria.score_weights,
                    "corridor_cost": zone.criteria.corridor_cost,
                    "bce_rules": zone.criteria.bce_rules,
                },
                "scientific_sources": zone.scientific_sources,
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except ImportError:
        raise HTTPException(status_code=500, detail="Module écologique non disponible")


@router.post("/validate")
async def validate_ecological_data(request: ValidationRequest):
    """Valide des données écologiques avec les validateurs BCE."""
    try:
        from bce.validators.ecological_validators_v8 import validate_ecological_compliance
        
        data = {
            "species": request.species,
            "zone_type": request.zone_type,
            "season": request.season,
            "ndvi": request.ndvi,
            "slope": request.slope,
            "distance_to_water": request.distance_to_water,
            "human_pressure": request.human_pressure,
            "ndvi_min": 0.3,  # Valeurs par défaut
            "ndvi_max": 0.8,
            "slope_max": 30,
            "water_distance_max": 1000,
        }
        
        # Ajouter les données de corridor si présentes
        if request.corridor_points:
            data["corridor_points"] = request.corridor_points
            data["positions"] = request.corridor_points
        
        if request.width_m:
            data["width_m"] = request.width_m
        
        # Exécuter la validation
        validation_type = "corridor" if request.corridor_points else "zone"
        result = validate_ecological_compliance(data, validation_type)
        
        return result
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return {
            "global_status": "SKIPPED",
            "global_score": 0,
            "message": "Validateurs écologiques non disponibles",
            "error": str(e)
        }


@router.get("/corridors/summary")
async def get_corridors_summary():
    """Retourne un résumé des corridors actifs détectés."""
    # Ce serait normalement calculé dynamiquement
    # Pour l'instant, retourne des données de démo
    return {
        "summary": {
            "total_corridors": 12,
            "macro_corridors": 2,
            "biological_corridors": 6,
            "conservation_corridors": 4,
        },
        "by_species": {
            "orignal": {
                "corridors_count": 5,
                "dominant_type": "biological_corridor",
                "connectivity_score": 78,
            },
            "chevreuil": {
                "corridors_count": 4,
                "dominant_type": "conservation_corridor",
                "connectivity_score": 72,
            },
            "ours_noir": {
                "corridors_count": 3,
                "dominant_type": "macro_corridor",
                "connectivity_score": 65,
            },
        },
        "wwf_legend": {
            "macro_corridor": {"label": "Macro-corridor (> 5 km)", "color": "#8B5CF6"},
            "biological_corridor": {"label": "Corridor biologique (1-5 km)", "color": "#10B981"},
            "conservation_corridor": {"label": "Corridor de conservation (< 1 km)", "color": "#F59E0B"},
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# =====================================================================
# FONCTIONS UTILITAIRES
# =====================================================================

def _get_fallback_zones(species: str) -> Dict[str, Any]:
    """Retourne des zones par défaut si le module n'est pas chargé."""
    fallback_zones = {
        "alimentation": {
            "description": f"Zone d'alimentation principale de {species}",
            "functional_role": "Primary foraging area",
            "habitat": {"forest_types": ["mixte", "feuillu"], "canopy_cover": "30-70%"},
            "criteria": {"ndvi_range": "0.4-0.8", "corridor_cost": 1.5}
        },
        "repos": {
            "description": f"Zone de repos et couvert thermique de {species}",
            "functional_role": "Thermal refuge and rest area",
            "habitat": {"forest_types": ["conifere", "mixte"], "canopy_cover": "60-90%"},
            "criteria": {"ndvi_range": "0.5-0.85", "corridor_cost": 2.0}
        },
        "corridor": {
            "description": f"Corridor de déplacement de {species}",
            "functional_role": "Movement corridor",
            "habitat": {"forest_types": ["mixte"], "canopy_cover": "40-80%"},
            "criteria": {"ndvi_range": "0.3-0.8", "corridor_cost": 1.0}
        }
    }
    
    return {
        "species": species,
        "zones": fallback_zones,
        "zones_count": len(fallback_zones),
        "note": "Fallback data - ecological module not loaded",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
