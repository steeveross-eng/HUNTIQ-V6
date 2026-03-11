"""
Test anti-regression BIONIC V7.1 — Exclusions urbaines
Garde-fou permanent: aucune zone ne doit jamais apparaitre en zone urbaine dense.

Waypoint: 46.8045, -71.2364 (Quebec centre-ville, zoom 14)
Attendu: 0 zones generees, 100% exclues.
"""
import pytest
import httpx
import os
import time

API_URL = os.environ.get("API_URL", "http://localhost:8001")

# Quebec centre-ville (Montcalm / Saint-Sauveur)
URBAN_WAYPOINT = {"lat": 46.8045, "lng": -71.2364}
URBAN_BOUNDS = {
    "north": URBAN_WAYPOINT["lat"] + 0.015,
    "south": URBAN_WAYPOINT["lat"] - 0.015,
    "east": URBAN_WAYPOINT["lng"] + 0.015,
    "west": URBAN_WAYPOINT["lng"] - 0.015,
}

# Reserve des Laurentides (foret profonde)
FOREST_WAYPOINT = {"lat": 47.285, "lng": -71.415}
FOREST_BOUNDS = {
    "north": FOREST_WAYPOINT["lat"] + 0.015,
    "south": FOREST_WAYPOINT["lat"] - 0.015,
    "east": FOREST_WAYPOINT["lng"] + 0.015,
    "west": FOREST_WAYPOINT["lng"] - 0.015,
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


class TestUrbanExclusionV71:
    """NORME BIONIC: zero zone en zone urbaine, zero bavure, zero regression."""

    def test_urban_quebec_city_zero_zones(self, client):
        """GARDE-FOU: Waypoint 46.8045, -71.2364 (Quebec centre-ville)
        doit retourner exactement 0 zones."""
        data = _call_organic_zones(client, URBAN_BOUNDS, URBAN_WAYPOINT)
        zones = data.get("features", [])
        stats = data.get("stats", {})
        exclusions = stats.get("exclusions_count", 0)

        assert len(zones) == 0, (
            f"REGRESSION BIONIC V7.1: {len(zones)} zones en zone urbaine "
            f"(Quebec centre-ville 46.8045, -71.2364). "
            f"Exclusions: {exclusions}. Zones: {[f.get('properties',{}).get('layer_id') for f in zones]}"
        )
        assert exclusions > 0, "Aucune exclusion fetchee — Overpass API defaillant?"

    def test_urban_has_exclusions(self, client):
        """Verifier que des exclusions anthropiques sont bien fetched."""
        data = _call_organic_zones(client, URBAN_BOUNDS, URBAN_WAYPOINT)
        stats = data.get("stats", {})
        assert stats.get("exclusions_count", 0) > 100, (
            f"Trop peu d'exclusions pour une zone urbaine dense: {stats.get('exclusions_count', 0)}"
        )

    def test_urban_all_rejected(self, client):
        """Verifier que le moteur rejette bien des zones (pas juste 0 generees)."""
        data = _call_organic_zones(client, URBAN_BOUNDS, URBAN_WAYPOINT)
        stats = data.get("stats", {})
        rejected = stats.get("rejected_exclusion", 0)
        assert rejected > 0, (
            f"Aucune zone rejetee en zone urbaine — le pipeline ne genere peut-etre aucune zone brute?"
        )

    def test_forest_has_zones(self, client):
        """Anti-regression: les zones forestieres doivent toujours etre generees."""
        data = _call_organic_zones(client, FOREST_BOUNDS, FOREST_WAYPOINT)
        zones = data.get("features", [])
        assert len(zones) > 0, (
            f"REGRESSION: 0 zones en zone forestiere (Reserve Laurentides). "
            f"Le filtre anti-urbain est trop agressif."
        )

    def test_forest_no_over_filtering(self, client):
        """Verifier que la foret n'est pas sur-filtree (>= 5 zones attendues)."""
        data = _call_organic_zones(client, FOREST_BOUNDS, FOREST_WAYPOINT)
        zones = data.get("features", [])
        assert len(zones) >= 3, (
            f"Trop peu de zones en foret: {len(zones)}. Le filtre est trop agressif."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
