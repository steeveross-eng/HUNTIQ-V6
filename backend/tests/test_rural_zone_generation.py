"""
Test anti-regression BIONIC V7.3 — Generation de zones en contexte rural.
Garde-fou permanent: les zones DOIVENT etre generees en milieu rural/forestier chassable.

Ce test complemente test_urban_exclusion_guard.py:
  - Urbain: 0 zones attendues
  - Rural/Foret: zones attendues (>= 3)

Waypoints:
  - Rural agricole: 46.65, -71.55 (Beauce, sud de Quebec — terres agricoles + foret)
  - Foret profonde: 47.285, -71.415 (Reserve des Laurentides)

BIONIC V7.3: farmland/farmyard/orchard/vineyard retires des exclusions urbaines.
"""
import pytest
import httpx
import os

API_URL = os.environ.get("API_URL", "http://localhost:8001")

# Beauce — zone rurale agricole chassable
RURAL_WAYPOINT = {"lat": 46.65, "lng": -71.55}
RURAL_BOUNDS = {
    "north": RURAL_WAYPOINT["lat"] + 0.015,
    "south": RURAL_WAYPOINT["lat"] - 0.015,
    "east": RURAL_WAYPOINT["lng"] + 0.015,
    "west": RURAL_WAYPOINT["lng"] - 0.015,
}

# Reserve des Laurentides — foret profonde
FOREST_WAYPOINT = {"lat": 47.285, "lng": -71.415}
FOREST_BOUNDS = {
    "north": FOREST_WAYPOINT["lat"] + 0.015,
    "south": FOREST_WAYPOINT["lat"] - 0.015,
    "east": FOREST_WAYPOINT["lng"] + 0.015,
    "west": FOREST_WAYPOINT["lng"] - 0.015,
}

# Quebec centre-ville — regression guard (doit rester 0 zones)
URBAN_WAYPOINT = {"lat": 46.8045, "lng": -71.2364}
URBAN_BOUNDS = {
    "north": URBAN_WAYPOINT["lat"] + 0.015,
    "south": URBAN_WAYPOINT["lat"] - 0.015,
    "east": URBAN_WAYPOINT["lng"] + 0.015,
    "west": URBAN_WAYPOINT["lng"] - 0.015,
}

LAYERS = ["habitats", "rut", "repos", "alimentation", "corridors"]
TIMEOUT = 120


@pytest.fixture(scope="module")
def client():
    return httpx.Client(base_url=API_URL, timeout=TIMEOUT)


def _call_organic_zones(client, bounds, waypoint_center=None):
    body = {
        "bounds": bounds,
        "species": "moose",
        "layers": LAYERS,
        "resolution": 60,
        "max_zones_per_layer": 8,
        "include_scoring": False,
    }
    if waypoint_center:
        body["waypoint_center"] = waypoint_center
    resp = client.post("/api/v1/bionic/organic-zones", json=body)
    assert resp.status_code == 200, f"API error: {resp.status_code} {resp.text[:200]}"
    return resp.json()


class TestRuralZoneGenerationV73:
    """BIONIC V7.3: Les zones rurales/forestieres DOIVENT etre generees."""

    def test_rural_beauce_has_zones(self, client):
        """GARDE-FOU V7.3: Zone rurale agricole (Beauce) doit generer des zones."""
        data = _call_organic_zones(client, RURAL_BOUNDS, RURAL_WAYPOINT)
        zones = data.get("features", [])
        stats = data.get("stats", {})

        assert len(zones) > 0, (
            f"REGRESSION V7.3: 0 zones en zone rurale (Beauce 46.65, -71.55). "
            f"Stats: rejected={stats.get('rejected_exclusion', 0)}, "
            f"exclusions={stats.get('exclusions_count', 0)}, "
            f"zero_reason={stats.get('zero_zones_reason', 'N/A')}"
        )

    def test_rural_beauce_minimum_zones(self, client):
        """Verifier >= 3 zones en contexte rural."""
        data = _call_organic_zones(client, RURAL_BOUNDS, RURAL_WAYPOINT)
        zones = data.get("features", [])
        assert len(zones) >= 3, (
            f"Trop peu de zones en zone rurale: {len(zones)}. "
            f"Le filtre est trop agressif meme pour le contexte rural."
        )

    def test_rural_no_exclusion_failure(self, client):
        """Verifier que l'exclusion n'a pas echoue en rural."""
        data = _call_organic_zones(client, RURAL_BOUNDS, RURAL_WAYPOINT)
        stats = data.get("stats", {})
        assert not stats.get("exclusion_failed", False), (
            "Overpass a echoue en zone rurale — pas de zones possibles."
        )

    def test_forest_laurentides_has_zones(self, client):
        """GARDE-FOU: Reserve des Laurentides doit generer des zones."""
        data = _call_organic_zones(client, FOREST_BOUNDS, FOREST_WAYPOINT)
        zones = data.get("features", [])
        assert len(zones) > 0, (
            f"REGRESSION: 0 zones en zone forestiere (Reserve Laurentides). "
            f"Le filtre anti-urbain est trop agressif."
        )

    def test_forest_minimum_zones(self, client):
        """Verifier >= 3 zones en foret profonde."""
        data = _call_organic_zones(client, FOREST_BOUNDS, FOREST_WAYPOINT)
        zones = data.get("features", [])
        assert len(zones) >= 3, (
            f"Trop peu de zones en foret: {len(zones)}. Le filtre est trop agressif."
        )

    def test_urban_still_zero_zones(self, client):
        """REGRESSION GUARD: Quebec centre-ville DOIT rester a 0 zones."""
        data = _call_organic_zones(client, URBAN_BOUNDS, URBAN_WAYPOINT)
        zones = data.get("features", [])
        assert len(zones) == 0, (
            f"REGRESSION V7.1/V7.2: {len(zones)} zones en zone urbaine "
            f"(Quebec centre-ville). Les exclusions urbaines ne fonctionnent plus!"
        )

    def test_urban_has_exclusions(self, client):
        """Verifier que des exclusions sont bien fetchees en urbain."""
        data = _call_organic_zones(client, URBAN_BOUNDS, URBAN_WAYPOINT)
        stats = data.get("stats", {})
        assert stats.get("exclusions_count", 0) > 50, (
            f"Trop peu d'exclusions en urbain: {stats.get('exclusions_count', 0)}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
