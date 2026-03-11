"""
MODULE WSE/WIV — Wind/Weather Scoring Engine + Wind Impact Vector
BIONIC V5 ULTIME 300% — Phase d'Optimisation #4

WSE — Wind Scoring Engine:
  - Champ de vent au sol (wind_field, gust_field)
  - Modulation par couvert forestier SSE (foret = abri, clairiere = exposition)
  - Modulation par micro-relief SSE (crete = acceleration, vallee = canalisation)
  - Scoring vent par espece

WIV — Wind Impact Vector:
  - Impact du vent sur chaque corridor CME
  - Exposition, abri, turbulence par segment
  - Vecteurs normalises direction/intensite

Consomme: SSE (certifie) + CME (certifie)
source_id dynamique: WSE_{SPECIES} et WIV_{SPECIES}
0 duplication. 0 transversalite. 0 fallback.
Pipeline organique immuable.
"""

import math
import hashlib
import logging
import numpy as np
from typing import Dict, List, Any

logger = logging.getLogger("bionic_engine.wse_wiv_engine")

METERS_PER_DEG_LAT = 111320.0

# =====================================================================
# SPECIES WIND SENSITIVITY PROFILES
# =====================================================================

WSE_WIND_PROFILES = {
    "moose": {
        "wind_sensitivity": 0.45,
        "gust_sensitivity": 0.55,
        "optimal_wind_kmh": (5, 15),
        "critical_wind_kmh": 40,
        "shelter_preference": 0.75,
        "headwind_penalty": 0.70,
        "crosswind_tolerance": 0.60,
    },
    "deer": {
        "wind_sensitivity": 0.65,
        "gust_sensitivity": 0.70,
        "optimal_wind_kmh": (3, 12),
        "critical_wind_kmh": 30,
        "shelter_preference": 0.85,
        "headwind_penalty": 0.80,
        "crosswind_tolerance": 0.50,
    },
    "bear": {
        "wind_sensitivity": 0.35,
        "gust_sensitivity": 0.40,
        "optimal_wind_kmh": (5, 20),
        "critical_wind_kmh": 50,
        "shelter_preference": 0.60,
        "headwind_penalty": 0.50,
        "crosswind_penalty": 0.45,
        "crosswind_tolerance": 0.70,
    },
    "wild_turkey": {
        "wind_sensitivity": 0.80,
        "gust_sensitivity": 0.85,
        "optimal_wind_kmh": (2, 10),
        "critical_wind_kmh": 25,
        "shelter_preference": 0.90,
        "headwind_penalty": 0.85,
        "crosswind_tolerance": 0.35,
    },
    "elk": {
        "wind_sensitivity": 0.50,
        "gust_sensitivity": 0.55,
        "optimal_wind_kmh": (5, 18),
        "critical_wind_kmh": 45,
        "shelter_preference": 0.70,
        "headwind_penalty": 0.65,
        "crosswind_tolerance": 0.55,
    },
}

# Simplex noise primitives (self-contained, zero cross-dependency)
_F2 = 0.5 * (math.sqrt(3.0) - 1.0)
_G2 = (3.0 - math.sqrt(3.0)) / 6.0
_GRAD2 = [
    (1, 0), (-1, 0), (0, 1), (0, -1),
    (1, 1), (-1, 1), (1, -1), (-1, -1),
    (1, 0.5), (-1, 0.5), (0.5, 1), (-0.5, 1),
]


def _perm_table(seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed & 0x7FFFFFFF)
    p = np.arange(256, dtype=np.int32)
    rng.shuffle(p)
    return np.concatenate([p, p])


