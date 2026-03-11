"""
MODULE A — Behavioral Rasterizer V2
BIONIC V5 — Pipeline Organique Unifié

Génère des rasters d'intensité continus (grille numpy) pour chaque couche
comportementale et environnementale.

CORRECTIONS V2:
  - Bruit simplex 2D (open simplex) → isotrope, pas d'alignement d'axes
  - Échantillonnage en MÈTRES (pas en degrés) → pas d'étirement lat/lng
  - Masque de cluster graduel (pas binaire) → transitions naturelles
  - Fréquences calibrées pour produire des formes organiques irrégulières

100% indépendant. Aucune dépendance transversale.
Orchestré uniquement par zone_engine_core_v2.
"""

import math
import hashlib
import numpy as np
from typing import Dict, List

METERS_PER_DEG_LAT = 111320.0

LAYER_PARAMS = {
    "rut":            {"octaves": 5, "base_freq": 0.0012, "threshold": 0.52, "cluster": 0.65},
    "repos":          {"octaves": 4, "base_freq": 0.0008, "threshold": 0.55, "cluster": 0.70},
    "alimentation":   {"octaves": 5, "base_freq": 0.0015, "threshold": 0.48, "cluster": 0.55},
    "corridors":      {"octaves": 5, "base_freq": 0.0018, "threshold": 0.40, "cluster": 0.45},
    "habitats":       {"octaves": 4, "base_freq": 0.0010, "threshold": 0.50, "cluster": 0.65},
    "peuplements":    {"octaves": 3, "base_freq": 0.0007, "threshold": 0.52, "cluster": 0.80},
    "ndvi":           {"octaves": 5, "base_freq": 0.0010, "threshold": 0.45, "cluster": 0.55},
    "hydro":          {"octaves": 4, "base_freq": 0.0018, "threshold": 0.60, "cluster": 0.45},
    "pentes":         {"octaves": 4, "base_freq": 0.0012, "threshold": 0.50, "cluster": 0.65},
    "orientation":    {"octaves": 3, "base_freq": 0.0009, "threshold": 0.48, "cluster": 0.75},
    "salines":        {"octaves": 5, "base_freq": 0.0025, "threshold": 0.55, "cluster": 0.35},
    "affuts":         {"octaves": 5, "base_freq": 0.0016, "threshold": 0.55, "cluster": 0.45},
    "trajets":        {"octaves": 5, "base_freq": 0.0018, "threshold": 0.45, "cluster": 0.45},
    "altitude":       {"octaves": 3, "base_freq": 0.0005, "threshold": 0.50, "cluster": 0.85},
    "ensoleillement": {"octaves": 3, "base_freq": 0.0007, "threshold": 0.48, "cluster": 0.75},
}

SPECIES_WEIGHTS = {
    "moose": {
        "rut": 0.95, "repos": 0.80, "alimentation": 0.85, "corridors": 0.90,
        "habitats": 0.95, "peuplements": 0.85, "ndvi": 0.80, "hydro": 0.95,
        "pentes": 0.70, "orientation": 0.60, "salines": 0.90, "affuts": 0.75,
        "trajets": 0.70, "altitude": 0.65, "ensoleillement": 0.55,
    },
    "deer": {
        "rut": 0.90, "repos": 0.85, "alimentation": 0.90, "corridors": 0.85,
        "habitats": 0.90, "peuplements": 0.90, "ndvi": 0.85, "hydro": 0.70,
        "pentes": 0.75, "orientation": 0.70, "salines": 0.60, "affuts": 0.90,
        "trajets": 0.80, "altitude": 0.60, "ensoleillement": 0.75,
    },
    "bear": {
        "rut": 0.40, "repos": 0.85, "alimentation": 0.95, "corridors": 0.80,
        "habitats": 0.90, "peuplements": 0.85, "ndvi": 0.90, "hydro": 0.85,
        "pentes": 0.80, "orientation": 0.50, "salines": 0.30, "affuts": 0.60,
        "trajets": 0.65, "altitude": 0.70, "ensoleillement": 0.55,
    },
    "wild_turkey": {
        "rut": 0.75, "repos": 0.70, "alimentation": 0.90, "corridors": 0.60,
        "habitats": 0.85, "peuplements": 0.80, "ndvi": 0.85, "hydro": 0.50,
        "pentes": 0.65, "orientation": 0.60, "salines": 0.20, "affuts": 0.85,
        "trajets": 0.70, "altitude": 0.50, "ensoleillement": 0.90,
    },
    "elk": {
        "rut": 0.90, "repos": 0.80, "alimentation": 0.85, "corridors": 0.90,
        "habitats": 0.85, "peuplements": 0.75, "ndvi": 0.80, "hydro": 0.75,
        "pentes": 0.80, "orientation": 0.65, "salines": 0.70, "affuts": 0.70,
        "trajets": 0.75, "altitude": 0.80, "ensoleillement": 0.60,
    },
}


