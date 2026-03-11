"""
Territory Module - Analysis, Layers, WMS, Probability, Climate
Phase 1.8 - Split from territory.py
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, Literal, List

from fastapi import HTTPException

from ._base import territory_router, get_db, logger
from .models import ProbabilityRequest, ProbabilityResponse


# Species-specific habitat preferences
SPECIES_HABITAT_RULES = {
    "orignal": {
        "preferred_forest": ["mixte", "coniferes", "feuillus_dense"],
        "water_distance_optimal_m": 500,
        "altitude_optimal_m": (200, 600),
        "prefers_transition_zones": True,
        "prefers_coulees": True,
        "prefers_southwest_slopes": True,
        "avoids_roads_within_m": 1000,
        "cooling_preference": "high",
        "refuge_type": "dense_conifer"
    },
    "chevreuil": {
        "preferred_forest": ["mixte", "feuillus", "regeneration"],
        "water_distance_optimal_m": 300,
        "altitude_optimal_m": (100, 400),
        "prefers_transition_zones": True,
        "prefers_coulees": True,
        "prefers_southwest_slopes": True,
        "avoids_roads_within_m": 500,
        "cooling_preference": "medium",
        "refuge_type": "dense_shrub"
    },
    "ours": {
        "preferred_forest": ["mixte", "feuillus", "coniferes"],
        "water_distance_optimal_m": 200,
        "altitude_optimal_m": (100, 800),
        "prefers_transition_zones": False,
        "prefers_coulees": True,
        "prefers_southwest_slopes": False,
        "avoids_roads_within_m": 2000,
        "cooling_preference": "high",
        "refuge_type": "dense_mixed"
    }
}

# Quebec Government WMS Services
WMS_LAYERS = {
    "foret_ecoforestiere": {
        "url": "https://geoegl.msp.gouv.qc.ca/ws/mffpecofor.fcgi",
        "name": "Carte ecoforestiere",
        "description": "Peuplements forestiers du Quebec (coniferes, feuillus, mixte)",
        "layers": "carte_ecoforestiere_quebec_sud"
    },
    "hydrographie": {
        "url": "https://serviceswebcarto.mern.gouv.qc.ca/pes/services/Territoire/SDA_WMS/MapServer/WMSServer",
        "name": "Reseau hydrographique",
        "description": "Lacs, rivieres, ruisseaux du Quebec",
        "layers": "0,1,2,3"
    },
    "topographie": {
        "url": "https://serviceswebcarto.mern.gouv.qc.ca/pes/services/Imagerie/LIDAR_Ombre_WMS/MapServer/WMSServer",
        "name": "Relief et courbes de niveau",
        "description": "Modele numerique de terrain LiDAR",
        "layers": "0"
    },
    "routes_chemins": {
        "url": "https://serviceswebcarto.mern.gouv.qc.ca/pes/services/Territoire/SDA_WMS/MapServer/WMSServer",
        "name": "Reseau routier",
        "description": "Routes et chemins forestiers",
        "layers": "4,5,6"
    }
}


@territory_router.get("/layers/heatmap_activite")
async def get_heatmap_activite(user_id: str, species: Optional[str] = None, hours: int = 72):
    """Get activity heatmap data (P2 NORMALIZED - reads from geo_entities)"""
    database = await get_db()
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    query = {"user_id": user_id, "entity_type": "observation", "created_at": {"$gte": cutoff_time}}
    if species:
        query["metadata.species"] = species
    events = await database.geo_entities.find(query).to_list(1000)
    grid_data = {}
    for event in events:
        location = event.get('location', {})
        coords = location.get('coordinates', [0, 0])
        lng, lat = coords[0], coords[1]
        lat_rounded = round(lat, 3)
        lon_rounded = round(lng, 3)
        key = f"{lat_rounded},{lon_rounded}"
        if key not in grid_data:
            grid_data[key] = {"lat": lat_rounded, "lon": lon_rounded, "intensity": 0,
                              "species": event.get('metadata', {}).get('species')}
        grid_data[key]["intensity"] += 1
    return {"type": "heatmap", "time_window_hours": hours, "species_filter": species,
            "points": list(grid_data.values())}


@territory_router.get("/stats")
async def get_territory_stats(user_id: str):
    """Get territory analysis statistics"""
    database = await get_db()
    total_events = await database.territory_events.count_documents({"user_id": user_id})
    orignal_count = await database.territory_events.count_documents({"user_id": user_id, "species": "orignal"})
    chevreuil_count = await database.territory_events.count_documents({"user_id": user_id, "species": "chevreuil"})
    ours_count = await database.territory_events.count_documents({"user_id": user_id, "species": "ours"})
    total_cameras = await database.territory_cameras.count_documents({"user_id": user_id})
    connected_cameras = await database.territory_cameras.count_documents({"user_id": user_id, "connected": True})
    total_photos = await database.territory_photos.count_documents({"user_id": user_id})
    processed_photos = await database.territory_photos.count_documents({"user_id": user_id, "processing_status": "completed"})
    return {
        "total_events": total_events,
        "species_counts": {"orignal": orignal_count, "chevreuil": chevreuil_count, "ours": ours_count},
        "cameras": {"total": total_cameras, "connected": connected_cameras},
        "photos": {"total": total_photos, "processed": processed_photos}
    }


@territory_router.get("/layers/wms-sources")
async def get_wms_sources():
    """Get available WMS layer sources from Quebec government"""
    return {"sources": WMS_LAYERS, "note": "Ces couches proviennent des services du gouvernement du Quebec"}


@territory_router.post("/analysis/probability", response_model=ProbabilityResponse)
async def calculate_presence_probability(request: ProbabilityRequest):
    """Calculate species presence probability based on environmental factors."""
    rules = SPECIES_HABITAT_RULES.get(request.species)
    if not rules:
        raise HTTPException(status_code=400, detail="Invalid species")
    factors = {}
    score = 50
    if request.water_distance_m is not None:
        optimal = rules["water_distance_optimal_m"]
        if request.water_distance_m <= optimal: water_score = 20
        elif request.water_distance_m <= optimal * 2: water_score = 15
        elif request.water_distance_m <= optimal * 4: water_score = 10
        else: water_score = 5
        factors["water_proximity"] = {"score": water_score, "max": 20, "distance_m": request.water_distance_m, "optimal_m": optimal}
        score += water_score - 10
    if request.forest_type:
        if request.forest_type in rules["preferred_forest"]: forest_score = 15
        elif request.forest_type in ["mixte", "regeneration"]: forest_score = 10
        else: forest_score = 5
        factors["forest_type"] = {"score": forest_score, "max": 15, "type": request.forest_type, "preferred": rules["preferred_forest"]}
        score += forest_score - 7.5
    if request.altitude_m is not None:
        alt_min, alt_max = rules["altitude_optimal_m"]
        if alt_min <= request.altitude_m <= alt_max: alt_score = 15
        elif alt_min - 100 <= request.altitude_m <= alt_max + 100: alt_score = 10
        else: alt_score = 5
        factors["altitude"] = {"score": alt_score, "max": 15, "altitude_m": request.altitude_m, "optimal_range": rules["altitude_optimal_m"]}
        score += alt_score - 7.5
    if request.is_transition_zone is not None:
        if request.is_transition_zone and rules["prefers_transition_zones"]: trans_score = 10
        elif request.is_transition_zone: trans_score = 7
        else: trans_score = 3
        factors["transition_zone"] = {"score": trans_score, "max": 10, "is_transition": request.is_transition_zone, "species_prefers": rules["prefers_transition_zones"]}
        score += trans_score - 5
    if request.is_coulee is not None:
        if request.is_coulee and rules["prefers_coulees"]: coulee_score = 10
        elif request.is_coulee: coulee_score = 6
        else: coulee_score = 2
        factors["coulee"] = {"score": coulee_score, "max": 10, "is_coulee": request.is_coulee, "species_prefers": rules["prefers_coulees"]}
        score += coulee_score - 5
    if request.slope_direction:
        sw_directions = ["S", "SW", "W"]
        if request.slope_direction in sw_directions and rules["prefers_southwest_slopes"]: slope_score = 10
        elif request.slope_direction in sw_directions: slope_score = 7
        else: slope_score = 4
        factors["slope_direction"] = {"score": slope_score, "max": 10, "direction": request.slope_direction, "preferred": sw_directions if rules["prefers_southwest_slopes"] else []}
        score += slope_score - 5
    if request.road_distance_m is not None:
        min_road_dist = rules["avoids_roads_within_m"]
        if request.road_distance_m >= min_road_dist * 2: road_score = 20
        elif request.road_distance_m >= min_road_dist: road_score = 15
        elif request.road_distance_m >= min_road_dist / 2: road_score = 8
        else: road_score = 2
        factors["road_isolation"] = {"score": road_score, "max": 20, "distance_m": request.road_distance_m, "min_preferred_m": min_road_dist}
        score += road_score - 10
    score = max(0, min(100, score))
    factors_count = len(factors)
    if factors_count >= 5: confidence = "high"
    elif factors_count >= 3: confidence = "medium"
    else: confidence = "low"
    recommendations = []
    if score >= 70:
        recommendations.append(f"Zone a haute probabilite pour {request.species}")
        recommendations.append("Installer une camera de trail dans ce secteur")
    elif score >= 50:
        recommendations.append(f"Zone de probabilite moyenne pour {request.species}")
        recommendations.append("Explorer les coulees et zones de transition a proximite")
    else:
        recommendations.append(f"Zone de faible probabilite pour {request.species}")
        recommendations.append("Chercher des zones avec meilleur acces a l'eau")
    refuge_zones = [{"type": rules["refuge_type"], "direction": "N", "distance_estimate_m": 200,
                     "description": f"Zone de refuge potentielle ({rules['refuge_type']})"}]
    cooling_zones = []
    if rules["cooling_preference"] == "high":
        cooling_zones = [
            {"type": "nord_slope", "description": "Versant nord - Zone ombragee", "priority": "high"},
            {"type": "water_body", "description": "Proximite cours d'eau", "priority": "high"}
        ]
    elif rules["cooling_preference"] == "medium":
        cooling_zones = [{"type": "forest_canopy", "description": "Couvert forestier dense", "priority": "medium"}]
    return ProbabilityResponse(
        latitude=request.latitude, longitude=request.longitude, species=request.species,
        probability_score=round(score, 1), confidence=confidence, factors=factors,
        recommendations=recommendations, refuge_zones=refuge_zones, cooling_zones=cooling_zones
    )


@territory_router.get("/analysis/cooling-zones")
async def get_cooling_zones(
    latitude: float, longitude: float,
    species: Literal['orignal', 'chevreuil', 'ours'],
    radius_km: float = 2.0
):
    """Get recommended cooling zones for a species in a given area."""
    rules = SPECIES_HABITAT_RULES.get(species)
    if not rules:
        raise HTTPException(status_code=400, detail="Invalid species")
    cooling_preference = rules["cooling_preference"]
    zones = []
    if cooling_preference in ["high", "medium"]:
        zones.append({"type": "north_slope", "name": "Versants nord",
                       "description": "Zones ombragees sur les versants exposes au nord",
                       "priority": "high" if cooling_preference == "high" else "medium",
                       "search_direction": "N",
                       "characteristics": ["Temperature plus fraiche", "Moins d'exposition solaire", "Humidite plus elevee"]})
        zones.append({"type": "water_proximity", "name": "Proximite eau",
                       "description": "Zones pres des cours d'eau, lacs et marecages",
                       "priority": "high", "search_radius_m": 500,
                       "characteristics": ["Effet rafraichissant", "Source d'eau", "Vegetation dense"]})
        zones.append({"type": "dense_canopy", "name": "Couvert forestier dense",
                       "description": "Zones avec canopee fermee offrant de l'ombre",
                       "priority": "medium", "forest_types": ["coniferes_dense", "mixte_dense"],
                       "characteristics": ["Ombre permanente", "Protection contre le soleil", "Microclimat frais"]})
    if species == "orignal":
        zones.append({"type": "wetland", "name": "Milieux humides",
                       "description": "Marecages et tourbieres - habitat de predilection pour le refroidissement",
                       "priority": "high",
                       "characteristics": ["Eau peu profonde pour se rafraichir", "Vegetation aquatique (nourriture)", "Protection contre les insectes"]})
    if species == "ours":
        zones.append({"type": "ravine", "name": "Coulees et ravins",
                       "description": "Depressions de terrain avec air frais descendant",
                       "priority": "high",
                       "characteristics": ["Air froid accumule", "Humidite elevee", "Couvert vegetal dense"]})
    return {
        "center": {"latitude": latitude, "longitude": longitude},
        "radius_km": radius_km, "species": species,
        "cooling_preference_level": cooling_preference,
        "recommended_zones": zones,
        "best_times": ["Tot le matin (5h-8h)", "Fin d'apres-midi (16h-19h)"],
        "temperature_threshold_celsius": 20 if cooling_preference == "high" else 25
    }


def calculate_point_probability(lat: float, lng: float, species: str) -> dict:
    """Calculate probability score for a point based on species habitat rules"""
    import random
    rules = SPECIES_HABITAT_RULES.get(species, SPECIES_HABITAT_RULES['orignal'])
    random.seed(int(lat * 1000 + lng * 1000))
    water_distance = random.randint(50, 1000)
    altitude = 200 + int(abs(lat - 46) * 100 + abs(lng + 71) * 50)
    is_transition = random.random() > 0.6
    has_coulee = random.random() > 0.7
    forest_density = random.choice(['dense', 'mixte', 'clairseme', 'regeneration'])
    score = 50
    factors = []
    optimal_water = rules["water_distance_optimal_m"]
    if water_distance <= optimal_water:
        score += 15; factors.append(f"Proche de l'eau ({water_distance}m)")
    elif water_distance <= optimal_water * 2:
        score += 8; factors.append(f"Distance eau acceptable ({water_distance}m)")
    alt_min, alt_max = rules["altitude_optimal_m"]
    if alt_min <= altitude <= alt_max:
        score += 12; factors.append(f"Altitude optimale ({altitude}m)")
    elif alt_min - 100 <= altitude <= alt_max + 100:
        score += 6
    if is_transition and rules["prefers_transition_zones"]:
        score += 10; factors.append("Zone de transition foret")
    if has_coulee and rules.get("prefers_coulees", False):
        score += 8; factors.append("Presence de coulee")
    if forest_density in rules["preferred_forest"]:
        score += 10; factors.append(f"Foret {forest_density}")
    score = max(0, min(100, score))
    if score >= 70: level = "high"; color = "#22c55e"
    elif score >= 50: level = "medium"; color = "#eab308"
    else: level = "low"; color = "#ef4444"
    return {"score": round(score, 1), "level": level, "color": color, "factors": factors}
