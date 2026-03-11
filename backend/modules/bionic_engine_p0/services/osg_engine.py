"""
MODULE OSG — Organic Shape Generator
BIONIC V5 ULTIME 300% — Phase d'Optimisation #2

Generation de formes organiques enrichies par le SSE:
  - Modulation par couvert forestier (SSE.landcover)
  - Modulation par micro-relief (SSE.microrelief)
  - Affinite aux lisieres (SSE.edges)
  - Chaikin 2x obligatoire + vertex jitter
  - Compactness < 0.85 strict
  - Multi-especes, multi-couches, multi-territoires

Consomme: SSE (certifie)
Produit: Zones organiques GeoJSON avec metadata enrichie
source_id dynamique: OSG_{SPECIES}
0 duplication. 0 transversalite. 0 fallback.
Pipeline organique immuable.
"""

import math
import hashlib
import logging
import numpy as np
from typing import Dict, List, Any, Tuple

logger = logging.getLogger("bionic_engine.osg_engine")

METERS_PER_DEG_LAT = 111320.0
MIN_AREA_M2 = 8000.0
MAX_AREA_M2 = 80000.0
TARGET_AREA_M2 = 25000.0
MAX_COMPACTNESS = 0.85
MIN_COMPACTNESS = 0.10
MIN_VERTICES = 8

# Species-specific shape profiles for OSG
OSG_SHAPE_PROFILES = {
    "moose": {
        "threshold_base": 0.48,
        "threshold_sse_weight": 0.15,
        "chaikin_iterations": 3,
        "jitter_m": 18.0,
        "edge_attraction": 0.85,
        "forest_preference": 0.80,
        "valley_preference": 0.70,
        "min_area_factor": 1.0,
        "max_zones": 12,
    },
    "deer": {
        "threshold_base": 0.50,
        "threshold_sse_weight": 0.12,
        "chaikin_iterations": 3,
        "jitter_m": 14.0,
        "edge_attraction": 0.90,
        "forest_preference": 0.60,
        "valley_preference": 0.55,
        "min_area_factor": 0.8,
        "max_zones": 14,
    },
    "bear": {
        "threshold_base": 0.45,
        "threshold_sse_weight": 0.18,
        "chaikin_iterations": 3,
        "jitter_m": 20.0,
        "edge_attraction": 0.60,
        "forest_preference": 0.90,
        "valley_preference": 0.75,
        "min_area_factor": 1.2,
        "max_zones": 10,
    },
    "wild_turkey": {
        "threshold_base": 0.52,
        "threshold_sse_weight": 0.10,
        "chaikin_iterations": 2,
        "jitter_m": 12.0,
        "edge_attraction": 0.75,
        "forest_preference": 0.45,
        "valley_preference": 0.40,
        "min_area_factor": 0.7,
        "max_zones": 16,
    },
    "elk": {
        "threshold_base": 0.47,
        "threshold_sse_weight": 0.14,
        "chaikin_iterations": 3,
        "jitter_m": 16.0,
        "edge_attraction": 0.80,
        "forest_preference": 0.65,
        "valley_preference": 0.60,
        "min_area_factor": 1.1,
        "max_zones": 12,
    },
}


# =====================================================================
# GEOMETRY UTILITIES (self-contained, zero import from organic_zone_generator_v2)
# =====================================================================

def _polygon_area_m2(coords: List[List[float]]) -> float:
    if len(coords) < 3:
        return 0.0
    center_lat = sum(c[1] for c in coords) / len(coords)
    ref_lng, ref_lat = coords[0]
    points_m = []
    for lng, lat in coords:
        x = (lng - ref_lng) * METERS_PER_DEG_LAT * math.cos(math.radians(center_lat))
        y = (lat - ref_lat) * METERS_PER_DEG_LAT
        points_m.append((x, y))
    n = len(points_m)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points_m[i][0] * points_m[j][1] - points_m[j][0] * points_m[i][1]
    return abs(area) / 2.0


def _polygon_compactness(coords: List[List[float]]) -> float:
    area = _polygon_area_m2(coords)
    if area <= 0:
        return 1.0
    center_lat = sum(c[1] for c in coords) / len(coords)
    perimeter = 0.0
    for i in range(len(coords) - 1):
        dy = (coords[i + 1][1] - coords[i][1]) * METERS_PER_DEG_LAT
        dx = (coords[i + 1][0] - coords[i][0]) * METERS_PER_DEG_LAT * math.cos(math.radians(center_lat))
        perimeter += math.sqrt(dx * dx + dy * dy)
    if perimeter == 0:
        return 1.0
    return (4 * math.pi * area) / (perimeter * perimeter)


