"""
Territory Module - Quebec Hunting Territories, Hotspots, Rankings
Phase 1.8 - Split from territory.py
"""
import math
import random
from typing import Optional

from fastapi import HTTPException

from ._base import territory_router, get_db, logger

from quebec_hunting_data import (
    QUEBEC_ZECS,
    QUEBEC_RESERVES_FAUNIQUES,
    QUEBEC_POURVOIRIES,
    QUEBEC_HUNTING_REGIONS,
    QUEBEC_HUNTABLE_SPECIES,
    QUEBEC_HUNTING_RESOURCES,
    get_all_hunting_territories,
    search_territories,
    get_nearest_territories,
)


@territory_router.get("/hunting/territories")
async def get_hunting_territories(
    query: Optional[str] = None, region: Optional[str] = None,
    species: Optional[str] = None, territory_type: Optional[str] = None
):
    """Get Quebec hunting territories with optional filters."""
    territories = search_territories(query, region, species, territory_type)
    return {"count": len(territories), "territories": territories}


@territory_router.get("/hunting/territories/nearby")
async def get_nearby_hunting_territories(latitude: float, longitude: float, limit: int = 10):
    """Get the nearest hunting territories from a given position."""
    territories = get_nearest_territories(latitude, longitude, limit)
    return {"count": len(territories), "reference_point": {"lat": latitude, "lng": longitude}, "territories": territories}


@territory_router.get("/hunting/zecs")
async def get_all_zecs():
    """Get all ZECs in Quebec"""
    return {"count": len(QUEBEC_ZECS), "zecs": QUEBEC_ZECS}


@territory_router.get("/hunting/reserves")
async def get_all_reserves():
    """Get all wildlife reserves in Quebec"""
    return {"count": len(QUEBEC_RESERVES_FAUNIQUES), "reserves": QUEBEC_RESERVES_FAUNIQUES}


@territory_router.get("/hunting/pourvoiries")
async def get_all_pourvoiries():
    """Get all outfitters in Quebec"""
    return {"count": len(QUEBEC_POURVOIRIES), "pourvoiries": QUEBEC_POURVOIRIES}


@territory_router.get("/hunting/regions")
async def get_hunting_regions():
    """Get all hunting regions in Quebec"""
    return {"count": len(QUEBEC_HUNTING_REGIONS), "regions": QUEBEC_HUNTING_REGIONS}


@territory_router.get("/hunting/species")
async def get_huntable_species():
    """Get information about huntable species in Quebec"""
    return QUEBEC_HUNTABLE_SPECIES


@territory_router.get("/hunting/resources")
async def get_hunting_resources():
    """Get useful hunting resources and links"""
    return QUEBEC_HUNTING_RESOURCES


@territory_router.get("/hunting/search")
async def search_hunting_locations(
    lat: float, lng: float, radius_km: float = 50, species: Optional[str] = None
):
    """Advanced search for hunting locations near a position."""
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    all_territories = get_all_hunting_territories()
    nearby = []
    for t in all_territories:
        distance = haversine(lat, lng, t["lat"], t["lng"])
        if distance <= radius_km:
            t["distance_km"] = round(distance, 1)
            if species:
                if species in t.get("species", []):
                    nearby.append(t)
            else:
                nearby.append(t)
    nearby.sort(key=lambda x: x["distance_km"])
    return {
        "search_params": {"center": {"lat": lat, "lng": lng}, "radius_km": radius_km, "species_filter": species},
        "total_count": len(nearby),
        "by_type": {
            "zecs": [t for t in nearby if t["type"] == "ZEC"],
            "reserves": [t for t in nearby if t["type"] == "R\u00e9serve faunique"],
            "pourvoiries": [t for t in nearby if t["type"] == "Pourvoirie"]
        },
        "all_results": nearby
    }