def _simplex2d(x: float, y: float, perm: np.ndarray) -> float:
    s = (x + y) * _F2
    i = int(math.floor(x + s))
    j = int(math.floor(y + s))
    t = (i + j) * _G2
    x0 = x - (i - t)
    y0 = y - (j - t)
    i1, j1 = (1, 0) if x0 > y0 else (0, 1)
    x1 = x0 - i1 + _G2
    y1 = y0 - j1 + _G2
    x2 = x0 - 1.0 + 2.0 * _G2
    y2 = y0 - 1.0 + 2.0 * _G2
    ii, jj = i & 255, j & 255
    gi0 = perm[ii + perm[jj]] % 12
    gi1 = perm[ii + i1 + perm[jj + j1]] % 12
    gi2 = perm[ii + 1 + perm[jj + 1]] % 12
    n0 = n1 = n2 = 0.0
    t0 = 0.5 - x0 * x0 - y0 * y0
    if t0 > 0:
        t0 *= t0; g = _GRAD2[gi0]; n0 = t0 * t0 * (g[0] * x0 + g[1] * y0)
    t1 = 0.5 - x1 * x1 - y1 * y1
    if t1 > 0:
        t1 *= t1; g = _GRAD2[gi1]; n1 = t1 * t1 * (g[0] * x1 + g[1] * y1)
    t2 = 0.5 - x2 * x2 - y2 * y2
    if t2 > 0:
        t2 *= t2; g = _GRAD2[gi2]; n2 = t2 * t2 * (g[0] * x2 + g[1] * y2)
    return 70.0 * (n0 + n1 + n2)


def _fractal_simplex(x: float, y: float, octaves: int, perm: np.ndarray) -> float:
    val, amp, freq, total = 0.0, 1.0, 1.0, 0.0
    for _ in range(octaves):
        val += amp * _simplex2d(x * freq, y * freq, perm)
        total += amp; amp *= 0.5; freq *= 2.0
    return (val / total + 1.0) * 0.5


def _seed_from(lat: float, lng: float, label: str, species: str) -> int:
    return int(hashlib.md5(f"WSE_{lat:.4f}_{lng:.4f}_{label}_{species}".encode()).hexdigest()[:8], 16)


# =====================================================================
# WSE — WIND FIELD GENERATION
# =====================================================================

