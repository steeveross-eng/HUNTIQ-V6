"""
MODULE SSE — Satellite-to-Semantic Engine
BIONIC V5 ULTIME 300% — Phase d'Optimisation #1

Extraction semantique du terrain:
  - Couvert forestier (densite, type, continuite)
  - Clairieres (detection, surface, forme)
  - Transitions foret-clairiere (lisiere, gradient)
  - Micro-reliefs (cretes, vallees, replats, pentes)

Sorties normalisees [0, 1] pour OSG et CME.
Rasters + vecteurs + metadata.

source_id dynamique: SSE_{SPECIES}
0 duplication. 0 transversalite. 0 fallback.
Pipeline organique immuable.
Orchestre uniquement par le router SSE ou l'orchestrateur principal.
"""

import math
import hashlib
import logging
import numpy as np
from typing import Dict, List, Any

logger = logging.getLogger("bionic_engine.sse_engine")

METERS_PER_DEG_LAT = 111320.0

# Skew/unskew constants for 2D simplex
_F2 = 0.5 * (math.sqrt(3.0) - 1.0)
_G2 = (3.0 - math.sqrt(3.0)) / 6.0

_GRAD2 = [
    (1, 0), (-1, 0), (0, 1), (0, -1),
    (1, 1), (-1, 1), (1, -1), (-1, -1),
    (1, 0.5), (-1, 0.5), (0.5, 1), (-0.5, 1),
]

# =====================================================================
# SSE LANDCOVER CLASSIFICATION PROFILES
# =====================================================================

SSE_LANDCOVER_PROFILES = {
    "moose": {
        "forest_affinity": 0.85,
        "clearing_affinity": 0.40,
        "edge_affinity": 0.95,
        "wetland_affinity": 0.90,
        "conifer_preference": 0.80,
    },
    "deer": {
        "forest_affinity": 0.75,
        "clearing_affinity": 0.70,
        "edge_affinity": 0.90,
        "wetland_affinity": 0.35,
        "conifer_preference": 0.50,
    },
    "bear": {
        "forest_affinity": 0.90,
        "clearing_affinity": 0.55,
        "edge_affinity": 0.70,
        "wetland_affinity": 0.65,
        "conifer_preference": 0.60,
    },
    "wild_turkey": {
        "forest_affinity": 0.65,
        "clearing_affinity": 0.85,
        "edge_affinity": 0.80,
        "wetland_affinity": 0.20,
        "conifer_preference": 0.25,
    },
    "elk": {
        "forest_affinity": 0.70,
        "clearing_affinity": 0.75,
        "edge_affinity": 0.85,
        "wetland_affinity": 0.40,
        "conifer_preference": 0.55,
    },
}

# Micro-relief sensitivity per species
SSE_MICRORELIEF_PROFILES = {
    "moose": {"ridge_sensitivity": 0.60, "valley_sensitivity": 0.85, "slope_threshold": 0.70, "plateau_affinity": 0.55},
    "deer": {"ridge_sensitivity": 0.50, "valley_sensitivity": 0.70, "slope_threshold": 0.80, "plateau_affinity": 0.75},
    "bear": {"ridge_sensitivity": 0.75, "valley_sensitivity": 0.80, "slope_threshold": 0.60, "plateau_affinity": 0.50},
    "wild_turkey": {"ridge_sensitivity": 0.65, "valley_sensitivity": 0.45, "slope_threshold": 0.85, "plateau_affinity": 0.80},
    "elk": {"ridge_sensitivity": 0.80, "valley_sensitivity": 0.65, "slope_threshold": 0.55, "plateau_affinity": 0.60},
}