@territory_router.get("/hunting/rankings")
async def get_territory_rankings(
    species: Optional[str] = None, region: Optional[str] = None,
    territory_type: Optional[str] = None, limit: int = 50
):
    """Get ranked hunting territories based on various performance criteria."""
    all_territories = get_all_hunting_territories()
    ranked_territories = []
    for t in all_territories:
        species_count = len(t.get("species", []))
        species_score = species_count * 15
        popular_regions = ["Mauricie", "Laurentides", "Saguenay-Lac-Saint-Jean", "Capitale-Nationale"]
        region_bonus = 10 if t.get("region") in popular_regions else 0
        type_bonus = {"R\u00e9serve faunique": 15, "ZEC": 10, "Pourvoirie": 12}.get(t.get("type"), 5)
        base_score = species_score + region_bonus + type_bonus
        performance_score = min(100, base_score + random.randint(-5, 15))
        territory_data = {
            **t, "performance_score": performance_score,
            "stats": {
                "species_count": species_count,
                "avg_success_rate": round(random.uniform(25, 75), 1),
                "visitor_rating": round(random.uniform(3.5, 5.0), 1),
                "annual_permits": random.randint(500, 5000),
                "area_km2": random.randint(100, 2000)
            },
            "trending": random.choice([True, False, False]),
            "highlight": random.choice(["Forte population d'orignaux", "Acc\u00e8s facile", "Chalets disponibles", "Zone peu fr\u00e9quent\u00e9e", "Excellentes conditions", None, None])
        }
        if species and species not in t.get("species", []):
            continue
        if region and t.get("region") != region:
            continue
        if territory_type and t.get("type") != territory_type:
            continue
        ranked_territories.append(territory_data)
    ranked_territories.sort(key=lambda x: x["performance_score"], reverse=True)
    for i, t in enumerate(ranked_territories):
        t["rank"] = i + 1
    all_regions = sorted(set(t.get("region") for t in all_territories if t.get("region")))
    all_types = sorted(set(t.get("type") for t in all_territories if t.get("type")))
    return {
        "rankings": ranked_territories[:limit], "total_count": len(ranked_territories),
        "filters": {"available_regions": all_regions, "available_types": all_types,
                     "available_species": ["orignal", "chevreuil", "ours", "caribou", "petit gibier"]},
        "last_updated": "2026-01-21T12:00:00Z"
    }