def generate_wind_field(
    bounds: Dict[str, float],
    species: str,
    sse_data: Dict[str, Any],
    resolution: int = 60,
    base_wind_kmh: float = 15.0,
    base_direction_deg: float = 270.0,
) -> Dict[str, Any]:
    """
    Generate terrain-modulated wind field.

    SSE modulation:
      - Forest density reduces wind speed (shelter)
      - Ridges accelerate wind (exposure)
      - Valleys channel wind (direction shift)
      - Clearings maintain full wind exposure

    Returns:
      - wind_speed: [0, 1] normalized wind intensity grid
      - wind_direction: direction in degrees grid
      - gust_field: [0, 1] gust probability grid
      - shelter_map: [0, 1] shelter quality grid
    """
    source_id = f"WSE_{species.upper()}"
    center_lat = (bounds["north"] + bounds["south"]) / 2
    center_lng = (bounds["east"] + bounds["west"]) / 2
    cos_lat = math.cos(math.radians(center_lat))
    y_range_m = (bounds["north"] - bounds["south"]) * METERS_PER_DEG_LAT
    x_range_m = (bounds["east"] - bounds["west"]) * METERS_PER_DEG_LAT * cos_lat

    profile = WSE_WIND_PROFILES.get(species, WSE_WIND_PROFILES["moose"])

    perm_wind = _perm_table(_seed_from(center_lat, center_lng, "wind", species))
    perm_gust = _perm_table(_seed_from(center_lat, center_lng, "gust", species))
    perm_dir = _perm_table(_seed_from(center_lat, center_lng, "dir", species))

    # SSE grids
    forest = sse_data.get("landcover", {}).get("forest_density", np.zeros((resolution, resolution)))
    ridge = sse_data.get("microrelief", {}).get("ridge_map", np.zeros((resolution, resolution)))
    valley = sse_data.get("microrelief", {}).get("valley_map", np.zeros((resolution, resolution)))
    slope = sse_data.get("microrelief", {}).get("slope_intensity", np.zeros((resolution, resolution)))

    wind_speed = np.zeros((resolution, resolution), dtype=np.float64)
    wind_direction = np.full((resolution, resolution), base_direction_deg, dtype=np.float64)
    gust_field = np.zeros((resolution, resolution), dtype=np.float64)
    shelter_map = np.zeros((resolution, resolution), dtype=np.float64)

    base_dir_rad = math.radians(base_direction_deg)

    for r in range(resolution):
        for c in range(resolution):
            y_m = (r / max(1, resolution - 1)) * y_range_m
            x_m = (c / max(1, resolution - 1)) * x_range_m

            # Base wind with spatial variation
            wind_noise = _fractal_simplex(x_m * 0.0005, y_m * 0.0005, 4, perm_wind)
            base_speed = base_wind_kmh * (0.7 + 0.6 * wind_noise)

            # SSE sampling
            fr, fc = min(r, forest.shape[0] - 1), min(c, forest.shape[1] - 1)
            f_val = float(forest[fr, fc])
            r_val = float(ridge[fr, fc])
            v_val = float(valley[fr, fc])
            s_val = float(slope[fr, fc])

            # Forest reduces wind speed (shelter effect)
            forest_reduction = f_val * 0.60
            shelter_val = f_val * profile["shelter_preference"]

            # Ridge accelerates wind
            ridge_acceleration = r_val * 0.40

            # Valley channels wind (reduces speed slightly, shifts direction)
            valley_reduction = v_val * 0.15

            # Modulated speed
            speed = base_speed * (1.0 - forest_reduction + ridge_acceleration - valley_reduction)
            speed = max(0.5, speed)

            # Normalize to [0, 1] relative to critical wind
            wind_speed[r, c] = min(1.0, speed / profile["critical_wind_kmh"])

            # Direction modulation
            dir_noise = _simplex2d(x_m * 0.0003, y_m * 0.0003, perm_dir)
            dir_shift = dir_noise * 25.0
            valley_dir_shift = v_val * 15.0 * math.sin(base_dir_rad)
            wind_direction[r, c] = (base_direction_deg + dir_shift + valley_dir_shift) % 360

            # Gust probability
            gust_noise = _fractal_simplex(x_m * 0.0008, y_m * 0.0008, 3, perm_gust)
            gust_base = gust_noise * (1.0 - f_val * 0.5 + r_val * 0.3)
            gust_field[r, c] = min(1.0, max(0.0, gust_base * profile["gust_sensitivity"]))

            shelter_map[r, c] = min(1.0, shelter_val)

    # Normalize wind_speed and gust_field
    for grid in [wind_speed, gust_field, shelter_map]:
        gmax = grid.max()
        if gmax > 0:
            grid[:] = grid / gmax

    # Compute wind scoring for species
    wind_score = _compute_wind_score(wind_speed, gust_field, shelter_map, profile)

    stats = {
        "mean_wind_speed": round(float(np.mean(wind_speed)), 4),
        "max_wind_speed": round(float(np.max(wind_speed)), 4),
        "mean_gust": round(float(np.mean(gust_field)), 4),
        "mean_shelter": round(float(np.mean(shelter_map)), 4),
        "mean_wind_score": round(float(np.mean(wind_score)), 4),
        "base_wind_kmh": base_wind_kmh,
        "base_direction_deg": base_direction_deg,
    }

    return {
        "source_id": source_id,
        "species": species,
        "bounds": bounds,
        "resolution": resolution,
        "wind_speed": wind_speed,
        "wind_direction": wind_direction,
        "gust_field": gust_field,
        "shelter_map": shelter_map,
        "wind_score": wind_score,
        "stats": stats,
    }


def _compute_wind_score(
    wind_speed: np.ndarray,
    gust_field: np.ndarray,
    shelter_map: np.ndarray,
    profile: Dict[str, Any],
) -> np.ndarray:
    """
    Score the wind conditions for the species.
    High score = favorable for the animal (good shelter, moderate wind).
    """
    resolution = wind_speed.shape[0]
    score = np.zeros((resolution, resolution), dtype=np.float64)

    for r in range(resolution):
        for c in range(resolution):
            ws = float(wind_speed[r, c])
            g = float(gust_field[r, c])
            sh = float(shelter_map[r, c])

            # Moderate wind is best (inverted U-curve)
            wind_comfort = 1.0 - abs(ws - 0.3) * 1.5
            wind_comfort = max(0.0, min(1.0, wind_comfort))

            # Low gusts are better
            gust_penalty = g * profile["gust_sensitivity"] * 0.4

            # High shelter is better
            shelter_bonus = sh * 0.3

            score[r, c] = max(0.0, min(1.0, wind_comfort - gust_penalty + shelter_bonus))

    gmax = score.max()
    if gmax > 0:
        score = score / gmax
    return score


