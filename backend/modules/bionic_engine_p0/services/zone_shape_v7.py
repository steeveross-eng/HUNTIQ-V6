"""
BIONIC V7 — Zone Shape V7
Morphologie terrain-aware des zones via Shapely.

Operations:
  - Lissage adaptatif (plus de lissage en plat, moins en accidente)
  - Snapping aux berges (plans d'eau)
  - Snapping aux lisieres (transition foret/ouvert)
  - Fusion de zones adjacentes du meme type
  - Validation topologique

Consomme: exclusion_geometry_v6, terrain_signals_v7
Consomme par: pipeline_v7
"""

import math
import logging
from typing import Dict, List, Optional

from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

logger = logging.getLogger("bionic_engine.zone_shape_v7")

METERS_PER_DEG_LAT = 111320.0


def _m_to_deg(meters: float, lat: float) -> float:
    """Convert meters to degrees (avg lat/lng)."""
    cos = math.cos(math.radians(lat))
    return meters / (METERS_PER_DEG_LAT * (1.0 + cos) / 2.0)


def smooth_zone_adaptive(
    coords: list,
    iterations: int = 4,
    terrain_roughness: float = 0.5,
) -> list:
    """
    Lissage Chaikin adaptatif.
    Plus de lissage si terrain plat (roughness bas),
    moins si terrain accidente (preserve les features).
    """
    effective_iterations = max(1, int(iterations * (1.0 - terrain_roughness * 0.5)))

    points = [(c[0], c[1]) for c in coords]
    if points[0] != points[-1]:
        points.append(points[0])

    for _ in range(effective_iterations):
        if len(points) < 4:
            break
        new_points = []
        for i in range(len(points) - 1):
            p0 = points[i]
            p1 = points[i + 1]
            q = (0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1])
            r = (0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1])
            new_points.append(q)
            new_points.append(r)
        if new_points:
            new_points.append(new_points[0])
        points = new_points

    return [[p[0], p[1]] for p in points]


def snap_to_shorelines(
    zone_poly: Polygon,
    water_exclusions: List[Dict],
    snap_distance_m: float = 30.0,
    lat_center: float = 46.0,
) -> Polygon:
    """
    Ajuste les bords de zone pour epouser les berges proches.
    Les points de zone proches d'une berge sont projetes sur celle-ci.
    """
    snap_deg = _m_to_deg(snap_distance_m, lat_center)

    water_polys = []
    for ex in water_exclusions:
        if ex.get("type") != "water" or ex.get("filtered_out"):
            continue
        if ex.get("geometry_type") != "polygon":
            continue
        sub = ex.get("sub_type", "")
        if sub in ("stream", "ditch", "drain", "micro_water"):
            continue
        coords = ex.get("coordinates", [])
        if len(coords) < 3:
            continue
        try:
            ring = [(c[0], c[1]) for c in coords]
            if ring[0] != ring[-1]:
                ring.append(ring[0])
            wp = Polygon(ring)
            if wp.is_valid and not wp.is_empty:
                water_polys.append(wp)
        except Exception:
            continue

    if not water_polys:
        return zone_poly

    water_union = unary_union(water_polys)

    exterior = list(zone_poly.exterior.coords)
    snapped = []
    for pt in exterior:
        from shapely.geometry import Point
        p = Point(pt)
        dist = p.distance(water_union.boundary) if hasattr(water_union, 'boundary') else float('inf')
        if dist < snap_deg:
            nearest = water_union.boundary.interpolate(water_union.boundary.project(p))
            snapped.append((nearest.x, nearest.y))
        else:
            snapped.append(pt)

    try:
        result = Polygon(snapped)
        if result.is_valid and not result.is_empty:
            return result
        return result.buffer(0)
    except Exception:
        return zone_poly


def merge_adjacent_zones(
    zones: List[Dict],
    merge_distance_m: float = 50.0,
    lat_center: float = 46.0,
) -> List[Dict]:
    """
    Fusionne les zones adjacentes du meme type.
    Deux zones du meme layer a moins de merge_distance sont fusionnees.
    """
    if len(zones) < 2:
        return zones

    merge_deg = _m_to_deg(merge_distance_m, lat_center)
    merged = list(zones)
    changed = True

    while changed:
        changed = False
        new_merged = []
        skip = set()

        for i in range(len(merged)):
            if i in skip:
                continue

            best_j = None
            best_dist = float("inf")

            for j in range(i + 1, len(merged)):
                if j in skip:
                    continue

                # Same type check
                t_i = merged[i].get("v7", {}).get("zone_type", "")
                t_j = merged[j].get("v7", {}).get("zone_type", "")
                if t_i != t_j:
                    continue

                # Distance check
                try:
                    poly_i = Polygon([(c[0], c[1]) for c in merged[i]["coordinates"]])
                    poly_j = Polygon([(c[0], c[1]) for c in merged[j]["coordinates"]])
                    dist = poly_i.distance(poly_j)
                except Exception:
                    continue

                if dist < merge_deg and dist < best_dist:
                    best_j = j
                    best_dist = dist

            if best_j is not None:
                try:
                    poly_i = Polygon([(c[0], c[1]) for c in merged[i]["coordinates"]])
                    poly_j = Polygon([(c[0], c[1]) for c in merged[best_j]["coordinates"]])
                    union = unary_union([
                        poly_i.buffer(merge_deg / 2),
                        poly_j.buffer(merge_deg / 2),
                    ]).buffer(-merge_deg / 2)

                    if union.is_empty:
                        new_merged.append(merged[i])
                        continue

                    if union.geom_type == "MultiPolygon":
                        union = max(union.geoms, key=lambda g: g.area)

                    new_coords = [[c[0], c[1]] for c in union.exterior.coords]
                    area_i = merged[i].get("area_m2", 0)
                    area_j = merged[best_j].get("area_m2", 0)

                    new_zone = {
                        **merged[i],
                        "coordinates": new_coords,
                        "area_m2": area_i + area_j,
                        "centroid": {
                            "lat": union.centroid.y,
                            "lng": union.centroid.x,
                        },
                        "merged": True,
                    }
                    if "v7" in merged[i]:
                        new_zone["v7"] = merged[i]["v7"]

                    new_merged.append(new_zone)
                    skip.add(best_j)
                    changed = True
                except Exception:
                    new_merged.append(merged[i])
            else:
                new_merged.append(merged[i])

        for j in range(len(merged)):
            if j in skip and j not in [x for x in range(len(new_merged))]:
                pass

        merged = new_merged

    return merged


def validate_zone_topology(
    coords: list,
    min_area_deg2: float = 1e-8,
) -> Optional[list]:
    """
    Valide la topologie d'un polygone zone.
    Corrige les auto-intersections via buffer(0).
    """
    if len(coords) < 3:
        return None

    try:
        ring = [(c[0], c[1]) for c in coords]
        if ring[0] != ring[-1]:
            ring.append(ring[0])
        poly = Polygon(ring)
        if not poly.is_valid:
            poly = poly.buffer(0)
        if poly.is_empty or poly.area < min_area_deg2:
            return None
        if poly.geom_type == "MultiPolygon":
            poly = max(poly.geoms, key=lambda g: g.area)
        return [[c[0], c[1]] for c in poly.exterior.coords]
    except Exception:
        return None