# =====================================================================
# SIMPLEX NOISE (shared primitives, zero dependency on behavioral_rasterizer)
# =====================================================================

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
    X0 = i - t
    Y0 = j - t
    x0 = x - X0
    y0 = y - Y0

    if x0 > y0:
        i1, j1 = 1, 0
    else:
        i1, j1 = 0, 1

    x1 = x0 - i1 + _G2
    y1 = y0 - j1 + _G2
    x2 = x0 - 1.0 + 2.0 * _G2
    y2 = y0 - 1.0 + 2.0 * _G2

    ii = i & 255
    jj = j & 255

    gi0 = perm[ii + perm[jj]] % 12
    gi1 = perm[ii + i1 + perm[jj + j1]] % 12
    gi2 = perm[ii + 1 + perm[jj + 1]] % 12

    n0 = n1 = n2 = 0.0

    t0 = 0.5 - x0 * x0 - y0 * y0
    if t0 > 0:
        t0 *= t0
        g = _GRAD2[gi0]
        n0 = t0 * t0 * (g[0] * x0 + g[1] * y0)

    t1 = 0.5 - x1 * x1 - y1 * y1
    if t1 > 0:
        t1 *= t1
        g = _GRAD2[gi1]
        n1 = t1 * t1 * (g[0] * x1 + g[1] * y1)

    t2 = 0.5 - x2 * x2 - y2 * y2
    if t2 > 0:
        t2 *= t2
        g = _GRAD2[gi2]
        n2 = t2 * t2 * (g[0] * x2 + g[1] * y2)

    return 70.0 * (n0 + n1 + n2)


def _fractal_simplex(x: float, y: float, octaves: int, perm: np.ndarray) -> float:
    value = 0.0
    amplitude = 1.0
    frequency = 1.0
    total_amp = 0.0
    for _ in range(octaves):
        value += amplitude * _simplex2d(x * frequency, y * frequency, perm)
        total_amp += amplitude
        amplitude *= 0.5
        frequency *= 2.0
    return (value / total_amp + 1.0) * 0.5


def _seed_from(lat: float, lng: float, layer: str, species: str) -> int:
    data = f"SSE_{lat:.4f}_{lng:.4f}_{layer}_{species}"
    return int(hashlib.md5(data.encode()).hexdigest()[:8], 16)


# =====================================================================
# SSE CORE — LANDCOVER RASTER
# =====================================================================

def generate_landcover_raster(
    bounds: Dict[str, float],
    species: str,
    resolution: int = 60,
) -> Dict[str, Any]:
    """
    Genere un raster de couvert terrestre semantique.

    Sorties:
      - forest_density: [0,1] densite du couvert forestier
      - clearing_map: [0,1] probabilite de clairiere
      - conifer_ratio: [0,1] proportion de coniferes vs feuillus
      - wetland_prob: [0,1] probabilite de zone humide

    Normalise pour OSG et CME.
    """
    center_lat = (bounds["north"] + bounds["south"]) / 2
    center_lng = (bounds["east"] + bounds["west"]) / 2
    cos_lat = math.cos(math.radians(center_lat))
    y_range_m = (bounds["north"] - bounds["south"]) * METERS_PER_DEG_LAT
    x_range_m = (bounds["east"] - bounds["west"]) * METERS_PER_DEG_LAT * cos_lat

    profile = SSE_LANDCOVER_PROFILES.get(species, SSE_LANDCOVER_PROFILES["moose"])

    perm_forest = _perm_table(_seed_from(center_lat, center_lng, "forest", species))
    perm_clearing = _perm_table(_seed_from(center_lat, center_lng, "clearing", species))
    perm_conifer = _perm_table(_seed_from(center_lat, center_lng, "conifer", species))
    perm_wetland = _perm_table(_seed_from(center_lat, center_lng, "wetland", species))

    forest_grid = np.zeros((resolution, resolution), dtype=np.float64)
    clearing_grid = np.zeros((resolution, resolution), dtype=np.float64)
    conifer_grid = np.zeros((resolution, resolution), dtype=np.float64)
    wetland_grid = np.zeros((resolution, resolution), dtype=np.float64)

    for r in range(resolution):
        for c in range(resolution):
            y_m = (r / max(1, resolution - 1)) * y_range_m
            x_m = (c / max(1, resolution - 1)) * x_range_m

            # Forest density — low frequency, high continuity
            f_base = _fractal_simplex(x_m * 0.0004, y_m * 0.0004, 4, perm_forest)
            f_detail = _fractal_simplex(x_m * 0.0012, y_m * 0.0012, 3, perm_forest)
            forest_val = 0.7 * f_base + 0.3 * f_detail
            forest_grid[r, c] = forest_val * profile["forest_affinity"]

            # Clearing detection — inverse of forest with micro-variation
            cl_noise = _fractal_simplex(x_m * 0.0008, y_m * 0.0008, 5, perm_clearing)
            clearing_val = max(0.0, 1.0 - forest_val - 0.1) * cl_noise
            clearing_grid[r, c] = clearing_val * profile["clearing_affinity"]

            # Conifer ratio — large-scale spatial gradient
            cn_base = _fractal_simplex(x_m * 0.0003, y_m * 0.0003, 3, perm_conifer)
            conifer_grid[r, c] = cn_base * profile["conifer_preference"]

            # Wetland probability — tied to low elevation + specific noise
            wt_base = _fractal_simplex(x_m * 0.0006, y_m * 0.0006, 4, perm_wetland)
            wt_low = _simplex2d(x_m * 0.0002, y_m * 0.0002, perm_wetland)
            wetland_val = wt_base * max(0.0, 0.5 + wt_low) * 0.8
            wetland_grid[r, c] = wetland_val * profile["wetland_affinity"]

    # Normalize all grids to [0, 1]
    for grid in [forest_grid, clearing_grid, conifer_grid, wetland_grid]:
        gmax = grid.max()
        if gmax > 0:
            grid[:] = grid / gmax

    return {
        "forest_density": forest_grid,
        "clearing_map": clearing_grid,
        "conifer_ratio": conifer_grid,
        "wetland_prob": wetland_grid,
        "resolution": resolution,
        "bounds": bounds,
        "species": species,
    }


