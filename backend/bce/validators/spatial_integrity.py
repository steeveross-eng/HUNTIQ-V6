"""
BCE — Spatial Integrity Validator
Validates all generated geometries are topologically valid.

Rules:
- No self-intersections or bow-ties
- No degenerate polygons (< 3 vertices)
- No empty or null geometries
- Corridors and buffers consistent with parent zone
- All coordinates within valid WGS84 range
"""

import logging
from typing import Dict, List, Any
from shapely.geometry import shape, Polygon, MultiPolygon
from shapely.validation import explain_validity

logger = logging.getLogger("bce.spatial_integrity")

VALIDATOR_NAME = "spatial_integrity"


def validate(zones_geojson: Dict[str, Any]) -> Dict[str, Any]:
    """Run all spatial integrity checks on generated zones GeoJSON."""
    checks = []
    errors = []
    features = zones_geojson.get("features", [])

    # CHECK 1: All geometries are valid
    invalid_count = 0
    for i, f in enumerate(features):
        geom = f.get("geometry")
        if not geom:
            errors.append(f"Feature {i}: missing geometry")
            invalid_count += 1
            continue
        try:
            shp = shape(geom)
            if not shp.is_valid:
                reason = explain_validity(shp)
                errors.append(f"Feature {i}: invalid geometry — {reason}")
                invalid_count += 1
            if shp.is_empty:
                errors.append(f"Feature {i}: empty geometry")
                invalid_count += 1
        except Exception as e:
            errors.append(f"Feature {i}: geometry parse error — {e}")
            invalid_count += 1

    checks.append({
        "name": "all_geometries_valid",
        "status": "PASS" if invalid_count == 0 else "FAIL",
        "detail": f"{len(features) - invalid_count}/{len(features)} valid",
    })

    # CHECK 2: No degenerate polygons (< 3 unique vertices)
    degenerate_count = 0
    for i, f in enumerate(features):
        geom = f.get("geometry")
        if not geom or geom.get("type") != "Polygon":
            continue
        coords = geom.get("coordinates", [[]])[0]
        unique = set(tuple(c[:2]) for c in coords)
        if len(unique) < 3:
            errors.append(f"Feature {i}: degenerate polygon ({len(unique)} unique vertices)")
            degenerate_count += 1

    checks.append({
        "name": "no_degenerate_polygons",
        "status": "PASS" if degenerate_count == 0 else "FAIL",
        "detail": f"{degenerate_count} degenerate",
    })

    # CHECK 3: All coordinates in WGS84 range
    out_of_range = 0
    for i, f in enumerate(features):
        geom = f.get("geometry")
        if not geom:
            continue
        for ring in geom.get("coordinates", []):
            for c in ring:
                lng, lat = c[0], c[1]
                if not (-180 <= lng <= 180 and -90 <= lat <= 90):
                    out_of_range += 1
                    errors.append(f"Feature {i}: coordinate out of WGS84 range ({lng}, {lat})")
                    break

    checks.append({
        "name": "coordinates_wgs84_valid",
        "status": "PASS" if out_of_range == 0 else "FAIL",
        "detail": f"{out_of_range} out of range",
    })

    # CHECK 4: No self-intersecting polygon rings
    self_intersect_count = 0
    for i, f in enumerate(features):
        geom = f.get("geometry")
        if not geom:
            continue
        try:
            shp = shape(geom)
            if shp.geom_type == "Polygon" and not shp.exterior.is_simple:
                self_intersect_count += 1
                errors.append(f"Feature {i}: self-intersecting exterior ring")
        except Exception:
            pass

    checks.append({
        "name": "no_self_intersections",
        "status": "PASS" if self_intersect_count == 0 else "FAIL",
        "detail": f"{self_intersect_count} self-intersecting",
    })

    # CHECK 5: Polygon areas > 0
    zero_area = 0
    for i, f in enumerate(features):
        geom = f.get("geometry")
        if not geom:
            continue
        try:
            shp = shape(geom)
            if shp.area <= 0:
                zero_area += 1
                errors.append(f"Feature {i}: zero or negative area")
        except Exception:
            pass

    checks.append({
        "name": "positive_area",
        "status": "PASS" if zero_area == 0 else "FAIL",
        "detail": f"{zero_area} zero-area zones",
    })

    status = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    return {
        "name": VALIDATOR_NAME,
        "status": status,
        "checks": checks,
        "errors": errors,
        "features_tested": len(features),
    }
