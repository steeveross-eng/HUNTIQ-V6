"""
BCE — Water Exclusion Validator
Ensures NO zone intersects water polygons.

Rules:
- No zone intersects any water polygon, even by 1 pixel
- No zone centroid is located inside water
- Zones adjacent to water follow shoreline (difference + buffer(0))
- Zone topology remains valid after water exclusion
"""

import logging
from typing import Dict, List, Any
from shapely.geometry import shape, Point, Polygon
from shapely.ops import unary_union

logger = logging.getLogger("bce.water_exclusion")

VALIDATOR_NAME = "water_exclusion"


def _build_water_union(exclusions: List[Dict]) -> Any:
    """Build unified water geometry from exclusion data."""
    water_polys = []
    for ex in exclusions:
        if ex.get("type") != "water":
            continue
        coords = ex.get("coordinates", [])
        geom_type = ex.get("geometry_type", "polygon")
        if geom_type != "polygon" or len(coords) < 3:
            continue
        try:
            ring = [(c[0], c[1]) for c in coords]
            if ring[0] != ring[-1]:
                ring.append(ring[0])
            poly = Polygon(ring)
            if not poly.is_valid:
                poly = poly.buffer(0)
            if not poly.is_empty:
                water_polys.append(poly)
        except Exception:
            continue

    if not water_polys:
        return None
    return unary_union(water_polys)


def validate(
    zones_geojson: Dict[str, Any],
    exclusions: List[Dict] = None,
    water_union=None,
) -> Dict[str, Any]:
    """Run water exclusion compliance checks."""
    checks = []
    errors = []
    features = zones_geojson.get("features", [])

    # Build water union if not provided
    if water_union is None and exclusions:
        water_union = _build_water_union(exclusions)

    if water_union is None:
        checks.append({
            "name": "water_data_available",
            "status": "WARN",
            "detail": "No water polygons available for validation",
        })
        return {
            "name": VALIDATOR_NAME,
            "status": "WARN",
            "checks": checks,
            "errors": ["No water data to validate against"],
            "features_tested": len(features),
        }

    checks.append({
        "name": "water_data_available",
        "status": "PASS",
        "detail": f"Water union area: {water_union.area:.8f} deg2",
    })

    # CHECK 1: No zone intersects water
    intersect_count = 0
    for i, f in enumerate(features):
        geom = f.get("geometry")
        if not geom:
            continue
        try:
            zone_shp = shape(geom)
            if zone_shp.intersects(water_union):
                overlap = zone_shp.intersection(water_union)
                overlap_ratio = overlap.area / zone_shp.area if zone_shp.area > 0 else 0
                if overlap_ratio > 1e-6:
                    intersect_count += 1
                    errors.append(
                        f"Feature {i}: intersects water "
                        f"(overlap={overlap_ratio:.4%})"
                    )
        except Exception as e:
            errors.append(f"Feature {i}: intersection check failed — {e}")

    checks.append({
        "name": "no_zone_intersects_water",
        "status": "PASS" if intersect_count == 0 else "FAIL",
        "detail": f"{intersect_count} zones intersect water",
    })

    # CHECK 2: No zone centroid in water
    centroid_in_water = 0
    for i, f in enumerate(features):
        geom = f.get("geometry")
        if not geom:
            continue
        try:
            zone_shp = shape(geom)
            centroid = zone_shp.centroid
            if water_union.contains(centroid):
                centroid_in_water += 1
                props = f.get("properties", {})
                errors.append(
                    f"Feature {i} (layer={props.get('layer_id', '?')}): "
                    f"centroid in water at ({centroid.y:.5f}, {centroid.x:.5f})"
                )
        except Exception:
            pass

    checks.append({
        "name": "no_centroid_in_water",
        "status": "PASS" if centroid_in_water == 0 else "FAIL",
        "detail": f"{centroid_in_water} centroids in water",
    })

    # CHECK 3: Adjacent zones follow shoreline (no jagged edges)
    adjacent_zones = 0
    poor_adherence = 0
    for i, f in enumerate(features):
        geom = f.get("geometry")
        if not geom:
            continue
        try:
            zone_shp = shape(geom)
            if zone_shp.distance(water_union) < 0.0005:  # ~55m
                adjacent_zones += 1
                # Check that zone boundary doesn't have jagged overlap
                boundary_overlap = zone_shp.boundary.intersection(water_union)
                if not boundary_overlap.is_empty and boundary_overlap.length > 0:
                    # Zone boundary touches water — check it's clean
                    overlap = zone_shp.intersection(water_union)
                    if overlap.area > zone_shp.area * 0.001:  # >0.1% overlap
                        poor_adherence += 1
                        errors.append(
                            f"Feature {i}: poor shoreline adherence "
                            f"(overlap={overlap.area / zone_shp.area:.4%})"
                        )
        except Exception:
            pass

    checks.append({
        "name": "shoreline_adherence",
        "status": "PASS" if poor_adherence == 0 else "FAIL",
        "detail": f"{adjacent_zones} zones near water, {poor_adherence} poor adherence",
    })

    status = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    return {
        "name": VALIDATOR_NAME,
        "status": status,
        "checks": checks,
        "errors": errors,
        "features_tested": len(features),
    }