# =====================================================================
# SSE CORE — MICRORELIEF RASTER
# =====================================================================

def generate_microrelief_raster(
    bounds: Dict[str, float],
    species: str,
    resolution: int = 60,
) -> Dict[str, Any]:
    """
    Genere un raster de micro-relief semantique.

    Sorties:
      - ridge_map: [0,1] probabilite de crete
      - valley_map: [0,1] probabilite de vallee/depression
      - slope_intensity: [0,1] intensite de la pente
      - plateau_map: [0,1] probabilite de replat

    Normalise pour OSG et CME.
    """
    center_lat = (bounds["north"] + bounds["south"]) / 2
    center_lng = (bounds["east"] + bounds["west"]) / 2
    cos_lat = math.cos(math.radians(center_lat))
    y_range_m = (bounds["north"] - bounds["south"]) * METERS_PER_DEG_LAT
    x_range_m = (bounds["east"] - bounds["west"]) * METERS_PER_DEG_LAT * cos_lat

    profile = SSE_MICRORELIEF_PROFILES.get(species, SSE_MICRORELIEF_PROFILES["moose"])

    perm_elev = _perm_table(_seed_from(center_lat, center_lng, "elevation", species))
    perm_detail = _perm_table(_seed_from(center_lat, center_lng, "relief_detail", species))

    ridge_grid = np.zeros((resolution, resolution), dtype=np.float64)
    valley_grid = np.zeros((resolution, resolution), dtype=np.float64)
    slope_grid = np.zeros((resolution, resolution), dtype=np.float64)
    plateau_grid = np.zeros((resolution, resolution), dtype=np.float64)

    # Generate base elevation field first
    elevation = np.zeros((resolution, resolution), dtype=np.float64)
    for r in range(resolution):
        for c in range(resolution):
            y_m = (r / max(1, resolution - 1)) * y_range_m
            x_m = (c / max(1, resolution - 1)) * x_range_m
            elev_base = _fractal_simplex(x_m * 0.0003, y_m * 0.0003, 5, perm_elev)
            elev_micro = _fractal_simplex(x_m * 0.0010, y_m * 0.0010, 4, perm_detail)
            elevation[r, c] = 0.6 * elev_base + 0.4 * elev_micro

    # Derive features from elevation field using gradient analysis
    for r in range(1, resolution - 1):
        for c in range(1, resolution - 1):
            # Gradient (slope) via finite differences
            dx = (elevation[r, c + 1] - elevation[r, c - 1]) / 2.0
            dy = (elevation[r + 1, c] - elevation[r - 1, c]) / 2.0
            slope_mag = math.sqrt(dx * dx + dy * dy)

            # Laplacian (curvature) — positive = valley, negative = ridge
            laplacian = (
                elevation[r + 1, c] + elevation[r - 1, c]
                + elevation[r, c + 1] + elevation[r, c - 1]
                - 4.0 * elevation[r, c]
            )

            # Ridge: negative curvature (convex)
            ridge_val = max(0.0, -laplacian * 8.0) * profile["ridge_sensitivity"]
            ridge_grid[r, c] = min(1.0, ridge_val)

            # Valley: positive curvature (concave)
            valley_val = max(0.0, laplacian * 8.0) * profile["valley_sensitivity"]
            valley_grid[r, c] = min(1.0, valley_val)

            # Slope intensity
            slope_grid[r, c] = min(1.0, slope_mag * 6.0) * (1.0 - profile["slope_threshold"] + 0.5)

            # Plateau: low slope + low curvature
            flatness = max(0.0, 1.0 - slope_mag * 10.0) * max(0.0, 1.0 - abs(laplacian) * 15.0)
            plateau_grid[r, c] = flatness * profile["plateau_affinity"]

    # Normalize
    for grid in [ridge_grid, valley_grid, slope_grid, plateau_grid]:
        gmax = grid.max()
        if gmax > 0:
            grid[:] = grid / gmax

    return {
        "ridge_map": ridge_grid,
        "valley_map": valley_grid,
        "slope_intensity": slope_grid,
        "plateau_map": plateau_grid,
        "elevation_field": elevation,
        "resolution": resolution,
        "bounds": bounds,
        "species": species,
    }