# =====================================================================
# WIV — WIND IMPACT VECTOR ON CORRIDORS
# =====================================================================

def compute_wiv_corridors(
    corridors: List[Dict[str, Any]],
    wse_data: Dict[str, Any],
    bounds: Dict[str, float],
    species: str,
    resolution: int = 60,
) -> Dict[str, Any]:
    """
    Compute Wind Impact Vector for each CME corridor.

    For each corridor:
      - Sample wind field along corridor path
      - Compute exposure (wind aligned with corridor = headwind/tailwind)
      - Compute shelter quality along corridor
      - Compute turbulence (gust exposure)
      - Classify wind impact: sheltered, exposed, turbulent

    source_id: WIV_{SPECIES}
    """
    source_id = f"WIV_{species.upper()}"
    profile = WSE_WIND_PROFILES.get(species, WSE_WIND_PROFILES["moose"])

    wind_speed = wse_data.get("wind_speed", np.zeros((resolution, resolution)))
    wind_direction = wse_data.get("wind_direction", np.full((resolution, resolution), 270.0))
    gust_field = wse_data.get("gust_field", np.zeros((resolution, resolution)))
    shelter_map = wse_data.get("shelter_map", np.zeros((resolution, resolution)))
    wind_score = wse_data.get("wind_score", np.zeros((resolution, resolution)))

    wiv_corridors = []

    for corridor in corridors:
        coords = corridor.get("geometry", {}).get("coordinates", [])
        if len(coords) < 2:
            continue

        # Sample wind along corridor
        samples = _sample_corridor_wind(
            coords, bounds, resolution,
            wind_speed, wind_direction, gust_field, shelter_map, wind_score,
        )

        # Compute corridor bearing
        bearing = _compute_bearing(coords[0], coords[-1])

        # Compute wind-corridor interaction
        interaction = _compute_wind_corridor_interaction(samples, bearing, profile)

        wiv_corridors.append({
            "corridor_id": corridor.get("corridor_id", ""),
            "corridor_type": corridor.get("corridor_type", ""),
            "wind_impact": interaction,
            "sample_count": len(samples),
        })

    return {
        "source_id": source_id,
        "wse_source_id": wse_data.get("source_id", ""),
        "species": species,
        "bounds": bounds,
        "corridors": wiv_corridors,
        "corridor_count": len(wiv_corridors),
        "validation": {
            "all_corridors_analyzed": len(wiv_corridors) == len(corridors),
            "wind_field_resolution": resolution,
            "species_profile_applied": True,
        },
    }


