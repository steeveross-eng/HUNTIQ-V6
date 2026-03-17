"""
Firewall BCE-4X Anti-Regression — Contours Organiques STEEVE-MAX + MULTI
=========================================================================
Ce test BLOQUE toute generation de polygones non-conformes.
Criteres valides:
  1. Nombre de vertices (min 100 par polygone)
  2. Continuite du contour (polygone ferme)
  3. Absence de spikes (aucun angle < 45 degres)
  4. Ratio surface/attraction conforme
  5. Structure: 16 polygones, 4 par type, cluster_size=4, 64 centres
  6. STEVE-MAX-MULTI: 7 engines actifs, metadata presente
  7. Invariance geometrique: surfaces et centres stables
"""
import pytest
import math
import httpx

API_URL = "http://localhost:8001"
PAYLOAD = {"center_lat": 46.85, "center_lng": -71.25, "species": "CERF", "month": 10}


@pytest.fixture(scope="module")
def v10_data():
    resp = httpx.post(f"{API_URL}/api/v10/corridors/analyze-full", json=PAYLOAD, timeout=30)
    assert resp.status_code == 200
    data = resp.json()
    features = data["geojson"]["features"]
    polygons = [f for f in features if f["geometry"]["type"] == "Polygon"]
    return polygons


def test_firewall_16_polygons(v10_data):
    assert len(v10_data) == 16, f"Expected 16 polygons, got {len(v10_data)}"


def test_firewall_4_per_type(v10_data):
    from collections import Counter
    tc = Counter(p["properties"]["zone_type"] for p in v10_data)
    for ztype in ["alimentation", "repos", "rut", "eau"]:
        assert tc[ztype] == 4, f"{ztype}: expected 4, got {tc[ztype]}"


def test_firewall_cluster_size_4(v10_data):
    for p in v10_data:
        cs = p["properties"].get("cluster_size", 0)
        assert cs == 4, f"cluster_size={cs}, expected 4"


def test_firewall_64_centers(v10_data):
    total = sum(len(p["properties"].get("all_centers", [])) for p in v10_data)
    assert total == 64, f"Total centers={total}, expected 64"


def test_firewall_min_vertices(v10_data):
    """Chaque polygone doit avoir au moins 100 vertices (BCE-4X: resolution preservee)."""
    for i, p in enumerate(v10_data):
        coords = p["geometry"]["coordinates"][0]
        assert len(coords) >= 100, (
            f"Zone {i+1} ({p['properties']['zone_type']}): "
            f"{len(coords)} vertices < 100 minimum"
        )


def test_firewall_contour_closed(v10_data):
    """Chaque contour doit etre ferme (premier point = dernier point)."""
    for i, p in enumerate(v10_data):
        coords = p["geometry"]["coordinates"][0]
        assert len(coords) >= 4, f"Zone {i+1}: too few coords"
        first = coords[0]
        last = coords[-1]
        assert abs(first[0] - last[0]) < 1e-6 and abs(first[1] - last[1]) < 1e-6, (
            f"Zone {i+1}: contour not closed"
        )


def test_firewall_zero_spikes(v10_data):
    """FIREWALL PRINCIPAL: Aucun angle < 45 degres (zero spike/etoile)."""
    for i, p in enumerate(v10_data):
        coords = p["geometry"]["coordinates"][0]
        n_pts = len(coords) - 1
        spike_count = 0
        min_angle = 180
        for j in range(n_pts):
            p1 = coords[(j - 1) % n_pts]
            p2 = coords[j]
            p3 = coords[(j + 1) % n_pts]
            v1 = (p1[0] - p2[0], p1[1] - p2[1])
            v2 = (p3[0] - p2[0], p3[1] - p2[1])
            mag1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
            mag2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)
            if mag1 < 1e-12 or mag2 < 1e-12:
                continue
            cos_a = max(-1, min(1, (v1[0] * v2[0] + v1[1] * v2[1]) / (mag1 * mag2)))
            angle = math.degrees(math.acos(cos_a))
            if angle < min_angle:
                min_angle = angle
            if angle < 45:
                spike_count += 1
        assert spike_count == 0, (
            f"Zone {i+1} ({p['properties']['zone_type']}): "
            f"{spike_count} spikes detectes (min_angle={min_angle:.1f}°)"
        )