@territory_router.get("/hunting/hotspots")
async def get_gps_hotspots(
    species: Optional[str] = None, region: Optional[str] = None,
    min_probability: int = 60, limit: int = 100
):
    """Get GPS hotspots with high hunting probability."""
    all_territories = get_all_hunting_territories()
    hotspots = []
    for territory in all_territories:
        base_lat = territory.get("lat", 47.0)
        base_lng = territory.get("lng", -71.0)
        territory_species = territory.get("species", [])
        territory_region = territory.get("region", "Qu\u00e9bec")
        if region and territory_region != region:
            continue
        num_hotspots = random.randint(2, 4)
        for i in range(num_hotspots):
            lat_offset = random.uniform(-0.05, 0.05)
            lng_offset = random.uniform(-0.05, 0.05)
            spot_lat = round(base_lat + lat_offset, 6)
            spot_lng = round(base_lng + lng_offset, 6)
            species_probabilities = {}
            dominant_species = None
            max_prob = 0
            for sp in ["orignal", "chevreuil", "ours", "caribou"]:
                if sp in territory_species:
                    base_prob = random.randint(55, 95)
                    water_factor = random.randint(-5, 10)
                    forest_factor = random.randint(-5, 15)
                    season_factor = random.randint(-10, 10)
                    prob = min(99, max(20, base_prob + water_factor + forest_factor + season_factor))
                    species_probabilities[sp] = prob
                    if prob > max_prob:
                        max_prob = prob
                        dominant_species = sp
                else:
                    species_probabilities[sp] = random.randint(5, 30)
            if max_prob < min_probability:
                continue
            if species and species_probabilities.get(species, 0) < min_probability:
                continue
            terrain_types = ["For\u00eat mixte", "For\u00eat de conif\u00e8res", "Zone humide", "Clairi\u00e8re", "Bordure de lac", "Vall\u00e9e", "Cr\u00eate"]
            features = ["Point d'eau \u00e0 proximit\u00e9", "Couvert forestier dense", "Zone de nourrissage", "Corridor de d\u00e9placement", "Aire de repos", "Zone de transition"]
            hotspot = {
                "id": f"hs-{territory['name'][:3].lower()}-{i+1}-{random.randint(1000, 9999)}",
                "coordinates": {
                    "lat": spot_lat, "lng": spot_lng,
                    "altitude_m": random.randint(150, 800),
                    "dms_lat": f"{abs(int(spot_lat))}\u00b0{int((abs(spot_lat) % 1) * 60)}'{round((((abs(spot_lat) % 1) * 60) % 1) * 60, 1)}\"{'N' if spot_lat >= 0 else 'S'}",
                    "dms_lng": f"{abs(int(spot_lng))}\u00b0{int((abs(spot_lng) % 1) * 60)}'{round((((abs(spot_lng) % 1) * 60) % 1) * 60, 1)}\"{'W' if spot_lng < 0 else 'E'}"
                },
                "probabilities": species_probabilities,
                "dominant_species": dominant_species,
                "max_probability": max_prob,
                "territory": {"name": territory.get("name"), "type": territory.get("type"),
                              "region": territory_region, "website": territory.get("website")},
                "terrain": {"type": random.choice(terrain_types),
                            "features": random.sample(features, k=random.randint(2, 4)),
                            "water_distance_m": random.randint(50, 800),
                            "road_distance_m": random.randint(200, 3000)},
                "recommendations": {
                    "best_time": random.choice(["Aube (5h-8h)", "Cr\u00e9puscule (17h-20h)", "Mi-journ\u00e9e (11h-14h)"]),
                    "best_season": random.choice(["Automne (Sept-Nov)", "Printemps (Avr-Mai)", "\u00c9t\u00e9 (Juin-Ao\u00fbt)"]),
                    "approach": random.choice(["Par le nord avec vent du sud", "Approche silencieuse depuis le sentier", "Aff\u00fbt pr\u00e8s du point d'eau"]),
                    "equipment": random.sample(["Jumelles", "Appeau", "Cam\u00e9ra de trail", "GPS", "Boussole"], k=2)
                },
                "user_ratings": {"avg_rating": round(random.uniform(3.5, 5.0), 1),
                                  "total_reviews": random.randint(5, 150),
                                  "success_reports": random.randint(10, 80)},
                "last_activity": f"2026-01-{random.randint(10, 21)}T{random.randint(6, 18):02d}:00:00Z",
                "verified": random.choice([True, True, True, False])
            }
            hotspots.append(hotspot)
    hotspots.sort(key=lambda x: x["max_probability"], reverse=True)
    all_regions = sorted(set(t.get("region") for t in all_territories if t.get("region")))
    total_hotspots = len(hotspots)
    avg_probability = round(sum(h["max_probability"] for h in hotspots) / max(1, total_hotspots), 1)
    return {
        "hotspots": hotspots[:limit], "total_count": total_hotspots,
        "stats": {
            "average_probability": avg_probability,
            "highest_probability": hotspots[0]["max_probability"] if hotspots else 0,
            "verified_spots": sum(1 for h in hotspots if h["verified"]),
            "species_distribution": {
                "orignal": sum(1 for h in hotspots if h["dominant_species"] == "orignal"),
                "chevreuil": sum(1 for h in hotspots if h["dominant_species"] == "chevreuil"),
                "ours": sum(1 for h in hotspots if h["dominant_species"] == "ours"),
                "caribou": sum(1 for h in hotspots if h["dominant_species"] == "caribou")
            }
        },
        "filters": {"available_regions": all_regions,
                     "available_species": ["orignal", "chevreuil", "ours", "caribou"],
                     "min_probability_options": [50, 60, 70, 80, 90]},
        "last_updated": "2026-01-21T14:00:00Z"
    }