# =====================================================================
# SIMPLEX-LIKE NOISE (isotrope, sans alignement d'axes)
# =====================================================================

# Skew/unskew constants for 2D simplex
_F2 = 0.5 * (math.sqrt(3.0) - 1.0)
_G2 = (3.0 - math.sqrt(3.0)) / 6.0

# Gradient vectors for simplex noise (12 directions for better isotropy)
_GRAD2 = [
    (1, 0), (-1, 0), (0, 1), (0, -1),
    (1, 1), (-1, 1), (1, -1), (-1, -1),
    (1, 0.5), (-1, 0.5), (0.5, 1), (-0.5, 1),
]


def _perm_table(seed: int) -> np.ndarray:
    """Permutation table seeded deterministically."""
    rng = np.random.RandomState(seed & 0x7FFFFFFF)
    p = np.arange(256, dtype=np.int32)
    rng.shuffle(p)
    return np.concatenate([p, p])


def _simplex2d(x: float, y: float, perm: np.ndarray) -> float:
    """2D simplex noise value in [-1, 1]. Isotrope, pas d'alignement."""
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
    """Bruit fractal multi-octave basé simplex (retourne 0-1)."""
    value = 0.0
    amplitude = 1.0
    frequency = 1.0
    total_amp = 0.0

    for i in range(octaves):
        value += amplitude * _simplex2d(x * frequency, y * frequency, perm)
        total_amp += amplitude
        amplitude *= 0.5
        frequency *= 2.0

    return (value / total_amp + 1.0) * 0.5  # Normalize to 0-1


def _seed_from_coords(lat: float, lng: float, layer: str, species: str) -> int:
    """
    Seed deterministe sur grille fixe 0.02deg (~2.2km).
    R1: Un pan < 2km ne change plus le seed.
    Floor division = pas de frontiere instable (round() a ce probleme).
    """
    lat_bin = math.floor(lat / 0.02) * 0.02
    lng_bin = math.floor(lng / 0.02) * 0.02
    data = f"{lat_bin:.4f}_{lng_bin:.4f}_{layer}_{species}"
    return int(hashlib.md5(data.encode()).hexdigest()[:8], 16)


# =====================================================================
# RASTER GENERATION (V2 — isotrope, en mètres)
# =====================================================================

