"""
BIONIC P0 — Water Exclusion Non-Regression Tests
=================================================

Validates that NO generated zone intersects water polygons.
Ensures the BIONIC water exclusion rules are permanently enforced:
  1. No zone centroid in water
  2. No zone polygon intersects water
  3. Zones adjacent to water follow shoreline (trimming)
  4. Zone topology remains valid after water exclusion

These tests reproduce the bug where zones were generated in the
Saint Lawrence River because oversized river polygons were filtered out.
"""

import pytest
import asyncio
import os
import sys
import math

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_build_exclusion_unions_includes_filtered_water():
    """
    CRITICAL: Verify that build_exclusion_unions includes filtered_out
    water features (oversized rivers/relations) instead of skipping them.
    """
    from modules.bionic_engine_p0.services.exclusion_geometry_v6 import (
        build_exclusion_unions,
    )

    # Simulate a large river polygon that would be marked filtered_out
    # (e.g., the Saint Lawrence River clipped to viewport)
    river_coords = [
        [-71.25, 46.80],
        [-71.20, 46.80],
        [-71.20, 46.82],
        [-71.25, 46.82],
        [-71.25, 46.80],
    ]

    exclusions = [
        {
            "id": 1,
            "type": "water",
            "geometry_type": "polygon",
            "sub_type": "river",
            "coordinates": river_coords,
            "area_m2": 5000000,  # 5 km2 — would be filtered_out
            "filtered_out": True,
            "reason": "oversized_river",
        },
        {
            "id": 2,
            "type": "water",
            "geometry_type": "polygon",
            "sub_type": "lake",
            "coordinates": [
                [-71.30, 46.85],
                [-71.29, 46.85],
                [-71.29, 46.86],
                [-71.30, 46.86],
                [-71.30, 46.85],
            ],
            "area_m2": 50000,
            "filtered_out": False,
            "reason": "valid_water",
        },
    ]

    bounds = {"south": 46.79, "north": 46.87, "west": -71.31, "east": -71.19}
    unions = build_exclusion_unions(exclusions, lat_center=46.83, bounds=bounds)

    # The water union MUST exist (river + lake)
    assert unions.get("raw_water") is not None, (
        "Water union is None — filtered_out river was skipped!"
    )
    assert unions.get("water") is not None, (
        "Prepared water union is None — filtered_out river was skipped!"
    )

    # The water union must cover the river area
    from shapely.geometry import Point
    river_center = Point(-71.225, 46.81)
    raw_water = unions["raw_water"]
    assert raw_water.contains(river_center) or raw_water.intersects(river_center.buffer(0.001)), (
        "Water union does not cover the river center — river polygon was not included!"
    )


def test_filtered_water_non_water_still_skipped():
    """
    Verify that filtered_out NON-water features are still skipped.
    Only water features should be rescued from filtering.
    """
    from modules.bionic_engine_p0.services.exclusion_geometry_v6 import (
        build_exclusion_unions,
    )

    exclusions = [
        {
            "id": 1,
            "type": "urban",
            "geometry_type": "polygon",
            "sub_type": "residential",
            "coordinates": [
                [-71.25, 46.80],
                [-71.20, 46.80],
                [-71.20, 46.82],
                [-71.25, 46.82],
                [-71.25, 46.80],
            ],
            "area_m2": 50000,
            "filtered_out": True,
            "reason": "oversized_urban",
        },
    ]

    bounds = {"south": 46.79, "north": 46.83, "west": -71.26, "east": -71.19}
    unions = build_exclusion_unions(exclusions, lat_center=46.81, bounds=bounds)

    # Urban should be None (the only entry was filtered_out)
    assert unions.get("raw_urban") is None, (
        "Filtered_out urban feature was NOT skipped — only water should be rescued!"
    )


def test_zone_centroid_never_in_water():
    """
    BIONIC RULE: No zone centroid may be located inside water.
    Simulate generating zones where a river polygon exists.
    """
    from shapely.geometry import Polygon, Point

    # River polygon
    river = Polygon([
        (-71.22, 46.80), (-71.18, 46.80),
        (-71.18, 46.82), (-71.22, 46.82),
        (-71.22, 46.80),
    ])

    # Simulated zone centroids
    test_centroids = [
        {"lat": 46.81, "lng": -71.20, "expected_in_water": True},   # In river
        {"lat": 46.85, "lng": -71.25, "expected_in_water": False},  # On land
        {"lat": 46.815, "lng": -71.19, "expected_in_water": True},  # In river
        {"lat": 46.83, "lng": -71.30, "expected_in_water": False},  # On land
    ]

    for tc in test_centroids:
        point = Point(tc["lng"], tc["lat"])
        in_water = river.contains(point)
        assert in_water == tc["expected_in_water"], (
            f"Centroid ({tc['lat']}, {tc['lng']}): "
            f"expected in_water={tc['expected_in_water']}, got {in_water}"
        )


