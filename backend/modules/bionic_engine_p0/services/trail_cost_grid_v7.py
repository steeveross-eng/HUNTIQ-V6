"""
BIONIC V7 — Trail Cost Grid V7
Rasterisation des exclusions OSM en grille de couts pour pathfinding A*.

Construit une grille 2D numpy ou chaque cellule a un cout de traversee:
  - IMPASSABLE (inf): plans d'eau, zones urbaines denses, routes majeures
  - TRES FAVORABLE (0.2-0.5): fonds de vallee, lisieres, ruisseaux
  - FAVORABLE (0.5-1.0): foret moderee, pentes douces
  - DEFAVORABLE (1.0-5.0): pentes raides, proximite routes
  - QUASI-IMPASSABLE (10+): infrastructure lourde

Differentiation male/femelle via sex_modifier.

100% independant. Consomme par corridor_v7.
"""

import math
import logging
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timezone

from .species_behavior_v7 import get_sex_params

logger = logging.getLogger("bionic_engine.trail_cost_grid_v7")

METERS_PER_DEG_LAT = 111320.0
IMPASSABLE = 999.0


def _m_to_cells(meters: float, cell_size_m: float) -> int:
    """Convert meters to cell count."""
    return max(1, int(meters / cell_size_m + 0.5))


def _latlon_to_cell(lat: float, lng: float, bounds: dict, rows: int, cols: int) -> Tuple[int, int]:
    """Convert lat/lng to grid cell (row, col)."""
    r = int((bounds["north"] - lat) / max(1e-9, bounds["north"] - bounds["south"]) * rows)
    c = int((lng - bounds["west"]) / max(1e-9, bounds["east"] - bounds["west"]) * cols)
    return max(0, min(rows - 1, r)), max(0, min(cols - 1, c))


def _rasterize_polygon(grid: np.ndarray, coords: list, bounds: dict, value: float, buffer_cells: int = 0):
    """Rasterise un polygone dans la grille (scanline simplifie)."""
    rows, cols = grid.shape
    if len(coords) < 3:
        return

    pix_coords = []
    for c in coords:
        r, cl = _latlon_to_cell(c[1], c[0], bounds, rows, cols)
        pix_coords.append((r, cl))

    min_r = max(0, min(p[0] for p in pix_coords) - buffer_cells)
    max_r = min(rows - 1, max(p[0] for p in pix_coords) + buffer_cells)
    min_c = max(0, min(p[1] for p in pix_coords) - buffer_cells)
    max_c = min(cols - 1, max(p[1] for p in pix_coords) + buffer_cells)

    for r in range(min_r, max_r + 1):
        for c in range(min_c, max_c + 1):
            grid[r, c] = max(grid[r, c], value)


def _rasterize_line(grid: np.ndarray, coords: list, bounds: dict, value: float, width_cells: int = 1):
    """Rasterise une ligne dans la grille (Bresenham + buffer)."""
    rows, cols = grid.shape
    if len(coords) < 2:
        return

    for i in range(len(coords) - 1):
        r0, c0 = _latlon_to_cell(coords[i][1], coords[i][0], bounds, rows, cols)
        r1, c1 = _latlon_to_cell(coords[i + 1][1], coords[i + 1][0], bounds, rows, cols)

        dr = abs(r1 - r0)
        dc = abs(c1 - c0)
        sr = 1 if r0 < r1 else -1
        sc = 1 if c0 < c1 else -1
        err = dr - dc
        r, c = r0, c0

        steps = max(dr, dc) + 1
        for _ in range(steps + 1):
            for br in range(-width_cells, width_cells + 1):
                for bc in range(-width_cells, width_cells + 1):
                    rr, cc = r + br, c + bc
                    if 0 <= rr < rows and 0 <= cc < cols:
                        grid[rr, cc] = max(grid[rr, cc], value)

            if r == r1 and c == c1:
                break
            e2 = 2 * err
            if e2 > -dc:
                err -= dc
                r += sr
            if e2 < dr:
                err += dr
                c += sc