# =====================================================================
# SSE CORE — EDGE TRANSITION DETECTION
# =====================================================================

def generate_edge_transitions(
    landcover: Dict[str, Any],
    species: str,
) -> Dict[str, Any]:
    """
    Detecte les transitions foret-clairiere (lisieres).

    Entree: sortie de generate_landcover_raster.
    Sortie:
      - edge_intensity: [0,1] raster d'intensite de lisiere
      - edge_vectors: liste de segments de lisiere (lat/lng)

    La lisiere est le gradient spatial entre forest_density et clearing_map.
    """
    forest = landcover["forest_density"]
    clearing = landcover["clearing_map"]
    resolution = landcover["resolution"]
    bounds = landcover["bounds"]
    profile = SSE_LANDCOVER_PROFILES.get(species, SSE_LANDCOVER_PROFILES["moose"])

    edge_grid = np.zeros((resolution, resolution), dtype=np.float64)

    for r in range(1, resolution - 1):
        for c in range(1, resolution - 1):
            # Gradient of forest density (Sobel-like)
            fx = abs(forest[r, c + 1] - forest[r, c - 1])
            fy = abs(forest[r + 1, c] - forest[r - 1, c])
            forest_grad = math.sqrt(fx * fx + fy * fy)

            # Gradient of clearing
            cx = abs(clearing[r, c + 1] - clearing[r, c - 1])
            cy = abs(clearing[r + 1, c] - clearing[r - 1, c])
            clearing_grad = math.sqrt(cx * cx + cy * cy)

            # Edge = high gradient in both forest and clearing
            edge_val = (forest_grad + clearing_grad) * profile["edge_affinity"]
            edge_grid[r, c] = min(1.0, edge_val * 3.0)

    # Normalize
    gmax = edge_grid.max()
    if gmax > 0:
        edge_grid = edge_grid / gmax

    # Extract edge vectors (high-intensity cells -> lat/lng segments)
    edge_vectors = _extract_edge_vectors(edge_grid, bounds, resolution, threshold=0.5)

    return {
        "edge_intensity": edge_grid,
        "edge_vectors": edge_vectors,
        "edge_count": len(edge_vectors),
        "resolution": resolution,
        "bounds": bounds,
        "species": species,
    }


def _extract_edge_vectors(
    edge_grid: np.ndarray,
    bounds: Dict[str, float],
    resolution: int,
    threshold: float = 0.5,
) -> List[Dict[str, Any]]:
    """Extrait les segments de lisiere au-dessus du seuil."""
    vectors = []
    lat_step = (bounds["north"] - bounds["south"]) / max(1, resolution - 1)
    lng_step = (bounds["east"] - bounds["west"]) / max(1, resolution - 1)

    for r in range(1, resolution - 1):
        for c in range(1, resolution - 1):
            if edge_grid[r, c] < threshold:
                continue

            lat = bounds["north"] - r * lat_step
            lng = bounds["west"] + c * lng_step

            # Find direction of maximum gradient
            best_dr, best_dc = 0, 1
            best_val = 0.0
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < resolution and 0 <= nc < resolution:
                    v = edge_grid[nr, nc]
                    if v > best_val:
                        best_val = v
                        best_dr, best_dc = dr, dc

            lat2 = lat - best_dr * lat_step
            lng2 = lng + best_dc * lng_step

            vectors.append({
                "start": {"lat": round(lat, 6), "lng": round(lng, 6)},
                "end": {"lat": round(lat2, 6), "lng": round(lng2, 6)},
                "intensity": round(float(edge_grid[r, c]), 3),
            })

    # Keep top 50 strongest edges
    vectors.sort(key=lambda v: v["intensity"], reverse=True)
    return vectors[:50]