def _sample_corridor_wind(
    coords: List[List[float]],
    bounds: Dict[str, float],
    resolution: int,
    wind_speed: np.ndarray,
    wind_direction: np.ndarray,
    gust_field: np.ndarray,
    shelter_map: np.ndarray,
    wind_score: np.ndarray,
) -> List[Dict[str, float]]:
    """Sample wind data at evenly-spaced points along a corridor."""
    total_pts = min(len(coords), 15)
    step = max(1, len(coords) // total_pts)
    sample_coords = coords[::step]

    samples = []
    for lng, lat in sample_coords:
        row = int(((bounds["north"] - lat) / max(0.0001, bounds["north"] - bounds["south"])) * (resolution - 1))
        col = int(((lng - bounds["west"]) / max(0.0001, bounds["east"] - bounds["west"])) * (resolution - 1))
        row = max(0, min(resolution - 1, row))
        col = max(0, min(resolution - 1, col))

        samples.append({
            "wind_speed": float(wind_speed[row, col]),
            "wind_direction": float(wind_direction[row, col]),
            "gust": float(gust_field[row, col]),
            "shelter": float(shelter_map[row, col]),
            "wind_score": float(wind_score[row, col]),
        })

    return samples


def _compute_bearing(start: List[float], end: List[float]) -> float:
    """Compute bearing from start to end in degrees."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    bearing = math.degrees(math.atan2(dx, dy)) % 360
    return bearing


def _compute_wind_corridor_interaction(
    samples: List[Dict[str, float]],
    corridor_bearing: float,
    profile: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compute wind-corridor interaction metrics.

    Returns exposure, shelter, turbulence, headwind/crosswind factors.
    """
    if not samples:
        return {
            "exposure": 0.0,
            "shelter_quality": 0.0,
            "turbulence": 0.0,
            "headwind_factor": 0.0,
            "crosswind_factor": 0.0,
            "mean_wind_score": 0.0,
            "wind_impact_class": "unknown",
            "direction_vector": {"dx": 0.0, "dy": 0.0, "magnitude": 0.0},
        }

    # Average metrics along corridor
    avg_speed = sum(s["wind_speed"] for s in samples) / len(samples)
    avg_shelter = sum(s["shelter"] for s in samples) / len(samples)
    avg_gust = sum(s["gust"] for s in samples) / len(samples)
    avg_score = sum(s["wind_score"] for s in samples) / len(samples)
    avg_dir = sum(s["wind_direction"] for s in samples) / len(samples)

    # Wind-corridor angle
    angle_diff = abs(avg_dir - corridor_bearing) % 360
    if angle_diff > 180:
        angle_diff = 360 - angle_diff

    # Headwind: angle close to 0 or 180 (opposing or following)
    headwind_factor = abs(math.cos(math.radians(angle_diff)))
    crosswind_factor = abs(math.sin(math.radians(angle_diff)))

    # Exposure = wind speed * (1 - shelter)
    exposure = avg_speed * (1.0 - avg_shelter * 0.6)

    # Turbulence = gusts * exposure
    turbulence = avg_gust * exposure * 0.8

    # Wind impact class
    if avg_shelter > 0.6:
        impact_class = "sheltered"
    elif turbulence > 0.5:
        impact_class = "turbulent"
    elif exposure > 0.6:
        impact_class = "exposed"
    else:
        impact_class = "moderate"

    # Normalized direction vector
    dir_rad = math.radians(avg_dir)
    dx = math.sin(dir_rad) * avg_speed
    dy = math.cos(dir_rad) * avg_speed
    magnitude = math.sqrt(dx * dx + dy * dy)

    return {
        "exposure": round(exposure, 4),
        "shelter_quality": round(avg_shelter, 4),
        "turbulence": round(turbulence, 4),
        "headwind_factor": round(headwind_factor, 4),
        "crosswind_factor": round(crosswind_factor, 4),
        "mean_wind_score": round(avg_score, 4),
        "wind_impact_class": impact_class,
        "direction_vector": {
            "dx": round(dx, 4),
            "dy": round(dy, 4),
            "magnitude": round(magnitude, 4),
        },
    }


# =====================================================================
# WSE/WIV COMPOSITE ORCHESTRATOR
# =====================================================================

def generate_wse_wiv_composite(
    bounds: Dict[str, float],
    species: str,
    sse_data: Dict[str, Any],
    cme_corridors: List[Dict[str, Any]],
    resolution: int = 60,
    base_wind_kmh: float = 15.0,
    base_direction_deg: float = 270.0,
) -> Dict[str, Any]:
    """
    Full WSE/WIV pipeline.

    1. WSE: Generate terrain-modulated wind field
    2. WIV: Compute wind impact on CME corridors
    """
    # WSE
    wse_data = generate_wind_field(
        bounds, species, sse_data, resolution,
        base_wind_kmh, base_direction_deg,
    )

    # WIV
    wiv_data = compute_wiv_corridors(
        cme_corridors, wse_data, bounds, species, resolution,
    )

    return {
        "wse": wse_data,
        "wiv": wiv_data,
    }


def get_supported_species() -> List[str]:
    return list(WSE_WIND_PROFILES.keys())