def generate_layer_raster(
    bounds: Dict[str, float],
    layer_id: str,
    species: str,
    resolution: int = 80
) -> np.ndarray:
    """
    Génère un raster d'intensité pour une couche donnée.
    V2: Échantillonnage en MÈTRES, bruit simplex isotrope.
    """
    params = LAYER_PARAMS.get(layer_id, LAYER_PARAMS["habitats"])
    weight = SPECIES_WEIGHTS.get(species, SPECIES_WEIGHTS["moose"]).get(layer_id, 0.5)
    center_lat = (bounds["north"] + bounds["south"]) / 2

    seed = _seed_from_coords(center_lat, (bounds["east"] + bounds["west"]) / 2, layer_id, species)
    perm = _perm_table(seed)
    perm2 = _perm_table(seed + 7777)

    freq = params["base_freq"]
    octaves = params["octaves"]
    cluster = params["cluster"]

    # Convert bounds to meters from origin for isotropic sampling
    cos_lat = math.cos(math.radians(center_lat))
    y_range_m = (bounds["north"] - bounds["south"]) * METERS_PER_DEG_LAT
    x_range_m = (bounds["east"] - bounds["west"]) * METERS_PER_DEG_LAT * cos_lat

    grid = np.zeros((resolution, resolution), dtype=np.float64)

    for r in range(resolution):
        for c in range(resolution):
            # Sample positions in meters (isotrope)
            y_m = (r / max(1, resolution - 1)) * y_range_m
            x_m = (c / max(1, resolution - 1)) * x_range_m

            # Base noise (simplex — isotrope, organic)
            base = _fractal_simplex(x_m * freq, y_m * freq, octaves, perm)

            # Cluster noise (low frequency — creates natural patches)
            cl = _fractal_simplex(x_m * freq * 0.4, y_m * freq * 0.4, 3, perm2)

            # Smooth gradient cluster (NOT binary — gradual transitions)
            cl_weight = _smooth_cluster(cl, cluster)

            # Layer-specific modulation
            mod = _layer_modulation_v2(x_m, y_m, layer_id, perm, seed)

            grid[r, c] = base * cl_weight * mod * (0.6 + 0.4 * weight)

    grid = np.clip(grid, 0.0, 1.0)
    gmax = grid.max()
    if gmax > 0:
        grid = grid / gmax

    return grid


def _smooth_cluster(value: float, cluster_threshold: float) -> float:
    """
    Masque de cluster GRADUEL (pas binaire).
    Transition douce autour du seuil pour éviter les frontières nettes.
    """
    edge = 1.0 - cluster_threshold
    low = edge - 0.15
    high = edge + 0.05
    if value <= low:
        return 0.0
    elif value >= high:
        return 1.0
    else:
        t = (value - low) / (high - low)
        return t * t * (3 - 2 * t)  # Smoothstep


def _layer_modulation_v2(x_m: float, y_m: float, layer_id: str, perm: np.ndarray, seed: int) -> float:
    """Modulation spécifique par couche, en mètres (isotrope)."""
    if layer_id == "corridors":
        v = _fractal_simplex(x_m * 0.0006, y_m * 0.0006, 4, perm)
        angle = _simplex2d(x_m * 0.0002, y_m * 0.0002, perm) * math.pi
        elongation = abs(math.cos(angle) * x_m * 0.001 + math.sin(angle) * y_m * 0.001)
        mod = _fractal_simplex(elongation, y_m * 0.0004 + x_m * 0.0003, 3, perm)
        return 0.3 + 0.7 * max(v, mod) if max(v, mod) > 0.5 else 0.2

    elif layer_id == "hydro":
        v1 = _simplex2d(x_m * 0.0008, y_m * 0.0012, perm)
        v2 = _simplex2d(x_m * 0.0015 + 100, y_m * 0.0005 + 100, perm)
        drainage = abs(v1 * v2)
        return 0.8 if drainage < 0.15 else 0.2

    elif layer_id == "repos":
        forest = _fractal_simplex(x_m * 0.0005, y_m * 0.0005, 4, perm)
        return 0.7 + 0.3 * forest if forest > 0.5 else 0.3

    elif layer_id == "salines":
        v = _fractal_simplex(x_m * 0.002, y_m * 0.002, 5, perm)
        return 1.0 if v > 0.82 else 0.1

    elif layer_id == "rut":
        edge = _fractal_simplex(x_m * 0.0008, y_m * 0.0008, 5, perm)
        return 0.5 + 0.5 * edge if edge > 0.4 else 0.2

    return 0.5 + 0.5 * _fractal_simplex(x_m * 0.0006, y_m * 0.0006, 3, perm)


def get_supported_layers() -> List[str]:
    return list(LAYER_PARAMS.keys())


def get_supported_species() -> List[str]:
    return list(SPECIES_WEIGHTS.keys())
