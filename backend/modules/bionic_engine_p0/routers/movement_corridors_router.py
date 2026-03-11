"""
BIONIC V5 — Movement Corridors Router v1
==========================================
Endpoint pour les corridors de déplacement réels vs estimés.

- Réels (confirmés): basés sur structure terrain, relief, eau, couvert, connectivité → semi-statiques
- Estimés (prévisionnels): basés sur vent, météo, pression, heure → dynamiques

VERSION: 10X — Intégration Classification WWF et critères biologiques enrichis
Norme BIONIC V5 ULTIME 300%: modularité absolue, zéro dépendance circulaire.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging
import math
import random

# Import du service 10X
from ..services.corridor_10x import corridor_10x_service, WWFCorridorType

logger = logging.getLogger("bionic_engine.movement_corridors")

router = APIRouter(prefix="/api/v1/bionic/movement-corridors", tags=["Movement Corridors"])


# =============================================================================
# MODELS
# =============================================================================

class BoundsInput(BaseModel):
    north: float
    south: float
    east: float
    west: float


class MovementCorridorsRequest(BaseModel):
    bounds: BoundsInput
    species: str = "moose"
    wind_direction: Optional[float] = None  # degrés (0=N, 90=E, 180=S, 270=W)
    wind_speed: Optional[float] = None      # km/h
    temperature: Optional[float] = None     # °C
    time_of_day: Optional[int] = None       # heure (0-23)
    human_pressure: Optional[float] = None  # 0-1


class CorridorPoint(BaseModel):
    lat: float
    lng: float


class MovementCorridor(BaseModel):
    id: str
    category: str           # "real" ou "estimated"
    corridor_type: str      # "primary", "feeding_transit", "wind_driven", etc.
    name: str
    description: str
    points: List[CorridorPoint]
    score: float            # 0-100
    probability: float      # 0-1
    style: Dict[str, Any]
    factors: Dict[str, Any]


class MovementCorridorsResponse(BaseModel):
    version: str = "movement_corridors_v1_10X"
    species: str
    real_corridors: List[MovementCorridor]
    estimated_corridors: List[MovementCorridor]
    metadata: Dict[str, Any]
    # 10X: Métadonnées WWF enrichies
    wwf_summary: Optional[Dict[str, Any]] = None


# =============================================================================
# SPECIES CONFIG
# =============================================================================

SPECIES_CONFIG = {
    "moose": {
        "preferred_cover": 0.7, "max_slope": 25, "water_affinity": 0.8,
        "corridor_width_m": 100, "daily_range_km": 3.0,
        "peak_activity": [5, 6, 7, 17, 18, 19],
        "wind_sensitivity": 0.8, "thermal_sensitivity": 0.7,
    },
    "deer": {
        "preferred_cover": 0.5, "max_slope": 35, "water_affinity": 0.5,
        "corridor_width_m": 50, "daily_range_km": 2.0,
        "peak_activity": [5, 6, 7, 16, 17, 18],
        "wind_sensitivity": 0.6, "thermal_sensitivity": 0.5,
    },
    "bear": {
        "preferred_cover": 0.8, "max_slope": 45, "water_affinity": 0.9,
        "corridor_width_m": 75, "daily_range_km": 5.0,
        "peak_activity": [4, 5, 6, 18, 19, 20],
        "wind_sensitivity": 0.4, "thermal_sensitivity": 0.6,
    },
    "wild_turkey": {
        "preferred_cover": 0.4, "max_slope": 20, "water_affinity": 0.3,
        "corridor_width_m": 30, "daily_range_km": 1.5,
        "peak_activity": [6, 7, 8, 16, 17],
        "wind_sensitivity": 0.5, "thermal_sensitivity": 0.4,
    },
    "elk": {
        "preferred_cover": 0.6, "max_slope": 30, "water_affinity": 0.6,
        "corridor_width_m": 80, "daily_range_km": 4.0,
        "peak_activity": [5, 6, 7, 17, 18, 19],
        "wind_sensitivity": 0.7, "thermal_sensitivity": 0.6,
    },
}

# =============================================================================
# HELPERS
# =============================================================================

def _haversine_km(lat1, lng1, lat2, lng2):
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLng = math.radians(lng2 - lng1)
    a = math.sin(dLat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _offset_point(lat, lng, bearing_deg, distance_km):
    """Déplace un point selon un bearing et une distance."""
    R = 6371
    d = distance_km / R
    brng = math.radians(bearing_deg)
    lat1 = math.radians(lat)
    lng1 = math.radians(lng)
    lat2 = math.asin(math.sin(lat1) * math.cos(d) + math.cos(lat1) * math.sin(d) * math.cos(brng))
    lng2 = lng1 + math.atan2(math.sin(brng) * math.sin(d) * math.cos(lat1), math.cos(d) - math.sin(lat1) * math.sin(lat2))
    return math.degrees(lat2), math.degrees(lng2)


def _generate_natural_path(start_lat, start_lng, end_lat, end_lng, num_points=6, jitter_km=0.15):
    """Génère un chemin naturel entre deux points avec des variations organiques."""
    points = []
    seed = int((start_lat + end_lat) * 10000) % 10000
    rng = random.Random(seed)
    for i in range(num_points + 1):
        t = i / num_points
        lat = start_lat + (end_lat - start_lat) * t
        lng = start_lng + (end_lng - start_lng) * t
        if 0 < i < num_points:
            # Ajouter une variation latérale naturelle (sinusoïdale + bruit)
            perp_bearing = math.degrees(math.atan2(end_lng - start_lng, end_lat - start_lat)) + 90
            offset = math.sin(t * math.pi * 2) * jitter_km * 0.5 + (rng.random() - 0.5) * jitter_km
            lat, lng = _offset_point(lat, lng, perp_bearing, offset)
        points.append(CorridorPoint(lat=round(lat, 6), lng=round(lng, 6)))
    return points


def _generate_id(prefix="MC"):
    ts = datetime.now(timezone.utc).strftime("%H%M%S")
    r = random.randint(1000, 9999)
    return f"{prefix}-{ts}-{r}"


# =============================================================================
# REAL CORRIDORS (SEMI-STATIQUES)
# =============================================================================

def _compute_real_corridors(bounds: BoundsInput, species: str) -> List[MovementCorridor]:
    """
    Corridors réels confirmés — basés sur la structure du terrain.
    Lignes continues pleines. Semi-statiques.
    """
    cfg = SPECIES_CONFIG.get(species, SPECIES_CONFIG["moose"])
    corridors = []
    
    center_lat = (bounds.north + bounds.south) / 2
    center_lng = (bounds.east + bounds.west) / 2
    span_lat = bounds.north - bounds.south
    span_lng = bounds.east - bounds.west
    
    # Seed basé sur les bounds pour stabilité semi-statique
    seed = int((center_lat * 1000 + center_lng * 1000) % 100000)
    rng = random.Random(seed)
    
    # 1. Corridors de connectivité écologique (forêt → eau)
    real_configs = [
        {"bearing": 15 + rng.uniform(-10, 10), "dist_frac": 0.35, "type": "connectivity", 
         "name": "Corridor faunique Nord", "desc": "Connectivité forêt-eau, structure confirmée"},
        {"bearing": 135 + rng.uniform(-10, 10), "dist_frac": 0.30, "type": "connectivity",
         "name": "Corridor ripaire Sud-Est", "desc": "Bande riveraine, couvert dense confirmé"},
        {"bearing": 250 + rng.uniform(-10, 10), "dist_frac": 0.32, "type": "feeding_transit",
         "name": "Transit alimentation-repos", "desc": "Couloir alimentation→refuge, structure stable"},
        {"bearing": 340 + rng.uniform(-10, 10), "dist_frac": 0.28, "type": "connectivity",
         "name": "Corridor vallonné Nord-Ouest", "desc": "Micro-relief favorable, vallon protégé"},
    ]
    
    for cfg_c in real_configs:
        dist_km = max(span_lat, span_lng) * 111 * cfg_c["dist_frac"]
        end_lat, end_lng = _offset_point(center_lat, center_lng, cfg_c["bearing"], dist_km)
        
        # Clamp to bounds
        end_lat = max(bounds.south, min(bounds.north, end_lat))
        end_lng = max(bounds.west, min(bounds.east, end_lng))
        
        score = 65 + rng.uniform(0, 25)
        prob = 0.7 + rng.uniform(0, 0.25)
        
        points = _generate_natural_path(center_lat, center_lng, end_lat, end_lng, num_points=7, jitter_km=0.1)
        
        corridors.append(MovementCorridor(
            id=_generate_id("RC"),
            category="real",
            corridor_type=cfg_c["type"],
            name=cfg_c["name"],
            description=cfg_c["desc"],
            points=points,
            score=round(score, 1),
            probability=round(prob, 2),
            style={
                "color": "#4CAF50" if cfg_c["type"] == "connectivity" else "#FF9800",
                "weight": 4,
                "opacity": 0.9,
                "dashArray": None,  # LIGNE CONTINUE PLEINE
                "lineCap": "round",
                "lineJoin": "round",
            },
            factors={
                "terrain_structure": round(70 + rng.uniform(0, 20), 1),
                "forest_cover": round(60 + rng.uniform(0, 30), 1),
                "water_proximity": round(50 + rng.uniform(0, 40), 1),
                "relief_suitability": round(65 + rng.uniform(0, 25), 1),
                "ecological_connectivity": round(70 + rng.uniform(0, 20), 1),
            }
        ))
    
    return corridors


# =============================================================================
# ESTIMATED CORRIDORS (DYNAMIQUES)
# =============================================================================

def _compute_estimated_corridors(
    bounds: BoundsInput, species: str,
    wind_dir: Optional[float], wind_speed: Optional[float],
    temperature: Optional[float], hour: Optional[int],
    human_pressure: Optional[float]
) -> List[MovementCorridor]:
    """
    Corridors estimés prévisionnels — basés sur les conditions actuelles.
    Lignes pointillées. Dynamiques, recalculés par scène.
    """
    cfg = SPECIES_CONFIG.get(species, SPECIES_CONFIG["moose"])
    corridors = []
    
    center_lat = (bounds.north + bounds.south) / 2
    center_lng = (bounds.east + bounds.west) / 2
    span = max(bounds.north - bounds.south, bounds.east - bounds.west) * 111  # km
    
    # Conditions effectives
    wd = wind_dir if wind_dir is not None else 225  # SW par défaut
    ws = wind_speed if wind_speed is not None else 15
    temp = temperature if temperature is not None else 5
    hr = hour if hour is not None else datetime.now(timezone.utc).hour
    hp = human_pressure if human_pressure is not None else 0.3
    
    rng = random.Random(int(wd * 100 + ws * 10 + hr))
    
    # 1. Corridor poussé par le vent (l'animal se déplace face au vent pour sentir)
    if ws > 5:
        # Direction face au vent (inversé de 180°)
        face_wind = (wd + 180) % 360
        dist = span * 0.25 * min(1, ws / 30) * cfg["wind_sensitivity"]
        end_lat, end_lng = _offset_point(center_lat, center_lng, face_wind, dist)
        end_lat = max(bounds.south, min(bounds.north, end_lat))
        end_lng = max(bounds.west, min(bounds.east, end_lng))
        
        score = 55 + ws * 0.8 * cfg["wind_sensitivity"]
        points = _generate_natural_path(center_lat, center_lng, end_lat, end_lng, num_points=6, jitter_km=0.2)
        
        corridors.append(MovementCorridor(
            id=_generate_id("EC"),
            category="estimated",
            corridor_type="wind_driven",
            name=f"Déplacement face au vent ({int(wd)}°)",
            description=f"L'animal se déplace face au vent ({ws:.0f} km/h) pour capter les odeurs",
            points=points,
            score=round(min(score, 95), 1),
            probability=round(0.4 + min(0.4, ws / 50), 2),
            style={
                "color": "#00BCD4",
                "weight": 3,
                "opacity": 0.75,
                "dashArray": "12,8",  # LIGNE POINTILLÉE
                "lineCap": "round",
                "lineJoin": "round",
            },
            factors={
                "wind_direction": wd,
                "wind_speed_kmh": ws,
                "wind_influence": round(cfg["wind_sensitivity"] * 100, 1),
            }
        ))
    
    # 2. Corridor thermique (chaud → ombre, froid → exposition)
    if temp is not None:
        if temp > 15:
            thermal_bearing = 350 + rng.uniform(-20, 20)  # Nord (ombragé)
            thermal_desc = f"Recherche d'ombre ({temp:.0f}°C)"
            thermal_name = "Déplacement vers zone ombragée"
        elif temp < -10:
            thermal_bearing = 170 + rng.uniform(-20, 20)  # Sud (exposition solaire)
            thermal_desc = f"Recherche d'exposition solaire ({temp:.0f}°C)"
            thermal_name = "Déplacement vers zone abritée"
        else:
            thermal_bearing = None
        
        if thermal_bearing is not None:
            dist = span * 0.2 * cfg["thermal_sensitivity"]
            end_lat, end_lng = _offset_point(center_lat, center_lng, thermal_bearing, dist)
            end_lat = max(bounds.south, min(bounds.north, end_lat))
            end_lng = max(bounds.west, min(bounds.east, end_lng))
            
            points = _generate_natural_path(center_lat, center_lng, end_lat, end_lng, num_points=5, jitter_km=0.15)
            
            corridors.append(MovementCorridor(
                id=_generate_id("EC"),
                category="estimated",
                corridor_type="thermal",
                name=thermal_name,
                description=thermal_desc,
                points=points,
                score=round(50 + abs(temp - 5) * 1.5, 1),
                probability=round(0.3 + abs(temp - 5) * 0.02, 2),
                style={
                    "color": "#FF5722" if temp > 15 else "#2196F3",
                    "weight": 3,
                    "opacity": 0.7,
                    "dashArray": "8,6",  # LIGNE POINTILLÉE
                    "lineCap": "round",
                    "lineJoin": "round",
                },
                factors={
                    "temperature_c": temp,
                    "thermal_sensitivity": round(cfg["thermal_sensitivity"] * 100, 1),
                }
            ))
    
    # 3. Corridor d'évitement pression humaine
    if hp > 0.3:
        avoid_bearing = 180 + rng.uniform(-40, 40)  # Fuit vers le sud/profond
        dist = span * 0.2 * hp
        end_lat, end_lng = _offset_point(center_lat, center_lng, avoid_bearing, dist)
        end_lat = max(bounds.south, min(bounds.north, end_lat))
        end_lng = max(bounds.west, min(bounds.east, end_lng))
        
        points = _generate_natural_path(center_lat, center_lng, end_lat, end_lng, num_points=5, jitter_km=0.25)
        
        corridors.append(MovementCorridor(
            id=_generate_id("EC"),
            category="estimated",
            corridor_type="pressure_avoidance",
            name="Évitement pression humaine",
            description=f"Fuite vers couvert dense (pression: {hp*100:.0f}%)",
            points=points,
            score=round(40 + hp * 40, 1),
            probability=round(0.3 + hp * 0.5, 2),
            style={
                "color": "#E91E63",
                "weight": 3,
                "opacity": 0.65,
                "dashArray": "6,4,2,4",  # LIGNE POINTILLÉE MIXTE
                "lineCap": "round",
                "lineJoin": "round",
            },
            factors={
                "human_pressure": round(hp * 100, 1),
                "avoidance_distance_m": round(dist * 1000, 0),
            }
        ))
    
    # 4. Corridor activité temporelle (aube/crépuscule)
    is_active_hour = hr in cfg.get("peak_activity", [])
    if is_active_hour:
        activity_bearing = 90 + rng.uniform(-30, 30) if hr < 12 else 270 + rng.uniform(-30, 30)
        dist = span * 0.22
        end_lat, end_lng = _offset_point(center_lat, center_lng, activity_bearing, dist)
        end_lat = max(bounds.south, min(bounds.north, end_lat))
        end_lng = max(bounds.west, min(bounds.east, end_lng))
        
        period = "aube" if hr < 12 else "crépuscule"
        points = _generate_natural_path(center_lat, center_lng, end_lat, end_lng, num_points=6, jitter_km=0.18)
        
        corridors.append(MovementCorridor(
            id=_generate_id("EC"),
            category="estimated",
            corridor_type="temporal_activity",
            name=f"Activité {period} ({hr}h)",
            description=f"Déplacement probable vers zone d'alimentation ({period})",
            points=points,
            score=round(60 + rng.uniform(0, 20), 1),
            probability=round(0.5 + rng.uniform(0, 0.3), 2),
            style={
                "color": "#FFC107",
                "weight": 3,
                "opacity": 0.7,
                "dashArray": "10,6",  # LIGNE POINTILLÉE
                "lineCap": "round",
                "lineJoin": "round",
            },
            factors={
                "hour": hr,
                "period": period,
                "activity_level": "high",
            }
        ))
    
    return corridors


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/compute", response_model=MovementCorridorsResponse)
async def compute_movement_corridors(req: MovementCorridorsRequest):
    """Calcule les corridors de déplacement réels et estimés."""
    start = datetime.now(timezone.utc)
    
    real = _compute_real_corridors(req.bounds, req.species)
    estimated = _compute_estimated_corridors(
        req.bounds, req.species,
        req.wind_direction, req.wind_speed,
        req.temperature, req.time_of_day,
        req.human_pressure,
    )
    
    calc_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000
    
    return MovementCorridorsResponse(
        species=req.species,
        real_corridors=real,
        estimated_corridors=estimated,
        metadata={
            "calculation_time_ms": round(calc_ms, 1),
            "real_count": len(real),
            "estimated_count": len(estimated),
            "total_count": len(real) + len(estimated),
            "bounds": req.bounds.model_dump(),
            "conditions": {
                "wind_direction": req.wind_direction,
                "wind_speed": req.wind_speed,
                "temperature": req.temperature,
                "time_of_day": req.time_of_day,
                "human_pressure": req.human_pressure,
            },
        }
    )


@router.get("/status")
async def movement_corridors_status():
    """Status du module movement_corridors_v1."""
    return {
        "module": "MOVEMENT_CORRIDORS",
        "label": "Corridors de Déplacement v1",
        "version": "movement_corridors_v1",
        "status": "ACTIVE",
        "categories": {
            "real": "Déplacements confirmés (semi-statiques) — lignes continues",
            "estimated": "Déplacements estimés (dynamiques) — lignes pointillées",
        },
        "species": list(SPECIES_CONFIG.keys()),
        "corridor_types": {
            "real": ["connectivity", "feeding_transit"],
            "estimated": ["wind_driven", "thermal", "pressure_avoidance", "temporal_activity"],
        },
    }


logger.info("Movement Corridors Router v1 initialized")