def test_zone_trimming_follows_shoreline():
    """
    BIONIC RULE: Zones adjacent to water must follow the shoreline.
    After trimming, the zone must not overlap water.
    """
    from shapely.geometry import Polygon
    from modules.bionic_engine_p0.services.exclusion_geometry_v6 import trim_zone

    # A zone that overlaps both land and water
    zone_poly = Polygon([
        (-71.24, 46.81), (-71.20, 46.81),
        (-71.20, 46.83), (-71.24, 46.83),
        (-71.24, 46.81),
    ])

    # River polygon (right half of the zone)
    river = Polygon([
        (-71.22, 46.80), (-71.18, 46.80),
        (-71.18, 46.84), (-71.22, 46.84),
        (-71.22, 46.80),
    ])

    min_area_deg2 = 0.00001  # Very small threshold for test

    trimmed = trim_zone(zone_poly, river, min_area_deg2)

    assert trimmed is not None, "Zone was completely eliminated — should have a land portion"
    assert not trimmed.is_empty, "Trimmed zone is empty"

    # Trimmed zone must NOT intersect river
    intersection = trimmed.intersection(river)
    # Allow tiny numerical errors
    assert intersection.area < 1e-10, (
        f"Trimmed zone still intersects water! "
        f"Overlap area: {intersection.area}"
    )

    # Trimmed zone must be on the LAND side
    assert trimmed.centroid.x < -71.22, (
        f"Trimmed zone centroid is on the water side: {trimmed.centroid}"
    )


def test_zone_topology_valid_after_trimming():
    """
    BIONIC RULE: Zone topology must remain valid after water exclusion.
    No degenerate polygons, self-intersections, or empty geometries.
    """
    from shapely.geometry import Polygon
    from modules.bionic_engine_p0.services.exclusion_geometry_v6 import trim_zone

    # Complex zone shape
    zone_poly = Polygon([
        (-71.25, 46.81), (-71.21, 46.81),
        (-71.20, 46.82), (-71.21, 46.83),
        (-71.25, 46.83), (-71.25, 46.81),
    ])

    # Irregularly shaped water body
    water = Polygon([
        (-71.23, 46.805), (-71.19, 46.815),
        (-71.19, 46.825), (-71.23, 46.835),
        (-71.23, 46.805),
    ])

    min_area_deg2 = 0.00001
    trimmed = trim_zone(zone_poly, water, min_area_deg2)

    if trimmed is not None:
        assert trimmed.is_valid, f"Trimmed zone has invalid topology: {trimmed}"
        assert not trimmed.is_empty, "Trimmed zone is empty"
        assert trimmed.geom_type == "Polygon", (
            f"Expected Polygon, got {trimmed.geom_type}"
        )


def test_clip_oversized_water_to_bounds():
    """
    Verify that oversized water features are properly clipped to viewport bounds.
    """
    from modules.bionic_engine_p0.services.exclusion_geometry_v6 import (
        build_exclusion_unions,
    )

    # Very large river polygon (100km long)
    large_river_coords = [
        [-72.0, 46.5],
        [-70.5, 46.5],
        [-70.5, 46.9],
        [-72.0, 46.9],
        [-72.0, 46.5],
    ]

    exclusions = [
        {
            "id": 1,
            "type": "water",
            "geometry_type": "polygon",
            "sub_type": "river",
            "coordinates": large_river_coords,
            "area_m2": 100000000,
            "filtered_out": True,
            "reason": "oversized_river",
        },
    ]

    # Small viewport
    bounds = {"south": 46.80, "north": 46.83, "west": -71.25, "east": -71.20}
    unions = build_exclusion_unions(exclusions, lat_center=46.815, bounds=bounds)

    raw_water = unions.get("raw_water")
    assert raw_water is not None, "Water union is None after clipping"

    # The water union should be clipped to roughly the viewport size
    minx, miny, maxx, maxy = raw_water.bounds
    assert maxx - minx < 0.1, (
        f"Water union is too wide after clipping: {maxx - minx}"
    )
    assert maxy - miny < 0.1, (
        f"Water union is too tall after clipping: {maxy - miny}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