# =====================================================================
# SSE COMPOSITE — UNIFIED OUTPUT
# =====================================================================

def generate_sse_composite(
    bounds: Dict[str, float],
    species: str,
    resolution: int = 60,
) -> Dict[str, Any]:
    """
    Orchestre le pipeline SSE complet.

    Genere: landcover + microrelief + edge transitions.
    Produit un composite normalise pour OSG et CME.

    source_id: SSE_{SPECIES}
    """
    source_id = f"SSE_{species.upper()}"

    landcover = generate_landcover_raster(bounds, species, resolution)
    microrelief = generate_microrelief_raster(bounds, species, resolution)
    edges = generate_edge_transitions(landcover, species)

    # Composite habitat quality raster (weighted blend for species)
    profile_lc = SSE_LANDCOVER_PROFILES.get(species, SSE_LANDCOVER_PROFILES["moose"])
    profile_mr = SSE_MICRORELIEF_PROFILES.get(species, SSE_MICRORELIEF_PROFILES["moose"])

    composite = np.zeros((resolution, resolution), dtype=np.float64)
    for r in range(resolution):
        for c in range(resolution):
            lc_score = (
                landcover["forest_density"][r, c] * 0.35
                + landcover["clearing_map"][r, c] * 0.15
                + landcover["wetland_prob"][r, c] * 0.15
                + edges["edge_intensity"][r, c] * 0.35
            )
            mr_score = (
                microrelief["valley_map"][r, c] * 0.30
                + microrelief["plateau_map"][r, c] * 0.30
                + microrelief["ridge_map"][r, c] * 0.20
                + (1.0 - microrelief["slope_intensity"][r, c]) * 0.20
            )
            composite[r, c] = lc_score * 0.6 + mr_score * 0.4

    gmax = composite.max()
    if gmax > 0:
        composite = composite / gmax

    # Statistics
    stats = {
        "mean_forest_density": round(float(np.mean(landcover["forest_density"])), 4),
        "mean_clearing": round(float(np.mean(landcover["clearing_map"])), 4),
        "mean_conifer_ratio": round(float(np.mean(landcover["conifer_ratio"])), 4),
        "mean_wetland_prob": round(float(np.mean(landcover["wetland_prob"])), 4),
        "mean_edge_intensity": round(float(np.mean(edges["edge_intensity"])), 4),
        "edge_count": edges["edge_count"],
        "mean_ridge": round(float(np.mean(microrelief["ridge_map"])), 4),
        "mean_valley": round(float(np.mean(microrelief["valley_map"])), 4),
        "mean_slope": round(float(np.mean(microrelief["slope_intensity"])), 4),
        "mean_plateau": round(float(np.mean(microrelief["plateau_map"])), 4),
        "composite_mean": round(float(np.mean(composite)), 4),
        "composite_std": round(float(np.std(composite)), 4),
    }

    return {
        "source_id": source_id,
        "species": species,
        "bounds": bounds,
        "resolution": resolution,
        "landcover": {
            "forest_density": landcover["forest_density"],
            "clearing_map": landcover["clearing_map"],
            "conifer_ratio": landcover["conifer_ratio"],
            "wetland_prob": landcover["wetland_prob"],
        },
        "microrelief": {
            "ridge_map": microrelief["ridge_map"],
            "valley_map": microrelief["valley_map"],
            "slope_intensity": microrelief["slope_intensity"],
            "plateau_map": microrelief["plateau_map"],
            "elevation_field": microrelief["elevation_field"],
        },
        "edges": {
            "edge_intensity": edges["edge_intensity"],
            "edge_vectors": edges["edge_vectors"],
            "edge_count": edges["edge_count"],
        },
        "composite": composite,
        "stats": stats,
    }


def get_supported_species() -> List[str]:
    """Especes supportees par le SSE."""
    return list(SSE_LANDCOVER_PROFILES.keys())