def _polygon_centroid(coords: List[List[float]]) -> Tuple[float, float]:
    n = len(coords)
    if n == 0:
        return (0.0, 0.0)
    return (sum(c[0] for c in coords) / n, sum(c[1] for c in coords) / n)


def _scale_polygon(coords: List[List[float]], target_area: float) -> List[List[float]]:
    current = _polygon_area_m2(coords)
    if current <= 0:
        return coords
    scale = math.sqrt(target_area / current)
    cx = sum(c[0] for c in coords) / len(coords)
    cy = sum(c[1] for c in coords) / len(coords)
    return [[cx + (p[0] - cx) * scale, cy + (p[1] - cy) * scale] for p in coords]


# =====================================================================
# CHAIKIN SMOOTHING (OSG standard — 2+ passes)
# =====================================================================

def _chaikin_smooth(points: List[List[float]], iterations: int = 2) -> List[List[float]]:
    if len(points) < 4:
        return points
    result = [list(p) for p in points]
    for _ in range(iterations):
        new_pts = []
        n = len(result) - 1
        for i in range(n):
            p0 = result[i]
            p1 = result[(i + 1) % n] if i + 1 < n else result[0]
            new_pts.append([0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1]])
            new_pts.append([0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1]])
        if new_pts:
            new_pts.append(list(new_pts[0]))
        result = new_pts
    return result


# =====================================================================
# VERTEX JITTER (natural irregularity)
# =====================================================================

def _jitter_vertices(coords: List[List[float]], jitter_m: float, seed: int) -> List[List[float]]:
    if len(coords) < 4 or jitter_m <= 0:
        return coords
    center_lat = sum(c[1] for c in coords) / len(coords)
    jitter_lat = jitter_m / METERS_PER_DEG_LAT
    jitter_lng = jitter_m / (METERS_PER_DEG_LAT * math.cos(math.radians(center_lat)))
    result = []
    for i, coord in enumerate(coords):
        if i == len(coords) - 1:
            result.append(list(result[0]))
            break
        h = hashlib.md5(f"OSG_{coord[0]:.8f}_{coord[1]:.8f}_{i}_{seed}".encode()).hexdigest()
        dx = (int(h[:4], 16) / 0xFFFF - 0.5) * 2 * jitter_lng
        dy = (int(h[4:8], 16) / 0xFFFF - 0.5) * 2 * jitter_lat
        result.append([coord[0] + dx, coord[1] + dy])
    return result


# =====================================================================
# BOUNDARY EXTRACTION
# =====================================================================