def _apply_proximity_gradient(grid: np.ndarray, base_value: float, decay_cells: int):
    """Ajoute un gradient de cout autour des cellules a haute valeur."""
    if decay_cells <= 0:
        return

    rows, cols = grid.shape
    mask = grid >= base_value * 0.8
    if not np.any(mask):
        return

    from scipy.ndimage import distance_transform_edt
    dist = distance_transform_edt(~mask)
    gradient = np.where(dist < decay_cells, base_value * 0.3 * (1.0 - dist / decay_cells), 0)
    np.maximum(grid, gradient, out=grid)


def build_cost_grid(
    bounds: Dict[str, float],
    exclusions: List[Dict],
    species: str,
    sex: str,
    grid_size: int = 50,
    dem_data: "Dict | None" = None,
    month: int = None,
) -> Tuple[np.ndarray, Dict]:
    """
    Construit la grille de couts ecologiques pour le pathfinding A*.
    R3: month pinne pour determinisme saisonnier.
    """
    rows, cols = grid_size, grid_size
    grid = np.ones((rows, cols), dtype=np.float64) * 0.5

    lat_span = bounds["north"] - bounds["south"]
    lng_span = bounds["east"] - bounds["west"]
    lat_center = (bounds["north"] + bounds["south"]) / 2
    cos_lat = math.cos(math.radians(lat_center))

    cell_h_m = (lat_span * METERS_PER_DEG_LAT) / rows
    cell_w_m = (lng_span * METERS_PER_DEG_LAT * cos_lat) / cols
    cell_size_m = (cell_h_m + cell_w_m) / 2

    params = get_sex_params(species, sex)
    min_road_dist = params.get("min_road_distance_m", 200)
    min_urban_dist = params.get("min_urban_distance_m", 500)
    cover_pref = params.get("cover_preference", 0.5)
    slope_tol = params.get("slope_tolerance", 0.6)

    road_buffer_cells = _m_to_cells(min_road_dist, cell_size_m)
    urban_buffer_cells = _m_to_cells(min_urban_dist, cell_size_m)

    # =====================================================================
    # PHASE 1: Rasteriser les exclusions comme obstacles
    # =====================================================================

    water_grid = np.zeros((rows, cols), dtype=np.float64)
    road_grid = np.zeros((rows, cols), dtype=np.float64)
    urban_grid = np.zeros((rows, cols), dtype=np.float64)
    infra_grid = np.zeros((rows, cols), dtype=np.float64)
    stream_grid = np.zeros((rows, cols), dtype=np.float64)

    ROAD_COSTS = {
        "motorway": IMPASSABLE, "trunk": IMPASSABLE,
        "primary": 20.0, "secondary": 8.0,
        "tertiary": 4.0, "residential": 3.0,
        "service": 2.0, "unclassified": 2.0,
        "track": 0.3, "footway": 0.2, "path": 0.2, "cycleway": 0.2,
    }

    for ex in exclusions:
        if ex.get("filtered_out"):
            continue
        ex_type = ex.get("type", "")
        sub_type = ex.get("sub_type", "")
        geom_type = ex.get("geometry_type", "polygon")
        coords = ex.get("coordinates", [])
        if not coords:
            continue

        if ex_type == "water":
            if sub_type in ("stream", "ditch", "drain"):
                if geom_type == "line":
                    _rasterize_line(stream_grid, coords, bounds, 1.0, 0)
                continue
            if sub_type == "wetland":
                continue
            if sub_type == "micro_water":
                continue
            if geom_type == "polygon":
                _rasterize_polygon(water_grid, coords, bounds, IMPASSABLE, 1)
            elif geom_type == "line":
                _rasterize_line(water_grid, coords, bounds, IMPASSABLE, 1)

        elif ex_type == "roads":
            cost = ROAD_COSTS.get(sub_type, 2.0)
            width = max(1, _m_to_cells(min_road_dist * 0.3, cell_size_m)) if cost >= 8.0 else 1
            if geom_type == "line":
                _rasterize_line(road_grid, coords, bounds, cost, width)
            elif geom_type == "polygon":
                _rasterize_polygon(road_grid, coords, bounds, cost, 0)

        elif ex_type == "urban":
            _rasterize_polygon(urban_grid, coords, bounds, IMPASSABLE, 0)

        elif ex_type == "infrastructure":
            if geom_type == "polygon":
                _rasterize_polygon(infra_grid, coords, bounds, 3.0, 0)
            elif geom_type == "line":
                _rasterize_line(infra_grid, coords, bounds, 2.0, 1)

    # =====================================================================
    # PHASE 2: Construire la grille composite
    # =====================================================================

    # Obstacles impassables
    grid = np.maximum(grid, water_grid)
    grid = np.maximum(grid, road_grid)
    grid = np.maximum(grid, urban_grid)
    grid = np.maximum(grid, infra_grid)

    # =====================================================================
    # PHASE 3: Gradients de proximite (attraction/repulsion)
    # =====================================================================

    try:
        _apply_proximity_gradient(urban_grid, IMPASSABLE * 0.8, urban_buffer_cells)
        _apply_proximity_gradient(road_grid, 8.0, road_buffer_cells)
        # Gradient ecologique: penalite progressive pres des zones humaines
        # Plafonner les gradients pour eviter que les couts dominent la grille
        np.maximum(grid, np.clip(urban_grid * 0.012, 0, 10), out=grid)
        np.maximum(grid, np.clip(road_grid * 0.08, 0, 4), out=grid)
    except ImportError:
        pass

    # =====================================================================
    # PHASE 4: Modele ecologique terrain-aware
    # =====================================================================
    from scipy.ndimage import distance_transform_edt, uniform_filter

    has_dem = False
    dem_slope_grid = None
    dem_elev_grid = None
    dem_aspect_grid = None

    # --- 4a. Extraction des couches DEM (si disponibles) ---
    if dem_data and dem_data.get("status") == "success":
        try:
            from scipy.ndimage import zoom as _zoom
            fields = dem_data.get("fields", {})

            def _resample(arr):
                if arr is None:
                    return None
                if arr.shape[0] == rows and arr.shape[1] == cols:
                    return arr[:rows, :cols]
                zy = rows / arr.shape[0]
                zx = cols / arr.shape[1]
                return _zoom(arr, (zy, zx), order=1)[:rows, :cols]

            dem_slope_grid = _resample(fields.get("slope"))
            dem_elev_grid = _resample(fields.get("elevation"))
            dem_aspect_grid = _resample(fields.get("aspect"))
            has_dem = dem_slope_grid is not None
        except Exception as e:
            logger.warning(f"[CostGrid] DEM extraction failed: {e}")

    # --- 4b. Pente DEM (slope cost) ---
    if has_dem and dem_slope_grid is not None:
        slope_cost = np.zeros((rows, cols), dtype=np.float64)
        slope_cost = np.where(dem_slope_grid > 8, (dem_slope_grid - 8) * 0.12, slope_cost)
        slope_cost = np.where(dem_slope_grid > 15, slope_cost + (dem_slope_grid - 15) * 0.18, slope_cost)
        slope_cost = np.where(dem_slope_grid > 25, slope_cost + (dem_slope_grid - 25) * 0.45, slope_cost)
        slope_cost = np.where(dem_slope_grid > 40, IMPASSABLE * 0.6, slope_cost)
        slope_cost = slope_cost * (1.0 / max(0.1, slope_tol))
        np.maximum(grid, slope_cost, out=grid)
        logger.info(f"[CostGrid] DEM slope: mean={np.mean(dem_slope_grid):.1f}deg")

    # --- 4c. Detection vallee/crete via TPI (Topographic Position Index) ---
    tpi_bonus = np.zeros((rows, cols), dtype=np.float64)
    tpi_penalty = np.zeros((rows, cols), dtype=np.float64)
    if has_dem and dem_elev_grid is not None:
        neighborhood = min(7, max(3, rows // 8))
        elev_smooth = uniform_filter(dem_elev_grid, size=neighborhood)
        tpi = dem_elev_grid - elev_smooth
        # Vallee (TPI negatif) = fond de ravin, couloir naturel -> bonus fort
        valley_mask = tpi < -2.0
        tpi_bonus = np.where(valley_mask, np.clip(-tpi / 15.0, 0, 0.45), 0)
        # Crete (TPI positif) = expose, visible -> penalite
        ridge_mask = tpi > 3.0
        tpi_penalty = np.where(ridge_mask, np.clip(tpi / 10.0, 0, 2.0), 0)
        logger.info(
            f"[CostGrid] TPI: valleys={int(np.sum(valley_mask))} cells, "
            f"ridges={int(np.sum(ridge_mask))} cells"
        )

    # --- 4d. Aspect (orientation) - versants nord = couvert plus dense ---
    aspect_bonus = np.zeros((rows, cols), dtype=np.float64)
    if has_dem and dem_aspect_grid is not None:
        # Hemisphere nord: versants nord (315-45 deg) = vegetation plus dense
        north_facing = ((dem_aspect_grid > 315) | (dem_aspect_grid < 45))
        aspect_bonus = np.where(north_facing, 0.08, 0)

    # --- 4e. Carte de couvert forestier (amelioree) ---
    # Le couvert = zones sans obstacles humains (proxy = inverse de urban+roads+infra)
    human_pressure = np.clip(urban_grid / max(1, IMPASSABLE) + road_grid / 15.0 + infra_grid / max(1, IMPASSABLE), 0, 1)
    forest_cover = 1.0 - human_pressure
    # Lissage pour des transitions realistes
    forest_cover_smooth = uniform_filter(forest_cover, size=3)

    # --- 4f. Detection des LISIERES (gradient du couvert forestier) ---
    # Lisiere = transition forte entre zone couverte et zone ouverte
    # Calculer le gradient (approximation Sobel simplifiee)
    grad_y = np.abs(np.diff(forest_cover_smooth, axis=0, prepend=forest_cover_smooth[:1, :]))
    grad_x = np.abs(np.diff(forest_cover_smooth, axis=1, prepend=forest_cover_smooth[:, :1]))
    edge_gradient = np.sqrt(grad_y**2 + grad_x**2)
    # Normaliser et creer le bonus lisiere
    edge_max = np.percentile(edge_gradient, 95) if np.any(edge_gradient > 0) else 1.0
    edge_gradient_norm = np.clip(edge_gradient / max(0.01, edge_max), 0, 1)
    # Bonus lisiere: fort la ou le gradient est eleve ET le couvert est intermediaire
    lisiere_mask = (edge_gradient_norm > 0.15) & (forest_cover_smooth > 0.2) & (forest_cover_smooth < 0.85)
    lisiere_bonus = np.where(lisiere_mask, 0.35 + edge_gradient_norm * 0.25, 0)
    # Dilater les lisieres pour creer un corridor de 2-3 cellules de large
    from scipy.ndimage import maximum_filter
    lisiere_bonus = maximum_filter(lisiere_bonus, size=3) * 0.85

    # --- 4g. Corridor de proximite eau (ruisseaux + plans d'eau) ---
    water_corridor_bonus = np.zeros((rows, cols), dtype=np.float64)
    combined_water = np.maximum(stream_grid, (water_grid > 0).astype(np.float64))
    if np.any(combined_water > 0):
        water_mask = combined_water > 0
        dist_from_water = distance_transform_edt(~water_mask) * cell_size_m
        # Bande optimale: 30-250m de l'eau (l'animal reste cache pres de l'eau mais pas dedans)
        water_params = get_sex_params(species, sex)
        optimal_near = 30
        optimal_far = water_params.get("optimal_water_distance_m", 250)
        # Bonus fort dans la bande optimale, decroissant au-dela
        in_band = (dist_from_water >= optimal_near) & (dist_from_water <= optimal_far)
        beyond_band = (dist_from_water > optimal_far) & (dist_from_water <= optimal_far * 2)
        water_corridor_bonus = np.where(
            in_band,
            0.40 * (1.0 - (dist_from_water - optimal_near) / max(1, optimal_far - optimal_near)),
            0
        )
        water_corridor_bonus = np.where(
            beyond_band,
            0.12 * (1.0 - (dist_from_water - optimal_far) / max(1, optimal_far)),
            water_corridor_bonus,
        )
        # Bonus supplementaire pres des ruisseaux (vs lacs)
        stream_dist = distance_transform_edt(~(stream_grid > 0)) * cell_size_m if np.any(stream_grid > 0) else dist_from_water
        stream_corridor = np.where(
            (stream_dist >= 20) & (stream_dist <= 150),
            0.15,
            0,
        )
        water_corridor_bonus = np.maximum(water_corridor_bonus, stream_corridor)

    # --- 4h. Couvert forestier dense: bonus couvert ---
    forest_dense_bonus = np.where(forest_cover_smooth > 0.7, forest_cover_smooth * cover_pref * 0.25, 0)
    # Couvert moyen: bonus modere
    forest_medium_bonus = np.where(
        (forest_cover_smooth > 0.35) & (forest_cover_smooth <= 0.7),
        forest_cover_smooth * cover_pref * 0.12,
        0,
    )

    # --- 4i. Zone ouverte: penalite proportionnelle a l'exposition ---
    open_penalty_base = np.where(forest_cover_smooth < 0.25, (0.25 - forest_cover_smooth) * 3.0, 0)

    # =====================================================================
    # PHASE 5: Synthese ecologique + modificateurs par sexe
    # =====================================================================

    # Appliquer TOUS les bonus (reduire le cout dans les zones attractrices)
    total_bonus = (
        lisiere_bonus +
        water_corridor_bonus +
        forest_dense_bonus +
        forest_medium_bonus +
        tpi_bonus +
        aspect_bonus
    )
    grid = grid - total_bonus

    # Appliquer les penalites
    grid = grid + tpi_penalty + open_penalty_base

    # --- Modificateurs par sexe ---
    if sex == "female":
        # Femelles: forte aversion aux zones ouvertes, preference couvert
        female_open_penalty = np.where(forest_cover_smooth < 0.30, (0.30 - forest_cover_smooth) * 2.5, 0)
        grid = grid + female_open_penalty
        # Bonus supplementaire en foret dense pour les femelles
        female_cover_bonus = np.where(forest_cover_smooth > 0.65, 0.15, 0)
        grid = grid - female_cover_bonus
        # Penalite cretes plus forte
        grid = grid + tpi_penalty * 0.5
    elif sex == "male":
        # Males: tolerent plus l'exposition, surtout en rut (automne)
        # R3: month pinne pour determinisme
        if month is None:
            month = datetime.now(timezone.utc).month
        male_exposure_reduce = np.where(forest_cover_smooth < 0.30, 0.3, 0)
        grid = grid - male_exposure_reduce * 0.15
        # En rut (sept-nov): males traversent les cretes
        if month in (9, 10, 11):
            grid = grid - tpi_penalty * 0.3  # Reduire la penalite crete en rut

    # Clamp final: minimum 0.1 (jamais 0 pour A*), maximum IMPASSABLE
    grid = np.clip(grid, 0.1, IMPASSABLE)

    # Diagnostic logging
    traversable = grid[grid < IMPASSABLE * 0.9]
    if len(traversable) > 0:
        logger.info(
            f"[CostGrid] {sex}: traversable={len(traversable)}/{rows*cols} "
            f"avg_cost={np.mean(traversable):.2f} "
            f"median={np.median(traversable):.2f} "
            f"p10={np.percentile(traversable, 10):.2f} "
            f"p90={np.percentile(traversable, 90):.2f} "
            f"lisiere={int(np.sum(lisiere_bonus > 0.1))} "
            f"water_corr={int(np.sum(water_corridor_bonus > 0.1))} "
            f"dem={has_dem}"
        )

    metadata = {
        "grid_size": grid_size,
        "cell_size_m": round(cell_size_m, 1),
        "species": species,
        "sex": sex,
        "bounds": bounds,
        "impassable_cells": int(np.sum(grid >= IMPASSABLE * 0.9)),
        "favorable_cells": int(np.sum(grid < 0.5)),
        "lisiere_cells": int(np.sum(lisiere_bonus > 0.1)),
        "water_corridor_cells": int(np.sum(water_corridor_bonus > 0.1)),
        "valley_cells": int(np.sum(tpi_bonus > 0.05)) if has_dem else 0,
        "ridge_cells": int(np.sum(tpi_penalty > 0.5)) if has_dem else 0,
        "total_cells": rows * cols,
        "dem_slope_applied": has_dem,
        "ecological_model": "v7.1",
    }

    return grid, metadata