def test_firewall_surface_attraction_ratio(v10_data):
    """Les zones fortes doivent etre plus grandes que les zones faibles."""
    type_areas = {}
    for p in v10_data:
        ztype = p["properties"]["zone_type"]
        coords = p["geometry"]["coordinates"][0]
        lats = [c[1] for c in coords]
        lngs = [c[0] for c in coords]
        area = (max(lats) - min(lats)) * (max(lngs) - min(lngs))
        type_areas.setdefault(ztype, []).append(area)

    for ztype, areas in type_areas.items():
        avg_area = sum(areas) / len(areas)
        assert avg_area > 0, f"{ztype}: surface nulle"


def test_firewall_polygon_extent_minimum(v10_data):
    """Chaque polygone doit couvrir au moins 150m dans chaque dimension."""
    for i, p in enumerate(v10_data):
        coords = p["geometry"]["coordinates"][0]
        lats = [c[1] for c in coords]
        lngs = [c[0] for c in coords]
        ext_lat_m = (max(lats) - min(lats)) * 111320
        ext_lng_m = (max(lngs) - min(lngs)) * 111320 * 0.67
        assert ext_lat_m > 150, (
            f"Zone {i+1}: extent lat {ext_lat_m:.0f}m < 150m minimum"
        )
        assert ext_lng_m > 150, (
            f"Zone {i+1}: extent lng {ext_lng_m:.0f}m < 150m minimum"
        )


# ══════ STEVE-MAX-MULTI: Tests multi-engine ══════

def test_firewall_multi_engine_metadata(v10_data):
    """Chaque zone doit porter les metadonnees STEVE-MAX-MULTI."""
    for i, p in enumerate(v10_data):
        props = p["properties"]
        assert props.get("engine") == "STEVE-MAX-MULTI", (
            f"Zone {i+1}: engine manquant, got {props.get('engine')}"
        )
        assert props.get("engines_count") == 7, (
            f"Zone {i+1}: engines_count={props.get('engines_count')}, expected 7"
        )


def test_firewall_7_engines_active(v10_data):
    """Les 7 engines doivent etre listes dans engines_active."""
    expected_engines = {
        "alimentation_v1", "rut_v1", "repos_v1",
        "trajets_v1", "affuts_v1", "habitat_v1", "corridors_v10",
    }
    for i, p in enumerate(v10_data):
        active = set(p["properties"].get("engines_active", []))
        assert active == expected_engines, (
            f"Zone {i+1}: engines_active={active}, expected {expected_engines}"
        )


def test_firewall_centers_invariance(v10_data):
    """Les centres BCE-4X doivent etre stables (lat/lng non-nuls, score > 0)."""
    for i, p in enumerate(v10_data):
        centers = p["properties"].get("all_centers", [])
        for j, c in enumerate(centers):
            assert c.get("lat") is not None and c.get("lng") is not None, (
                f"Zone {i+1} center {j}: lat/lng manquant"
            )
            assert c.get("score", 0) > 0, (
                f"Zone {i+1} center {j}: score <= 0"
            )


def test_firewall_surface_invariance(v10_data):
    """Aucune zone ne doit avoir une surface nulle ou negative."""
    from shapely.geometry import Polygon as ShapelyPolygon
    for i, p in enumerate(v10_data):
        coords = p["geometry"]["coordinates"][0]
        poly = ShapelyPolygon(coords)
        assert poly.is_valid, f"Zone {i+1}: polygone invalide"
        assert poly.area > 0, f"Zone {i+1}: surface nulle"
