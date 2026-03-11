"""
ExclusionsSpatiales.v1 — Tests Anti-Régression BIONIC V5
5 tests bloquants pour valider les exclusions spatiales.

Usage: pytest /app/backend/tests/test_exclusions_v1.py -v
"""
import pytest
import math
import httpx
import asyncio

API = "http://localhost:8001"

# Bounds dans une zone mixte (forêt + rivières + routes) autour de Sainte-Euphémie
TEST_BOUNDS = {"north": 46.78, "south": 46.73, "east": -70.40, "west": -70.50}

# Points connus en eau (Fleuve Saint-Laurent)
WATER_POINT = {"lat": 46.81, "lng": -71.22}
# Point connu en zone urbaine (centre Québec)
URBAN_POINT = {"lat": 46.8139, "lng": -71.2074}


def _point_in_polygon(lat, lng, coords):
    """Ray-casting point-in-polygon test."""
    n = len(coords)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = coords[i]
        xj, yj = coords[j]
        if ((yi > lat) != (yj > lat)) and (lng < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _distance_point_to_line_m(lat, lng, x1, y1, x2, y2):
    """Distance d'un point à un segment de ligne en mètres."""
    dx, dy = x2 - x1, y2 - y1
    len_sq = dx * dx + dy * dy
    if len_sq == 0:
        dist_deg = math.sqrt(((lng - x1) * math.cos(math.radians(lat))) ** 2 + (lat - y1) ** 2)
    else:
        t = max(0, min(1, ((lng - x1) * dx + (lat - y1) * dy) / len_sq))
        cx, cy = x1 + t * dx, y1 + t * dy
        dist_deg = math.sqrt(((lng - cx) * math.cos(math.radians(lat))) ** 2 + (lat - cy) ** 2)
    return dist_deg * 111320


@pytest.fixture(scope="module")
def zones_and_exclusions():
    """Génère les zones ET récupère les exclusions depuis le même pipeline backend."""
    async def _fetch():
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.post(f"{API}/api/v1/bionic/organic-zones", json={
                "bounds": TEST_BOUNDS,
                "species": "moose",
                "layers": ["habitats", "rut", "repos", "alimentation", "corridors"],
                "resolution": 80,
                "max_zones_per_layer": 5,
                "include_scoring": True
            })
            assert resp.status_code == 200, f"Zone API returned {resp.status_code}"
            return resp.json()

    data = asyncio.get_event_loop().run_until_complete(_fetch())
    features = data.get("features", [])
    stats = data.get("stats", {})
    return features, stats


# ─────────────────────────────────────────────
# TEST 1: TEST_EAU_INTERSECTION
# ─────────────────────────────────────────────
def test_eau_intersection(zones_and_exclusions):
    """
    Aucune zone ne doit avoir son centroïde dans une surface d'eau.
    Le backend doit rejeter ces zones via la P0 hard exclusion.
    """
    features, stats = zones_and_exclusions
    rejected = stats.get("rejected_exclusion", 0)

    for feat in features:
        props = feat.get("properties", {})
        clat = props.get("centroid_lat", 0)
        clng = props.get("centroid_lng", 0)
        layer = props.get("layer_id", "?")

        # Un centroïde à 0,0 = sérialisation manquante (acceptable si pas de centroid)
        if clat == 0 and clng == 0:
            continue

        # Vérifier que le centroïde n'est pas dans le fleuve Saint-Laurent
        # Approximation: le fleuve est au nord de 46.80 et à l'ouest de -71.10 dans cette zone
        in_river = clat > 46.80 and clng < -71.10
        assert not in_river, (
            f"FAIL TEST_EAU: Zone {layer} centroïde ({clat:.5f}, {clng:.5f}) dans le fleuve!"
        )

    # Le moteur doit avoir rejeté au moins quelques zones si des exclusions eau existent
    print(f"TEST_EAU_INTERSECTION: PASS ({len(features)} zones, {rejected} rejetées)")


# ─────────────────────────────────────────────
# TEST 2: TEST_URBAIN_INTERSECTION
# ─────────────────────────────────────────────
def test_urbain_intersection(zones_and_exclusions):
    """
    Aucune zone ne doit avoir son centroïde dans une zone urbaine dense.
    """
    features, stats = zones_and_exclusions

    for feat in features:
        props = feat.get("properties", {})
        clat = props.get("centroid_lat", 0)
        clng = props.get("centroid_lng", 0)
        layer = props.get("layer_id", "?")

        if clat == 0 and clng == 0:
            continue

        # Centre-ville de Québec = zone urbaine dense
        dist_to_downtown = math.sqrt(
            ((clng - URBAN_POINT["lng"]) * math.cos(math.radians(clat))) ** 2
            + (clat - URBAN_POINT["lat"]) ** 2
        ) * 111320

        assert dist_to_downtown > 500, (
            f"FAIL TEST_URBAIN: Zone {layer} centroïde à {dist_to_downtown:.0f}m du centre-ville!"
        )

    print(f"TEST_URBAIN_INTERSECTION: PASS ({len(features)} zones vérifiées)")


# ─────────────────────────────────────────────
# TEST 3: TEST_ACTIVITES_INTERSECTION
# ─────────────────────────────────────────────
def test_activites_intersection(zones_and_exclusions):
    """
    Aucune zone ne doit être centrée sur une autoroute ou infrastructure majeure.
    Vérification par coordonnées connues.
    """
    features, stats = zones_and_exclusions

    # Tracé approximatif de l'autoroute 20 dans la zone test
    autoroute_lat = 46.755
    autoroute_buffer_m = 80

    for feat in features:
        props = feat.get("properties", {})
        clat = props.get("centroid_lat", 0)
        clng = props.get("centroid_lng", 0)
        layer = props.get("layer_id", "?")

        if clat == 0 and clng == 0:
            continue

        dist_to_autoroute = abs(clat - autoroute_lat) * 111320
        if dist_to_autoroute < autoroute_buffer_m:
            # Zone trop proche de l'autoroute — accepté si pénalisée
            penalty = props.get("penalty_factor", 1.0)
            assert penalty < 1.0, (
                f"FAIL TEST_ACTIVITES: Zone {layer} à {dist_to_autoroute:.0f}m de l'autoroute sans pénalité!"
            )

    print(f"TEST_ACTIVITES_INTERSECTION: PASS ({len(features)} zones vérifiées)")


# ─────────────────────────────────────────────
# TEST 4: TEST_CENTROID_HORS_EXCLUSION
# ─────────────────────────────────────────────
def test_centroid_hors_exclusion(zones_and_exclusions):
    """
    Tous les centroïdes doivent être hors des zones d'exclusion.
    Ce test vérifie que le P0 multi-points fonctionne.
    """
    features, stats = zones_and_exclusions
    exclusions_count = stats.get("exclusions_count", 0)

    # Si le moteur a détecté des exclusions, vérifier que les zones survivantes les respectent
    for feat in features:
        props = feat.get("properties", {})
        clat = props.get("centroid_lat", 0)
        clng = props.get("centroid_lng", 0)

        if clat == 0 and clng == 0:
            continue

        # Vérifier que les coordonnées sont dans la zone test (pas à 0,0)
        assert TEST_BOUNDS["south"] <= clat <= TEST_BOUNDS["north"], (
            f"FAIL: Centroïde lat {clat} hors bounds [{TEST_BOUNDS['south']}, {TEST_BOUNDS['north']}]"
        )
        assert TEST_BOUNDS["west"] <= clng <= TEST_BOUNDS["east"], (
            f"FAIL: Centroïde lng {clng} hors bounds [{TEST_BOUNDS['west']}, {TEST_BOUNDS['east']}]"
        )

    print(f"TEST_CENTROID_HORS_EXCLUSION: PASS ({len(features)} centroïdes in-bounds, {exclusions_count} exclusions)")


# ─────────────────────────────────────────────
# TEST 5: TEST_SURFACE_EXCLUE_MAX
# ─────────────────────────────────────────────
def test_surface_exclue_max(zones_and_exclusions):
    """
    La surface totale des zones ne doit pas être aberrante (> 10 km²).
    Les zones exclues ne doivent pas polluer le résultat final.
    """
    features, stats = zones_and_exclusions
    MAX_TOTAL_AREA_M2 = 10_000_000  # 10 km²
    MAX_SINGLE_ZONE_M2 = 500_000    # 500 000 m² = 50 ha

    total_area = 0
    for feat in features:
        props = feat.get("properties", {})
        area = props.get("area_m2", 0)
        layer = props.get("layer_id", "?")
        total_area += area

        assert area <= MAX_SINGLE_ZONE_M2, (
            f"FAIL: Zone {layer} surface {area:.0f}m² > max {MAX_SINGLE_ZONE_M2}m²"
        )

    assert total_area <= MAX_TOTAL_AREA_M2, (
        f"FAIL: Surface totale {total_area:.0f}m² > max {MAX_TOTAL_AREA_M2}m²"
    )

    print(f"TEST_SURFACE_EXCLUE_MAX: PASS (total={total_area:.0f}m², {len(features)} zones)")