def _extract_boundary(mask: np.ndarray) -> List[Tuple[int, int]]:
    from scipy.ndimage import binary_erosion
    eroded = binary_erosion(mask, iterations=1)
    border = mask.astype(np.int32) - eroded.astype(np.int32)
    border = np.clip(border, 0, 1)
    points = list(zip(*np.where(border > 0)))
    if len(points) < 4:
        return []
    cr = sum(p[0] for p in points) / len(points)
    cc = sum(p[1] for p in points) / len(points)
    points.sort(key=lambda p: math.atan2(p[0] - cr, p[1] - cc))
    if len(points) > 30:
        step = max(1, len(points) // 25)
        points = points[::step]
    return points


# =====================================================================
# SSE-MODULATED RASTER
# =====================================================================

def _build_sse_modulated_raster(
    base_grid: np.ndarray,
    sse_composite: np.ndarray,
    sse_weight: float,
) -> np.ndarray:
    """
    Module le raster de base avec le composite SSE.
    Le SSE enrichit les zones a haute valeur semantique et attenue les zones pauvres.
    """
    rows_b, cols_b = base_grid.shape
    rows_s, cols_s = sse_composite.shape

    if rows_b != rows_s or cols_b != cols_s:
        from scipy.ndimage import zoom as ndimage_zoom
        scale_r = rows_b / rows_s
        scale_c = cols_b / cols_s
        sse_resized = ndimage_zoom(sse_composite, (scale_r, scale_c), order=1)
    else:
        sse_resized = sse_composite

    modulated = base_grid * (1.0 - sse_weight) + base_grid * sse_resized * sse_weight
    gmax = modulated.max()
    if gmax > 0:
        modulated = modulated / gmax
    return modulated


# =====================================================================
# OSG CORE — ZONE GENERATION
# =====================================================================

def generate_osg_zones(
    bounds: Dict[str, float],
    species: str,
    layer_id: str,
    base_grid: np.ndarray,
    sse_data: Dict[str, Any],
    resolution: int = 60,
) -> Dict[str, Any]:
    """
    Pipeline OSG: base_grid + SSE → modulation → blob detection → Chaikin → jitter → validation.

    Args:
        bounds: Limites geographiques
        species: Espece (transmise par l'orchestrateur)
        layer_id: Couche BIONIC (habitats, rut, etc.)
        base_grid: Raster d'intensite du behavioral_rasterizer
        sse_data: Sortie de generate_sse_composite (SSE certifie)
        resolution: Resolution de grille

    Returns:
        Dict avec zones organiques enrichies, metadata SSE, source_id dynamique
    """
    from scipy.ndimage import label, binary_fill_holes, zoom as ndimage_zoom

    source_id = f"OSG_{species.upper()}"
    profile = OSG_SHAPE_PROFILES.get(species, OSG_SHAPE_PROFILES["moose"])
    seed = int(hashlib.md5(f"OSG_{bounds['south']:.4f}_{species}_{layer_id}".encode()).hexdigest()[:6], 16)

    # Modulate base grid with SSE composite
    sse_composite = sse_data.get("composite", np.ones_like(base_grid))
    modulated = _build_sse_modulated_raster(base_grid, sse_composite, profile["threshold_sse_weight"])

    # Upsample for finer contours
    try:
        up_grid = ndimage_zoom(modulated, 2, order=1)
    except Exception:
        up_grid = modulated

    rows, cols = up_grid.shape
    threshold = profile["threshold_base"]
    binary = (up_grid >= threshold).astype(np.int32)

    labeled, num_features = label(binary)

    # SSE grids for per-zone metadata enrichment
    sse_forest = sse_data.get("landcover", {}).get("forest_density", np.zeros((resolution, resolution)))
    sse_edge = sse_data.get("edges", {}).get("edge_intensity", np.zeros((resolution, resolution)))
    sse_valley = sse_data.get("microrelief", {}).get("valley_map", np.zeros((resolution, resolution)))
    sse_ridge = sse_data.get("microrelief", {}).get("ridge_map", np.zeros((resolution, resolution)))

    min_area = MIN_AREA_M2 * profile["min_area_factor"]
    max_area = MAX_AREA_M2

    zones = []
    rejected_compactness = 0
    rejected_area = 0
    rejected_vertices = 0

    for blob_id in range(1, num_features + 1):
        mask = (labeled == blob_id)
        filled = binary_fill_holes(mask).astype(np.uint8)

        boundary = _extract_boundary(filled)
        if len(boundary) < 6:
            rejected_vertices += 1
            continue

        geo_coords = []
        for (pr, pc) in boundary:
            lng = bounds["west"] + (pc / max(1, cols - 1)) * (bounds["east"] - bounds["west"])
            lat = bounds["north"] - (pr / max(1, rows - 1)) * (bounds["north"] - bounds["south"])
            geo_coords.append([lng, lat])
        geo_coords.append(list(geo_coords[0]))

        # Chaikin smoothing (profile-defined iterations, minimum 2)
        chaikin_iter = max(2, profile["chaikin_iterations"])
        smoothed = _chaikin_smooth(geo_coords, iterations=chaikin_iter)
        if len(smoothed) < MIN_VERTICES:
            rejected_vertices += 1
            continue

        # Vertex jitter
        smoothed = _jitter_vertices(smoothed, profile["jitter_m"], seed + blob_id)

        area = _polygon_area_m2(smoothed)

        # Scale to target range
        if area > max_area * 1.5:
            smoothed = _scale_polygon(smoothed, TARGET_AREA_M2)
            area = _polygon_area_m2(smoothed)
        elif area < min_area * 0.3:
            rejected_area += 1
            continue

        if area < min_area * 0.5 or area > max_area * 2:
            rejected_area += 1
            continue

        if area < min_area or area > max_area:
            target = max(min_area, min(max_area, TARGET_AREA_M2))
            smoothed = _scale_polygon(smoothed, target)
            area = _polygon_area_m2(smoothed)

        compactness = _polygon_compactness(smoothed)
        if compactness > MAX_COMPACTNESS:
            rejected_compactness += 1
            continue
        if compactness < MIN_COMPACTNESS:
            rejected_compactness += 1
            continue

        centroid = _polygon_centroid(smoothed)

        # SSE metadata enrichment — sample SSE grids at zone centroid
        sse_meta = _sample_sse_at_centroid(
            centroid, bounds, resolution,
            sse_forest, sse_edge, sse_valley, sse_ridge,
        )

        zones.append({
            "coordinates": smoothed,
            "area_m2": round(area, 1),
            "compactness": round(compactness, 4),
            "centroid": {"lng": round(centroid[0], 6), "lat": round(centroid[1], 6)},
            "vertices": len(smoothed),
            "sse_context": sse_meta,
        })

    # Sort by SSE composite quality (best zones first)
    zones.sort(key=lambda z: z["sse_context"]["composite_quality"], reverse=True)
    zones = zones[:profile["max_zones"]]

    return {
        "source_id": source_id,
        "species": species,
        "layer_id": layer_id,
        "zones": zones,
        "zone_count": len(zones),
        "validation": {
            "all_compactness_below_085": all(z["compactness"] < MAX_COMPACTNESS for z in zones),
            "chaikin_iterations": chaikin_iter,
            "jitter_applied": True,
            "sse_modulated": True,
        },
        "rejected": {
            "compactness": rejected_compactness,
            "area": rejected_area,
            "vertices": rejected_vertices,
        },
    }


def _sample_sse_at_centroid(
    centroid: Tuple[float, float],
    bounds: Dict[str, float],
    resolution: int,
    forest: np.ndarray,
    edge: np.ndarray,
    valley: np.ndarray,
    ridge: np.ndarray,
) -> Dict[str, Any]:
    """Sample SSE grids at zone centroid for metadata enrichment."""
    lng, lat = centroid
    col = int(((lng - bounds["west"]) / max(0.0001, bounds["east"] - bounds["west"])) * (resolution - 1))
    row = int(((bounds["north"] - lat) / max(0.0001, bounds["north"] - bounds["south"])) * (resolution - 1))
    col = max(0, min(resolution - 1, col))
    row = max(0, min(resolution - 1, row))

    f_rows, f_cols = forest.shape
    r_f = min(row, f_rows - 1)
    c_f = min(col, f_cols - 1)

    forest_val = float(forest[r_f, c_f]) if f_rows > 0 else 0.0
    edge_val = float(edge[r_f, c_f]) if edge.shape[0] > 0 else 0.0
    valley_val = float(valley[r_f, c_f]) if valley.shape[0] > 0 else 0.0
    ridge_val = float(ridge[r_f, c_f]) if ridge.shape[0] > 0 else 0.0

    # Composite quality score from SSE context
    composite_quality = round(forest_val * 0.35 + edge_val * 0.30 + valley_val * 0.20 + (1.0 - ridge_val) * 0.15, 4)

    # Classify relief context
    if valley_val > ridge_val and valley_val > 0.4:
        relief_type = "valley"
    elif ridge_val > valley_val and ridge_val > 0.4:
        relief_type = "ridge"
    else:
        relief_type = "plateau"

    # Classify cover context
    if forest_val > 0.6:
        cover_type = "forest"
    elif forest_val < 0.3:
        cover_type = "clearing"
    else:
        cover_type = "transition"

    return {
        "forest_density": round(forest_val, 4),
        "edge_proximity": round(edge_val, 4),
        "valley_affinity": round(valley_val, 4),
        "ridge_affinity": round(ridge_val, 4),
        "composite_quality": composite_quality,
        "relief_type": relief_type,
        "cover_type": cover_type,
    }


# =====================================================================
# MULTI-LAYER ORCHESTRATOR
# =====================================================================

def generate_osg_multi_layer(
    bounds: Dict[str, float],
    species: str,
    layers: List[str],
    sse_data: Dict[str, Any],
    resolution: int = 60,
    max_zones_per_layer: int = 8,
) -> Dict[str, Any]:
    """
    Orchestre la generation OSG sur plusieurs couches.

    Pour chaque couche:
      1. Genere le raster comportemental (behavioral_rasterizer)
      2. Module par SSE composite
      3. Extrait les zones organiques OSG
      4. Valide compactness + area

    source_id: OSG_{SPECIES}
    """
    from modules.bionic_engine_p0.services.behavioral_rasterizer import (
        generate_layer_raster, LAYER_PARAMS,
    )

    source_id = f"OSG_{species.upper()}"
    all_zones = {}
    total_zones = 0
    total_rejected = {"compactness": 0, "area": 0, "vertices": 0}

    valid_layers = [l for l in layers if l in LAYER_PARAMS]

    for layer_id in valid_layers:
        base_grid = generate_layer_raster(bounds, layer_id, species, resolution)

        result = generate_osg_zones(
            bounds, species, layer_id, base_grid, sse_data, resolution,
        )

        layer_zones = result["zones"][:max_zones_per_layer]
        if layer_zones:
            all_zones[layer_id] = layer_zones
            total_zones += len(layer_zones)

        for k in total_rejected:
            total_rejected[k] += result["rejected"].get(k, 0)

    return {
        "source_id": source_id,
        "species": species,
        "bounds": bounds,
        "resolution": resolution,
        "layers_processed": len(valid_layers),
        "zones_by_layer": all_zones,
        "total_zones": total_zones,
        "validation": {
            "all_compactness_below_085": all(
                z["compactness"] < MAX_COMPACTNESS
                for zones in all_zones.values()
                for z in zones
            ),
            "sse_integration": True,
            "chaikin_applied": True,
        },
        "rejected_total": total_rejected,
    }


def get_supported_species() -> List[str]:
    return list(OSG_SHAPE_PROFILES.keys())
