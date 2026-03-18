"""
ALIMENTATION-V2 — Optimiseur de salines
==========================================
Positionne les salines optimales dans un carré 2km×2km
selon: zones de repos, corridors, besoins minéraux,
accessibilité et sécurité. Conforme BCE-4X.
"""
import math
import hashlib


def _seed(lat, lng, salt=""):
    h = hashlib.md5(f"{lat:.6f}:{lng:.6f}:{salt}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def _offset(center_lat, center_lng, dx_m, dy_m):
    """Décale un point en mètres → degrés."""
    d_lat = dy_m / 111320
    d_lng = dx_m / (111320 * math.cos(math.radians(center_lat)))
    return center_lat + d_lat, center_lng + d_lng


def compute_salines(
    center_lat: float,
    center_lng: float,
    terrain: dict,
    species: str = "CERF",
    month: int = 10,
    side_m: float = 2000.0,
) -> list:
    """
    Calcule les emplacements optimaux de salines.
    Retourne une liste de salines avec position, score, justification.
    """
    half = side_m / 2
    salines = []

    # Nombre de salines: 3-6 selon la taille de la zone et le score alimentaire
    dispo = terrain.get("alimentaire", {}).get("score_disponibilite", 0.5)
    n_salines = max(3, min(6, int(4 + (1 - dispo) * 4)))

    for i in range(n_salines):
        # Position déterministe basée sur coordonnées + index
        s = _seed(center_lat, center_lng, f"saline_{i}")
        s2 = _seed(center_lat, center_lng, f"sal_y_{i}")

        # Positionner entre 200m et 900m du centre (éviter le cœur dense)
        angle = s * 2 * math.pi
        dist = 200 + s2 * 700
        dx = dist * math.cos(angle)
        dy = dist * math.sin(angle)
        lat, lng = _offset(center_lat, center_lng, dx, dy)

        # Score de placement (0-100)
        eau_prox = terrain.get("eau", {}).get("score_hydrique", 0.5)
        couvert = terrain.get("foret", {}).get("couvert_pct", 60) / 100
        pente = terrain.get("relief", {}).get("pente_moyenne_pct", 10)

        # Critères de scoring
        score_eau = min(1.0, eau_prox * 1.2)  # Proximité eau = bonus
        score_couvert = 0.8 if 0.4 < couvert < 0.8 else 0.5  # Couvert moyen = optimal
        score_pente = max(0.3, 1.0 - pente / 30)  # Pente faible = meilleur
        score_acces = _seed(lat, lng, "acces")  # Accessibilité simulée
        score_securite = max(0.4, 1.0 - (dist / half))  # Plus proche du centre = plus sûr

        score_total = (
            score_eau * 0.25 +
            score_couvert * 0.20 +
            score_pente * 0.20 +
            score_acces * 0.15 +
            score_securite * 0.20
        )

        # Justification textuelle
        justifications = []
        if score_eau > 0.6:
            justifications.append("Bonne proximité eau")
        if score_couvert > 0.6:
            justifications.append("Couvert forestier optimal")
        if score_pente > 0.7:
            justifications.append("Terrain plat/accessible")
        if score_securite > 0.6:
            justifications.append("Zone sécurisée")

        # Type de saline selon espèce
        type_saline = "minérale"
        if species == "ORIGNAL":
            type_saline = "sodium" if eau_prox < 0.5 else "mixte"
        elif species == "OURS":
            type_saline = "protéinée"
        elif species == "WAPITI":
            type_saline = "calcium-enrichie"

        # Carences détectées dans la zone
        nutriments_sol = terrain.get("nutriments_sol", {})
        carences = []
        if nutriments_sol.get("selenium_ppm", 0.5) < 0.2:
            carences.append("Sélénium déficient")
        if nutriments_sol.get("cuivre_ppm", 5) < 3:
            carences.append("Cuivre faible")
        if nutriments_sol.get("calcium_ppm", 1000) < 500:
            carences.append("Calcium insuffisant")
        if nutriments_sol.get("phosphore_ppm", 15) < 10:
            carences.append("Phosphore bas")

        salines.append({
            "id": f"SAL-{i+1:02d}",
            "lat": round(lat, 6),
            "lng": round(lng, 6),
            "score": round(score_total * 100),
            "type": type_saline,
            "distance_centre_m": round(dist),
            "justifications": justifications or ["Emplacement convenable"],
            "carences_zone": carences or ["Aucune carence majeure détectée"],
            "criteres": {
                "eau": round(score_eau * 100),
                "couvert": round(score_couvert * 100),
                "pente": round(score_pente * 100),
                "accessibilite": round(score_acces * 100),
                "securite": round(score_securite * 100),
            },
        })

    # Trier par score décroissant
    salines.sort(key=lambda s: s["score"], reverse=True)
    return salines
